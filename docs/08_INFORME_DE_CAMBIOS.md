# 📋 Informe de cambios — SIGVACH

**Proyecto:** SIGVACH — Sistema de Gestión de Variables para Cultivos Hidropónicos
**Autor:** Freddy Carlo Santos Navarro
**Repositorio:** https://github.com/saintssud-sud/Proyecto---Diplomado (rama `main`)
**Fecha del informe:** 11 de septiembre de 2026
**Base del informe:** cambios pendientes entre el commit `c937e32` y el estado actual del proyecto
**Resumen del diff:** 22 archivos, +372 / −549 líneas

---

## 1. Resumen ejecutivo

En esta etapa el proyecto dejó de usar **Supabase** y pasó a **Firebase (Authentication + Cloud Firestore)**. Además de la migración de backend, se construyó un **sistema de gestión de usuarios con rol administrador**, se limpió código que no pertenecía al SIGVACH real y se **blindó el repositorio** para no publicar credenciales.

| # | Cambio | Alcance | Archivos |
|---|---|---|---|
| 1 | Migración de backend: Supabase → Firebase | App completa (auth + datos) | 12 |
| 2 | Gestión de usuarios (CRUD + rol admin) | Nuevo módulo | 5 nuevos + 3 modificados |
| 3 | Eliminación de SQL de Supabase | Limpieza | 5 eliminados |
| 4 | Seguridad del repositorio (credenciales) | `.gitignore` + plantillas | 5 |

---

## 2. Cambio de base de datos: Supabase (SQL) → Cloud Firestore (NoSQL)

### 2.1 Qué se cambió

| Aspecto | ANTES | AHORA |
|---|---|---|
| Autenticación | Supabase Auth | **Firebase Authentication** (correo/contraseña) |
| Base de datos | PostgreSQL gestionado por Supabase | **Cloud Firestore** (NoSQL, orientada a documentos) |
| Modelo de datos | Tablas relacionales con SQL + `JOIN` | Colecciones y documentos (JSON anidado) |
| Seguridad de datos | Políticas **RLS** (Row Level Security) en SQL | **Reglas de seguridad de Firestore** (`.rules`) |
| Configuración en la app | `--dart-define-from-file=config/local.json` | Incrustada en `lib/firebase_options.dart` |
| Dependencia Flutter | `supabase_flutter` | `firebase_core`, `firebase_auth`, `cloud_firestore` |

### 2.2 Por qué se migró (SQL → NoSQL)

1. **Simplicidad para el alcance del proyecto:** SIGVACH no necesita relaciones complejas ni `JOIN`. Guarda perfiles y registros con estructura plana, que es exactamente el caso de uso de un documento NoSQL.
2. **Sincronización en tiempo real sin esfuerzo:** Firestore ofrece streams nativos (`.snapshots()`), por lo que el panel de administración se actualiza solo, sin refrescar ni volver a consultar. Con SQL eso requería *polling* o *realtime* extra.
3. **Reglas declarativas por documento:** las reglas de Firestore permiten expresar directamente `uid == resource.id`, que es la verificación que necesita el CRUD de usuarios.
4. **Un solo proveedor para todo:** Auth y base de datos bajo el mismo SDK, un proyecto y una configuración, en lugar de dos servicios separados.
5. **Escalado automático:** Firestore es serverless, sin servidor que administrar, adecuado para un prototipo académico.

### 2.3 Equivalencias conceptuales SQL → NoSQL

| Concepto SQL (Supabase/PostgreSQL) | Equivalente en Firestore | En SIGVACH |
|---|---|---|
| Tabla | Colección | `usuarios` |
| Fila | Documento | `usuarios/{uid}` |
| Columna | Campo | `nombre`, `rol`, `activo` |
| Clave primaria | ID del documento | UID de Firebase Auth |
| `SELECT * FROM usuarios` | `collection('usuarios').get()` | `listarTodos()` |
| `SELECT ... WHERE` | `where(...)` sobre la colección | filtrado por `uid` |
| `UPDATE ... SET rol` | `doc(uid).update({'rol': ...})` | `cambiarRol()` |
| `DELETE FROM usuarios` | `doc(uid).delete()` | `eliminar()` |
| Política RLS | Regla de seguridad | `match /usuarios/{uid}` |
| `ORDER BY creado_en DESC` | `.orderBy('creado_en', descending: true)` | listado del panel admin |

### 2.4 Estructura de datos: antes y después

**ANTES (SQL relacional)** — archivos `supabase/01_SCHEMA_BASE_SESION1.sql`, `02_`, `03_`, `04_`:

```sql
create table public.registros (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id),
  ...
);
alter table public.registros enable row level security;
```

**AHORA (NoSQL, documentos)** — colección `usuarios`:

```
usuarios/{uid}
├── email:      "operador1@sigvach.com"
├── nombre:     "Operador Uno"
├── telefono:   "71234567"
├── cargo:      "Operador de invernadero"
├── rol:        "admin" | "usuario"
├── activo:     true | false
└── creado_en:  "2026-09-08T11:46:33.262"
```

