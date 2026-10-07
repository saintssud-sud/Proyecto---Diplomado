# 35 · Guía para entender el código y defenderlo

**Para qué sirve.** La rúbrica da **30 de 100 puntos** al dominio técnico: «explica y ubica en el
repositorio el código, el esquema y sus decisiones; hace un cambio simple si se le pide». Y la regla
es explícita: *quien no ejecuta ni explica su sistema, no aprueba la defensa*.

Esta guía está escrita para leerse con el repositorio abierto al lado. Todo lo que dice de archivos,
funciones y líneas salió de leer los archivos, no de los documentos. Donde algo no existe en el
repositorio, lo dice con esas palabras y aclara dónde se buscó.

**Repositorio:** `D:\SIGVACH-Monograf\Proyecto SIGVACH` (público, rama `main`).
**Las tres partes:** backend en `backend/app/` (FastAPI, Python), aplicación en `lib/` (Flutter),
firmware en `hardware/firmware/main/` (ESP32, C con ESP-IDF).

**Cómo se lee cada sección de las ocho preguntas.** Primero la respuesta como se dice en voz alta;
después la tabla de dónde vive cada cosa con archivo y línea; después el fragmento que es el corazón
de la respuesta; al final, qué abrir y qué señalar en vivo.

---

## 1. Mapa del repositorio

Carpetas que importan, en una frase cada una.

| Carpeta o archivo | Para qué sirve |
|---|---|
| `backend/app/` | El servicio de la API: punto de entrada, configuración, seguridad, esquemas y datos de demostración. |
| `backend/app/rutas/` | Un archivo por recurso del contrato (`lecturas`, `modulos`, `perfiles`, `rangos`, `alertas`, `exportaciones`, `usuarios`, `salud`): cada endpoint con su dependencia de autorización. |
| `backend/app/servicios/` | Las reglas de negocio del dominio: `lecturas.py` registra una lectura y decide si genera alerta; `evaluacion.py` tiene las funciones puras (evaluar contra el rango, armar la alerta, resumir una serie, generar el CSV). |
| `backend/app/repositorios/` | El acceso a los datos: `base.py` declara la interfaz, `firestore.py` la implementa sobre Cloud Firestore y `memoria.py` sobre diccionarios, para las pruebas y el modo de demostración. |
| `backend/pruebas/` | Las 119 pruebas del servicio, con `conftest.py` que sustituye Firestore por el repositorio en memoria y el verificador de identidad por uno simulado. |
| `backend/README.md`, `requirements*.txt` | Cómo se ejecuta el servicio en local y qué dependencias necesita (las de desarrollo van aparte). |
| `lib/` | La aplicación Flutter: `main.dart` arma los proveedores, `app.dart` el tema y la pantalla inicial. |
| `lib/config/` | La dirección del backend (`api_config.dart`, que se define al compilar) y los datos de configuración de la aplicación (`app_config.dart`). |
| `lib/services/` | Lo que habla con el mundo: `api_cliente.dart` (HTTP, token y traducción de errores), `api_errores.dart` (los tipos de error), `auth_service.dart` (sesión con Firebase), más clima y ubicación. |
| `lib/repositories/api/` | Un repositorio por recurso del contrato: arma la ruta con `ApiConfig.ruta` y convierte el JSON en modelos. |
| `lib/controllers/` | Un controlador por dominio que resuelve los cuatro estados de la vista (cargando, con datos, vacío, error) y traduce los fallos. |
| `lib/screens/` | Las pantallas, agrupadas por área: `ajustes/`, `alertas/`, `cultivos/`, `historial/`, `variables/`, `context/`. |
| `lib/models/` | Los modelos: `api/modelos_api.dart` para lo que devuelve el servicio y `roles.dart` como única fuente de los nombres de rol. |
| `lib/widgets/` | Piezas compartidas: `vista_con_estados.dart` (los cuatro estados), `tarjeta_de_modulo.dart`, `encabezado_del_menu.dart`. |
| `test/` | Las 96 pruebas de la aplicación, sin credenciales ni red. |
| `hardware/firmware/main/` | El firmware del módulo: `main.c` (arranque, red, ciclo de lectura), `sensores.c` (ambiente, solución, TDS), `publicacion.c` (envío HTTPS), `cola_nvs.c` (lecturas pendientes en memoria no volátil) y `configuracion.ejemplo.h` (plantilla de la configuración privada). |
| `hardware/evidencias/` | Los registros del Monitor Serie con fecha: calibración del pH, arranque y ciclo, contraste de sensores, publicación de las seis variables. |
| `evidencia/` | Los informes de ejecución de pruebas con fecha en el nombre, incluido el XML de JUnit del servicio, y las capturas de pantalla. |
| `scripts/` | Los verificadores (`verificar_sin_secretos.py`, `verificar_despliegue.py`, `verificar_dart.py`), el simulador del dispositivo y los generadores de figuras y documentos. |
| `docs/` | Documentación de trabajo del proyecto (75 archivos): bitácoras, planes, guías y verificaciones. **No forma parte de la monografía.** |
| `.github/workflows/` | `verificacion.yml` (pruebas y compilación en cada confirmación) y `monitoreo.yml` (consulta de salud cada 15 minutos). |
| `assets/images/` | El logo que muestran la pantalla de presentación y la de inicio de sesión. |
| `android/`, `web/`, `platform_templates/` | El andamiaje de las plataformas de Flutter; no se toca a mano salvo la firma de Android. |
| `.env.example` | La plantilla de variables de entorno: **solo los nombres**, nunca los valores reales. |
| `render.yaml` | El despliegue del servicio como infraestructura declarada: comando de arranque, puerto, ruta de salud y variables que se completan en el panel. |
| `firebase.json`, `firestore.rules`, `firestore.indexes.json` | La publicación de la aplicación web, las reglas de seguridad de la base y los índices compuestos declarados. |
| `pubspec.yaml` | Las dependencias de la aplicación Flutter. |
| `README.md` | La puerta de entrada: qué es el sistema, cómo se ejecuta en local y las direcciones públicas. |

**Números que conviene tener a mano** (contados sobre el código, no copiados de un documento):

| Dato | Valor | Cómo se cuenta |
|---|---|---|
| Endpoints del contrato | **32** | Los decoradores `@enrutador.get/post/patch/delete` en `backend/app/rutas/*.py`. |
| Endpoints que exigen identidad de usuario | **30** | Todos menos `GET /salud` (público) y `POST /lecturas` (clave de dispositivo). |
| Pruebas del servicio | **119** | `def test_` en `backend/pruebas/*.py` (eran 106 antes del 5/10; se sumaron las 13 del registro de peticiones). |
| Pruebas de la aplicación | **96** | `test(` y `testWidgets(` en `test/*.dart`. |
| Variables del catálogo | **6** | `CATALOGO_VARIABLES` en `backend/app/esquemas.py:36-47`. |
| Colecciones de la base | **6** | Las constantes `COLECCION_*` en `backend/app/repositorios/firestore.py:20-25`. |

---

## 2. Las ocho preguntas

### 2.1 ¿Dónde se verifica el rol?

**Respuesta en voz alta.** El rol se verifica **en el servidor**, en una dependencia de FastAPI que se
declara en cada ruta protegida: la ruta no ejecuta su código si el rol no alcanza, y responde 403 con
el rol requerido y el rol actual en el detalle. Que la aplicación oculte un botón es comodidad de uso,
no control de acceso. En el servicio hay dos middleware —el de CORS y, desde el 5/10, el de registro de
peticiones (`backend/app/registro_peticiones.py`)—, pero **ninguno de los dos decide el rol**: el 403 no
viene de un middleware sino de esa dependencia.

**Dónde vive en el código**

| Archivo | Líneas | Qué hace |
|---|---|---|
| `backend/app/seguridad.py` | 59-105 | `usuario_actual`: lee la cabecera `Authorization`, verifica el token, busca el perfil y resuelve el rol. Sin cabecera responde 401 (65-70); sin perfil, 403 (91-96); con la cuenta desactivada, 403 (97-102). |
| `backend/app/seguridad.py` | 108-123 | `requiere_administracion`: exige un rol de administración y lanza el **403**. |
| `backend/app/seguridad.py` | 126-147 | `requiere_consulta`: el nivel más bajo (operación + invitado). Lanza **403**. |
| `backend/app/seguridad.py` | 150-165 | `requiere_operacion`: registrar y modificar datos. Lanza **403**. |
| `backend/app/seguridad.py` | 168-186 | `dispositivo_autorizado`: la otra identidad, la del módulo, por la cabecera `X-Device-Key`. |
| `backend/app/rutas/usuarios.py` | 137-142 | Ejemplo de ruta de administración: `listar_cuentas`, con `Depends(requiere_administracion)` en la línea 138. |
| `backend/app/errores.py` | 63-68 | El manejador que convierte cualquier `ErrorApi` (incluido el 403) en el cuerpo uniforme `{codigo, mensaje, detalle}`. |
| `backend/app/config.py` | 100-120 | De dónde salen los conjuntos de roles: `roles_administracion`, `roles_operacion` y `roles_consulta`, leídos de la configuración y no escritos en el código de autorización. |
| `backend/app/main.py` | 141-153 | Los **dos** middleware registrados: `CORSMiddleware` (141-147) y el registro de peticiones (153). Ninguno decide el rol: sirven para saber contestar que el 403 no es middleware. |

