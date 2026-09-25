# Firmware del módulo de adquisición — guía paso a paso (ESP-IDF)

**Proyecto:** SI.G.VA.C.H. · **Módulo:** ESP32 con sensores de temperatura, humedad
y sólidos disueltos (el pH se suma cuando el electrodo esté recuperado)

**Versión del firmware:** ESP-IDF v5.5.3 · **Placa:** ESP32 de 38 pines sobre placa
de expansión · **Puerto:** COM6

> **Esta es la versión ESP-IDF del firmware.** Sustituye a la versión de Arduino
> (`firmware/sigvach_esp32/`), que se conserva como referencia. Las diferencias
> que importan están explicadas en el apartado 8.

---

## 1. Qué hace el programa

Cada **5 minutos** (tiempo configurable):

1. Lee los sensores del módulo.
2. Publica cada variable en el servicio por HTTPS, con la clave del dispositivo.
3. Si el servicio no responde —arranque en frío, corte de red o servicio caído—,
   **guarda las lecturas en memoria NO VOLÁTIL y las reintenta**, con la hora en
   que se midieron.

Se puede probar **sin WiFi y sin servicio**: con el modo de prueba solo informa
por el Monitor Serie.

### Estado verificado de los sensores

Los cuatro sensores del montaje actual están **verificados con ensayos propios**:

| Variable | Sensor | Verificación realizada |
|---|---|---|
| `temp_ambiental` | AM2302 / DHT22 | Responde en P33 desde el primer intento |
| `humedad` | AM2302 / DHT22 | Idem |
| `temp_solucion` | DS18B20 | **Contrastado contra el AM2302: coinciden en 0,01 °C** |
| `tds` | TDS Meter V1.0 | **Prueba de la sal: 155 mV → 2 415 mV** |
| `ec` | derivada del TDS | `ppm ÷ 500` |
| `ph` | PH-4502C | Pendiente: electrodo en recuperación |

---

## 2. Materiales

| Pieza | Estado |
|---|---|
| ESP32 de 38 pines + placa de expansión | ✅ |
| AM2302 (el de cable) | ✅ **verificado en P33** |
| DS18B20 sumergible | ✅ **verificado en P32** |
| TDS Meter V1.0 + sonda | ✅ **verificado en SVN** |
| PH-4502C + electrodo BNC | ⏸️ electrodo en recuperación (24–48 h en KCl) |
| Sonda NTC de suelo (Thermoreg) | ⏸️ fuera: mide sustrato, que no es una variable |
| Protoboard, cables dupont, multímetro | ✅ |
| **Resistencia de 4,7 kΩ** | ⚠️ **necesaria para el DS18B20** (véase 3.3) |
| Resistencias de 10 kΩ (×2) | Para el divisor del pH (cuando llegue el electrodo) |
| Depósito con tapa · solución nutritiva A/B/C | ❌ Falta |
| Solución de conservación (KCl) y patrones de pH | ❌ Falta |

---

## 3. Conexionado

### 3.1 Alimentación y señales

| Sensor | Terminal | Pin de la placa | Tensión |
|---|---|---|---|
| **AM2302** | rojo · VDD | `3,3V` | 3,3 V |
| | amarillo · datos | **`P33`** (GPIO 33) | 3,3 V |
| | negro · GND | `GND` | — |
| **DS18B20** | rojo · VDD | `3,3V` | 3,3 V |
| | amarillo · datos | **`P32`** (GPIO 32) **+ 4,7 kΩ a 3,3 V** | 3,3 V |
| | negro · GND | `GND` | — |
| **TDS V1.0** | `AOUT` | **`SVN`** (GPIO 39) — directo | ≤ 2,3 V |
| | `VCC` / `GND` | `5V` / `GND` | **5 V** |
| **PH-4502C** *(pendiente)* | `Po` | `SVP` (GPIO 36) — **con divisor ÷2** | 5 V → 2,5 V |
| | `V+` / `G` | `5V` / `GND` | 5 V |

**Masa común obligatoria:** todos los `GND` van al mismo punto. Sin eso, las
lecturas analógicas son inutilizables.

### 3.2 Ubicación de los pines en la placa de expansión

