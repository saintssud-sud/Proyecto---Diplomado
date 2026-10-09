# Bitácora — jueves 8 de octubre de 2026

Sesión de trabajo sobre el **documento final (E4)**: ensamblado de las capturas del Anexo A,
reconstrucción de los índices y exportación del PDF.

**Resultado: el E4 quedó en 145 páginas, con 31 de las 32 figuras del Anexo A y los tres
índices coherentes con el índice de contenido.** Falta únicamente la captura A.6.

Esta bitácora se escribe el mismo día. Sirve para no repetir pruebas ya hechas, para poder
explicar cada decisión en la defensa y para no volver a pisar los mismos errores.

---

## 1. Resumen en cinco líneas

1. Se armó el Anexo A con **las 32 capturas**: 31 elegidas de las 91 disponibles y la A.6, que apareció entre las tomadas a última hora (19:16 a 19:21).
2. Se reconstruyeron los **tres índices** con números de página reales: **20 tablas, 48 figuras y 7 anexos**.
3. Apareció un **desfase de 9 páginas** entre lo que medía el script y lo que ve el lector: el script devolvía la **página física** del archivo, no la **impresa**.
4. La causa era que **los preliminares (portada + 8 páginas en romanos) no llevan número arábigo**, y el cuerpo arranca a contar desde 1 en la página física 10.
5. El **índice de anexos tenía números falsos** (decía «Anexo A → 1») porque se buscaba el texto del título y encontraba una mención suelta; además había **7 entradas de índice metidas dentro del Capítulo 1**.
6. La **Figura 1 (tablero Kanban) estaba congelada** al cierre de la Semana 4 y todavía mostraba la calibración del TDS en el backlog: se regeneró desde el tablero y se reemplazó.
7. La **exportación del PDF** se trababa más de 40 minutos sin escribir nada. Quedó resuelta y documentada la forma que funciona: **una invocación propia, Word cerrado, desde una copia**: 12 segundos.

---

## 2. Cronología de la sesión

### 2.1 Elección de las capturas del Anexo A

Se revisaron las 91 capturas de `Proyecto SIGVACH/evidencia/Nueva carpeta/` contra los
32 rótulos del Anexo A. Las capturas se repartieron en tres lotes y se eligió, para cada
figura, la imagen que muestra exactamente lo que el texto describe.

Hallazgos de la revisión:

- Varias capturas son **duplicados byte a byte** (por ejemplo `A18` = `A19` = `A19.1`): sirven, pero no aportan información nueva.
- El archivo que estaba guardado como `A6.jpg` **era la pantalla de Alertas**, que corresponde a la figura A.16, no a la A.6. Por eso la A.6 quedó sin captura válida.
- Se reemplazaron tres figuras provisionales por versiones más claras (A.15, A.20 y A.21), con datos reales del sistema (23 mediciones, teléfono 60278965, cuenta "Admin Prueba").

### 2.2 Ajuste de la figura ancha

La **Figura 1** (arquitectura) se salía del margen: se redujo de **15,9 cm a 14,4 cm** de
ancho, que es lo que entra en el ancho útil de la hoja.

### 2.3 Inserción de las figuras en el documento

Se insertaron las 31 figuras del Anexo A con el script `_diagnostico/insertar_figuras_anexo_a.py`:

- imagen centrada, **14 cm de ancho**;
- rótulo debajo, en estilo Normal, cursiva, 10 pt;
- sin "Fuente:" para no romper el formato del anexo.

### 2.4 Reconstrucción de los índices: el desfase de 9 páginas

**Síntoma.** El índice de anexos decía que el Anexo A estaba en la página 49, mientras el
índice de contenido (el campo automático de Word) decía 40.

**Diagnóstico.** Los dos tenían razón: **medían cosas distintas**.

| Concepto | Qué es | Cómo se obtenía |
|---|---|---|
| Página física | La posición del papel dentro del archivo, contando la portada | `Information(3)` de Word |
| Página impresa | La que ve el lector en el pie de página | La que usa el índice de contenido |

Los preliminares van en **números romanos** y no consumen numeración arábiga. El cuerpo
arranca a contar desde 1, pero lo hace en la **página física 10**:

```
física 1        portada
físicas 2 a 9   preliminares (i a viii)
física 10       CAPÍTULO 1. INTRODUCCIÓN  -> impresa 1
física 49       Anexo A                   -> impresa 40
```

De ahí el desfase constante de **9 páginas** en todo el cuerpo y los anexos.

