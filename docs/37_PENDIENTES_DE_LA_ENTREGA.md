# Pendientes de la entrega E4 — recordatorio

Estado al **9 de octubre de 2026, madrugada**. Todo lo que queda por hacer, en el orden en
que conviene hacerlo. Sale de las correcciones del E3 (`Recomendaciones_E3_T4.txt`, tutoría T4).

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
| 2.7 en cinco apartados (2.7.1 a 2.7.5) | **Pendiente** (documento, una sola pasada al final). |
| 2.3.1: nombrar el rol de solo consulta | **Pendiente** (documento, una sola pasada al final). |
| CP-24 (RNF-01 «No cumple») | **En curso**: índice compuesto + límite, con medición antes y después. |
| `DELETE /api/v1/lecturas/{id}` → anulación con motivo (A-01, RNF-08) | **En curso**. |
| Cerrar CP-06, CP-11 y CP-19 (los «Parcial» baratos) | **Pendiente**. |
