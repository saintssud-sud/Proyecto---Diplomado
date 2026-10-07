# Bitácora — miércoles 7 de octubre de 2026

Sesión de trabajo sobre el canal de TDS del módulo de adquisición.
**Resultado: se encontró y se corrigió la causa de un desvío del 16 % en la sonda.**

Esta bitácora se escribe el mismo día, con los números tomados en el momento. Es la
memoria de trabajo de la sesión: sirve para no repetir pruebas ya hechas y para
poder explicar cada decisión en la defensa.

---

## 1. Resumen en cinco líneas

1. Al repetir la verificación de la calibración del TDS, la sonda informó **16 a 23 % menos** que el día anterior para el mismo patrón.
2. Se probaron **cinco hipótesis con mediciones** (dilución, recipiente, alimentación, geometría, profundidad) y **todas se descartaron**.
3. La causa era **una película sobre las placas** de la sonda, formada en la noche que pasó secándose con restos encima.
4. Limpiar con **alcohol isopropílico** devolvió la lectura al valor correcto: **707,08 ppm de media contra un patrón de 707** (error +0,01 %).
5. **La calibración del 6 de octubre queda validada**: el factor 0,9373 estaba bien; lo que fallaba era la sonda sucia.

---

## 2. Cronología de la sesión

### 2.1 Preparación del patrón (tarde)

Se intentó medir el patrón en un vaso de vidrio de **fondo grueso con hueco interno**. Los
resultados fueron bajos y no cerraban:

| Intento | Preparación | Lectura | Concentración implícita |
|---|---|---|---|
| 1.º | Vaso con agua desionizada dentro + 100 mL de patrón | 1469 mV / 550 ppm | **78 %** del patrón |
| 2.º | Vaso vaciado y secado parcialmente + enjuague | 1556 mV / 572 ppm | **81 %** del patrón |

**Diagnóstico:** el vaso retenía agua en el hueco de la base, que no se vacía sacudiendo
y no se ve desde el costado. Esa agua diluía el patrón.

**Regla que salió de acá:** el recipiente tiene que ser de **fondo plano y fino**, y
**nunca se enjuaga con agua antes de medir**. Si se enjuaga, el enjuague final es **con el
propio patrón, y se tira**.

### 2.2 Prueba del envase nuevo con agua desionizada

Frasco nuevo de fondo plano, sonda enjuagada, agua desionizada adentro:

```
Solucion -> 21,75 °C
TDS -> 142 mV crudo 0   dispersión 0   señal estable
    -> 58,48 ppm   0,12 mS/cm
```

**58,48 ppm es el piso del módulo.** Con la sonda seca al aire el módulo informa lo mismo
(142 mV). O sea: **el módulo tiene un desplazamiento de base y nunca llega a cero**. Es un
dato que conviene tener anotado: cualquier lectura por debajo de ~60 ppm significa
«líquido sin iones o sonda al aire», no un valor real.

Y sirvió como verificación: **el frasco y las sondas estaban limpios.**

### 2.3 El patrón en el frasco seco

```
Solucion -> 25,19 °C
TDS -> 1453 mV crudo 1597   dispersión 18   señal estable
    -> 520,06 ppm   1,04 mS/cm
```

**520 ppm.** La más baja de todas, cuando tendría que haber sido la más alta. Con esto
**quedó descartada la dilución** (el frasco estaba seco) y el problema pasó a estar en la
sonda o en el módulo.

### 2.4 Prueba de la alimentación del módulo

Se midió con multímetro la alimentación del módulo de TDS: **3,28 V** (el pin 3V3 del
ESP32). Se movió el cable al pin **5V** y se volvió a medir: **5,08 V**.

| Alimentación | Lectura del patrón |
|---|---|
| 3,28 V | 1456 mV |
| 5,08 V | 1468 mV |

**Diferencia de 0,8 %.** La alimentación **no** es la causa: el módulo no es tan
ratométrico como se suponía. Hipótesis descartada con medición.

### 2.5 Barrido de profundidad

Se grabaron 21 lecturas moviendo la sonda de arriba abajo dentro del patrón:

```
mV: 1472 a 1482   ->  10 mV de recorrido (0,7 %)
ppm: 555,9 a 561,7
```

