# 📓 Bitácora — Sesión del domingo 27 de septiembre de 2026

**Proyecto:** SIGVACH — Sistema de Gestión de Variables para Cultivos Hidropónicos
**Grupo:** 3 · **Entrega E2:** sábado 26/09 (entregada) · **Defensa:** martes 13/10 a las 17:00
**Objetivo de la sesión:** cerrar los flecos de la entrega del E2, verificar que lo
publicado funciona de verdad y volver a poner en marcha el módulo de adquisición.

---

## 1. Punto de partida

| Pieza | Estado al comenzar |
|---|---|
| Entregable E2 | **Entregado** el sábado 26 a las 00:52, 23 horas antes del cierre |
| Cuestionario Q2 | **Completado** el mismo día |
| Aplicación publicada | En línea, pero con dudas sobre qué versión estaba sirviendo |
| Módulo de adquisición | **Apagado desde el 25/09 a las 04:45**, sin publicar |
| Electrodo de pH | Guardado seco, sin medir desde las prácticas con Arduino |
| Repositorio | 125 confirmaciones en 13 días distintos |

---

## 2. El fallo del despliegue: la aplicación publicada apuntaba al equipo local

### 2.1 El síntoma

Abriendo la dirección publicada, la aplicación mostraba «No se pudo conectar con el
servidor», mientras que el servicio respondía con normalidad y desde el mismo equipo se
podía abrir `https://sigvach-api.onrender.com/api/v1/salud` y obtener
`{"estado":"ok",...}`.

### 2.2 Cómo se encontró la causa

Se comparó el paquete que sirve Firebase con el que había en el equipo:

| Archivo | Tamaño | Huella SHA-256 |
|---|---|---|
| `build/web/main.dart.js` (local) | 3.128.379 bytes | `5A26E5E5…C603DA` |
| `main.dart.js` (publicado) | 3.128.379 bytes | `5A26E5E5…C603DA` |

**Eran el mismo archivo.** Y dentro de él:

| Dirección buscada | Apariciones |
|---|---|
| `sigvach-api.onrender.com` | **0** |
| `127.0.0.1:8011` | 1 |

La aplicación publicada le pedía los datos a `127.0.0.1`, que significa «este equipo»: el
de quien esté mirando la página. En el equipo del autor funcionaba si la API local estaba
levantada; en el de cualquier otra persona, no.

### 2.3 La causa de fondo

La dirección del servicio **no se elige al ejecutar la aplicación, sino al compilarla**:

```bash
flutter build web --release --dart-define=API_BASE_URL=https://sigvach-api.onrender.com
```

Se había compilado **para probar en local** —sin ese parámetro— y se publicó **esa misma
carpeta** `build/web`. El error no estaba en el código ni en el navegador: estaba en
publicar la compilación equivocada.

### 2.4 El arreglo

1. Recompilar con la dirección pública y volver a publicar. El paquete publicado pasó a
   tener la huella `C7A10F2C…C5F1` y a contener la dirección del servicio.
2. Publicar **sin caché** los archivos que deciden qué versión se carga, en
   `firebase.json`: `index.html`, `flutter_bootstrap.js`, `flutter_service_worker.js` y
   `main.dart.js`. Antes se servían con `max-age=3600`, de modo que un navegador podía
   seguir usando la versión vieja hasta una hora después de publicar.
3. Añadir `scripts/verificar_despliegue.py`, que comprueba en cinco segundos las cuatro
   cosas que se rompen en silencio: que el paquete publicado lleve la dirección pública,
   que coincida con `build/web`, que `/api/v1/salud` responda y que el origen de la
   aplicación esté autorizado, **incluido el examen previo** que hace el navegador antes
   de las peticiones con token.

### 2.5 Cómo se explica el error

Se dibujó la lámina `Figuras/20-error-del-despliegue.png`, que resume el fallo en cuatro
bandas: los dos caminos desde el mismo código, qué significa `127.0.0.1`, que el navegador
no se rompió (solo obedecía lo que decía la página) y la regla final: **se puede levantar
la API en local; lo que no se puede es publicar la carpeta compilada para local**.

---

## 3. Revisión final del entregable E2

