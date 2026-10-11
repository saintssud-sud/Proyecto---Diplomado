# Anexo H · Inventario de dispositivos y materiales

Este anexo reúne **todo lo que compone el sistema por el lado del hardware**: los dispositivos
del módulo de adquisición, los materiales con los que se calibró y verificó, los elementos de
la maqueta hidropónica, las herramientas y consumibles empleados, y los servicios que sostienen
la solución. Se distingue en cada caso **lo que ya está en uso y verificado** de **lo que queda
por adquirir o por montar**, con la fecha en que se incorporó cuando corresponde.

**Fecha de actualización:** 11 de octubre de 2026.

**Sobre la columna de costo.** El costo se informa en bolivianos y corresponde al
precio de adquisición de cada elemento; queda a completar por el autor. Los servicios
de la sección H.5 operan en capas gratuitas y por eso no tienen costo.

**Cómo leer el estado de cada elemento:**

| Estado | Significado |
| --- | --- |
| **En uso** | Está montado y funcionando en el módulo o en el sistema |
| **Verificado** | Se usó en los ensayos o en la calibración, con evidencia fechada |
| **Por adquirir** | Falta conseguirlo para completar la maqueta |
| **Reserva** | Se tiene, pero no forma parte del montaje; queda como repuesto |
| **Fuera de alcance** | Se evaluó y se decidió no usarlo, con su justificación |

---

## H.1 Dispositivos del módulo de adquisición

| Elemento | Modelo o especificación | Cant. | Función en el sistema | Conexión | Estado | Costo (Bs) |
| --- | --- | --- | --- | --- | --- | --- |
| Microcontrolador | **ESP32-WROOM-32**, módulo de 38 pines | 1 | Ejecuta el firmware: lee los sensores y publica las seis variables | — | En uso |  |
| Placa de expansión | Placa con conector de barril DC 6,5–16 V, USB-C y micro-USB, puente 3,3 V/5 V y cabecera rotulada (`SVP`, `SVN`, `P32`, `P33`, `5V`, `GND`) | 1 | Alimenta y ordena el conexionado; sus rótulos definen el mapa de pines | — | En uso |  |
| Acondicionador de pH | **PH-4502C**, con electrodo de pH de conector **BNC** y capuchón de conservación | 1 | Mide el pH de la solución nutritiva | Salida `Po` → `SVP` (GPIO 36) con divisor ÷2 | En uso |  |
| Sonda de sólidos disueltos | **TDS Meter V1.0**, con sonda de dos electrodos | 1 | Mide los sólidos disueltos totales en ppm; de ahí se deriva la conductividad eléctrica | Salida `AOUT` → `SVN` (GPIO 39) | En uso |  |
| Sonda de temperatura de la solución | **DS18B20** sumergible, punta de acero inoxidable, bus OneWire, resolución 12 bits (0,0625 °C) | 1 | Mide la temperatura del agua; es también la que aporta la compensación por temperatura del TDS | Datos → `P32` (GPIO 32), con resistencia de pull-up a 3,3 V | En uso |  |
| Sensor de ambiente | **AM2302 (DHT22)**, con cable de tres hilos; ±0,5 °C y ±2 % HR | 1 | Mide temperatura ambiental y humedad relativa: cubre dos variables | Datos → `P33` (GPIO 33) | En uso |  |
| Resistencia de pull-up del sensor de ambiente | **10 kΩ** entre el hilo de datos y 3,3 V | 1 | Sin ella el AM2302 con cable no entrega lecturas | Sobre el hilo de datos del `P33` | En uso |  |
| Divisor de tensión del pH | **Dos resistencias iguales** (del orden de 4,7 a 22 kΩ) | 2 | Baja la salida del PH-4502C —que puede superar los 3,3 V— a la tensión que admite el ESP32 | Entre `Po` y `SVP`, con la segunda a masa | En uso |  |
| Sensor de ambiente (reserva) | **DHT11** en plaqueta de tres pines (o DHT22 en plaqueta, ver H.4) | 1 | Sensor de pruebas: se enchufa sin agregar resistencia. Menos preciso (±2 °C, ±5 % HR) y se satura por encima del 90 % de humedad | `P33`, misma conexión | Reserva |  |
| Sensor de distancia ultrasónico | **HC-SR04** | 1 | Se evaluó para medir el nivel del depósito. Su salida `Echo` es de 5 V y exigiría un divisor; la variable de nivel quedó fuera del alcance | — | Fuera de alcance |  |
| Sonda de temperatura de sustrato | Sonda **NTC** de termostato comercial (identificada el 23/09) | 1 | Mide la temperatura del suelo, que no es una de las seis variables; al ser resistiva exigiría su propia curva de calibración | — | Fuera de alcance |  |

**Las seis variables del sistema quedan cubiertas** con los cinco dispositivos en uso: el
PH-4502C aporta el pH; el TDS Meter, los sólidos disueltos y —por la relación
`EC ≈ TDS ÷ 500`— la conductividad eléctrica; el DS18B20, la temperatura de la solución; y el
AM2302, la temperatura ambiental y la humedad relativa.

