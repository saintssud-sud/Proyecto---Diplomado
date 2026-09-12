# 📓 Bitácora — Martes 8 de septiembre de 2026

**Proyecto:** SIGVACH — Sistema de Gestión de Variables para Cultivos Hidropónicos
**Objetivo del día:** Migrar el backend de Supabase a **Firebase** (Authentication + Cloud Firestore), conectar la app a Firestore en Android/Web/Windows, eliminar el módulo "registros" ajeno al proyecto, e implementar un **sistema completo de gestión de usuarios** con rol admin y CRUD.

**Backend final del día:** Firebase (proyecto `sigvach26-bd`) — Authentication (correo/contraseña) + Cloud Firestore.

---

## 1. Actividades realizadas

### 1.1 Conexión de Firebase y Firestore al proyecto
- Se agregaron las dependencias oficiales al `pubspec.yaml`:
  ```yaml
  firebase_core: ^4.14.0
  cloud_firestore: ^6.9.0
  firebase_auth: ^6.6.1
  ```
- Se instaló la **FlutterFire CLI** (herramienta global) con:
  ```powershell
  dart pub global activate flutterfire_cli
  ```
- Se re-autenticó la Firebase CLI (el token estaba vencido) con `firebase login --reauth`.

### 1.2 Registro de la app en Firebase Console (proyecto sigvach26-bd)
- Se registraron las 3 apps con la FlutterFire CLI:
  ```powershell
  & "$env:...\flutter_pub_cache\bin\flutterfire" configure `
    --project=sigvach26-bd --platforms=android,web,windows --yes
  ```
- Resultado:
  - App **Android** (`bo.edu.uajms.sigvach`)
  - App **Web** (`sigvach (web)`)
  - App **Windows** (`sigvach (windows)`)
- Se generó `lib/firebase_options.dart` con la configuración de las 3 plataformas.

### 1.3 Configuración de Android
- La FlutterFire CLI generó automáticamente:
  - `android/app/google-services.json`
  - Plugin de Google Services en `android/settings.gradle.kts` (bloque `// START: FlutterFire Configuration`)
  - Plugin en `android/app/build.gradle.kts`

### 1.4 Base de datos Firestore
- Se confirmó que la base de datos `(default)` ya existía (región `southamerica-west1`).
- Se habilitó el proveedor **Correo electrónico/contraseña** en **Firebase Authentication** (Método de acceso).

### 1.5 Migración completa: Supabase → Firebase Auth
Se reemplazó todo el código de Supabase por Firebase:

| Archivo | Cambio |
|---|---|
| `lib/services/auth_service.dart` | Reescrito: `signIn`/`signUp`/`signOut` con **Firebase Auth** (guarda `displayName`) |
| `lib/screens/auth_gate.dart` | Usa `authStateChanges` de Firebase en lugar de Supabase |
| `lib/screens/login_screen.dart` | Login/registro con Firebase; traduce códigos de error a mensajes claros |
| `lib/screens/home_screen.dart` | Nombre del usuario desde Firebase; cierre de sesión con Firebase |
| `lib/screens/ajustes/ajustes_screen.dart` | Cierre de sesión con Firebase |
| `lib/screens/ajustes/perfil_screen.dart` | Cierre de sesión con Firebase |
| `lib/screens/splash_screen.dart` | Ruta según `firebaseReady` (AppConfig) |
| `lib/screens/setup_required_screen.dart` | Texto actualizado a "Firebase no está configurado" |
| `lib/config/app_config.dart` | Simplificado (ya no lee Supabase; `firebaseReady` + `modeLabel='FIREBASE'`) |
| `lib/main.dart` | Inicializa Firebase con try/catch; provee `AuthService`, `FirestoreService`, `UsuarioController` |

### 1.6 Eliminación de Supabase
- Se quitó la dependencia `supabase_flutter`:
  ```powershell
  flutter pub remove supabase_flutter
  ```
- Se eliminó `lib/repositories/supabase_registro_repository.dart`.
- Quedaron inertes (ya no se leen) `config/local.json` y `assets/config/supabase.json` (referencia del aula; no se borraron por regla).

### 1.7 Limpieza del módulo "registros" (proyecto base)
- El módulo "Mis registros" (`RecordsScreen`, repositorio, etc.) **no pertenece al SIGVACH real**: vino de un proyecto base.
- Decisión del usuario: **desconectarlo**.
  - Se quitó la entrada del menú y el `Provider<RegistroRepository>`/`FirestoreRegistroRepository` de `main.dart`.
  - Se eliminó la colección `registros` de Firestore y su regla de seguridad en la consola.

---

## 2. Sistema de gestión de usuarios (CRUD con rol admin)

### 2.1 Diseño elegido (Camino B + Opción 2)
- **Camino B** (sin Cloud Functions, plan Spark): auto-registro con datos personales + panel de admin.
- **Opción 2**: el rol `admin` se asigna automáticamente SOLO al correo `admin@sigvach.com`; cualquier otro correo queda como `usuario`.

### 2.2 Archivos nuevos
| Archivo | Rol |
|---|---|
| `lib/models/usuario_perfil.dart` | Modelo `UsuarioPerfil` (uid, email, nombre, telefono, cargo, rol, activo, creadoEn) |
| `lib/repositories/usuario_repository.dart` | CRUD sobre Firestore `usuarios/{uid}` + asignación automática de rol |
| `lib/controllers/usuario_controller.dart` | Perfil/rol del usuario autenticado (exposición `esAdmin`); escucha cambios de sesión |
| `lib/screens/ajustes/usuarios_admin_screen.dart` | Panel admin: listar, editar, cambiar rol, activar/desactivar, eliminar |

