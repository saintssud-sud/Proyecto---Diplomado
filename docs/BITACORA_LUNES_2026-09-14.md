# 📓 Bitácora — Sesión del domingo 13 y del lunes 14 de septiembre de 2026

**Proyecto:** SIGVACH — Sistema de Gestión de Variables para Cultivos Hidropónicos
**Grupo:** 3 — martes de 17:00 a 18:00 · **Tutoría:** martes 15/09 a las 17:00 · **Defensa:** martes 13/10 a las 17:00
**Objetivo de la sesión:** iniciar el Módulo 4 con el pie derecho: cerrar la entrega **E1** (documento y repositorio) y dejar encaminada la **E2** (vertical funcional), con el software desplegable y la monografía en el formato institucional.

**Alcance de esta bitácora.** La sesión empezó el **domingo 13 a las 22:58** y terminó el **lunes 14 a las 00:42**, con **38 confirmaciones** en el repositorio. Se documenta como una sola jornada de trabajo porque fue un bloque continuo; debajo de cada actividad se indica la fecha real.

**Punto de partida:** la aplicación Flutter existía con siete pantallas, pero guardaba los datos del dominio en `SharedPreferences`; la monografía estaba en borrador sin figuras ni anexos; no había servicio propio de API; no había verificación automática.

---

## 1. Lectura del documento de apertura y plan de trabajo

- Se revisó `P1_Apertura_Modulo4.pdf`, el documento de apertura del módulo: cuatro entregas semanales, los **ocho requisitos mínimos** del software, la monografía de **30 a 40 páginas** y las fechas de cierre.
- Se creó **`docs/09_PLAN_MODULO4.md`**, que es el documento de trabajo de todo el módulo: calendario real, matriz de los ocho requisitos, priorización MoSCoW, lista de evidencias por entrega, riesgos abiertos y registro de avance.
- Se ajustó el calendario al **Grupo 3 (martes 17:00)** y se adelantaron los cierres internos al **viernes anterior** de cada entrega (18/09, 25/09, 02/10 y 09/10), por pedido expreso del autor: los sábados no puede trabajar. Las fechas oficiales quedan como colchón.
- Se incorporó al repositorio la plantilla **`.env.example`** con las variables necesarias, sin ningún valor real.

## 2. Decisión de arquitectura: monolito modular con API propia

El problema de fondo: la aplicación hablaba **directamente con Cloud Firestore**, y eso hace imposible cumplir tres de los ocho requisitos —validación en servidor, credenciales fuera del repositorio y contraste verificable— además de dejar el dispositivo de adquisición sin forma de autenticarse.

| Decisión | Contenido |
|---|---|
| Estilo arquitectónico | **Monolito modular** con API REST propia, en lugar de microservicios o cómputo sin servidor. La justificación quedó escrita en el apartado 2.4.1: con un plazo de cuatro semanas, el costo de varios despliegues y de la red entre servicios no se justifica |
| Frontera de datos | **La API es el único componente que conoce las credenciales de Firestore.** Ni la aplicación ni el dispositivo las llevan |
| Autenticación | Personas: token de identidad de Firebase Authentication. Dispositivo de adquisición: clave propia en la cabecera `X-Device-Key` |
| Contrato de errores | `{"codigo", "mensaje", "detalle"}` con 400, 401, 403, 404, 409 y 422; el 422 señala **el campo rechazado** |
| Versionado | Prefijo `/api/v1` en todas las rutas |

## 3. Servicio de la API (13/09)

| Pieza | Estado |
|---|---|
| Contrato | **26 operaciones sobre 11 rutas**, con documentación OpenAPI generada desde el propio código (`/docs`) |
| Tamaño | 23 archivos y 1 929 líneas en `backend/app/`; 7 archivos y 583 líneas de pruebas |
| Validación en servidor | Rechaza variable fuera del catálogo, valor fuera del límite físico, unidad incoherente, marca de tiempo futura y campos ajenos al contrato |
| Reglas de negocio | Evaluación de cada lectura contra el rango vigente, **una alerta por lectura fuera de rango referenciada a su lectura**, resumen de series y exportación en CSV |
| Persistencia | Interfaz de repositorio con dos implementaciones: **Cloud Firestore** para el despliegue y **memoria** para desarrollo y pruebas |
| Pruebas | **59 casos automatizados, todos aprobados**, ejecutables sin credenciales ni conexión |
| Modo de demostración | `USAR_REPOSITORIO_EN_MEMORIA=true` levanta la API completa con datos: perfil de lechuga con seis rangos, dos módulos, doce lecturas y tres alertas. Las lecturas se cargan con **el mismo servicio que usa la ingesta real**, así que las alertas las produce la regla de negocio y no la semilla |