Antes de la entrega se revisó el documento apartado por apartado. Lo que se encontró y se
corrigió:

| Hallazgo | Corrección |
|---|---|
| La figura de casos de uso medía 16,99 × 14,43 cm y estaba estirada un 12 % | Se le devolvió la escala uniforme: 14,40 × 10,95 cm. Es un **grupo flotante** de Word, no una imagen suelta |
| La figura del segundo *wireframe* estaba comprimida un 13 % | Se corrigió a 6,76 × 9,68 cm, conservando su proporción real (880 × 1260 px) |
| El párrafo con estilo de apartado antes de «2.4.4» aparecía como título vacío | **No se borró**: es el párrafo que lleva el **salto de sección**. Se le quitó solo el estilo de apartado |
| Faltaba puntuación en la línea del tablero (apartado 2.2) | Se cerró la frase antes de «Enlace» y se añadió el punto final |

**Verificación posterior:** 48 páginas, 8.697 palabras, 19 tablas, seis figuras con su
proporción exacta, tres secciones con sus márgenes intactos y sin restos de plantilla.

Un dato que se comprobó y conviene recordar: **ensanchar el segundo *wireframe* para
igualar su altura con el primero llevaba el documento de 48 a 50 páginas.** Se midió cada
cambio por separado para aislar el efecto y se optó por conservar la proporción.

---

## 4. El módulo de adquisición vuelve a publicar

### 4.1 Estaba apagado

La última lectura del módulo era del **25/09 a las 04:45**. Al encenderlo, publicó su
primer ciclo en veinte segundos: el bucle mide y publica al arrancar, y después cada cinco
minutos.

### 4.2 Un fallo de conexión que se pudo ver en el Monitor Serie

Publicaba **tres** de las cinco variables. Faltaban `temp_ambiental` y `humedad`, y el
registro explicaba por qué:

```
I (4614) SENSORES: Buscando el sensor de ambiente (primero en P33)...
E (4734) dht: Initialization error, problem in phase 'B'
W (9174) SENSORES: ENCONTRADO: AM2302 / DHT22 en GPIO 33
...
E (17864) dht: Initialization error, problem in phase 'B'
W (17864) SIGVACH: Ambiente -> sin respuesta (ESP_ERR_TIMEOUT)
W (18704) SIGVACH:   temp_ambiental  sin dato: no se publica
W (18704) SIGVACH:   humedad         sin dato: no se publica
```

El propio firmware documenta qué significa ese error: *«la línea se quedó en alto: el
pull-up la sostiene y nadie del otro lado la baja, o sea que el sensor no está conectado a
ESE pin, o no está alimentado»*. El síntoma era elocuente: **respondía al arrancar y
fallaba en todos los ciclos**, que es la firma de un contacto flojo.

**La solución fue desconectar y volver a conectar el cable de datos del sensor**, con un
matiz que conviene dejar anotado: **el cable parecía bien conectado**. Se revisó primero y
a simple vista estaba en su sitio; aun así no daba datos, y fue al sacarlo y volver a
meterlo cuando empezó a responder. Es decir, no era un cable fuera de su pin, sino un
**contacto eléctrico deficiente con aspecto correcto**: la punta entraba, pero no llegaba
a tocar bien. Suele deberse al terminal hembra que se abre con el uso, a óxido o suciedad
en el pin, o a un hilo roto por dentro del aislamiento.

Ese tipo de avería **vuelve sola**: por eso conviene sustituir el cable por uno nuevo si el
terminal está flojo, sujetarlo con una brida o cinta para que nadie lo mueva, y —cuando la
maqueta quede armada— dejarla publicando un buen rato y comprobar que **ningún ciclo se
queda sin las dos variables de ambiente**. Si aparece un hueco, el contacto volvió a
fallar.

Desde las 22:54 el módulo publica las **cinco** variables en el mismo ciclo:

```
22:54:01  temp_ambiental   26,3 °C
22:54:05  humedad          33,1 %
22:54:08  temp_solucion    24,56 °C
22:54:11  tds            239,31 ppm
22:54:15  ec               0,48 mS/cm
```

### 4.3 Lo que el arranque confirmó del resto del módulo

