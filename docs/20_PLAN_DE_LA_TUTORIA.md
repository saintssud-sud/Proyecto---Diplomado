# Plan de la tutoría — martes 29 de septiembre de 2026

**Objetivo de la sesión:** cerrar las observaciones que quedaron **pendientes del tutor**
(A-4, A-11 y A-12), mostrarle el sistema funcionando y llevarse las decisiones por escrito.

**Idea de fondo:** a una tutoría se va **con respuestas y se sale con decisiones**. No es una
sesión para explicar lo que ya está en el documento, sino para desbloquear lo que depende de él.

---

## 1. Lo que se reporta (cinco minutos)

| Tema | Qué decir |
|---|---|
| **Entregable E2** | Entregado el **sábado 26 a las 00:52**, 23 horas antes del cierre. El PDF con las figuras ajustadas al ancho y los datos de acceso en el campo de texto |
| **Cuestionario Q2** | Completado el mismo día |
| **Sistema desplegado** | La aplicación (`sigvach26-bd.web.app`) contra el servicio publicado, con login, panel, alertas e historial |
| **Módulo de adquisición** | El **ESP32 real** publicando **cinco variables** en producción: `temp_ambiental`, `humedad`, `temp_solucion`, `tds` y `ec` |
| **Repositorio** | Más de 130 confirmaciones repartidas en **14 días distintos**, con README, tablero y documentación |
| **Semana en curso** | La maqueta se monta esta semana, y el electrodo de pH está en recuperación |

**Un dato que conviene decir de entrada**, porque evita la pregunta incómoda: el módulo publica
**cinco** variables; la sexta, el **pH**, está **pendiente de forma declarada**, con el electrodo en
remojo y una decisión prevista para el miércoles. No es un olvido: es un alcance declarado.

---

## 2. Lo que se muestra (cinco minutos)

1. **La aplicación en vivo**, en el navegador, con el módulo de la maqueta seleccionado y los
   valores actualizándose. Conviene abrirla **dos minutos antes**: la capa gratuita del servicio
   se duerme por inactividad y la primera carga puede tardar.
2. **El Monitor Serie**, si se lleva el módulo: las lecturas entrando solas y el `-> almacenada`
   de cada variable. Es la prueba de que el dato nace en el hardware.
3. **El tablero** (`docs/TABLERO.md`) y el **plan de la semana**, para que vea que hay método.

---

## 3. Lo que se cierra con el tutor — el punto central de la agenda

### A-4 · Ámbito del módulo piloto

El entregable menciona «el módulo de cultivo piloto» y no existía un módulo físico construido. Hay
que decidir cómo se nombra ese ámbito en el objetivo general y en el apartado 1.2.

**Qué decir:** la maqueta física se monta esta semana —depósito, los cinco sensores, el módulo
publicando—, así que el «módulo piloto» deja de ser una mención en el documento y pasa a ser un
montaje real y verificable. **Preguntar si con eso queda cerrada** o si prefiere otro nombre.

### A-11 y A-12 · Quedaron sin registrar

En la bitácora del 22 de septiembre aparecen como pendientes, pero **no quedó escrito qué pedían**.
**Pedirle que las precise** y anotarlas en el momento, con sus palabras.

### C · El dato del ensayo previo

- **Número de detecciones tardías**: confirmar el dato con él.
- **Ámbito del módulo piloto**: es el mismo asunto que A-4, se cierra junto.

### D · Los tres puntos de limpieza

Se informan como **resueltos**: el usuario de prueba está declarado como ficticio, el documento no
tiene hojas de verificación ni restos de plantilla, y las figuras están ajustadas al ancho de la
página y sin deformación.

---

## 4. Lo que se pregunta (llevarlo escrito y leerlo)

1. **A-11 y A-12**: ¿cuáles eran exactamente?
2. **A-4**: ¿cerramos el ámbito del módulo piloto con la maqueta que se está montando esta semana?
3. **Detecciones tardías** del ensayo previo: ¿confirmamos el número con este dato?
4. **E3**: ¿qué espera exactamente para el E3 —roles con autorización en cada ruta, batería de
   pruebas del apartado 2.8, Capítulos 1 y 2 completos— y para cuándo?
5. **Defensa del 13 de octubre**: ¿qué quiere ver en el guion y con cuánto tiempo se presenta?
6. **El pH**: si el electrodo no revive, ¿le parece correcto presentar la variable como
   **pendiente declarada** con la compra prevista, en lugar de forzar un dato?

---

## 5. Qué llevar

- [ ] La **dirección de la aplicación** y el **usuario de prueba** (por si quiere entrar en el momento)
- [ ] El **módulo ESP32** con los sensores, si se puede transportar
- [ ] **Fotos** del montaje y del electrodo en remojo, por si falla la conexión
- [ ] Este plan, el **tablero** y el **registro del remojo**, en el celular
- [ ] Papel y lapicero: los acuerdos se escriben **en el momento**

---

## 6. Cómo cerrar la sesión

Antes de salir, leer en voz alta **los acuerdos** y confirmarlos: qué quedó cerrado, qué queda
pendiente y quién hace qué. Después, al llegar, registrarlos en la bitácora del día.

Ese resumen escrito es lo que evita que, en la próxima tutoría, vuelvan a aparecer observaciones
que ya se habían atendido.
