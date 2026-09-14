# Plan de trabajo — Módulo 4 (SIGVACH)

Documento interno de trabajo. No forma parte de la monografía.
Base normativa: *P1 Apertura Módulo 4* (UAJMS, 2026), *Lineamientos Técnicos Complementarios* (2026) y
*Formato para la Elaboración del Trabajo Final* (Dirección de Posgrado, 2020).

---

## 1. Calendario real

**Grupo 3 · franja martes de 17:00 a 18:00**, sin cambios salvo la excepción del 9 de octubre.

| Fecha | Hito | Qué debe estar cerrado |
|---|---|---|
| Dom 13 sep | Preparación | Ficha de proyecto, arreglos de repositorio, backend y capa de API de la aplicación |
| **Mar 15 sep, 17:00** | Tutoría 1 (Grupo 3) | Problema en una frase, tres objetivos, pantallas, decisiones de alcance. Ocurre **antes** del cierre de E1: el borrador puede corregirse con el tutor |
| Sáb 19 sep 23:59 | **E1 · Perfil de proyecto** | Capítulo 1, 2.2 metodología, 2.3 requisitos, repositorio inicializado |
| Mar 22 sep, 17:00 | Tutoría 2 | Revisa el avance hacia E2 |
| Sáb 26 sep 23:59 | **E2 · Vertical funcional** | 2.4 diseño técnico, frontend navegable, API con CRUD, **primer despliegue público** |
| Mar 29 sep, 17:00 | Tutoría 3 | Revisa el avance hacia E3 |
| Sáb 3 oct 23:59 | **E3 · Checkpoint técnico** | 2.7 seguridad, 2.8 pruebas con evidencia, borrador de los Capítulos 1 y 2 |
| **Vie 9 oct, 17:00** | Tutoría 4 — **franja excepcional** | El martes 6 no hay clase; los Grupos 3 y 4 pasan al viernes. Único cambio de franja del módulo |
| Sáb 10 oct 23:59 | **E4 · Documento y sistema** | Documento completo, despliegue verificado, manuales y anexos |
| **Mar 13 oct, 17:00** | **Defensa técnica** | 7 minutos de demostración en vivo del sistema desplegado + 5 de preguntas |

Penalización por entrega tardía: 10 puntos porcentuales por día, hasta 72 horas. Nota mínima de
aprobación: 70 sobre 100. El Módulo 4 es condición necesaria, no suficiente.

---

## 2. Matriz de los ocho requisitos mínimos

| # | Requisito | Estado al 13/09/2026 | Acción | Sprint |
|---|---|---|---|---|
| 1 | Desplegado y accesible por dirección pública, o instalable | ❌ Sin URL pública ni APK de release | `flutter build web` + Firebase Hosting; `flutter build apk --release` | 2 |
| 2 | Autenticación y control de acceso por rol | 🟡 Auth operativo; roles `admin`/`usuario` en Firestore, sin versionar las reglas | Definir el alcance de roles; mover la autorización al backend y versionar `firestore.rules` | 2 y 3 |
| 3 | Persistencia en base de datos con el CRUD del dominio | ❌ Cultivos, lecturas, alertas y rangos en SharedPreferences | CRUD del dominio en Cloud Firestore, accedido a través de la API | 2 |
| 4 | Interfaz adaptable a distintos tamaños de pantalla | 🟡 Existen `MaxWidthBox` y `mode_banner`, sin evidencia | Capturas fechadas por tamaño (móvil, tableta, escritorio) y apartado 2.4.3 | 3 |
| 5 | Repositorio con historial de avance progresivo | ✅ 13 confirmaciones entre el 30/08 y el 12/09 | Verificar el acceso del docente y mantener la cadencia semanal | continuo |
| 6 | README con descripción e instrucciones de ejecución local | ✅ Completo | Añadir el procedimiento de despliegue y de ejecución del backend | 2 |
| 7 | Credenciales y variables sensibles fuera del repositorio | 🟡 Archivos sensibles ignorados y plantillas `*.example.*` presentes | `.env.example` del backend; credenciales del servidor como variables de entorno de la plataforma | 2 y 3 |
| 8 | Validación de datos de entrada en cliente y en servidor | ❌ Sin validación en servidor | Esquemas de validación en el backend (Pydantic) y respuestas de error documentadas | 2 |

