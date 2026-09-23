# 16 · Simulador del módulo de adquisición (ESP32)

**Proyecto:** SI.G.VA.C.H. · **Fecha:** 22 de septiembre de 2026
**Requisito que atiende:** el entregable E2 pide la aplicación funcionando contra la
API publicada con **dispositivo simulado**: una alerta generada por un valor fuera de
rango tiene que poder verse en el panel.

---

## 1. Qué es y por qué existe

El sistema está diseñado para que las lecturas entren por dos caminos:

| Origen | Quién lo usa | Autenticación |
|---|---|---|
| **Automático** | El módulo de adquisición (ESP32) | Clave de dispositivo en la cabecera `X-Device-Key` |
| **Manual** | El operador, con instrumentos portátiles | Token de identidad de Firebase |

El ESP32 real todavía no está construido —su modelo está por definir—, de modo que el
camino automático quedaría sin demostrar. El simulador **ocupa el lugar del
dispositivo**: envía las lecturas por el mismo endpoint, con la misma clave y el mismo
cuerpo que enviará el firmware, de manera que el servicio no distingue una lectura
simulada de una real. Eso permite demostrar el flujo completo —adquisición, evaluación
contra el rango del perfil, almacenamiento y alerta— sin hardware.

Además, el simulador reproduce el comportamiento que el firmware **debe** tener: si el
servicio no responde, la lectura **no se descarta**, queda en memoria y se reintenta.
Es la respuesta al problema del arranque en frío de la capa gratuita, donde la primera
petición puede demorar hasta sesenta segundos.

---

## 2. Cómo se ejecuta

El programa está en `scripts/simulador_dispositivo.py`. La clave del dispositivo se lee
del entorno (`DEVICE_API_KEY`) o de los archivos `.env` del proyecto: **nunca se escribe
en el código ni se muestra en pantalla**.

| Para qué | Comando |
|---|---|
| Enviar las siete variables una vez (lo más útil para la demostración) | `python scripts/simulador_dispositivo.py --modulo modulo-1 --ciclos 1` |
| Enviar contra el servicio publicado | `python scripts/simulador_dispositivo.py --url https://sigvach-api.onrender.com --modulo <ID> --ciclos 1` |
| Forzar una alerta | `python scripts/simulador_dispositivo.py --modulo <ID> --ciclos 1 --fuera-de-rango ph` |
| Envío continuo cada cinco minutos | `python scripts/simulador_dispositivo.py --modulo <ID> --intervalo 300` |
| Saber qué pasar en `--modulo` | `python scripts/simulador_dispositivo.py --listar-modulos` |

Opciones principales: `--variable` (repetible, para enviar solo algunas variables),
`--reintentos`, `--espera-reintento`, `--espera` (setenta y cinco segundos por omisión,
para cubrir el arranque en frío), `--ciclos` (0 significa sin límite).

El programa informa el código de salida: **0** si todas las lecturas quedaron
almacenadas y **2** si alguna quedó pendiente en la memoria del dispositivo, de modo que
puede usarse en una verificación automática.

---

## 3. Comportamiento verificado

Las dos pruebas siguientes se ejecutaron el 22 de septiembre contra el servicio local
en **modo de demostración** (`USAR_REPOSITORIO_EN_MEMORIA=true`), de modo que no se
escribió ningún documento en la base real.

### 3.1 Envío normal y generación de la alerta

```
[23:31:22] ciclo 1
    ph                   4.3         201  bajo
    tds               775.93 ppm     201  dentro
    ec                  1.53 mS/cm   201  dentro
    temp_solucion      21.31 °C      201  dentro
    temp_ambiental     21.22 °C      201  dentro
    humedad            59.53 %       201  dentro
    nivel_agua         18.53 cm      201  sin_rango

  Lecturas intentadas:                  7
  Almacenadas por el servicio (201):    7
  Con estado fuera de rango:            1
  Sin enviar (quedaron en memoria):     0
```

El valor forzado de pH (4,3, por debajo del mínimo 5,5 del perfil de lechuga) quedó
evaluado como **`bajo`**, que es lo que genera la alerta que aparece en el panel. La
variable `nivel_agua` informa `sin_rango` porque el perfil de demostración no tiene
rango configurado para ella: el sistema no inventa una alerta sin rango de referencia.

### 3.2 Arranque en frío: memoria y reintento

Se inició el simulador **antes** que el servicio, y el servicio se levantó cuatro
segundos después:

```
[23:33:28] ciclo 1
    ph              intento 1/1 sin respuesta (código sin conexión); reintento en 1 s
    ph              queda en la memoria del dispositivo
    ec              intento 1/1 sin respuesta (código sin conexión); reintento en 1 s
    ec              queda en la memoria del dispositivo

[23:33:45] ciclo 2
  quedan 2 lecturas en memoria: se reintentan
    recuperada: ph             6.31
    recuperada: ec             1.57
    ph                  5.93         201  dentro
    ec                  1.54 mS/cm   201  dentro

  Lecturas intentadas:                  8
  Almacenadas por el servicio (201):    6
  Recuperadas tras reintentar:          2
  Sin enviar (quedaron en memoria):     0
```

Las dos lecturas del primer ciclo **llegaron con su valor original** (pH 6,31 y
EC 1,57) en cuanto el servicio estuvo disponible: no se perdió ninguna medición. Es el
comportamiento que debe implementar el firmware y que quedaba documentado como riesgo
en las observaciones de la tutoría.

### 3.3 Pruebas del servicio

| Comprobación | Resultado |
|---|---|
| Conjunto de pruebas del servicio | **90 casos, todos aprobados** |
| Caso `test_lectura_fuera_de_rango_genera_una_alerta` | Una lectura del dispositivo fuera de rango genera **exactamente una** alerta, con la referencia a la lectura que la originó |
| Caso `test_lectura_dentro_de_rango_no_genera_alerta` | Ninguna alerta cuando el valor está dentro del rango |

---

## 4. Consumo de la base de datos (cuota diaria)

Cada envío del dispositivo escribe **un documento por variable** en la colección
`lecturas`: **siete documentos por envío**, más un documento en `alertas` por cada valor
fuera de rango que se detecte.

La capa gratuita de Cloud Firestore (edición estándar) permite, por día, **20 000
escrituras**, **50 000 lecturas**, **20 000 eliminaciones**, **1 GiB** almacenado y
**10 GiB** de salida al mes; la cuota se reinicia a la medianoche del Pacífico
([Firestore: cuotas y límites](https://docs.cloud.google.com/firestore/quotas)).

| Intervalo de envío | Envíos por día | Documentos por día | % de la cuota de escritura |
|---|---|---|---|
| 30 segundos | 2 880 | 20 160 | **101 % — excede la cuota** |
| 1 minuto | 1 440 | 10 080 | 50 % |
| **5 minutos** | **288** | **2 016** | **10 %** |
| 10 minutos | 144 | 1 008 | 5 % |
| 30 minutos | 48 | 336 | 2 % |

**Decisión.** El intervalo de referencia del prototipo se fija en **cinco minutos**:
consume una décima parte de la cuota de escritura, deja margen para las alertas y para
las lecturas del panel, y es suficiente para el seguimiento de un cultivo hidropónico,
donde las variables evolucionan en horas y no en segundos. Un intervalo de treinta
segundos agotaría la cuota diaria con un solo módulo, y por eso queda descartado
mientras el sistema funcione en la capa gratuita.

**Almacenamiento.** Un documento de lectura ocupa del orden de medio kilobyte; con
cinco minutos de intervalo, 2 016 documentos diarios representan alrededor de **1 MB por
día**, unos **30 MB al mes**: menos del 3 % del gibibyte disponible al año de operación
continua. El factor limitante es la escritura diaria, no el espacio.

**Lecturas.** El panel consulta la última lectura de cada variable y el historial del
periodo elegido. Una sesión de consulta con historial y tendencia ronda las doscientas
lecturas, de modo que la cuota diaria admite del orden de doscientas sesiones: es un
límite que corresponde vigilar, no un riesgo para el prototipo.

---

## 5. Guion para la demostración del E2

| Paso | Acción | Qué se ve |
|---|---|---|
| 1 | Abrir `https://sigvach26-bd.web.app` e iniciar sesión | El panel con el estado de las siete variables |
| 2 | Ejecutar `python scripts/simulador_dispositivo.py --url https://sigvach-api.onrender.com --modulo <ID> --ciclos 1` | Siete lecturas almacenadas con origen automático |
| 3 | Refrescar el panel | Los valores y la hora de la última lectura actualizados |
| 4 | Ejecutar el simulador con `--fuera-de-rango ph` | Una lectura `bajo` y la **alerta** correspondiente en el panel |
| 5 | Abrir el historial de pH | La serie con el valor desviado y la tendencia |
| 6 | Marcar la alerta como atendida | La alerta sale de las activas y permanece en el historial |

> **Antes del paso 2**, si el servicio estuvo inactivo, la primera petición puede tardar
> hasta sesenta segundos: el simulador espera ese tiempo y, si aun así no responde,
> conserva las lecturas y las reintenta, de modo que la demostración no se pierde.

---

*Documento de trabajo. Las pruebas del apartado 3 se ejecutaron contra el servicio local
en modo de demostración y quedan registradas en la bitácora del 22 de septiembre.*
