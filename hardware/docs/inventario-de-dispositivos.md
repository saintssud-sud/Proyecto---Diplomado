# Prototipo del módulo — inventario de dispositivos identificados

**Fecha:** miércoles 23 de septiembre de 2026
**Fotos:** `dispositivos/` (20 archivos)

---

## 1. Lo que hay, ya identificado

| # | Pieza (según la foto) | Identificación | Notas |
|---|---|---|---|
| 1 | `ModuloESP32-38pines.jpg` | **ESP32 de 38 pines** (módulo ESP32-WROOM-32), con la serigrafía de sus pines | Es la placa que va a ejecutar el firmware |
| 2 | `ModuloESP32+placa-Expancion.jpg` | **Placa de expansión** morada, con conector de barril **DC 6,5–16 V**, USB-C, micro-USB, **puente 3,3 V/5 V** y cabecera rotulada (`SVP`, `SVN`, `P34`, `P35`, `P32`, `P33`, `P25`, `P26`, `P27`, `P14`, `P12`, `P13`, `SD2`, `SD3`, `CMD`, `5V`, `GND`, `EN`) | Es la que alimenta y ordena las conexiones: sus rótulos son los que se usan en el mapa de pines |
| 3 | `Sensor-pH1.jpg`, `Sensor-pH4.jpg`, `cajaSensor-pH.jpg` | **Electrodo de pH con conector BNC** + **placa de acondicionamiento PH-4502C** (dos potenciómetros azules, bornera de 6 pines) | La caja azul es el envase del electrodo (serie de electrodos de pH) |
| 4 | `SensotTDS.jpg` | **TDS Meter V1.0** (placa negra rotulada) + sonda blanca de dos electrodos | El módulo entrega la señal ya acondicionada |
| 5 | `SensorDS18b20.jpg` | **DS18B20** sumergible, punta de acero inoxidable, cable negro | Temperatura de la solución |
| 6 | `SensorDHT22.jpg` | **DHT22 / AM2302** en plaqueta de 3 pines (`+`, `out`, `−`) | Temperatura ambiental **y** humedad relativa. **Elegido para el montaje** (véase §1.2) |
| 7 | `SensorAM2302.jpg` | **AM2302 (DHT22)** con cable de tres hilos, sin plaqueta | Segunda unidad, reserva. **Mejor ubicación** si se quiere alejar del calor de la electrónica (véase §1.2) |
| 8 | `SENSOR ULTRASÓNICO HC-SR04.jpg` | **HC-SR04** (dos cilindros, rótulo `Vcc Trig Echo Gnd`), ya montado en un soporte de cartón | **Fuera del alcance.** La variable de nivel de agua se retiró del sistema, así que la pieza queda como repuesto; su salida Echo es de 5 V y exigiría un divisor |
| 9 | `MiniBomba.jpg` | **Bomba sumergible de corriente continua** con su fuente (adaptador negro con conector de barril) | Recirculación del NFT. No la controla el sistema: funciona siempre o con temporizador |
| 10 | `MaquetaAccesorios.jpg`, `PartesMaqueta.jpeg` | **Estructura NFT**: cuatro tubos con orificios, colector con codos, dos canastillas, microtubo negro con goteros y manguera corrugada de retorno | Fotografiada sobre el piso, todavía sin armar sobre las patas |
| 11 | `SensorDesconocido.jpg` | **Sensor de temperatura de suelo (sonda NTC) para termostato Thermoreg** | **Identificado el 23/09.** No se usa en el prototipo: mide la temperatura del **suelo o sustrato**, que no es una de las seis variables del sistema, y al ser una sonda resistiva del termostato exige una curva de calibración propia. La temperatura de la solución la mide el **DS18B20**, que es digital, calibrado y sumergible |

---

### 1.1 Por qué la sonda de suelo queda fuera

| Pregunta | Respuesta |
|---|---|
| ¿Mide alguna de las seis variables? | **No.** El sistema mide temperatura **ambiental**, humedad **relativa**, temperatura de la **solución**, pH, TDS y EC. La temperatura del sustrato no está en el alcance |
| ¿Puede reemplazar al DS18B20? | **No conviene.** Es una sonda resistiva (NTC) pensada para un termostato comercial: habría que averiguar su curva de calibración y armar un divisor para leerla, mientras que el DS18B20 ya entrega la temperatura en grados, calibrada y por un solo hilo |
| ¿Sirve para algo más adelante? | Sí: si el proyecto mayor mide el **sustrato** en lugar de la solución, es una pieza aprovechable |

**Decisión:** se guarda como repuesto y no forma parte del módulo.

---

