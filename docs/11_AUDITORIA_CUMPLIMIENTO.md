# Auditoría de cumplimiento — documento y producto

**Fecha:** 14 de septiembre de 2026
**Alcance:** verificación del trabajo final contra el *Formato para la Elaboración del Trabajo Final de
Diplomado* (Dirección de Posgrado, 2020), los *Lineamientos Técnicos Complementarios* (2026) y el
*P1 Apertura Módulo 4*.
**Método:** revisión punto por punto de cada exigencia normativa contra el documento y el repositorio, con
conteo automático de marcadores pendientes y de elementos de estilo.

Documento interno de trabajo. No forma parte de la monografía.

---

## 1. Aspectos formales (los rige el Formato 2020)

| Exigencia | Estado | Observación |
|---|---|---|
| Arial o Times New Roman 12 puntos, interlineado 1,5, espaciado 0,3 | ⚠️ | Depende de la plantilla: el borrador es texto plano y la tipografía se aplica al volcarlo en Word |
| Márgenes de 4 cm (izquierdo) y 3 cm (resto), papel carta | ⚠️ | Ídem |
| Numeración romana en preliminares y arábiga desde el Capítulo 1, abajo a la derecha | ⚠️ | Ídem |
| Preliminares completos (portada, contratapa, hoja de aprobación, hoja de advertencia, dedicatoria y agradecimientos opcionales, índices de contenido, tablas, figuras y anexos) | ❌ | No elaborados. El **resumen** sí existe y tiene 294 palabras, dentro del máximo de 300 |
| Extensión de 30 a 40 páginas sin preliminares ni anexos | ❌ | **Excede**: 15 305 palabras de cuerpo (≈41 páginas solo de texto) y entre 46 y 48 sumando tablas, fragmentos y figuras. Plan de recorte medido, dentro del borrador |
| Normas Harvard e ISO 690-2 | ✅ | 19 entradas en estilo ISO 690-2, orden alfabético verificado, con fecha de consulta |

## 2. Contenido técnico por capítulo (punto 3 de los Lineamientos)

### Capítulo 1

| Exigencia | Estado | Dónde |
|---|---|---|
| 3.1.1 Antecedentes: estado del conocimiento, **soluciones informáticas existentes** y desarrollos previos, con qué resuelven y qué dejan sin resolver | ✅ | 1.1.1, 1.1.2 (cuatro soluciones con fuente), 1.1.3 y Tabla 1 |
| 3.1.2 Descripción y planteamiento del problema, con los puntos críticos del proceso actual | 🟡 | 1.2 y 1.3 completos, pero **la caracterización con datos del contexto real sigue siendo referencial** ("treinta a sesenta minutos por jornada") |
| 3.1.3 Justificación con factibilidad técnica, pertinencia e impacto | ✅ | 1.4 |
| 3.1.4 Objetivo general con verbo de acción y objetivos específicos verificables | 🟡 | 1.5 completo, pero el objetivo específico 1 enumera **cuatro perfiles de usuario** y el producto implementa dos: depende de la decisión pendiente |

### Capítulo 2

| Exigencia | Estado | Dónde |
|---|---|---|
| 3.2.1 Fundamentos con autores y documentación oficial | ✅ | 2.1 (ESPressif, Firebase, Flutter citados en la bibliografía) |
| 3.2.2 Metodología con justificación y **evidencia de su aplicación** | ✅ | 2.2: iteración semanal justificada, Tabla 3 con fechas y estado, confirmaciones del repositorio, declaración del uso de asistentes de IA |
| 3.2.3 Requisitos: actores, requisitos funcionales con criterios de aceptación, no funcionales (rendimiento, seguridad, usabilidad, compatibilidad, disponibilidad) y **diagramas de casos de uso con su descripción textual** | 🟡 | 2.3.1 a 2.3.5 completos y la descripción textual está; **el diagrama está listo como código pero no incorporado como figura** |
| 3.2.4 Diseño: arquitectura con diagrama, modelo de datos **con diccionario**, diseño de interfaz con wireframes, y endpoints con parámetros y códigos de respuesta | 🟡 | Arquitectura y contrato ✅ (Tablas 5 y 6); **diccionario de datos agregado el 14/09** (Tabla 5, 28 filas); **faltan los wireframes** y el diagrama de arquitectura como figura |
| 3.2.5 Stack con versiones y justificación contra los requisitos | ✅ | 2.5 y Tabla 7 con las versiones reales |
| 3.2.6 Implementación: funcionalidades críticas, decisiones técnicas, **dificultades y su resolución**, fragmentos ilustrativos de hasta 20 líneas | ✅ | 2.6 reescrito: cinco subapartados, cinco dificultades reales, dos fragmentos verificados literalmente contra el código (12 y 18 líneas) |
| 3.2.7 Seguridad: autenticación, autorización por rol, validación, cifrado y variables sensibles | ✅ | 2.7 |
| 3.2.8 Pruebas: plan, ejecución y **tabla con identificador, escenario, resultado esperado, obtenido y estado** | 🟡 | Tabla 8 con 23 casos definidos y **23 resultados pendientes de ejecutar**; las pruebas automatizadas (59 del servicio y 63 de la aplicación) sí están ejecutadas y documentadas |
| 3.2.9 Despliegue: plataforma, procedimiento, configuración y **dirección pública** | ❌ | Pendiente el despliegue. El procedimiento está completo en el Anexo B y en la guía de despliegue |
| 3.3 Conclusiones en correspondencia con **cada** objetivo específico, con grado de cumplimiento y evidencia | 🟡 | 3.1 **reescrito el 14/09**: las seis conclusiones citan su objetivo y su evidencia concreta (apartados, tablas y cifras de pruebas). Quedan dos marcadores precisos, que dependen de la ejecución de los casos y del despliegue. 3.2 tiene catorce recomendaciones, cuya reducción forma parte del plan de recorte |
| 3.4 Bibliografía y anexos obligatorios | 🟡 | Anexos A, B, C, E y F ✅; **Anexo D pendiente** (dirección pública y archivo instalable) |