---

## 3. Decisión de arquitectura propuesta

### 3.1 El problema de la arquitectura actual

Hoy la aplicación Flutter escribe y lee **directamente** en Cloud Firestore. Eso deja tres huecos:

1. **Requisito 8.** No existe validación en servidor: el cliente es la única barrera.
2. **Entrega E2.** El módulo pide explícitamente "API con CRUD" y advierte que, si el contrato no está
   escrito, el sistema está acoplado.
3. **Adquisición IoT.** El borrador 2.4.4 propone que el ESP32 se autentique contra la API REST de
   Firestore con "credenciales restringidas". Eso es inviable de forma segura en un microcontrolador
   (requiere un token OAuth2 de cuenta de servicio) y es un hallazgo que el tribunal puede atacar.

### 3.2 Arquitectura propuesta: monolito modular con API REST

```
ESP32 ──(HTTPS + clave de dispositivo)──┐
                                        ▼
Aplicación Flutter ──(HTTPS + token)──► API REST (backend propio) ──► Cloud Firestore
   (presenta)                             (decide, valida, autoriza)      (guarda el estado)
```

| Componente | Responsabilidad en una frase |
|---|---|
| Aplicación Flutter | Presenta la información y recoge los datos del usuario; no decide reglas de negocio |
| API REST | Autentica, valida, autoriza y expone el contrato; es el único que habla con la base de datos |
| Cloud Firestore | Guarda el estado del dominio |
| Firebase Authentication | Verifica la identidad del usuario y emite el token que la API valida |

El patrón elegido es **monolito modular**, que es el que el módulo recomienda para cuatro semanas: un solo
despliegue, una sola base de datos y depuración simple, con separación interna por módulos.

### 3.3 Stack del backend recomendado

**FastAPI (Python 3.13) desplegado en Render, capa gratuita.** Justificación contra los requisitos:

| Criterio | Por qué FastAPI |
|---|---|
| Requisito 8 (validación en servidor) | Los esquemas de Pydantic validan cada cuerpo de petición y devuelven 422 con el detalle del campo rechazado; la validación queda visible en el código, que es lo que el tribunal va a pedir ver |
| Requisito 2 (autorización por rol) | El SDK `firebase-admin` verifica el token de identidad en cada petición y el rol se resuelve contra la colección `usuarios` |
| Requisito 7 (variables sensibles) | Las credenciales de la cuenta de servicio entran por variables de entorno de la plataforma, nunca por el repositorio |
| Apartado 2.4 (contrato de la API) | Genera automáticamente la documentación OpenAPI navegable en `/docs`, que es el artefacto que evidencia el contrato |
| Entorno | Python ya está instalado y en uso en el proyecto; Render despliega Python de forma nativa en capa gratuita |
| Requisito 1 (despliegue) | Un solo servicio que se despliega desde el repositorio con cada confirmación |

Alternativas descartadas: **Node.js con Express** (equivalente en esfuerzo, sin ventaja concreta en este
proyecto), **Dart con Shelf o dart_frog** (un solo lenguaje para todo el proyecto, pero el despliegue exige
Dockerfile y hay menos ejemplos), **solo reglas de Firestore** (lo más rápido, pero deja sin cumplir el
requisito 8 y la exigencia de "API con CRUD" de la entrega E2).

*Limitación a declarar:* la capa gratuita de Render suspende el servicio por inactividad, por lo que la
primera petición tras un periodo sin uso tarda unos segundos. Se documenta en 2.9 y se mitiga con una
llamada de mantenimiento al endpoint de salud antes de la demostración.

### 3.4 Contrato de la API (versión 1)

