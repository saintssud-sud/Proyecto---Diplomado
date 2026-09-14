# Guía de despliegue — SIGVACH

Documento de trabajo. Es la base del **Anexo B (manual de instalación y despliegue)** de la monografía
y del apartado **2.9 Despliegue**.

Al terminar este procedimiento el sistema cumple el **requisito mínimo 1** (desplegado y accesible por
dirección pública, con archivo instalable para Android) y queda evidencia para los requisitos 5, 6, 7 y 8.

---

## 0. Qué se despliega y en qué orden

| Orden | Componente | Plataforma | Requisito que cubre |
|---|---|---|---|
| 1 | Servicio de la API (FastAPI) | Render, capa gratuita | Requisito 1 (la dirección pública del sistema) |
| 2 | Aplicación web (Flutter compilado) | Firebase Hosting | Requisito 1 y 4 |
| 3 | Archivo instalable de Android (APK) | Distribución directa | Requisito 1 (variante móvil) |

**Antes de empezar** hace falta: el repositorio publicado en GitHub (con las confirmaciones ya
subidas), una cuenta en Render y acceso a la consola de Firebase del proyecto.

> ⚠️ Ninguna credencial se escribe en el repositorio. Las claves se cargan en el panel de la
> plataforma y el archivo `.gitignore` ya las excluye.

---

## Parte A · Servicio de la API en Render

### A.1 Crear el servicio

1. Entrar a <https://render.com> y crear una cuenta (se puede con la cuenta de GitHub).
2. **New** → **Blueprint**.
3. Elegir el repositorio del proyecto. Render detecta el archivo `backend/render.yaml` y propone el
   servicio `sigvach-api` con su configuración.
4. Confirmar. Render pide los valores de las variables marcadas con `sync: false`.

> Si se prefiere crear el servicio a mano y no por Blueprint: **New** → **Web Service** → repositorio →
> *Root Directory*: `backend`; *Build Command*: `pip install -r requirements.txt`; *Start Command*:
> `uvicorn app.main:app --host 0.0.0.0 --port $PORT`; *Health Check Path*: `/api/v1/salud`;
> *Instance Type*: Free.

### A.2 Obtener la clave de la cuenta de servicio de Firebase

El backend necesita esta clave para acceder a Cloud Firestore y para verificar los tokens de identidad.