## 3. Requisitos mínimos del producto (punto 4)

Detalle y acciones en `09_PLAN_MODULO4.md`, sección 2. Resumen del estado:

| # | Requisito | Estado |
|---|---|---|
| 1 | Desplegado y accesible, o instalable | ❌ pendiente de despliegue |
| 2 | Autenticación y control por rol | 🟡 implementado; la autorización se resuelve en el servidor |
| 3 | Persistencia con el CRUD del dominio | 🟡 servicio completo y verificado; **la aplicación aún no consume todo el CRUD desde las pantallas** |
| 4 | Interfaz adaptable | 🟡 hay criterios y comportamiento declarados; faltan las capturas en tres anchos |
| 5 | Repositorio con historial progresivo | ✅ 19 confirmaciones repartidas; **falta publicarlas** |
| 6 | README con descripción e instrucciones | ✅ |
| 7 | Credenciales fuera del repositorio | ✅ `.gitignore`, plantillas y variables de entorno |
| 8 | Validación en cliente y en servidor | ✅ 422 con el campo rechazado, verificado con pruebas |

## 4. Convenciones de elementos técnicos (punto 5)

| Exigencia | Estado | Observación |
|---|---|---|
| Diagramas elaborados con herramientas de diagramación, legibles en carta | 🟡 | Los cuatro diagramas existen como código Mermaid (`Diagramas Mermaid - Modulo 4.md`); falta renderizarlos e insertarlos |
| Capturas numeradas como figuras, con datos de prueba y sin datos personales | ❌ | Pendientes; la lista de las nueve capturas necesarias está en la guía de despliegue |
| Fragmentos de código en monoespaciada de 10 puntos, numerados como figuras y con su archivo | 🟡 | Contenido y longitud correctos; la fuente se aplica al volcar en Word |
| Primera mención de cada tecnología con su versión | ✅ | 2.1.3, 2.1.4 y 2.1.5, y Tabla 7 |
| Términos extranjeros en cursiva, con su equivalente en español en la primera aparición | ✅ | Corregido el 14/09: *backend* con su equivalente, y en cursiva *framework*, *dashboard*, *Sprint*, *stakeholder* y *Product Owner* |

## 5. Inventario de marcadores sin completar

Se contaron **55 marcadores** en el cuerpo del documento (el recuento se corrigió el 14/09: la primera
estimación no contemplaba la columna de estado de la tabla de casos de prueba):

| Marcador | Cantidad | Qué falta |
|---|---|---|
| `[resultado]` y `[pendiente]` en las veintitrés filas de la Tabla 8 | 46 | Ejecutar cada caso y registrar el resultado obtenido, el estado y la fecha |
| `[N]` (números de figura) | 3 | Asignar al ensamblar el documento |
| `[Firebase Hosting u otra plataforma]`, `[URL del sistema]` y `[enlace al repositorio]` en el apartado 2.9 | 3 | Completar al desplegar |
| `[pendiente: ...]` en las conclusiones 5 y 6 | 2 | Se cierran con los dos grupos anteriores |
| `[cultivo y módulo piloto]` | 1 | Confirmar el cultivo del prototipo con el tutor |

Además hay **33 notas internas de revisión** dentro del documento (`<!-- -->`), que no se imprimen y
señalan cada punto que requiere atención antes de la entrega.

## 6. Lo que hay que hacer, en orden de dependencia

1. **Cerrar la decisión de roles** en la tutoría. Desbloquea el objetivo específico 1, el apartado 2.3.1,
   la autorización de 2.7 y una recomendación de 3.2.
2. **Publicar las confirmaciones** y, con eso, obtener la verificación automática y el historial visible.
3. **Desplegar** el servicio y la aplicación web. Desbloquea el requisito 1, el apartado 2.9, el Anexo D y
   cinco de los marcadores pendientes.
4. **Ejecutar los casos de prueba** de la Tabla 8 y registrar sus resultados (23 marcadores).
5. **Renderizar e insertar las figuras** y tomar las capturas con datos de prueba.
6. **Aplicar el plan de recorte de extensión**, previa conformidad del tutor.
7. **Completar los preliminares** en la plantilla oficial, cuando el contenido esté cerrado.

Los puntos 3 y 4 son los que más marcadores cierran de una sola vez: **51 de los 55**.

---

*Fuente: Elaboración propia.*