En la columna que rotula `5V · CMD · SD3 · SD2 · P13 · GND · P12 · P14 · P27 ·
P26 · P25 · P33 · P32 · P35 · P34 · SVN · SVP · EN · 3V3`, el orden de abajo
hacia arriba es:

```
        3V3     ← extremo de abajo
        EN
        SVP     ← pH            (GPIO 36)
        SVN     ← TDS           (GPIO 39)
        P34
        P35
        P32     ← DS18B20       (GPIO 32)
        P33     ← AM2302        (GPIO 33)
        P25
        P26
```

> 🛑 **NUNCA conectar nada a `CMD`, `SD2` ni `SD3`:** son los pines de la
> **memoria flash interna** y conectarlos cuelga el arranque del chip.

### 3.3 Las resistencias de pull-up: lo que se aprendió midiendo

Este es el punto donde la teoría y el montaje real se separaron, y conviene
dejarlo anotado tal como se comprobó:

| Sensor | ¿Necesita la resistencia externa? |
|---|---|
| **AM2302** | **No, en este montaje.** Funciona con el pull-up interno del ESP32 (~45 kΩ). Comprobado con el sensor midiendo de forma estable |
| **DS18B20** | **Sí, es obligatoria.** Sin ella el bus OneWire no responde: `1-wire reset pulse receive timeout` |

**Por qué la diferencia.** El AM2302 usa un protocolo de un solo pulso de
respuesta, tolerante a tiempos largos. El DS18B20 se implementa con el
periférico **RMT**, que mide en microsegundos: con 45 kΩ la línea tarda
demasiado en volver a alto y el periférico da timeout. La documentación del
componente de Espressif lo advierte: *"the internal pull-up resistor cannot
provide enough current for some devices"*.

**Si no hay de 4,7 kΩ, una de 10 kΩ sirve** para el cable propio del sensor.

### 3.4 El divisor del pH (÷2)

El pH es la única señal que necesita divisor: la salida `Po` del PH-4502C llega
a unos 5 V y el ESP32 tolera 3,3 V.

```
   Po (PH-4502C) ──[ 10 kΩ ]──┬── SVP (GPIO 36)
                              │
                          [ 10 kΩ ]
                              │
                             GND
```

El firmware informa la tensión **tal como llega al pin**, es decir ya dividida:
en el patrón de pH 7 se leerá alrededor de 1,25 V, no 2,5 V.

### 3.5 Antes de conectar: medir con el multímetro

Con la placa alimentada por USB y **sin sensores conectados**:

1. `3,3V` contra `GND` → deben ser **3,3 V**.
2. `5V` contra `GND` → deben ser **5 V**.
3. Si no coincide, revisar el **puente 3,3 V / 5 V** (el jumper amarillo de la placa).

### 3.6 Orden de montaje: de a uno por vez

| Paso | Qué se conecta | Cómo se verifica | Si falla |
|---|---|---|---|
| **1** | Nada. Solo la placa por USB | Multímetro: 3,3 V y 5 V | Revisar el puente de la placa |
| **2** | El riel de masa al protoboard | Continuidad entre los extremos | — |
| **3** | **AM2302** (rojo → 3,3 V, amarillo → `P33`, negro → GND) | `Sensor de ambiente: AM2302 / DHT22 en GPIO 33` | Revisar alimentación y orden de hilos |
| **4** | **DS18B20** (rojo → 3,3 V, amarillo → `P32` **+ 4,7 kΩ**, negro → GND) | `DS18B20 en uso: ROM ...` y temperatura creíble | `reset pulse receive timeout` → falta la resistencia |
| **5** | **TDS V1.0** (VCC → 5 V, GND → GND, AOUT → `SVN`) | Voltaje estable; **sube al agregar sal** | Voltaje fijo → sonda seca o sin alimentar |
| **6** | **PH-4502C con su divisor** *(cuando lleguen los patrones)* | El voltaje **cambia** al pasar de un patrón a otro | Sin reacción → electrodo deshidratado |
| **7** | Nada nuevo: se pone `PUBLICAR_EN_SERVICIO` en 1 | `... -> almacenada` y las variables en la app | 401 → clave; 404 → módulo; 422 → unidad |