**El corazón de la respuesta** — `backend/app/seguridad.py:113-122`:

```python
    if usuario.rol not in configuracion.roles_administracion:
        raise ErrorApi(
            403,
            CODIGO_SIN_PERMISO,
            "La operación requiere el rol de administrador.",
            {
                "rol_requerido": sorted(configuracion.roles_administracion),
                "rol_actual": usuario.rol,
            },
        )
```

**Cómo mostrarlo en vivo.** Abrir `backend/app/seguridad.py` y señalar la línea 108 (la función) y la
línea 114 (el `raise` con el 403). Después abrir `backend/app/rutas/usuarios.py` y señalar la línea
138, donde la ruta `GET /api/v1/usuarios` declara `Depends(requiere_administracion)`. Cerrar con la
llamada real desde la sesión del operador:

```
GET https://sigvach-api.onrender.com/api/v1/usuarios
Authorization: Bearer <token del operador>

HTTP 403
{"codigo":"sin_permiso","mensaje":"La operación requiere el rol de administrador.",
 "detalle":{"rol_requerido":["administrador"],"rol_actual":"operador"}}
```

---

### 2.2 ¿Qué pasa si el token vence?

**Respuesta en voz alta.** El servicio responde **401 `no_autenticado`** con el mensaje «El token de
identidad no es válido o expiró», y la aplicación, al ver ese 401, **cierra la sesión local y vuelve a
la pantalla de inicio de sesión** mostrando el motivo: «Tu sesión venció. Volvé a iniciar sesión.» Un
token vencido no se arregla reintentando la misma petición, así que la aplicación pide las
credenciales otra vez. La decisión fina: **solo el 401 del servidor cierra la sesión**, no la falta de
token en el equipo, porque al arrancar la sesión todavía se está restaurando y cerrarla dejaría al
usuario afuera sin motivo.

**Dónde vive en el código**

| Archivo | Líneas | Qué hace |
|---|---|---|
| `backend/app/seguridad.py` | 39-56 | `_verificar_token_identidad`: verifica contra Firebase Authentication y convierte cualquier fallo en **401** (51-56). |
| `backend/app/seguridad.py` | 65-70 | Sin cabecera `Authorization`, 401 con el mensaje «Falta el token de identidad…». |
| `lib/services/api_cliente.dart` | 59-60 | De dónde sale el token: `FirebaseAuth.instance.currentUser?.getIdToken()`. |
| `lib/services/api_cliente.dart` | 206-234 | Adjunta `Authorization: Bearer <token>`; si no hay token, corta antes de salir a la red (225-232). |
| `lib/services/api_cliente.dart` | 80-88 | `_avisarSesionExpirada`: el aviso, que no puede tumbar la respuesta original. |
| `lib/services/api_cliente.dart` | 310-316 | `_errorDeRespuesta`: si el error es 401, avisa. |
| `lib/services/api_errores.dart` | 37 | `esNoAutenticado` es exactamente «el estado es 401». |
| `lib/services/auth_service.dart` | 38-41 | `cerrarSesionPorExpiracion`: deja el aviso y cierra la sesión. |
| `lib/services/auth_service.dart` | 20-21 y 44-48 | Dónde vive el aviso y cómo se consume una sola vez. |
| `lib/main.dart` | 92-100 | El cableado: `ApiCliente(alExpirarLaSesion: auth?.cerrarSesionPorExpiracion)`. |
| `lib/screens/login_screen.dart` | 31-37 | Al abrirse, la pantalla de inicio de sesión muestra el motivo. |
| `test/api_cliente_test.dart` | 304-329 y 331-366 | Las dos pruebas: el 401 del servicio **cierra** la sesión; un fallo de conexión y la falta de token local **no** la cierran. |

**El corazón de la respuesta** — `lib/services/api_cliente.dart:310-316`:

```dart
  ErrorApi _errorDeRespuesta(http.Response respuesta) {
    final ErrorApi error = _errorDesdeRespuesta(respuesta);
    if (error.esNoAutenticado) {
      _avisarSesionExpirada();
    }
    return error;
  }
```

**Cómo mostrarlo en vivo.** Abrir `lib/services/api_cliente.dart` en la línea 310 y leer en voz alta
que solo el 401 avisa. Después abrir `lib/services/auth_service.dart:38-41` y mostrar que el aviso se
deja antes de cerrar la sesión. Cerrar ejecutando la prueba, que es la evidencia más rápida:

```
flutter test test/api_cliente_test.dart
```

---

### 2.3 ¿Cómo guarda las contraseñas?

**Respuesta en voz alta.** **No las guardamos: no las vemos.** El alta y el inicio de sesión los
resuelve el proveedor de identidad (Firebase Authentication), que guarda el resumen de la contraseña
de su lado y nos devuelve un token firmado; lo único que viaja hacia nuestro servicio es ese token, y
el servicio lo verifica en cada petición. Por eso en el backend no hay ni una línea que lea una
contraseña, y el repositorio no guarda ninguna.

**Lo que hay que decir con precisión.** El **algoritmo de hash no está en el repositorio**: lo aplica
el proveedor, no lo elegimos nosotros. Busqué `password`, `contrasena`, `contraseña`, `hash`,
`bcrypt`, `scrypt` y `argon` en todo `backend/`: **cero coincidencias**. Lo que sí está en el código y
se puede mostrar es el camino por el que la contraseña **pasa de largo**: la aplicación la entrega al
SDK y el backend solo ve el token.

**Dónde vive en el código**

| Archivo | Líneas | Qué hace |
|---|---|---|
| `lib/services/auth_service.dart` | 51-56 | `signIn`: entrega correo y contraseña al SDK de Firebase y no los guarda. |
| `lib/services/auth_service.dart` | 59-77 | `signUp`: crea la cuenta en el proveedor y guarda el nombre en el perfil del proveedor. |
| `lib/screens/login_screen.dart` | 136-156 | Traduce los códigos de error del proveedor a mensajes presentables; ninguna credencial se registra. |
| `backend/app/seguridad.py` | 39-56 | Lo único que el backend hace con la identidad: verificar el **token**. |
| `backend/app/repositorios/firestore.py` | 271-294 | El único acceso a la colección `usuarios`: lee y actualiza el perfil; no hay campo de contraseña. |
| `backend/app/esquemas.py` | 214-226 y 349-363 | Los dos esquemas de perfil: ninguno admite contraseña, y el del propio usuario tampoco admite `rol`. |
| `firestore.rules` | 87-103 | La regla que cierra la escalada de privilegios: al crear el perfil el rol **solo** puede ser `operador`, y el usuario no puede cambiar su propio rol ni su estado. |

**El corazón de la respuesta** — `lib/services/auth_service.dart:51-56`:

```dart
  Future<void> signIn({required String email, required String password}) async {
    await _auth.signInWithEmailAndPassword(
      email: email.trim(),
      password: password,
    );
  }
```

**Cómo mostrarlo en vivo.** Abrir `lib/services/auth_service.dart` en la línea 51 y mostrar que la
contraseña entra directo al SDK, sin pasar por ninguna variable ni por ningún registro. Después hacer
la búsqueda que lo prueba, en la raíz del proyecto:

```
Select-String -Path backend\**\*.py -Pattern "password|contrasena|hash|bcrypt|scrypt"
```

No devuelve nada. Eso es la respuesta: **no hay código nuestro que toque la contraseña**.

---

### 2.4 ¿Dónde están los secretos?

**Respuesta en voz alta.** En **variables de entorno de la plataforma**, nunca en el repositorio. Lo
que el repositorio sí guarda es la **plantilla** con los nombres: `.env.example` en la raíz. En
producción los valores se completan en el panel del proveedor —`render.yaml` los declara con
`sync: false`, que significa «este valor no viene del archivo, se completa en el panel»— y en el
equipo del autor viven en un `.env` local. La clave del WiFi y la del módulo viven en
`configuracion.h`, que está excluido por `.gitignore` y **verifiqué que no está versionado**.

**Dónde vive en el código**

