# 📓 Bitácora — Sesión del martes 29 de septiembre de 2026

**Proyecto:** SIGVACH — Sistema de Gestión de Variables para Cultivos Hidropónicos
**Grupo:** 3 · **Entrega E3:** sábado 3/10 a las 23:59 · **Defensa:** martes 13/10 a las 17:00
**Objetivo de la sesión:** soldar la resistencia de *pull-up* del AM2302, devolver el sensor
al módulo y comprobar por el puerto serie que el módulo vuelve a publicar las cinco variables.

---

## 1. Punto de partida

| Pieza | Estado al comenzar |
|---|---|
| Módulo de adquisición | **Apagado desde el 27/09 a las 23:58**, última lectura publicada |
| AM2302 (temperatura y humedad del ambiente) | Conectado, pero sin resistencia de *pull-up*: el firmware avisaba `problem in phase 'B'` |
| Variables publicadas por ciclo | 5 (ambiente, humedad, temperatura de la solución, TDS, conductividad) |
| Electrodo de pH | En remojo desde el lunes 28/09 a las 19:52, en disolución patrón de pH 4,01 |
| Cinta aislante | Única opción disponible: no hay termorretráctil en el taller |

El error `problem in phase 'B'` significa que la línea de datos se quedó en alto: el sensor no
está en ese pin, no está alimentado, o la línea no tiene a quién subir. El AM2302 no trae la
resistencia puesta, así que hay que soldarla entre el cable de alimentación y el de datos.

---

## 2. La resistencia de *pull-up*: qué es y por qué va ahí

El AM2302 habla por un solo hilo y no empuja la línea hacia arriba: solo la baja. Si nadie la
sube, el microcontrolador lee un valor indefinido. La resistencia de 4,7 kΩ hace ese trabajo:
mantiene la línea en 3,3 V cuando nadie habla.

| Cable del sensor | Pin de la placa | Papel |
|---|---|---|
| Rojo | `3,3V` | Alimentación |
| **Amarillo** | **`P33` · GPIO 33** | **Datos** |
| Negro | `GND` | Masa |

La resistencia va **entre el rojo y el amarillo**, y los dos cables quedan **enteros**: es un
puente en paralelo, no un empalme en serie. Si se cortara el cable para intercalarla, el sensor
quedaría desconectado.

El valor está dentro de lo que pide la hoja de datos (4,7 kΩ a 10 kΩ). Se eligió 4,7 kΩ porque
es el que había y deja la línea más firme. Los tres resistores del taller se midieron entre
4,6 kΩ y 4,8 kΩ: los cuatro son de 4,7 kΩ (amarillo, violeta, rojo).

---

## 3. Cómo se soldó

El colocado se hizo siguiendo la guía `25_GUIA_DE_SOLDADURA_DEL_AM2302.md` y su lámina de
cuatro pasos (`Figuras/22-soldadura-del-pullup.png`):

1. Una ventana de 3 mm pelada en el rojo y otra en el amarillo, sin cortar el cobre y a
   distinta altura, para que las dos uniones no queden enfrentadas.
2. Estañado de la ventana y de la pata por separado.
3. Pata enrollada media vuelta sobre la ventana antes de soldar: eso es lo que aguanta los
   tirones.
4. Pata sobrante recortada y doblada contra el cable, y cada unión cubierta con cinta aislante
   de PVC, **una tira por unión**, para que las dos patas no queden apretadas una contra otra.

**Antes de conectar a la placa** se midió con el multímetro:

| Medición | Resultado esperado | Resultado obtenido |
|---|---|---|
| Punta libre del amarillo contra la del rojo | 4 600 a 4 800 Ω | **4,7 kΩ** |
| Punta libre del rojo contra la del negro | Distinto de 0 Ω | Sin continuidad |
| Tirón suave de cada pata | La unión resiste | Resiste |

Se comparó antes con una foto de referencia de internet que mostraba el estaño pegado sobre el
aislante derretido, con las patas sin enrollar: las dos uniones quedaron brillantes y lisas, y
por eso se decidió que el trabajo estaba bien hecho. El termorretráctil se reemplazó por cinta
aislante, y queda anotado revisarla antes de la demostración, porque la cinta cede con el calor.

---

## 4. Verificación en el módulo: el AM2302 ya responde

Con la placa conectada por USB y el módulo encendido, se escuchó el puerto `COM6` a 115 200
baudios. En el primer ciclo después del arranque llegaron estas líneas:

| Marca de tiempo | Variable | Valor | Estado |
|---|---|---|---|
| 43,7 s | **humedad** | **43,80 %** | almacenada |
| 47,6 s | temperatura de la solución | 23,31 °C | almacenada |
| 50,9 s | TDS | 262,31 ppm | almacenada |
| 54,9 s | conductividad eléctrica | 0,52 mS/cm | almacenada |

**La humedad es la prueba**: ese valor solo puede venir del AM2302, porque es el único sensor de
humedad del montaje. El error `problem in phase 'B'` no volvió a aparecer. La soldadura quedó
bien y el sensor está funcionando.

Los cuatro valores van separados por unos 4 segundos: es el tiempo de asentamiento del
convertidor analógico a digital (`ASENTAMIENTO_ADC_MS 4000`) antes de cada lectura de las sondas.

En un escucha posterior se capturó un **ciclo completo**, ya con el módulo en régimen normal y
las cinco variables juntas. La captura literal quedó como evidencia en
`hardware/evidencias/ciclo-completo-2026-09-29.txt`:

| Variable | Valor | Origen |
|---|---|---|
| temperatura ambiental | 25,20 °C | AM2302 (GPIO 33) |
| humedad | 49,20 % | AM2302 (GPIO 33) |
| temperatura de la solución | 22,31 °C | DS18B20 (GPIO 32) |
| TDS | 267,87 ppm | sonda TDS (SVN · GPIO 39) |
| conductividad eléctrica | 0,54 mS/cm | calculada del TDS |

Las dos primeras son del mismo sensor, así que **el AM2302 entrega las dos magnitudes**: la
temperatura del ambiente y la humedad. Cada línea termina en `almacenada` y va precedida por
`esp-x509-crt-bundle: Certificate validated`, que es la validación del certificado del servicio
publicado: las cinco variables no solo se leyeron, **llegaron al servidor**.

Dos observaciones del ciclo, que quedan anotadas:

- **El pH se lee estable**: 142 mV crudos, con dispersión 0 y la señal marcada como estable. El
  electrodo lleva desde el lunes en la disolución patrón de pH 4,01. El valor no se publica
  todavía: falta la conversión y la calibración con los tres patrones.
- **El TDS sale algo ruidoso**: 683 mV crudos con dispersión de 659, y el firmware lo marca como
  `algo ruidosa`. El valor publicado es coherente con el ciclo anterior (268,94 ppm), pero
  conviene revisar el filtrado y la puesta a masa cuando la sonda se monte en la maqueta, porque
  todavía está sobre la mesa y sin apantallar.

Los valores de cada ciclo van separados por unos 4 segundos: es el tiempo de asentamiento del
convertidor analógico a digital (`ASENTAMIENTO_ADC_MS 4000`) antes de cada lectura de las sondas.
Y entre ciclo y ciclo el módulo queda callado los 300 segundos completos: en modo servicio solo
imprime cuando lee, de modo que una escucha de menos de cinco minutos puede no capturar nada.

---

## 5. Dos problemas del monitor serie, y cómo se resolvieron

El monitor serie no se pudo leer de buenas a primeras. Aparecieron dos estorbos distintos, y
conviene tenerlos anotados porque van a volver a aparecer en la demostración:

### 5.1 El módulo imprime una línea de depuración del WiFi a chorro

Miles de veces por segundo aparece:

```
ssn:5, winSize:64
```

No es un error del módulo: es una traza de depuración del WiFi que quedó activada en la
configuración y tapa las líneas útiles. Se resolvió en el lector, con un filtro que la descarta
y que al final informa cuántas líneas descartó, para no perder la cuenta.

### 5.2 El puerto se atascó y devolvió el mismo fragmento a velocidad imposible

En una de las escuchas el lector informó **2 136 055 repeticiones de la línea `cenada` en 120
segundos**. Eso son 17 800 líneas por segundo, y a 115 200 baudios el cable no puede pasar más
de unos 11 500 caracteres por segundo. **El dato era imposible**: no venía del módulo, era un
resto del buffer del puerto que se repetía.

El riesgo no es el ruido, es creerle: un registro así parece una prueba y no lo es. Se agregó al
lector un control de ritmo que compara los caracteres recibidos por segundo contra el techo
físico del cable; si lo supera, detiene el escucha, avisa y termina con código de error. Las
líneas idénticas y consecutivas también se cuentan y se informan una sola vez.