**Corrección.** El script ahora pregunta a Word en qué página física arranca el cuerpo,
calcula el desfase y lo resta en todo lo que esté dentro del cuerpo. Los preliminares se
informan como están (ahí página física y romana coinciden en valor numérico).

Con eso los tres índices y el índice de contenido coinciden:

| Anexo | Página impresa | Anexo | Página impresa |
|---|---|---|---|
| A | 41 | E | 98 |
| B | 85 | F | 104 |
| C | 96 | G | 105 |
| D | 97 | | |

### 2.5 La exportación del PDF que se trababa

**Síntoma.** La exportación del PDF se quedaba **más de 40 minutos sin escribir un solo
byte**, quemando procesador. En una de esas corridas se llevó puesto el PDF que ya estaba
bien, porque el script borraba el archivo anterior **antes** de exportar y después nunca
llegaba a escribirlo.

**Primer hallazgo: 14 instancias de Word huérfanas.** Había **14 procesos de Word sin
ventana** acumulados (1,6 GB de RAM). Ninguno era del usuario: eran automatizaciones
anteriores que quedaron vivas al cortarse el proceso que las lanzó. **La causa de que se
acumularan: el script que rehace los índices cerraba el documento pero no cerraba Word.**
Ya está corregido (ahora cierra la instancia que abrió).

**Segundo hallazgo: el documento no tenía nada roto.** Se probó exportar un documento
trivial creado al vuelo: **3,5 segundos**. Y el E4 completo, desde una copia,
**11 segundos**. Con eso quedó descartado que el problema fuera el tamaño, las imágenes
(la más pesada pesa 0,25 MB), los campos (25 abiertos y 25 cerrados, todos bien) o los
encabezados.

**Lo que quedó medido, probando una cosa por vez:**

| Forma de exportar | Resultado |
|---|---|
| Documento trivial, instancia nueva | 3,5 s — bien |
| E4 desde una **copia**, instancia nueva, nombre simple | **11 a 20 s — bien** |
| E4 desde el **archivo original**, en la misma sesión que lo guardó, con `TEMP` cambiado y nombre con paréntesis | se traba (más de 40 min sin escribir) |
| E4 exportando **un rango de páginas** (1 a 8) | se traba |

No se logró aislar **una** causa única: lo que sí quedó establecido es **qué forma
funciona**, y el script ahora usa esa: dos fases con **dos instancias distintas** de Word
(una actualiza los campos y guarda; otra, nueva y en solo lectura, exporta), **sin cambiar
`TEMP`**, con **nombre de archivo simple** y **sin rango de páginas**.

**Corrección, además, para que no se pierda trabajo:**

1. El PDF se arma en un **archivo temporal** y solo reemplaza al bueno cuando termina bien.
2. Cada paso deja una **traza con tiempos** en `_diagnostico/exportacion.log`.
3. El script cierra Word y limpia las instancias colgadas **incluso si falla** (bloque `finally`), y cierra **solo las que no tienen ventana**: si el usuario tiene Word abierto, no se toca.

**Lo que se midió después, ya con el documento terminado.** La exportación volvió a trabarse
dos veces más y se acotó la causa: **se traba si el mismo proceso —o su proceso padre— ya usó
Word**. Se probó encadenando la actualización de campos y la exportación en un mismo script, y
también llamando a la exportación como proceso hijo: las dos veces se trabó. Como invocación
**propia**, en cambio, exportó siempre: 11, 12, 13 y 20 segundos. Por eso quedaron dos scripts
separados: `actualizar_indices_y_pdf.ps1` (campos) y `exportar_pdf.ps1` (PDF), y **no se
encadenan**.

**Regla que sale de acá:** la exportación del PDF **siempre en su propia invocación**, con Word
cerrado y desde una copia. Si se demora más de lo normal, **no esperar**: cortar y repetirla
así.

### 2.6 Defecto encontrado en la aplicación

Al cargar los rangos del perfil **Apio**, el botón **Guardar** parecía no hacer nada.

**Causa real.** Se escribió `1.200` y `1.150` con **punto de miles**. La aplicación interpretó
`1.200` como `1,2`, que está fuera del rango permitido, y mostró el error de validación
**debajo del área visible** del cuadro de diálogo. El diálogo quedó abierto y parecía colgado.

**Solución inmediata:** escribir los valores **sin punto de miles** (`1200`). Los rangos se
guardaron correctamente y quedaron en la base de datos.

**Queda anotado como defecto a corregir:** aceptar la notación local y mostrar el mensaje de
error **arriba**, donde se vea.