## 4. Capa de acceso a la API en la aplicación Flutter (13/09)

| Pieza | Estado |
|---|---|
| `lib/config/api_config.dart` | Dirección del servicio por `--dart-define=API_BASE_URL`; si no se define, usa `10.0.2.2` en el emulador de Android y `localhost` en web y escritorio |
| `lib/services/api_errores.dart` | Tres errores distintos: `ErrorApi` (rechazo del servidor, con código y detalle por campo), `ErrorConexion` (la petición no se completó) y `ErrorDeContrato` (la respuesta no cumple el contrato) |
| `lib/services/api_cliente.dart` | Adjunta el token, traduce el formato de error del contrato, distingue red de negocio, falla sin salir a la red cuando no hay sesión y **decodifica en UTF-8 de forma explícita** |
| `lib/models/api/modelos_api.dart` | Modelos fieles al contrato y el catálogo de las siete variables, con la advertencia de que la validación la hace siempre el servidor |
| `lib/repositories/api/` | Cinco repositorios que arman las rutas, envían solo los campos declarados y convierten las respuestas |
| `lib/widgets/vista_con_estados.dart` | La vista con sus **cuatro estados** (carga, con datos, vacío y error), reutilizable. El error se presenta distinto según sea fallo de conexión o rechazo del servidor |
| `lib/controllers/` | `lecturas_controller`, `panel_controller` y —del lunes— `historial_controller`; todos publican el estado de la vista y traducen los fallos con `FalloDeVista` |
| Pruebas | **63 casos aprobados**: 16 del cliente, 25 de los repositorios, 11 de los cuatro estados y 11 del controlador |

## 5. Panel principal conectado al servicio (14/09 00:04)

`home_screen` dejó de leer datos locales: ahora consume el servicio a través de `PanelController` y muestra el módulo, el estado de cada variable contra su rango de referencia, el número de alertas activas y la fecha de la última lectura.

## 6. Migración del historial al servicio (14/09 00:42)

**Lo que se encontró.** El historial era el caso más engañoso de la capa local: la gráfica tenía un filtro por período **simulado** —tomaba las tres, cuatro o todas las mediciones de una lista en memoria, con un comentario en el código que lo admitía—; el rango de fechas que el usuario elegía en la pantalla anterior **no llegaba a ninguna consulta**; y el desplegable de variables ofrecía cuatro nombres inventados (`Temperatura`, `Humedad`, …) que no son códigos del sistema.

| Antes | Ahora |
|---|---|
| La gráfica filtraba con `take(3)` y `take(4)` sobre datos locales | Consulta al servicio por variable y rango; los períodos rápidos aplican un rango de fechas real |
| El rango de fechas se recogía y se descartaba | Viaja al servicio como `desde` y `hasta` |
| El resumen se calculaba en el cliente | Lo devuelve `GET /api/v1/lecturas/resumen`, única fuente del promedio, máximo y mínimo |
| La lista mostraba todas las mediciones locales | Muestra las lecturas de la consulta vigente, con su origen, su observación y el estado que evaluó el servidor |
| Cuatro nombres inventados | El **catálogo real de siete variables** con sus códigos y unidades |
| Sin estados de vista | Los cuatro estados, con la distinción entre fallo de conexión y rechazo del servidor |

**Cambio de contrato asociado.** `LecturaSalida` no declaraba la observación: el servicio la guardaba —`POST /api/v1/lecturas` la acepta— y la descartaba al responder. `AlertaSalida` no declaraba la unidad ni el sentido de la desviación, que el documento de la alerta sí guarda. Se declararon para que el contrato coincida con lo que se almacena y con lo que la aplicación espera.

