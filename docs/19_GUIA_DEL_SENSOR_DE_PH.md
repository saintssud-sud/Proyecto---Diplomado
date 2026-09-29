# Guía del sensor de pH — para llevar

**Para qué es esta hoja:** para comprar lo correcto y para tratar bien el electrodo.
Resume lo acordado en el plan de la semana (`18_PLAN_DE_LA_SEMANA.md`).

---

## 1. Qué comprar y cómo pedirlo

| Qué | Cómo pedirlo en la tienda | Nota |
|---|---|---|
| Solución de almacenamiento | «¿Tienen **solución de almacenamiento 3 M KCl** o *storage solution* para electrodos de pH?» | Con **100 ml** sobra para todo |
| Patrones de pH | «¿Tienen **soluciones patrón de pH 4,00 y 6,86**?» | **Imprescindibles**: sin ellos no hay calibración |
| Patrón de TDS | «¿Tienen **patrón de 707 ppm** para TDS?» | Para calibrar el TDS (T-32) |
| Agua destilada | farmacia o supermercado | Solo para **enjuagar**. Medio litro basta |
| Cloruro de potasio en polvo | «¿Tienen **cloruro de potasio p.a.** o para análisis?» | Solo si no hay solución preparada. Con **25 g** sobra |

**Dónde buscar, en orden:**

1. **La tienda donde compraste el sensor** (electrónica, robótica o hidroponía). Es lo más
   probable, y muchas veces venden un **kit** con los patrones y el KCl juntos.
2. **Los laboratorios de la universidad** (química, agronomía, suelos). Suele ser lo más
   rápido y gratis, y pueden tener también los patrones.
3. **Droguerías y casas de reactivos químicos** de la ciudad.
4. **Farmacia**, para el agua destilada y, si acaso, el cloruro de potasio en polvo.

---

## 2. Las tres reglas de oro

1. **Se guarda en KCl, se enjuaga con agua destilada.**
2. **Nunca** dejar la sonda sumergida en agua destilada: le roba las sales de dentro y la
   arruina.
3. Al sacarla de un líquido, **enjuagar con agua destilada y sacudir las gotas**. No frotar
   el vidrio con papel ni con los dedos.

---

## 3. Recuperación del electrodo, paso a paso

- [ ] **Paso 1.** Enjuagar el bulbo con agua destilada y sacudir las gotas. No frotar.
- [ ] **Paso 2.** Sumergir el bulbo **2 o 3 cm** en **KCl 3 M**.
      Si todavía no hay KCl, usar **patrón de pH 4,00** (sirve como remojo de emergencia).
- [ ] **Paso 3.** Dejarlo **24 a 48 horas** a temperatura ambiente, quieto y tapado del polvo.
- [ ] **Paso 4.** Sacarlo y enjuagar con agua destilada; sacudir las gotas.
- [ ] **Paso 5.** Medir en el patrón de 4,00 y en el de 6,86, y **anotar las dos tensiones**
      en la tabla del apartado 6.

---

### 3.2 El divisor ÷2 que hay que armar antes de medir

La placa PH-4502C se alimenta a **5 V** y su salida `Po` puede acercarse a esa tensión, mientras
que el ESP32 tolera **3,3 V** en sus entradas. Entre `Po` y el pin `SVP` (GPIO 36) va un divisor
con dos resistencias iguales de 4,7 kΩ:

```
Po (PH-4502C) ---[ 4,7 kΩ ]---+--- SVP (GPIO 36)
                              |
                          [ 4,7 kΩ ]
                              |
                             GND
```

El punto del medio es el **nodo**: ahí se juntan la primera resistencia, la segunda y el cable al
`SVP`, los tres en el mismo punto. La masa tiene que ser común a la placa del pH y al ESP32.

**Va del lado que va al ESP32, no del lado de la sonda.** El electrodo se enchufa al BNC y su
señal la acondiciona la propia placa; lo que hay que bajar es la salida de la placa antes de que
entre al microcontrolador:

```
[electrodo] ──BNC──> [placa PH-4502C] ──PO──> [divisor] ──> SVP · GPIO 36
   lado de la sonda                                ↑
                                    acá va el divisor: del lado del ESP32
```

Del lado del BNC no se suelda nada. Y el divisor no tiene que quedar pegado al pin del conector:
sirve en cualquier punto del cable que va de `PO` al `GPIO 36`, siempre que la pata de la segunda
resistencia llegue al `GND` de la placa y ese `GND` sea el mismo del ESP32.