### 1.2 Cuál de los dos sensores de ambiente usar (DHT22 o AM2302)

**Son el mismo sensor.** El **DHT22** es la denominación comercial y **AM2302** es el
modelo del fabricante (Aosong): misma precisión (±0,5 °C y ±2 % de humedad relativa),
misma frecuencia de lectura (una cada 2 segundos) y misma tensión de trabajo. Lo único
que cambia es **cómo viene presentado**:

| | **DHT22 en plaqueta** (foto 6) | **AM2302 con cable** (foto 7) |
|---|---|---|
| Presentación | Sensor soldado a una plaqueta con 3 pines (`+`, `out`, `−`) | Sensor con cable de tres hilos (rojo, amarillo, negro) |
| Resistencia de pull-up | **Ya viene incorporada** en la mayoría de estas plaquetas | **Hay que agregarla**: 10 kΩ entre el hilo de datos y 3,3 V |
| Conexión | Directa al protoboard con cables dupont | Requiere bornera o estaño |
| Ubicación del sensor | Queda **junto a la electrónica** | Permite **alejarlo 30 a 50 cm** |

**Criterio de elección.** El ESP32 y su placa de expansión **generan calor**: si el sensor
queda pegado a ellos, la temperatura ambiental que informa el sistema es la del
microcontrolador y no la del cultivo, con una desviación de 1 a 3 °C. Eso afecta a una de
las seis variables y, de paso, a la compensación por temperatura del TDS.

| Momento | Cuál usar | Por qué |
|---|---|---|
| **Montaje y pruebas** | **DHT22 en plaqueta** | Se conecta al protoboard sin agregar nada y permite verificar el conexionado enseguida |
| **Instalación definitiva** | **AM2302 con cable** (con su pull-up de 10 kΩ) | El sensor se ubica **a la altura del cultivo**, ventilado y a la sombra, lejos del calor de la electrónica: la medición corresponde al ambiente real |

**El cambio es libre.** Los dos son el mismo sensor para el programa
(`#define TIPO_DHT DHT22` sirve para ambos) y se conectan al **mismo pin `P33`**: no hay
que modificar el firmware, solo mover el cable y agregar la resistencia.

**Recomendación:** arrancar con el de la plaqueta y pasar al de cable cuando se instale el
módulo en la maqueta. Si el de la plaqueta se coloca con ventilación y lejos del
regulador de la placa de expansión, la diferencia se reduce, pero no desaparece.

### 1.3 Cómo saber si alguno es un DHT11 (y no un DHT22)

El autor observó que **una pieza es más grande que la otra**. Eso importa, porque el
**DHT11 y el DHT22 se parecen por fuera pero no son equivalentes**, y la biblioteca
necesita saber cuál es: con el tipo equivocado entrega valores inválidos.

| | **DHT11** | **DHT22 / AM2302** |
|---|---|---|
| Tamaño de la carcasa | **≈ 12 × 15,5 mm** | **≈ 15 × 25 mm** (más grande) |
| Precisión de temperatura | ±2 °C | **±0,5 °C** |
| Precisión de humedad | ±5 % | **±2 %** |
| Rango de humedad | 20 a 90 % | **0 a 100 %** |
| Frecuencia de lectura | 1 por segundo | 1 cada 2 segundos |

**Cómo distinguirlos:**

1. **Con una regla**, midiendo la carcasa blanca: 15 mm de alto es un DHT11; 25 mm, un
   DHT22.
2. **Buscando el modelo impreso** en la carcasa (muchas unidades lo traen). En las fotos
   disponibles no se lee.
3. **Con el propio firmware** (lo más simple): el programa **prueba primero el DHT22** y,
   si no responde, **prueba el DHT11** e informa por el Monitor Serie cuál encontró:

```
  Sensor de ambiente: DHT22 / AM2302  (precision +-0,5 C y +-2 % HR)
      o bien
  Sensor de ambiente: DHT11  (menos preciso: +-2 C y +-5 % HR)
```

**Qué conviene para el proyecto.** El **DHT22/AM2302**: un error de ±2 °C en la
temperatura ambiental es mucho para un sistema cuyo propósito es vigilar rangos, y el
DHT11 **se satura por encima del 90 % de humedad**, justo cuando una jornada húmeda
sacaría el valor del rango. Si el sensor grande resulta ser el del cable, se usa ese —
que además es el que puede ubicarse lejos de la electrónica— agregando su resistencia de
**10 kΩ** entre el hilo de datos y 3,3 V.

### 1.4 Identificación confirmada (23/09)

La fotografía de las dos piezas juntas, con la etiqueta del fabricante a la vista,
resolvió la duda:

**La pieza grande, la que tiene cable, es un AM2302** —es decir, un **DHT22**—, y su
propia etiqueta lo declara:

| Dato de la etiqueta | Valor |
|---|---|
| Modelo | **AM2302** |
| Alimentación | **3,3 a 5,5 V** continua |
| Humedad | **0 a 99,9 % HR** |
| Temperatura | **−40 a 80 °C** |
| **Precisión** | **±2 % HR y ±0,5 °C** |
| Salida | Digital, de un solo hilo |
| Número de serie | D546300ZB9 |

**La pieza pequeña, la de la plaqueta negra, no trae etiqueta** y es la mitad de alta: por
tamaño corresponde a un **DHT11** (el modelo menos preciso). No hace falta decidirlo a
ojo: cuando se cargue el programa, el Monitor Serie lo informará.

### Decisión

| Pieza | Papel en el proyecto |
|---|---|
| **AM2302 con cable** (grande) | **Sensor definitivo del módulo.** Es el preciso (±0,5 °C y ±2 % HR), admite 3,3 V —lo que reduce su autocalentamiento— y su cable permite ubicarlo **a la altura del cultivo**, lejos del calor del ESP32. **Necesita una resistencia de 10 kΩ** entre el hilo de datos y 3,3 V |
| **DHT11 en plaqueta** (pequeño) | **Sensor de pruebas y repuesto.** Sirve para verificar el conexionado en el protoboard, porque se enchufa sin agregar nada |

**Conexión del AM2302** (verificar los colores del cable antes de conectar):

| Hilo | Va a |
|---|---|
| **Rojo** (VDD) | `3,3V` |
| **Amarillo** (datos) | `P33` **+ resistencia de 10 kΩ a `3,3V`** |
| **Negro** (GND) | `GND` |

---

## 2. Consecuencias para el conexionado

1. **El electrodo de pH y el TDS son analógicos** y van a las **únicas entradas analógicas que
   funcionan con el WiFi encendido**: las del **ADC1**. En la placa de expansión están rotuladas
   **`SVP` (GPIO 36)**, **`SVN` (GPIO 39)**, `P32`, `P33`, `P34`, `P35`. Las demás (25, 26, 27,
   12, 13, 14) pertenecen al ADC2 y **no sirven para leer analógico con WiFi**.
2. **La salida del PH-4502C puede superar los 3,3 V** → necesita **divisor de tensión** antes de
   entrar al ESP32. La calibración se hace **con el divisor ya conectado**, de modo que el factor
   del divisor queda absorbido por la recta de calibración.
3. **El DS18B20 necesita una resistencia de 4,7 kΩ** entre el pin de datos y 3,3 V.
4. **El DHT22 en plaqueta** suele traer su resistencia de pull-up incorporada; el **AM2302 con
   cable no**, y necesita 10 kΩ entre datos y 3,3 V.
5. **Masa común** para todas las piezas y alimentación de las placas de pH y TDS desde el riel de
   **5 V**, mientras que el DS18B20 y el DHT22 van al de **3,3 V**.

---

## 3. Mapa de pines propuesto (a confirmar con el multímetro antes de conectar)

| Pieza | Terminal | Pin en la placa de expansión | Tensión |
|---|---|---|---|
| PH-4502C | `Po` (salida analógica) | `SVP` (GPIO 36), **con divisor** | 5 V → 3,3 V |
| PH-4502C | `V+` / `G` | `5V` / `GND` | 5 V |
| TDS Meter V1.0 | `AOUT` | `SVN` (GPIO 39) | señal ≤ 2,3 V |
| TDS Meter V1.0 | `VCC` / `GND` | `5V` / `GND` | 5 V |
| DS18B20 | datos (amarillo) | `P32` + **4,7 kΩ a 3,3 V** | 3,3 V |
| DS18B20 | `VDD` / `GND` | `3,3V` / `GND` | 3,3 V |
| DHT22 | `out` | `P33` | 3,3 V |
| DHT22 | `+` / `−` | `3,3V` / `GND` | 3,3 V |

**Los seis pines del ADC1 quedan así ocupados en dos** (`SVP` y `SVN`): el resto se usa como
entrada o salida digital, que no tiene esa restricción.

---

## 4. Lo que falta averiguar

