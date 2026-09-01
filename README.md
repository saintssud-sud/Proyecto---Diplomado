# 🌱 SIGVACH — Sistema de Gestión de Variables para Cultivos Hidropónicos

## 1. Nombre y descripción del proyecto

**SIGVACH** es una aplicación móvil desarrollada con **Flutter** que permite monitorear y gestionar las principales variables de un cultivo hidropónico: **temperatura, humedad, pH, TDS (conductividad) y nivel de agua**.

Forma parte de una **práctica de aula acumulativa** en la que se integran conceptos como asincronía, consumo de API REST, GPS, mapas, persistencia local y autenticación con Supabase.

> Este proyecto **no es otro proyecto distinto**: es el mismo sistema que crece sesión a sesión (Sesión 1 → Sesión 2 → Proyecto Final 360).

## 2. Problema u objetivo

**Problema:** en un cultivo hidropónico, mantener las variables dentro de sus rangos óptimos es crítico para la salud de las plantas, pero hacerlo de forma manual es lento y propenso a errores, y es difícil detectar a tiempo cuándo una variable sale de rango.

**Objetivo:** ofrecer una aplicación que centralice el registro, el monitoreo y las alertas de las variables de los cultivos, además de servir como proyecto de aprendizaje para aplicar Flutter, asincronía, API REST, GPS, mapas y Supabase.

## 3. Funcionalidades implementadas

| Módulo | Funcionalidad |
|---|---|
| Presentación | Splash con logo, nombre del sistema y animación de aparición. |
| Autenticación | Registro e inicio de sesión con Supabase (email + contraseña); guarda el nombre del usuario. |
| Dashboard (Inicio) | Métricas de temperatura, humedad, pH, TDS y nivel de agua; banner de estado y última actualización. |
| Variables | Lista con estado Normal/Fuera de rango; detalle y edición del rango óptimo (mín/máx/unidad). |
| Cultivos | Listar, agregar, ver detalle, ver variables por cultivo y eliminar cultivos. |
| Alertas | Pestañas Activas/Historial; alertas automáticas cuando una variable sale de su rango óptimo; marcar como resuelta. |
| Historial | Rango de fechas, gráfica histórica (CustomPaint) con promedio/máx/mín y lista de mediciones. |
| Contexto | GPS + clima (API Open-Meteo) y registro de un snapshot de contexto en Supabase. |
| Ajustes | Perfil (nombre/cargo), tema claro/oscuro, opciones y rangos de variables. |
| Persistencia | Datos locales con SharedPreferences (dashboard, cultivos, alertas, mediciones, perfil, rangos). |

## 4. Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Flutter / Dart | Framework y lenguaje (Material 3). |
| Provider | Gestión de estado. |
| Supabase | Autenticación y base de datos (único modo de este proyecto). |
| SharedPreferences | Persistencia local en el dispositivo. |
| HTTP + Open-Meteo | Consumo de API REST para el clima. |
| flutter_launcher_icons | Generación de iconos de la app. |

**Versiones principales (`pubspec.yaml`):** `provider 6.1.5+1`, `shared_preferences 2.5.5`, `supabase_flutter 2.17.2`, `http 1.6.0`, `geolocator 14.0.3`, `flutter_map 8.3.2`, `latlong2 0.10.1`.

## 5. Requisitos para ejecutar el proyecto

- Flutter SDK **>= 3.35.0** y Dart **>= 3.9.0**.
- Editor (VS Code con extensión Flutter, o Android Studio).
- Un proyecto **Supabase** con las tablas y políticas aplicadas (SQL en `supabase/`).
- Archivo `config/local.json` con `SUPABASE_URL` y `SUPABASE_PUBLISHABLE_KEY` (solo necesario para desarrollo con `flutter run`).
- Dispositivo **Android** (o Chrome para probar).

> ℹ️ Para el **APK de release** no necesitas `--dart-define`: la configuración de Supabase va empaquetada en `assets/config/supabase.json`.

> ⚠️ Regla de estabilidad del aula: `flutter pub get` **SÍ** — `flutter pub upgrade` **NO** (podría romper dependencias).

## 6. Instrucciones de instalación y ejecución

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

### Configuración de Supabase (único modo)

Este proyecto usa **solo** la parte final (Supabase). No hay modo DEMO.

1. Ejecuta el SQL de `supabase/` en tu proyecto Supabase.
2. Crea `config/local.json` a partir de `config/local.example.json` (Project URL + Publishable Key).
3. Ejecuta la app:
   ```powershell
   flutter run --dart-define-from-file=config/local.json
   ```

> ⚠️ Nunca pongas `service_role` ni secret keys dentro de Flutter.

## 7. Estructura general del proyecto

```
lib/
├── main.dart                # Punto de entrada: inicializa Supabase y los providers
├── app.dart                 # MaterialApp (SIGVACH, tema claro/oscuro)
├── config/                  # AppConfig (config desde --dart-define o asset empaquetado)
├── controllers/             # PreferencesController, ContextController
├── models/                  # cultivo, variable_rango, alerta, medicion, registro, snapshots
├── repositories/            # RegistroRepository + SupabaseRegistroRepository
├── screens/                 # Splash, Login, Home y módulos: variables, cultivos,
│                            #   alertas, historial, ajustes, contexto
├── services/                # AuthService, WeatherService, LocationService, PreferencesService
└── widgets/                 # context_card, max_width_box, mode_banner

assets/images/               # logo e iconos de la app
assets/config/               # supabase.json (config empaquetada para el APK de release)
config/                      # local.json (configuración de Supabase, para desarrollo)
scripts/                     # scripts de preparación y menú (Windows / Linux)
supabase/                    # scripts SQL (schema base y migraciones)
docs/                        # documentación e hilo conductor del proyecto
```

## 8. Procedimiento para generar el APK

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

> 📌 El APK de release incluye la configuración de Supabase empaquetada en `assets/config/supabase.json` (solo la Publishable Key pública, nunca claves secretas). No es necesario usar `--dart-define` para compilar el APK final.

## 9. Versión entregada

- **Versión:** `1.0.0+1` (definida en `pubspec.yaml`).
- **Sesión / etapa:** Sesión 2 — Proyecto Final SIGVACH.
- **Plataforma objetivo:** Android (y web para pruebas).

## 10. Limitaciones conocidas

- Los valores del dashboard se editan manualmente; **aún no** están conectados a sensores reales.
- La gráfica del historial simula el filtro por periodo (3/6/12 meses) con `take()`.
- La casilla "Recordarme" del login aún no guarda las credenciales en preferencias.
- El proyecto usa **solo el modo Supabase** (no hay modo demo).
- Está pensado para Android/web; Windows Desktop no es requisito de la clase.
- La confirmación por correo del registro depende de la configuración del proyecto Supabase.

## 11. Autor del proyecto

- **Autor:** Freddy Carlo Santos Navarro
- **Proyecto / materia:** Proyecto SIGVACH — Programación de aplicaciones móviles (Flutter).
- **Año:** 2026