**Lección:** antes de dar por buena una captura, comparar lo recibido con lo que el cable puede
llevar. Un registro imposible se detecta con una división.

---

## 6. Cómo se ven las lecturas, y por qué el panel no es instantáneo

| Vía | Qué muestra | Cada cuánto cambia |
|---|---|---|
| **Monitor serie** (`Modulo ESP32/Diagnostico/leer_serial.ps1`) | Las cinco variables, en el instante en que el módulo las lee | Al instante, y un ciclo completo cada 5 minutos |
| **Panel de la aplicación** (web publicada o Android) | Las variables del módulo y su estado | Se actualiza al deslizar hacia abajo, y solo cambia cuando el módulo publica: cada 5 minutos |
| **Consola de Firestore** (`lecturas`) | Los documentos crudos, con marca de tiempo | Al instante en que el módulo publica |
| **API** (`GET /api/v1/lecturas?limite=5` con token) | El JSON crudo | Igual que Firestore |

El límite no está en la aplicación sino en el módulo: `SEGUNDOS_ENTRE_LECTURAS` está en 300
segundos en modo servicio. Para la demostración se puede bajar a 60 segundos y volver a grabar,
de modo que el panel cambie mientras el docente mira. El costo en Firestore sigue siendo bajo:
con 5 minutos son 1 440 escrituras por día (7,2 % del plan gratuito); con 1 minuto serían 7 200
(36 %), aceptable por un día de demostración y no para dejarlo permanente.

---

## 7. Pendiente para la próxima sesión

| Pendiente | Detalle |
|---|---|
| Filtrado de la sonda TDS | Sale marcada como `algo ruidosa` (dispersión de 659 sobre 683 mV): revisar filtrado y puesta a masa al montarla en la maqueta |
| Divisor de tensión del pH | Armar la mitad del divisor (dos resistencias de 4,7 kΩ) antes del miércoles |
| Revisión del remojo del electrodo | A las 24 horas del lunes 19:52, y decisión a las 48 horas: recuperar o comprar |
| Termorretráctil | Comprar en una tienda de eléctricos y reemplazar la cinta aislante de las uniones |
| Entrega E3 | Apartados 2.1, 2.7 y 2.8, informe de pruebas y correcciones pendientes |

---

## 8. La tutoría del martes 29

### 8.1 Cómo salió

La sesión fue **corta**: alcanzó para mostrar el sistema funcionando y para consultar algunas cosas,
pero **no hubo tiempo para las observaciones pendientes**. El docente indicó que el trabajo está
bien y no planteó dudas nuevas.

### 8.2 Lo que preguntó el docente

> «¿Cómo está conectado el módulo ESP32 con Firestore?»

La respuesta que se le dio: **a través del servicio**. Conviene dejarla escrita con precisión,
porque es la respuesta que sostiene el diseño de seguridad del proyecto:

| Quién | Qué hace | Qué credenciales tiene |
|---|---|---|
| El módulo ESP32 | Publica las lecturas por HTTPS al servicio | Su clave de dispositivo, y nada más |
| El servicio | Valida el dato, autoriza y **escribe** en Firestore | Credenciales de servicio de Firebase |
| La aplicación | Lee y escribe **a través del servicio** | El token de identidad del usuario |
| Firestore | Guarda los datos | Reglas de seguridad que cierran el acceso directo |

**El módulo no conoce la base ni tiene credenciales de ella.** Ese es el punto: si alguien captura la
clave del dispositivo, no puede leer ni borrar la base, solo publicar lecturas.

### 8.3 Lo que quedó sin responder, y cómo se recupera

Las cuatro consultas que bloqueaban el trabajo quedaron **sin respuesta**: las observaciones
**A-11 y A-12**, el cierre de la **A-4** y el **número de detecciones tardías** del ensayo previo.

Como la próxima tutoría puede volver a quedarse corta, se pasa la consulta **por escrito**, en un
solo mensaje al docente, con las cuatro preguntas numeradas. Lo que se pide:

1. Qué pedían las observaciones **A-11 y A-12** de la bitácora del 22 de septiembre.
2. Si la **A-4** queda cerrada con la maqueta y el nombre del módulo piloto.
3. El **número de detecciones tardías** del ensayo previo.
4. **Día y hora de la próxima tutoría**, y si hay alguna fecha antes del sábado.

Además conviene **revisar el documento devuelto del T3**: si las observaciones A-11 y A-12 quedaron
como comentarios en el archivo, están ahí y no hace falta esperar la respuesta.