## 7. Monografía

| Apartado | Trabajo realizado |
|---|---|
| 1.1.2 | Reescrito con **cuatro soluciones concretas del dominio** (Bluelab, Hanna Instruments, TrolMaster y MyCodo), cada una con qué resuelve y qué deja sin resolver, con fuente citada |
| 1.3 | Párrafo de limitaciones, con la declaración de que el cumplimiento de los requisitos no depende del hardware |
| 2.1.3 a 2.1.5 | Primera mención de cada tecnología con su versión |
| 2.2 | Reescrito: iteración semanal justificada, tabla de fechas reales y declaración del uso de asistentes de IA |
| 2.3.1 a 2.3.5 | Actores, trece requisitos funcionales con criterio de aceptación, ocho requisitos no funcionales con magnitud verificable, diez casos de uso y priorización MoSCoW con el alcance excluido |
| 2.4.1 a 2.4.4 | Arquitectura de monolito modular justificada, diccionario de datos, criterios de accesibilidad y contrato de la API con formato de peticiones, errores, autenticación y versionado |
| 2.5 y 2.7 | Tabla con las versiones reales del stack, tomadas de `pubspec.lock`; seguridad reescrita: sesión, autorización en servidor, autenticación del dispositivo, doble validación, cifrado y variables sensibles |
| 2.6 | **Reescrito por completo** (1 506 palabras): componentes construidos, seis decisiones técnicas con su fundamento, cinco dificultades reales con su resolución y dos fragmentos de código verificados **literalmente** contra el repositorio, de 12 y 18 líneas |
| 2.8 | Tabla con **23 casos de prueba** vinculados a los requisitos, listos para registrar resultado y fecha |
| 3.1 | **Reescrito**: las seis conclusiones citan su objetivo específico, su grado de cumplimiento y su evidencia concreta. Los cinco marcadores vagos se redujeron a dos precisos |
| Resumen | Reescrito a **290 palabras** (el máximo son 300), incorpora la metodología y el servicio de API, y **afirma solo lo verificado**: antes decía que «las pruebas evidenciaron el cumplimiento», que es un resultado todavía no ejecutado |
| Tablas | Ocho, numeradas en orden de aparición y con las referencias del texto coherentes |
| Bibliografía | 19 entradas en estilo ISO 690-2 con orden alfabético verificado |

**Anexos creados** (dos de ellos eran entregables obligatorios que no existían):

- **Anexo A — Manual de usuario:** quince apartados, una sección por pantalla con los rótulos reales **verificados contra el código**, los cuatro estados de las vistas, preguntas frecuentes y glosario de las siete variables.
- **Anexo B — Manual de instalación y despliegue:** siete secciones, desde la instalación local con el modo de demostración sin credenciales hasta el despliegue completo y los problemas frecuentes.
- **Anexos C a F:** enlace al repositorio con instrucciones de acceso para el tribunal, dirección pública y archivo instalable (pendientes de completar al desplegar), los diagramas y la documentación complementaria.

**Archivos superados, marcados.** Los capítulos sueltos quedaron con una advertencia al inicio, **en Markdown y también en los `.docx`**. Motivo: el Capítulo 1 llegó a tener cuatro versiones en carpetas distintas y ya costó tiempo decidir cuál valía.

**Auditoría de cumplimiento** (`docs/11_AUDITORIA_CUMPLIMIENTO.md`): revisión punto por punto contra el Formato 2020 y los Lineamientos 2026 —aspectos formales, contenido de cada apartado obligatorio, los ocho requisitos mínimos y las convenciones de elementos técnicos— con el inventario de los **55 marcadores** que quedan sin completar y el orden para cerrarlos. Desplegar y ejecutar los casos de prueba cierra **51 de una sola vez**.

## 8. Formato institucional y conversión a Word (14/09)

**El camino de entrega estaba roto.** El conversor anterior (`md2docx.py`) generaba tablas **sin el elemento obligatorio `w:tblGrid`**, que Word no puede interpretar, y no aplicaba estilos de título: el archivo de Word que existía tenía sus cinco tablas ilegibles y ningún estilo. El conversor del repositorio producía tablas válidas, pero en Calibri 11 y con los títulos en verde.

