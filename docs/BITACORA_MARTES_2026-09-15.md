# 📓 Bitácora — Sesión del lunes 14 (tarde) y martes 15 de septiembre de 2026

**Proyecto:** SIGVACH — Sistema de Gestión de Variables para Cultivos Hidropónicos
**Grupo:** 3 · **Tutoría:** martes 15/09 a las 17:00 · **Defensa:** martes 13/10 a las 17:00
**Objetivo de la sesión:** poner el sistema en marcha de punta a punta (aplicación → servicio → Cloud Firestore) y resolver los bloqueos que impedían demostrarlo.

**Alcance.** La sesión empezó el lunes 14 por la tarde, con la revisión del documento y de la configuración, y continuó el martes 15 por la mañana con la puesta en marcha del servicio y la localización de la causa raíz que impedía cargar el panel.

---

## 1. Punto de partida

| Pieza | Estado al comenzar |
|---|---|
| Servicio (API) | Existía y arrancaba, pero **no lograba conectarse a Firestore** |
| Credencial de Firebase | La clave estaba descargada, pero **no era leída por el servicio** |
| Base de datos | Creada y vacía (sin perfiles, módulos, rangos ni lecturas) |
| Aplicación web | Arrancaba, pero mostraba **"No se pudo conectar con el servidor"** |
| Monografía | Con los recortes de extensión aplicados (14 527 palabras de cuerpo) |

---

## 2. Diagnóstico 1 — El servicio rechazaba todos los tokens

**Síntoma.** Al iniciar sesión, el panel mostraba: *"La operación no pudo completarse. El token de identidad no es válido o expiró."*

**Causa.** El SDK de Firebase se inicializaba **de forma perezosa**, dentro del repositorio de Firestore, y solo al tocar la base de datos. Pero la primera petición autenticada **verifica el token antes** de tocar la base: en ese momento el SDK no existía y la verificación fallaba. La excepción real que el código ocultaba era:

```
ValueError: The default Firebase app does not exist.
Make sure to initialize the SDK by calling initialize_app().
```

**Corrección.** Se añadió `asegurar_sdk_firebase()` en `backend/app/main.py` y se invoca en el ciclo de vida del servicio, de modo que el SDK se inicializa **al arrancar**, tanto en modo real como en modo demostración. Cambio: `backend/app/main.py`, +53 / −3 líneas.

**Verificación.**

| Comprobación | Resultado |
|---|---|
| SDK inicializado al arrancar (modo real) | 1 aplicación ✅ |
| SDK inicializado al arrancar (modo demostración) | 1 aplicación ✅ |
| Pruebas del servicio | **59 casos, todos aprobados** (código de salida 0) ✅ |

---

## 3. Diagnóstico 2 — El puerto 8000 está reservado en el equipo

**Síntoma.** El servicio no podía escuchar en el puerto 8000:

```
ERROR: [WinError 10013] Intento de acceso a un socket no permitido
por sus permisos de acceso
```

**Causa.** Windows reserva rangos de puertos para Hyper-V/WSL; el 8000 cae dentro de esa reserva en este equipo.

**Corrección.** Se adopta el **puerto 8011** en todos los puntos:

| Archivo | Cambio |
|---|---|
| `SIGVACH.bat` (lanzador, fuera del repositorio) | `PUERTO=8011` |
| `.env` (no versionado) | `PORT=8011` |
| `.vscode/launch.json` y `.vscode/tasks.json` (no versionados) | perfil F5 y tarea de Flutter con 8011 |
| `lib/config/api_config.dart` | dirección local por defecto: 8011 |

Verificado: `http://localhost:8011/api/v1/salud` responde
`{"estado":"ok","version_api":"v1","entorno":"desarrollo","base_de_datos":"conectada"}`.

---

## 4. Diagnóstico 3 — `localhost` frente a `127.0.0.1`

Se sospechó que el navegador resolviera `localhost` como IPv6 (`::1`) mientras el servicio escucha en IPv4, de modo que la petición se rechazara. **Se descartó**: en Firefox y en Brave, `localhost:8011` y `127.0.0.1:8011` responden igual.

Aun así se dejó la aplicación apuntando a **`127.0.0.1`** en lugar de `localhost`, porque es determinista y evita depender de la resolución de nombres del equipo.

---

## 5. Carga de datos de ejemplo en Cloud Firestore

La base estaba vacía, de modo que el panel no tenía nada que mostrar. Se cargaron datos de ejemplo **con el código del proyecto**:

| Colección | Documentos | Contenido |
|---|---|---|
| `perfiles_cultivo` | 1 | `perfil-lechuga` (Lechuga, predefinido) |
| `modulos_cultivo` | 2 | `modulo-1` (activo, Invernadero Norte) y `modulo-2` (inactivo) |
| `rangos` | 6 | pH, EC, TDS, temperatura de solución, temperatura ambiental y humedad |
| `lecturas` | 12 | Con 3 valores fuera de rango (pH 7,4; EC 2,3; humedad 42 %) |
| `alertas` | 3 | Generadas por la **regla de negocio**, no por la semilla |