| # | Dato | Para qué |
|---|---|---|
| 1 | Qué es el «sensor desconocido» (cable negro con punta azul) | Saber si aporta otra variable o es un repuesto |
| 2 | Etiqueta de la bomba: caudal (L/h) y tensión | Confirmar el caudal para los cuatro tubos |
| 3 | Medidas de los tubos: **largo**, **diámetro** y **cuántos orificios** | Dimensión del depósito y dosis de solución |
| 4 | ¿Hay **depósito** (balde o caja) y de cuántos litros? | Es el recipiente donde van las sondas |
| 5 | ¿Hay **solución nutritiva A/B/C**? | Puesta en marcha del cultivo |
| 6 | ¿Hay **soluciones de calibración** de pH (4,00 y 6,86) y de TDS (707 ppm)? | Calibración de los dos sensores analógicos |
| 7 | ¿Hay **protoboard, cables dupont, resistencias** (4,7 kΩ, 10 kΩ, 20 kΩ, 1 kΩ, 2 kΩ) y **multímetro**? | Montaje y verificación |

---

## 5. Estado de los inconvenientes detectados (23/09)

### 5.1 El electrodo de pH no mide: le falta la solución de conservación

**Qué pasa.** Un electrodo de pH tiene un bulbo de vidrio y una junta de referencia que
**deben permanecer húmedos**. Si se guarda en seco, la membrana se deshidrata y la
lectura deja de responder; el síntoma es exactamente el que describe el autor: el sensor
no entrega datos utilizables.

**Qué se necesita.**

| Elemento | Para qué | Alternativa |
|---|---|---|
| **Solución de conservación (KCl 3 M)** | Mantener el electrodo húmedo entre mediciones; es lo que debe llevar el capuchón | Se puede preparar con cloruro de potasio y agua destilada |
| **Solución patrón pH 4,00** | Primera recta de calibración | Sobres de buffer de un solo uso |
| **Solución patrón pH 6,86 (o 7,00)** | Segundo punto de calibración | Ídem |
| **Agua destilada** | Enjuagar entre patrones | — |

**Recuperación del electrodo (antes de comprar otro).** Sumergir el bulbo en solución de
conservación (o, en su defecto, en el patrón de pH 4,00) durante **24 a 48 horas**. Un
electrodo deshidratado suele recuperar la respuesta. Si después de eso la lectura sigue
sin reaccionar al cambiar de patrón, la membrana está dañada y corresponde **reemplazar
el electrodo** (es la pieza más económica del conjunto y se consigue sola, con conector
BNC).

**Mientras tanto, el proyecto no se detiene:** el firmware y la maqueta se prueban con
las demás variables —temperatura ambiental, humedad relativa, temperatura de la solución y TDS—, que no dependen de ninguna solución. El sistema admite que una
variable no tenga lecturas: simplemente informa que no hay datos, sin inventar valores.

### 5.2 Los tubos de PVC

| Dato | Valor informado | Observación |
|---|---|---|
| Largo | **90 cm** por tubo | Cuatro tubos, según las fotos |
| Cantidad | 4 tubos con orificios + colector | ~20 a 24 sitios de cultivo |
| Ancho del conjunto armado | 73 a 74 cm | Es la medida del panel de tubos en paralelo |
| Diámetro | **2,4 a 2,6 cm** informado | A confirmar: conviene una foto con la huincha sobre el tubo, porque con ese diámetro las canastillas no entrarían |

**Falta confirmar con una foto y una huincha:** el **diámetro exterior del tubo** y el
**diámetro de los orificios**. De esos dos números dependen el tamaño del depósito, el
caudal de la bomba y la geometría del sensor de nivel.

---

## 6. Módulo registrado en el sistema

El 23 de septiembre se dio de alta el módulo de cultivo que usará la maqueta, **con el
perfil de lechuga** (que ya tiene sus seis rangos de referencia cargados), para que las
lecturas del prototipo no se mezclen con las de la demostración del entregable:

| Dato | Valor |
|---|---|
| Identificador | **`v6wrYSXxeHyttf3prDd7`** |
| Nombre | Maqueta NFT - Lechuga |
| Tipo de cultivo | Lechuga |
| Perfil | `perfil-lechuga` |
| Rangos vigentes | pH 5,5–6,5 · EC 1,2–1,8 · TDS 600–900 · temperatura de solución 15–25 · temperatura ambiental 15–25 · humedad 50–80 |
| Ubicación | Interior – maqueta demostrativa *(se puede editar desde la aplicación)* |

**Ese identificador es el que se copia en `MODULO_ID`** del archivo `configuracion.h` del
firmware. El módulo se creó con la misma estructura que los módulos creados desde la
aplicación, de modo que el panel lo muestra igual y se puede renombrar, desactivar o
eliminar desde ahí.

**Estado de la base al 23/09:** 3 perfiles (lechuga, acelga, apio), 4 módulos,
6 rangos (todos del perfil de lechuga), 29 lecturas y 5 alertas de la demostración.

---

*Documento de trabajo. Se actualiza a medida que se confirman los datos faltantes.*