| Archivo | Líneas | Qué hace |
|---|---|---|
| `.env.example` | 14, 17, 23, 26, 32-34, 40-41 | Los nombres y la explicación de cada variable: `PORT`, `ALLOWED_ORIGINS`, `DEVICE_API_KEY`, `FIREBASE_PROJECT_ID`, los tres roles, `FIREBASE_SERVICE_ACCOUNT_JSON` y `GOOGLE_APPLICATION_CREDENTIALS`. |
| `backend/app/config.py` | 23-89 | Cómo se leen: `BaseSettings` con `validation_alias`, que admite el nombre en inglés y en español. |
| `backend/app/config.py` | 123-126 | `obtener_configuracion` con `lru_cache`: se resuelve una sola vez por proceso. |
| `render.yaml` | 28-45 | Las variables del despliegue; los secretos con `sync: false` para que se completen en el panel. |
| `.gitignore` | 52-54 | Excluye `.env` y `.env.*`, y conserva `!.env.example`. |
| `.gitignore` | 66-67 y 28 | Excluye `configuracion.h` (dos veces, por si alguien lo mueve de lugar) y `lib/firebase_options.dart`. |
| `hardware/firmware/main/configuracion.ejemplo.h` | 14-44 | La plantilla del firmware, con valores de ejemplo. |
| `hardware/firmware/main/configuracion.h` | — | El archivo real con el WiFi y la clave del dispositivo: existe en el disco y **no está en git** (comprobado con `git ls-files --error-unmatch`, que responde que no lo conoce, y con `git check-ignore -v`, que lo atribuye a `hardware/firmware/.gitignore:17`). |
| `scripts/verificar_sin_secretos.py` | 33-73 | El verificador: lee los valores reales del `.env` y de `configuracion.h` y los busca en los archivos versionados **y en todo el historial**. |

**El corazón de la respuesta** — `.env.example:19-23`:

```
# Clave que autentica al módulo de adquisición (ESP32) al publicar lecturas.
# Debe ser una cadena aleatoria larga y distinta de cualquier credencial de
# usuario. Se envía en la cabecera X-Device-Key y puede rotarse sin afectar a
# los usuarios del sistema.
DEVICE_API_KEY=cambiar-por-una-cadena-aleatoria-larga
```

**Cómo mostrarlo en vivo.** Abrir `.env.example` y señalar que cada línea es un **nombre** con un
valor de ejemplo, incluida `DEVICE_API_KEY=cambiar-por-una-cadena-aleatoria-larga`. Después abrir
`backend/app/config.py:50-55` y mostrar que el valor real llega por `FIREBASE_SERVICE_ACCOUNT_JSON`.
Cerrar con el verificador:

```
python scripts/verificar_sin_secretos.py
```

**Aviso para la pantalla compartida:** no abrir `hardware/firmware/main/configuracion.h` durante la
defensa. Tiene la clave del WiFi y la del dispositivo. Está fuera de git, pero se vería en pantalla.

---

### 2.5 ¿Por qué este stack?

**Respuesta en voz alta.** Cada pieza se justifica contra un requisito y por su identificador, no por
gusto. El servicio separado con **FastAPI** porque la validación y la autorización no pueden depender
del cliente: eso es el **requisito mínimo 8** y el **RNF-02**. **Flutter** porque un solo código tiene
que responder al **requisito mínimo 4** con **RNF-06** (adaptabilidad) y **RNF-04** (compatibilidad,
web y Android). **Cloud Firestore** por el **requisito mínimo 3** (persistencia con las operaciones
del dominio) y el **RNF-01**. **Firebase Authentication** por el **RNF-02**: delega la autenticación
en un proveedor especializado y evita que el sistema guarde contraseñas. El despliegue con las
credenciales en variables de entorno, por el **requisito mínimo 7** y el **requisito mínimo 1**
(accesible por una dirección pública).

**Dónde vive en el código** (los requisitos están citados **dentro** del código, que es lo que hace
verificable la justificación)

| Archivo | Líneas | Qué requisito ancla |
|---|---|---|
| `backend/app/esquemas.py` | 1-10 | «La validación de los datos de entrada es un requisito mínimo del producto (**requisito 8**) y reside aquí, en el servidor». |
| `backend/app/esquemas.py` | 67-74 | La base común de todos los esquemas de entrada: `extra="forbid"`. Es la forma concreta de cumplir el requisito mínimo 8. |
| `backend/app/servicios/evaluacion.py` | 43-48 | Cada alerta conserva la lectura que la originó: **RNF-08** (trazabilidad). |
| `backend/app/rutas/salud.py` | 1-7 | El endpoint público que sirve para verificar el despliegue (apartado 2.9). |
| `backend/app/config.py` | 3-6 | «Ninguna credencial se escribe en el código ni en el repositorio»: **requisito mínimo 7**. |
| `backend/app/config.py` | 63-65 y 100-120 | Los roles se leen de la configuración para que el alcance de roles no obligue a tocar el código de autorización: **RF-02**. |
| `backend/pruebas/test_validacion.py` | 1 | La prueba dice a qué requisito corresponde: **requisito mínimo 8**. |
| `backend/pruebas/test_api_autorizacion.py` | 1-4 | Las pruebas de autorización declaran el **requisito mínimo 2** y el **RNF-03**. |
| `backend/pruebas/test_api_lecturas.py` | 131 | La trazabilidad del autor de la lectura: **RNF-08**. |
| `render.yaml` | 1-13 | «Los valores secretos NO se declaran aquí… conforme al requisito mínimo 7», y la ruta de salud que verifica la plataforma. |
| `scripts/llenar_perfil_e1.py` | 634-649 | La tabla completa del stack con su requisito por identificador, tal como quedó en el apartado 2.5 de la monografía. |

**El corazón de la respuesta** — `backend/app/esquemas.py:67-74`:

```python
class _BaseEntrada(BaseModel):
    """Base común: se rechazan los campos no declarados en el contrato."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class _LecturaBase(_BaseEntrada):
    """Campos y validaciones comunes a toda lectura, cualquiera sea su origen."""
```

**Cómo mostrarlo en vivo.** Abrir `backend/app/esquemas.py` y señalar el encabezado (líneas 1-10),
donde el requisito está citado por su número, y la línea 70 con `extra="forbid"`. Después hacer la
llamada que demuestra que la validación no está en el cliente:

```powershell
curl -X POST https://sigvach-api.onrender.com/api/v1/lecturas `
  -H "X-Device-Key: <clave>" -H "Content-Type: application/json" `
  -d '{"modulo_id":"<id>","variable":"ph","valor":99}'
```

Responde **422** con `detalle.campos.valor` = «ph debe estar entre 0.0 y 14.0». Ese rechazo lo hace el
servidor por el esquema, y es exactamente el requisito mínimo 8 en acción.

---

### 2.6 ¿Cómo sabe que funciona?

**Respuesta en voz alta.** Con **215 pruebas automatizadas que se vuelven a ejecutar en un minuto**:
119 del servicio y 96 de la aplicación, más los casos medidos contra el servicio publicado. Una fila
concreta de la tabla: *el operador no puede crear módulos y el servicio responde 403 con el detalle
del rol*, cubierta por una prueba y con evidencia fechada contra producción. Ninguna prueba necesita
credenciales ni red: el servicio sustituye Firestore por un repositorio en memoria y el verificador de
identidad por uno simulado, así que **se puede correr entera delante del tribunal**.

**Dónde vive el código y la evidencia**

| Archivo | Líneas | Qué es |
|---|---|---|
| `backend/pruebas/test_api_autorizacion.py` | 59-67 | **La fila que conviene mostrar**: `test_el_operador_no_puede_crear_modulos`. |
| `backend/pruebas/conftest.py` | 128-152 | Cómo se prueba sin credenciales: se sustituye solo la llamada a Firebase Authentication; el resto del camino se ejecuta tal como en producción. |
| `backend/pruebas/conftest.py` | 66-81 | Los cuatro perfiles de prueba: administrador, operador, inactivo y solicitante sin perfil. |
| `backend/pruebas/test_api_lecturas.py` | 71-82 | Otra fila buena: una lectura fuera de rango genera exactamente una alerta que conserva la lectura de origen. |
| `backend/pruebas/test_evaluacion.py` | 8-35 | Las reglas de negocio puras, incluido el límite exacto: el valor igual al mínimo o al máximo se considera dentro. |
| `docs/24_EVIDENCIA_401_403_422.txt` | 60-69 | La evidencia del 403 **medido contra el servicio publicado**, con la fecha, la URL y la respuesta textual. |
| `backend/pruebas/test_registro_peticiones.py` | 37-59 | La fila nueva del 5/10: una línea por petición, con los cuatro datos, y la duración en milisegundos. |
| `evidencia/pytest-2026-10-02.txt` | 31 | «106 passed, 9 warnings in 5.34s»: el informe de la corrida del 2/10, que es el último guardado en `evidencia/`. Después se sumaron las 13 pruebas del registro, así que hoy son 119. |
| `evidencia/flutter-test-2026-10-02.txt` | 1-5 | El informe de la aplicación, con la fecha y el comando. |
| `evidencia/LEEME.md` | 11-17 y 32-44 | La tabla de resultados y **los comandos para volver a ejecutar todo**. |
| `evidencia/pytest-2026-10-02.xml` | — | El mismo resultado en formato JUnit, para leer los números sin abrir el texto. |

**El corazón de la respuesta** — `backend/pruebas/test_api_autorizacion.py:59-67`:

```python
def test_el_operador_no_puede_crear_modulos(cliente_con_token, entorno):
    respuesta = cliente_con_token.post(
        "/api/v1/modulos",
        json={"nombre": "Módulo 3", "tipo_cultivo": "Tomate", "perfil_id": entorno.perfil_id},
        headers=cabecera("operador"),
    )
    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "sin_permiso"
    assert respuesta.json()["detalle"]["rol_actual"] == "operador"
```

**Cómo mostrarlo en vivo.** Tener el comando ya escrito en la terminal, desde la raíz del proyecto:

```
.venv\Scripts\python.exe -m pytest backend -q --no-header
```

Corre 119 pruebas en unos cinco segundos y termina en verde. Si quieren ver una fila concreta y su
nombre, agregar `-k autorizacion -v`. Después abrir `docs/24_EVIDENCIA_401_403_422.txt` en la línea 60
y mostrar que ese mismo 403 está medido contra la dirección pública, con fecha del 29 de septiembre.

---

### 2.7 ¿Qué pasa si se cae?

**Respuesta en voz alta.** Hay que contestar por partes, porque son **cuatro capas y las cuatro están
hechas**. Primero, **el módulo no pierde lecturas**: si el servicio no responde o no hay red, guarda
cada lectura con su hora original en memoria no volátil y la reintenta cuando vuelve la conexión;
sobrevive a un corte de luz. Segundo, **el monitoreo de disponibilidad está activo**: un flujo de
GitHub consulta `/api/v1/salud` cada quince minutos desde los servidores de GitHub —no desde la
computadora del autor— y falla si el servicio no responde o si la base no contesta; el historial de
ejecuciones queda como página de estado pública. Tercero, **hay respaldo y está probado**: un script
exporta los datos del dominio a un archivo JSON fechado y otro procedimiento restauró ese respaldo en
un módulo de prueba contra el servicio publicado, con la constancia de que la base quedó igual.
Cuarto, **el servicio deja una línea de registro por petición**, con método, ruta, código y duración.
El redespliegue, además, es automático: la plataforma reconstruye y arranca desde `render.yaml` en
cada confirmación, y la aplicación web se vuelve a publicar con dos comandos.

**Dónde vive en el código**

| Archivo | Líneas | Qué hace |
|---|---|---|
| `.github/workflows/monitoreo.yml` | 27-31 | La programación: `cron: "*/15 * * * *"`, cada quince minutos. |
| `.github/workflows/monitoreo.yml` | 44-75 | La consulta y las tres condiciones: HTTP 200, `"estado":"ok"` y `"base_de_datos":"conectada"`. |
| `backend/app/rutas/salud.py` | 19-31 | La ruta de salud: informa `ok` o `degradado` según la base. |
| `backend/app/repositorios/firestore.py` | 310-325 | `verificar_conexion`: lee un documento; si falla, lo registra con su causa y devuelve `False`. |
| `hardware/firmware/main/cola_nvs.h` | 29-42 | La cola en memoria no volátil: 60 lecturas, y cada una guarda su **marca de tiempo original**. |
| `hardware/firmware/main/main.c` | 663-700 | `publicarPendientes`: primero la más antigua; si falla, se detiene y la conserva. |
| `hardware/firmware/main/main.c` | 643-652 | Un rechazo del contrato (401, 404, 422) **no** se guarda: reintentarlo no lo arreglaría. |
| `hardware/firmware/main/main.c` | 780-795 | Sin red, las seis lecturas del ciclo van a la cola en lugar de perderse. |
| `hardware/firmware/main/publicacion.c` | 19-23 | Espera máxima de 75 segundos, para cubrir el despertar en frío de la capa gratuita. |
| `scripts/respaldar_base.py` | 441-495 y 503-582 | El respaldo: consulta la API publicada y guarda perfiles, módulos, rangos, lecturas y alertas en un JSON fechado dentro de `respaldos/`. |
| `scripts/restaurar_prueba_base.py` | — | La restauración probada: crea su propio módulo de prueba, restaura lecturas del respaldo, comprueba la evaluación del servidor y **borra todo lo creado**. |
| `evidencia/restauracion-2026-10-05.txt` | 1-14 y 130-146 | La constancia, con fecha 5/10: 1000 lecturas y 605 alertas antes y después, 0 desaparecidas. |
| `backend/app/registro_peticiones.py` | 104-121 y 168-207 | El middleware que escribe una línea por petición, en un `finally` para registrar también el error no previsto. |
| `backend/app/main.py` | 129 y 153 | Dónde se instala: `configurar_registro(...)` y `add_middleware(MiddlewareRegistroPeticiones)`. |
| `render.yaml` | 22-27 | El redespliegue: `buildCommand`, `startCommand`, `healthCheckPath` y `autoDeploy: true`. |
| `firebase.json` | 6-8 | La publicación de la aplicación: `public: "build/web"`. |
| `scripts/verificar_despliegue.py` | 76-164 | Las cuatro comprobaciones del despliegue: que el paquete publicado lleve la dirección pública, que coincida con la compilación local, que el servicio responda y que el origen esté autorizado. |
| `scripts/verificar_despliegue.py` | 96-98 | Los dos comandos de la publicación, impresos por el propio verificador. |

**El corazón de la respuesta** — `.github/workflows/monitoreo.yml:44-53`:

```yaml
      - name: Consultar /api/v1/salud
        env:
          URL_SALUD: https://sigvach-api.onrender.com/api/v1/salud
        run: |
          echo "Momento de la consulta: $(date -u +'%Y-%m-%dT%H:%M:%SZ') (UTC)"
          echo "Ruta consultada: $URL_SALUD"
          echo ""

          codigo=$(curl -s -o respuesta.json -w "%{http_code}" \
                   --max-time 120 --retry 2 --retry-delay 10 "$URL_SALUD" || echo "000")
```

**Cómo mostrarlo en vivo.** Abrir la pestaña *Actions* del repositorio y mostrar el flujo
«Monitoreo de disponibilidad» con las corridas de las últimas horas: es la página de estado pública,
sin cuentas ni servicios externos. Después abrir `.github/workflows/monitoreo.yml` en la línea 65 y
señalar que no alcanza con que el servicio responda: el flujo falla si la base no está conectada.
**Y mostrar el respaldo, que es lo nuevo**: abrir `evidencia/restauracion-2026-10-05.txt` en la línea
140 y leer la conclusión de la restauración probada. Si hay tiempo, correr
`python scripts/respaldar_base.py` y mostrar el archivo JSON recién generado.

---

### 2.8 ¿Qué quedó pendiente?

**Respuesta en voz alta.** Se contesta con la lista, sin adornos, y conviene empezar aclarando lo que
**ya dejó de estar pendiente**: el respaldo de la base con su restauración probada y el registro de una
línea por petición se cerraron el 5 de octubre; **la calibración del TDS quedó cerrada el 6 de octubre**
contra el patrón trazable Hanna HI7031, con la verificación en 707,97 ppm y una aclaración importante
—corrige la pendiente con un solo punto, así que no se afirma precisión cerca de 0 ppm—; y el **índice
compuesto que faltaba** —el de `alertas` por `(modulo_id, timestamp)`, que ya había dado error del
servidor en producción— está declarado en `firestore.indexes.json` y desplegado, con la consulta
verificada en 200. Lo que queda es esto. Primero, **eliminar una cuenta borra el perfil pero no la
credencial** de Firebase Authentication: dar de baja la credencial exige el SDK de administración y
quedó fuera del alcance; está escrito en el propio código. Segundo, **el rendimiento con respuestas
grandes**: cumple con el tamaño que usa el panel y no cumple con 200 registros. Tercero, **la anulación
de lecturas**: la operación `DELETE /api/v1/lecturas/{id}` sigue existiendo y borra de verdad, aunque la
revisión del E3 recomendaba quitarla o convertirla en anulación con motivo. Y cuarto, un detalle menor:
en `lib/repositories/usuario_repository.dart` quedó un método sin usar que escribe directo en la base.

**Dónde vive en el código**

| Archivo | Líneas | El pendiente, escrito en el código |
|---|---|---|
| `backend/app/repositorios/firestore.py` | 296-307 | «Se elimina el **perfil** de la base de datos, no la cuenta de Firebase Authentication… queda como limitación declarada del prototipo». |
| `backend/app/rutas/usuarios.py` | 228-232 | Lo mismo, del lado del endpoint. |
| `backend/app/rutas/lecturas.py` | 161-173 | `DELETE /api/v1/lecturas/{id}` existe y elimina la lectura. |
| `backend/app/registro_peticiones.py` | 104-121 | **Ya no es un pendiente**: desde el 5/10 cada petición deja su línea (método, ruta, código y duración), instalada en `main.py:129` y `:153`. |
| `backend/app/main.py` | 48-54 y 73-77 | Lo que sí se registra: si las credenciales de servicio llegaron y con qué proyecto quedó el SDK. |
| `backend/app/repositorios/firestore.py` | 322-324 | Se registra el fallo de la base con su causa, para distinguir una credencial ausente de un problema de permisos. |
| `hardware/firmware/main/sensores.c` | 355-392 | La conversión del TDS: compensación por temperatura y polinomio cúbico del fabricante. **Sigue sin corrección propia a propósito**: acá vive el datasheet, no la sonda. |
| `hardware/firmware/main/main.c` | 68-103 y 790-805 | La calibración del pH, con la recta del 4 de octubre y su evidencia. |
| `hardware/firmware/main/main.c` | 105-131 y 776-778 | La calibración del TDS: `TDS_FACTOR_CORRECCION` (0,9373) medido contra el patrón Hanna HI7031 el 6 de octubre, aplicado justo después del polinomio, y la verificación en 707,97 ppm. |
| `firestore.indexes.json` | 36-43 | El índice `alertas(modulo_id, timestamp)` que faltaba: **declarado y desplegado**, con la consulta verificada en 200. |
| `docs/32_LISTA_DE_VERIFICACION_DEL_E4.md` | 40-44 | La lista de lo que faltaba en despliegue **al cierre de ese documento**; dos de sus filas —el respaldo con restauración probada y la línea por petición— quedaron cerradas el 5/10 y conviene decirlo al mostrarla. |
| `docs/30_PLAN_DE_LA_SEMANA_E4.md` | 180 y 196 | El respaldo, que figuraba como tarea pendiente del apartado 2.9 y ya está hecho (`evidencia/restauracion-2026-10-05.txt`). |

