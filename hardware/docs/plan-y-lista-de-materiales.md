# Prototipo del módulo de adquisición (ESP32 + cama hidropónica)

**Proyecto:** SI.G.VA.C.H. · **Preparado:** miércoles 23 de septiembre de 2026
**Objetivo:** construir el módulo de adquisición real —el que hoy se sustituye con el
simulador— y conectarlo al servicio publicado.

> **Por qué conviene hacerlo.** El sistema ya está terminado y verificado: aplicación
> publicada, servicio en Render, base de datos con sus reglas y 106 pruebas aprobadas.
> Lo único que quedaba como limitación declarada era el hardware. Construirlo cambia
> tres cosas a la vez: deja de ser una limitación, la defensa se hace con **datos
> reales del cultivo** en lugar de datos generados, y aparece un capítulo nuevo y
> verificable —calibración e integración del módulo— que ninguna otra propuesta del
> grupo va a tener.
>
> Además resuelve la observación **A-4** de la tutoría: el "módulo piloto" dejaría de
> ser una expresión del documento y pasaría a ser la cama hidropónica real, en un lugar
> concreto, con las siete variables medidas allí.

---

## 0. Decisión: maqueta hidropónica ahora, cama de 2,50 m después

Se evaluaron dos formas de montar el módulo:

| | **Maqueta hidropónica** (decisión) | **Cama NFT de 2,50 m** (proyecto futuro) |
|---|---|---|
| **Escala** | Depósito de 10 a 15 L, tubo de 60 cm con 3 o 4 canastillas | Tubos de 2,50 m sobre patas de madera, depósito de 40 L, ~12 plantas |
| **Portabilidad** | ✅ **Se lleva al aula**: la defensa se hace con el sistema midiendo en vivo | ❌ No se traslada: habría que mostrar video y capturas |
| **Tiempo de armado** | Días | Semanas, y exige bomba en marcha permanente |
| **Riesgo** | Bajo: volumen chico, todo controlado | Medio: la bomba es un punto de falla y el cultivo depende de ella |
| **Datos que aporta** | ✅ Reales: se cultiva lechuga y se registra el ciclo completo | Reales, pero más lentos de estabilizar |
| **Para qué sirve** | **El diplomado**: calibración, demostración y datos del ciclo | **El proyecto mayor**, después de graduarse |

**La decisión:** la maqueta para el trabajo del diplomado y la cama grande como
proyecto posterior. Las tres razones que la sostienen:

1. **El firmware y el módulo son los mismos.** El sistema no distingue una maqueta de
   una cama industrial: cambia el identificador del módulo y los rangos del cultivo.
   Lo que se construya y calibre ahora **se traslada tal cual** a la cama de 2,50 m.
2. **La defensa se puede hacer con el sistema funcionando de verdad.** Un módulo
   portátil permite entrar al aula, encenderlo y mostrar el panel actualizándose con
   las lecturas reales; una cama de 2,50 m solo admite fotos y video.
3. **El sistema admite varios módulos.** Se puede registrar la maqueta como un módulo y,
   más adelante, la cama grande como otro, sin rehacer nada.

**Sobre el sistema de la maqueta:** se adopta el **NFT** —tubo de 60 cm, pendiente del
3 % y una bomba pequeña—, que es el mismo principio del video y el sistema que evalúa el
antecedente local. La decisión es única: la maqueta se arma en NFT y no se contempla una
segunda variante de montaje (el detalle, en el apartado siguiente).

### Materiales de la maqueta

| Elemento | Medida sugerida |
|---|---|
| Depósito con tapa | 10 a 15 L (caja plástica o bidón cortado) |
| Tubo de PVC | 60 cm de 75 o 100 mm, con 3 o 4 orificios de 50 mm |
| Canastillas + esponja o sustrato inerte | 4 unidades |
| Bomba sumergible | 200 a 400 L/h, con filtro de malla |
| Manguera de retorno y microtubo de riego | 1 m |
| Bomba de aire + piedra difusora | Opcional, pero mejora el cultivo |
| Solución nutritiva A, B y C | La dosis para lechuga |
| Estructura | Listones de madera o una repisa: solo tiene que sostener el tubo inclinado |

