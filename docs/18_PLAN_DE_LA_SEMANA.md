# Plan de la semana — maqueta y sensor de pH

**Periodo:** lunes 28 de septiembre al viernes 2 de octubre de 2026
**Objetivo de la semana:** dejar la maqueta hidropónica montada y funcionando, con el
módulo de adquisición midiendo **las seis variables** en producción, y con el sensor de
pH recuperado o sustituido y calibrado.

**Tareas del tablero que cierra esta semana:** T-28 (montaje de la maqueta), T-30
(recuperar el electrodo e instalar el divisor ÷2), T-31 (calibrar el pH con los patrones
4,00 y 6,86), T-32 (calibrar el TDS con el patrón de 707 ppm) y T-19 (verificación de
adaptabilidad con capturas en tres anchos).

---

## 1. Punto de partida

**Lo que ya funciona.** El firmware sobre ESP-IDF lee el sensor de ambiente (P33 · GPIO 33),
el DS18B20 de la solución (P32 · GPIO 32) y el TDS (SVN · GPIO 39, sin divisor). Publica
cinco variables en producción: `temp_ambiental`, `humedad`, `temp_solucion`, `tds` y `ec`.

**Lo que falta.** La entrada del pH (SVP · GPIO 36) ya está reservada y el programa la lee,
pero **solo la informa en el monitor serie**: no la convierte a pH ni la publica. Quedan
cuatro cosas encadenadas:

1. que el electrodo vuelva a medir (o comprar uno nuevo);
2. montar el **divisor ÷2** entre la salida `Po` del módulo PH-4502C y el GPIO 36;
3. **calibrar** con los patrones de 4,00 y 6,86, anotando las dos tensiones;
4. añadir al firmware la **conversión de milivoltios a pH** y publicar `ph`.

Es una cadena: si el electrodo no revive, nada de lo demás sirve. Por eso el plan pone la
decisión sobre el electrodo el **miércoles**, para que queden dos días de margen si hay que
comprar.

---

## 2. Recuperar el electrodo de pH

### 2.1 Por qué se secó

**Lo que pasó con este electrodo, según lo confirmado por el autor.** Se usó dos o tres
veces durante las prácticas con Arduino y después se guardó **seco, dentro de su caja, sin
solución de almacenamiento**. Al retomar el trabajo con ESP-IDF ya no respondía: el bulbo se
había secado durante ese tiempo. La caja del proveedor no incluye solución de almacenamiento,
y la costra blanca que se ve dentro del tapón es el KCl de esa solución que se evaporó.

Esto importa para el pronóstico: el electrodo **no tiene desgaste de uso**, solo sequedad.
Es el caso que el remojo revierte con más probabilidad, siempre que el vidrio esté entero.

El bulbo de vidrio y la unión de referencia tienen que estar siempre hidratados. Guardado en
seco, el vidrio pierde la capa de gel que le da sensibilidad y la referencia se obstruye.
La forma correcta de guardarlo es **sumergido en KCl 3 M** (o en la solución de
almacenamiento del fabricante), nunca en seco y **nunca en agua destilada**, que le roba
iones al electrodo.

**Qué es el KCl.** Son las siglas del **cloruro de potasio**, una sal común de laboratorio.
Es el líquido que llevan dentro los electrodos de pH en su parte de referencia, y por eso se
usa también para guardarlos: mantiene húmeda la unión porosa y con la misma concentración
que el interior, de manera que el electrodo no se desequilibra. El «3 M» es la
concentración: tres moles por litro.

**Dónde se consigue.** Se vende ya preparado, y es lo recomendable:

* en las tiendas de electrónica e hidroponía, como **«solución de almacenamiento 3 M KCl»**
  o *«storage solution»*, casi siempre junto a los patrones de calibración;
* en farmacias o casas de reactivos, como **cloruro de potasio** en polvo para prepararlo.

Si se prepara a mano, se disuelven unos **224 gramos de cloruro de potasio puro por litro de
agua destilada**. Tiene que ser reactivo de laboratorio: **no sirve la sal dietética de
cocina**, que lleva aditivos y antiaglomerantes que ensucian la unión del electrodo.

Hace falta muy poca cantidad: con 100 ml hay de sobra para la recuperación y para mantener
el tapón durante meses.

### 2.2 Procedimiento