Se le agregó la opción **`--institucional`**: Arial 12, interlineado 1,5, márgenes 4/3/3/3 cm, papel carta y la jerarquía del índice oficial (Título 1 = capítulo, 2 = apartado, 3 = subapartado), de modo que el índice y la numeración se generen solos. Además:

- Portada, contratapa, hoja de aprobación, hoja de advertencia y los **tres índices como campos de Word**, que se actualizan tras cada corrección.
- **Numeración romana en los preliminares y arábiga desde el Capítulo 1**, con el número en el pie derecho.
- **Tablas sin líneas verticales**, título de figura **arriba a la izquierda en 10 puntos** con la fuente debajo, y el cuerpo justificado.
- **Cada capítulo y la bibliografía comienzan en página nueva**; los separadores del borrador se omiten.

**Contradicción de formato, resuelta.** El módulo dice «las figuras llevan epígrafe debajo»; la plantilla oficial y las normas que cita dicen que **el título va arriba**. Se siguió la plantilla, porque el propio módulo dispone que *el Formato 2020 manda en lo formal y los Lineamientos en lo técnico*. **Conviene confirmarlo con el tutor el martes**: es una pregunta de treinta segundos y el conversor puede cambiarlo en una línea.

## 9. Figuras

**12 imágenes (523 KB)** generadas con dos scripts, sin depender de renderizarlas en un sitio externo:

- **Nueve bocetos de interfaz** con `generar_figuras_interfaz.py`: las siete pantallas, la administración de usuarios y —la más útil— **los cuatro estados de una vista que consume datos**, que es la parte del diseño que el módulo pide documentar y que suele improvisarse.
- **Tres diagramas técnicos** con `generar_figuras_diagramas.py`: arquitectura de componentes, casos de uso y **secuencia del registro de una lectura**, que muestra dónde se valida, dónde se decide y qué se devuelve cuando algo falla.

Todas verificadas **por geometría**: el texto entra en todos los contenedores y el contenido queda centrado. Numeración asignada: Figuras 1 a 5 en el cuerpo, 6 y 7 para los fragmentos de código, y E.1 a E.7 en el Anexo E. **No queda ningún marcador `[N]`** en el documento.

## 10. Herramientas de verificación (14/09)

**`scripts/verificar_dart.py`.** El analizador de Flutter no puede ejecutarse en este entorno (véase el apartado 12), así que se escribió un verificador que cubre los tres defectos que más veces aparecieron al escribir las pantallas: un delimitador sin cerrar, una importación relativa que dejó de resolver y un campo declarado que nadie lee. Tiene una **autoprueba** que lo revisa contra dos archivos con defectos deliberados y exige volver a encontrarlos: su primera versión **no era fiable** y marcaba como no leído un campo que sí se usaba. Con eso se revisaron los **74 archivos** de `lib/` y `test/` sin hallazgos. No sustituye al analizador: no comprueba tipos.

**Otras comprobaciones ejecutadas:**

| Comprobación | Resultado |
|---|---|
| Catálogo de variables: aplicación contra servicio | 7 = 7, mismos códigos, mismas unidades, mismos nombres |
| Referencias cruzadas del documento («apartado N.M») | 27 de 27 resuelven |
| Objetivos específicos contra conclusiones | 6 objetivos ↔ 6 conclusiones, correspondencia uno a uno |
| Numeración de tablas y figuras | Coherente con las referencias del texto; sin marcadores |
| Notas internas del borrador en el Word generado | Cero |
| `render.yaml` y el flujo de verificación | YAML válido, con los pasos en el orden previsto |

## 11. Verificación automática en el repositorio (14/09 00:06)

Se incorporó integración continua con **dos trabajos independientes**, de modo que un fallo en una parte no oculte el estado de la otra:

| Trabajo | Qué comprueba |
|---|---|
| Servicio de la API | Instala las dependencias declaradas —incluidas `uvicorn` y `firebase-admin`, con lo que comprueba de paso que el servicio pueda desplegarse en Linux— y ejecuta las pruebas |
| Aplicación Flutter | Prepara la configuración de Firebase desde la plantilla, **verifica la estructura del código Dart**, analiza, ejecuta las pruebas y **compila la versión web** |