**Hallazgo asociado.** El archivo `backend/app/semilla.py` **solo puede sembrar el repositorio en memoria**: el repositorio de Firestore genera identificadores aleatorios y descarta el campo `id` que recibe (`documento.pop("id")`), por lo que la semilla no encuentra después el módulo `modulo-1` que ella misma creó. Mejora propuesta (3 líneas): que `crear_perfil`, `crear_modulo` y `crear_rango` respeten el identificador cuando se les entrega.

---

## 6. Causa raíz del fallo del panel — Faltan índices compuestos en Firestore

**Síntoma.** La aplicación mostraba: *"No se pudo comunicar con el servidor (detalle: La petición excedió el tiempo de espera.)"*.

**Cómo se localizó.** Se reprodujeron las consultas **exactas del panel** con un token de identidad real:

| Consulta del panel | Resultado |
|---|---|
| `/modulos?activo=true` | **HTTP 500** (error interno) |
| `/lecturas?modulo_id=modulo-1&limite=200` | **HTTP 500** |
| `/alertas?estado=activa&modulo_id=modulo-1` | **HTTP 500** |
| `/rangos?perfil_id=perfil-lechuga` | HTTP 200 ✅ |

**Causa.** Las consultas que combinan un **filtro** con un **ordenamiento por otro campo** requieren un **índice compuesto** en Firestore. La excepción real es:

```
FailedPrecondition: 400 The query requires an index.
```

**Los tres índices que faltan** (pendiente que ya figuraba en el plan del Módulo 4):

| Colección | Campos del índice | Consulta que lo necesita |
|---|---|---|
| `modulos_cultivo` | `activo` ↑ , `nombre` ↑ | Módulos activos ordenados por nombre |
| `lecturas` | `modulo_id` ↑ , `timestamp` ↓ | Lecturas de un módulo, más recientes primero |
| `alertas` | `estado` ↑ , `modulo_id` ↑ , `timestamp` ↓ | Alertas activas de un módulo, más recientes primero |

**Cómo se crean.** Desde la consola de Firebase (Firestore Database → Índices → Crear índice), o con el enlace que la propia excepción entrega. La cuenta de servicio del proyecto **no tiene permiso** para crearlos por API (HTTP 403 `PERMISSION_DENIED`), de modo que es un paso manual del despliegue. Tardan de 1 a 5 minutos en quedar *Habilitados*.

---

## 7. Anexo didáctico — Qué es un índice (explicado con vectores)

**Un vector guarda las cosas por su POSICIÓN.**

```dart
final lecturas = ['pH 6.1', 'pH 7.4', 'pH 6.3'];
lecturas[0]  // 'pH 6.1'  -> porque está en la posición 0
```

La posición depende del **orden de inserción**: si se agrega un elemento al principio, todos se corren. Y para responder *"las lecturas del módulo 1"* habría que **recorrer todo el vector** comparando uno a uno.

**Una base de datos guarda las cosas por su CONTENIDO.** Los documentos **no tienen posición**: se identifican por un identificador y tienen campos:

```
documento A → modulo_id: modulo-1 | variable: ph | valor: 6.1 | timestamp: 13/09 22:10
documento B → modulo_id: modulo-1 | variable: ph | valor: 7.4 | timestamp: 13/09 20:10
documento C → modulo_id: modulo-1 | variable: ec | valor: 1.5 | timestamp: 13/09 18:10
documento D → modulo_id: modulo-2 | variable: ph | valor: 6.0 | timestamp: 12/09 10:00
```

**El índice es un catálogo ordenado que la base mantiene aparte**, como el índice al final de un libro: no es contenido nuevo, es una lista ordenada que permite encontrar algo sin leerlo todo. En este caso, con el índice `(modulo_id ↑ , timestamp ↓)` el catálogo sería:

```
1º → modulo-1 | 13/09 22:10 | ph | 6.1   (documento A)
2º → modulo-1 | 13/09 20:10 | ph | 7.4   (documento B)
3º → modulo-1 | 13/09 18:10 | ec | 1.5   (documento C)
4º → modulo-2 | 12/09 10:00 | ph | 6.0   (documento D)
```

Con el catálogo, la base va **directo al bloque de `modulo-1`** y lo entrega ya ordenado; sin él tendría que leer todos los documentos y ordenarlos después. Por eso Firestore **rechaza** la consulta en lugar de resolverla lentamente.

**Por qué "compuesto" (varios campos).** Es como una guía telefónica: ordenada solo por apellido, todos los «Pérez» aparecen juntos pero desordenados por nombre; ordenada por **apellido y luego nombre**, aparecen juntos y ordenados. El índice compuesto declara ese orden de prioridad entre campos.

**Cuadro comparativo**