### Ubicación: interior, en una vivienda alquilada

La maqueta se arma **dentro de la casa** (vivienda alquilada, sin patio disponible y con
trabajos de albañilería en el predio). Eso ajusta el diseño y agrega cuatro cuidados:

| Punto | Decisión |
|---|---|
| **Tamaño** | Compacta: depósito de **8 a 12 L** y **2 o 3 plantas**. Entra en una mesa, una repisa o el piso junto a una ventana, y se puede mover si la obra avanza |
| **Luz** | Lechuga necesita de **4 a 6 horas** de luz. Junto a una ventana soleada alcanza; si el lugar es oscuro, una **lámpara LED de cultivo de 20 a 30 W** resuelve el ciclo completo |
| **Ruido** | La bomba sumergible es silenciosa. La **bomba de aire es la que hace ruido**: puede funcionar por intervalos (15 min cada hora) o suprimirse, con el costo de menor oxigenación |
| **Derrames** | Bandeja o cubeta **debajo** del depósito y tapa con orificio para las sondas: protege el piso de la vivienda, que es lo que no se puede dañar |
| **Polvo de obra** | Mientras duren los trabajos, la maqueta se cubre con una bolsa o una caja cuando no se la está mirando; el polvo de cemento obstruye la bomba y ensucia las sondas |
| **Consumo eléctrico** | Alrededor de **15 a 20 W** en total: un alargador o una zapatilla alcanza para la bomba y el cargador del ESP32 |
| **Traslado a la defensa** | El sistema se traslada **sin agua**: se vacía el depósito, se desconecta y se arma de nuevo en el aula en cinco minutos. Las sondas de pH y EC viajan **húmedas**, con la funda o en un frasco con solución |

**Sistema de la maqueta: NFT.** Un tubo de 50 a 60 cm con 2 o 3 canastillas, pendiente
del 3 % y una bomba de 200 L/h: es el sistema del video y el mismo que el antecedente
local comparó contra la raíz flotante. Todo el diseño —el depósito, las sondas, el
conexionado y el firmware— se define sobre esta única variante.

---

## 1. Qué tiene que medir el módulo

El sistema gestiona **siete variables**. La correspondencia con los dispositivos que ya
tenés es la siguiente (a confirmar con las fotos y la hoja de datos de cada placa):

| Variable del sistema | Sensor disponible | Observación |
|---|---|---|
| `temp_ambiental` (temperatura ambiental) | Sensor de temperatura ambiente | Si es un DHT11/DHT22 **también entrega la humedad**: cubre dos variables con una pieza |
| `humedad` (humedad relativa) | El mismo sensor anterior (DHT/SHT) | — |
| `temp_solucion` (temperatura de la solución) | **DS18B20** (sonda de acero inoxidable) | Es el sensor adecuado para el agua: sumergible, digital y preciso. Necesita una resistencia de **4,7 kΩ** |
| `nivel_agua` (nivel de agua) | **Ultrasónico** | Mide la distancia al agua; hay que convertirla a **centímetros de columna** según la geometría del depósito |
| `tds` (sólidos disueltos totales, ppm) | **Sensor TDS** (analógico) | Mide conductividad y la presenta como ppm; requiere **compensación por temperatura**, que aporta el DS18B20 |
| `ec` (conductividad eléctrica, mS/cm) | ⚠️ **No hay sensor de EC aparte** | La EC se **deriva del TDS**: `TDS (ppm) ≈ EC (mS/cm) × 500`. El módulo puede medir el TDS y publicar la EC calculada, o publicar solo el TDS. Hay que decidirlo y documentarlo |
| `ph` | **Sensor de pH** (analógico, con conector BNC) | Es el más delicado: necesita **calibración con soluciones patrón** (4,00 y 6,86) y su electrodo **nunca debe secarse** |