1. Entrar a la <https://console.firebase.google.com/> y abrir el proyecto.
2. **⚙ Proyecto** (arriba a la izquierda) → **Configuración del proyecto** → pestaña **Cuentas de servicio**.
3. **Generar nueva clave privada** → **Generar clave**. Se descarga un archivo `.json`.
4. Guardarlo **fuera del repositorio** (por ejemplo en `D:\credenciales\`, nunca dentro de la carpeta
   del proyecto).

Para pegarlo en el panel de Render conviene convertirlo a una sola línea. En PowerShell:

```powershell
(Get-Content "D:\credenciales\sigvach-service-account.json" -Raw | ConvertFrom-Json | ConvertTo-Json -Compress) | Set-Clipboard
```

Eso deja el JSON completo en el portapapeles, en una sola línea.

### A.3 Cargar las variables de entorno

En el panel del servicio → **Environment** → agregar:

| Variable | Valor |
|---|---|
| `DEVICE_API_KEY` | Una cadena aleatoria larga, distinta de cualquier contraseña. Es la clave con la que el ESP32 publica lecturas. Para generarla: `-join ((48..57) + (65..90) + (97..122) \| Get-Random -Count 48 \| % {[char]$_})` |
| `FIREBASE_PROJECT_ID` | El identificador del proyecto, el mismo que aparece en `lib/firebase_options.dart` |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | El contenido pegado en A.2 (una línea) |
| `ALLOWED_ORIGINS` | La dirección del despliegue web de la Parte C. Mientras no exista, usar `http://localhost:8080` y completarla después |

> **Alternativa a `FIREBASE_SERVICE_ACCOUNT_JSON`:** Render permite montar *Secret Files*. Se sube el
> archivo `.json` como secreto (por ejemplo en `/etc/secrets/sigvach-sa.json`) y se define
> `GOOGLE_APPLICATION_CREDENTIALS` con esa ruta, dejando vacía la variable anterior. El backend admite
> las dos formas.

### A.4 Verificar el despliegue

Cuando el servicio termine de compilar, Render muestra su dirección, del tipo
`https://sigvach-api.onrender.com`. Comprobar:

```powershell
Invoke-RestMethod https://sigvach-api.onrender.com/api/v1/salud
```

Respuesta esperada:

```json
{"estado":"ok","version_api":"v1","entorno":"produccion","base_de_datos":"conectada"}
```

Si `base_de_datos` dice `"no disponible"`, la clave de la cuenta de servicio no está bien cargada:
revisar **Logs** en el panel de Render.

Abrir también la documentación del contrato, que es la que se cita en el apartado 2.4.4:

```
https://sigvach-api.onrender.com/docs
```

Y probar la ingesta del dispositivo, que es la ruta que usarán los sensores:

```powershell
$cuerpo = '{"modulo_id":"modulo-1","variable":"ph","valor":6.1}'
Invoke-RestMethod -Method Post -Uri "https://sigvach-api.onrender.com/api/v1/lecturas" `
  -Headers @{ "X-Device-Key" = "LA-CLAVE-DEL-PASO-A3"; "Content-Type" = "application/json" } `
  -Body $cuerpo
```

Debe responder con la lectura almacenada y su estado respecto del rango. Con una clave equivocada debe
responder **401**, que es lo que se espera.

### A.5 Índices de Cloud Firestore

Las consultas de lecturas que combinan un filtro de igualdad con un rango de fechas necesitan índices
compuestos. La primera vez que se ejecute una de esas consultas, Firestore devuelve en el error un
enlace directo para crearlos. Los previstos están listados en `backend/README.md`, sección 9.

---

## Parte B · Aplicación web en Firebase Hosting

### B.1 Compilar apuntando al backend desplegado

```powershell
cd "D:\SIGVACH-Monograf\Proyecto SIGVACH"
flutter build web --release --dart-define=API_BASE_URL=https://sigvach-api.onrender.com
```

El resultado queda en `build/web`. La dirección del backend entra por configuración de compilación, no
por el código: es lo que permite que el mismo repositorio sirva para local y para producción.

### B.2 Publicar

```powershell
firebase login
firebase deploy --only hosting
```

El archivo `firebase.json` ya tiene configurado el directorio (`build/web`) y la reescritura de rutas
necesaria para una aplicación de una sola página.

Firebase muestra la dirección pública, del tipo `https://sigvach26-bd.web.app`.

### B.3 Completar la configuración de CORS

Volver al panel de Render y cambiar `ALLOWED_ORIGINS` por la dirección de B.2. Sin esto el navegador
bloquea las peticiones de la aplicación web al servicio (en el escritorio y en Android no ocurre, porque
la restricción de origen es propia de los navegadores). El servicio se reinicia solo al guardar.

### B.4 Verificar

Abrir la dirección pública en el navegador: debe cargar la pantalla de inicio de sesión de SIGVACH y
permitir registrarse o iniciar sesión. Al entrar, el panel debe mostrar el estado de las variables
tomadas del backend.

---

## Parte C · Archivo instalable de Android

### C.1 Generar un almacén de claves propio

El proyecto firma hoy con la clave de depuración, que sirve para probar pero no para distribuir.

```powershell
keytool -genkey -v -keystore "$env:USERPROFILE\sigvach-release.jks" -keyalg RSA `
  -keysize 2048 -validity 10000 -alias sigvach
```

Guardar el archivo **fuera del repositorio** y anotar su contraseña. Luego crear
`android/key.properties` (ya está excluido por `.gitignore`):

```properties
storePassword=LA-CONTRASEÑA
keyPassword=LA-CONTRASEÑA
keyAlias=sigvach
storeFile=C:/Users/TU-USUARIO/sigvach-release.jks
```

### C.2 Compilar el APK

```powershell
flutter build apk --release --dart-define=API_BASE_URL=https://sigvach-api.onrender.com
```

El archivo queda en `build\app\outputs\flutter-apk\sigvach_1.0.0+1.apk`.

### C.3 Instalar y verificar

Copiar el APK al teléfono e instalarlo (hay que permitir la instalación desde orígenes desconocidos).
Comprobar que la aplicación abre, permite iniciar sesión y consulta el mismo backend que la versión web.

---

## Parte D · Verificación de los requisitos mínimos

| # | Requisito | Cómo se verifica | Evidencia |
|---|---|---|---|
| 1 | Desplegado y accesible por dirección pública, o instalable | Abrir la dirección de Firebase Hosting e instalar el APK | Captura de la aplicación desplegada y archivo APK |
| 2 | Autenticación y control de acceso por rol | Iniciar sesión con una cuenta de operador e intentar una operación de administración | Captura del 403 y de la pantalla de usuarios |
| 3 | Persistencia con el CRUD del dominio | Crear, consultar, modificar y eliminar desde la aplicación | Capturas del CRUD y consulta en la consola de Firestore |
| 4 | Interfaz adaptable | Abrir la aplicación web en tres anchos de ventana | Tres capturas: móvil, tableta y escritorio |
| 5 | Repositorio con historial de avance progresivo | Ver la lista de confirmaciones con sus fechas | Captura del historial en GitHub |
| 6 | README con descripción e instrucciones | Abrir el repositorio en modo incógnito y seguir las instrucciones | Captura del README |
| 7 | Credenciales fuera del repositorio | Buscar `serviceAccount`, `apiKey` y `PRIVATE KEY` en el repositorio | Captura del `.env.example` y de la búsqueda sin resultados |
| 8 | Validación en cliente y en servidor | Enviar una lectura con un valor imposible desde el cliente y ver el rechazo del servidor | Captura del 422 con el campo señalado |

---

## Parte E · Capturas que hay que tomar para el apartado 2.9

Guardarlas en `docs/capturas/`, con nombres descriptivos y la fecha en que se tomaron. **Sin datos
personales de terceros:** usar las cuentas de prueba.

1. El panel de Render con la compilación correcta y el servicio activo.
2. El panel de Render con las variables de entorno configuradas, **con los valores ocultos**.
3. Los registros del servicio atendiendo una petición real.
4. La respuesta de `/api/v1/salud` desde el navegador.
5. La documentación del contrato (`/docs`) con las rutas publicadas.
6. La consola de Firebase con las colecciones creadas y un documento de lectura.
7. La dirección pública de la aplicación funcionando con dos roles distintos.
8. Firebase Hosting con el historial de publicaciones.
9. El archivo APK generado y la aplicación abierta en el teléfono.

---

## Parte F · Problemas previsibles

| Síntoma | Causa | Solución |
|---|---|---|
| La primera petición tarda veinte o treinta segundos | La capa gratuita de Render suspende el servicio por inactividad | Es una limitación declarada en 2.9. Antes de la demostración, invocar `/api/v1/salud` para despertarlo |
| El navegador bloquea las peticiones de la aplicación web | `ALLOWED_ORIGINS` no incluye la dirección del despliegue | Completar la variable en Render con la dirección exacta de Firebase Hosting |
| Todas las peticiones responden 401 | El token se emite para un proyecto de Firebase distinto del configurado en `FIREBASE_PROJECT_ID` | Verificar que el identificador del proyecto sea el mismo en la aplicación y en el servicio |
| `base_de_datos: no disponible` en `/salud` | La clave de la cuenta de servicio está incompleta o mal formada | Volver a generarla y pegarla en una sola línea |
| Una consulta de lecturas falla con un error de índice | Falta el índice compuesto | Abrir el enlace que incluye el error y crearlo |
| La aplicación no alcanza al backend en local | El emulador de Android no ve `localhost` | Usar `--dart-define=API_BASE_URL=http://10.0.2.2:8000` |

---

## Parte G · Lo que no se debe hacer

- No subir al repositorio el archivo de la cuenta de servicio, el almacén de claves ni el archivo
  `.env`. Están en `.gitignore`, pero conviene verificar antes de cada confirmación.
- No pegar claves en el documento de la monografía ni en las capturas.
- No usar en la demostración datos personales reales de terceros: las cuentas de prueba son
  `admin@sigvach.com` y `operador@sigvach.com`.
- No ejecutar `flutter pub upgrade`: puede romper las versiones verificadas del proyecto.
