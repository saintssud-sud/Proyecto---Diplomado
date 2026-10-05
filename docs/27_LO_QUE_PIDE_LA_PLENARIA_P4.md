# 27 · Lo que pide la plenaria P4, comparado con lo que tenemos

**Fuente:** `P4_Pruebas_Despliegue_Defensa_Modulo4.pdf` — plenaria del martes 29 de septiembre de
2026, 19:00 a 20:30, M.Sc. Ing. Isaac Lange Aguilar. **Fue la última plenaria.**
**Para qué sirve este archivo:** es la lista de trabajo del E3 y del E4, cotejada contra lo que el
proyecto ya tiene. Cada fila marcada con ✗ es una acción pendiente.

---

## 1. Las cinco fallas que se repitieron en el E2, y dónde estamos

| Falla que se repitió en el E2 | Qué pide la plenaria | Cómo estamos |
|---|---|---|
| Nada que revisar en producción (10 de 28) | Desplegar antes de programar | ✓ Aplicación web y servicio publicados, con `/api/v1/salud` respondiendo |
| Salud ausente o fuera del contrato (7 de 28) | `GET /api/v1/salud`, y que **consulte la base** | ✓ Existe y responde `{"estado":"ok","base_de_datos":"conectada"}`: consulta la base de verdad |
| **Credenciales reales o débiles** (9 de 28) | **Una cuenta `@proyecto.test` por rol, con contraseña de 10 o más caracteres** | ✗ **Las cuentas de prueba son `mateosantos@yahoo.es` y `tecnico@gmail.com`, con contraseñas de 6 y 6 caracteres. Hay que crear dos cuentas nuevas y ficticias** |
| Restos de plantilla y de asistente (13 de 28) | Buscar `[`, `**` y «Verificación» en el documento antes de exportar | ✗ Por hacer en el documento del E3 |
| El Capítulo 2 no es lo desplegado | 2.6 con lo construido, una decisión y una dificultad | ✓ Escrito sobre lo que corre |

> **Las cuatro señales de una vertical sana:** salud que consulta la base ✓ · la regla vive en el
> servidor ✓ · una dificultad de verdad contada con su resolución ✓ · una cuenta ficticia por rol ✗.

**Acción 1 (de hoy):** crear dos cuentas `@proyecto.test`, una por rol, con contraseña de 10 o más
caracteres; retirar de circulación las dos actuales. La plenaria lo pide de forma explícita y es una
de las fallas más repetidas del grupo.

---

## 2. Pruebas con evidencia · apartado 2.8

### 2.1 La tabla de casos

Formato exigido por los lineamientos 3.2.8: **ID · escenario · esperado · obtenido · estado**.
La columna «obtenido» dice lo que se observó (código, mensaje, tiempo) **y dónde está la evidencia**.

Mínimo por nivel:

| Nivel | Mínimo para el E3 | Cómo estamos |
|---|---|---|
| Unitaria | Dos o tres funciones con reglas de negocio: validaciones, totales, transiciones de estado | ✓ Hay pruebas de servicio y de aplicación, falta contarlas y citarlas por función |
| Integración (API + base) | **Cada ruta Must con camino feliz y error**, incluidos 401 y 403 | ✓ 106 pruebas del servicio; el 401, el 403 y el 422 ya están medidos contra producción |
| Funcional (de punta a punta) | El flujo Must completo desde la interfaz, **en producción, con capturas fechadas** | ✗ Falta el recorrido con capturas fechadas de la URL pública |
| Rendimiento | **Una medición del RNF de tiempo sobre la URL pública** | ✗ Falta la medición y su número |

> **Guarda la plenaria:** «Un caso fallido registrado vale más que una tabla donde todo pasó». Hay que
> incluir al menos un caso **fallido** con su commit de corrección y su reejecución. Tenemos tres
> candidatos reales: la unidad del dato de temperatura que el servicio rechazaba con 422, la
> aplicación publicada apuntando a `127.0.0.1`, y el AM2302 con el error de la fase 'B'.

### 2.2 Qué evidencia vale

| Vale | Cómo estamos |
|---|---|
| Captura fechada en producción, mostrando la URL pública y datos ficticios, numerada como figura | ✗ Por hacer |
| Reporte del runner en el repositorio, en `/evidencia`, con fecha | ✗ Los informes no están versionados |
| El fallo con su corrección: caso fallido, commit que lo corrige y reejecución | ✓ Existen los tres casos, falta armar la fila |
| La medición del RNF, con la herramienta y la cantidad de registros declaradas | ✗ Por hacer |

**No vale:** «funciona», capturas de `localhost`, recortes sin URL ni fecha.

**Acción 2:** crear la carpeta `evidencia/` en el repositorio y guardar ahí las salidas de `pytest` y
de `flutter test` con la fecha en el nombre del archivo.

---

## 3. Del despliegue al despliegue verificado