> **Lo que sí quedó claro:** el docente mira el flujo del dato, no la electrónica. La pregunta fue
> por el camino entre el módulo y la base. Por eso el apartado **2.7 (Seguridad)** y el guion de la
> demostración tienen que explicar ese camino con este mismo cuadro.

---

## 9. El trabajo de la noche: los tres pendientes del E3 resueltos

Después de la tutoría se leyó la plenaria **P4** (la última del módulo) y se trabajó sobre lo que
pide. Quedaron hechos tres de los pendientes, con su evidencia.

### 9.1 La plenaria P4: lo que pide y lo que faltaba

El documento `P4_Pruebas_Despliegue_Defensa_Modulo4.pdf` se guardó en `docs/plenarias/`, y sus
requisitos quedaron extraídos y cotejados con el estado del proyecto en
`docs/27_LO_QUE_PIDE_LA_PLENARIA_P4.md`. Lo que apareció y no teníamos anotado:

| Requisito de la plenaria | Estado al leerlo |
|---|---|
| Una cuenta `@proyecto.test` por rol, con contraseña de 10 o más caracteres | ✗ Se usaban correos personales con contraseñas de 6 |
| Que la aplicación vuelva al inicio de sesión cuando el token vence | ✗ Estaba declarado en el código y nunca se usaba |
| Nivel de rendimiento: una medición del RNF sobre la URL pública | ✗ Por hacer |
| Nivel funcional: el flujo Must con capturas fechadas en producción | ✗ Por hacer |
| Informes de los ejecutores de prueba versionados en el repositorio | ✗ Por hacer |

También quedó anotado el calendario nuevo: la **T4 del Grupo 3 es el viernes 9 de octubre a las
17:00**, con el ensayo de la defensa, y la defensa es del 12 al 15 de octubre, siete minutos de
demostración y cinco de preguntas.

### 9.2 El 401 devuelve al inicio de sesión

Era la **pregunta 2 de la defensa** («¿qué pasa si el token vence?») y estaba sin resolver: la API
respondía 401 correctamente, pero la aplicación se quedaba en la pantalla mostrando un error.

| Archivo | Cambio |
|---|---|
| `lib/services/api_cliente.dart` | Cuando el servicio responde 401, avisa en lugar de sólo lanzar el error |
| `lib/services/auth_service.dart` | Cierra la sesión y guarda el motivo |
| `lib/main.dart` | Conecta el aviso con el cierre de sesión |
| `lib/screens/login_screen.dart` | Muestra «Tu sesión venció. Volvé a iniciar sesión.» |

**La decisión que conviene saber explicar:** sólo el 401 del **servidor** cierra la sesión, no la
falta de token en el equipo. Al arrancar, el proveedor de identidad tarda unos milisegundos en
restaurar la sesión; si una pantalla pidiera datos en ese instante, cerrar la sesión dejaría al
usuario afuera sin motivo. Quedó escrito en el propio código, y hay una prueba que lo comprueba.

### 9.3 Las dos cuentas de prueba, una por rol

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | `administrador@proyecto.test` | `SIGVACH.Adm.2026` |
| Operador | `operador@proyecto.test` | `SIGVACH.Ope.2026` |

Se crearon en Firebase Authentication, se les creó el perfil con el **rol de menor privilegio** y el
ascenso del administrador se hizo **por el servicio**, que es la vía correcta. Las credenciales
quedaron en el README y en el campo de texto de la entrega, nunca en el documento. Las dos cuentas
anteriores, con correos reales y contraseñas cortas, quedaron fuera de circulación.

La comprobación contra el servicio publicado, en `evidencia/cuentas-de-prueba-2026-09-29.txt`:

| Caso | Petición | Respuesta |
|---|---|---|
| 1 | `GET /usuarios` sin token | **401** |
| 2 | `GET /usuarios` con el operador | **403**, con `rol_requerido` y `rol_actual` |
| 3 | `GET /lecturas` con el mismo operador | **200** |
| 4 | `GET /usuarios` con el administrador | **200** |

El caso 3 es el que importa para la defensa: demuestra que el 403 no es un bloqueo de la cuenta,
sino de la operación.

### 9.4 Se cerró una escalada de privilegios

Al revisar cómo se asigna el rol apareció esto: **el rol de administrador se concedía por correo**.
El alta de un perfil admitía `rol: administrador` para `admin@sigvach.com`, en la aplicación y en
las reglas de la base. Cualquiera que consiguiera registrarse con ese correo obtenía las
atribuciones sin que nadie se las diera, lo que contradice el principio de menor privilegio que
exige la plenaria.

