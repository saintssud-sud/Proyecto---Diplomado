# Pendientes de la entrega E4 — recordatorio

Estado al **9 de octubre de 2026, madrugada**. Todo lo que queda por hacer, en el orden en
que conviene hacerlo. Sale de las correcciones del E3 (`Recomendaciones_E3_T4.txt`, tutoría T4).

---

## 0. El E4 va con el formato de MONOGRAFÍA  ⏰ *recordar*

**No** con el formato de perfil de proyecto que usaron el E1, el E2 y el E3.

El E4 ya está armado sobre la estructura de monografía —portada, índice, capítulos 1 a 3,
bibliografía y anexos— y con la tipografía de la norma (Arial 12, interlineado 1,5, márgenes
4/3/3/3 en carta). Lo que falta es **verificarlo punto por punto contra el documento de
lineamientos**, antes de la pasada final al documento:

- [ ] Leer `Lineamientos-Tecnicos-Trabajo-Final-Diplomado-Desarrollo-Web-y-Apps-Moviles.pdf` y `Formato-Trabajo-Final-Diplomado-Distintas-Areas.pdf` (el que corresponda a Desarrollo Web y Apps Móviles).
- [ ] Comprobar la **portada** contra el modelo de la norma (sin la línea de entregable que se quitó).
- [ ] Comprobar los **apartados obligatorios** de la monografía y que no quede ninguno con nombre de perfil de proyecto (planteamiento, aspectos administrativos, cronograma).
- [ ] Comprobar el **resumen / abstract**, las palabras clave y la paginación (preliminares en romanos, cuerpo desde 1).
- [ ] Comprobar las **citas y referencias** contra la norma que pide el documento (Harvard / ISO 690).
- [ ] Comprobar el **límite de páginas** del cuerpo (hoy 38; el tope es 40) después de los cambios de la pasada final.

---

## 1. CP-22 — Usabilidad con tres personas  ⏰ *recordar*

**Qué pide el docente:** el caso CP-22 (usabilidad, RNF-06) está en «Parcial» porque la sesión
con usuarios **no se ejecutó**. Es de 15 minutos por persona.

**Cómo se hace (no tiene misterio):**

1. Buscar **tres personas** que no hayan usado nunca el sistema (familiar, compañero, vecino). No hace falta que sepan de hidroponía: **justamente se prueba que no hagan falta conocimientos previos**.
2. Darle a cada una **solo el enlace** `https://sigvach26-bd.web.app` y las credenciales de la cuenta de operador. Nada de explicaciones.
3. Cronometrar y anotar, por persona, si logró **sin ayuda** estas cinco tareas:
   - entrar al sistema,
   - ver el estado del cultivo (las seis variables),
   - consultar el historial de una variable,
   - registrar una medición a mano,
   - atender una alerta.
4. Anotar también: si preguntó algo, cuánto tardó y qué le costó más. **Un tropiezo es un dato, no un fracaso**: sirve para la tabla.
5. Guardar la evidencia: la planilla con los tres registros y, si se puede, una captura de cada persona usando la aplicación (con su permiso).

**Con eso se cierra el caso:** pasa de «Parcial» a «Aprobado» si dos de las tres personas
completan las cinco tareas sin ayuda, y queda la tabla con los tiempos.

**Lo que preparo yo cuando digas:** el guion de las cinco tareas para imprimir y la planilla
de registro (una fila por persona).

---

## 2. Medición en vivo en la tutoría T4

El docente quiere ver, en vivo:

- `GET /api/v1/usuarios` → **401** sin token, **403** con la cuenta de operador, **200** con el administrador.
- Una lectura del dispositivo con **`X-Device-Key` inválida** → **401**.

El programa ya está: `backend/pruebas/` y el archivo de cuentas de prueba del 29 de septiembre.
Solo hay que ejecutarlo delante del docente.

---

## 3. Subir el entregable

- `Santos_Freddy_E4.docx` y `Santos_Freddy_E4.pdf` → **plataforma (Moodle) y SharePoint**.
- El archivo se llama `Santos_Freddy_E4.pdf`.
- Regla del docente: **al menos un día antes de la tutoría**.

---

## Lo que ya quedó cerrado (para no repetirlo)

| Punto de la recomendación | Estado |
|---|---|
| Open-Meteo fuera del documento | **Hecho**: 0 menciones en el E4. |
| 2.9 (Render, Firebase Hosting, monitor de `/api/v1/salud`) | **Hecho**: el apartado existe. |
| Capítulo 3 con una conclusión por objetivo | **Hecho**: seis objetivos, uno por párrafo. |
| Extensión del cuerpo (límite 30–40 páginas) | **Hecho**: 38 páginas. |
| Detalle de los casos de prueba a anexos | **Hecho**: 24 casos en la tabla G.9 del Anexo G. |
| CP-24 (RNF-01 «No cumple») | **Hecho y medido** el 9 de octubre contra el servicio publicado: con 200 registros el p95 bajó de 1042 a **427 ms** y con 50 registros de 984 a **406 ms**; en los dos casos 20 de 20 consultas dentro del objetivo de 800 ms. Evidencia en `evidencia/rendimiento-2026-10-09-*.txt`. |
| `DELETE /api/v1/lecturas/{id}` → anulación con motivo (A-01, RNF-08) | **Hecho**: la ruta de borrado ya no existe (405) y en su lugar está `POST /api/v1/lecturas/{id}/anulacion`, con motivo obligatorio. Verificado en vivo: el operador recibe 403, el administrador anula (200), el registro se conserva consultable y anular dos veces da 409. Evidencia en `evidencia/anulacion-2026-10-09.txt`. |
| Cerrar CP-06, CP-11 y CP-19 (los «Parcial» baratos) | **CP-11 y CP-19 verificados en vivo** (los tres filtros juntos responden 200 en 0,45 s con el índice compuesto, y la exportación filtrada devuelve el CSV). **CP-06**: la mitad de la baja queda cerrada con la anulación; la de modificación queda por registrar. |
| 2.7 en cinco apartados (2.7.1 a 2.7.5) | **Pendiente** (documento, una sola pasada al final). |
| 2.3.1: nombrar el rol de solo consulta | **Pendiente** (documento, una sola pasada al final). |
| Actualizar el documento con todo lo de arriba | **Pendiente**: la tabla G.9 (CP-24, CP-11, CP-19), el conteo de pruebas de 2.8 (149 → **152** del servicio), la tabla del contrato (la anulación en lugar del borrado) y el enunciado del RNF-01 con la medición nueva. |

### Índice de Firestore agregado el 9 de octubre

`firestore.indexes.json` incorpora el índice compuesto de `lecturas` por
**módulo, variable y fecha**, que es el que necesitan los tres filtros juntos de la pantalla
de historial. Ya está desplegado en el proyecto `sigvach26-bd`.