| Pieza | Qué pide | Cómo estamos |
|---|---|---|
| Pipeline | Push → pruebas → construcción → despliegue → verificación de salud | ✗ No hay. **Es opcional para el E3**: «sin pipeline, el procedimiento manual se documenta paso a paso en 2.9». Suma, y su ausencia documentada no resta |
| Monitoreo de disponibilidad | Un servicio externo consulta `/api/v1/salud` y avisa si falla | ✗ Es del **E4** |
| Errores, registros, respaldo, límites del plan | Sentry o logs, una línea por petición, respaldo con restauración probada, y las limitaciones declaradas | ✗ Es del **E4**, en el apartado 2.9 |
| Rendimiento | Medir **antes** de optimizar, con número antes y después | ✗ La medición es del **E3**; la optimización, del E4 |

---

## 4. El documento

### 4.1 Lo que falta escribir

| Apartado | Contenido exigido | Cuándo |
|---|---|---|
| **2.7 Seguridad** | Autenticación y sesiones, autorización por rol, validación, cifrado de credenciales y de comunicaciones, gestión de secretos | **E3** |
| **2.8 Pruebas** | Plan por niveles y tabla de casos con ID, escenario, esperado, obtenido y estado, con la evidencia referida | **E3** |
| **2.9 Despliegue** | Plataforma, procedimiento, entornos, URL pública, y en móvil la distribución y el instalable. Limitaciones del plan | E4 |
| **Capítulo 3** | Una conclusión por objetivo específico, con grado de cumplimiento y evidencia. Recomendaciones | E4 |
| **Anexos** | Manual de usuario, manual de instalación y despliegue, repositorio, URL o APK, diagramas legibles | E4 |

### 4.2 Formato

| Exigencia | Cómo estamos |
|---|---|
| **De 30 a 40 páginas**, sin preliminares ni anexos | ✗ Por verificar con el documento del E3 ya armado |
| **Resumen de 300 palabras como máximo** | ✗ Por verificar |
| Preliminares completos: portada, índices de contenido, de tablas, de figuras y de anexos, con numeración romana hasta el Capítulo 1 | ✓ El formato institucional ya está aplicado |
| Conclusiones: cada una con su evidencia, no con adjetivos | ✓ Criterio ya adoptado; hay que escribirlas con el número adentro |

**Ejemplo de la plenaria**, que conviene imitar: en lugar de *«se aplicó seguridad»*, escribir
*«cumplido: token de 60 minutos, contraseñas con hash del proveedor y control de rol en cada ruta
protegida; los casos de 403 aprobados (Tabla 19)»*.

---

## 5. La defensa · T5, del 12 al 15 de octubre

Doce minutos por persona: **siete de demostración y cinco de preguntas**, con cronómetro.

| Tramo | Qué se muestra |
|---|---|
| 0:00 – 1:00 | Problema y usuario: quién usa el sistema, qué hacía antes y qué dato lo prueba |
| 1:00 – 4:30 | **El flujo Must completo en producción**, entrando con el usuario de prueba |
| 4:30 – 5:30 | **Seguridad en vivo**: un rol intenta lo que no le corresponde y la API responde 403 |
| 5:30 – 7:00 | Evidencia: tabla de pruebas, repositorio con historial y monitoreo en línea |
| 7:00 – 12:00 | Preguntas, con el sistema abierto |

**Una diapositiva como máximo** para el problema, y **a los 7 minutos se corta la demostración**.
Se ensaya con cronómetro en la tutoría T4.

### 5.1 Las ocho preguntas que se hacen en la defensa

| # | Pregunta | Dónde está nuestra respuesta |
|---|---|---|
| 1 | ¿Dónde se verifica el rol? | `backend/app/seguridad.py`: `requiere_administracion`, `requiere_operacion`, `requiere_consulta`. El 403 ya está medido contra producción |
| 2 | **¿Qué pasa si el token vence?** | La API responde 401. **La aplicación todavía no vuelve al inicio de sesión: hay que implementarlo** ✗ |
| 3 | ¿Cómo guarda las contraseñas? | Con el *hash* del proveedor de identidad; nuestro servicio nunca ve la contraseña |
| 4 | ¿Dónde están los secretos? | En variables de entorno de la plataforma; el repositorio tiene `.env.example` con los nombres y sin valores, y hay un verificador que lo comprueba |
| 5 | ¿Por qué este stack? | Cada elección justificada contra un requisito por su ID |
| 6 | ¿Cómo sabe que funciona? | Una fila de la tabla de pruebas con su evidencia |
| 7 | ¿Qué pasa si se cae? | Monitoreo, respaldo y procedimiento de redespliegue (E4) |
| 8 | ¿Qué quedó pendiente? | Lo declarado como *Won't have* y las recomendaciones, sin esconderlo |

> **Regla de la defensa, textual:** «Quien no ejecuta ni explica su sistema, no aprueba la defensa.
> La falta de dominio técnico anula el componente, con independencia de quién haya escrito el código.
> Usar IA está permitido; no entender lo que entregó, no.»
>
> Por eso hace falta, antes del 12 de octubre, un **mapa del repositorio**: dónde está cada cosa que
> se puede preguntar, con la ruta del archivo y la línea. Ver la acción 5.

Pueden pedir **un cambio pequeño en vivo**: un texto, una validación, un campo.

### 5.2 Rúbrica