| Paso | Qué se hace | Cuándo |
|---|---|---|
| 1 | Inspeccionar el bulbo: descartar grietas o rayones. Si está partido, no hay recuperación | lunes |
| 2 | Enjuagar con agua destilada y sacudir las gotas. **No frotar** con papel | lunes |
| 3 | Sumergir el bulbo 2 o 3 cm en **KCl 3 M** entre **24 y 48 horas** | lunes a miércoles |
| 4 | Si todavía no hay KCl, dejar esas horas en **solución patrón de pH 4,00** y pasar a KCl en cuanto llegue | lunes |
| 5 | Enjuagar con agua destilada al sacarlo, sin frotar | miércoles |
| 6 | Medir en las dos soluciones patrón y anotar las tensiones | miércoles |

### 2.3 Cómo saber si quedó inservible

Sirve si, después de las 48 horas, cumple **todo** esto:

* la lectura se mantiene estable (no se va más de 0,1 pH por minuto);
* el valor **vuelve** al mismo número cuando se repite la medida en el mismo patrón;
* la diferencia entre el patrón de 4,00 y el de 6,86 es clara y en el sentido esperado;
* tras calibrar con esos dos puntos, una tercera referencia (agua de la llave o un patrón
  de 9,18) da un error menor de ±0,3 pH.

Si falla cualquiera de los cuatro, el electrodo no sirve para el proyecto y hay que
comprar. Un electrodo agotado suele delatarse porque en el patrón de 7 marca valores
disparatados y tarda minutos en estabilizarse.

### 2.4 Prueba rápida mientras no haya patrones

Solo para saber **si responde algo**, nunca para calibrar: medir en vinagre blanco diluido
(ácido) y luego en una disolución de bicarbonato (básica). La tensión tiene que moverse
varios cientos de milivoltios en menos de un minuto y regresar al mismo valor al volver al
primer líquido. Si no se mueve, está muerto.

### 2.5 El divisor ÷2 que pide la tarea T-30

El módulo PH-4502C se alimenta a **5 V** y su salida `Po` puede acercarse a ese valor, por
encima de lo que aguanta el convertidor del ESP32. Se intercala un divisor con **dos
resistencias iguales de 4,7 kΩ** —las que ya hay en el equipo—, que parte la tensión a la
mitad:

```
   Po (módulo pH) ---[ 4,7 kΩ ]---+---[ 4,7 kΩ ]--- GND
                                  |
                                  +--- SVP · GPIO 36
```

Puntos a tener en cuenta:

* El módulo se alimenta a **5 V**, no a 3,3 V: a 3,3 V el electrodo no trabaja bien.
* Las masas del módulo y del ESP32 van **unidas**.
* El GPIO 36 es de solo entrada y pertenece al ADC1, que es el correcto: el ADC2 no se
  puede usar mientras el WiFi está activo.
* Si hay un condensador de 100 nF a mano, ponerlo entre el punto medio y GND estabiliza la
  lectura. El programa ya informa la dispersión, que sirve para saber si la señal es de
  fiar o es ruido.
* Conviene medir con multímetro la tensión en `Po` y en el punto medio antes de conectar el
  ESP32, para no arriesgar el pin.

### 2.6 Registro del remojo (en curso)

**En marcha desde el lunes 28 de septiembre de 2026 a las 19:52.**

| Dato | Valor |
|---|---|
| Inicio del remojo | **lunes 28/09/2026, 19:52** |
| Patrón usado | **4,01** (sobre de polvo en 250 ml de agua desionizada) |
| Recipiente | Vaso estrecho de vidrio, cubierto con la jarra medidora invertida |
| KCl | **No se consiguió** el lunes; se sigue buscando en el laboratorio y las droguerías |

**Puntos de control:**

| Momento | Fecha y hora | Qué toca | Resultado |
|---|---|---|---|
| +24 h | martes 29/09, 19:52 | Enjuagar con agua desionizada y **revisar el estado del bulbo** | *(por anotar)* |
| +48 h | miércoles 30/09, 19:52 | **Medir en los patrones 4,01 y 6,86** y decidir si revive | *(por anotar)* |

> **Lo que hay que dejar listo para el miércoles.** La decisión no depende solo del electrodo:
> hace falta el **divisor ÷2 montado** (dos resistencias de 4,7 kΩ entre la salida `Po` del
> módulo PH-4502C y el GPIO 36) y el módulo alimentado a 5 V. Conviene armarlo el **martes**,
> para que el miércoles solo sea medir.

