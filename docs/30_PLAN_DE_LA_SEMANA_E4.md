# Plan de la semana del E4 — 5 al 13 de octubre de 2026

Documento interno de trabajo. No forma parte de la monografía.
Complementa a `09_PLAN_MODULO4.md`, que tiene el calendario general del módulo.

---

## 1. El cambio de agenda, y qué implica

| Antes | Ahora |
|---|---|
| Tutoría 4 el **martes 6 a las 17:00** | **Viernes 9 a las 17:00** — el martes 6 no hay actividad; los Grupos 3 y 4 pasan al viernes |
| E4 con cierre interno el viernes 9 a las 23:59 | **Igual**, pero ahora **coincide con la tutoría** |

**Consecuencia práctica, y es la decisión que ordena toda la semana:** el E4 tiene que estar
**subido antes de la tutoría del viernes por la mañana**. Si se sube a las 23:59 del viernes, la
tutoría se aprovecha a ciegas; si se sube antes, la reunión sirve para corregir sobre algo que el
tutor ya puede mirar. El sábado 10 a las 23:59 sigue siendo el cierre oficial y funciona como
colchón, pero no hay que planificar trabajo para ese día: los sábados no están disponibles.

| Fecha | Hito | Qué tiene que estar cerrado |
|---|---|---|
| **Lun 5** | Trabajo de documento | Recorte de extensión y estructura del E4 |
| **Mar 6** | Sin clase: día completo de trabajo | Capítulo 3 y apartado 2.9 |
| **Mié 7** | Trabajo de documento | Anexos, figuras y referencias cruzadas |
| **Jue 8** | Revisión final | Documento cerrado y verificado; preparación de la tutoría |
| **Vie 9, mañana** | **Subida del E4** | Documento en editable y PDF, con la evidencia ya dentro |
| **Vie 9, 17:00** | **Tutoría 4 (Grupo 3)** | Preguntas y correcciones sobre lo ya subido |
| Vie 9, 23:59 | Cierre interno de E4 | — |
| Sáb 10, 23:59 | Cierre oficial de E4 (colchón) y cuestionario Q4 | — |
| Dom 11 y lun 12 | Preparación de la defensa | Guion de 7 minutos ensayado y maqueta estable |
| **Mar 13, 17:00** | **Defensa técnica** | 7 minutos de demostración en vivo y 5 de preguntas |

---

## 2. Lo que falta para el E4, por bloque

### 2.1 Documento

| Qué | Estado | Detalle |
|---|---|---|
| Extensión del cuerpo | **Pendiente, es lo más pesado** | El límite es de 30 a 40 páginas **sin preliminares ni anexos**. El cuerpo lo supera. Las medidas de recorte ya están escritas en el borrador; hay que aplicarlas y volver a medir |
| Recorte por traslado | Pendiente | Mover a anexos lo que es documentación de soporte y no cuerpo: la tabla de casos de prueba y los manuales |
| Apartado 2.9 Despliegue | Pendiente | Plataforma, procedimiento, entornos, dirección pública, límites del plan gratuito y el respaldo con la restauración probada |
| Capítulo 3 | Borrador hecho | Una conclusión por objetivo específico, con grado de cumplimiento y evidencia concreta; más recomendaciones |
| Preliminares | En buena parte automático | El conversor genera portada, contratapa, hoja de aprobación, advertencia, los tres índices como campos de Word, **numeración romana hasta el Capítulo 1** y arábiga desde ahí |
| Anexos A a F | Escritos | Manual de usuario, manual de instalación y despliegue, repositorio con acceso para el tribunal, dirección pública y APK, diagramas legibles y documentación complementaria |
| Resumen | Hecho | 290 palabras, por debajo del máximo de 300 |
| Pendientes manuales en Word | Pendiente | Escudo de la universidad, nombres del tribunal, nombre completo del autor |

### 2.2 Evidencias que todavía faltan

| Evidencia | Cómo se consigue | Prioridad |
|---|---|---|
| **CP-24 · Rendimiento con número antes y después** | Se declaró «no cumple» con 200 registros y sí cumple con el tamaño que usa el panel. Hay que medir después de la corrección y dejar los dos números | Alta: es una promesa del E3 |
| **CP-22 · Usabilidad con tres personas** | Tres personas que no conocen el sistema realizan las tareas del guion, con fecha y observaciones | Alta |
| **CP-19 · Exportación en CSV** | Descarga desde el navegador contra la dirección pública, con la URL y la fecha visibles | Media |
| **RNF-01 en el panel** | Cronometrar la carga del panel en el navegador: el requisito pide 3 segundos o menos | Media |
| **Monitoreo de disponibilidad** | Algo externo consulta `/api/v1/salud` y avisa si falla. El visor de escritorio ya consulta el servicio cada 15 segundos y sirve como punto de partida | Media |
| **Respaldo con restauración probada** | Exportar la base y restaurarla en un entorno de prueba, con la constancia | Media |

Las capturas tienen que mostrar **la dirección pública y la fecha**, con datos de prueba, y sin
recortes que oculten esas dos cosas.

### 2.3 Sistema