**El corazón de la respuesta** — `backend/app/repositorios/firestore.py:296-307`:

```python
    def eliminar_perfil_usuario(self, uid: str) -> bool:
        """Elimina el perfil del usuario; devuelve False si no existe.

        Se elimina el **perfil** de la base de datos, no la cuenta de Firebase
        Authentication: dar de baja la credencial exige el SDK de administración
        de Authentication y queda como limitación declarada del prototipo.
        """
        referencia = self._coleccion(COLECCION_USUARIOS).document(uid)
        if not referencia.get().exists:
            return False
        referencia.delete()
        return True
```

**Cómo mostrarlo en vivo.** Abrir `backend/app/repositorios/firestore.py` en la línea 296 y leer el
comentario en voz alta: la limitación está documentada donde vive el código, no escondida. Después
abrir `docs/32_LISTA_DE_VERIFICACION_DEL_E4.md` en la línea 40 y mostrar la tabla completa de lo que
falta. La frase que cierra bien: «esto es lo que no está; lo demás está y lo puedo mostrar».

---

## 3. Los cinco recorridos que conviene saber de memoria

### 3.1 Desde que una persona inicia sesión hasta que ve el panel

1. `lib/main.dart:32-48` — arranca la aplicación, inicializa Firebase y las preferencias locales.
2. `lib/main.dart:92-100` — se registra el `ApiCliente` con el aviso de sesión vencida conectado.
3. `lib/app.dart:24` — la pantalla inicial es la de presentación.
4. `lib/screens/splash_screen.dart:43-59` — a los 2,8 segundos decide: si Firebase está configurado va al `AuthGate`, si no a la pantalla de configuración pendiente.
5. `lib/screens/auth_gate.dart:15-22` — escucha los cambios de sesión; sin usuario muestra el inicio de sesión.
6. `lib/screens/login_screen.dart:89-92` — el usuario envía correo y contraseña.
7. `lib/services/auth_service.dart:51-56` — el SDK del proveedor de identidad valida y emite el token.
8. `lib/screens/login_screen.dart:95-108` — si la cuenta no tiene documento de perfil, se crea.
9. `lib/repositories/usuario_repository.dart:38-56` — el perfil nace con el **rol por defecto**, que es el de operación.
10. `lib/screens/auth_gate.dart:18-21` — con sesión iniciada, entra a la pantalla principal.
11. `lib/screens/home_screen.dart:40-48` — pide el perfil al servicio para poder mostrar el rol.
12. `lib/repositories/api/usuarios_api_repository.dart:22-26` — `GET /api/v1/usuarios/perfil`.
13. `lib/services/api_cliente.dart:206-234` — adjunta `Authorization: Bearer <token>`.
14. `backend/app/seguridad.py:59-105` — el servicio verifica el token, busca el perfil y resuelve el rol.
15. `backend/app/rutas/usuarios.py:67-78` — devuelve el perfil con el rol **que resolvió el servidor**.
16. `lib/screens/home_screen.dart:107-113 y 147` — el menú lateral muestra el nombre y el rol.
17. `lib/screens/home_screen.dart:228-235` → `lib/controllers/panel_controller.dart:102-136` — el panel consulta módulos, lecturas, rangos y alertas, y compone las variables.
18. `lib/screens/home_screen.dart:340-379` — muestra el estado general, el módulo y las seis variables.

### 3.2 Desde que el módulo mide hasta que la lectura queda guardada y evaluada

1. `hardware/firmware/main/main.c:856-868` — el módulo abre la memoria no volátil y la cola de pendientes.
2. `hardware/firmware/main/main.c:248-315` — inicializa el conversor analógico con su calibración de fábrica y espera a que se asiente.
3. `hardware/firmware/main/main.c:730-762` — lee el ambiente, la temperatura de la solución y las dos entradas analógicas (pH y TDS).
4. `hardware/firmware/main/main.c:776-778` — convierte el TDS a ppm compensando con la temperatura de la solución y aplica `TDS_FACTOR_CORRECCION`.
5. `hardware/firmware/main/main.c:792-795` — convierte milivoltios a pH con la recta de calibración y descarta el valor si se sale del rango del catálogo.
6. `hardware/firmware/main/main.c:808-823` — sin red, guarda las seis lecturas en la cola con su hora y termina el ciclo.
7. `hardware/firmware/main/main.c:641-655` — con red, toma la marca de tiempo **antes** de enviar, para que una lectura guardada conserve la hora en que se midió.
8. `hardware/firmware/main/publicacion.c:82-135` — arma el JSON y hace `POST` a `/api/v1/lecturas` con la cabecera `X-Device-Key`.
9. `backend/app/rutas/lecturas.py:45-57` — el endpoint exige `dispositivo_autorizado` y llama al servicio.
10. `backend/app/seguridad.py:168-186` — compara la clave del dispositivo con `compare_digest`; si no coincide, 401.
11. `backend/app/esquemas.py:73-117` — valida la variable contra el catálogo, el valor contra los límites físicos y la marca de tiempo contra el futuro.
12. `backend/app/servicios/lecturas.py:55` — comprueba que el módulo exista y esté activo (404 o 409 si no).
13. `backend/app/servicios/lecturas.py:58-61` — busca el rango vigente de esa variable en el perfil del módulo.
14. `backend/app/servicios/lecturas.py:63-67` → `backend/app/servicios/evaluacion.py:18-30` — evalúa el valor: `bajo`, `dentro`, `alto` o `sin_rango`.
15. `backend/app/servicios/lecturas.py:69-82` — guarda la lectura con el estado, la unidad del catálogo y el origen.
16. `backend/app/servicios/lecturas.py:84-85` → `backend/app/servicios/evaluacion.py:33-61` — si salió del rango, crea la alerta conservando el identificador de la lectura.
17. `backend/app/repositorios/firestore.py:88-94 y 233-238` — la lectura y la alerta quedan en las colecciones `lecturas` y `alertas`.
18. `hardware/firmware/main/main.c:663-700` — el módulo reintenta lo que quedó en la cola en el ciclo siguiente, con su hora original.
19. `lib/controllers/panel_controller.dart:126-135` — la aplicación vuelve a consultar y muestra el valor con su estado.

### 3.3 Cuando alguien intenta una operación que su rol no permite

1. `lib/screens/ajustes/ajustes_screen.dart:17-18 y 38-43` — la aplicación **oculta** el acceso a la gestión de usuarios si el perfil no es de administración. Es comodidad: no protege nada.
2. `lib/screens/ajustes/usuarios_admin_screen.dart:41-51` — la pantalla consulta las cuentas por el servicio.
3. `lib/repositories/api/usuarios_api_repository.dart:62-66` — `GET /api/v1/usuarios`.
4. `lib/services/api_cliente.dart:233` — la petición viaja con `Authorization: Bearer <token>`.
5. `backend/app/seguridad.py:59-105` — el servicio resuelve la identidad y el rol **desde el perfil de la base**, no desde lo que diga el cliente.
6. `backend/app/rutas/usuarios.py:137-142` — la ruta declara `Depends(requiere_administracion)` en la línea 138: el código de la ruta **no llega a ejecutarse**.
7. `backend/app/seguridad.py:113-122` — se lanza el 403 con `rol_requerido` y `rol_actual`.
8. `backend/app/errores.py:63-68` — el manejador le da el formato uniforme `{codigo, mensaje, detalle}`.
9. `lib/services/api_cliente.dart:318-340` — el cliente traduce el cuerpo a un `ErrorApi` con su código y su mensaje.
10. `lib/services/api_errores.dart:40` — `esSinPermiso`; no se cierra la sesión, porque el 403 no es un problema de sesión.
11. `lib/screens/ajustes/usuarios_admin_screen.dart:53-61` — la pantalla muestra «La cuenta con la que inició sesión no tiene atribuciones de administración».
12. `backend/pruebas/test_api_autorizacion.py:59-67` — la prueba que fija ese comportamiento: 403, código `sin_permiso` y `rol_actual` en el detalle.
13. `firestore.rules:87-103` — el cierre por el otro lado: aunque alguien llame a la base directamente, no puede crearse con rol de administrador ni cambiarse el rol.

### 3.4 Cuando el token vence

