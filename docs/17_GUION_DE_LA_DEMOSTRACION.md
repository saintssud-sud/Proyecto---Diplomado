# 17 · Guion de la demostración — E2 y defensa

**Proyecto:** SI.G.VA.C.H. · **Actualizado:** 25 de septiembre de 2026
**Para qué sirve:** qué mostrar, en qué orden y qué decir, en la entrega del E2 y en
la defensa técnica del 13 de octubre.

> **La diferencia con lo previsto originalmente.** El E2 admitía un *dispositivo
> simulado*. El módulo real ya está construido, calibrado y publicando en
> producción, de modo que la demostración se hace **con el módulo** y el simulador
> queda como plan B. Es más contundente y además cierra la observación **B-3** de la
> tutoría: ya no hay nada «por definir».

---

## 1. Qué se demuestra

El E2 pide una **vertical funcional desplegada**:

> *"`https://sigvach26-bd.web.app` funcionando contra la API en Render: login +
> registrar lectura manual + panel con estado y una alerta generada por un valor
> fuera de rango."*

| Pieza | Cómo se muestra |
|---|---|
| Aplicación publicada contra la API | Se abre la dirección **en incógnito**, desde un dispositivo limpio |
| Inicio de sesión | Con la cuenta declarada en el documento |
| Registrar lectura manual | Se registra un valor desde la aplicación |
| Panel con estado | Se muestra el estado de cada variable contra su rango |
| **Alerta por valor fuera de rango** | Se provoca y se ve la alerta, y se marca como atendida |
| **Dispositivo** | **El módulo ESP32 real**, publicando por su cuenta |

---

## 2. Antes de empezar (cinco minutos)

| # | Verificación | Cómo |
|---|---|---|
| 1 | **El servicio está despierto** | Abrir `https://sigvach-api.onrender.com/api/v1/salud` **dos o tres minutos antes de empezar**: debe responder `{"estado":"ok",...}`. Si tarda, es el arranque en frío: esperar y volver a intentar |
| 2 | **El módulo está publicando** | El Monitor Serie debe mostrar `... -> almacenada` en cada variable. Si no, revisar la alimentación y el WiFi |
| 3 | **La aplicación abre en incógnito** | Abrir la dirección en una ventana de incógnito y entrar. **Esto es lo que hace el evaluador** |
| 4 | **La sesión está iniciada** | Entrar una vez antes de la demostración: así la base y el servicio ya respondieron una vez |
| 5 | **El módulo está a la vista** | Que se vean la placa, los sensores y el Monitor Serie |
| 6 | **Ningún bloqueador corta la conexión** | Usar **Chrome o Firefox**. En **Brave**, bajar los escudos para `sigvach26-bd.web.app`: el servicio vive en otro dominio, y los bloqueadores cortan esa llamada. El síntoma es «No se pudo conectar con el servidor» |
| 7 | **El despliegue es el correcto** | `python scripts/verificar_despliegue.py`, que comprueba que la aplicación publicada apunta a la API pública y no a una dirección local |
| 8 | **Sin secretos en el repositorio** | `python scripts/verificar_sin_secretos.py`: revisa que no se haya publicado la clave del dispositivo, las credenciales del WiFi ni claves privadas, ni en los archivos ni en el historial |

> ⚠️ **Regla de oro: no cerrar la ventana del Monitor Serie durante la demostración.**
> Es la prueba de que las lecturas salen del hardware y no de un archivo.

---

## 3. Guion del E2 (cinco minutos)