### 2.3 Modificaciones para el sistema de usuarios
- `lib/screens/login_screen.dart`: el registro ahora pide **Nombres, Apellidos, Teléfono, Cargo** + correo + contraseña; al registrarse crea la cuenta en Auth **y** el perfil en Firestore; si un usuario ya existente inicia sesión sin perfil, se lo crea automáticamente.
- `lib/main.dart`: registra `UsuarioRepository` y `UsuarioController` como providers.
- `lib/screens/ajustes/ajustes_screen.dart`: muestra la opción **"Usuarios (admin)"** solo cuando el usuario autenticado es admin.

### 2.4 Estructura de datos (Firestore)
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
> El **id del documento = UID de Firebase Authentication** (así se vincula la cuenta con el perfil).

### 2.5 Regla de Firestore publicada (para que el admin pueda editar)
```js
match /usuarios/{uid} {
  allow read:   if isAuthenticated() && (getUid() == uid || isAdmin());
  allow create: if isAuthenticated() && getUid() == uid;
  allow update: if isAuthenticated() && (getUid() == uid || isAdmin());
  allow delete: if isAdmin();
}
```

### 2.6 Usuarios creados y verificados (Chrome/Web)
| Usuario | Rol | Estado |
|---|---|---|
| `admin@sigvach.com` | `admin` | ✅ login + panel "Usuarios (admin)" |
| `operador1@sigvach.com` | `usuario` | ✅ registro con datos personales |
| `tecnico@gmail.com` | `usuario` | ✅ registro con datos personales |
| `prueba.firestore@ejemplo.com` | `usuario` | ✅ registro/login (creado antes) |

- Se verificó en vivo:
  - Registro con datos personales → perfil creado en Firestore con rol correcto.
  - Login como admin → aparece la opción **"Usuarios (admin)"**.
  - Panel lista los usuarios y las acciones de editar/cambiar rol/activar-desactivar/eliminar **se reflejan en Firestore en tiempo real** (ej. cambio de nombre de "Operador Uno" a "Lucio Navarro").

### 2.7 Límites conocidos (Camino B)
- "Eliminar" desde el panel borra el **perfil de Firestore**, pero **no** la cuenta de **Firebase Authentication** (eso requiere Cloud Functions o hacerlo en la consola).
- Un usuario "eliminado" que vuelve a iniciar sesión se **recrea el perfil** automáticamente.
- Para borrado real desde la app o bloquear el login de inactivos se necesitaría **Cloud Functions** (Camino A).

---

## 3. Comandos utilizados

| Comando | Uso |
|---|---|
| `flutter pub get` | Descargar dependencias (permitido en el aula). |
| `flutter pub upgrade` | ❌ PROHIBIDO (podría romper dependencias). |
| `flutter pub add firebase_core cloud_firestore firebase_auth` | Agregar dependencias de Firebase. |
| `flutter pub remove supabase_flutter` | Quitar Supabase. |
| `dart pub global activate flutterfire_cli` | Instalar la FlutterFire CLI. |
| `flutterfire configure --project=sigvach26-bd --platforms=android,web,windows --yes` | Registrar apps y generar `firebase_options.dart`. |
| `firebase login --reauth` | Re-autenticar la Firebase CLI. |
| `flutter analyze` | Verificar que no haya errores de análisis. |
| `flutter run -d chrome` | Ejecutar la app en Chrome. |
| `flutter run -d web-server --web-port=8091` | Ejecutar la app como servidor web para probar. |

---

## 4. Cómo correr la app (NUEVO)

La configuración de Firebase va **incrustada** en `lib/firebase_options.dart`, por lo que **ya NO hace falta** `config/local.json` ni `--dart-define-from-file`.

```bash
flutter pub get     # SÍ (permitido)
flutter run         # elige dispositivo (chrome / windows / android)
```

---

## 5. Archivos modificados/creados (resumen)

**Nuevos:**
- `lib/firebase_options.dart`
- `lib/models/usuario_perfil.dart`
- `lib/repositories/usuario_repository.dart`
- `lib/controllers/usuario_controller.dart`
- `lib/screens/ajustes/usuarios_admin_screen.dart`
- `docs/07_FIRESTORE.md`
- `android/app/google-services.json`

**Modificados:**
- `pubspec.yaml`
- `lib/main.dart`
- `lib/app.dart`
- `lib/services/auth_service.dart`
- `lib/screens/auth_gate.dart`
- `lib/screens/login_screen.dart`
- `lib/screens/home_screen.dart`
- `lib/screens/splash_screen.dart`
- `lib/screens/setup_required_screen.dart`
- `lib/screens/ajustes/ajustes_screen.dart`
- `lib/screens/ajustes/perfil_screen.dart`
- `lib/config/app_config.dart`
- `android/settings.gradle.kts`
- `android/app/build.gradle.kts`

**Eliminados / desconectados:**
- `lib/repositories/supabase_registro_repository.dart` *(eliminado)*
- Módulo "registros" *(desconectado de `main.dart` y del menú; no pertenece al SIGVACH)*
- Colección `registros` de Firestore y su regla *(eliminadas en la consola)*

---

## 6. Pendientes / siguientes pasos
- [ ] Probar `flutter run` en **Windows** y en un dispositivo/emulador **Android** reales (solo se probó Chrome/Web).
- [ ] (Opcional) Implementar **Cloud Functions** (Camino A) para: borrado real de cuentas desde la app, bloquear login de usuarios inactivos y que el admin cree cuentas de login ajenas.
- [ ] Conectar los módulos reales del SIGVACH (dashboard/cultivos/variables/alertas) a Firestore cuando se requiera (hoy quedaron en SharedPreferences, según decisión de aula).
- [ ] Documentar en Word la sección de Firebase/gestión de usuarios para repaso (material de estudio del usuario).