El historial de ejecuciones es evidencia de las pruebas del apartado 2.8, y el repositorio muestra el distintivo de estado en su README. Se incluyó a propósito la compilación web: es el artefacto que se publica en Firebase Hosting.

## 12. Entorno de trabajo: hallazgos y bloqueos

| Hallazgo | Consecuencia |
|---|---|
| **El tool de Flutter se colgaba sin dar error** porque necesita escribir en `C:\src\flutter\bin\cache\lockfile`, fuera del proyecto, y el modo de trabajo actual lo impide | Toda orden de Flutter (analizar, probar, compilar web, generar APK) **requiere aprobación de acceso ampliado**, que quedó rechazada. Alternativa: ejecutarlas el propio autor en su terminal, o esperar a la verificación automática al publicar |
| La instalación de paquetes con `pip` fallaba con «Permission denied» al desempaquetar, en tres configuraciones distintas | Se resolvió con **una única ejecución de acceso ampliado** autorizada; `uvicorn`, `httpx` y `pytest` quedaron disponibles en el entorno del proyecto |
| Restos que no se pudieron borrar: `.tmp-pip/` y `backend/pytest-cache-files-*/` | Quedaron con permisos que el entorno no permite modificar. Están excluidos por `.gitignore`, pero **conviene eliminarlos a mano** |
| Las reglas de seguridad de Firestore | El archivo es una **propuesta**: debe probarse en *Rules Playground* antes de publicarlas |

**Consecuencia práctica:** los cambios en Dart escritos en esta sesión están verificados de forma **estructural, no de tipos**. El análisis de tipos se ejecuta en la verificación automática en cuanto se publiquen las confirmaciones.

## 13. Preparación del despliegue (13/09)

| Pieza | Estado |
|---|---|
| `backend/render.yaml` | Blueprint del servicio para Render, validado: nombre, runtime, plan, región, comandos de compilación y arranque, ruta de salud y las siete variables de entorno (cuatro se cargan a mano; ninguna en el repositorio) |
| `docs/10_DESPLIEGUE.md` | Guía paso a paso del despliegue completo (API, aplicación web y APK), con la obtención de la clave de la cuenta de servicio, la verificación de los ocho requisitos, las nueve capturas que exige el apartado 2.9, los problemas previsibles y lo que no debe hacerse |
| `uvicorn` 0.52.4 | Instalado; el arranque real se verificó con el comando exacto del despliegue |
| `firestore.rules` y `firebase.json` | Incorporados al control de versiones, **sin publicar todavía** |

---

## 14. Defectos encontrados y corregidos

Se listan porque en varios casos el defecto era **invisible** hasta que se probó el resultado, y porque son el material real del apartado 2.6 de la monografía.