| Método | Ruta | Quién | Qué hace |
|---|---|---|---|
| GET | `/api/v1/salud` | Público | Comprueba que el servicio y la base de datos responden |
| POST | `/api/v1/lecturas` | Dispositivo (clave de dispositivo) | Registra una lectura enviada por el ESP32 |
| GET | `/api/v1/lecturas` | Usuario autenticado | Consulta lecturas filtradas por módulo, variable y fechas |
| POST · GET · PATCH · DELETE | `/api/v1/modulos` `/api/v1/modulos/{id}` | Administrador | CRUD de los módulos de cultivo |
| POST · GET · PATCH · DELETE | `/api/v1/rangos` `/api/v1/rangos/{id}` | Administrador | CRUD de los rangos de referencia por perfil |
| POST · GET · PATCH · DELETE | `/api/v1/alertas` `/api/v1/alertas/{id}` | Operador | CRUD de las alertas |
| GET | `/api/v1/exportaciones/lecturas.csv` | Usuario autenticado | Exporta el historial consultado en CSV |

**Autenticación.** Los usuarios envían el token de identidad de Firebase en la cabecera
`Authorization: Bearer <token>`. El dispositivo envía la cabecera `X-Device-Key`, cuyo valor vive en una
variable de entorno del servidor.

**Forma de las respuestas.** Éxito: el recurso o la lista, con `200`, `201` o `204`.
Error: `{"codigo": "...", "mensaje": "...", "detalle": {...}}` con `400` (datos inválidos), `401` (sin
token o token inválido), `403` (rol sin permiso), `404` (recurso inexistente), `409` (conflicto) o `422`
(validación de campos). **Versionado:** el prefijo `/api/v1` se mantiene estable; todo cambio incompatible
publica `/api/v2` y la versión anterior queda en desuso anunciada en el README.

---

## 4. Priorización preliminar (MoSCoW)

**Must (sin esto no se aprueba):** autenticación y control por rol en servidor; CRUD de módulos de cultivo,
lecturas, rangos y alertas sobre Cloud Firestore; ingesta de lecturas por API con clave de dispositivo;
panel principal con los cuatro estados de vista; historial con filtro por variable y fechas; alertas por
valor fuera de rango; despliegue público y APK instalable; reglas de seguridad y `.env.example`; README;
tabla de casos de prueba ejecutados.

**Should (si el tiempo alcanza):** exportación en CSV; panel de administración de usuarios (ya construido);
gráfica de tendencia en el historial (ya construida).

**Could (deseable):** notificación por correo; comparación entre ciclos de cultivo; registro de contexto
con GPS y clima (ya construido, se documenta como funcionalidad complementaria).

**Won't (fuera de alcance de esta gestión, se declara en 1.6):** control automático de actuadores; MQTT;
predicciones con aprendizaje automático; reportes en PDF o Excel; calibración automática de sensores.

---

## 5. Checklist de evidencias por entrega

**E1 (19/09).** Capítulo 1 en formato oficial · 2.2 metodología con cronograma real y declaración de IA ·
2.3 requisitos con criterios de aceptación y MoSCoW · `firestore.rules` y configuración de despliegue en el
repositorio · acceso del docente confirmado · confirmaciones de la semana.

**E2 (26/09).** 2.4 arquitectura con diagrama de componentes, modelo de datos y contrato de la API ·
2.5 tabla del stack con versiones reales · frontend navegable · backend con CRUD desplegado · URL pública
operativa · capturas del panel de la plataforma (build, variables de entorno y registros) · README
actualizado.

**E3 (03/10).** 2.7 seguridad con autenticación, autorización por rol, validación y gestión de variables
sensibles · reglas de seguridad publicadas y versionadas · 2.8 con la tabla de casos de prueba ejecutados
(identificador, escenario, resultado esperado, resultado obtenido, estado, fecha) · pruebas automatizadas
del backend · capturas legibles con datos de prueba · borrador de los Capítulos 1 y 2.

**E4 (10/10).** 2.9 despliegue con plataforma, procedimiento, configuración de entornos y dirección pública ·
Capítulo 3 con una conclusión por objetivo específico · Anexo A manual de usuario · Anexo B manual de
instalación y despliegue · Anexo C enlace al repositorio con acceso para el tribunal · Anexo D dirección
pública y APK · Anexo E diagramas en tamaño legible · documento en editable y PDF, de 30 a 40 páginas sin
preliminares ni anexos.