| Pregunta | Vector | Base de datos |
|---|---|---|
| "Dame el elemento 3" | `v[3]` inmediato | Los documentos no tienen posición |
| "Dame los pH del módulo 1" | Recorrer todo y comparar | Con índice: va directo |
| "Damelos ordenados por fecha" | Ordenar después | El índice ya los tiene ordenados |
| "Dos criterios a la vez" | No es posible | Sí, con índice compuesto |

**Diferencias de fondo.** El subíndice de un vector es **posicional** (0, 1, 2… en orden de inserción); el índice de una base de datos es **por contenido** (ordenado por el valor de los campos, sean textos o fechas) y puede ser **compuesto**. Además, el índice **cuesta** espacio y escrituras algo más lentas, y **no modifica los documentos**: es una estructura auxiliar.

---

## 8. Mejoras recomendadas al servicio

1. **Errores 500 sin cabeceras CORS.** Cuando ocurre una excepción no controlada, la respuesta no incluye `Access-Control-Allow-Origin`, de modo que el navegador no puede leerla y la aplicación la interpreta como un fallo de conexión (o de tiempo agotado) en lugar de un error del servidor. Conviene un manejador de excepciones que devuelva un `ErrorApi` (por ejemplo 503) y registre la causa.
2. **Registrar la causa real de los errores.** Hoy se pierde: el mensaje al usuario es siempre el mismo y el registro del servicio no conserva la excepción.
3. **Tiempo de espera de la aplicación.** La aplicación espera 20 segundos y la **primera** consulta a Firestore puede tardar 25-30 segundos (arranque en frío). Conviene elevar el tiempo de espera o mantener el servicio "caliente" antes de la demostración.
4. **Identificadores en la semilla** (apartado 5): permitir que el repositorio respete el `id` recibido, para que la misma semilla sirva en memoria y en la base real.

---

## 9. Verificaciones ejecutadas

| Comprobación | Resultado |
|---|---|
| Pruebas del servicio (`pytest`) | **59 aprobadas**, sin fallos ✅ |
| Verificador estructural de Dart | 74 archivos sin hallazgos ✅ |
| CORS: preflight `OPTIONS` con `Origin` | HTTP 200 con `Access-Control-Allow-Origin: http://localhost:8080` ✅ |
| CORS: `GET` autenticado con `Origin` | HTTP 200 con las cabeceras correctas ✅ |
| Peticiones autenticadas sin filtros (`/perfiles`, `/rangos`) | HTTP 200 ✅ |
| Peticiones autenticadas **con filtros** (`/modulos`, `/lecturas`, `/alertas`) | HTTP 500 → **por falta de índices** ❌ |
| Credenciales versionadas | Ninguna: `.env` está excluido por `.gitignore` ✅ |

---

## 10. Cambios realizados en el repositorio

| Archivo | Cambio | Estado |
|---|---|---|
| `backend/app/main.py` | Inicialización del SDK de Firebase al arrancar (+53 / −3) | Modificado |
| `lib/config/api_config.dart` | Dirección local: puerto 8011 y `127.0.0.1` | Modificado |
| `lib/controllers/estado_de_vista.dart` | Muestra el detalle interno del fallo (**cambio de diagnóstico**) | Modificado |
| `.env` (no versionado) | `PORT=8011` y credencial de servicio | Modificado |
| `.vscode/launch.json`, `.vscode/tasks.json` (no versionados) | Puerto 8011 | Modificados |

Fuera del repositorio: `SIGVACH.bat` (panel de control con las dos ventanas: motor y aplicación).

---

## 11. Pendientes y su estado al cierre

| # | Pendiente | Estado |
|---|---|---|
| 1 | Crear los índices compuestos de Firestore | ✅ **Hecho**: declarados en `firestore.indexes.json` y desplegados con `firebase deploy --only firestore:indexes` (5 en total, incluido el de `lecturas` por variable creado a mano desde la consola) |
| 2 | Comprobar el panel con datos reales | ✅ **Hecho**: el panel carga el módulo, las 7 variables y las alertas |
| 3 | Recompilar la aplicación tras los cambios de configuración | ✅ **Hecho** |
| 4 | Tutoría del martes 15/09 a las 17:00 | ⏳ Hoy, con la nota de decisiones |
| 5 | Migrar las pantallas del dominio al servicio | ✅ **Hecho**: Variables, Alertas, Cultivos (módulos) y Rangos; además el **Perfil** con el recurso nuevo de usuarios |
| 6 | Desplegar (alojamiento, clave de servicio, índices, reglas, APK) | ⏳ Pendiente |
| 7 | Decidir si el detalle de diagnóstico en pantalla se conserva | ⏳ Pendiente (hoy resultó muy útil: permitió distinguir «tiempo agotado» de «conexión rechazada») |
| 8 | `flutter analyze` y `flutter test` en el equipo del autor | ⏳ Pendiente (el entorno de trabajo usado en esta sesión no puede ejecutar el analizador) |