| Defecto | Causa | Corrección |
|---|---|---|
| Las **31 notas internas** del borrador se imprimían como texto en el Word | El conversor no filtraba los comentarios; en Markdown no se ven, así que habría aparecido recién al imprimir | El conversor elimina los comentarios antes de procesar. Verificado: cero notas |
| Las tablas del Word eran ilegibles | El conversor anterior generaba tablas sin el elemento obligatorio `w:tblGrid` | Se adoptó el conversor del repositorio y se verificó la lectura de las 8 tablas |
| El epígrafe de las figuras iba debajo | Se siguió la indicación del módulo y no la plantilla oficial | Se corrigió a **arriba, a la izquierda y en 10 puntos**, con la fuente debajo |
| Los separadores del borrador se dibujaban como líneas de guiones bajos | El conversor los interpretaba como contenido | Se omiten |
| Cada capítulo seguía al anterior sin salto de página | El conversor no insertaba salto | Salto de página antes de cada capítulo y de la bibliografía |
| Los títulos tenían un nivel de menos | El capítulo se mapeaba como «Título» y no como «Título 1» | Jerarquía corregida a la del índice oficial |
| La configuración de los títulos se perdía | Una función posterior sobrescribía el estilo ya configurado | Se reordenó la configuración |
| Las referencias a tablas quedaron corridas | Al insertar el diccionario de datos, las tablas siguientes cambiaron de número | Renumeración 3 a 8, con todas las referencias verificadas |
| **El filtro por período de la gráfica era simulado** | Tomaba las primeras mediciones de una lista en memoria, con un comentario que lo admitía | Consulta real al servicio por variable y rango |
| **El rango de fechas del historial se descartaba** | La pantalla no lo pasaba a ninguna consulta | Viaja al servicio como `desde` y `hasta` |
| El desplegable de variables ofrecía nombres inventados | La pantalla no usaba el catálogo del sistema | Catálogo real de siete variables |
| Los acentos llegaban mal | La librería HTTP decodificaba en latin-1 al no declararse el juego de caracteres | Decodificación explícita en UTF-8 |
| El 422 señalaba `cuerpo` y no el campo rechazado | La validación estaba en el modelo y no en el campo | Se movió a un validador por campo con acceso a los datos ya validados |
| Una excepción inesperada del verificador de identidad salía como error 500 | No estaba encapsulada | Se devuelve 401 |
| `CrossAxisAlignment.stretch` dentro de una fila de una lista | Habría reventado en ejecución | Se retiró |
| Aviso de variable no usada en un `catch` | Detalle del analizador | Se retiró la variable |
| `LecturaSalida` no devolvía la observación | El esquema de salida no la declaraba y el servicio la descartaba | Declarada en el contrato |
| `AlertaSalida` no devolvía la unidad ni la desviación | Mismo caso: el documento las guarda, el esquema no las declaraba | Declaradas |
| El nombre de una variable difería entre la aplicación y el servicio | Copia del catálogo desactualizada | Alineado |
| **El propio verificador de Dart era incorrecto** | Acortaba el texto al quitar cadenas, las posiciones se desfasaban y marcaba como no leído un campo que sí se usaba | Se corrigió para conservar la longitud y se fijó con una autoprueba |
| Una nota interna anidada se truncaba y filtraba texto interno | Comentarios HTML anidados | Reescrita; 33 comentarios equilibrados |

## 15. Estado de los ocho requisitos mínimos

| # | Requisito | Estado |
|---|---|---|
| 1 | Software desplegado y accesible públicamente, instalable | **Preparado, no desplegado.** Faltan la cuenta de Render y la clave de la cuenta de servicio |
| 2 | Autenticación con roles | Cumplido: Firebase Authentication y autorización resuelta en el servidor; una cuenta desactivada o sin perfil recibe 403 |
| 3 | Persistencia en base de datos con CRUD del dominio | **Parcial.** El servicio implementa el CRUD completo y el panel y el historial ya lo consumen; alertas, cultivos, variables y rangos todavía leen datos locales |
| 4 | Interfaz adaptable | Cumplido en el componente de estados y en el panel; el resto de pantallas se migran con el mismo patrón |
| 5 | Repositorio con historial progresivo | Cumplido: **51 confirmaciones**, 38 en esta sesión, con mensajes que describen el cambio |
| 6 | README | Cumplido, con el distintivo de la verificación automática |
| 7 | Credenciales fuera del repositorio | Cumplido: variables de entorno y plantilla sin valores reales |
| 8 | Validación en cliente y servidor | Cumplido en el servicio; en la aplicación queda pendiente en las pantallas sin migrar |

---

## 16. Pendientes, en orden

