# 28 · Mapa del repositorio para la defensa

**Para qué sirve.** La plenaria P4 lo dice sin vueltas: *«Quien no ejecuta ni explica su sistema, no
aprueba la defensa. La falta de dominio técnico anula el componente, con independencia de quién haya
escrito el código. Usar IA está permitido; no entender lo que entregó, no.»* El criterio **dominio
técnico** vale **30 de los 100 puntos**, y las preguntas son ocho y se conocen de antemano.

Este documento es el mapa: para cada pregunta, **qué se responde**, **dónde está en el repositorio**
y **cómo se muestra en vivo**.

---

## 1. El recorrido de los siete minutos

| Tramo | Qué se muestra | Dónde se ensaya |
|---|---|---|
| 0:00 – 1:00 | **Problema y usuario.** Quién usa el sistema, qué hacía antes y qué dato lo prueba. **Una sola diapositiva** | El apartado 1 del documento |
| 1:00 – 4:30 | **El flujo Must completo en producción.** Inicio de sesión con el usuario de prueba, panel con las variables, una lectura manual y el historial | https://sigvach26-bd.web.app |
| 4:30 – 5:30 | **Seguridad en vivo.** Con la sesión del operador se intenta una operación de administración y se ve el rechazo | La cuenta `operador@proyecto.test` |
| 5:30 – 7:00 | **Evidencia.** La tabla de pruebas, el repositorio y su historial | `evidencia/` |
| 7:00 – 12:00 | **Preguntas**, con el sistema abierto | Este documento |

> **A los 7 minutos se corta la demostración, esté donde esté.** Conviene ensayarlo con cronómetro:
> es lo que se hace en la tutoría T4 del **viernes 9 de octubre a las 17:00**.

---

## 2. Las ocho preguntas

### 2.1 ¿Dónde se verifica el rol?

**Respuesta.** En el servicio, con una dependencia que se aplica a **cada ruta protegida**. La
interfaz puede esconder un botón, pero eso no protege nada: quien decide es el servidor, a partir
del perfil del usuario en la base.

**Dónde está:**

| Archivo | Línea | Qué hace |
|---|---|---|
| `backend/app/seguridad.py` | 59 | `usuario_actual`: lee el token, busca el perfil y resuelve el rol |
| `backend/app/seguridad.py` | 108 | `requiere_administracion` |
| `backend/app/seguridad.py` | 126 | `requiere_consulta` |
| `backend/app/seguridad.py` | 150 | `requiere_operacion` |
| `backend/app/rutas/*.py` | — | **28 rutas** declaran su dependencia; por ejemplo `usuarios.py:167` |

**Cómo se muestra en vivo.** Con la sesión del operador se llama a `GET /api/v1/usuarios` y el
servicio responde:

```
HTTP 403
{"codigo":"sin_permiso","mensaje":"La operación requiere el rol de administrador.",
 "detalle":{"rol_requerido":["administrador"],"rol_actual":"operador"}}
```

Y se abre `seguridad.py` en la pantalla para mostrar la dependencia que lo produce.

### 2.2 ¿Qué pasa si el token vence?

**Respuesta.** La API responde **401** y la aplicación **cierra la sesión y vuelve al inicio de
sesión**, mostrando el motivo: «Tu sesión venció. Volvé a iniciar sesión.»

**Dónde está:**

| Archivo | Qué hace |
|---|---|
| `backend/app/seguridad.py:65` | Sin cabecera `Authorization`, responde 401 `no_autenticado` |
| `lib/services/api_cliente.dart` | Al recibir un 401 del servicio, avisa con `alExpirarLaSesion` |
| `lib/services/auth_service.dart` | `cerrarSesionPorExpiracion`: cierra la sesión y deja el aviso |
| `lib/screens/login_screen.dart` | Muestra el aviso al volver a la pantalla de inicio |
| `test/api_cliente_test.dart` | Dos pruebas: el 401 **cierra** la sesión y un fallo de conexión **no** la cierra |

**La decisión que conviene contar.** Sólo el 401 del **servidor** cierra la sesión, no la falta de
token en el equipo. Al arrancar, el proveedor de identidad tarda unos milisegundos en restaurar la
sesión; si una pantalla pidiera datos en ese instante, cerrar la sesión dejaría al usuario afuera sin
motivo. Ese razonamiento está escrito en el propio código.

**Cómo se muestra en vivo.**

```powershell
flutter test test/api_cliente_test.dart
```

### 2.3 ¿Cómo guarda las contraseñas?

**Respuesta.** **Nuestro servicio nunca ve la contraseña.** El ingreso lo resuelve el proveedor de
identidad, que guarda el *hash* del lado del servidor; lo único que viaja hacia la API es el token
firmado, y el servicio lo verifica en cada petición.

**Dónde está:** `lib/services/auth_service.dart` (el ingreso y el alta contra el proveedor) y
`backend/app/seguridad.py:39` (`_verificar_token_identidad`).

### 2.4 ¿Dónde están los secretos?