---

## 6. Riesgos abiertos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Sin backend, no se cumplen los requisitos 3 y 8 | Alto | Sprint 2: backend, contrato y despliegue público |
| Incoherencia entre roles del documento (4) y del producto (2) | Medio | Cerrar la decisión en la tutoría del 14/09 y ajustar 1.5 y 2.3 |
| Disponibilidad y calibración del hardware ESP32 | Medio | El sistema se verifica sin hardware: alta manual y lecturas de prueba contra la API; se declara como limitación |
| Documento y producto divergen al final | Medio | Cada entrega semanal actualiza el mismo archivo; ninguna cifra del documento sin evidencia |
| Historial de repositorio concentrado | Bajo | Confirmaciones semanales con mensajes descriptivos, ya en curso |

---

## 7. Estado de avance

### 7.1 Hecho

**Repositorio (confirmaciones del 13/09).**

| Confirmación | Contenido |
|---|---|
| `chore(firebase)` | `firestore.rules`, `firebase.json` (reglas + hosting) y `.firebaserc` incorporados al control de versiones; `.gitignore` deja de excluir la configuración de despliegue |
| `docs(plan)` | Este documento |
| `docs(seguridad)` | `.env.example` con las variables del backend, las claves de cliente de Firebase y la ruta de la plantilla |

Las reglas de seguridad **no están publicadas todavía**: el archivo es una propuesta y debe probarse en *Rules Playground* antes de ejecutar `firebase deploy --only firestore:rules`. Las tres confirmaciones están **sin publicar** en el repositorio remoto.

**Monografía.**

| Apartado | Estado |
|---|---|
| 1.3 | Se agregó el párrafo de limitaciones, con la declaración de que el cumplimiento de los requisitos mínimos no depende del hardware |
| 2.1.3 · 2.1.4 · 2.1.5 | Primera mención de cada tecnología con su versión, conforme al punto 5 de los Lineamientos Técnicos |
| 2.2 | Reescrito: iteración semanal justificada, Tabla 3 con fechas reales y estado, evidencia de aplicación y declaración del uso de asistentes de IA |
| 2.3.1 | Actores sin cambios: queda como punto único de decisión, con una nota que indica los cuatro lugares a ajustar según la opción que se apruebe |
| 2.3.2 | Trece requisitos funcionales reescritos con criterio de aceptación, alineados con la arquitectura de la API |
| 2.3.3 | Ocho requisitos no funcionales con magnitud verificable y mecanismo de comprobación |
| 2.3.4 | Diez casos de uso, cada uno ligado a su requisito |
| 2.3.5 | Priorización MoSCoW (Tabla 4), con el alcance excluido declarado de forma expresa |
| 2.4.1 | Arquitectura de monolito modular, con la justificación del descarte de microservicios y de cómputo sin servidor |
| 2.4.4 | Contrato de la API versión 1 (Tabla 5), con formato de peticiones, de errores, autenticación y versionado |
| 2.5 | Tabla 6 con las versiones reales del stack, tomadas de `pubspec.lock` y del SDK de Flutter |
| 2.7 | Reescrito: sesión, autorización en servidor, autenticación del dispositivo, doble validación, cifrado y variables sensibles |
| 2.8 | Tabla 7 con veintitrés casos de prueba vinculados a los requisitos, listos para registrar resultado y fecha |

Numeración de tablas verificada: 1 a 7, en orden de aparición y con sus referencias en el texto coherentes.

**Backend de la API** (confirmación `c37792e`, 34 archivos, 3176 líneas).

