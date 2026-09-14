# 🌱 SIGVACH — Sistema de Gestión de Variables para Cultivos Hidropónicos

## 1. Nombre y descripción del proyecto

**SIGVACH** es una aplicación móvil desarrollada con **Flutter** que permite monitorear y gestionar las principales variables de un cultivo hidropónico: **temperatura, humedad, pH, TDS (conductividad) y nivel de agua**.

Se compone de dos piezas: la **aplicación Flutter** y el **servicio backend** que expone la API y concentra la validación, la autorización y las reglas de negocio (apartado 5).

Forma parte de una **práctica de aula acumulativa** en la que se integran conceptos como asincronía, consumo de API REST, GPS, mapas, persistencia local y autenticación con **Firebase** (Authentication + Cloud Firestore).

> Este proyecto **no es otro proyecto distinto**: es el mismo sistema que crece sesión a sesión (Sesión 1 → Sesión 2 → Proyecto Final 360).

## 2. Problema u objetivo

**Problema:** en un cultivo hidropónico, mantener las variables dentro de sus rangos óptimos es crítico para la salud de las plantas, pero hacerlo de forma manual es lento y propenso a errores, y es difícil detectar a tiempo cuándo una variable sale de rango.

**Objetivo:** ofrecer una aplicación que centralice el registro, el monitoreo y las alertas de las variables de los cultivos, además de servir como proyecto de aprendizaje para aplicar Flutter, asincronía, API REST, GPS, mapas y Firebase.

## 3. Funcionalidades implementadas

| Módulo | Funcionalidad |
|---|---|
| Presentación | Splash con logo, nombre del sistema y animación de aparición. |
| Autenticación | Registro e inicio de sesión con **Firebase Authentication** (correo + contraseña); el perfil del usuario (nombres, apellidos, teléfono, cargo, rol) se guarda en **Cloud Firestore**. |
| Dashboard (Inicio) | Métricas de temperatura, humedad, pH, TDS y nivel de agua; banner de estado y última actualización. |
| Variables | Lista con estado Normal/Fuera de rango; detalle y edición del rango óptimo (mín/máx/unidad). |
| Cultivos | Listar, agregar, ver detalle, ver variables por cultivo y eliminar cultivos. |
| Alertas | Pestañas Activas/Historial; alertas automáticas cuando una variable sale de su rango óptimo; marcar como resuelta. |
| Historial | Rango de fechas, gráfica histórica (CustomPaint) con promedio/máx/mín y lista de mediciones. |
| Contexto | GPS + clima (API Open-Meteo) y registro de un snapshot de contexto. |
| Usuarios (admin) | Panel de gestión de usuarios: listar, editar datos, cambiar rol, activar/desactivar y eliminar. Visible solo para el rol `admin`. |
| Ajustes | Perfil (nombre/cargo), tema claro/oscuro, opciones y rangos de variables. |
| Persistencia | Datos locales con SharedPreferences (dashboard, cultivos, alertas, mediciones, perfil, rangos). |

## 4. Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Flutter / Dart | Framework y lenguaje (Material 3). |
| Provider | Gestión de estado. |
| Firebase Authentication | Registro e inicio de sesión (correo/contraseña). |
| Cloud Firestore | Base de datos NoSQL (perfiles de usuario en `usuarios/{uid}`). |
| FastAPI sobre Python 3.13 | Backend del sistema: expone el contrato de la API, valida los datos, autoriza por rol y aplica las reglas de negocio. |
| SharedPreferences | Persistencia local en el dispositivo. |
| HTTP + Open-Meteo | Consumo de API REST para el clima. |
| flutter_launcher_icons | Generación de iconos de la app. |

**Versiones principales (`pubspec.yaml`):** `provider 6.1.5+1`, `shared_preferences 2.5.5`, `firebase_core ^4.14.0`, `firebase_auth ^6.6.1`, `cloud_firestore ^6.9.0`, `http 1.6.0`, `geolocator 14.0.3`, `flutter_map 8.3.2`, `latlong2 0.10.1`.

## 5. Backend de la API

El sistema cuenta además con un **servicio backend** (FastAPI sobre Python 3.13) que expone el contrato de la API, valida los datos de entrada, autoriza cada operación según el rol y es el único componente que accede a Cloud Firestore. Ni la aplicación ni el módulo de adquisición tocan la base de datos directamente.

| Componente | Responsabilidad |
|---|---|
| Aplicación Flutter | Presenta la información y recoge los datos del usuario; no decide reglas de negocio |
| Backend (API REST) | Autentica, valida, autoriza y aplica las reglas de negocio |
| Cloud Firestore | Guarda el estado del dominio |

- Código y documentación del servicio: [`backend/README.md`](backend/README.md)
- Ejecución local en modo de demostración, sin credenciales: desde `backend/`, con `USAR_REPOSITORIO_EN_MEMORIA=true`, ejecutar `uvicorn app.main:app --reload`
- Contrato navegable del servicio (OpenAPI): `http://localhost:8000/docs`
- Pruebas automatizadas del backend: `python -m pytest` desde `backend/` (54 casos, sin credenciales ni conexión)
- Apuntar la aplicación al backend, sin editar el código:

```bash
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000        # emulador de Android
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000
flutter build web --dart-define=API_BASE_URL=https://TU-API.onrender.com
```

Si no se define `API_BASE_URL`, la aplicación usa una dirección local adecuada al dispositivo
(`10.0.2.2` en el emulador de Android y `localhost` en la web y el escritorio).

## 6. Requisitos para ejecutar el proyecto