1. **Tutoría del martes 15/09 a las 17:00** — cerrar tres decisiones: alcance de roles (2 o 4), backend con API propia y recortes del documento. Preguntar además por la ubicación del epígrafe de las figuras y por el resumen como parte preliminar.
2. **Publicar las confirmaciones** (38 sin publicar). Es lo único que dispara la verificación automática y, con ella, el **análisis de tipos** del código Dart escrito en esta sesión.
3. **Desplegar**: cuenta de Render, clave de la cuenta de servicio, índices compuestos de Firestore, publicación de las reglas, versión web en Firebase Hosting y APK firmado. Cierra el requisito 1 y **51 de los 55 marcadores** del documento.
4. **Ejecutar los 23 casos de prueba** de la tabla del apartado 2.8 y registrar resultado y fecha.
5. **Migrar las pantallas que faltan** al servicio: alertas, cultivos, variables y rangos. Es lo que cierra el requisito 3 y lo que hace demostrable el guion de la defensa. El patrón ya está fijado por `PanelController` e `HistorialController`.
6. **Exportación en CSV desde la aplicación**: el servicio publica el recurso y el repositorio sabe descargarlo, pero ninguna pantalla lo ofrece porque guardar el archivo requiere una dependencia que no se puede añadir sin ejecutar `flutter pub get`. Mientras tanto se demuestra desde el navegador.
7. **Recortar el documento.** El cuerpo tiene 15 738 palabras y, con las tablas, los fragmentos y las figuras que ya existen, llegaría a **49 o 51 páginas** frente al límite de 30 a 40. El plan de recorte está medido y escrito dentro del borrador, y quedó ampliado a nueve medidas (del orden de 2 500 palabras): hay que validarlo con el tutor. **Es la única tarea del proyecto que crece sola si no se atiende.**
8. **Cuatro cosas manuales en Word**, que no se pueden automatizar: pegar el escudo de la universidad en la portada, completar los nombres del tribunal en la hoja de aprobación, decidir si se incluyen dedicatoria y agradecimientos, y revisar que el nombre completo del autor sea el correcto.
9. **Decisión pendiente sobre el control de versiones del documento.** El repositorio versiona el código y las bitácoras, pero **la monografía y los anexos no están bajo control de versiones**: viven como archivos sueltos en la raíz. Con cuatro semanas de escritura por delante conviene incorporarlos.

## 17. Comandos utilizados con más frecuencia

| Comando | Uso |
|---|---|
| `python "Proyecto SIGVACH/scripts/md_a_docx.py" <entrada.md> <salida.docx> --institucional` | Convertir la monografía al formato institucional |
| `python "Proyecto SIGVACH/scripts/md_a_docx.py" <entrada.md> <salida.docx>` | Convertir un documento interno (como esta bitácora) |
| `python scripts/verificar_dart.py --autoprueba` | Comprobar que el verificador de Dart es fiable |
| `python scripts/verificar_dart.py` | Verificar la estructura de los 74 archivos Dart |
| `python -m pytest backend/pruebas -q` | Ejecutar las 59 pruebas del servicio |
| `python -m uvicorn app.main:app --reload` | Arrancar el servicio en desarrollo |
| `git log --oneline` | Revisar el historial progresivo del repositorio |

## 18. Cifras de la sesión

| Dato | Valor |
|---|---|
| Duración | Del domingo 13 a las 22:58 al lunes 14 a las 00:42 |
| Confirmaciones en esta sesión | **38** (51 en el repositorio) |
| Archivos rastreados | 188 |
| Servicio: código / pruebas | 1 929 líneas en 23 archivos / 583 líneas en 7 archivos |
| Aplicación: código / pruebas | 8 328 líneas en `lib/` / 1 584 líneas en `test/` |
| Pruebas aprobadas | **59 del servicio + 63 de la aplicación** |
| Pruebas escritas sin ejecutar todavía | 17 (se ejecutan en la verificación automática) |
| Operaciones del contrato | 26 sobre 11 rutas |
| Figuras generadas | 12 (523 KB) |
| Tablas de la monografía | 8 |
| Marcadores por completar | 55 (51 se cierran al desplegar y probar) |

## 19. Para retomar

**Lo primero, mañana martes:** la tutoría de las 17:00. Las tres decisiones que bloquean trabajo son el alcance de roles —que afecta a los objetivos 1.5, 2.3.1, 2.7 y 3.2 del documento—, la confirmación del backend con API propia y el plan de recorte. Las dos preguntas de formato son de treinta segundos.

**Lo primero en lo técnico:** migrar la pantalla de alertas, que es la que falta para que el paso más vistoso de la demostración —registrar una medición fuera de rango y ver la alerta— funcione sin salir de la aplicación. Después, publicar las confirmaciones y desplegar: desplegar cierra por sí solo 51 de los 55 marcadores del documento.

---

*Bitácora de trabajo del Módulo 4. Elaborada al cierre de la sesión del 13 y 14 de septiembre de 2026.*