| Pieza | Estado |
|---|---|
| Contrato de la API versión 1 | 26 operaciones sobre 11 rutas, con documentación OpenAPI generada desde el propio código (`/docs`) |
| Validación en servidor | Esquemas que rechazan variable fuera del catálogo, valor fuera del límite físico, unidad incoherente, marca de tiempo futura y campos ajenos al contrato; la respuesta 422 indica el campo rechazado |
| Autenticación | Token de identidad verificado con Firebase Authentication para las personas; clave de dispositivo en `X-Device-Key` para el módulo de adquisición |
| Autorización | Resuelta en el servidor a partir del perfil y del rol; una cuenta desactivada o sin perfil recibe 403 |
| Reglas de negocio | Evaluación de cada lectura contra el rango vigente, generación de una alerta por lectura fuera de rango, referenciada a su lectura, resumen de series y exportación en CSV |
| Persistencia | Interfaz de repositorio con dos implementaciones: Cloud Firestore para el despliegue y memoria para el desarrollo y las pruebas |
| Pruebas | 54 casos automatizados, todos aprobados, ejecutables sin credenciales ni conexión |
| Modo de demostración | `USAR_REPOSITORIO_EN_MEMORIA=true` permite demostrar la API completa sin Firebase, útil para la defensa |

**Bloqueos de entorno resueltos.** La instalación de paquetes con `pip` fallaba con «Permission denied» al desempaquetar, en tres configuraciones distintas; se resolvió con una única ejecución de acceso ampliado, autorizada por el usuario. `uvicorn` y `firebase-admin` quedaron declarados en `requirements.txt` pero **no instalados ni verificados** en este equipo: el arranque real del servidor y la conexión con Firestore deben comprobarse en el despliegue.

**Restos que no se pudieron borrar.** Las carpetas `.tmp-pip/` (raíz) y `backend/pytest-cache-files-*/` quedaron con permisos que el entorno no permite modificar; están excluidas por `.gitignore` para que no entren al repositorio, pero conviene eliminarlas a mano.

**Entorno de Flutter (hallazgo operativo).** El tool de Flutter se colgaba sin dar error porque necesita escribir en `C:\src\flutter\bin\cache\lockfile`, fuera del workspace, y el modo de sandbox `workspace-write` lo impide. Invocando la instantánea directamente, el mensaje es explícito: «Flutter failed to open a file at C:\src\flutter\bin\cache\lockfile». **Consecuencia práctica: toda orden de Flutter (analizar, probar, compilar web, generar APK) requiere aprobación de acceso ampliado en esta sesión.** Alternativa: ejecutarlas el propio usuario en su terminal, que no está sujeta al sandbox.

**Línea base verificada del proyecto Flutter** (con acceso ampliado): Flutter 3.44.8 estable, Dart 3.12.2, DevTools 2.57.0; `flutter pub get` correcto; `flutter analyze` sin ningún problema; `flutter test` con los casos existentes aprobados.

**Capa de API de la aplicación Flutter** (confirmación `acae25c`).

| Pieza | Estado |
|---|---|
| `lib/config/api_config.dart` | Dirección del servicio recibida con `--dart-define=API_BASE_URL`; si no se define, usa `10.0.2.2` en el emulador de Android y `localhost` en web y escritorio. Centraliza el prefijo de versión del contrato |
| `lib/services/api_errores.dart` | Dos tipos de error distintos — `ErrorApi` (rechazo del servidor, con código, mensaje y detalle por campo) y `ErrorConexion` (la petición no se completó) — cada uno con su mensaje para el usuario |
| `lib/services/api_cliente.dart` | Adjunta el token de identidad, traduce el formato de error del contrato, distingue red de negocio, falla sin salir a la red cuando no hay sesión, y decodifica en UTF-8 explícitamente |
| `test/api_cliente_test.dart` | 16 pruebas con un servicio simulado, incluida la del UTF-8 y la de «sin sesión no se llama al servicio» |
| `lib/models/api/modelos_api.dart` | Modelos fieles al contrato del backend: módulo, perfil, rango, lectura, resumen y alerta, con el catálogo de variables y un error propio para las respuestas que no cumplen el contrato |
| `lib/repositories/api/` | Cinco repositorios —módulos, lecturas, rangos, alertas y perfiles— que arman las rutas del contrato, envían solo los campos declarados y convierten las respuestas en modelos |
| `lib/utils/formato_fecha.dart` | Formato de fecha y hora en un solo lugar; antes cada pantalla lo escribía a mano y producía etiquetas distintas para la misma fecha |
| `test/repositorios_api_test.dart` | 25 pruebas: rutas, nombres de campo del contrato, filtros, conversión de modelos y propagación de los errores del servidor |
| `lib/widgets/vista_con_estados.dart` | La vista con sus **cuatro estados** (carga, con datos, vacío y con error), reutilizable por todas las pantallas. El estado de error se presenta distinto según sea fallo de conexión o rechazo del servidor |
| `lib/controllers/lecturas_controller.dart` | Controlador que consulta la API y publica el estado de la vista, el mensaje del fallo y la lista de lecturas fuera de rango |
| `test/vista_con_estados_test.dart` | 11 pruebas de widget de los cuatro estados, incluidas las dos que fijan la diferencia entre «no se pudo conectar» y «la operación fue rechazada» |
| `test/lecturas_controller_test.dart` | 11 pruebas del controlador con el servicio simulado, más la prueba de widget que recorre la caída de la conexión, el reintento y la recuperación |