---

## 12. Cifras de la sesión

| Dato | Valor |
|---|---|
| Diagnósticos cerrados | 5 (token, puerto, IPv4/localhost, datos y tiempos de espera) |
| Causa raíz del fallo del panel | Índices compuestos ausentes |
| Índices declarados y desplegados | 5 |
| Datos en Firestore al cierre | 1 perfil, 2 módulos, 6 rangos, 15 lecturas, 4 alertas |
| Pruebas del servicio | **69 aprobadas** (59 previas + 10 del perfil del usuario) |
| Palabras de la monografía | 14 746 (se añadió el apartado de índices en 2.4.2) |
| Pantallas migradas al servicio en la sesión | 5 (Variables, Alertas, Cultivos, Rangos y Perfil) |

---

## 13. Desenlace: los índices y el panel funcionando

Los índices se declararon en el archivo `firestore.indexes.json` del proyecto —que no existía— y se desplegaron con la CLI de Firebase:

```bash
firebase deploy --only firestore:indexes
```

Declararlos en el repositorio, y no solo crearlos desde la consola, tiene dos consecuencias que interesan al trabajo final: quedan **versionados** (cualquiera puede recrearlos con un comando) y dejan de ser un paso informal sin registro. Además se añadió al `firebase.json` la referencia al archivo de índices.

Durante la jornada aparecieron **dos consultas más** que necesitaban índice propio: la lista de alertas activas **sin filtrar por módulo** (pantalla de alertas) y el filtro de lecturas **por variable** (historial). El archivo quedó con cinco índices.

**Lección registrada.** Un índice ausente no se manifiesta como lentitud, sino como un error interno del servicio; y como las respuestas 500 no llevan cabeceras CORS, el navegador no puede leerlas y la aplicación informa de un fallo de conexión. De ahí la mejora recomendada en el apartado 8: tipificar los errores internos y registrarlos.

---

## 14. Migración de las pantallas del dominio al servicio

Antes de esta sesión, cuatro pantallas —y la de perfil— leían datos locales del navegador (SharedPreferences) o escribían directamente en Firestore desde el cliente. Al cierre, todas consultan al servicio:

| Pantalla | Fuente anterior | Fuente actual | Controlador nuevo |
|---|---|---|---|
| Variables | Datos locales (5 tarjetas fijas) | Servicio (7 variables del catálogo) | `PanelController` (reutilizado) |
| Alertas | Datos locales | Servicio (activas e historial) | `AlertasController` |
| Cultivos | Datos locales | Servicio (módulos de cultivo, alta/edición/activación/baja) | `ModulosController` |
| Rangos | Datos locales | Servicio (consulta y edición de límites) | `RangosController` |
| Perfil | Datos locales + escritura directa | Servicio (recurso nuevo `/usuarios/perfil`) | `PerfilController` |

Todas usan el mismo componente de **cuatro estados** (cargando, con datos, vacío y error) y distinguen el fallo de conexión del rechazo del servidor, que es el criterio que se documentó en el apartado 2.6.

**Efecto colateral deseable:** el panel y la pantalla de variables comparten el mismo controlador, de modo que ya no pueden mostrar información distinta sobre el mismo módulo.

---

## 15. Recurso nuevo en el servicio: el perfil del usuario

El servicio no exponía los usuarios: la aplicación los gestionaba escribiendo directamente en Firestore, con una excepción explícita en las reglas de seguridad. Se añadió el recurso `/api/v1/usuarios` con dos operaciones:

| Operación | Ruta | Quién |
|---|---|---|
| Consultar el perfil propio | `GET /api/v1/usuarios/perfil` | Cualquier cuenta con perfil habilitado |
| Actualizar los datos personales | `PATCH /api/v1/usuarios/perfil` | El propio usuario |

**Decisión de seguridad.** El esquema de entrada admite únicamente `nombre`, `telefono` y `cargo`: el **rol** y el estado de **activación** no son campos del contrato, de modo que no se rechazan con un mensaje —sencillamente no existen como entrada— y ningún cliente puede elevar sus privilegios ni reactivar su cuenta por esta vía. Dos pruebas lo verifican.

Archivos: `backend/app/rutas/usuarios.py` (nuevo), `backend/app/esquemas.py`, `backend/app/repositorios/{base,memoria,firestore}.py`, `backend/app/rutas/__init__.py` y `backend/pruebas/test_api_usuarios.py` (10 pruebas nuevas).

---

## 16. Ajuste del tiempo de espera del cliente

Al reiniciar el servicio, la primera consulta volvió a fallar con *«la petición excedió el tiempo de espera»*: el arranque en frío de Firestore tarda entre 25 y 30 segundos y el cliente esperaba 20. Se elevó el límite a **45 segundos** en `lib/config/api_config.dart`, con la razón escrita en el propio código.