> 🔎 **Con el paso 5 ya se puede publicar.** El módulo mide cuatro variables
> **sin necesitar ninguna solución de calibración**.

---

## 4. Poner en marcha el programa

### Paso 1 — El entorno ya está instalado

ESP-IDF está en `C:\esp-idf-v5.5.3\Espressif\frameworks\esp-idf-v5.5.3`, con el
toolchain `xtensa-esp32-elf` y `idf.py` funcionando. **No hay que instalar nada.**

### Paso 2 — Activar el entorno

Cada vez que se abra una terminal nueva, hay que activar el entorno. Para eso
está el archivo `entorno_idf.ps1`:

```powershell
cd "D:\SIGVACH-Monograf\Prototipo ESP32\firmware\sigvach_idf"
. .\entorno_idf.ps1
```

> **El punto del principio es obligatorio.** Sin él, el script se ejecuta en un
> proceso aparte y las variables se pierden al terminar la línea.

### Paso 3 — Crear el archivo de datos privados

1. En `main/`, copiar `configuracion.ejemplo.h` con el nombre **`configuracion.h`**.
2. Completar:
   - `NOMBRE_WIFI` y `CLAVE_WIFI` → la red **(de 2,4 GHz)**
   - `CLAVE_DISPOSITIVO` → del `.env` del proyecto (`DEVICE_API_KEY`)
   - `MODULO_ID` → el módulo de la maqueta: `v6wrYSXxeHyttf3prDd7`
   - `PUBLICAR_EN_SERVICIO` → `0` para probar sin publicar, `1` para publicar

> 🔒 **Este archivo no se comparte ni se sube al repositorio.** El `.gitignore`
> de la carpeta lo excluye —incluidas las variantes de respaldo
> (`configuracion.h.bueno`, `.respaldo`, `.old`), que también llevan los secretos.

### Paso 4 — Compilar y cargar

```powershell
idf.py build                 # compila
idf.py -p COM6 flash         # carga en la placa
idf.py -p COM6 monitor       # Monitor Serie (salir: Ctrl+])
```

Para salir del monitor: **Ctrl + ]**

---

## 5. Las pruebas, en orden

| Prueba | Configuración | Qué se espera ver |
|---|---|---|
| **1. Conexionado** | `PUBLICAR_EN_SERVICIO = 0` | El barrido de entradas y las cuatro lecturas por el Monitor Serie |
| **2. Publicación** | `PUBLICAR_EN_SERVICIO = 1` con el WiFi cargado | `... -> almacenada` en las cinco variables |
| **3. Cola de pendientes** | Apuntar `HOST_API` a una dirección inválida | `guardada en memoria no volatil (quedan N)`; al restaurar, `recuperada: ...` |
| **4. pH** | Calibrar el electrodo | La sexta variable se publica |

### Cómo reconocer que cada sensor responde

| Sensor | Señal de que funciona |
|---|---|
| AM2302 | Temperatura y humedad con valores razonables (15–30 °C, 30–80 %) |
| DS18B20 | `DS18B20 en uso: ROM ...` con una dirección y temperatura creíble |
| TDS | Voltaje **estable** entre 0,1 y 2,3 V que **sube** al agregar sal |
| pH | Voltaje que **cambia** al pasar el electrodo de un patrón a otro |

---

## 6. Las herramientas de diagnóstico del firmware

El firmware trae dos herramientas pensadas para no perder tiempo con el
conexionado. **Conviene conocerlas antes de tocar un cable.**

### 6.1 Barrido de pines del sensor de ambiente

Si el AM2302 no responde en `P33`, el programa **prueba solo los demás pines**
de la placa y dice en cuál está:

```
SENSORES: Buscando el sensor de ambiente (primero en P33)...
SENSORES:   GPIO 33: sin respuesta
SENSORES:   GPIO 32: sin respuesta
SENSORES: ENCONTRADO: AM2302 / DHT22 en GPIO 13 (NO en el P33 del manual)
```

**Por qué existe.** En el montaje real el sensor apareció en `P13` en vez de
`P33`. Ese barrido resolvió en 18 segundos una duda que a mano lleva media hora
de prueba y error.

### 6.2 Medición de dispersión: señal real o ruido

