# CP-22 — Guion para la prueba de usabilidad con tres personas

Esto es lo que pide el docente para cerrar el caso **CP-22** (usabilidad, RNF-06), que hoy
figura como «Parcial» porque la sesión con usuarios no se ejecutó.

**Qué necesitás:** tres personas que **no hayan usado nunca el sistema** (familiar, compañero,
vecino). No hace falta que sepan de hidroponía: **se prueba justamente que no hagan falta
conocimientos previos**. Quince minutos por persona.

**Qué necesitás tener a mano:** el enlace `https://sigvach26-bd.web.app` y las credenciales de
la cuenta de **operador**. Nada más.

**Regla de oro:** no les expliques cómo usar la aplicación. Si preguntan algo, anotá la pregunta
y respondé «probá vos». Un tropiezo es un dato valioso, no un fracaso tuyo.

---

## Guion para darle a cada persona (copiá y pegá, o imprimí)

> Te voy a pedir que hagas cinco cosas en una aplicación web de monitoreo de cultivos
> hidropónicos. No conozco tu experiencia previa y no importa: quiero ver cómo te manejás vos
> sola/o. Si algo no se entiende, decilo en voz alta. No hay respuestas incorrectas.
>
> Entrá a **https://sigvach26-bd.web.app** con el correo **operador@proyecto.test** y la clave
> que te doy en papel en este momento.
>
> 1. **Entrá al sistema** y decime cuál es el nombre de la cuenta con la que entraste.
> 2. **Mirá cómo está el cultivo ahora**: ¿qué valores tienen las seis variables?
> 3. **Consultá cómo evolucionó el pH** en los últimos días.
> 4. **Registrá una medición a mano**: por ejemplo, que la temperatura del agua es 21,5 °C.
> 5. **Atendé la alerta** que está activa y contame qué pasó con ella después de atenderla.

---

## Planilla de registro (llená una columna por persona)

| # | Tarea | Persona 1 | Persona 2 | Persona 3 |
|---|---|---|---|---|
| | Nombre o iniciales | | | |
| | Edad aproximada | | | |
| | ¿Usó antes una aplicación parecida? | | | |
| 1 | Entró al sistema — ¿lo logró sin ayuda? / tiempo | | | |
| 2 | Vio las seis variables — ¿sin ayuda? / tiempo | | | |
| 3 | Consultó el historial del pH — ¿sin ayuda? / tiempo | | | |
| 4 | Registró una medición — ¿sin ayuda? / tiempo | | | |
| 5 | Atendió la alerta — ¿sin ayuda? / tiempo | | | |
| | **Tareas logradas sin ayuda (de 5)** | | | |
| | Tiempo total | | | |
| | Qué fue lo que más le costó | | | |
| | ¿Pidió ayuda? ¿en qué momento? | | | |
| | Comentarios que dijo | | | |

**Evidencia a guardar** (en `evidencia/`):
- esta planilla completada, como `usabilidad-2026-10-XX-planilla.txt`;
- una captura o foto de cada persona usando la aplicación, con su permiso
  (`usabilidad-2026-10-XX-persona-1.jpg`, etc.);
- si alguna persona lo permite, una captura del historial de la sesión.

---

## Cómo se cierra el caso

1. **Criterio:** el caso se aprueba si **al menos dos de las tres personas** completan las cinco
   tareas sin ayuda. Si dos lo logran y una se traba en el registro manual, el caso se aprueba
   **y anotás el tropiezo** como mejora recomendada (eso suma, no resta).
2. Se actualiza la fila de **CP-22 en la tabla G.9** del documento: de «Parcial» a «Aprobado»,
   con el resumen en la columna del resultado obtenido (por ejemplo: «3 usuarios, 15 min cada
   uno; 5 de 5 tareas en dos de ellos y 4 de 5 en el tercero»).
3. Se agrega el párrafo de usabilidad en el apartado **2.8** con los números medidos y la
   referencia a la evidencia.

---

## Emparejado con el guion que ya existe

Las cinco tareas son las del **manual de usuario (Anexo A)**, que ya está escrito y con sus
capturas: entrar al sistema, consultar el estado del cultivo, ver la evolución de una variable,
registrar una medición a mano y atender una alerta. No hay que inventar nada nuevo: la prueba
comprueba que ese manual coincide con lo que la gente hace de verdad.