`flutter analyze` sin problemas y `flutter test` con 63 casos aprobados. Los casos CP-16 y CP-17 de la tabla del apartado 2.8 (estado vacío y estado con error del panel) ya tienen cobertura automatizada a nivel de componente; quedarán completos cuando las pantallas queden conectadas a los repositorios.

**Documento · entregables del 14/09 (fuera del repositorio, en la raíz del proyecto).**

| Pieza | Estado |
|---|---|
| Apartado 1.1.2 | Reescrito con **cuatro soluciones concretas** del dominio (Bluelab, Hanna Instruments, TrolMaster y MyCodo), cada una con qué resuelve y qué deja sin resolver, con fuente citada. Antes solo había categorías genéricas, que es lo que el punto 3.1.1 de los Lineamientos no admite |
| Tabla 1 | Ampliada con las cuatro soluciones y retitulada «Matriz de antecedentes y soluciones existentes»: 11 filas y 6 columnas coherentes. No se agregó una tabla nueva para no renumerar las siete del documento |
| Bibliografía | Cuatro entradas nuevas en el estilo ISO 690-2 del documento; **19 entradas con orden alfabético verificado** |
| `Diagramas Mermaid - Modulo 4.md` | Las tres figuras que exigen los Lineamientos y que no existían: casos de uso (con la correspondencia uno a uno con los requisitos funcionales), arquitectura de componentes y **secuencia del registro de una lectura**, que es la que conviene mostrar en la defensa cuando pregunten por el contrato |
| `Diagrama Mermaid - Antecedentes y Propuesta.md` | Corregido: describía el envío de lecturas «directamente a Cloud Firestore» y listaba cuatro roles, ambas cosas superadas |
| `Anexo A - Manual de usuario.md` | **Entregable obligatorio del lineamiento que no existía.** Quince apartados: qué es el sistema, requisitos, perfiles, acceso, navegación y una sección por pantalla con los rótulos reales verificados contra el código, más los cuatro estados de las vistas, preguntas frecuentes, glosario de las siete variables y buenas prácticas |
| `Anexo B - Manual de instalacion y despliegue.md` | **Segundo entregable obligatorio que faltaba.** Siete secciones: qué se instala, requisitos, instalación local (con el modo de demostración sin credenciales), despliegue completo del servicio y de la aplicación, operación y mantenimiento, problemas frecuentes y lo que no debe hacerse. Numeración y referencias cruzadas verificadas |
| `Anexos C a F.md` | Enlace al repositorio con las instrucciones de acceso para el tribunal, la dirección pública y el archivo instalable (**pendientes de completar al desplegar**), los cuatro diagramas y su forma de incorporarlos, y la documentación complementaria con lo que no debe incluirse |
| Presupuesto de páginas | Los anexos **no cuentan** para el límite de 30 a 40 páginas, así que la documentación de soporte puede ser exhaustiva. **El cuerpo, en cambio, ya excede el límite**: medido el 14/09, tiene 15 268 palabras (unas 41 páginas de texto) y, sumadas las 8 tablas, los 2 fragmentos de código y las figuras previstas, llegaría a 46 o 48 páginas. El plan de recorte —seis medidas con su ahorro estimado, entre 1 700 y 1 800 palabras— quedó escrito dentro del propio borrador, en la nota de presupuesto de extensión, y conviene validarlo con el tutor antes de aplicarlo |
| Archivos superados, marcados | Los capítulos sueltos (`Capitulo 1/2/3 - ... (Diplomado)`, `Capitulo I`, `Capitulo I - Mejorado`) quedaron marcados con una advertencia al inicio, **en Markdown y también en los `.docx`** (insertada con python-docx, verificando que no se perdiera contenido). La versión vigente es `Monografia - Borrador Completo (Diplomado).md`. Motivo: el Capítulo 1 llegó a tener cuatro versiones en carpetas distintas y ya costó tiempo decidir cuál valía |
| `docs/11_AUDITORIA_CUMPLIMIENTO.md` | **Auditoría punto por punto** contra el Formato 2020 y los Lineamientos 2026: aspectos formales, contenido técnico de cada apartado obligatorio, los ocho requisitos mínimos, las convenciones de elementos técnicos y el inventario de los 34 marcadores que quedan sin completar, con el orden en que conviene cerrarlos. Los puntos 3 y 4 de ese orden —desplegar y ejecutar los casos de prueba— cierran 28 marcadores de una sola vez |
| Rótulo «Cerrar sesion» | Corregido a «Cerrar sesión» en la barra lateral; verificado con `flutter analyze` y las 63 pruebas |
| Apartado 2.6 Implementación | **Reescrito por completo** (1506 palabras en cinco subapartados): componentes efectivamente construidos, seis decisiones técnicas con su fundamento, cinco dificultades reales con su resolución —incluida la del dispositivo que no podía autenticarse como se había previsto— y dos fragmentos de código ilustrativos. Los fragmentos se verificaron **literalmente** contra los archivos del repositorio y respetan el límite de veinte líneas (12 y 18) |