Se retiró la excepción en los dos lugares, se actualizaron los documentos que la describían y se
publicaron las reglas con `firebase deploy --only firestore:rules`. Las reglas publicadas se
compararon después contra el archivo del repositorio: **el contenido coincide, carácter por
carácter**.

Y se probó el efecto, no sólo la publicación: con el token de la cuenta de operador se intentó
cambiar el rol propio a administrador contra la API de Firestore.

```
Petición  : PATCH usuarios/<uid propio>  con  rol = administrador
Respuesta : HTTP 403
            {"error":{"code":403,"message":"Missing or insufficient permissions.",
                      "status":"PERMISSION_DENIED"}}
```

Es la respuesta que hay que saber dar en la defensa: **el rol no se concede desde el cliente; ni
siquiera la base lo permite**.

### 9.5 La aplicación publicada, actualizada

Se volvió a compilar con la dirección del servicio publicado (`flutter build web` con
`--dart-define=API_BASE_URL=https://sigvach-api.onrender.com`) y se desplegó a Firebase Hosting. La
verificación posterior comprobó las cuatro cosas: que el paquete publicado pide los datos al
servicio publicado, que coincide con la compilación local, que la ruta de salud responde
`{"estado":"ok","base_de_datos":"conectada"}` y que el origen está autorizado (CORS y examen
previo correctos).

### 9.6 Las pruebas, con su informe versionado

| Batería | Comando | Resultado |
|---|---|---|
| Servicio | `pytest backend -q --no-header -p no:cacheprovider` | **106 pruebas, 0 fallos** (7,24 s) |
| Aplicación | `flutter test` | **96 pruebas en verde** (eran 93: se agregaron 3 del cierre de sesión) |
| Análisis estático | `flutter analyze` | Sin observaciones |

**Total: 202 pruebas automatizadas.** Los informes quedaron en `evidencia/` con la fecha en el
nombre, y el del servicio también en formato JUnit (`.xml`), para poder leer los números sin abrir
el texto. El README decía 90 casos y no mencionaba `flutter test`: quedó corregido.

### 9.7 Lo que quedó guardado, y las confirmaciones del día

| Pieza | Dónde |
|---|---|
| Informe del servicio y de la aplicación | `evidencia/pytest-2026-09-29.txt` y `.xml`, `evidencia/flutter-test-2026-09-29.txt` |
| Análisis estático | `evidencia/flutter-analyze-2026-09-29.txt` |
| Las dos cuentas y el control de rol | `evidencia/cuentas-de-prueba-2026-09-29.txt` |
| Reglas de la base y escalada cerrada | `evidencia/reglas-firestore-2026-09-29.txt` |
| Verificación del despliegue web | `evidencia/despliegue-web-2026-09-29.txt` |
| Requisitos de la plenaria P4 | `docs/27_LO_QUE_PIDE_LA_PLENARIA_P4.md` |
| La plenaria, archivada | `docs/plenarias/P4_Pruebas_Despliegue_Defensa_Modulo4.pdf` |

Confirmaciones del día, en orden: `7c1f510` (pull-up del AM2302 y ciclo completo), `0a20ffa` y
`d63fd59` (diagramas del divisor), `b8171b0` (aclaración del lado del divisor), `aa64057` (guía
simple), `ff009ce` y `75e55a3` (patrón del TDS y cotización de Hanna), `6eda3d1` (la tutoría en la
bitácora), `bad6ef5` (requisitos de la P4), `4bf4991` (arreglo del 401 con los informes),
`deeda2b` (cuentas de prueba) y `d14aa39` (escalada de privilegios cerrada).

### 9.8 Lo que sigue

| Pendiente | Cuándo |
|---|---|
| **La prueba de los dos patrones del electrodo de pH** | miércoles 30 a las 19:52, y es lo del banco |
| El divisor ÷2 del pH, con las dos resistencias de 4,7 kΩ | miércoles, con la prueba |
| El mapa del repositorio para la defensa (dónde está cada cosa que pueden preguntar) | antes del 9 de octubre |
| La tabla 2.8 con sus casos, y las capturas fechadas del flujo completo | para el E3 del sábado 3 |
| La medición de rendimiento sobre la URL pública | para el E3 |
| Escribir los apartados 2.1, 2.7 y 2.8 | para el E3 |