| Paso | Acción | Qué se ve | Qué decir |
|---|---|---|---|
| **1** | Abrir la dirección **en incógnito** | La pantalla de inicio de sesión | *"La aplicación está publicada y es accesible desde cualquier red, sin sesión previa."* |
| **2** | Entrar con la cuenta declarada | El panel con las variables del módulo | *"El servicio valida el token en el servidor y resuelve el rol; no es la aplicación la que decide."* |
| **3** | Señalar el **Monitor Serie** | Las lecturas entrando solas | *"Estas lecturas no las escribió nadie a mano: las publica el módulo por HTTPS cada cinco minutos, autenticándose con su clave de dispositivo."* |
| **4** | **Refrescar el panel** | Los valores y la hora de la última lectura actualizados | *"El dato nació en el sensor, viajó por el módulo, cruzó el servicio y llegó acá."* |
| **5** | Registrar una **lectura manual** | El valor aparece en el panel, marcado como manual | *"El sistema distingue el origen: esta la ingresó una persona y queda registrado quién. Es el camino para lo que se mide a mano, por ejemplo una lectura de pH tomada con el medidor portátil."* |
| **6** | Registrar un **valor fuera de rango** | Aparece la **alerta** | *"El servicio evaluó el valor contra el rango del perfil del cultivo y generó la alerta. Ni la aplicación ni la base deciden eso."* |
| **7** | Abrir el **historial** de esa variable | La serie con el valor desviado | *"El historial conserva la serie completa, que es lo que el antecedente local no registraba."* |
| **8** | **Marcar la alerta como atendida** | Sale de las activas y queda en el historial | *"Atender una alerta no la borra: deja constancia."* |

**Cierre:** *"La vertical está completa: de la pantalla a la base y de vuelta, en
producción."*

---

## 4. Guion de la defensa (siete minutos)

El tribunal del 13 de octubre evalúa el **sistema desplegado que se entregó en el E4**,
no una versión local.

| Min | Qué | Qué decir |
|---|---|---|
| **0–1** | El problema en una frase | *"Quien monitorea un cultivo hidropónico a mano no tiene historial organizado ni aviso oportuno cuando una variable sale de rango."* |
| **1–4** | **Demostración** con el módulo | Los ocho pasos del apartado 3, condensados |
| **4–5** | **Arquitectura**, en una frase por pieza | *"La aplicación presenta y recoge; el servicio decide, valida y autoriza; la base guarda el estado y nadie la toca sin pasar por el servicio."* |
| **5–6** | **El módulo**: lo que aporta | *"Mide las seis variables de forma automática; guarda las lecturas en memoria no volátil si el servicio no responde, y las publica con la hora en que se midieron."* |
| **6–7** | **Riesgos y límites** | El arranque en frío de la capa gratuita, y la calibración del TDS —que todavía usa el factor de fábrica— a la espera del patrón de 1413 µS/cm |

---

## 5. Plan de contingencia

**Lo que puede fallar y qué hacer.** Ningún imprevisto debe detener la demostración.

| Si falla… | Qué hacer |
|---|---|
| **El servicio está dormido** (primera petición lenta) | Esperar y pulsar **Reintentar**. La aplicación muestra el estado de error con esa opción. Mientras tanto: *"La capa gratuita suspende el servicio por inactividad; es una limitación declarada."* |
| **El módulo no publica** | Seguir con la demostración y **explicar la cola**: *"Si el servicio no responde, la lectura queda en memoria no volátil y se reintenta. Puedo mostrarlo apagando el WiFi."* — y hacerlo, que es más convincente |
| **El WiFi del aula falla** | Usar el **simulador** (apartado 6). El flujo se ve igual: mismo endpoint, misma clave, mismo cuerpo |
| **La aplicación no carga en el navegador** | Abrir en **otro navegador** o en incógnito. Casi siempre es la caché del service worker, y desde ahora los archivos que deciden qué versión se carga se publican **sin caché**, así que esto debería desaparecer |
| **«No se pudo conectar con el servidor»** | Tres causas, en este orden: (1) el servicio está **dormido** → esperar y pulsar *Reintentar*; (2) un **bloqueador** corta la llamada → probar en Chrome o bajar los escudos en Brave; (3) el paquete publicado **apunta a otra dirección** → comprobarlo con `python scripts/verificar_despliegue.py` |
| **El módulo deja de publicar dos variables** (`temp_ambiental` y `humedad`) | Es el **contacto del cable de datos del AM2302**: en el Monitor Serie aparece `dht: Initialization error, problem in phase 'B'` y `temp_ambiental sin dato: no se publica`. Sacar y volver a meter el cable en el GPIO 33; si vuelve a pasar, cambiar el cable, porque el terminal está flojo |
| **La base rechaza una escritura** | Mostrar el `422` y el campo señalado: *"La validación está en el servidor y el error dice qué corregir."* |
| **Nada de lo anterior funciona** | Quedan las **capturas fechadas** y el **repositorio**, que es donde el docente verifica. La demostración en vivo suma, pero la entrega ya está subida |

