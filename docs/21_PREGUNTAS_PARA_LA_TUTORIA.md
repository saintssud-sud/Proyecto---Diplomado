# Preguntas para la tutoría

**Fecha:** martes 29 de septiembre de 2026
**Cómo se usa:** se lee la pregunta tal como está escrita, se anota la respuesta debajo, y se marca
el cuadradito cuando ya se hizo. Al final se leen los acuerdos en voz alta y se confirman.

> **Regla de la sesión:** no se sale sin haber preguntado **el primer bloque completo**. Lo demás
> es importante, pero eso es lo que bloquea el trabajo.
>
> **Y no se pregunta lo que ya está respondido:** la fecha del E3 es el sábado 3 de octubre a las
> 23:59, con hasta 72 horas de tolerancia y 10 puntos porcentuales por día de atraso, y el
> cuestionario Q3 vence el mismo día sin tolerancia.

---

## Bloque 1 · Lo que bloquea el trabajo

- [ ] **1.1** «En la bitácora del 22 de septiembre figuran las observaciones **A-11 y A-12** como
  pendientes, pero no anoté qué pedían. ¿Me las puede precisar, por favor?»

  *Anoté:*

- [ ] **1.2** «La **A-4** pedía decidir cómo nombrar el ámbito del módulo piloto. Esta semana monto
  la maqueta física: depósito, los sensores y el módulo publicando. ¿Le parece que con eso queda
  cerrada, o preferiría otro nombre en el objetivo general y en el apartado 1.2?»

  *Anoté:*

- [ ] **1.3** «Sobre los datos del ensayo previo: el **número de detecciones tardías**.
  ¿Confirmamos el dato que figura en el documento?»

  *Anoté:*

- [ ] **1.4** «Los tres puntos de limpieza —usuario de prueba declarado como ficticio, sin hojas de
  verificación en el documento, figuras ajustadas al ancho— los damos por resueltos.
  ¿Está de acuerdo?»

  *Anoté:*

- [ ] **1.5** «Le traigo las **once recomendaciones del T3** con lo que hicimos en cada una.
  ¿Queda alguna sin tratar, o alguna que haya entendido al revés?»

  *Anoté:*

---

## Bloque 2 · El pH y la maqueta

- [ ] **2.1** «El módulo publica **cinco variables** en producción. La sexta, el **pH**, está
  **pendiente de forma declarada**: el electrodo está en remojo y la decisión es el miércoles.
  ¿Le parece correcto presentarlo así?»

  *Anoté:*

- [ ] **2.2** «Si el electrodo no revive y compramos la sonda nueva, ¿basta con documentar el
  reemplazo y su calibración, o quiere que quede declarado de otra forma?»

  *Anoté:*

- [ ] **2.3** «Para calibrar el TDS conseguimos un patrón de **800 ppm** en lugar del 707 ppm que
  cita la bibliografía. ¿Es aceptable si queda documentado con qué patrón se calibró?»

  *Anoté:*

- [ ] **2.4** «¿Qué alcance espera para la **maqueta**: basta con el montaje midiendo, o quiere que
  en esta entrega incluya también el cultivo con plantines?»

  *Anoté:*

---

## Bloque 3 · El alcance del E3

- [ ] **3.1** «Entendí que para el **E3** van los roles con autorización en cada ruta, la batería
  de pruebas con su evidencia en el apartado 2.8, y los capítulos 1 y 2. ¿Es correcto, o hay algo
  más?»

  *Anoté:*

- [ ] **3.2** «El ingreso lo resuelve **Firebase Authentication**: la contraseña nunca pasa por
  nuestro servicio y se guarda con *hash* del lado del proveedor; nosotros validamos el token en
  cada petición, y el token vence. ¿Le sirve así como cumplimiento del requisito, o quiere que
  mostremos el *hash* en un almacenamiento propio?»

  *Anoté:*

- [ ] **3.3** «En el servicio quedó el punto de acceso **`DELETE /api/v1/lecturas/{id}`**, que
  permite borrar una lectura. Lo quitamos de la tabla de requisitos. ¿Prefiere que lo eliminemos
  del servicio, o que lo convirtamos en una **anulación con motivo**, que conserva el registro y
  guarda quién lo anuló y por qué?»

  *Anoté:*

- [ ] **3.4** «Para el **2.8**, ¿la tabla de casos con el resultado alcanza, o quiere el informe de
  las pruebas automáticas como anexo dentro del documento? Hoy van **199 pruebas**, 106 del
  servicio y 93 de la aplicación, y el informe puede quedar versionado en el repositorio.»

  *Anoté:*

- [ ] **3.5** «El **2.7 de seguridad**: ¿espera el detalle de cada control —token que vence, roles
  por operación, doble validación, CORS, sin secretos en el repositorio— o prefiere un resumen con
  la referencia a la evidencia?»

  *Anoté:*

- [ ] **3.6** «¿El **Capítulo 1** tiene que estar completo para el E3, o alcanza con el borrador de
  los apartados 2.1 a 2.8?»

  *Anoté:*

- [ ] **3.7** «¿Alcanza con la **aplicación web publicada**, o quiere que el E3 incluya también el
  **APK de Android** instalado y probado en el teléfono?»

  *Anoté:*

- [ ] **3.8** «¿Qué espera del **E4** y para cuándo?»

  *Anoté:*

- [ ] **3.9** «Para la **defensa del 13 de octubre**: ¿qué quiere ver en el guion, y de cuánto
  tiempo disponemos?»

  *Anoté:*

---

## Bloque 4 · Lo administrativo

- [ ] **4.1** «¿Mantenemos la tutoría en el mismo día y hora?»

  *Anoté:*

- [ ] **4.2** «¿Hay algún apartado del documento que prefiera que reescriba antes del E3?»

  *Anoté:*

---

## Cierre · Los acuerdos de la sesión

Se leen en voz alta **antes de salir** y se confirman. Después se registran en la bitácora del día.

| Qué quedó cerrado | Qué queda pendiente | Quién lo hace | Para cuándo |
|---|---|---|---|
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

**Firma de conformidad del tutor sobre los acuerdos:** ______________________________