Se comprobó que ninguna prueba de la aplicación dependa de ese valor: las pruebas construyen sus clientes con su propio tiempo de espera (2 segundos) para simular respuestas.

---

## 17. Estado final del sistema al cierre de la jornada

| Pieza | Estado |
|---|---|
| Servicio (API) | ✅ En marcha en el puerto 8011, con base de datos conectada |
| Autenticación | ✅ Firebase Authentication + perfil y rol resueltos por el servicio |
| Base de datos | ✅ Cloud Firestore con datos del dominio y cinco índices |
| Aplicación | ✅ Panel, Variables, Cultivos, Alertas, Historial, Rangos y Perfil contra el servicio |
| Pruebas del servicio | ✅ 81 aprobadas |
| Documentación | ✅ Monografía con el apartado de índices, mapa del proyecto, nota de tutoría y esta bitácora |

**Pendiente para la entrega final:** completar la migración del panel de administración de usuarios (que aún escribe en Firestore desde el cliente), publicar las reglas de seguridad, desplegar el servicio y la aplicación, y ejecutar el analizador y las pruebas de la aplicación en el equipo del autor.

---

*Bitácora de trabajo del Módulo 4. Elaborada al cierre de la sesión del lunes 14 y del martes 15 de septiembre de 2026.*

---

# Segunda parte de la jornada — martes 15, desde las 14:00

## 18. Entrega E1 — Perfil de proyecto

El docente entregó en la tutoría la **plantilla del perfil de proyecto** (entregable E1) y se completó con el contenido del proyecto: **14 tablas y 5 figuras**, conservando estilos, numeración y márgenes de la plantilla y eliminando los recuadros grises de instrucciones.

| Elemento | Contenido incorporado |
|---|---|
| Tabla 1 | Datos generales: título, línea de investigación, decisión de la tutoría (Aprobado), alcance acordado, enlace al repositorio y al tablero, fecha de entrega |
| 1.1 | Estado del conocimiento y contraste con cuatro soluciones del dominio, con la columna «qué deja sin resolver» completa |
| 1.2 | Caracterización del proceso actual y tres puntos críticos con su dato del contexto |
| 1.3 · 1.4 | Planteamiento y justificación (factibilidad técnica, pertinencia e impacto esperado) |
| 1.5 | Objetivo general y seis objetivos específicos, con la tabla de correspondencia objetivo – evidencia (2.3 a 2.9) – conclusión |
| 2.2 | Marco de trabajo (Scrum reducido con sprints de una semana), justificación, plan de sprints y tablero |
| 2.3 | Tres actores, 13 requisitos funcionales con dos criterios de aceptación cada uno, 8 no funcionales con métrica, 5 capacidades fuera de alcance y 3 casos de uso descritos |
| 2.4 | Arquitectura con justificación citada por identificador de requisito, modelo de datos con su diccionario, criterios de usabilidad y contrato de la API |
| 2.5 | Stack tecnológico con versión y criterio referido a un requisito |

**Figuras.** El entregable exige cinco: el tablero, los casos de uso, la arquitectura, el modelo de datos y los bocetos de interfaz. Dos de ellas **no existían** y se generaron por código: el **tablero Kanban** y el **modelo de datos**.

**Tablero de tareas.** La plantilla exige un tablero con enlace y captura, y no existía. Se creó `docs/TABLERO.md`, versionado en el repositorio, con tres columnas —backlog, en curso con límite de dos tarjetas y hecho— y el estado real del proyecto: **11 tareas terminadas, 2 en curso y 8 en el backlog**.

**Proporción del alcance indispensable.** El MoSCoW se reajustó a **7 de 13** requisitos funcionales como *Must* (53,8 %) y **9 de 21** requisitos en total (42,9 %), dentro del límite del 60 % que fija el módulo.

---

## 19. Decisión sobre los roles: dos roles de usuario

La tutoría recomendó documentar **dos roles** —Administrador y Operador— en lugar de los cuatro perfiles del borrador inicial. La decisión se aplicó en toda la documentación: el objetivo específico 1, el apartado 2.3.1, los casos de uso del 2.3.4, el apartado 2.7 y la nota del resumen; la **Figura 1 se regeneró con los dos actores**.

**El nivel de solo consulta no se descartó: quedó como extensión prevista.** El servicio incorpora un nivel de autorización de lectura (`requiere_consulta`) y un nombre de rol configurable por variable de entorno (`ROL_INVITADO`), de modo que habilitar cuentas de visitante no obligue a modificar la lógica de autorización. Se cubrió con **doce pruebas** —doce operaciones de lectura lo admiten y cada intento de escritura se rechaza con 403— y se documentó como **recomendación del Capítulo 3**.

---

## 20. Alineación de la documentación con la plantilla del docente