**Respuesta.** En **variables de entorno de la plataforma**. El repositorio sólo guarda **los
nombres** de las variables (`.env.example`), nunca los valores. Hay un verificador que lo comprueba
sobre los archivos **y sobre el historial** de confirmaciones.

**Dónde está:** `.env.example`, `docs/10_DESPLIEGUE.md` (la lista de variables) y
`scripts/verificar_sin_secretos.py`.

**Cómo se muestra en vivo.**

```powershell
python scripts/verificar_sin_secretos.py
```

### 2.5 ¿Por qué este stack?

**Respuesta.** Cada elección se justifica contra un requisito **por su identificador**, no por
preferencia: el servicio separado porque la validación y la autorización no pueden depender del
cliente; la base documental por el modelo de datos y su escalabilidad; la aplicación multiplataforma
porque el requisito de compatibilidad pide Android desde la versión 8.

**Dónde está:** `docs/08_INFORME_DE_CAMBIOS.md` (por qué el servicio y por qué la base) y el
apartado 2.1 del documento.

### 2.6 ¿Cómo sabe que funciona?

**Respuesta.** Con la tabla de casos del apartado 2.8 y su evidencia: **202 pruebas automatizadas**
(106 del servicio y 96 de la aplicación) más los casos medidos contra el servicio publicado.

**Dónde está:** `evidencia/` (informes con fecha, incluido el JUnit del servicio),
`backend/pruebas/` y `test/`.

**Cómo se muestra en vivo.**

```powershell
.venv\Scripts\python.exe -m pytest backend -q --no-header
flutter test
```

### 2.7 ¿Qué pasa si se cae?

**Respuesta.** Tres capas:

1. **El módulo no pierde lecturas:** guarda en memoria no volátil lo que no pudo enviar y lo
   reintenta (`hardware/firmware/main/cola_nvs.c` y `publicacion.c`). Está verificado en la
   evidencia del 30/09: el primer envío esperó 40 segundos al servicio dormido y **no se perdió
   ninguna lectura**.
2. **El servicio despierta solo:** la capa gratuita se suspende por inactividad y la primera
   petición puede tardar hasta **60 segundos**, que es exactamente lo que declara el requisito
   RNF-05, y el cliente espera ese tiempo antes de darse por vencido.
3. **Pendiente declarado:** el monitoreo de disponibilidad y el respaldo de la base son del **E4**.

### 2.8 ¿Qué quedó pendiente?

**Respuesta, sin esconder nada.**

| Pendiente | Estado |
|---|---|
| La **calibración del TDS** | El módulo publica el TDS, pero todavía con el factor de fábrica: falta contrastarlo con el patrón de 1413 µS/cm, que está pedido y en camino. El **pH sí quedó calibrado** el 1 de octubre, con los patrones de 4,01 y 6,86 |
| El **monitoreo y el respaldo** de la base | Del E4 |
| El punto `DELETE /api/v1/lecturas/{id}` | Quitado de la tabla de requisitos; queda decidir si se elimina del servicio o se convierte en anulación con motivo |
| El **rendimiento con respuestas grandes** | Medido: cumple con el tamaño que usa el panel (536 ms de percentil 95) y no cumple con 200 registros (1042 ms). La optimización, con su número antes y después, es del E4 |

---

## 3. Si piden un cambio pequeño en vivo

Pueden pedir un texto, una validación o un campo. Conviene saber dónde se toca cada cosa:

| Qué cambian | Dónde |
|---|---|
| Un mensaje de error del servicio | `backend/app/errores.py` |
| Una regla de validación | `backend/app/esquemas.py` |
| Una ruta o su contrato | `backend/app/rutas/<recurso>.py` |
| Un texto de una pantalla | `lib/screens/<pantalla>.dart` |
| El nombre o la unidad de una variable | `lib/models/api/modelos_api.dart` |
| Un valor del firmware (intervalo, pin) | `hardware/firmware/main/configuracion.h` |

---

## 4. Los números que hay que saber de memoria

| Dato | Valor |
|---|---|
| Pruebas automatizadas | **202** (106 del servicio + 96 de la aplicación) |
| Rutas protegidas por rol | **28** |
| Variables publicadas | **6**: temperatura ambiental, humedad, temperatura de la solución, sólidos disueltos totales, conductividad eléctrica y pH |
| Colecciones de la base | **6** |
| Cuentas de prueba | **2**, una por rol, del dominio `.test` |
| Confirmaciones en el repositorio | **161**, en **17 días distintos** |
| Demora admitida al despertar el servicio | **60 s** (RNF-05) |
| Objetivo de rendimiento de la API | 95 % de las consultas en **800 ms** (RNF-01) |

---

## 5. El día de la defensa

- Sistema abierto **30 minutos antes**, para que la capa gratuita despierte.
- Una cuenta de prueba **por rol**: sin dos cuentas no se puede mostrar el 403.
- El comando de al menos una prueba automatizada, **ya escrito en la terminal**.
- Repositorio y documento abiertos, en el esquema, el contrato y la tabla de pruebas.
- **Cronómetro propio**: siete minutos de demostración.
- Pantalla compartida probada antes del turno.
