# Prototipo del módulo — calibración paso a paso

**Proyecto:** SI.G.VA.C.H. · **Módulo:** `v6wrYSXxeHyttf3prDd7` — *Maqueta NFT - Lechuga*
**Fecha de preparación:** miércoles 23 de septiembre de 2026

> **Para qué sirve este documento.** Los sensores analógicos (pH y TDS) no entregan
> unidades: entregan una tensión que hay que traducir. La calibración consiste en medir
> **dos puntos conocidos** y anotar las tensiones obtenidas, de modo que el firmware
> pueda convertir cualquier lectura futura. Los valores que se anotan aquí se copian
> después en las **constantes del programa** (`sigvach_esp32.ino`).
>
> Las mediciones de este documento son, además, **evidencia directa** para el capítulo
> de implementación de la monografía: quedan registradas con fecha, valores y resultado.

---

## 1. Qué se calibra y qué no

| Variable | Sensor | ¿Se calibra? | Qué se ajusta en el programa |
|---|---|---|---|
| pH | PH-4502C + electrodo | **Sí**: dos patrones (4,00 y 6,86) | `VOLTAJE_PATRON_400`, `VOLTAJE_PATRON_686` |
| TDS y EC | TDS Meter V1.0 | **Sí**: un patrón (707 ppm) | `FACTOR_TDS` |
| Temperatura de la solución | DS18B20 | Contraste con termómetro | `AJUSTE_TEMPERATURA` |
| Temperatura ambiental y humedad | DHT22 | No requiere; se verifica coherencia | — |
| Nivel de agua | Manual (regla) | No aplica | — |

---

## 2. Materiales

| Elemento | Para qué |
|---|---|
| Patrón **pH 4,00** y patrón **pH 6,86** | Los dos puntos de la recta del pH |
| Patrón de **TDS 707 ppm** (o 1413 µS/cm) | Punto de calibración del TDS |
| **Agua destilada** | Enjuagar la sonda entre patrones |
| Tres vasos limpios y secos | Uno por solución; **no mezclar** los patrones |
| Termómetro de referencia | Contrastar el DS18B20 |
| La maqueta armada y el programa cargado en modo **solo Monitor Serie** | Para leer las tensiones |

**Precauciones.** Cada sonda se enjuaga con agua destilada **antes** de pasar de una
solución a otra: unas gotas de la solución anterior contaminan el patrón. Los patrones
se usan una vez y se descartan si quedaron turbios; no se devuelven al frasco.

---

## 3. Calibración del pH

### 3.1 Preparación del electrodo

Si el electrodo estuvo guardado en seco, **sumergirlo de 24 a 48 horas** en solución de
conservación (KCl) o, en su defecto, en el patrón de pH 4,00 antes de empezar. Un
electrodo deshidratado no responde y ninguna calibración lo arregla.

### 3.2 Procedimiento

1. Cargar el programa con `MODO_SOLO_SERIAL` en **true** y `USAR_PH` en **false**.
2. Abrir el Monitor Serie a **115200** y esperar a que aparezca la línea
   `Voltaje pH: X.XXX V`.
3. Enjuagar el electrodo con agua destilada y sacudirlo suavemente (**no** frotar el bulbo).
4. Sumergirlo en el **patrón 4,00** sin que toque las paredes del vaso. Agitar despacio.
5. Esperar de **30 a 60 segundos** hasta que la lectura se estabilice y anotar el voltaje.
6. Enjuagar con agua destilada y repetir con el **patrón 6,86**.
7. Copiar los dos valores en las constantes del programa y poner `USAR_PH` en **true**.

### 3.3 Registro

| Patrón | Voltaje medido (V) | Hora | Observaciones |
|---|---|---|---|
| pH 4,00 | | | |
| pH 6,86 | | | |

**Cómo calcula el programa el pH** (no hay que hacer cuentas, solo entenderlas):

```
pendiente = (V(6,86) − V(4,00)) / (6,86 − 4,00)        voltios por unidad de pH
pH        = 6,86 + ( V(6,86) − V(medido) ) / pendiente
```

Si la diferencia entre los dos voltajes medidos fuera **muy pequeña** (menos de 0,3 V),
el electrodo está agotado: corresponde reemplazarlo.

---

## 4. Calibración del TDS

1. Enjuagar la sonda con agua destilada y secarla con papel absorbente.
2. Sumergirla en el **patrón de 707 ppm**, sin que toque el fondo, y agitar suavemente
   para eliminar las burbujas de aire entre los electrodos.
3. Esperar de **1 a 2 minutos**: la lectura del TDS tarda más que la del pH.
4. Anotar el valor que informa el programa (en ppm).
5. Calcular el factor y copiarlo en el programa:

```
FACTOR_TDS = 707 ÷ (ppm informados por el programa)
```

### Registro