| Ajuste | Detalle |
|---|---|
| Requisitos no funcionales | Se reordenaron y renumeraron según la plantilla del entregable: RNF-01 Rendimiento, RNF-02 Seguridad, RNF-03 Usabilidad, RNF-04 Compatibilidad y RNF-05 Disponibilidad, seguidos de los tres adicionales (adaptabilidad, mantenibilidad y trazabilidad) |
| Referencias | Se actualizaron las cuatro filas de casos de prueba que citaban los identificadores anteriores (CP-09, CP-20, CP-21 y CP-22) y las notas de revisión correspondientes |
| MoSCoW | Se alineó con la clasificación del entregable, para que ambos documentos declaren la misma proporción de alcance indispensable |
| Contrato de la API | Se incorporó el recurso `usuarios` y el total pasó de veintiséis a **veintiocho operaciones**; se declaró además el servicio externo de contexto climático (Open-Meteo), que no figuraba en el apartado del stack |

---

## 21. Hallazgos de la jornada

Tres defectos reales, dos pendientes de corregir:

1. **La obtención del token de identidad no tenía límite de tiempo** *(corregido)*. Cuando el proveedor de identidad debía renovar el token y la petición no completaba —por ejemplo, porque un bloqueador de rastreadores la intercepta—, la aplicación quedaba en «cargando información» de forma **indefinida**, sin mensaje y sin acción posible. Se acotó a quince segundos y se informa como fallo de conexión, con su acción de reintento. **Este defecto impidió la demostración durante la tutoría**: el servicio y la base de datos respondían con normalidad, como se verificó después (las consultas del panel respondieron 200 en unos tres segundos).
2. **La aplicación abría por defecto el primer módulo por orden alfabético** *(pendiente)*. Durante las pruebas, un módulo creado para verificar el alta —`Modulo 3`, escrito sin tilde— se ordenaba antes que `Módulo 1`, de modo que la aplicación presentaba un módulo sin lecturas. El comportamiento del estado vacío fue el correcto; lo que conviene revisar es el criterio de selección inicial: priorizar el módulo con lecturas o, en su defecto, el más antiguo.
3. **El indicador de estado del panel produce falsos negativos** *(pendiente)*. Comprueba el puerto con `netstat` y en este equipo informó «apagado» mientras el servicio respondía con normalidad. Conviene sustituirlo por una consulta real al endpoint de salud.

**Aprendizaje de diagnóstico que conviene conservar.** Un índice ausente en Firestore no se manifiesta como lentitud, sino como error interno del servicio; y como las respuestas de error no incluyen cabeceras CORS, el navegador no puede leerlas y la aplicación lo presenta como un fallo de conexión. Se resolvió declarando los índices en `firestore.indexes.json` y desplegándolos con la CLI, de modo que queden versionados en el repositorio.

**Y una observación sobre los tiempos de espera.** La primera consulta posterior al arranque del servicio tarda entre veinticinco y treinta segundos, porque abre la conexión con Cloud Firestore. El tiempo máximo de espera del cliente se elevó de veinte a **cuarenta y cinco segundos** para no confundir una espera con un fallo; conviene, además, encender el servicio unos minutos antes de una demostración.

---

## 22. Estado al cierre de la jornada

| Pieza | Estado |
|---|---|
| Servicio (API) | ✅ 28 operaciones documentadas con OpenAPI; **81 pruebas aprobadas** |
| Autorización | ✅ Dos roles documentados (administrador y operador) y un nivel de solo consulta disponible como extensión, con pruebas |
| Base de datos | ✅ Cloud Firestore con cinco índices compuestos declarados en el repositorio |
| Aplicación | ✅ Siete pantallas consumiendo el servicio, con los cuatro estados de vista |
| Documento E1 | ✅ Completo: 14 tablas y 5 figuras; pendiente la revisión final, la exportación a PDF y la carga en el aula virtual |
| Monografía | ✅ Alineada con la plantilla del docente (roles, requisitos y priorización) |
| Monografía (extensión) | ⏳ Pendiente de recorte final: el cuerpo está en torno a 39 páginas frente al límite de 30 a 40, y la tabla de pruebas del 2.8 sigue en revisión |

**Pendientes inmediatos.**

1. Cargar la entrega **E1** antes del **domingo 20 de septiembre a las 23:59** (se preparará el viernes 19).
2. Corregir el criterio de selección de módulo y el indicador de estado del panel.
3. Ejecutar el analizador y las pruebas de la aplicación en el equipo del autor.
4. Confirmar en el repositorio los archivos nuevos: el tablero, el entregable E1 y las figuras generadas.

---

# Tercera parte — miércoles 16: despliegue del servicio

## 23. Publicación del servicio en la plataforma

El servicio quedó desplegado en **Render**, en su capa gratuita, con la definición declarada en el repositorio (`render.yaml`) y creado a partir del repositorio de GitHub.

