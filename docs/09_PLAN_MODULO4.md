# Plan de trabajo — Módulo 4 (SIGVACH)

Documento interno de trabajo. No forma parte de la monografía.
Base normativa: *P1 Apertura Módulo 4* (UAJMS, 2026), *Lineamientos Técnicos Complementarios* (2026) y
*Formato para la Elaboración del Trabajo Final* (Dirección de Posgrado, 2020).

---

## 1. Calendario real

| Fecha | Hito | Qué debe estar cerrado |
|---|---|---|
| Dom 13 sep | Preparación de la tutoría | Ficha de proyecto, arreglos de repositorio |
| Lun 14 sep | Primera tutoría | Problema en una frase, tres objetivos, pantallas, decisiones de alcance |
| Sáb 19 sep 23:59 | **E1 · Perfil de proyecto** | Capítulo 1, 2.2 metodología, 2.3 requisitos, repositorio inicializado |
| Sáb 26 sep 23:59 | **E2 · Vertical funcional** | 2.4 diseño técnico, frontend navegable, API con CRUD, **primer despliegue público** |
| Sáb 3 oct 23:59 | **E3 · Checkpoint técnico** | 2.7 seguridad, 2.8 pruebas con evidencia, borrador de los Capítulos 1 y 2 |
| Sáb 10 oct 23:59 | **E4 · Documento y sistema** | Documento completo, despliegue verificado, manuales y anexos |
| Lun 12 – jue 15 oct | Defensa | 7 minutos de demostración en vivo + 5 de preguntas |

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