1. `lib/services/api_cliente.dart:59-60` — la aplicación pide el token de identidad antes de cada petición.
2. `backend/app/seguridad.py:49-56` — el servicio lo verifica; si está vencido o no es válido, responde **401**.
3. `lib/services/api_cliente.dart:310-316` — el cliente ve el 401 y avisa.
4. `lib/main.dart:97` — el aviso está conectado a `AuthService.cerrarSesionPorExpiracion`.
5. `lib/services/auth_service.dart:38-41` — se deja el mensaje «Tu sesión venció. Volvé a iniciar sesión.» y se cierra la sesión.
6. `lib/screens/auth_gate.dart:15-22` — sin usuario, la aplicación vuelve a la pantalla de inicio de sesión.
7. `lib/screens/login_screen.dart:31-37` — la pantalla consume el aviso y lo muestra.
8. `lib/services/auth_service.dart:44-48` — el aviso se consume una sola vez, para que no reaparezca en cada visita.
9. `test/api_cliente_test.dart:304-329` — la prueba: el 401 del servicio cierra la sesión local.
10. `test/api_cliente_test.dart:331-366` — la prueba complementaria: un fallo de conexión y la falta de token local **no** la cierran.

### 3.5 Cuando se registra una medición a mano desde el panel

1. `lib/screens/home_screen.dart:349-356` — el botón «Registrar medición» abre el diálogo.
2. `lib/screens/home_screen.dart:588-601` — se envían **solo** las variables que el usuario completó; un campo vacío no registra un cero.
3. `lib/controllers/panel_controller.dart:161-197` — se registra variable por variable; si una falla, se conserva el primer fallo y se continúa.
4. `lib/repositories/api/lecturas_api_repository.dart:58-75` — `POST /api/v1/lecturas/manual`.
5. `backend/app/rutas/lecturas.py:60-79` — la ruta exige `requiere_operacion` y el servidor fija el origen `manual` y el autor desde la sesión.
6. `backend/app/esquemas.py:141-146` — el esquema de la lectura manual no admite el campo `origen`: el cliente no puede declararla automática.
7. `backend/app/servicios/lecturas.py:55-87` — la misma evaluación y la misma generación de alerta que usa el envío del módulo.
8. `lib/controllers/panel_controller.dart:191` — al terminar, el panel se **vuelve a consultar** en lugar de suponer el resultado.
9. `backend/pruebas/test_api_lecturas.py:135-142` — la prueba: la lectura manual conserva el usuario que la registró.
10. `backend/pruebas/test_api_lecturas.py:155-162` — la prueba: si el cliente intenta declarar quién registró la lectura, el contrato responde **422**.

---

## 4. Cambios simples para practicar

Tres cambios que se hacen en pocos minutos, con el archivo, la línea, el texto exacto y cómo
comprobar que quedó bien. Los tres están elegidos para **no romper ninguna prueba**.

### 4.1 Cambiar un texto que ve el usuario

**Qué se cambia.** El título del aviso de estado del panel: de «Sistema con alertas» a «Hay variables
fuera de rango».

**Archivo y línea.** `lib/screens/home_screen.dart`, línea **673**.

**Qué escribir.** La línea dice:

```dart
    final titulo = hayAlertas ? 'Sistema con alertas' : 'Sistema normal';
```

Se reemplaza por:

```dart
    final titulo = hayAlertas ? 'Hay variables fuera de rango' : 'Todo dentro del rango';
```

**Cómo comprobar que quedó bien.**

1. `flutter analyze` — sin observaciones.
2. `flutter test` — las 96 pruebas siguen en verde (ninguna prueba afirma ese texto; comprobado
   buscando «Sistema con alertas» en `test/`).
3. En la aplicación, forzar una alerta (registrar un pH de 7,4 con el rango 5,5–6,5) y ver el texto
   nuevo en el panel.

**Lo que hay que decir mientras se hace.** Ese texto está citado en el manual de usuario
(`docs/33_ANEXO_A_MANUAL_DE_USUARIO.md:102` y `:414`): un cambio de texto visible obliga a revisar el
manual. Decirlo demuestra que se entiende el efecto del cambio, no solo el cambio.

**Variante con prueba.** Si el tribunal quiere ver el texto de la etiqueta de estado, está en
`lib/models/api/modelos_api.dart:249` (`return 'Normal';`). Pero **dos pruebas lo afirman**:
`test/panel_controller_test.dart:146` y `test/repositorios_api_test.dart:489`. Cambiarlo es un
ejercicio de dos pasos: se cambia el código y se actualiza la prueba, y eso se muestra.

### 4.2 Agregar una validación

**Qué se agrega.** Que la observación de una lectura, si se escribe, tenga al menos 3 caracteres. Hoy
solo se limita el máximo.

**Archivo y línea.** `backend/app/esquemas.py`, línea **80**.

**Qué escribir.** La línea dice:

```python
    observacion: str | None = Field(default=None, max_length=200)
```

Se reemplaza por:

```python
    observacion: str | None = Field(default=None, min_length=3, max_length=200)
```

**Cómo comprobar que quedó bien.**

1. `python -m pytest backend/pruebas -q` — las 119 pruebas siguen en verde (comprobado: ninguna prueba
   envía una observación de menos de 3 caracteres; la más corta es «medición con kit colorimétrico»).
2. La prueba de la API, con una observación de dos letras, tiene que responder 422 con el campo
   señalado:

```powershell
curl -X POST https://sigvach-api.onrender.com/api/v1/lecturas/manual `
  -H "Authorization: Bearer <token del operador>" -H "Content-Type: application/json" `
  -d '{"modulo_id":"<id>","variable":"ph","valor":6.1,"observacion":"ok"}'
```

Responde `422` con `{"codigo":"validacion_rechazada", ... "detalle":{"campos":{"observacion":"String should have at least 3 characters"}}}`.

3. Con una observación válida y larga, sigue respondiendo 201.

**Lo que hay que decir.** La validación se agrega en **el esquema**, que es la puerta del servidor: por
eso vale tanto para la aplicación como para el módulo y para cualquier cliente. Es el requisito mínimo
8 aplicado.

### 4.3 Modificar el valor de un rango de referencia

**Qué se cambia.** El rango de pH del perfil de demostración: de 5,5–6,5 a 5,8–6,4.

**Archivo y línea.** `backend/app/semilla.py`, línea **28**.

**Qué escribir.** La línea dice:

```python
    ('ph', 5.5, 6.5),
```

Se reemplaza por:

```python
    ('ph', 5.8, 6.4),
```

**Cómo comprobar que quedó bien.**

1. `python -m pytest backend/pruebas -q` — todo sigue en verde. Comprobado de antemano: ninguna lectura
   de la semilla queda entre 5,5 y 5,8 ni entre 6,4 y 6,5 (las lecturas de pH son 6,0, 6,1, 6,2, 6,3 y
   7,4), así que la semilla sigue generando **exactamente tres alertas** y `backend/pruebas/test_semilla.py:31-34`
   sigue pasando.
2. Levantar el servicio con `USAR_REPOSITORIO_EN_MEMORIA=true` y abrir `http://127.0.0.1:8011/api/v1/rangos`:
   el rango de pH tiene que decir `minimo: 5.8, maximo: 6.4`.
3. En el panel, la tarjeta del pH muestra «Rango: 5,8 – 6,4».

**Lo que hay que decir.** El rango de referencia vive en el **perfil de cultivo**, no en el código de la
evaluación: por eso se puede cambiar sin tocar la regla que evalúa. Y conviene decir también la verdad
del alcance: la semilla solo se carga con `USAR_REPOSITORIO_EN_MEMORIA=true`; en producción el rango se
cambia desde Ajustes o con `PATCH /api/v1/rangos/{id}`, que exige el rol de administración
(`backend/app/rutas/rangos.py:91-120`).

**Variante con prueba (para lucirse).** Si en lugar de 5,8–6,4 se angosta a 5,9–6,1, tres lecturas de
pH pasan a estar fuera y la semilla genera cinco alertas: entonces hay que **actualizar**
`backend/pruebas/test_semilla.py:31-34`, que hoy afirma tres. Cambiar código y prueba, y explicar por
qué cambió la prueba, es exactamente lo que la rúbrica llama dominio técnico.

---

## 5. Glosario breve