| Elemento | Valor |
|---|---|
| Nombre del servicio | `sigvach-api` |
| Repositorio y rama | `saintssud-sud/Proyecto---Diplomado` · `main` |
| Directorio raíz | `backend` |
| Construcción | `pip install -r requirements.txt` |
| Arranque | `uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips="*"` |
| Comprobación de salud | `/api/v1/salud` |
| Tipo de instancia | Gratuita |
| Variables de entorno | `ENTORNO`, `FIREBASE_PROJECT_ID`, `ALLOWED_ORIGINS`, `DEVICE_API_KEY` y `FIREBASE_SERVICE_ACCOUNT_JSON` |
| Despliegue automático | Al confirmar cambios en el repositorio |

**Decisiones tomadas durante la publicación.**

- Se eligió el nombre `sigvach-api` para que la dirección pública sea legible y citable en la monografía.
- El **directorio raíz** se fijó en `backend` porque el servicio y sus dependencias viven en esa carpeta: sin esa indicación la construcción falla.
- El **comando de arranque** obliga a escuchar en `0.0.0.0` y en el puerto que asigna la plataforma (`$PORT`), y a confiar en las cabeceras del proxy (`--proxy-headers`), condición para funcionar detrás del terminador TLS de la plataforma.
- Los secretos se declararon como **variables de entorno** en el panel y no como archivos: la clave de la cuenta de servicio se cargó en una sola línea JSON (2330 caracteres) y la clave del módulo de adquisición con su valor vigente.
- Se concedió a la plataforma acceso **solo al repositorio del proyecto**, según el criterio de mínimo privilegio.

**Hallazgo de seguridad.** Al revisar la configuración se detectó que el archivo de entorno local conservaba el **valor de ejemplo** de la clave del módulo de adquisición (`cambiar-por-una-cadena-aleatoria-larga`), que está publicado en la plantilla del repositorio: cualquier persona que accediera al repositorio podía enviar lecturas al servicio. Se generó una clave aleatoria de 64 caracteres con `secrets.token_urlsafe`, se actualizó el archivo de entorno local y la configuración del despliegue, y se conservó un respaldo del archivo anterior. La comprobación inicial no lo detectó porque solo medía la longitud del valor, que coincidía con la de una clave real.

**Hallazgo de disponibilidad.** La plataforma advierte que, en su capa gratuita, la instancia se suspende por inactividad y que la primera petición posterior puede demorar **cincuenta segundos o más**. El requisito RNF-05 declaraba treinta segundos, de modo que se corrigió a **sesenta segundos** —en la monografía y en el entregable E1— y el tiempo máximo de espera del cliente se elevó de 45 a **60 segundos**, para que esa primera petición no se interprete como un fallo de conexión.

**Archivos de apoyo generados.** Se prepararon dos utilidades reproducibles: una que convierte la clave de la cuenta de servicio en una sola línea y comprueba que sirve para autenticar, y otra que reúne las cinco variables de entorno en un archivo para cargarlas de una vez en la plataforma. Ese archivo contiene secretos, se guardó **fuera del repositorio** y se elimina una vez cargado.

**Pendiente de esta fase.** Publicar la aplicación web en Firebase Hosting con la dirección del servicio, cerrar los orígenes permitidos (CORS) con la dirección pública de la aplicación, publicar las reglas de seguridad de Firestore y generar el archivo instalable de Android. Se recomienda además **rotar la clave de la cuenta de servicio**, porque una captura de pantalla mostró su encabezado durante la configuración.

---

## 24. Jueves 17: publicación de la aplicación web y cierre de la seguridad

**Publicación de la aplicación web.** Se compiló la aplicación apuntando al servicio publicado y se publicó en Firebase Hosting, con el agregado de una opción al panel de control que realiza los dos pasos —compilar y publicar— sin escribir comandos. La aplicación quedó accesible en `https://sigvach26-bd.web.app` y consume el servicio de la nube, de modo que el sistema completo funciona sin depender del equipo del autor. Los orígenes permitidos quedaron verificados sin intervención adicional: si la aplicación publicada lee datos del servicio, el navegador no está bloqueando las peticiones.

**Hallazgo: el servicio buscaba la base de datos en otro proyecto.** La comprobación de salud del servicio desplegado informaba `degradado` con la base como no disponible, mientras que el servicio local conectaba sin inconvenientes con las **mismas** credenciales. El registro del servicio permitió identificar la causa con precisión: la consulta se dirigía al proyecto `production` en lugar de `sigvach26-bd`, y Google respondía `403 Cloud Firestore API has not been used in project production`. Corregida la variable de configuración del proyecto, la comprobación de salud pasó a informar `ok` con la base conectada.

> Este caso dejó dos enseñanzas que se incorporaron al sistema. La primera es de **diagnóstico**: el repositorio de Firestore atrapaba cualquier fallo y devolvía «no disponible» sin dejar constancia de la causa, de modo que una credencial ausente, un proyecto equivocado y un problema de permisos producían el mismo síntoma. Ahora la excepción se registra con su tipo y su mensaje, y al arrancar se informa el proyecto y la cuenta de servicio con los que quedó vinculado el SDK. La segunda es de **método**: comparar el comportamiento local con el desplegado permitió descartar en un paso las credenciales —que funcionaban— y concentrar la búsqueda en la configuración del entorno.