| Fecha | ppm informados | Factor calculado | Observaciones |
|---|---|---|---|
| | | | |

> **Nota sobre la EC.** La conductividad eléctrica que publica el sistema **se deriva del
> TDS** con la equivalencia `EC (mS/cm) = TDS (ppm) ÷ 500`, que es la escala de conversión
> habitual de estos medidores. Por eso, al calibrar el TDS, la EC queda calibrada en la
> misma operación: es una sola medición la que sostiene las dos variables.

---

## 5. Contraste de la temperatura

1. Preparar un vaso con **hielo picado y agua** (mezcla bien removida): son **0 °C**.
2. Sumergir el DS18B20 y el termómetro de referencia; esperar un minuto y anotar los dos.
3. Repetir a temperatura ambiente.
4. Si la diferencia es mayor que **0,5 °C**, corregirla:

```
AJUSTE_TEMPERATURA = temperatura de referencia − temperatura del DS18B20
```

### Registro

| Condición | DS18B20 (°C) | Termómetro (°C) | Diferencia | Ajuste aplicado |
|---|---|---|---|---|
| Agua con hielo (≈ 0 °C) | | | | |
| Ambiente | | | | |

> La temperatura importa **dos veces** en este proyecto: es una de las siete variables y,
> además, el TDS se corrige por temperatura usando justamente esta medición. Un error de
> 3 °C en el DS18B20 desvía el TDS alrededor de un 6 %.

---

## 6. Humedad y temperatura ambiental

El DHT22 viene calibrado de fábrica y no se ajusta. Se verifica que sus valores sean
**coherentes**: la temperatura ambiental debe parecerse a la del termómetro de referencia
(±1 °C) y la humedad, a la de un higrómetro o al pronóstico del día (±10 %). Anotar la
comprobación:

| Fecha | Temperatura DHT22 | Humedad DHT22 | Referencia | Diferencia |
|---|---|---|---|---|
| | | | | |

---

## 7. Nivel de agua (registro manual)

El nivel **no se mide con sensor**: se mide con una regla graduada y se registra desde la
aplicación, en *Registrar medición manual*, cuando se rellena el depósito.

| Fecha | Nivel medido (cm) | Acción realizada |
|---|---|---|
| | | |

**Si algún día se instala el ultrasónico**, hay que medir dos cosas con la regla y
anotarlas en el programa: la **altura total del agua cuando el depósito está lleno**
(`ALTURA_TANQUE_CM`) y la **distancia desde el sensor hasta la superficie con el depósito
lleno** (`DISTANCIA_SENSOR_CM`).

---

## 8. Registro de la calibración (evidencia)

| Fecha | Qué se calibró | Resultado | Responsable | Observaciones |
|---|---|---|---|---|
| | pH (dos patrones) | | | |
| | TDS (707 ppm) | | | |
| | Temperatura | | | |

---

## 9. Mantenimiento

| Pieza | Cuidado | Frecuencia |
|---|---|---|
| **Electrodo de pH** | Guardarlo **siempre húmedo**, con el capuchón lleno de solución de conservación (KCl). Nunca en agua destilada ni seco | Cada vez que se retira del agua |
| **Electrodo de pH** | Recalibrar con los dos patrones | Cada 2 a 4 semanas, y siempre después de limpiarlo |
| **Sonda de TDS** | Enjuagar con agua destilada y secar; limpiar los electrodos con un cepillo suave si se incrustan sales | Semanal |
| **DS18B20** | Revisar que el cable no quede sumergido más allá del prensaestopas | Mensual |
| **Electrónica** | Que la caja quede **fuera** del agua y tapada: el vapor y el polvo de obra dañan las placas | Continuo |

---

## 10. Verificación final

Con la calibración aplicada, el sistema queda correcto si:

| Comprobación | Resultado esperado |
|---|---|
| Sumergir el electrodo en el patrón 4,00 | El panel informa **≈ 4,0** (tolerancia ±0,2) |
| Sumergir el electrodo en el patrón 6,86 | El panel informa **≈ 6,9** (tolerancia ±0,2) |
| Sumergir la sonda TDS en el patrón 707 ppm | El panel informa **≈ 707 ppm** (tolerancia ±30) |
| Cambiar el agua por solución nutritiva | El TDS y la EC **suben**; si el valor sale del rango del perfil de lechuga (600 a 900 ppm · 1,2 a 1,8 mS/cm), **aparece una alerta** |
| Comparar la temperatura con un termómetro | Diferencia menor que 0,5 °C |
| Registrar el nivel desde la aplicación | El valor aparece en el panel y en el historial |

Cuando estas seis comprobaciones se cumplen, el módulo está calibrado y listo para
quedar midiendo de forma continua.

---

*Documento de trabajo del prototipo. Los valores anotados aquí se copian a las constantes
del firmware y se conservan como registro de la calibración para la monografía.*