> El **ID del documento es el UID de Firebase Authentication**: así el perfil queda vinculado 1 a 1 con la cuenta, sin necesidad de una columna `user_id` ni de una relación.

### 2.5 Impacto en el código de la app

| Archivo | Qué cambió |
|---|---|
| `pubspec.yaml` | Se quitó `supabase_flutter`; se agregaron `firebase_core`, `firebase_auth`, `cloud_firestore` |
| `lib/services/auth_service.dart` | Reescrito completo: `signIn` / `signUp` / `signOut` sobre Firebase Auth |
| `lib/services/firestore_service.dart` | **Nuevo.** Inicializa Firebase y expone un CRUD de ejemplo |
| `lib/config/app_config.dart` | Simplificado: ya no lee Supabase; expone `firebaseReady` y la etiqueta de modo |
| `lib/main.dart` | Inicializa Firebase con `try/catch` y registra los providers |
| `android/settings.gradle.kts` | Plugin de Google Services (bloque `FlutterFire Configuration`) |
| `android/app/build.gradle.kts` | Aplicación del plugin `com.google.gms.google-services` |
| `firebase.json` | **Nuevo.** Configuración de FlutterFire (apps android/web/windows) |
| `lib/firebase_options.dart` | **Nuevo.** Opciones por plataforma, generado por la FlutterFire CLI |

---

## 3. Gestión de usuarios (CRUD con rol administrador)

### 3.1 Qué se mejoró

| Antes | Ahora |
|---|---|
| Solo se guardaba el **nombre** del usuario (en `displayName` y `SharedPreferences`) | **Perfil completo en Firestore**: nombres, apellidos, teléfono, cargo, rol, estado |
| Sin roles: todos los usuarios eran iguales | **Rol `admin`** asignado automáticamente al correo `admin@sigvach.com`; el resto es `usuario` |
| Sin administración desde la app | **Panel de administración** que lista y edita usuarios en tiempo real |
| Sin control de estado | Campo **`activo`** para habilitar/deshabilitar usuarios |
| Sin perfil para usuarios ya existentes | **Backfill automático:** si alguien inicia sesión y no tiene perfil, se le crea |

### 3.2 Archivos del módulo

| Archivo | Rol |
|---|---|
| `lib/models/usuario_perfil.dart` | Modelo `UsuarioPerfil` (uid, email, nombre, telefono, cargo, rol, activo, creadoEn) |
| `lib/repositories/usuario_repository.dart` | CRUD sobre `usuarios/{uid}` + asignación automática de rol |
| `lib/controllers/usuario_controller.dart` | Perfil y rol del usuario autenticado; expone `esAdmin`; escucha cambios de sesión |
| `lib/screens/ajustes/usuarios_admin_screen.dart` | Panel admin: listar, editar, cambiar rol, activar/desactivar, eliminar |

### 3.3 Operaciones CRUD implementadas

| Operación | Método | Descripción | Quién puede |
|---|---|---|---|
| **C**reate | `crearPerfilInicial()` | Crea el perfil al registrarse, con rol automático | El propio usuario |
| **R**ead | `obtenerPorUid()`, `obtenerUsuarioActual()`, `listarTodos()` | Lee un perfil, el perfil propio o todos | Propio usuario o admin |
| **R**ead (tiempo real) | `verTodos()` (Stream) | Escucha la colección y refresca el panel en vivo | Admin |
| **U**pdate | `actualizarDatos()`, `cambiarRol()`, `cambiarActivo()` | Edita datos, cambia rol y activa/desactiva | Propio usuario o admin |
| **D**elete | `eliminar()` | Borra el perfil de Firestore | Admin |

### 3.4 Reglas de seguridad publicadas en Firestore

```js
match /usuarios/{uid} {
  allow read:   if isAuthenticated() && (getUid() == uid || isAdmin());
  allow create: if isAuthenticated() && getUid() == uid;
  allow update: if isAuthenticated() && (getUid() == uid || isAdmin());
  allow delete: if isAdmin();
}
```

### 3.5 Límites conocidos

- El botón **Eliminar** del panel borra el **perfil de Firestore**, pero **no la cuenta de Firebase Authentication** (eso requiere Cloud Functions o hacerlo desde la consola).
- Un usuario eliminado que vuelve a iniciar sesión **recupera su perfil automáticamente**.
- Bloquear realmente el login de un usuario inactivo requeriría **Cloud Functions**.

---

## 4. Pantallas modificadas