**Hallazgo de interfaz: el estado vacío no ofrecía salida.** Al probar la aplicación publicada, el panel mostró el estado vacío del módulo recién creado —que todavía no tiene lecturas— y, en ese estado, no presentaba el selector de módulo ni la acción de registrar una medición: el usuario quedaba viendo un aviso sin forma de llegar al módulo que sí tiene datos. Se corrigió el componente de estados para que admita un contenido propio del estado vacío, y el panel ahora ofrece allí el encabezado con el selector de módulo y la acción de actualizar.

**Hallazgo de interfaz: el módulo nuevo no aparecía en el panel.** Al registrar un módulo desde la pantalla de módulos, la lista del panel de inicio no se actualizaba: cada controlador conserva la suya, de modo que el módulo recién creado solo aparecía en el selector del panel después de reiniciar la aplicación. Se incorporó un aviso al panel después de cada operación sobre módulos —registrar, modificar y eliminar—, conservando el módulo vigente cuando sigue existiendo.

**Hallazgo de interfaz: la pantalla de rangos no dejaba elegir el cultivo.** Los rangos de referencia pertenecen a un cultivo, pero la pantalla los listaba todos juntos. Como solo el cultivo predefinido tenía rangos cargados, la pantalla parecía indicar que el sistema admitía un único cultivo, y no había forma de ver —ni de advertir— que un cultivo recién creado no tiene rangos: sus lecturas no se evalúan y no generan alertas, que es justamente lo que el usuario observaba sin explicación. Se incorporó el **selector de cultivo**, el filtro de la lista por cultivo y un aviso que indica, para el cultivo sin rangos, dónde se definen.

**Hallazgo de coherencia: alertas e historial no estaban acotados al módulo.** El panel y la pantalla de variables trabajan sobre el módulo vigente, pero las pantallas de alertas y de historial consultaban el servicio sin filtrar por módulo, de modo que mezclaban datos de módulos con cultivos y rangos distintos —y el resumen del periodo no correspondía a ningún módulo en particular—. Se acotaron ambas consultas al módulo vigente, se rehacen si el usuario cambia de módulo, y las cuatro pantallas muestran ahora el mismo detalle del módulo mediante un componente compartido.

**Hallazgo de interfaz: un módulo nuevo no podía recibir su primera medición.** El razonamiento del autor durante la prueba fue el que permitió encontrarlo: si un módulo recién creado no tiene lecturas, el panel muestra su estado vacío; y la acción de registrar una medición existía **únicamente** en el estado con datos. El resultado era que un módulo nuevo no podía poblarse nunca desde la aplicación: quedaba vacío de forma permanente y daba la impresión de que crear módulos no aportaba nada. El estado vacío ofrece ahora la acción de registrar la primera medición, además del selector de módulo y la recarga.

> Los tres hallazgos anteriores provienen de **usar la aplicación publicada**, no de revisar el código: crear un módulo, verlo en el panel y registrar sus mediciones son las operaciones que un usuario real hace en los primeros minutos. Quedan como ejemplo de por qué la prueba en el entorno desplegado —y no solo en el equipo de desarrollo— forma parte del trabajo de construcción.

**Reglas de seguridad publicadas y verificadas.** Antes de publicarlas se verificó que ningún componente del cliente acceda a las colecciones del dominio: la aplicación solo lee y escribe la colección `usuarios` —el perfil propio y, para el administrador, el resto— y todo el dominio pasa por el servicio. Se comprobó además que el correo del administrador declarado en las reglas coincide con el que asigna la aplicación (`admin@sigvach.com`) y que las colecciones heredadas del proyecto del aula (`registros` y `firestore_demo`) corresponden a código sin uso, de modo que cerrarlas no afecta ninguna pantalla. Publicadas las reglas, se verificó su efecto **contra la base de datos real**: consultando la API REST sin credenciales, las cinco colecciones del dominio responden `403`, y con la cuenta de servicio responden `200`. La comprobación quedó implementada como programa (`scripts/verificar_acceso_directo.py`) para poder repetirla tras cualquier cambio, y documentada en `docs/12_VERIFICACION_SEGURIDAD.md`.

**Estado del despliegue.** Servicio en la nube (`Live`), documentación de la API publicada, aplicación web publicada, reglas de seguridad publicadas y comprobación de salud en `ok` con la base conectada. Queda pendiente generar el archivo instalable de Android y reunir las evidencias de los ocho requisitos mínimos.

---

*Bitácora de trabajo del Módulo 4. Elaborada al cierre de las sesiones del lunes 14, del martes 15, del miércoles 16 y del jueves 17 de septiembre de 2026.*
