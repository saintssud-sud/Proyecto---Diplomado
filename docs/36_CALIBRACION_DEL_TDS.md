# Calibración del TDS con el patrón Hanna HI7031

Documento interno de trabajo. Registra el procedimiento **y el resultado** de la calibración del TDS.

**Estado: EJECUTADA el 6 de octubre de 2026**, entre las 22:21 y las 22:27.
La sonda leía un **6,7 % alto**; factor **0,9373** aplicado en el firmware; verificación con el patrón
todavía en el vaso: **707,97 ppm** contra los 707 ppm del patrón.
Evidencia: `hardware/evidencias/calibracion-del-tds-2026-10-06.txt`.

---

## 0. Resumen del resultado

| | |
|---|---|
| Patrón | Hanna HI7031 · 1413 µS/cm a 25 °C, ± 5 µS/cm, trazable a material de referencia NIST |
| Equivalencia | 1413 µS/cm = 1,413 mS/cm × 500 = **707 ppm** |
| Medido: 30 lecturas, una cada 5 s | media **754,25 ppm** · mínimo 751,62 · máximo 756,44 (0,6 % de recorrido) |
| Temperatura de la solución | 23,50 a 23,63 °C |
| Factor | 707 ÷ 754,25 = **0,9373** |
| Constante en el firmware | `TDS_FACTOR_CORRECCION 0.9373f` (`hardware/firmware/main/main.c`) |
| Verificación tras regrabar | **707,97 ppm**, error +0,14 % |

---

## 1. Qué faltaba y por qué

El pH ya estaba calibrado y verificado: el electrodo en el patrón 4,01 da 4,01 exacto, y la recta está
declarada en `hardware/firmware/main/main.c` con sus dos tensiones medidas.

El **TDS no estaba calibrado**. Lo que había era la conversión del fabricante, sin ninguna corrección
propia:

1. Compensación por temperatura, que lleva la tensión medida a su equivalente a 25 °C:
   `V(25) = V medida / (1 + 0,02 · (T − 25))`.
2. Polinomio cúbico del fabricante del módulo TDS Meter V1.0 (`sensores.c`, `sensores_tds_a_ppm`):
   `ppm = (133,42·V³ − 255,86·V² + 857,39·V) · 0,5`.

Ese polinomio describe el sensor **típico** del fabricante, no el nuestro: cada placa y cada sonda se
apartan un poco. Por eso el TDS figura como pendiente en el documento y por eso se compró un patrón.

## 2. Lo que llegó (6 de octubre de 2026)

| Reactivo | Qué es | Para qué se usa acá |
|---|---|---|
| **Hanna HI7031**, 500 mL | Patrón de conductividad **1413 µS/cm ± 5 µS/cm a 25 °C**, trazable a material de referencia NIST | **Calibrar el TDS.** Es el único patrón de conductividad del laboratorio |
| **Hanna HI70300**, 230 mL | Solución de almacenamiento para electrodos de pH y ORP | **No es patrón.** Mantiene hidratado el electrodo de pH entre mediciones |

El HI70300 **no se usa para calibrar**: no tiene un valor de pH certificado. Su función es que la
membrana del electrodo no se seque — el peor enemigo de un electrodo de pH.

## 3. El valor objetivo: 707 ppm

El patrón está certificado en **conductividad**, no en TDS. La conversión que usa el sistema es la
habitual en soluciones nutritivas, `TDS (ppm) ≈ EC (mS/cm) × 500`, la misma que aplica
`sensores_ppm_a_conductividad` para derivar la EC de la lectura de TDS:

```
1413 µS/cm = 1,413 mS/cm        (1 mS/cm = 1000 µS/cm)
1,413 mS/cm × 500 = 706,5 ppm  →  objetivo 707 ppm
```

**La temperatura ambiente no cambia el objetivo.** El patrón está certificado a 25 °C y el firmware ya
lleva la tensión medida a su equivalente a 25 °C usando el DS18B20. Los dos efectos —el del patrón y el
de la compensación— son el mismo, así que a 20 °C o a 28 °C el número que hay que alcanzar sigue siendo
707 ppm. Lo que sí importa es que **el DS18B20 esté en el mismo vaso**: si se queda en el tanque, la
compensación trabaja con la temperatura equivocada y el error es de ~2 % por grado.

## 4. Procedimiento

### 4.1 Preparación

1. Enchufar el módulo por USB. **No abrir el Monitor Serie del ESP-IDF**: el puerto lo lee
   `_diagnostico/leer_serial.ps1` desde la PC, y dos programas no pueden tener COM6 abierto a la vez.
2. Enjuagar la sonda de TDS con agua destilada y sacudirla para quitar las gotas. No frotarla: son dos
   placas enfrentadas y se pueden separar.
3. Echar unos **100 mL del patrón en un vaso limpio y seco**. **Nunca meter la sonda en la botella**: la
   sonda arrastra restos de la solución del tanque y contamina los 500 mL que quedan para las próximas
   calibraciones. Es el error clásico y arruina el patrón en una sola vez.
4. Enjuagar la sonda con un chorrito de ese mismo patrón y tirar ese chorrito, para que el agua
   destilada que quedó no diluya la medición.

### 4.2 Medición