**La profundidad de inmersión no explica el desvío.** Hipótesis descartada.

### 2.6 Un tropiezo: el módulo dejó de responder

Al mover cables, el ESP32 **dejó de imprimir por el puerto serie**. Se verificó que el
puerto seguía existiendo (COM6, el CP210x) pero sin datos: el chip del puerto serie se
alimenta del USB, así que **el puerto aparece aunque el microcontrolador no arranque** —
una trampa que conviene conocer.

Se volvió el cable de alimentación a su posición original y el módulo volvió a funcionar.

### 2.7 La limpieza, y el resultado

**Antes de limpiar:** 1456 mV → 546 ppm.

Se sumergió **solo la punta** en alcohol isopropílico, se dejó evaporar, se enjuagó con
agua desionizada y se volvió a poner en el frasco.

**Después de limpiar:** 1733 mV → **706 ppm**.

---

## 3. Las cinco hipótesis descartadas

| Hipótesis | Cómo se probó | Resultado |
|---|---|---|
| Dilución por agua en el recipiente | Frasco seco, patrón directo | **Descartada** |
| Recipiente con agua escondida | Vaso de fondo grueso vs frasco plano | **Descartada** |
| Alimentación 3,3 V vs 5 V | Se movió al pin 5V y se midió | **Descartada** (0,8 %) |
| Geometría del recipiente | Tres recipientes distintos | **Descartada** |
| Profundidad de inmersión | Barrido de 21 lecturas | **Descartada** (0,7 %) |
| **Película sobre las placas** | Limpieza con alcohol isopropílico | **CONFIRMADA** |

---

## 4. La causa raíz

Una **película sobre los electrodos**. En un conductímetro, la película agrega una
resistencia en serie con la del líquido y **baja** la lectura. Una pérdida de 10 a 30 % es
típica.

**De dónde salió:** la sonda pasó **la noche secándose con restos de líquido encima**. Al
evaporarse, lo disuelto se concentra y forma una costra que el agua sola no disuelve. La
secuencia lo confirma:

| Momento | Estado de la sonda | Lectura del patrón |
|---|---|---|
| 6/10, calibración | Recién usada, húmeda | **1758 mV** (correcto) |
| 7/10, por la tarde | Después de la noche seca | **1456 mV** (−16 %) |
| 7/10, tras limpiar | Placas limpias | **1733 mV** (correcto) |

---

## 5. Verificación final

Patrón en el frasco, sin tocar nada más, 25 lecturas consecutivas una cada 5 segundos:

```
mV crudos : 1732 a 1734       (recorrido de 2 mV)
ppm       : 705,95 a 708,55   ->  MEDIA 707,08 ppm
patrón    : 707 ppm           ->  error +0,01 %
temperatura: 22,75 a 22,81 °C
dispersión : 19 de 25 ciclos «señal estable»
```

Evidencia: `hardware/evidencias/limpieza-de-la-sonda-de-tds-2026-10-07.txt`.

---

## 6. Lo que aprendimos: reglas de mantenimiento

### Sonda de TDS

1. **No se guarda seca con restos encima.** Se enjuaga con **agua desionizada** y se
   sacude antes de guardarla.
2. **Se limpia con alcohol isopropílico** cuando la lectura se aparta más de un 5 % de lo
   esperado. Solo la punta; el cable y el conector, fuera.
3. **Después de limpiar, siempre se verifica**: la lectura puede cambiar hasta un 16 %.
4. **Su piso es ~58 ppm.** Por debajo de eso, la lectura no es un valor real.
5. Se guarda **seca y limpia**, nunca con líquido adentro del frasco (el líquido se
   evapora y deja la película).

### Electrodo de pH

1. **No puede quedarse seco.** Entre mediciones va en la **solución de almacenamiento
   Hanna HI70300**, parado y con el bulbo hacia abajo.
2. **Guardado seco, el cero se corre.** Ya pasó: entre el 1 y el 4 de octubre el cero se
   desplazó **33 mV** (de 1520 a 1553 mV) mientras la pendiente no cambió (−84,2 a −83,9
   mV por unidad). Recuperarlo costó días de remojo.