---

## 3. Lista de compras

Precios a consultar salvo los dos del sensor, que ya están en las capturas.

| Qué | Para qué | Prioridad |
|---|---|---|
| KCl 3 M o solución de almacenamiento | recuperar y **guardar** el electrodo | alta, el lunes |
| ~~Solución patrón pH 4,00 y 6,86~~ | calibrar el pH (T-31) | **ya se tienen**: sobres de polvo de pH **4,01**, **6,86** y **9,18** (250 ml cada uno), aparecidos el domingo |
| Agua destilada | disolver los patrones (750 ml) y enjuagar el electrodo | alta, el lunes |
| Solución patrón de 707 ppm | calibrar el TDS (T-32) | media |
| Depósito de 5 a 10 litros, opaco o con tapa | la solución del cultivo | alta, el lunes |
| Tabla o bandeja de apoyo (madera o plástico) | montar la electrónica | alta |
| Sonda BNC de pH sola | **solo si el electrodo no revive** | decisión del miércoles |
| Kit de pH: 280 Bs (SEN-73, ARDUNEL, dice «consulta stock») o 320 Bs (SEN-090, disponible) | si no venden la sonda sola | decisión del miércoles |

> **Sobre los patrones que aparecieron.** Son sobres de polvo: cada uno se disuelve en
> **250 ml de agua destilada** y da una solución de pH exacto a 25 °C. Se preparan en un
> recipiente limpio, se guardan cerrados y etiquetados con su pH, y **no se reutilizan**:
> para calibrar se echa un poco en un vaso aparte y lo usado se descarta, porque el
> electrodo contamina lo que toca. El de 9,18 es el que más se degrada con el aire, así que
> conviene prepararlo el mismo día que se use.
>
> Además, el patrón de **4,01** sirve como **remojo de emergencia** del electrodo si el KCl
> no aparece el lunes (ver el apartado 2.2).

**Conviene preguntar por WhatsApp a las dos tiendas el lunes temprano**, en un solo
mensaje, por: KCl o solución de almacenamiento, patrón de 707 ppm, sonda BNC sola, y si el
kit de 280 Bs tiene stock. Los patrones de pH **ya no hacen falta**: aparecieron el domingo.
Comprar todo en un viaje ahorra dos días.

**Sobre la compra del sensor:** si el electrodo no revive, primero preguntar si venden **la
sonda sola**. El módulo PH-4502C probablemente siga bueno, y la sonda suelta tiene que ser
más barata que el kit. Si no la venden suelta: el de 320 Bs aparece con botón de compra, y
el de 280 Bs dice «consulta stock», así que la disponibilidad decide.

---

## 4. La maqueta

### 4.1 Qué debe quedar montado

| Elemento | Dónde va |
|---|---|
| ESP32 con el firmware | sobre la tabla, con el puerto USB accesible |
| Sensor de ambiente AM2302 | fuera del agua, a la altura de la planta |
| DS18B20 con su resistencia de 4,7 kΩ | dentro de la solución |
| Sonda de TDS | dentro de la solución, sin tocar el fondo |
| Sonda de pH con el divisor ÷2 | dentro de la solución, junto a las anteriores |
| Depósito con la solución | en la base, con tapa para que no le dé la luz |

### 4.2 Montaje, en orden

1. Fijar el ESP32 y los módulos a la tabla, dejando el USB a mano.
2. Cablear según el mapa de pines que documenta el propio firmware:
   P33 ambiente · P32 DS18B20 · SVP GPIO 36 (pH, tras el divisor) · SVN GPIO 39 (TDS).
3. Sujetar las sondas con ventosas o espuma, sumergidas de 2 a 4 cm, sin tocarse entre
   ellas ni el fondo del depósito.
4. Llenar con la solución y encender.
5. Comprobar en el monitor serie las variables, y en la aplicación que las lecturas llegan.
6. Mover algo real (añadir agua, disolver nutriente) y ver que los valores cambian: eso es
   lo que demuestra que mide de verdad.
7. Ordenar los cables, etiquetar cada sonda y proteger la electrónica de salpicaduras.

---

## 5. Semana, día por día

### Lunes 28

- **Mensaje a las dos tiendas** con la lista de compras (sección 3) y comprar el mismo día
  lo que haya.
- **Arrancar la recuperación del electrodo (T-30):** enjuagar y sumergir en KCl 3 M, o en
  patrón de pH 4,00 si el KCl todavía no llegó. Queda ahí 24 a 48 horas.