| Término | Qué es, en una línea |
|---|---|
| **API** | La puerta por la que otros programas le piden datos y acciones a nuestro sistema. |
| **REST** | Estilo de API que usa direcciones y los métodos HTTP (GET, POST, PATCH, DELETE) para nombrar recursos. |
| **Endpoint** | Una dirección concreta de la API con su método: por ejemplo `POST /api/v1/lecturas`. |
| **Ruta** | El camino de una dirección, sin el dominio: `/api/v1/lecturas`. |
| **Contrato de la API** | El acuerdo escrito de qué entra y qué sale en cada endpoint; acá vive en los esquemas y se publica solo en `/docs` (OpenAPI). |
| **OpenAPI** | El documento que describe la API y que FastAPI genera desde el propio código; se ve en `/docs`. |
| **Backend** | El servicio del servidor: valida, autoriza y guarda. En este proyecto, `backend/app/`. |
| **Frontend** | Lo que ve y usa la persona; acá es la aplicación Flutter de `lib/`. |
| **Firmware** | El programa que corre dentro del módulo de adquisición (el ESP32), en `hardware/firmware/main/`. |
| **Controlador** | La pieza de la aplicación que pide los datos, resuelve los estados de la vista y avisa a la pantalla; en `lib/controllers/`. |
| **Repositorio (patrón)** | La pieza que aísla el acceso a los datos detrás de una interfaz; acá `backend/app/repositorios/base.py` con dos implementaciones: Firestore y memoria. |
| **Repositorio (git)** | El proyecto guardado con su historial de confirmaciones, en GitHub. El contexto dice cuál de los dos sentidos se está usando. |
| **Esquema (schema)** | La declaración de qué campos tiene un dato, de qué tipo y con qué límites; en `backend/app/esquemas.py`. |
| **Modelo** | La clase que representa un dato dentro de la aplicación; en `lib/models/`. |
| **Inyección de dependencias** | Que una función reciba lo que necesita en lugar de fabricarlo; en FastAPI se escribe `Depends(...)`. |
| **Dependencia (FastAPI)** | La función que se ejecuta antes del endpoint y puede cortarlo; así se aplica la autorización. |
| **Middleware** | Una capa que envuelve todas las peticiones antes de llegar a las rutas; acá el único es el de CORS. |
| **CORS** | La regla del navegador que decide qué páginas pueden llamar a la API; se configura con `ALLOWED_ORIGINS`. |
| **Token de identidad** | El pase firmado que emite el proveedor de identidad al iniciar sesión y que la aplicación envía en cada petición. |
| **Proveedor de identidad** | El servicio externo que administra las cuentas y las contraseñas; acá, Firebase Authentication. |
| **Hash** | El resumen irreversible de una contraseña: se guarda el resumen, no la contraseña. Lo aplica el proveedor; no está en este repositorio. |
| **Rol** | El conjunto de atribuciones de una cuenta: administrador, operador o invitado. |
| **Autorización** | Decidir qué puede hacer una identidad ya autenticada; en `backend/app/seguridad.py`. |
| **Autenticación** | Comprobar quién es: verificar el token o la clave del dispositivo. |
| **401** | No estás autenticado: falta el token, es inválido o venció. |
| **403** | Estás autenticado, pero tu rol no alcanza para esta operación. |
| **404** | El recurso no existe. |
| **409** | La operación choca con el estado actual (módulo inactivo, perfil con rangos, la administración queriendo cambiar su propio rol). |
| **422** | Los datos enviados no cumplen el contrato; el detalle indica el campo. |
| **500** | Error no previsto del servidor; el detalle técnico no se le muestra al cliente. |
| **Validación** | Comprobar que un dato cumple el contrato y sus límites, antes de guardarlo. |
| **Variable de entorno** | Un valor que se le pasa al proceso al arrancar, en lugar de escribirlo en el código. |
| **`.env`** | El archivo local con esas variables; **no se versiona**, y su plantilla es `.env.example`. |
| **Migración** | El cambio ordenado de esquema o de datos de una base. Acá **no hay migraciones**: Firestore no tiene esquema fijo; lo que hubo fue una migración de proveedor (de Supabase a Firebase, `lib/config/app_config.dart:1-7`) y una de vocabulario de roles (`lib/models/roles.dart:1-13`). |
| **Semilla** | Los datos de demostración que se cargan cuando el servicio arranca sin credenciales; en `backend/app/semilla.py`. |
| **Colección y documento** | Las dos unidades de Firestore: la colección agrupa y el documento guarda un registro. |
| **Índice compuesto** | El índice que Firestore exige para consultar por más de un campo a la vez; están declarados en `firestore.indexes.json`. |
| **Reglas de seguridad** | Las reglas de la base que deciden quién puede leer y escribir; acá cierran todo al cliente y dejan solo el perfil propio (`firestore.rules`). |
| **NVS** | La memoria no volátil del ESP32: lo que se guarda ahí sobrevive al corte de luz. |
| **ADC** | El conversor analógico-digital del ESP32: convierte la tensión de los sensores en un número. |
| **Calibración** | La recta o polinomio que traduce una tensión a una magnitud física (pH, ppm). |
| **SNTP** | El protocolo con el que el módulo pone su reloj por Internet, para poder fechar las lecturas. |
| **Estado de la vista** | Los cuatro casos que toda pantalla que consume datos tiene que resolver: cargando, con datos, vacío y con error. |
| **Despliegue** | Publicar el sistema para que se use desde Internet: el servicio en la nube y la aplicación web en Firebase Hosting. |
| **Integración continua** | Ejecutar pruebas y compilaciones automáticamente en cada confirmación; acá, `.github/workflows/verificacion.yml`. |
| **Monitoreo** | Consultar la ruta de salud cada quince minutos para saber si el sistema está en pie; `.github/workflows/monitoreo.yml`. |
| **Ruta de salud** | `GET /api/v1/salud`: informa si el servicio responde y si la base contesta. |

---

## 6. Cosas que conviene revisar antes de la defensa

**Estado al 5 de octubre de 2026.** Todo lo que sigue salió de leer el código y compararlo con los
documentos. La lista tiene tres partes: lo que **ya quedó resuelto** —verificado hoy abriendo cada
archivo—, lo que **sigue vigente** y lo que **apareció al revisar los textos que se usan en vivo**.
Importante: si el autor repite como pendiente algo de la primera parte, se está restando puntos solo.
Las otras cinco secciones de esta guía ya están ajustadas a este estado.

### 6.1 Ya resuelto (verificado el 5/10 leyendo el archivo)

| # | Qué era el problema | Qué se hizo | Dónde se comprueba |
|---|---|---|---|
| 1 | El comentario de la ruta de salud citaba el **RNF-02** (seguridad) para la suspensión por inactividad de la capa gratuita | Ahora cita el requisito correcto: **RNF-05 (disponibilidad)** | `backend/app/rutas/salud.py:6` |
| 2 | **No existía respaldo de la base** | Se agregó `scripts/respaldar_base.py`, que exporta perfiles, módulos, rangos, lecturas y alertas a un JSON fechado dentro de `respaldos/` (carpeta excluida por `.gitignore:61-65`), y `scripts/restaurar_prueba_base.py`, con **una restauración probada contra el servicio publicado** | `scripts/respaldar_base.py`, `scripts/restaurar_prueba_base.py`, `evidencia/restauracion-2026-10-05.txt` |
| 3 | **No había registro de una línea por petición** | Se agregó `backend/app/registro_peticiones.py`: un middleware ASGI que escribe `peticion metodo=… ruta=… codigo=… duracion_ms=…`, con la **ruta declarada** (los identificadores salen como `{modulo_id}`), y **sin** credenciales, cuerpos ni cadena de consulta | `backend/app/registro_peticiones.py`, `backend/app/main.py:129` y `:153`, `backend/app/config.py:44-47`, `.env.example:19-23`, `backend/pruebas/test_registro_peticiones.py` |
| 4 | `.env.example` se contradecía: hablaba de «admin y usuario» | Quedó un solo bloque coherente con los tres roles y su alcance | `.env.example:34-43` |
| 5 | «Siete variables» donde el catálogo tiene **seis** | Corregido a «seis variables» | `scripts/llenar_perfil_e1.py:382` (RF-04), `:410` (RF-11) y `:581`; `scripts/simulador_dispositivo.py:19` |
| 6 | `docs/28` decía «28 rutas» | Ahora dice **32 endpoints** con el desglose: 30 exigen identidad de usuario (**28** de ellos con una dependencia de rol y **2** con solo el perfil propio), **1** se autentica con la clave del dispositivo y **1** es público. Verifiqué el desglose y es exacto: los dos que solo piden el perfil propio son `GET` y `PATCH /api/v1/usuarios/perfil` | `docs/28_MAPA_DEL_REPOSITORIO_PARA_LA_DEFENSA.md:44` |
| 7 | Dos códigos distintos para el mismo 400: `"solicitud_invalida"` frente a `"datos_invalidos"` | Unificados en `datos_invalidos`, usando la constante `CODIGO_DATOS_INVALIDOS` | `backend/app/rutas/usuarios.py:106` y `:188`; constante en `backend/app/errores.py:18` |
| 8 | `sensores.h` decía «pH (pendiente)» | Ahora dice «pH (calibrado y publicado)» | `hardware/firmware/main/sensores.h:7` |
| 9 | `api_errores.dart` tenía un bloque de comentario duplicado y fuera de lugar | Corregido: queda una sola descripción, limpia | `lib/services/api_errores.dart:75-79` |

**Los dos que conviene mostrar en vivo, porque son nuevos y se ven.**

- **El respaldo y su restauración probada.** Correr `python scripts/respaldar_base.py` (necesita el
  archivo de credenciales **fuera** del repositorio, `C:\Users\<usuario>\credenciales-sigvach\operador.txt`)
  y después abrir `evidencia/restauracion-2026-10-05.txt`. Ese informe muestra, paso por paso, la
  exportación del dominio, la creación de un módulo de prueba, la restauración de tres lecturas, la
  evaluación que hizo el servidor de cada una —el campo `estado_rango` de la respuesta—, el borrado de
  todo lo creado y la comprobación final de que la base quedó igual: **1000 lecturas y 605 alertas
  antes y después, 0 desaparecidas** (líneas 130-136). La conclusión está en las líneas 138-146.