> Corrección de honestidad: primero se pensó que era un problema de caché del navegador
> (la aplicación es una PWA). Se verificó y era **falso**: la versión publicada sí tenía el
> botón correcto. Se deja anotado para no volver a atribuir fallas a la caché sin comprobarlo.

### 2.7 El índice de anexos con números falsos

**Síntoma.** Al revisar el documento ya exportado, el índice de anexos decía
«Anexo A → 1», «Anexo B → 1», «Anexo C → 1», «Anexo E → 2»… mientras el índice de
contenido decía 40, 83, 94. Y había **siete líneas de índice metidas dentro del Capítulo 1**,
entre dos párrafos de la introducción.

**Diagnóstico.** Las dos cosas eran el mismo problema. Un script anterior había dejado esas
siete entradas sueltas dentro del cuerpo. El script que rehace los índices le pedía a Word
la página **buscando el texto** del título («Anexo A. Manual de usuario»), y la búsqueda
encontraba **esa mención suelta**, que está en las páginas 1 y 2, en vez del anexo de
verdad. De ahí los números 1 y 2.

**Corrección:**

1. **Ya no se busca el texto.** Word ahora **recorre los párrafos** y anota en qué página está cada leyenda: así no puede confundirse con una mención escrita en otro lado.
2. **Se saltan las entradas de los índices** (párrafos con estilo «toc»), que repiten los mismos rótulos.
3. **Se borran las entradas sueltas** que hayan quedado dentro del cuerpo. Se quitaron las 7 y el documento pasó de 27 437 a **27 379 palabras**.

**Resultado.** El índice de anexos ahora coincide **exactamente** con el índice de contenido
que calcula Word:

| Anexo | Página | Anexo | Página |
|---|---|---|---|
| A | 41 | E | 98 |
| B | 85 | F | 104 |
| C | 96 | G | 105 |
| D | 97 | | |

(Estas son las páginas **finales**, ya con la figura A.6 y con el tablero nuevo: cada figura
que se agrega o crece corre las páginas de todo lo que sigue.)

**Regla que sale de acá:** para saber en qué página está algo, **recorrer los párrafos**, no
buscar el texto: cualquier leyenda puede estar mencionada antes en el cuerpo y la búsqueda
devuelve la mención, no la leyenda.

### 2.8 La figura A.6, la última que faltaba

El texto del Anexo A la anuncia: «El panel sin novedades se muestra en la Figura A.5 y el
panel con parámetros fuera de rango en la Figura A.6».

Se revisaron las capturas guardadas a las 19:16–19:21 y **`A6.1.jpg` es la que sirve**: el
panel de inicio con «Sistema con alertas», el Módulo 1 seleccionado y el pH en 7,4 marcado
«Por encima del rango». Las otras dos que había con ese nombre (`A6.2` y `A6.3`) son la
pantalla de Alertas, que ya se usan en las figuras A.16 y A.18.

Se insertó con `_diagnostico/insertar_figura_a6.py`, que la coloca **después de la leyenda
de la A.5** con el mismo formato de las demás (14 cm, centrada, leyenda en cursiva de
10 pt). **No se usó el script general de inserción** porque ese inserta *todas* las figuras
anunciadas en el texto y habría repetido las 31 que ya estaban.

Al agregar la figura el documento pasó de 145 a **146 páginas** y todo lo que está después
del Anexo A corrió una página: el Anexo B pasó de 83 a 84, el C de 94 a 95, y así. **Por eso
los índices se rehicieron después de insertar la figura**, no antes.

**Regla que sale de acá:** insertar primero todas las figuras y recién al final rehacer los
índices: cualquier imagen movida corre las páginas de todo lo que sigue.

### 2.9 La Figura 1 del tablero estaba congelada

**Síntoma.** El tablero de tareas que se ve en la Figura 1 del documento mostraba la tarjeta
«Calibrar el sensor de TDS con el patrón de 707 ppm» **todavía en el backlog**, con 40 tareas
terminadas, cuando la calibración ya estaba hecha.

**Diagnóstico.** El tablero fuente —`docs/TABLERO.md`— **sí estaba al día**: la tarea T-32
figura en «Hecho» de la Semana 5 y el backlog está vacío. Lo que había quedado viejo era **la
figura dibujada**: el programa que la dibuja leía la línea de estado **del cierre de semana**, y
como esa línea decía «40 terminadas · 1 en curso · 1 en el backlog», la figura se quedaba en ese
punto. Además, el programa **se niega a dibujar** si el resumen no coincide con las tarjetas de
las columnas: con el tablero al día y el resumen viejo, la comprobación fallaba.