5. Meter en el vaso **la sonda de TDS y el DS18B20**, las dos juntas: las placas del TDS bien
   sumergidas, a unos 2 cm del fondo, sin tocar las paredes del vaso ni una sonda a la otra.
6. Revolver suave 5 segundos, golpear la sonda contra el vaso para soltar burbujas y dejarla **quieta
   2 minutos**. Una burbuja entre las placas baja la lectura, y es la causa más común de una
   calibración mal hecha.
7. Registrar al menos **8 lecturas** (mV crudos, ppm y temperatura de la solución) del Monitor Serie.

### 4.3 Cálculo

```
factor = 707 ÷ ppm medido
```

El factor es **multiplicativo**: con un solo patrón se calibra la **pendiente**, no el cero. Eso se
declara así en el documento — no se puede afirmar precisión cerca de 0 ppm con un punto de calibración,
y no se va a inventar.

### 4.4 Cambio en el firmware

La constante se agrega en el bloque de calibración de `main.c`, junto a las del pH, para que todas las
constantes de calibración de este montaje estén en el mismo lugar y se lean de un vistazo:

```c
#define TDS_FACTOR_CORRECCION   1.00f   /* pendiente medida el 2026-10-xx */
```

y se aplica donde se convierte la tensión a ppm, en el ciclo de lectura:

```c
float ppm = sensores_tds_a_ppm((float)mvTDS / 1000.0f, temperaturaSolucion);
if (!isnan(ppm)) ppm *= TDS_FACTOR_CORRECCION;
```

`sensores.c` queda intacto: ahí vive la conversión **del fabricante** —el datasheet—, y en `main.c`
viven los números **de esta sonda**. Mezclarlos haría que después nadie sepa cuál de los dos números
es del datasheet y cuál se midió acá.

### 4.5 Verificación

8. ~~Flashear la versión final y comprobar que la lectura quede en 707 ppm ± 2 %~~ **Hecho**: 707,97 ppm,
   con el error de +0,14 %, dentro del margen previsto.
9. Falta la comprobación de coherencia en el tanque: devolver la sonda a la solución nutritiva y
   comparar el valor con el que informaba antes de la corrección. Queda pendiente para la próxima
   sesión con el módulo sobre el cultivo.

## 5. Evidencia que queda

| Archivo | Contenido |
|---|---|
| `hardware/evidencias/calibracion-del-tds-2026-10-06.txt` | La nota de calibración: procedimiento, las 30 lecturas, el factor, la verificación y las dos interpretaciones del error |
| `hardware/evidencias/calibracion-del-tds-2026-10-06-registro-serie.txt` | Volcado crudo del Monitor Serie con las 30 lecturas antes de corregir |
| `hardware/evidencias/calibracion-del-tds-2026-10-06-verificacion.txt` | Volcado crudo de la verificación: 707,97 ppm |
| `hardware/evidencias/patrones-hanna-recibidos-2026-10-06.png` | Foto de los dos reactivos, con su código y su valor certificado |

## 6. Lugares que decían que el TDS estaba pendiente — ya actualizados

| Archivo | Qué decía | Estado |
|---|---|---|
| `hardware/firmware/LEEME.md` | El TDS con la conversión del fabricante | Actualizado |
| `docs/TABLERO.md` | TDS en el backlog, sin calibrar | Actualizado: T-32 pasó a «Hecho» (Semana 5, 06/10) y el backlog quedó vacío |
| `docs/28_MAPA_DEL_REPOSITORIO_PARA_LA_DEFENSA.md` | Pendiente de calibración | Actualizado |
| `docs/17_GUION_DE_LA_DEMOSTRACION.md` | Se declaraba como límite en la defensa | Actualizado: ahora el límite declarado es que la calibración es de pendiente con un solo punto |
| `docs/30_PLAN_DE_LA_SEMANA_E4.md` | Tarea de la semana y riesgo abierto | Actualizado: el riesgo quedó cerrado |
| `docs/35_GUIA_PARA_ENTENDER_EL_CODIGO.md` | Pregunta de defensa: por qué el TDS no está calibrado | Actualizado, con las líneas nuevas del código |
| `Santos_Freddy_E4.docx` | Estado de la calibración | **Pendiente de actualizar**: es el entregable |

También se corrigió, de paso, una afirmación que había quedado vieja en `docs/35`: decía que el índice
`alertas(modulo_id, timestamp)` faltaba y que la consulta devolvía error del servidor, cuando ya está
declarado en `firestore.indexes.json` (líneas 36-43) y desplegado.

## 7. Lo que este resultado permite afirmar, y lo que no

**Sí:** que la sonda, contrastada contra un patrón trazable a NIST, entregaba un valor un 6,7 % alto, y
que después de aplicar el factor el módulo informa 707,97 ppm donde el patrón vale 707. Que el montaje
es repetible: 30 lecturas dentro de un recorrido del 0,6 %, con el firmware informando «señal estable».

**No:** que el instrumento tenga precisión absoluta en todo el rango. Con un único punto de calibración
se corrige la **pendiente**; el cero no está verificado, así que cerca de 0 ppm no se afirma nada. Y no
se atribuye el error a una causa física concreta —sonda, amplificador o convertidor—, porque un solo
punto no permite distinguirlas: se aplica como corrección de pendiente, que es el método del propio
fabricante del módulo.