- **La línea por petición.** Correr `python -m pytest backend/pruebas/test_registro_peticiones.py -q`
  y, si se levanta el servicio en local, señalar en la consola la línea
  `peticion metodo=GET ruta=/api/v1/salud codigo=200 duracion_ms=…`. El nivel se controla con
  `NIVEL_REGISTRO` (`.env.example:23`; por omisión `INFO`, en `backend/app/config.py:45`).

### 6.2 Sigue vigente

1. **El rol llega a la aplicación por dos caminos distintos.** El encabezado del menú lo pide a la API
   (`lib/controllers/perfil_controller.dart:46`), pero el menú de Ajustes decide si muestra la gestión
   de usuarios leyendo **directo de Firestore** (`lib/controllers/usuario_controller.dart:27` →
   `lib/repositories/usuario_repository.dart:66-70`). Si preguntan «¿de dónde saca la aplicación el
   rol?», la respuesta honesta es esa, con la aclaración de que la decisión que importa la toma el
   servidor.
2. **Queda un método muerto que escribe la base directamente.** Los cinco que había antes
   (`listarTodos`, `verTodos`, `cambiarRol`, `cambiarActivo`, `eliminar`) **ya se eliminaron el 5/10**,
   pero `actualizarDatos` sigue en el archivo, sigue escribiendo directo (`_doc(uid).update(data)`) y no
   lo llama nadie: lo comprobé con una búsqueda de `actualizarDatos` en todo `lib/`, que devuelve solo
   su propia definición. Mientras esté, el comentario de `backend/app/rutas/usuarios.py:14-17` y el de
   `lib/repositories/api/usuarios_api_repository.dart:55-59` no son del todo ciertos, y
   `firestore.rules:96-103` todavía permitiría esa escritura a un administrador.
3. **El borrado físico de lecturas sigue existiendo.** `DELETE /api/v1/lecturas/{id}`
   (`backend/app/rutas/lecturas.py:161-173`) borra de verdad.
   `docs/22_RECOMENDACIONES_T3_VERIFICADAS.md` recomendaba quitarlo o convertirlo en anulación con
   motivo, porque contradice la trazabilidad del RNF-08. Decirlo antes de que lo pregunten.
4. **El algoritmo de hash de las contraseñas es externo al repositorio.** Lo aplica el proveedor de
   identidad. No se puede mostrar en el código porque no está: conviene decir «no lo elegimos nosotros,
   lo aplica el proveedor» en lugar de afirmar un algoritmo que no se puede respaldar con un archivo.
5. **`hardware/firmware/main/configuracion.h` tiene secretos reales y está en el disco.**
   **NO ABRIRLO CON LA PANTALLA COMPARTIDA.** Tiene el nombre y la clave del WiFi y la clave del
   dispositivo. Verifiqué que **no** está versionado (`git ls-files --error-unmatch` no lo conoce, y
   `git check-ignore -v` lo atribuye a `hardware/firmware/.gitignore:17`, con la red de seguridad de
   `.gitignore:66-67`), así que el repositorio está limpio; el riesgo es solo el de la demostración en
   vivo. Si hay que mostrar la configuración, usar `hardware/firmware/main/configuracion.ejemplo.h`.
6. **El puerto por defecto del código no es el que usa el entorno local.** `backend/app/config.py:38`
   tiene `8000` por defecto, mientras `.env.example:14` y `lib/config/api_config.dart:36` usan `8011`.
   Si falta el `.env`, el servicio arranca en 8000 y la aplicación busca en 8011: un fallo de conexión
   que parece un problema de red y es de configuración.
7. ~~**Faltaba un índice compuesto y ya produjo un error del servidor en producción.**~~
   **Resuelto**: el índice `alertas(modulo_id, timestamp)` está declarado en
   `firestore.indexes.json:36-43` (seis índices en total) y desplegado con
   `firebase deploy --only firestore:indexes --project sigvach26-bd`. La consulta
   `/api/v1/alertas?modulo_id=…` que respondía **HTTP 500** (`evidencia/restauracion-2026-10-05.txt:51`)
   ahora responde **200**, y conviene decirlo así si alguien recuerda el 500. Queda en pie el otro
   detalle de ese punto: la API no pagina alertas, el máximo es 500 por consulta
   (`scripts/respaldar_base.py:51-53`).
8. **Si falta `firebase-admin`, todo lo autenticado responde 500 y no 401.**
   `backend/app/seguridad.py:43-48` devuelve 500 cuando el verificador no está disponible. Es correcto
   para diagnosticar, pero conviene saber que un despliegue sin esa dependencia no falla «por falta de
   sesión» sino por error interno.

### 6.3 Apareció al revisar los textos que se usan en vivo

9. **`hardware/firmware/LEEME.md:76`** dice «**PH-4502C** *(pendiente)*» en el inventario de
   conexionado: es el mismo reclamo viejo que se corrigió en `sensores.h:7`. El pH está calibrado y
   publicado desde el 4 de octubre (`hardware/firmware/main/main.c:99-103` y `:764-777`).
10. **«Siete variables» en los textos que se dicen en voz alta.** La respuesta correcta en la defensa
    es **seis**. Ojo con esto: los dos primeros archivos **no están en el repositorio**, viven en
    `D:\SIGVACH-Monograf\`, un nivel arriba de `Proyecto SIGVACH`, así que no se los encuentra buscando
    dentro del proyecto.
    - `Guia para la tutoria - 2026-09-15.md`, líneas 37, 46 y 111.
    - `Hoja de apoyo - tutoria 2026-09-15.md`, líneas 12 y 21.

    Dentro del repositorio quedan estas menciones viejas, todas del mismo error:
    `docs/BITACORA_LUNES_2026-09-14.md:51, 71, 96 y 190`;
    `docs/BITACORA_MARTES_2026-09-15.md:214 y 260` (escrito «7 variables»);
    `docs/BITACORA_MARTES_2026-09-22.md:169 y 224`; y `docs/09_PLAN_MODULO4.md:291 y 369`.
11. **El arranque en frío aparece con cifras distintas según el documento.** El requisito quedó en
    **60 s**, así que conviene unificar en 60 s:
    - `backend/README.md:240-241` dice «hasta treinta segundos»;
    - `docs/10_DESPLIEGUE.md:248` dice «veinte o treinta segundos»;
    - `docs/14_GLOSARIO_DE_CONCEPTOS.md:407` dice «los 50 segundos» y, en la línea 411, «50-60
      segundos», mientras la línea 524 del mismo archivo dice «**60 s** (RNF-05)»: se contradice
      consigo mismo;
    - `README.md:278` dice «cincuenta segundos o más», que es lo más cercano a lo correcto.

    El número que hay que decir es **60 segundos**: es lo que declara el RNF-05, lo que espera el
    cliente antes de darse por vencido (`lib/config/api_config.dart:66`) y lo que aguanta el firmware
    (`hardware/firmware/main/publicacion.c:23`).
12. **`docs/09_PLAN_MODULO4.md:320` habla de «las siete variables de entorno» de `render.yaml`**, y ese
    número está viejo: `render.yaml:28-45` declara **seis** (`PYTHON_VERSION`, `ENTORNO`,
    `FIREBASE_PROJECT_ID`, `ALLOWED_ORIGINS`, `DEVICE_API_KEY`, `FIREBASE_SERVICE_ACCOUNT_JSON`), y las
    que se cargan a mano en el panel son **tres**, no cuatro (las que llevan `sync: false`). La misma
    cuenta vieja está en `docs/BITACORA_LUNES_2026-09-14.md:167`.
13. **Los números de las pruebas quedaron viejos en la evidencia.** Esta es la que más puede doler en
    la pregunta 6, porque se muestra justamente ese archivo. El número vigente —ya corregido en
    `evidencia/LEEME.md:9-29`— es de **245 pruebas: 149 del servicio y 96 de la aplicación**, con los
    informes `pytest-2026-10-05-memoria-lecturas.txt` y `flutter-test-2026-10-05.txt` del 5/10. Los
    informes del 29 de septiembre se conservan como historial y dicen 202: son anteriores a los trece
    casos del registro de peticiones y a los treinta de la memoria intermedia. Si se muestra un informe
    viejo, decir el número correcto y explicar por qué el guardado es anterior — o volver a correr las
    dos baterías con los comandos de `evidencia/LEEME.md:35-42` y guardar el informe con la fecha del
    día. Lo mismo pasa con `docs/32_LISTA_DE_VERIFICACION_DEL_E4.md:40-44`, que sigue listando como
    pendientes el respaldo y la línea por petición.

**Resumen para tener a mano: 9 puntos resueltos el 5/10 y 13 vigentes** (ocho de la sección 6.2 y
cinco de la 6.3). De los vigentes, dos son los que más conviene tener preparados: el **séptimo**, que
es el único que hoy produce un error visible en producción, y el **decimotercero**, porque toca el
archivo que se muestra al responder la pregunta 6.