| Criterio | Puntos |
|---|---|
| Sistema en producción | 25 |
| Dominio técnico | 30 |
| Seguridad demostrada (401 y 403 en vivo) | 15 |
| Pruebas y evidencia | 10 |
| Respuesta a preguntas | 15 |
| Tiempo y claridad | 5 |
| **Total** | **100** (vale el 20 % de la nota del módulo) |

---

## 6. Lo que cierra cada entrega

### 6.1 E3 · sábado 3 de octubre a las 23:59, con el cuestionario Q3

| Pieza | Qué se entrega | Estado |
|---|---|---|
| Autenticación y roles | Sesión que vence y autorización por rol **verificada en el servidor** en cada ruta protegida | ✓ Servidor sí · ✗ el cliente no vuelve al login con el 401 |
| Pruebas con evidencia | Tabla 2.8 con camino feliz y error de cada Must, casos de 401 y 403, y al menos una suite automatizada | ✗ Por armar |
| Documento | Capítulos 1 y 2 completos en borrador (2.1 a 2.8), con lo observado en el E2 corregido | ✗ Faltan 2.1, 2.7 y 2.8 |
| Sistema | Todos los Must en producción, con validación en cliente y en servidor | ✓ Verificado, falta la comprobación final ruta por ruta |
| Repositorio | Commits en días distintos, pruebas en el repositorio y README al día | ✓ Commits sí · ✗ informes de prueba y README |

> «Un rol que solo se esconde en el frontend no está implementado.» El nuestro se verifica en el
> servidor, así que ese punto está cubierto.

### 6.2 E4 · cierre interno el viernes 9, oficial el sábado 10 a las 23:59, con el cuestionario Q4

> **El E4 se sube antes de la tutoría del viernes 9 a las 17:00.** El cierre interno coincide con el
> día de la tutoría, así que el objetivo es tenerlo subido por la mañana y usar la reunión para
> corregir sobre lo ya entregado. El sábado 10 a las 23:59 sigue siendo el cierre oficial y funciona
> como colchón.

Documento completo (Capítulos 1, 2 y 3, preliminares, bibliografía y anexos) · despliegue verificado
el día de la entrega · los dos manuales como anexos · monitoreo y medición del rendimiento en
producción · repositorio final sin secretos.

---

## 7. Fechas que hay que tener escritas

| Cuándo | Qué |
|---|---|
| 28 de septiembre al 1 de octubre | Tutoría T3, en la franja del grupo (la del martes 29 fue corta) |
| **Sábado 3 de octubre, 23:59** | **E3 y cuestionario Q3** |
| 5 al 9 de octubre | Tutoría T4: revisión del E3, documento completo y **ensayo de la defensa** |
| **Viernes 9 de octubre, 17:00** | **T4 del Grupo 3** (el martes 6 no hay actividad; los Grupos 3 y 4 tienen su T4 el viernes a las 17:00 y 18:00) |
| **Viernes 9 de octubre, por la mañana** | **Subida del E4** — cierre interno a las 23:59 del mismo día |
| **Sábado 10 de octubre, 23:59** | **Cierre oficial del E4 y cuestionario Q4** (colchón) |
| 12 al 15 de octubre | T5: defensa técnica evaluada, 7 minutos de demostración y 5 de preguntas |
| Martes 13 de octubre, 17:00 | Franja del Grupo 3 para la defensa |

---

## 8. Las acciones, en orden

| # | Acción | Para qué | Cuándo |
|---|---|---|---|
| 1 | Crear **dos cuentas `@proyecto.test`**, una por rol, con contraseña de 10 o más caracteres | Es una de las fallas más repetidas del E2 y lo pide de forma explícita | Hoy o mañana |
| 2 | Que la aplicación **vuelva al inicio de sesión cuando el token vence** (401) | Es la pregunta 2 de la defensa y un requisito del E3 | Antes del viernes |
| 3 | Armar la **tabla 2.8** con ID, escenario, esperado, obtenido y estado, y un caso fallido con su corrección | Requisito central del E3 | Jueves |
| 4 | Guardar los **informes de `pytest` y `flutter test`** con fecha en `evidencia/` del repositorio, y corregir el README | Requisito del E3 | Jueves |
| 5 | **Medir el rendimiento en producción** sobre la URL pública, con la herramienta y la cantidad de registros declaradas | Nivel de rendimiento del E3 | Jueves |
| 6 | **Capturas fechadas** del flujo Must completo desde la interfaz, en producción | Nivel funcional del E3 | Viernes |
| 7 | Escribir **2.1, 2.7 y 2.8** del documento | Requisito del E3 | Viernes |
| 8 | Pasar el **control de limpieza** al documento: buscar `[`, `**`, «Verificación», «POR CONFIRMAR» | Falla repetida del E2, con −5 puntos | Antes de exportar |
| 9 | Armar el **mapa del repositorio para la defensa**: dónde está cada cosa que pueden preguntar | La regla dice que quien no explica su sistema no aprueba | Antes del 9 de octubre |
| 10 | **Ensayo con cronómetro** del guion de la defensa, de 7 minutos | Se ensaya en la T4 del viernes 9 | Viernes 9 |
