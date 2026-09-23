# 🌱 SIGVACH — Sistema de Gestión de Variables para Cultivos Hidropónicos

[![Verificación](https://github.com/saintssud-sud/Proyecto---Diplomado/actions/workflows/verificacion.yml/badge.svg)](https://github.com/saintssud-sud/Proyecto---Diplomado/actions/workflows/verificacion.yml)

> El distintivo anterior muestra el resultado de la verificación automática: análisis del código,
> pruebas del servicio y de la aplicación, y compilación de la versión web. Se ejecuta en cada
> confirmación publicada en la rama principal.

## 1. Nombre y descripción del proyecto

**SIGVACH** es una aplicación desarrollada con **Flutter** —para Android y web— que permite monitorear y gestionar las **siete variables** de un cultivo hidropónico: **pH, sólidos disueltos totales, conductividad eléctrica, temperatura de la solución, temperatura ambiental, humedad relativa y nivel de agua**. Las mediciones se evalúan contra los **rangos de referencia del cultivo** que se siembra en cada módulo, y el sistema genera una alerta cuando un valor sale de rango.

Se compone de dos piezas: la **aplicación Flutter** y el **servicio backend** que expone la API y concentra la validación, la autorización y las reglas de negocio (apartado 5).

Se desarrolla como **trabajo final del Módulo 4** del Diplomado en Desarrollo Web y Aplicaciones Móviles (UAJMS), e integra autenticación con **Firebase** (Authentication + Cloud Firestore), consumo de un servicio propio con **API REST**, y su publicación en la nube.

**El sistema está publicado y en funcionamiento:**

| Componente | Dirección |
|---|---|
| Aplicación web | https://sigvach26-bd.web.app |
| Servicio (API) | https://sigvach-api.onrender.com |
| Documentación interactiva de la API | https://sigvach-api.onrender.com/docs |

El **archivo instalable de Android** se compila apuntando al servicio publicado, de modo que la aplicación funciona desde cualquier red, sin depender del equipo del autor. El repositorio conserva además el histórico del proyecto de aula del que proviene: el mismo sistema, que fue creciendo sesión a sesión.

## 2. Problema u objetivo

**Problema:** en un cultivo hidropónico, mantener las variables dentro de sus rangos óptimos es crítico para la salud de las plantas, pero hacerlo de forma manual es lento y propenso a errores, y es difícil detectar a tiempo cuándo una variable sale de rango.

**Objetivo:** centralizar el registro, el monitoreo y las alertas de las variables de un módulo de cultivo hidropónico piloto, de modo que la información medida conserve su valor: que permita observar la evolución de cada variable, compararla contra el rango de referencia del cultivo y avisar cuando un valor sale de rango.

## 3. Funcionalidades implementadas

| Módulo | Funcionalidad |
|---|---|
| Módulo | Funcionalidad |
|---|---|
| Presentación | Splash con logo, nombre del sistema y animación de aparición. |
| Autenticación | Registro e inicio de sesión con **Firebase Authentication** (correo + contraseña); el perfil del usuario (nombres, apellidos, teléfono, cargo, rol) se guarda en **Cloud Firestore** y se consulta a través del servicio. |
| Inicio (panel) | Las **siete variables** del módulo vigente, con su último valor, su rango de referencia y su estado; aviso de alertas activas, selector de módulo y registro de mediciones manuales. |
| Variables | Detalle de las siete variables del módulo, contra los rangos del cultivo que se siembra en él. |
| Módulo | Alta, edición, activación y baja de los módulos de cultivo; cada uno se asocia a un cultivo y a una ubicación. |
| Cultivos | Catálogo de especies con sus **rangos de referencia** (lechuga, acelga, apio u otra hortaliza): alta, edición de rangos y baja. |
| Alertas | Pestañas Activas/Historial **del módulo vigente**; las genera el **servicio** cuando una lectura sale del rango del cultivo; se marcan como atendidas. |
| Historial | Consulta al servicio por variable y período, con promedio, máximo y mínimo calculados por el servicio, gráfica y listado. |
| Contexto | GPS + clima (API Open-Meteo) y registro de un snapshot de contexto. |
| Usuarios (admin) | Panel de gestión de usuarios: listar, editar datos, cambiar rol, activar/desactivar y eliminar. Visible solo para el rol `admin`. |
| Ajustes | Perfil, tema claro/oscuro y acceso al catálogo de cultivos y a los rangos de referencia. |
| Servicio propio | Todo el dominio —módulos, cultivos, rangos, lecturas y alertas— se gestiona a través de la **API REST** del servicio, que valida, autoriza por rol y es el único componente que accede a la base de datos. |

## 4. Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Flutter / Dart | Framework y lenguaje (Material 3). |
| Provider | Gestión de estado. |
| Firebase Authentication | Registro e inicio de sesión (correo/contraseña). |
| Cloud Firestore | Base de datos NoSQL (perfiles de usuario en `usuarios/{uid}`). |
| FastAPI sobre Python 3.13 | Backend del sistema: expone el contrato de la API, valida los datos, autoriza por rol y aplica las reglas de negocio. |
| SharedPreferences | Preferencias de la aplicación (tema, opciones). Los datos del dominio **no** se guardan en el dispositivo: viven en la nube y se consultan por la API. |
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
- Contrato navegable del servicio (OpenAPI): `http://localhost:8011/docs` en local, y el publicado en https://sigvach-api.onrender.com/docs
- Pruebas automatizadas del backend: `python -m pytest` desde `backend/` (**87 casos**, sin credenciales ni conexión)
- Apuntar la aplicación al backend, sin editar el código:

```bash
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8011        # emulador de Android
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8011
flutter build web --dart-define=API_BASE_URL=https://sigvach-api.onrender.com
flutter build apk --release --dart-define=API_BASE_URL=https://sigvach-api.onrender.com
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

1. Clona o descarga el repositorio en una ruta corta, por ejemplo `C:\SIGVACH`.
2. Instala las dependencias, desde la raíz del proyecto:

```powershell
flutter pub get
```

3. Ejecuta la aplicación. Hay dos formas:

```powershell
# Menú del proyecto (permite elegir dispositivo o Chrome)
scripts\01_MENU_WINDOWS.bat

# O directamente
flutter run                  # dispositivo Android conectado
flutter run -d chrome        # navegador
```

4. Para comprobar el entorno y ejecutar las verificaciones, existe un diagnóstico:

```powershell
scripts\99_DIAGNOSTICO_WINDOWS.bat
```

> ⚠️ La aplicación necesita **Firebase configurado** (`lib/firebase_options.dart` y
> `android/app/google-services.json`), que no se publican en el repositorio: se
> generan con `flutterfire configure` (sección 6).

### Linux (MX)

1. Clona el proyecto dentro de tu carpeta personal.
2. Instala las dependencias y ejecuta:

```bash
flutter pub get
flutter run -d chrome
```

> La guía detallada para Linux está en [`docs/02_LINUX_MX_SIN_DOLOR.md`](docs/02_LINUX_MX_SIN_DOLOR.md).
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
- **Etapa:** trabajo final del Módulo 4 del Diplomado en Desarrollo Web y Aplicaciones Móviles (UAJMS).
- **Plataforma objetivo:** Android (archivo instalable) y web publicada.
- **Estado:** desplegado y en funcionamiento — aplicación web, servicio y base de datos en la nube.

## 11. Limitaciones conocidas

- El **módulo de adquisición físico** (ESP32) no está conectado de forma permanente: las lecturas se registran desde el dispositivo cuando se lo conecta, o de forma manual con instrumentos portátiles. El servicio admite ambos orígenes y los distingue.
- La **capa gratuita** de la plataforma de alojamiento suspende el servicio por inactividad: la primera petición posterior puede demorar hasta **cincuenta segundos o más**, demora que el requisito no funcional RNF-05 admite de forma explícita.
- El archivo instalable se firma con la **clave de depuración**; una firma propia queda pendiente para su distribución fuera del ámbito académico.
- La aplicación está pensada para **Android y web**; el escritorio no forma parte del alcance.
- La confirmación por correo del registro depende de la configuración de Firebase Authentication.
- **Eliminar** un usuario desde el panel borra su perfil de Firestore, pero **no** su cuenta de Authentication (requeriría Cloud Functions).
- Un **cultivo sin rangos definidos** no permite evaluar sus lecturas: mientras no se le definan, no se generan alertas. La pantalla de rangos lo advierte de forma explícita.

## 12. Autor del proyecto

- **Autor:** Freddy Santos N.
- **Proyecto / Materia:** Proyecto SIGVACH — Programación de aplicaciones móviles (Flutter).
- **Año:** 2026