| Pantalla | Archivo | Líneas | Cambio principal |
|---|---|---|---|
| Inicio de sesión / Registro | `lib/screens/login_screen.dart` | +131 | Firebase Auth, traducción de errores, campos personales (nombres, apellidos, teléfono, cargo) y creación del perfil |
| Inicio (Dashboard) | `lib/screens/home_screen.dart` | +35 | Nombre desde Firebase, cierre de sesión con Firebase, menú depurado |
| Ajustes | `lib/screens/ajustes/ajustes_screen.dart` | +26 | Opción **"Usuarios (admin)"** visible solo para administradores |
| Control de sesión | `lib/screens/auth_gate.dart` | +11 | `authStateChanges` de Firebase en lugar de Supabase |
| Configuración pendiente | `lib/screens/setup_required_screen.dart` | +6 | Texto actualizado a "Firebase no está configurado" |
| Perfil | `lib/screens/ajustes/perfil_screen.dart` | +4 | Cierre de sesión con Firebase |
| Presentación | `lib/screens/splash_screen.dart` | +2 | Ruta según `firebaseReady` |

---

## 5. Archivos nuevos y eliminados

**Nuevos**
- `lib/firebase_options.dart` *(local, no se publica)*
- `lib/services/firestore_service.dart`
- `lib/models/usuario_perfil.dart`
- `lib/repositories/usuario_repository.dart`
- `lib/repositories/firestore_registro_repository.dart`
- `lib/controllers/usuario_controller.dart`
- `lib/screens/ajustes/usuarios_admin_screen.dart`
- `firebase.json`
- `docs/07_FIRESTORE.md`, `docs/BITACORA_MARTES_2026-09-08.md` (+ `.docx`)
- `scripts/md_a_docx.py`
- Plantillas `*.example`: `lib/firebase_options.example.dart`, `android/app/google-services.example.json`, `assets/config/supabase.example.json`

**Eliminados (limpieza de Supabase)**

| Archivo | Líneas |
|---|---|
| `lib/repositories/supabase_registro_repository.dart` | −51 |
| `supabase/01_SCHEMA_BASE_SESION1.sql` | −52 |
| `supabase/02_MIGRACION_SESION2_CONTEXTO.sql` | −24 |
| `supabase/03_VERIFICAR.sql` | −11 |
| `supabase/04_MIGRACION_SESION3_NOMBRES.sql` | −38 |

---

## 6. Seguridad del repositorio (credenciales)

### 6.1 Situación detectada

El repositorio es **público**, y `assets/config/supabase.json` **ya estaba publicado** con la URL y la publishable key reales del proyecto Supabase. También había archivos de credenciales de Firebase listos para subirse por primera vez.

### 6.2 Medidas aplicadas

| Medida | Detalle |
|---|---|
| `.gitignore` reforzado | Nueva sección de credenciales: Supabase, Firebase, keystores, `.env`, `*.pem`, `*.key`, service accounts |
| Archivos sensibles destrackeados | `assets/config/supabase.json` y `.flutter-plugins-dependencies` salieron del control de versiones (siguen en disco) |
| Plantillas en lugar de secretos | Se publican `*.example.json` / `*.example.dart` con valores de relleno |
| Verificación previa al push | Escaneo de todos los archivos a subir buscando `AIza…`, `sb_publishable_…` y el ref del proyecto: **sin coincidencias** |

### 6.3 ⚠️ Acción pendiente del autor

> Quitar un archivo del repositorio **no lo borra del historial de Git**. La publishable key de Supabase del commit `c937e32` **ya es pública** y debe considerarse comprometida.
>
> **Acción:** entrar al panel de Supabase y **rotar/invalidar esa key** (o eliminar el proyecto, ya que la app migró a Firebase y Supabase quedó sin uso).

---

## 7. Cómo ejecutar el proyecto ahora

```bash
flutter pub get     # SÍ (permitido en el aula)
flutter run         # elige dispositivo: chrome / windows / android
```

| Regla | Estado |
|---|---|
| `flutter pub get` | ✅ Permitido |
| `flutter pub upgrade` | ❌ Prohibido (podría romper dependencias) |
| `--dart-define-from-file` | ❌ Ya no se usa: Firebase va incrustado |
| `config/local.json` | ❌ Ya no se lee (inerte, solo referencia) |

**En una copia nueva del repositorio** hay que recrear la configuración local:

```bash
dart pub global activate flutterfire_cli
flutterfire configure --project=TU-PROYECTO-FIREBASE
```

Eso regenera `lib/firebase_options.dart` y `android/app/google-services.json`. Las plantillas `*.example.*` documentan el formato esperado.

---

## 8. Pendientes y recomendaciones

1. **Rotar la clave de Supabase** (sección 6.3) — es la acción más urgente.
2. **Verificar las reglas de Firestore** publicadas, en especial las de la colección `usuarios`.
3. **Restringir la API key de Firebase** por aplicación y por API en Google Cloud Console.
4. **Actualizar el `README.md`**: todavía describe Supabase como único backend, `config/local.json` y el `--dart-define`; hoy ya no aplica.
5. **Revisar el mensaje "Recordarme"** del login: sigue sin guardar credenciales (limitación heredada).
6. **Unificar los documentos de Supabase** (`docs/03_SUPABASE.md` y `docs/04_SUPABASE.md`): hoy describen un backend que ya no se usa.
