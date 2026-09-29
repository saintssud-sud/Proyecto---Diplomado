# El pH, paso a paso (versión simple)

Esto es solo preparación para la prueba de mañana. El pH todavía no se publica ni se usa en la
entrega, así que **no hay apuro y nada se puede arruinar**.

Solo hay cuatro cosas que hacer. Ninguna es nueva: es soldar como con el AM2302 y enchufar cables.

---

## Lo único que NO se puede hacer

**El cable amarillo no va directo al ESP32.** Tiene que pasar por las dos resistencias.

Si lo conectás directo, la placa del pH puede entregar más de 3,3 V y el ESP32 no lo tolera.
Todo lo demás se puede probar sin miedo.

---

## Paso 1 · Los dos cables fáciles

| Cable | Pin de la placa de expansión |
|---|---|
| Rojo | el que dice `5V` |
| Negro | el que dice `GND` |

Es como una lámpara: uno va y el otro vuelve. Nada más. En este paso no puede pasar nada malo.

**Probá:** ¿nada se calienta? Listo, paso 1 terminado.

---

## Paso 2 · Las dos resistencias, en el cable amarillo

El amarillo sale del pin `Po` de la placa del pH. En ese cable van las dos resistencias, así:

```
amarillo ──[ resistencia ]── PUNTO MEDIO ──[ resistencia ]── negro (GND)
                                   │
                                   └── cable nuevo que va al ESP32
```

Cómo se hace, con el soldador:

**Ojo: el cable amarillo se corta.** No es como el AM2302, donde pelábamos una ventana y la
resistencia quedaba al costado. Acá la primera resistencia va **en el medio del camino**: si le
pelás una ventana y soldás ahí la pata, el cable puentea la resistencia y el divisor no hace nada.

1. **Cortá el cable amarillo** a unos 10 cm del conector. Quedan dos pedazos: el que viene de la
   placa del pH y el que sigue hacia el ESP32.
2. Soldá una resistencia **entre los dos pedazos**: una pata a cada lado. Es la misma soldadura que
   hiciste en el AM2302, solo que ahora el cable va cortado.
3. La pata de la derecha de esa resistencia es el **punto medio**. Ahí vas a soldar dos cosas más:
   la segunda resistencia y el cable nuevo que va al ESP32.
4. La segunda resistencia va del punto medio al cable **negro**. Al negro no se le corta nada: se
   le pela una ventana de 3 mm y ahí se suelda la pata.

**El punto medio es un solo punto:** ahí se juntan tres cosas, la primera resistencia, la segunda
y el cable que va al ESP32.

El dibujo de estos tres pasos está en `Figuras/25-divisor-cable-a-cable.png`.

---

## Paso 3 · El cable del punto medio al ESP32

El cable que sale del punto medio va al pin que dice **`SVP`** de la placa de expansión.

Los otros dos (el rojo y el negro del paso 1) no se tocan: ya están puestos.

---

## Paso 4 · Medir antes de encender

Con el multímetro, tres números:

| Qué se mide | Qué tiene que dar |
|---|---|
| Amarillo contra negro | alrededor de **9,4 kΩ** |
| Punto medio contra negro | alrededor de **4,7 kΩ** |
| Con todo encendido: punto medio y amarillo | el punto medio da **la mitad** de lo que da el amarillo |

Si esos tres números salen bien, el divisor quedó armado y se puede enchufar el `SVP`.

Si el primero da `1`, `OL` o nada, hay una soldadura floja: se recalienta y se agrega estaño.

---

## Si algo no cuadra

**No adivines.** Sacá una foto y anotá el número que dio el multímetro, y lo revisamos juntos.

---

## Glosario de las palabras raras de las otras guías

| Palabra | Qué es, en simple |
|---|---|
| **Divisor** | Las dos resistencias que bajan la tensión a la mitad |
| **Nodo** | El punto medio entre las dos resistencias, de donde sale el cable al ESP32 |
| **`Po`** | El pin de la placa del pH por donde sale la medición |
| **`SVP`** | El pin del ESP32 por donde entra esa medición (es el GPIO 36) |
| **`V+` o `U+`** | El pin de alimentación de la placa del pH: va al `5V` |
| **`G`** | Masa: va al `GND` |
| **`To` y `Do`** | Pines que no se usan, se dejan al aire |
| **kΩ** | Kiloohmio: la unidad con la que se miden las resistencias |