| Elemento | Estado |
|---|---|
| Memoria no volátil | Lista, con la cola de pendientes vacía |
| Convertidor analógico | **Calibración de fábrica desde el eFuse**, con los 4 s de asentamiento cumplidos |
| DS18B20 | Detectado con su ROM y 12 bits: `Solucion -> 24.81 C` |
| WiFi | Conectado, con la hora tomada del servicio |
| HTTPS | `Certificate validated` en cada envío |
| Entrada del pH | 142 mV con dispersión 0: igual que un pin al aire, es decir, el módulo de pH aún no está conectado |

---

## 5. El electrodo de pH: diagnóstico y plan

**El historial confirmado por el autor:** se usó dos o tres veces durante las prácticas con
Arduino y después se guardó **seco, dentro de su caja**, sin solución de almacenamiento. Al
retomar el trabajo con ESP-IDF ya no respondía. La caja del proveedor no incluye solución
de almacenamiento, y la costra blanca que se ve dentro del tapón es el KCl de esa solución
que se evaporó.

**Lo que se vio en las fotos:** el bulbo está presente y entero dentro de su jaula
protectora, sin grietas ni depósitos oscuros; el conector BNC está limpio. El pronóstico es
bueno, porque **no hay desgaste de uso, solo sequedad**.

**El plan de recuperación** (documentado en `18_PLAN_DE_LA_SEMANA.md` y en la guía
`19_GUIA_DEL_SENSOR_DE_PH.md`): remojo del bulbo en **KCl 3 M** durante 24 a 48 horas, con
los criterios de descarte escritos, y la decisión de comprar o no el **miércoles**, para
que quede margen.

**Dato útil para el firmware:** la clave del dispositivo que exige el servicio está en el
`.env` del proyecto, y se comprobó contra el servicio publicado que es válida (respondió
422 ante una variable desconocida, no 401). Con ella se rehizo el archivo
`hardware/firmware/main/configuracion.h`, que faltaba, dejando pendiente solo el nombre y
la clave del WiFi.

---

## 6. Estado del repositorio y del tablero

| Elemento | Antes | Ahora |
|---|---|---|
| T-29 (entregable E2) | En curso | **Hecho** (26/09) |
| Tareas terminadas | 30 | **31** |
| Tareas en curso | 2 | **1** (T-28, la maqueta) |
| Confirmaciones | 125 en 13 días | **128 en 14 días** |

Se añadieron al repositorio el plan de la semana, la guía del sensor de pH, el verificador
de despliegue y la nota correspondiente en `10_DESPLIEGUE.md`. La figura del tablero dentro
del E2 entregado retrata el estado al 25/09 (30/2/4), de modo que hay una diferencia
deliberada y explicable con el tablero actual.

---

## 7. Lo que queda para la semana

1. **Lunes:** comprar **KCl 3 M** y los **patrones de pH 4,00 y 6,86**; preguntar por el
   patrón de 707 ppm y por la sonda de pH sola. Arrancar el remojo del electrodo.
2. **Miércoles:** decisión sobre el electrodo. Si no revive, comprar ese mismo día.
3. **Semana:** montar el divisor ÷2 del pH con dos resistencias de 4,7 kΩ, calibrar el pH y
   el TDS, y añadir al firmware la conversión y la publicación de la variable `ph`.
4. **Viernes:** maqueta terminada, evidencias fotográficas y capturas de adaptabilidad.

---

## 8. Lo que se aprendió

1. **La dirección del servicio viaja dentro del paquete compilado.** Publicar la carpeta
   del modo local deja a la aplicación pidiendo datos al equipo de quien la mira. Se
   detecta en cinco segundos con el verificador.
2. **Un fallo de contacto se disfraza de fallo de sensor.** Responder al arrancar y fallar
   después no es un sensor agotado: es un cable a medio meter.
3. **El firmware hace bien en no publicar un valor inválido.** Las dos variables ausentes
   no eran un error del sistema, sino la consecuencia de una lectura que no se pudo hacer.
4. **Los instrumentos tienen requisitos de conservación.** El electrodo de pH se guarda
   húmedo, en KCl, con el tapón lleno; en seco pierde la referencia por más que apenas se
   haya usado.