Una entrada al aire puede entregar **cualquier** tensión, pero **salta mucho**
entre muestras. El firmware mide esa dispersión y dice cuál es cuál:

```
PIN           PREVISTO        MEDIANA DISPERSION  ESTADO
SVP GPIO 36   pH               142 mV          0  senal estable
SVN GPIO 39   TDS             2415 mV         31  senal estable
P34 GPIO 34   alternativa      142 mV         12  senal estable
```

| Dispersión | Significado |
|---|---|
| Menos de 40 | Señal estable |
| 40 a 150 | Algo ruidosa |
| **Más de 150** | **Nada conectado (pin flotando)** |

Un sensor conectado da dispersión de **decenas**; un pin al aire, de **cientos o
miles**. Fue lo que permitió demostrar que el TDS estaba midiendo y que el pH
todavía no.

> 💡 **`142 mV` es el cero del instrumento, no un error.** Con la calibración de
> fábrica, `crudo 0` equivale a 142 mV. Un pin desconectado y ya asentado se
> descarga a 0 cuentas, así que **`142 mV` significa "no hay nada conectado"**.

---

## 7. Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `1-wire reset pulse receive timeout` | **Falta la resistencia de 4,7 kΩ** del DS18B20 | Colocarla entre datos y 3,3 V |
| `NO se encontro ningun DS18B20 en P32` | Hilos invertidos o placa mal asentada | Revisar orden: rojo 3,3 V, amarillo datos, negro GND |
| `Sensores DS18B20 encontrados: 0` | Idem | Idem |
| Temperatura y humedad en `nan` | El AM2302 no responde | Alimentación a 3,3 V, datos en `P33`, masa común |
| **`422` al publicar** | **La unidad no coincide con el catálogo del servicio** | Ver el aviso del apartado 8.4: las temperaturas van en **`"°C"`**, no `"C"` |
| `401` | Clave del dispositivo distinta de la del servicio | Copiar de nuevo `DEVICE_API_KEY` del `.env` |
| `404` | El identificador del módulo no existe | Listar los módulos y corregir `MODULO_ID` |
| `sin respuesta del servicio` | Servicio arrancando en frío | Esperar: la lectura queda en memoria no volátil y se reintenta |
| El WiFi no conecta | La red es de 5 GHz | Usar la red de **2,4 GHz** |
| Lecturas de pH o TDS saltan mucho | Entrada al aire | Consultar la dispersión (apartado 6.2) |

---

## 8. Lo que cambia respecto de la versión de Arduino

Esta sección existe porque las siete trampas que siguen **costaron tiempo real**
y no son evidentes. Están ordenadas por lo que más desconcierta.

### 8.1 El ADC necesita asentarse varios segundos

**El ADC del ESP32 no queda listo al inicializarlo.** Durante los primeros
segundos informa `142 mV` con dispersión cero en **todos** los canales — un
valor que parece una señal limpia y no lo es.

Está medido: **a 1 s las lecturas son falsas; a 5 s ya son reales.** Por eso el
firmware espera 4 segundos (`ASENTAMIENTO_ADC_MS`) después de inicializar.

**Sin esa espera, la primera lectura que el módulo publiques después de
encenderse sería falsa.** Es un error que no se nota: el dato entra en la base
con aspecto perfectamente normal.

### 8.2 El ESP32 clásico solo admite un esquema de calibración

El esquema de **ajuste de curva** (`adc_cali_curve_fitting`) **no compila** en el
ESP32: solo existe en los S2, S3 y C3. En este chip hay que usar el de **ajuste
de recta** (`adc_cali_line_fitting`).

Además, el manejador de calibración **depende de la atenuación, no del canal**:
uno solo sirve para todos los canales. Y el ESP32 tiene un campo extra,
`default_vref` (1100 mV), que solo aplica a este chip.

### 8.3 No declarar `REQUIRES` en el componente `main`

El componente `main` recibe automáticamente **todos** los demás componentes. Si
se declara `REQUIRES` o `PRIV_REQUIRES`, ESP-IDF **deja de agregar los
requisitos comunes** y el programa falla con:

```
fatal error: esp_event.h: No such file or directory
```

Los componentes externos (`dht`, `ds18b20`) se declaran en `main/idf_component.yml`,
**no** en `CMakeLists.txt`.