3. El calibrado se hace con **dos patrones** (4,01 y 6,86) y la lectura solo se asienta
   cuando están sumergidos **el bulbo y la junta de referencia**. En agua de baja
   mineralización la lectura es menos repetible: es una limitación de la técnica.
4. **Cuidado con publicar valores flotantes.** Con el electrodo al aire, el firmware lo
   detecta por la dispersión (200-280, «nada conectado») pero **igual publica** si el valor
   cae dentro de 0-14. Se publicaron así un 6,54, un 8,10 y un 10,96 que **parecen
   mediciones reales y no lo son**, y pueden disparar alertas falsas.

**El paralelo entre los dos sensores, que es la lección del día:**

- El **pH** necesita **hidratación** (agua o solución de almacenamiento).
- El **TDS** necesita **limpieza** (que no se seque nada sobre las placas).
- Los dos, si se guardan mal, **se apartan sin dar señal de alarma** — y ese es el peor
  tipo de falla, porque envenena el registro sin que nadie se entere.

---

## 7. Corrección a una interpretación del 6 de octubre

Durante la sesión del 6 de octubre se estimó una **dependencia térmica del canal de ~1,4 %
por grado**, comparando dos temperaturas separadas por 1 °C de esa jornada (707,97 ppm a
23,44 °C y 697,75 ppm a 22,44 °C). Esa cifra **no llegó a escribirse en la nota de
evidencia** del 6 de octubre: quedó como interpretación de la sesión.

**Hoy queda en revisión.** La verificación de hoy dio **707,08 ppm a 22,8 °C**, o sea 0,6 °C
por debajo de la temperatura de calibración, y con el mismo factor. Si la dependencia fuera
de 1,4 % por grado, habría dado unos 700 ppm.

Lo más probable es que aquel apartamiento **no fuera térmico, sino la película empezando a
formarse** — el mismo mecanismo que hoy quedó demostrado.

Mientras no se mida con la sonda limpia y un rango amplio de temperatura, la afirmación
correcta es: **la lectura se mantiene dentro del 1 % entre 22,8 y 23,4 °C; el coeficiente
térmico no está determinado.** Si en el documento llegó a declararse el 1,4 % por grado,
hay que corregirlo.

---

## 8. Pendientes que quedaron de la sesión

1. **Devolver las sondas al tanque** y ver el valor real con la sonda limpia (los valores
   anteriores del tanque estaban hasta un 16 % bajos por la película).
2. **Devolver el firmware a la versión de producción** (`PUBLICAR_EN_SERVICIO 1`): el
   módulo quedó con la versión de prueba, que no publica.
3. **Un soporte fijo para la sonda**: aunque la profundidad se descartó como causa, hoy no
   hay forma de fijar la posición. Una pinza o una marca en la sonda hacen el montaje
   repetible entre sesiones.
4. **El umbral de dispersión para el pH**: no publicar cuando el firmware ya detecta que la
   entrada está flotando (dispersión > ~120; en líquido es 9-41, en aire 200-280).
5. **Fotografiar los procedimientos** para el anexo del manual: la limpieza de la sonda de
   TDS y la preparación del patrón.

---

## 9. Archivos y evidencia de esta sesión

| Archivo | Contenido |
|---|---|
| `hardware/evidencias/limpieza-de-la-sonda-de-tds-2026-10-07.txt` | La nota completa: síntoma, hipótesis, causa, limpieza y verificación |
| `hardware/evidencias/tds-verificacion-limpieza-2026-10-07.txt` | Volcado crudo de las 25 lecturas de la verificación |
| `hardware/evidencias/tds-barrido-profundidad-2026-10-07.txt` | Volcado crudo del barrido de profundidad (21 lecturas) |
| `hardware/evidencias/calibracion-del-tds-2026-10-06.txt` | La calibración del día anterior, que esta sesión valida |

---

## 10. Lo que esta sesión demuestra, dicho en una frase

**El canal de TDS no tenía un problema de calibración: tenía una sonda sucia.** Y llegar a
esa conclusión costó descartar cinco hipótesis con mediciones propias — que es exactamente
el trabajo que hay que hacer para poder afirmar algo con respaldo.