---

## H.2 Materiales de calibración y verificación

| Elemento | Especificación | Fecha | Para qué se usó | Estado | Costo (Bs) |
| --- | --- | --- | --- | --- | --- |
| Patrón de conductividad | **Hanna HI7031**, 1413 µS/cm | 6 de octubre de 2026 | Calibrar y verificar la sonda de TDS: es el patrón que equivale a 707 ppm | Verificado |  |
| Solución patrón de pH 4,01 | Patrón trazable | 1 y 4 de octubre de 2026 | Primera recta de calibración del electrodo de pH | Verificado |  |
| Solución patrón de pH 6,86 | Patrón trazable | 1 y 4 de octubre de 2026 | Segundo punto de calibración del electrodo de pH | Verificado |  |
| Solución de conservación del electrodo | KCl 3 M (o Hanna HI70300) | Desde el 1 de octubre | Mantener húmedo el bulbo del electrodo entre mediciones; guardarlo seco lo deshidrata y descalibra | En uso |  |
| Agua desionizada | — | Septiembre y octubre | Enjuagar las sondas entre patrones y antes de guardarlas | Verificado |  |
| Alcohol isopropílico | — | 7 de octubre de 2026 | Limpiar la película que se había formado sobre las placas de la sonda de TDS, que causaba una lectura 16 % baja | Verificado |  |
| Recipiente de fondo plano | Vaso o frasco de fondo fino, sin hueco en la base | Octubre | Medir el patrón. Un vaso de fondo grueso con hueco retenía agua y diluía la muestra en un 20 % | Verificado |  |
| Multímetro | Digital | Septiembre y octubre | Verificar las tensiones antes de conectar, y medir el divisor del pH | En uso |  |
| Termómetro de contraste | El propio **AM2302** | 27 de septiembre de 2026 | Contrastar el DS18B20 con el sensor de ambiente: el ensayo se registró como evidencia | Verificado |  |

---

## H.3 Materiales de la maqueta hidropónica

La maqueta es del tipo **NFT** (película nutritiva): un tubo con una pendiente del 3 % por el
que circula la solución, con el depósito abajo. Se arma en interiores, así que el diseño es
compacto y contempla derrames, ruido y polvo de obra.

| Elemento | Medida o especificación | Función | Estado | Costo (Bs) |
| --- | --- | --- | --- | --- |
| Tubos de PVC con orificios | 4 tubos de **90 cm**; el conjunto armado mide 73 a 74 cm de ancho | Canal de cultivo. Alcanza para 20 a 24 sitios | En uso *(a confirmar el diámetro exterior y el de los orificios)* |  |
| Colector y codos | Colector con codos para el retorno | Une los tubos y devuelve la solución al depósito | En uso |  |
| Canastillas | 2 unidades | Sostienen las plantas en los orificios | En uso |  |
| Microtubo con goteros | — | Distribuye la solución en cada sitio de cultivo | En uso |  |
| Manguera corrugada de retorno | 1 m | Devuelve la solución del canal al depósito | En uso |  |
| Bomba sumergible | Bomba de corriente continua con su fuente y conector de barril | Recirculación de la solución. El sistema no la controla: funciona de forma continua o con temporizador | En uso |  |
| Depósito con tapa | **10 a 15 L** (caja plástica o bidón cortado); para interiores, 8 a 12 L | Contiene la solución nutritiva y es donde se sumergen las sondas | Por adquirir |  |
| Estructura de sostén | Listones de madera o una repisa | Sostiene el tubo inclinado | Por adquirir |  |
| Bandeja o cubeta antiderrame | — | Va **debajo** del depósito: protege el piso de la vivienda, que es lo que no se puede dañar | Por adquirir |  |
| Esponja o sustrato inerte | Para las canastillas | Sujeta la planta y mantiene la raíz en la corriente | Por adquirir |  |
| Solución nutritiva A, B y C | Dosis para lechuga | Alimento del cultivo | Por adquirir |  |
| Plántulas de lechuga | 2 a 4 unidades | El cultivo que se monitorea | Por adquirir |  |
| Lámpara LED de cultivo | 20 a 30 W | Solo si el lugar no alcanza las 4 a 6 horas de luz natural que necesita la lechuga | Opcional |  |
| Bomba de aire con piedra difusora | — | Mejora la oxigenación del depósito. Es la pieza más ruidosa: puede funcionar 15 minutos por hora | Opcional |  |
| Caja estanca con prensacables | IP65 | Proteger la electrónica de la humedad del ambiente del cultivo | Por adquirir |  |
| Cargador USB de 5 V | ≥ 2 A, con su cable | Alimentar el conjunto. Conviene usarlo en lugar de la computadora cuando las sondas están en el agua, para evitar lazos de masa | En uso |  |
| Alargador o zapatilla | — | El consumo total del conjunto es del orden de 15 a 20 W | En uso |  |

**Traslado a la defensa.** La maqueta viaja **sin agua**: se vacía el depósito, se desconecta
y se arma de nuevo en el aula en unos cinco minutos. Las sondas de pH y de conductividad viajan
**húmedas**, con su capuchón o en un frasco con solución de conservación.