**Conclusión del inventario:** con lo que tenés se cubren **las siete variables**. No
falta ningún sensor; faltan accesorios eléctricos, calibración y la puesta en marcha.

> **El prototipo mide y publica; no acciona nada.** El documento declara fuera de
> alcance el control automático de actuadores (bombas y dosificadores), y el prototipo
> respeta esa decisión: el módulo sensa, envía y el sistema avisa. Eso mantiene la
> coherencia con el alcance aprobado en la tutoría.

---

## 2. Advertencias eléctricas (leer antes de conectar nada)

Son las cinco trampas clásicas de este montaje. Ninguna es difícil, pero las tres
primeras **dañan el ESP32** si se pasan por alto:

| # | Advertencia | Por qué |
|---|---|---|
| 1 | **El ESP32 tolera 3,3 V en sus entradas.** El pH y el TDS trabajan a **5 V** y su salida analógica puede llegar a esa tensión | Conectar 5 V a una entrada del ESP32 lo daña. Hay que usar un **divisor de tensión** (por ejemplo 10 kΩ y 20 kΩ) o alimentar la placa a 3,3 V si su hoja de datos lo permite |
| 2 | **Usar solo entradas analógicas del ADC1** (GPIO 32 a 39) | El **ADC2 no funciona mientras el WiFi está activo**. Es el error más frecuente: el sensor "no lee" y en realidad el canal está ocupado por la radio |
| 3 | **El pin ECHO del ultrasónico** devuelve 5 V si es un **HC-SR04** | Necesita divisor (1 kΩ y 2 kΩ) o un módulo que ya acepte 3,3 V. Si es **JSN-SR04T** (un solo cilindro, impermeable) trabaja mejor sobre una cama húmeda |
| 4 | **El ADC del ESP32 es ruidoso y no lineal** | Se leen 15 a 30 muestras y se toma la **mediana**; después se aplica la recta de calibración de dos puntos |
| 5 | **Masa común obligatoria** | Todos los módulos y el ESP32 comparten GND; sin eso las lecturas son basura |

**Y tres cuidados del montaje:** la electrónica va **fuera** de la cama, en una caja
estanca con prensacables; las sondas de pH y EC **no deben secarse nunca** (se guardan
en la solución o en KCl); y conviene alimentar con un **cargador USB** y no con la
computadora cuando las sondas estén en el agua, para evitar lazos de masa y ruido.

---

## 3. Lo que falta conseguir

| Elemento | Para qué | ¿Imprescindible? |
|---|---|---|
| **Protoboard** y cables dupont (macho-hembra y macho-macho) | Conectar sin soldar | Sí |
| **Resistencia de 4,7 kΩ** | Pull-up del DS18B20 | Sí |
| **Resistencias para divisores** (10 kΩ y 20 kΩ; 1 kΩ y 2 kΩ) | Bajar de 5 V a 3,3 V las señales de pH, TDS y ECHO | Sí |
| **Fuente de 5 V ≥ 2 A** (cargador USB) y cable | Alimentar el conjunto | Sí |
| **Caja estanca (IP65)** y prensacables | Proteger la electrónica de la humedad | Sí |
| **Soluciones de calibración de pH**: 4,00 y 6,86 (o 7,00) | Calibrar el electrodo de pH | Sí |
| **Solución patrón de TDS/EC**: 707 ppm (o 1413 µS/cm) | Calibrar el sensor de TDS | Sí |
| **Agua destilada** y dos recipientes | Enjuagar las sondas entre calibraciones | Sí |
| **Multímetro** | Verificar tensiones antes de conectar | Muy recomendable |
| **Termómetro de referencia** | Contrastar el DS18B20 | Deseable |
| **JSN-SR04T** (ultrasónico impermeable) | Si el que tenés es HC-SR04, mide mejor sobre el agua | Opcional |