Comprobación con el multímetro **antes de conectar**: entre `Po` y `GND` debe dar unos 9,4 kΩ
(las dos resistencias en serie), entre el nodo y `GND` unos 4,7 kΩ, y con el módulo encendido y el
electrodo en el patrón, el nodo debe dar **la mitad** de lo que hay en `Po`.

El procedimiento dibujado, con los siete pasos y la tabla de comprobaciones, está en
`Figuras/23-divisor-ph.png`, y el lugar físico donde va sobre la placa, con el orden real de los
seis pines del conector (`TO · DO · PO · GND · GND · VCC`), en `Figuras/24-divisor-ph-donde.png`.
El divisor se arma **del lado del conector de 6 pines**, entre `PO` y uno de los dos `GND`; el
BNC de la derecha es solo para enchufar el electrodo y de ese lado no se suelda nada.

---

## 4. La prueba que decide

El electrodo sirve si cumple **las cuatro**:

| Comprobación | Cómo se nota |
|---|---|
| Lectura estable | No se va más de 0,1 pH por minuto |
| Repetible | Al volver al mismo patrón, da el mismo número |
| Diferencia clara entre patrones | El 4,00 y el 6,86 se distinguen sin duda y en el orden correcto |
| Tercera referencia | Tras calibrar, el agua de la llave o un patrón de 9,18 da menos de ±0,3 pH de error |

**Si falla alguna:** el electrodo no sirve para el proyecto y hay que comprar uno nuevo el
mismo día. Si venden la sonda sola, esa es la compra; si no, el kit completo.

### 4.1 Cuándo se revisa y qué número se espera

El remojo empezó el **lunes 28/09 a las 19:52** en patrón de pH 4,00. De ahí salen los dos
momentos:

| Momento | Cuándo | Qué se hace |
|---|---|---|
| Las 24 horas | martes 29/09 a las 19:52 | Revisión rápida: que el bulbo esté húmedo y brillante y la lectura quieta. Todavía no se decide nada |
| Las 48 horas | miércoles 30/09 a las 19:52 | Prueba de los dos patrones y **decisión**: si no revive, se compra la sonda el mismo día |

**Qué número se espera.** Un electrodo sano entrega unos **59 mV por unidad de pH** a 25 °C, así
que entre el patrón de 4,00 y el de 6,86 la diferencia debe rondar los **168 mV**, y el patrón de
4,00 es el que da la tensión **más alta**. No hace falta que dé exacto, pero sí que la diferencia
sea del orden de los cientos de mV y en ese sentido.

Si la diferencia es de unas decenas de mV, si sale invertida, o si el valor se mueve solo, la
membrana no revivió: por más horas de remojo no va a mejorar, y la compra es la salida.

Dos advertencias sobre ese número:

- Si el **divisor de tensión** (las dos resistencias de 4,7 kΩ) ya está armado, todas las
  tensiones se ven a la mitad. Lo que se compara es la **diferencia por unidad de pH**, no el
  valor absoluto.
- La placa PH-4502C puede amplificar la señal del electrodo. Si amplifica, la diferencia será
  proporcionalmente mayor, y eso no es mejor señal: el criterio que manda sigue siendo la
  calibración con los tres patrones.

**Mientras se espera, no tocar nada:** el electrodo quieto, tapado, lejos del sol y del calor, y
sin cambiarle el líquido. El agua desionizada sirve para enjuagar, nunca para guardarlo.

---

## 5. Cómo guardarlo desde ahora

- Después de **cada** medición: enjuagar con agua destilada, sacudir, y poner el tapón **con
  KCl dentro**.
- Revisar de vez en cuando que el tapón siga teniendo líquido: si se seca, vuelve a empezar
  el problema.
- Si va a estar semanas sin usarse: guardarlo **vertical, con el tapón lleno de KCl**.

---

## 6. Tabla para anotar las medidas

Estos datos son los que después van al apartado 2.8 como evidencia de la calibración.

| Fecha | Tensión en patrón 4,00 (mV) | Tensión en patrón 6,86 (mV) | Temperatura (°C) | Observaciones |
|---|---|---|---|---|
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

---

## 7. Lo que NO hay que comprar ni hacer

- **Fertilizante agrícola de cloruro de potasio** (el saco de 50 kg, etiquetado 0-0-60): es la
  misma sal, pero con impurezas y colorantes que obstruyen la unión del electrodo.
- **Sal dietética de cocina** («sal sin sodio») para preparar la solución: lleva aditivos.
- **Guardar la sonda seca** o sumergida en agua destilada.
- **Forzar el tapón** ni meter nada por las ranuras de la jaula negra del bulbo.
- **Comprar una sonda nueva antes de la prueba**, salvo que el vidrio esté partido.