- Comprar el depósito y la tabla de apoyo.
- Montar la electrónica sobre la tabla y cablear el DS18B20 (con su resistencia de 4,7 kΩ)
  y el TDS. El pH se deja para el miércoles.
- **Actualizar el tablero:** mover T-29 (entregable E2) a «Hecho», porque ya se subió al
  aula virtual el sábado 26, y pasar T-30 y T-28 a «En curso».

### Martes 29

- **Primera comprobación del electrodo** a las 24 horas: enjuagar y hacer la prueba rápida
  de respuesta (sección 2.4). Anotar el resultado.
- Armar el **divisor ÷2** con las dos resistencias de 4,7 kΩ y comprobar con multímetro la
  tensión en `Po` y en el punto medio, antes de conectar el GPIO 36.
- Montar las sondas de TDS y DS18B20 en el depósito y verificar que las cinco variables
  siguen llegando a la aplicación con la sonda ya dentro del agua.
- Fotografiar el montaje: vista general, detalle del cableado y monitor serie.

### Miércoles 30 — día de decisión

- **Decisión sobre el electrodo**, a las 48 horas de remojo, con los cuatro criterios de la
  sección 2.3:
  * **revive** → seguir con el montaje y dejarlo listo para calibrar el jueves;
  * **no revive** → comprar ese mismo día (sonda sola si la venden; si no, el kit de 320 Bs
    o el de 280 Bs si tiene stock). La compra no se puede dejar para el jueves.
- **Calibrar el TDS con el patrón de 707 ppm (T-32)** y anotar la tensión obtenida.
- Si llega la sonda nueva: enjuagarla, comprobar que responde y guardarla en KCl.

### Jueves 1

- **Calibrar el pH (T-31)** con los patrones de 4,00 y 6,86: anotar las **dos tensiones**,
  ajustar los potenciómetros del módulo y verificar con una tercera referencia.
- **Cerrar el firmware:** añadir la conversión de milivoltios a pH con las dos constantes
  medidas y publicar la variable `ph`. Con eso el módulo queda publicando **seis**
  variables, que es el objetivo de la semana.
- Ensayo completo de punta a punta: solución → servicio → aplicación.

### Viernes 2

- Remates de la maqueta: cables ordenados, etiquetas, protección, sondas limpias y el
  electrodo guardado en KCl (con su tapón lleno: es lo que evita que se seque otra vez).
- **Evidencias para el E3:** fotos y vídeos cortos del montaje, del proceso de calibración
  con los patrones y de la aplicación mostrando las seis variables.
- **T-19:** capturas de adaptabilidad en los tres anchos (320, 768 y 1920 px).
- Actualizar tablero, README y el apartado de calibración (2.8) con las tensiones medidas.
- Confirmar con `git` que la clave del dispositivo sigue fuera del repositorio y hacer el
  envío de los cambios.
- Ensayar la demostración con la maqueta real como protagonista.

---

## 6. Riesgos y qué hacer

| Riesgo | Prevención |
|---|---|
| El electrodo no revive | decisión el miércoles, no el viernes; preguntar el lunes si venden la sonda sola |
| No hay patrones de pH en las tiendas | pedirlos el lunes; sin patrones **no** se puede presentar el pH como medido, solo como pendiente |
| El kit de 280 Bs no tiene stock | el de 320 Bs aparece disponible; decidir por disponibilidad, no por precio |
| La salida del módulo se sale del rango del ADC | comprobar con multímetro antes de conectar; el divisor ÷2 es obligatorio |
| El servicio tarda en responder en la demostración | abrir la dirección dos minutos antes: la capa gratuita se duerme por inactividad |
| El navegador bloquea la conexión | usar Chrome o Firefox para la demostración, no Brave con escudos |

---

## 7. Cómo sabremos que la semana salió bien

- El electrodo mide y está calibrado con dos patrones, o hay uno nuevo comprado y calibrado.
- El módulo publica **seis** variables en producción y la aplicación las muestra.
- La maqueta está montada, ordenada y con las sondas dentro de la solución.
- Hay evidencias fotográficas del montaje y del proceso de calibración.
- Las tarjetas T-28, T-30, T-31 y T-32 están en «Hecho» y T-19 también.
- La clave del dispositivo y la red WiFi siguen fuera del repositorio.