---

## H.4 Insumos de laboratorio y del banco de pruebas

| Elemento | Especificación | Para qué | Estado | Costo (Bs) |
| --- | --- | --- | --- | --- |
| Protoboard | — | Montar el circuito sin soldar durante las pruebas | En uso |  |
| Cables dupont | Macho-macho y macho-hembra | Conexionado del banco de pruebas | En uso |  |
| Cables USB de datos | — | Cargar el firmware y ver el Monitor Serie | En uso |  |
| Resistencias de 4,7 kΩ | — | Pull-up del bus OneWire del DS18B20 | En uso |  |
| Resistencias de 10 kΩ y 20 kΩ | — | Divisor de tensión del pH y pull-up del AM2302 | En uso |  |
| Soldador y estaño | — | Soldar la resistencia de pull-up del AM2302, documentado con foto en la evidencia | Verificado |  |
| Computadora | Con ESP-IDF v5.5.3 y Flutter instalados | Compilar el firmware y la aplicación | En uso |  |
| Teléfono Android | — | Instalar el archivo instalable y comprobar la aplicación en el móvil | En uso |  |
| Huincha métrica | — | Medir los tubos de la maqueta | En uso |  |
| Bolsas u hojas de plástico | — | Cubrir la maqueta mientras duran los trabajos de albañilería: el polvo de cemento obstruye la bomba y ensucia las sondas | Por adquirir |  |

---

## H.5 Software, plataformas y servicios

No son materiales, pero el sistema no funciona sin ellos: se declaran aquí para que el
inventario esté completo. Todos operan en capas gratuitas, cuyas limitaciones están declaradas
en el apartado 2.9 del documento.

| Elemento | Versión o plan | Función | Estado | Costo (Bs) |
| --- | --- | --- | --- | --- |
| ESP-IDF | v5.5.3 | Entorno de desarrollo del firmware del módulo de adquisición | En uso |  |
| Flutter | Canal estable | Base de código única para la aplicación web y el instalable de Android | En uso |  |
| Python y FastAPI | 3.13 y FastAPI con Pydantic | Servicio de la API con el contrato `/api/v1` | En uso |  |
| Cloud Firestore | Capa gratuita | Base de datos del dominio | En uso |  |
| Firebase Authentication | Capa gratuita | Autenticación y emisión del token de identidad | En uso |  |
| Firebase Hosting | Capa gratuita | Publicación de la aplicación web | En uso |  |
| Render | Capa gratuita | Publicación del servicio de la API | En uso |  |
| GitHub | Repositorio público | Control de versiones, integración continua y monitoreo de disponibilidad | En uso |  |

---

## H.6 Lo que queda por adquirir, en orden de prioridad

| # | Elemento | Para qué | Prioridad | Costo (Bs) |
| --- | --- | --- | --- | --- |
| 1 | Depósito con tapa (10 a 15 L) | Es el recipiente donde viven las sondas y la solución | Alta |  |
| 2 | Solución nutritiva A, B y C | Sin ella no hay cultivo que monitorear | Alta |  |
| 3 | Plántulas de lechuga y esponja | El cultivo del ciclo de demostración | Alta |  |
| 4 | Estructura de sostén del tubo | Sostiene el canal con la pendiente del 3 % | Alta |  |
| 5 | Bandeja antiderrame | Proteger el piso de la vivienda | Media |  |
| 6 | Caja estanca con prensacables | Proteger la electrónica de la humedad | Media |  |
| 7 | Lámpara LED de cultivo | Solo si el lugar no alcanza las horas de luz necesarias | Baja |  |
| 8 | Bomba de aire con difusor | Mejora la oxigenación, a costa de ruido | Baja |  |

---

## H.7 Estado de verificación del hardware

| Ensayo | Fecha | Resultado | Costo (Bs) |
| --- | --- | --- | --- |
| Identificación de cada pieza por foto y etiqueta | 23 de septiembre de 2026 | Doce piezas identificadas; dos quedaron fuera del alcance con su justificación (H.1) |  |
| Contraste del DS18B20 contra el AM2302 | 27 de septiembre de 2026 | Registrado como evidencia en el repositorio |  |
| Divisor de tensión del pH montado y medido | 30 de septiembre de 2026 | Registrado como evidencia |  |
| Calibración del pH | 1 y 4 de octubre de 2026 | Patrones de 4,01 y 6,86 |  |
| Calibración del TDS | 6 de octubre de 2026 | Patrón Hanna HI7031; factor de corrección 0,9373 aplicado en el firmware |  |
| Limpieza de la sonda de TDS y verificación | 7 de octubre de 2026 | Se encontró la causa de un desvío del 16 %: una película sobre las placas. Tras limpiarla, la lectura volvió al valor del patrón |  |

Las bitácoras de cada jornada de trabajo con el hardware están en el repositorio, con los
archivos de evidencia correspondientes.

---

*Este anexo se actualiza a medida que se adquieren o montan los elementos pendientes.*
