# 📓 Bitácora — Sábado 30 de agosto de 2026

**Proyecto:** SIGVACH — Sistema de Gestión de Variables para Cultivos Hidropónicos
**Objetivo del día:** Preparar la identidad visual del proyecto (splash, icono, login, dashboard), unificar el color de marca y dejar todo listo para generar el APK.

---

## 1. Actividades realizadas

### 1.1 Pantalla de presentación (Splash)
- Se creó `lib/screens/splash_screen.dart` con la pantalla de carga inicial.
- Se usó la imagen real del logo en `assets/images/logo.png` (gota de agua azul con hoja).
- Diseño final: fondo verde neón, logo en recuadro blanco redondeado, texto **S.I.G.V.A.C.H.**, subtítulo "Sistema de Gestión de Variables para Cultivos Hidropónicos", indicador de carga y texto "Cargando...".
- El splash navega automáticamente al `LoginScreen` (o a la pantalla de configuración si no hay Supabase).

### 1.2 Registro de assets
- En `pubspec.yaml` se declaró la carpeta de recursos:
  ```yaml
  flutter:
    uses-material-design: true
    assets:
      - assets/images/
  ```

### 1.3 Icono de la aplicación
- Se creó `assets/images/icon.png` (1024×1024): fondo verde, tarjeta blanca redondeada y el logo centrado.
- Se agregó `flutter_launcher_icons` como dependencia de desarrollo y su configuración en `pubspec.yaml`.
- Se generaron todos los tamaños del icono para **Android** (normales + adaptativos) y **web**:
  ```powershell
  dart run flutter_launcher_icons
  ```
- Se crearon las carpetas `mipmap-anydpi-v26/`, `drawable-*/` y el `colors.xml` del icono adaptativo.

### 1.4 Nombre de la app: SIGVACH
- `android/app/src/main/AndroidManifest.xml` → `android:label="SIGVACH"`.
- `lib/app.dart` → `title: 'SIGVACH'` (pestaña del navegador / conmutador de tareas).
- `web/index.html` y `web/manifest.json` → título y descripción actualizados a SIGVACH.

### 1.5 Pantalla de inicio de sesión (Login)
- Se rediseñó `lib/screens/login_screen.dart` según la imagen de referencia:
  - Encabezado verde con logo, **S.I.G.V.A.C.H.** y "Inicia sesión para continuar".
  - Campo **Usuario** (icono de persona) y **Contraseña** (icono de candado + ojo para mostrar/ocultar).
  - Casilla **Recordarme**.
  - Botón verde **Iniciar Sesión** con icono de acceso.
  - Enlace para alternar entre "Iniciar sesión" y "Crear cuenta".

### 1.6 Pantalla principal (Dashboard)
- Se rediseñó `lib/screens/home_screen.dart` como tablero principal:
  - Barra superior verde con título "Dashboard Principal" y menú lateral (hamburguesa a la izquierda).
  - Tarjeta de bienvenida ("Bienvenido de nuevo").
  - Cuadrícula 2×2 de métricas: **Temperatura 22.8 °C**, **pH 5.9**, **Conductividad 1.59 mS/cm**, **Nivel de Agua 72 %**.
  - Tarjeta "Estado del sistema" (sensores operativos, sincronización en línea, alertas).
- Toda la navegación (Mis registros, Conexión con el mundo, Preferencias, Adaptar a mi proyecto) se movió al menú lateral, junto con "Cerrar sesión".

### 1.7 Color de marca (verde neón)
- Se unificó el color de marca en **verde neón `#39B54A`** en: splash, login, dashboard, icono de la app, `colors.xml` y `web/manifest.json`.

---

## 2. Comandos utilizados

| Comando | Uso |
|---|---|
| `flutter pub get` | Descargar dependencias (permitido en el aula). |
| `flutter pub upgrade` | ❌ PROHIBIDO (podría romper dependencias). |
| `flutter analyze` | Verificar que no haya errores de análisis. |
| `dart run flutter_launcher_icons` | Generar/regenerar los iconos de Android y web. |
| `flutter run --dart-define-from-file=config/local.json` | Ejecutar la app con la configuración de Supabase. |

---

## 3. Generación del APK

Para generar el APK instalable del proyecto:

### APK de depuración (rápido para probar)
```powershell
flutter build apk --debug
```
- Ruta del APK: `build\app\outputs\flutter-apk\app-debug.apk`

### APK de lanzamiento (para distribución)
```powershell
flutter build apk --release --dart-define-from-file=config/local.json
```
- Ruta del APK: `build\app\outputs\flutter-apk\app-release.apk`

> 📌 **Nota:** se usa `--dart-define-from-file=config/local.json` para que el APK incluya la configuración de Supabase (URL + Publishable Key). No tocar `config/local.json` (contiene claves del aula).

### Instalación en un teléfono
1. Conecta el celular por USB (con depuración USB activada).
2. Ejecuta:
   ```powershell
   flutter install
   ```
   o copia el archivo `app-release.apk` al teléfono e instálalo manualmente.

---

## 4. Archivos modificados (resumen)

- `lib/screens/splash_screen.dart` *(nuevo)*
- `lib/screens/login_screen.dart`
- `lib/screens/home_screen.dart`
- `lib/app.dart`
- `pubspec.yaml`
- `android/app/src/main/AndroidManifest.xml`
- `android/app/src/main/res/values/colors.xml`
- `android/app/src/main/res/mipmap-*/ic_launcher.png`
- `android/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml`
- `android/app/src/main/res/drawable-*/ic_launcher_foreground.png`
- `assets/images/icon.png` *(nuevo)*
- `web/manifest.json`
- `web/index.html`
- `web/icons/*`

---

## 5. Pendientes / siguientes pasos
- [ ] Conectar los valores del dashboard (Temperatura, pH, Conductividad, Nivel de Agua) a datos reales (sensor/API).
- [ ] Conectar la casilla "Recordarme" del login a `shared_preferences`.
- [ ] Generar y probar el APK final en un dispositivo físico.