**Recomendación pendiente de decisión.** El repositorio versiona el código y las bitácoras, pero **la monografía y los anexos no están bajo control de versiones**: viven como archivos sueltos en la raíz. Con cuatro semanas de escritura por delante, conviene incorporarlos al repositorio (o a uno propio para el documento) para no depender de copias manuales.

**Despliegue preparado y comando de arranque verificado.**

| Pieza | Estado |
|---|---|
| `backend/render.yaml` | Blueprint del servicio para Render, validado con PyYAML: nombre, runtime, plan, región, directorio raíz, comandos de compilación y arranque, ruta de salud y las siete variables de entorno (cuatro de ellas se cargan a mano en el panel, ninguna en el repositorio) |
| `docs/10_DESPLIEGUE.md` | Guía paso a paso del despliegue completo (API, aplicación web y APK), con la obtención de la clave de la cuenta de servicio, la verificación de los ocho requisitos mínimos, las nueve capturas que exige el apartado 2.9, los problemas previsibles y lo que no debe hacerse |
| `backend/app/semilla.py` | Modo de demostración con datos: perfil de lechuga con seis rangos, dos módulos (uno inactivo), doce lecturas repartidas en treinta y seis horas y tres alertas. Las lecturas se registran con **el mismo servicio que usa la ingesta real**, así que las alertas las produce la regla de negocio y no la semilla |
| `uvicorn` 0.52.4 | Instalado; el arranque real se verificó con el comando exacto del despliegue |

**Verificación automática en el repositorio** (`.github/workflows/verificacion.yml`).

Se incorporó integración continua con dos trabajos independientes, de modo que un fallo en una parte no
oculte el estado de la otra:

| Trabajo | Qué comprueba |
|---|---|
| Servicio de la API | Instala las dependencias declaradas —incluidas `uvicorn` y `firebase-admin`, con lo que comprueba de paso que el servicio pueda desplegarse en Linux— y ejecuta las pruebas del backend |
| Aplicación Flutter | Prepara la configuración de Firebase a partir de la plantilla (la real no está en el repositorio), analiza el código, ejecuta las pruebas y **compila la versión web**, que es el artefacto que se publica en Firebase Hosting |