---

## 6. Plan B: el simulador

Si no hay red para el módulo, el simulador ocupa su lugar. **Envía las lecturas por el
mismo endpoint, con la misma clave y el mismo cuerpo**, de modo que el servicio no
distingue una lectura simulada de una real.

```powershell
cd "D:\SIGVACH-Monograf\Proyecto SIGVACH"
.venv\Scripts\python.exe scripts\simulador_dispositivo.py --url https://sigvach-api.onrender.com --modulo v6wrYSXxeHyttf3prDd7 --ciclos 1
```

Para **forzar una alerta** sin esperar a que el cultivo se desvíe:

```powershell
.venv\Scripts\python.exe scripts\simulador_dispositivo.py --url https://sigvach-api.onrender.com --modulo v6wrYSXxeHyttf3prDd7 --ciclos 1 --fuera-de-rango ph
```

El detalle completo está en `docs/16_SIMULADOR_DEL_DISPOSITIVO.md`.

---

## 7. Preguntas previsibles del tribunal

| Pregunta | Respuesta |
|---|---|
| **¿De dónde salen estos datos?** | Del módulo ESP32, que los publica por HTTPS con su clave de dispositivo. **Se ve en el Monitor Serie** |
| **¿Qué pasa si se corta la luz?** | Las lecturas pendientes están en **memoria no volátil**: sobreviven al reinicio y se publican con la hora en que se midieron. **Se probó**: diez lecturas sobrevivieron a dos reinicios |
| **¿Por qué el servicio y no la base directamente?** | *"Nadie toca la base sin pasar por el servicio."* La validación y la autorización no pueden depender del cliente. Las reglas de Firestore cierran el acceso directo |
| **¿Cómo se que un sensor mide bien?** | Con **ensayos propios** documentados: el DS18B20 se contrastó contra el AM2302 y coincidieron en 0,01 °C; el TDS se probó alterando la concentración de la solución; y el pH se calibró con los **patrones de 4,01 y 6,86**, que dieron 1520 mV y 1280 mV, o sea 84,2 mV por unidad de pH. Los registros están en el repositorio |
| **¿Qué queda fuera del alcance?** | El **control de actuadores** —el módulo mide y publica, no acciona la bomba— y la variable de **nivel de agua**, que se retiró del alcance al analizar el montaje |
| **¿Ese pH del panel lo mide el módulo?** | **Sí**, desde el 1 de octubre: el electrodo se recuperó con el remojo, se instaló el divisor ÷2 y se calibró con los dos patrones. En el historial también hay lecturas de pH **manuales y de prueba**, anteriores a esa fecha, y el panel las distingue por su origen |
| **¿Cuánto cuesta operarlo?** | La capa gratuita del servicio y de la base; a cinco minutos por ciclo se usa el **10 % de la cuota diaria** de escrituras |
| **¿Qué error les costó más?** | Decirlo con honestidad: el asentamiento del convertidor analógico, que hacía que la **primera lectura publicada tras encender fuera falsa** y con apariencia normal |

---

## 8. Tres cosas que no hay que olvidar

1. **Abrir la aplicación una vez antes de empezar.** Así el servicio y la base ya
   respondieron y no se pierde tiempo en la primera espera.
2. **Mostrar el Monitor Serie, no contarlo.** Que las lecturas se vean entrar es la
   prueba de que el módulo existe y funciona.
3. **Ensayar la contingencia.** Si el plan B nunca se practicó, el día que haga falta
   no va a funcionar. Conviene haber corrido el simulador una vez.

---

*Documento de trabajo. Se actualiza con cada iteración del prototipo.*
