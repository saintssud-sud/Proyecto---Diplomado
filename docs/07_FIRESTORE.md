# SIGVACH + Firebase/Firestore

Guía de referencia de la migración: **Supabase → Firebase Authentication + Cloud Firestore**.

## 1. Resumen del proyecto en Firebase

- Proyecto Firebase: `sigvach26-bd`
- Base de datos Firestore: `(default)` en región `southamerica-west1`
- Firebase Authentication: proveedor **Correo electrónico/contraseña** habilitado ✅
- Apps registradas: `android` (`bo.edu.uajms.sigvach`), `web`, `windows`
- Archivo de configuración: `lib/firebase_options.dart` (generado por FlutterFire CLI)

## 2. Cómo correr la app

La configuración de Firebase va **incrustada** en `lib/firebase_options.dart`.
Ya NO hace falta `config/local.json` ni `--dart-define-from-file`.

```bash
flutter pub get        # SÍ (permitido en aula)
flutter run            # elige dispositivo (chrome / windows / android)
```

> Regla de aula: `flutter pub upgrade` NO.

## 3. Dependencias nuevas (pubspec.yaml)

| Paquete | Uso |
|---|---|
| `firebase_core` | Núcleo de Firebase |
| `firebase_auth` | Login con correo/contraseña |
| `cloud_firestore` | Base de datos Firestore |

Se eliminó `supabase_flutter`. Los archivos `config/local.json` y
`assets/config/supabase.json` quedaron inertes (la app ya no los lee).

## 4. Arquitectura (patrón igual al anterior)

```
Pantalla (login / records)  →  Service / Repository  →  Firebase
```

| Archivo | Rol |
|---|---|
| `lib/firebase_options.dart` | Opciones de Firebase por plataforma (no tocar) |
| `lib/services/auth_service.dart` | signIn / signUp / signOut (Firebase Auth) |
| `lib/services/firestore_service.dart` | init Firebase + CRUD demo |
| `lib/repositories/firestore_registro_repository.dart` | CRUD colección `registros` |
| `lib/config/app_config.dart` | Solo flag `firebaseReady` + etiqueta de modo |

`FirestoreRegistroRepository` guarda cada registro en la colección `registros`
con el campo `user_id = uid` del usuario autenticado.

## 5. Reglas de Firestore (módulos reales del SIGVACH)

> NOTA: la pantalla/repositorio de "registros" que venía del **proyecto base**
> NO forma parte del SIGVACH real, por lo que quedó **desconectado** (sin
> entrada en el menú y sin provider en `main.dart`). No hace falta publicar
> reglas para la colección `registros`.

Las reglas que publiques deben cubrir SOLO las colecciones que la app real
usa. Cuando conectes un módulo real (por ejemplo guardar lecturas o cultivos
en Firestore), añade su regla correspondiente. Recuerda que Firestore deniega
por defecto todo lo que no esté cubierto por una regla.

## 6. Qué se conserva de Firebase

| Servicio | Estado |
|---|---|
| Firebase Authentication (email/contraseña) | ✅ conectado y en uso (login/registro) |
| Cloud Firestore | ✅ dependencia y servicio base listos (`FirestoreService`) |
| Repositorio `registros` (proyecto base) | ⛔ desconectado (no pertenece al SIGVACH) |

Cuando quieras guardar datos de un módulo real del SIGVACH en Firestore,
usa `FirestoreService` y crea un repositorio propio siguiendo el patrón que
ya quedó documentado en el proyecto.

## 7. Datos que siguen locales (SharedPreferences)

Dashboard (temperatura/humedad/pH/TDS/agua), cultivos, variables, alertas e
historial se siguen guardando en el dispositivo (decisión de aula). Firestore
queda conectado como servicio base, listo para cuando se integre un módulo
real del SIGVACH.

## 8. Sistema de gestión de usuarios (CRUD con rol admin)

### 8.1 Cómo funciona
- **Registro en la app:** cada usuario se registra con sus **datos personales**
  (Nombres, Apellidos, Teléfono, Cargo) + correo + contraseña.
- Al registrarse se crean DOS cosas a la vez:
  1. La cuenta en **Firebase Authentication** (credenciales de acceso).
  2. Su **perfil** en Firestore → colección `usuarios/{uid}` (datos + rol).
- **Rol automático:** solo `admin@sigvach.com` recibe rol `admin`; cualquier
  otro correo recibe rol `usuario`.

### 8.2 Estructura de datos (Firestore)
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
El **id del documento = UID de Firebase Authentication** (así se vincula).

### 8.3 Archivos del módulo
| Archivo | Rol |
|---|---|
| `lib/models/usuario_perfil.dart` | Modelo `UsuarioPerfil` |
| `lib/repositories/usuario_repository.dart` | CRUD Firestore `usuarios/{uid}` + rol automático |
| `lib/controllers/usuario_controller.dart` | Perfil/rol del usuario autenticado (`esAdmin`) |
| `lib/screens/ajustes/usuarios_admin_screen.dart` | Panel admin: listar, editar, cambiar rol, activar/desactivar, eliminar |

### 8.4 Regla de Firestore requerida (ya publicada)
Para que el admin pueda editar el rol de cualquier usuario:
```js
match /usuarios/{uid} {
  allow read:   if isAuthenticated() && (getUid() == uid || isAdmin());
  allow create: if isAuthenticated() && getUid() == uid;
  allow update: if isAuthenticated() && (getUid() == uid || isAdmin());
  allow delete: if isAdmin();
}
```

### 8.5 Cómo entrar como admin
1. Crea `admin@sigvach.com` en **Authentication → Agregar usuario** (correo + contraseña).
2. Inicia sesión en la app con ese correo → se crea su perfil con rol `admin`.
3. Ve a **Ajustes → "Usuarios (admin)"** → panel de CRUD.

### 8.6 Límite conocido (Camino B, sin Cloud Functions)
- **Eliminar** un usuario desde el panel borra su **perfil de Firestore** pero
  **NO** su cuenta de **Firebase Authentication**. Para borrarla del todo:
  Authentication → Usuarios → ⋮ → Eliminar cuenta.
- Si un usuario "eliminado" vuelve a iniciar sesión, se le **recrea el perfil**
  automáticamente.
- Para borrado real desde la app o bloquear login de inactivos, se necesitaría
  **Cloud Functions** (Camino A).

## 9. Usuario de prueba

- Admin: `admin@sigvach.com` (rol admin)
- Operador: `operador1@sigvach.com`
- Otro: `prueba.firestore@ejemplo.com` / `Prueba123456`

Puedes borrarlos en Firebase Console → Authentication → Usuarios.