**Corrección.** El programa ahora lee **la última línea de estado** del tablero, sea del cierre
de una semana o de una fecha, y limpia las marcas de negrita antes de leer los números. Se
regeneró la figura y se reemplazó la del documento: **backlog vacío, 1 en curso, 41 terminadas**,
con la T-32 del TDS en la Semana 5. La leyenda pasó de «al cierre de la Semana 4» a «al 6 de
octubre de 2026».

**De paso se corrigió otro defecto del programa:** informaba las rutas tomando su propia carpeta
en vez de la raíz del proyecto, y al ejecutarlo desde `Proyecto SIGVACH/scripts/` **fallaba antes
de dibujar nada**.

**Regla que sale de acá:** el tablero versionado es la **única fuente**; la figura se regenera
desde él y **nunca se dibuja a mano**, porque una figura escrita a mano se desincroniza sola.

---

## 3. Estado del documento al cerrar la sesión

| Dato | Valor |
|---|---|
| Páginas | 147 |
| Palabras | 27 407 |
| Cuerpo (capítulos y bibliografía) | páginas impresas 1 a **38** |
| Anexo A | arranca en la página impresa 41 |
| Tablas numeradas | 20 |
| Figuras numeradas | 48 |
| Anexos | 7 (A a G) |
| Dibujos incrustados | 51 |
| Entradas de índice sueltas en el cuerpo | 0 (se quitaron 7) |
| Figuras del Anexo A | **32 de 32** |
| Peso del `.docx` / del `.pdf` | 7,61 MB / 3,06 MB |

El cuerpo termina en la página impresa **38**: sigue dentro del límite de 30 a 40 páginas que
pide la norma, con dos páginas de margen.

**Ya no falta ninguna captura.** La A.6 se insertó (apartado 2.8), así que el Anexo A queda
completo con sus 32 figuras y el texto que la anunciaba ya tiene su imagen.

**Lo que queda por hacer** es subir el entregable: el `.docx` y el `.pdf`, con el nombre
`Santos_Freddy_E4.pdf`, a la plataforma y al SharePoint, al menos un día antes de la tutoría.

---

## 4. Reglas que salieron de esta sesión

1. **La exportación del PDF, siempre en su propia invocación** (`exportar_pdf.ps1`), con Word cerrado, una sola instancia, desde una copia y sin rango de páginas. Así tarda unos 15 segundos. **No encadenarla** con el script de los índices: si el mismo proceso ya usó Word, se traba. Si se demora más de lo normal, **no esperar**: cortar y repetirla.
2. **El tablero versionado es la única fuente de la figura del tablero:** se regenera desde `docs/TABLERO.md`, nunca se dibuja a mano.
3. **Nunca borrar el PDF bueno antes de exportar:** exportar a un temporal y reemplazar al final.
4. **Insertar primero todas las figuras y rehacer los índices al final:** cualquier imagen que se agregue o crezca corre las páginas de todo lo que sigue.
5. **Para saber en qué página está algo, recorrer los párrafos; no buscar el texto**, porque la leyenda puede estar mencionada antes en el cuerpo.
6. **Los números de página del script no son los del lector:** el cuerpo se numera desde 1, pero arranca en la página física 10.
7. **Lo que se sube a la plataforma es el `.docx` y el `.pdf`**, y el archivo se llama `Santos_Freddy_E4.pdf`.
8. **Abrir Word siempre por PID y solo cerrar las instancias sin ventana**, para no tocar el trabajo del usuario.

---

## 5. Pendientes al cerrar

- [x] Insertar la captura **A.6** (hecho: `A6.1.jpg`, con `insertar_figura_a6.py`).
- [x] Regenerar la **Figura 1 del tablero** desde `docs/TABLERO.md` y reemplazarla en el documento.
- [ ] Si el tablero cambia antes de la entrega: regenerar la figura (`scripts/generar_figura_tablero.py`), reemplazarla (`reemplazar_figura_tablero.py`), rehacer los índices y exportar el PDF, en ese orden.
- [ ] Subir el **E4** (`.docx` y `.pdf`) a la plataforma y al SharePoint, al menos un día antes de la tutoría.
- [ ] Responder el **Cuestionario Q4** cuando el docente lo habilite.
- [ ] Con la maqueta armada: **restaurar el firmware de producción** (ahora tiene la versión de prueba, que no publica a la nube) y volver a medir con las sondas ya instaladas.
- [ ] Corregir en la aplicación el separador de miles y la visibilidad del mensaje de error.
- [ ] Guardar las capturas del Anexo A como evidencia en el repositorio.