| Qué | Estado |
|---|---|
| Servicio publicado | Operativo, con TLS y certificado validado |
| Aplicación web publicada | Operativa |
| Módulo de adquisición | Publicando cada ~5 minutos y media, con cola de respaldo si no hay red |
| Sensores | pH calibrado y verificado; temperatura y humedad verificadas; **TDS pendiente de calibrar** cuando llegue el patrón de 1413 µS/cm |
| Maqueta | Falta armarla y dejarla funcionando sola (módulo alimentado con cargador, no con la PC) |

---

## 3. Plan día por día

### Lunes 5 — el recorte, que es lo único que crece solo

1. **Medir el documento como está**: páginas del cuerpo sin preliminares ni anexos, para saber cuánto hay que recortar.
2. **Aplicar el recorte por traslado** (lo que no pierde contenido): tabla de casos de prueba y manuales a los anexos.
3. **Escribir 2.9 Despliegue**, que hoy es el hueco más grande del cuerpo y además es contenido obligatorio.
4. Si queda tiempo: preparar el guion de las tres personas para CP-22 y pedirles el turno para el martes.

### Martes 6 — sin clase, día completo

1. **Cerrar el Capítulo 3** con una conclusión por objetivo específico, cada una con su evidencia.
2. **Ejecutar CP-24** (medición de rendimiento con el número antes y después) y **CP-22** (las tres personas).
3. **Ejecutar CP-19** (exportación CSV) y la medición del panel para RNF-01.
4. Armado de la maqueta, si el hardware está disponible.

### Miércoles 7 — anexos y coherencia

1. Revisar los anexos A a F y **completar el Anexo D** con la dirección pública y el archivo instalable.
2. Verificar **todas** las referencias cruzadas y la numeración de tablas y figuras.
3. Regenerar el documento y **volver a medir la extensión**.
4. Rehacer la figura del tablero con el estado real de la semana.

### Jueves 8 — revisión final y preparación de la tutoría

1. **Revisión de extremo a extremo** contra la lista de `27_LO_QUE_PIDE_LA_PLENARIA_P4.md` y la auditoría de `11_AUDITORIA_CUMPLIMIENTO.md`.
2. **Exportar a PDF** y comprobar el índice, la numeración romana y la arábiga.
3. **Preparar la tutoría**: las preguntas pendientes (colocación del epígrafe de las figuras, alcance del E4, qué espera del sistema en la defensa) y la explicación de la corrección de la Tabla 3 del E3.
4. Ensayo corto del guion de la defensa, sin público.

### Viernes 9 — subir y después la tutoría

1. **Por la mañana: subir el E4** (editable y PDF) y responder el cuestionario si ya está disponible.
2. **17:00 · Tutoría 4**: llegar con el documento subido y con las preguntas escritas. Anotar cada observación del tutor con la hora.
3. Cerrar el cierre interno a las 23:59 solo si hubo correcciones que valga la pena subir.

### Sábado 10 — colchón (sin trabajo previsto)

Cierre oficial a las 23:59 y cuestionario Q4.

### Domingo 11 y lunes 12 — la defensa

1. Ensayar el guion de 7 minutos **cronometrado**, al menos tres veces.
2. Dejar la maqueta funcionando sola y comprobar la señal del WiFi en el lugar de la defensa.
3. **Despertar el servicio** un minuto antes de cada ensayo: la capa gratuita se suspende por inactividad y la primera petición puede tardar hasta un minuto.
4. Preparar las respuestas a las preguntas previsibles (`21_PREGUNTAS_PARA_LA_TUTORIA.md` y el mapa del repositorio).

### Martes 13, 17:00 — defensa

7 minutos de demostración en vivo del sistema desplegado y 5 de preguntas.

---

## 4. Riesgos de esta semana, y su mitigación

| Riesgo | Mitigación |
|---|---|
| **El recorte de extensión se come el martes entero** | Es lo primero del lunes, y el traslado a anexos no pierde contenido: si el tiempo aprieta, se traslada más y se recorta menos |
| **El hardware falla justo el día de la defensa** | La demostración se apoya en el sistema desplegado, no en el módulo. El módulo es el valor agregado; si falla, la defensa sigue en pie |
| **El TDS no llega calibrado** | Se declara como pendiente con el procedimiento escrito. Es una limitación honesta, no un hueco |
| **La capa gratuita del servicio está dormida en plena demostración** | Calentamiento con `/api/v1/salud` un minuto antes, ya previsto en el guion |
| **La tutoría del viernes revela correcciones grandes** | El cierre oficial del sábado queda como colchón, y el viernes se sube temprano justamente para que la reunión sirva |

---

## 5. Lo que no hay que olvidar llevarle al tutor el viernes

1. La **corrección de la Tabla 3** del E3, con la explicación de por qué no se volvió a subir el archivo.
2. La pregunta sobre **dónde va el epígrafe de las figuras**: la plantilla oficial y el módulo se contradicen.
3. **Qué espera del sistema en la defensa** y qué peso tiene el hardware frente al software.
4. Los dos **casos fallidos registrados** —la corrección del manejador de WiFi y la limitación del agua de baja mineralización—, que valen más que una tabla donde todo pasó.