### 8.4 Las unidades deben coincidir EXACTAMENTE con el catálogo del servicio

El servicio valida la unidad y responde **422** si no coincide, con el mensaje
*"valor fuera de rango o variable desconocida"* — que induce a pensar que el
**valor** está mal, cuando el problema es la **unidad**.

El catálogo vive en `backend/app/esquemas.py` (`CATALOGO_VARIABLES`):

| Variable | Unidad |
|---|---|
| `temp_solucion`, `temp_ambiental` | **`"°C"`** ← con el símbolo de grado, **no** `"C"` |
| `tds` | `"ppm"` |
| `ec` | `"mS/cm"` |
| `humedad` | `"%"` |
| `ph` | `""` (vacía) |

### 8.5 El driver `dht` NO configura el pull-up

El driver de esp-idf-lib usa la línea como **salida de drenador abierto** y como
entrada, pero **no activa ningún pull-up**. Si no se hace a mano, el sensor deja
de funcionar aunque el cableado sea correcto:

```c
gpio_set_pull_mode(PIN_AMBIENTE, GPIO_PULLUP_ONLY);
```

La biblioteca `DHT` de Arduino lo hacía sola; en ESP-IDF hay que hacerlo
explícitamente.

### 8.6 Al reemplazar un archivo de encabezado, forzar la recompilación

**`Copy-Item` conserva la fecha de modificación del archivo original.** Si al
restaurar un respaldo de `configuracion.h` la fecha queda **más vieja** que el
objeto compilado, el sistema de compilación cree que nada cambió y **no
recompila**: el `build OK` es engañoso y el firmware cargado sigue teniendo la
configuración anterior.

```powershell
(Get-Item $cfg).LastWriteTime = Get-Date   # antes de compilar
```

**Cómo detectarlo:** mirar si el registro del `build` menciona `main.c.obj`.
Si no lo menciona, **no se recompiló**.

### 8.7 El formateo de decimales: evitar `%f`

El formateo "nano" de newlib puede no soportar `%f`, y en ese caso el Monitor
Serie y el cuerpo JSON mostrarían basura en lugar de números. El firmware arma
los decimales con enteros, en `formatear2()` y `numeroAJson()`.

### 8.8 Lo que se ganó con la migración

| Aspecto | Arduino | ESP-IDF |
|---|---|---|
| **ADC** | `analogRead` × `3.3/4095` (aproximación) | **Calibración de fábrica del chip**, en milivoltios reales |
| **Cola de pendientes** | RAM → se perdía con un corte de luz | **NVS** → sobrevive al reinicio |
| **HTTPS** | `setInsecure()`: cifra sin validar | **`esp_crt_bundle`**: valida el certificado |
| **Concurrencia** | `delay()` bloqueante | FreeRTOS: tareas y colas |
| **Consumo** | siempre despierto | Posibilidad de `deep sleep` |

**La cola en NVS quedó verificada en hardware:** diez lecturas sobrevivieron a
dos reinicios y dos regrabaciones del firmware, y se publicaron con su hora
original (`medida el 2026-09-23T20:58:40Z`).

---

## 9. Qué sigue

1. **Calibrar** el TDS con el patrón de 707 ppm y el pH con los patrones 4,00 y 6,86.
2. **Recuperar y calibrar el electrodo de pH** (24–48 h en KCl) e instalar su divisor ÷2.
3. **Medir la geometría** del depósito para el nivel manual.
4. **Registrar** los valores de calibración: son evidencia directa para el Capítulo 2.
5. **Instalar** los sensores en el depósito, con la electrónica fuera del agua.

> **Cuidado con la sonda del DS18B20.** El tubo de acero es impermeable, pero la
> unión entre el tubo y el cable es el punto por donde fallan las sondas
> económicas. Conviene dejar esa unión fuera del agua o sellarla con silicona
> neutra: si le entra agua, la lectura se vuelve errática con los días — y no es
> un fallo evidente, es de los que envenenan los datos sin que uno se dé cuenta.

---

*Documento de trabajo del prototipo. El programa y su guía se versionan en el
repositorio; el archivo `configuracion.h` queda fuera.*