Dos razones para haberlo montado ahora: resuelve el problema de que **en este entorno el tool de Flutter
no puede ejecutarse sin permisos ampliados**, de modo que la verificación deje de depender del equipo del
autor; y su historial de ejecuciones es **evidencia de las pruebas del apartado 2.8**, con el resultado de
cada confirmación. El repositorio muestra el distintivo de estado en su archivo README.

> Para que la verificación corra hace falta **publicar las confirmaciones**: el flujo se dispara con el
> envío a la rama principal. Mientras el trabajo esté solo en local, el código del panel conectado a la
> API sigue sin analizar.

**Verificación de extremo a extremo del servicio real** (14/09/2026, contra el repositorio en memoria):

| Comprobación | Resultado |
|---|---|
| `GET /api/v1/salud` | 200 · `{"estado":"ok","version_api":"v1","entorno":"desarrollo","base_de_datos":"conectada"}` |
| `POST /api/v1/lecturas` con clave de dispositivo válida | 201 · lectura almacenada con `estado_rango: "alto"`, es decir la evaluación del rango ocurrió de extremo a extremo |
| `POST /api/v1/lecturas` con clave equivocada | 401 · «La clave del módulo de adquisición no es válida.» |
| `GET /api/v1/lecturas` sin token | 401 |
| `GET /api/v1/openapi.json` | 200 · 31 KB de contrato publicado |
| Pruebas del backend | 59 casos aprobados |

**Herramientas y versiones verificadas.** Flutter 3.44.8 (canal estable), Dart 3.12.2, `cloud_firestore` 6.9.0, `firebase_core` 4.14.0, `firebase_auth` 6.6.1, `provider` 6.1.5+1, `http` 1.6.0, `shared_preferences` 2.5.5, `geolocator` 14.0.3, `flutter_map` 8.3.2, `latlong2` 0.10.1.

### 7.2 Pendiente, en orden

1. **Tutoría del 14/09** — cerrar las tres decisiones de la ficha: alcance de roles, backend con API propia y recortes.
2. **Documento (E1)** — ajustar 1.5 y 2.3.1 a la decisión de roles y revisar que el objetivo específico 1 y el apartado 3.2 queden coherentes; confirmar cuál es el archivo maestro del documento: el borrador en Markdown o el documento de Word generado con la plantilla oficial.
3. **Repositorio** — publicar las tres confirmaciones; confirmar el acceso del docente; probar y publicar las reglas.
4. **Iteración 2 (E2)** — lo que falta del vertical funcional:
   - instalar `uvicorn` y `firebase-admin`, arrancar el servicio y verificar la conexión con Cloud Firestore;
   - crear los índices compuestos de Firestore que exigen las consultas de lecturas y alertas;
   - migrar la capa de datos de Flutter para que consuma la API en lugar de `SharedPreferences`;
   - desplegar la API en Render y publicar la aplicación web en Firebase Hosting, con su dirección pública;
   - registrar las capturas del panel de la plataforma (compilación, variables de entorno y registros) para el apartado 2.9.
5. **Capa de API de la aplicación (en curso)** — el cliente, los modelos del contrato y los cinco repositorios están implementados y probados. Falta: **conectar las pantallas** con sus cuatro estados de vista (carga, con datos, vacío y error) y retirar la persistencia local de los datos del dominio. Es lo que cierra el requisito mínimo 3. Los modelos locales (`Cultivo`, `Medicion`, `Alerta`, `VariableRango`) se retiran a medida que cada pantalla migra; no se convierten entre sí porque su forma es distinta y la conversión perdería datos.
6. **Extensión del documento** — el cuerpo excede el límite institucional en unas seis páginas. El plan de recorte está medido y escrito dentro del borrador; hay que validarlo con el tutor y aplicarlo antes del cierre de la iteración 4. Es la única tarea del proyecto que **crece sola** si no se atiende.