- Flutter SDK **>= 3.35.0** y Dart **>= 3.9.0**.
- Editor (VS Code con extensión Flutter, o Android Studio).
- Un proyecto **Firebase** con **Authentication** (correo/contraseña) y **Cloud Firestore** habilitados.
- Los archivos de configuración de Firebase: `lib/firebase_options.dart` y `android/app/google-services.json`. **No se publican en el repositorio**: se generan con `flutterfire configure` (ver sección 7).
- Dispositivo **Android** (o Chrome para probar).

> ℹ️ La configuración de Firebase va **incrustada** en la app: no hace falta `--dart-define` ni archivos `.json` sueltos.

> ⚠️ Regla de estabilidad del aula: `flutter pub get` **SÍ** — `flutter pub upgrade` **NO** (podría romper dependencias).

## 7. Instrucciones de instalación y ejecución

### Windows

1. Extrae el proyecto en una ruta corta, por ejemplo: `C:\flutter_aula\PROYECTO_FINAL_360_SESION2_FINAL`
2. Ejecuta `scripts\00_PREPARAR_WINDOWS.bat`
3. Luego `scripts\02_MENU_WINDOWS.bat`
4. Elige Android o Chrome.

> Windows Desktop **no** es requisito para esta clase.

### Linux (MX)

1. Extrae el proyecto dentro de tu HOME.
2. `chmod +x scripts/*.sh`
3. `./scripts/00_PREPARAR_LINUX.sh`
4. `./scripts/01_MENU_LINUX.sh`
5. Si aparece error de Ninja: `./scripts/98_REPARAR_NINJA_LINUX.sh`

### Configuración de Firebase

El proyecto usa **Firebase** (Authentication + Cloud Firestore). No hay modo DEMO.

La configuración va incrustada en `lib/firebase_options.dart`, así que para ejecutar no hace falta crear **ningún** archivo:

```powershell
flutter pub get
flutter run
```

**En una copia nueva del repositorio** (los archivos de configuración no se publican por seguridad) hay que generarlos:

```powershell
dart pub global activate flutterfire_cli
flutterfire configure --project=TU-PROYECTO-FIREBASE
```

Eso crea `lib/firebase_options.dart` y `android/app/google-services.json`. Las plantillas `lib/firebase_options.example.dart` y `android/app/google-services.example.json` muestran el formato esperado.

> ⚠️ Los archivos con las API keys de Firebase (`lib/firebase_options.dart` y `android/app/google-services.json`) están en `.gitignore`: **nunca** se suben al repositorio. La plantilla de las variables de entorno, incluida la del backend, está en `.env.example` (ver sección 7).

## 8. Estructura general del proyecto

```
lib/
├── main.dart                # Punto de entrada: inicializa Firebase y los providers
├── app.dart                 # MaterialApp (SIGVACH, tema claro/oscuro)
├── firebase_options.dart    # Configuración de Firebase (NO se publica)
├── config/                  # AppConfig (flag firebaseReady)
├── controllers/             # PreferencesController, ContextController, UsuarioController
├── models/                  # cultivo, variable_rango, alerta, medicion, usuario_perfil, snapshots
├── repositories/            # UsuarioRepository (Firestore) + RegistroRepository
├── screens/                 # Splash, Login, Home y módulos: variables, cultivos,
│                            #   alertas, historial, ajustes (incl. usuarios admin), contexto
├── services/                # AuthService, FirestoreService, WeatherService,
│                            #   LocationService, PreferencesService
└── widgets/                 # context_card, max_width_box, mode_banner

backend/                     # servicio de la API (FastAPI): app/ y pruebas/
assets/images/               # logo e iconos de la app
scripts/                     # scripts de preparación y menú (Windows / Linux)
docs/                        # documentación e hilo conductor del proyecto
```

## 9. Procedimiento para generar el APK

### APK de depuración (rápido para probar)

```powershell
flutter build apk --debug
```

- Ruta del APK: `build\app\outputs\flutter-apk\app-debug.apk`

### APK de lanzamiento (para distribución)

```powershell
flutter build apk --release
```

- Ruta del APK: `build\app\outputs\flutter-apk\sigvach_1.0.0+1.apk`

### Instalación en un teléfono

1. Conecta el celular por USB (con depuración USB activada).
2. Ejecuta `flutter install`, o copia el archivo `sigvach_1.0.0+1.apk` al teléfono e instálalo manualmente.

> 📌 El APK de release incluye la configuración de Firebase compilada dentro de la app (vía `lib/firebase_options.dart`). No es necesario usar `--dart-define`.

## 10. Versión entregada

- **Versión:** `1.0.0+1` (definida en `pubspec.yaml`).
- **Sesión / etapa:** Sesión 2 — Proyecto Final SIGVACH.
- **Plataforma objetivo:** Android (y web para pruebas).

## 11. Limitaciones conocidas

- Los valores del dashboard se editan manualmente; **aún no** están conectados a sensores reales.
- La gráfica del historial simula el filtro por periodo (3/6/12 meses) con `take()`.
- La casilla "Recordarme" del login aún no guarda las credenciales en preferencias.
- La gestión de datos del dominio a través de la API todavía no está integrada en la aplicación: el servicio de API está implementado y probado (54 casos) y la aplicación ya cuenta con su cliente de API y sus pruebas (16 casos), pero falta conectar las pantallas y los repositorios, de modo que los módulos de cultivos, lecturas, alertas y rangos siguen persistiendo en el dispositivo (`SharedPreferences`).
- Está pensado para Android/web; Windows Desktop no es requisito de la clase.
- La confirmación por correo del registro depende de la configuración de Firebase Authentication.
- **Eliminar** un usuario desde el panel borra su perfil de Firestore, pero **no** su cuenta de Authentication (requeriría Cloud Functions).

## 12. Autor del proyecto

- **Autor:** Freddy Santos N.
- **Proyecto / Materia:** Proyecto SIGVACH — Programación de aplicaciones móviles (Flutter).
- **Año:** 2026