---

## 4. Plan por etapas

El calendario está ordenado para que **el E2 del sábado no corra ningún riesgo**: ese
entregable ya está cubierto con el simulador, que entra por el mismo endpoint y con la
misma clave que usará el firmware. El hardware se estrena cuando esté verificado, y su
lugar natural es la defensa del 13/10.

| Etapa | Fechas | Qué se hace | Resultado |
|---|---|---|---|
| **1. Inventario e identificación** | 23 y 24/09 | Fotos de cada placa y de cada etiqueta; se identifican modelos, tensiones y pines | Tabla de conexionado definitiva (sensor → GPIO) y lista exacta de lo que falta |
| **2. Banco de pruebas, sin agua** | 24 y 25/09 | Firmware mínimo: conexión WiFi y lectura de cada sensor por el Monitor Serie | Cada sensor responde y se conoce su escala real |
| **3. Publicación contra el servicio** | 25 y 26/09 | Firmware completo: envío al endpoint con la clave de dispositivo, **reintento y memoria** ante cortes | Las siete variables aparecen en el panel de la aplicación |
| **4. Calibración** | 28/09 al 4/10 | Rectas de calibración de pH y de TDS, contraste del DS18B20, geometría del nivel de agua | Curvas y constantes documentadas (material directo para el Capítulo 2) |
| **5. Instalación en la cama y marcha continua** | 5 al 11/10 | El módulo instalado midiendo de forma sostenida, con las alertas del sistema funcionando | Evidencia para la defensa: fotos, capturas del panel y datos reales del cultivo |
| **6. Documentación** | 11 y 12/10 | Apartado del prototipo: materiales, conexionado, calibración, dificultades y resultados | Capítulo nuevo, verificado y con evidencia propia |

**Recomendación de arranque:** hacer las pruebas **en un balde con solución**, no
directamente en la cama. La calibración y la corrección de errores se hacen mucho mejor
en un recipiente controlado, y la cama se reserva para la instalación definitiva.

---

## 5. Qué necesito para empezar

**Fotos** (con la etiqueta o el serigrafiado visible) de cada pieza. Se guardan en
`Prototipo ESP32/fotos/` y desde ahí las identifico una por una:

1. La placa **ESP32** (interesa leer si dice `ESP32-WROOM-32` y cuántos pines tiene)
2. El sensor de **humedad y temperatura ambiente** (¿DHT11, DHT22, SHT31?)
3. El **ultrasónico** (¿dos cilindros = HC-SR04, o uno solo = JSN-SR04T?)
4. El módulo de **pH** (¿plaqueta con conector BNC redondo?)
5. El módulo de **TDS** (¿plaqueta con sonda de dos placas?)
6. La sonda **DS18B20** (¿cable con tres hilos y punta de acero?)

**Datos que necesito que me confirmes:**

| # | Pregunta |
|---|---|
| 1 | ¿Tenés protoboard, cables dupont, resistencias y multímetro? |
| 2 | ¿Tenés las soluciones de calibración (pH y TDS) o hay que conseguirlas? |
| 3 | ¿La cama hidropónica ya está armada? ¿Qué forma y qué profundidad tiene el depósito? ¿Cuántos litros? |
| 4 | ¿Hay WiFi de 2,4 GHz donde está la cama? (el ESP32 clásico no ve redes de 5 GHz) |
| 5 | ¿Preferís programarlo con **Arduino IDE** (más simple, más tutoriales) o con PlatformIO? |

Con las fotos y esos cinco datos te escribo el **conexionado exacto** (qué pin va a
qué) y el **firmware completo**, comentado línea por línea, para que solo tengas que
cargarlo y ver las lecturas.

---

*Documento de trabajo. Cuando el conexionado esté verificado, este plan pasa al
repositorio como documentación del módulo de adquisición.*
