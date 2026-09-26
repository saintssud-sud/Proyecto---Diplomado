# Diccionario de conceptos — SI.G.VA.CH.

**Sistema de Gestión de Variables para Cultivos Hidropónicos**
Módulo 4 · Grupo 3 · Diplomado en Desarrollo Web y Aplicaciones Móviles · UAJMS

> **Cómo usar este diccionario.** Cada término trae una definición en lenguaje
> sencillo y, debajo, qué significa **en este proyecto**. La segunda parte es la
> importante para la defensa: no alcanza con definir la palabra, hay que poder
> decir **dónde se usa en tu sistema**.

---

# 1. Dominio: hidroponía y cultivo

**Hidroponía** — Cultivo de plantas sin suelo, con las raíces en una solución
nutritiva.
*En el proyecto:* es el contexto del sistema; todo lo que se mide pertenece a un
cultivo hidropónico.

**Solución nutritiva** — Agua con los nutrientes disueltos que alimentan a la
planta.
*En el proyecto:* es lo que se controla a través del pH, la conductividad y la
temperatura de la solución.

**NFT (Nutrient Film Technique)** — Técnica en la que la solución circula en una
película delgada por canales donde están las raíces.
*En el proyecto:* se nombra como antecedente del seguimiento previo del cultivo.

**Raíz flotante** — Técnica en la que las plantas flotan sobre la solución, sin
sustrato.
*En el proyecto:* la otra técnica comparada en el antecedente citado.

**Variable fisicoquímica** — Magnitud que describe el estado químico de la
solución.
*En el proyecto:* pH, conductividad eléctrica y sólidos disueltos totales.

**Variable ambiental** — Magnitud que describe el entorno del cultivo.
*En el proyecto:* temperatura ambiental, humedad relativa y temperatura de la
solución.

**pH** — Medida de acidez o alcalinidad, de 0 a 14.
*En el proyecto:* una de las seis variables; fuera de rango impide que la planta
absorba nutrientes aunque estén presentes.

**Conductividad eléctrica (EC)** — Capacidad de la solución de conducir
electricidad; indica la concentración de sales.
*En el proyecto:* variable medida en mS/cm; su exceso quema las raíces por
salinidad.

**Sólidos disueltos totales (TDS)** — Cantidad de sales disueltas, en partes por
millón (ppm).
*En el proyecto:* variable medida en ppm; se relaciona con la conductividad.

**Humedad relativa** — Porcentaje de vapor de agua en el aire respecto del máximo
que admitiría a esa temperatura.
*En el proyecto:* variable medida en %; su exceso favorece enfermedades fúngicas.

**Rango de referencia** — Valores mínimo y máximo entre los que una variable se
considera adecuada para un cultivo.
*En el proyecto:* es el corazón del sistema: cada lectura se evalúa contra el
rango del cultivo del módulo.

**Cultivo (especie)** — La planta que se siembra: lechuga, acelga, apio.
*En el proyecto:* define **qué rangos** se aplican; se administra en el catálogo
de cultivos.

**Módulo de cultivo** — La **instalación física** donde están los sensores.
*En el proyecto:* es la unidad de trabajo; tiene un cultivo asociado y una
ubicación. **No confundir con "cultivo"**: el módulo es el lugar, el cultivo es la
especie.

**Perfil de cultivo** — El conjunto de rangos de referencia de una especie.
*En el proyecto:* es el nombre técnico de "cultivo" en la base de datos; por eso
al cultivo se le asocian sus rangos.

**Lectura o medición** — Un valor registrado de una variable, en un momento dado.
*En el proyecto:* puede ser **automática** (la envía el ESP32) o **manual** (la
registra una persona con instrumentos portátiles).

**Alerta** — Aviso que genera el sistema cuando una lectura sale de su rango.
*En el proyecto:* la genera el **servidor**, no la aplicación; guarda referencia a
la lectura que la originó.

**Estado de una variable** — Clasificación de una lectura: normal, bajo, alto o
sin rango.
*En el proyecto:* lo calcula el servidor comparando la lectura con el rango.

**Trazabilidad** — Poder reconstruir el camino de un dato: quién, cuándo, con qué
y de dónde.
*En el proyecto:* cada lectura guarda su origen, su autor o dispositivo y su marca
de tiempo.

---

# 2. Arquitectura de software

**Arquitectura** — La forma en que se organiza un sistema: qué partes tiene y cómo
se comunican.
*En el proyecto:* cuatro niveles: adquisición, servicio, datos y presentación.

**Monolito** — Sistema construido y desplegado como **una sola unidad**.
*En el proyecto:* el servicio es un monolito: un programa, un proceso, una
dirección pública.

**Monolito modular** — Monolito organizado internamente en **módulos con
responsabilidad separada**.
*En el proyecto:* **es tu patrón**: una unidad desplegable, con módulos internos
(rutas, servicios, repositorios, esquemas).

**Microservicios** — Arquitectura en la que el sistema se divide en servicios
independientes que se comunican por la red.
*En el proyecto:* se evaluó y **se descartó**, por el costo operativo frente al
alcance del prototipo.

**Arquitectura en capas (N-Tier)** — Organización del código en niveles:
presentación, lógica de negocio y datos.
*En el proyecto:* tus carpetas lo reflejan: `rutas/` (presentación),
`servicios/` (lógica), `repositorios/` (datos).

**Cliente-servidor** — Modelo en el que un cliente pide y un servidor responde.
*En el proyecto:* la app Flutter es el cliente; el servicio FastAPI es el servidor.

**API (Interfaz de Programación de Aplicaciones)** — El conjunto de operaciones que
un servicio ofrece a otros programas.
*En el proyecto:* tu API tiene **32 operaciones**, todas bajo `/api/v1`.

**REST** — Estilo de API que usa direcciones (URL) y verbos HTTP (GET, POST,
PATCH, DELETE).
*En el proyecto:* es el estilo de tu contrato.

**Endpoint (punto de acceso)** — Cada dirección concreta de la API.
*En el proyecto:* por ejemplo `GET /api/v1/lecturas` o `POST /api/v1/lecturas/manual`.

**Contrato de la API** — La descripción formal de qué operaciones existen, qué
reciben y qué devuelven.
*En el proyecto:* se genera **automáticamente** desde el código con **OpenAPI** y
se publica en `/docs`.

**OpenAPI / Swagger** — Estándar para describir una API, y la página que la
documenta de forma interactiva.
*En el proyecto:* `https://sigvach-api.onrender.com/docs` — desde ahí se pueden
ejecutar las operaciones.

**Versión de la API (`/api/v1`)** — Prefijo que indica que el contrato puede
cambiar sin romper a quien ya lo usa.
*En el proyecto:* cumple el RNF-07 (mantenibilidad).

**Esquema (schema)** — La definición de los campos que un dato debe tener y de sus
tipos.
*En el proyecto:* `esquemas.py` valida todo lo que entra al servicio.

**DTO (objeto de transferencia de datos)** — Objeto que solo sirve para transportar
datos entre capas.
*En el proyecto:* los esquemas de entrada y salida de la API.

**Patrón repositorio** — Separar el acceso a los datos detrás de una interfaz, para
que la lógica no dependa del motor de base de datos.
*En el proyecto:* tienes **dos implementaciones**: una en memoria (pruebas) y otra
sobre Firestore (producción).

**Controlador** — Componente que recibe la acción del usuario y coordina la
respuesta.
*En el proyecto:* los `controllers/` de Flutter (panel, historial, alertas…).

**Inyección de dependencias** — Entregar a un componente lo que necesita desde
afuera, en lugar de que lo construya él.
*En el proyecto:* `Provider` en Flutter; `Depends` en FastAPI.

**Estado de la vista** — Las cuatro situaciones posibles de una pantalla que
consume datos: cargando, con datos, vacía y con error.
*En el proyecto:* es un criterio de diseño explícito, aplicado en todas las
pantallas.

**Validación en el cliente y en el servidor** — Comprobar los datos en los dos
lados.
*En el proyecto:* el cliente evita enviar datos incompletos; el servidor **siempre**
valida (doble barrera).

**Separación de responsabilidades** — Cada componente debe hacer una sola cosa.
*En el proyecto:* el cliente no evalúa rangos ni autoriza: eso es del servidor.

---

# 3. Servicio (backend) y seguridad

**Backend** — La parte del sistema que corre en el servidor.
*En el proyecto:* el servicio en Python con FastAPI.

**FastAPI** — Marco de trabajo de Python para construir APIs.
*En el proyecto:* es el marco del servicio.

**Uvicorn** — Servidor que ejecuta la aplicación FastAPI.
*En el proyecto:* comando de arranque: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

**Pydantic** — Biblioteca que valida y convierte los datos según un esquema.
*En el proyecto:* si un dato no cumple, el servicio responde **422**.

**Código HTTP 422** — "Entidad no procesable": los datos llegaron pero son
inválidos.
*En el proyecto:* es la respuesta ante un valor de tipo incorrecto o fuera de los
límites físicos.

**Autenticación** — Verificar **quién** es el usuario.
*En el proyecto:* se delega en Firebase Authentication (correo y contraseña).

**Autorización** — Verificar **qué puede hacer** ese usuario.
*En el proyecto:* se resuelve en el servidor según el rol, en cada operación.

**Token de identidad** — Comprobante firmado que el proveedor emite al iniciar
sesión.
*En el proyecto:* la app lo adjunta en la cabecera `Authorization` de cada petición.

**JWT (JSON Web Token)** — Formato habitual de esos tokens.
*En el proyecto:* lo emite Firebase; el servicio lo valida antes de atender.

**Rol** — Perfil de permisos de un usuario.
*En el proyecto:* **Administrador** (configura) y **Operador** (opera el cultivo).

**Nivel de autorización** — Grado de permiso que exige una operación.
*En el proyecto:* tres niveles: consulta, operación y administración.

**Escalada de privilegios** — Cuando alguien consigue permisos que no le
corresponden.
*En el proyecto:* está bloqueada: un usuario no puede cambiarse el rol a sí mismo.

**Mínimo privilegio** — Dar a cada componente solo los permisos que necesita.
*En el proyecto:* la aplicación de Render accede **solo** al repositorio del proyecto.

**HTTPS / TLS** — Protocolo que cifra la comunicación por internet.
*En el proyecto:* todas las comunicaciones van cifradas.

**CORS (intercambio de recursos de origen cruzado)** — Regla del navegador que
controla qué páginas pueden llamar a un servicio.
*En el proyecto:* `ALLOWED_ORIGINS` permite solo la dirección de tu aplicación web.

**Origen permitido** — La dirección web autorizada a consumir la API.
*En el proyecto:* `https://sigvach26-bd.web.app`.

**Clave de dispositivo (`X-Device-Key`)** — Clave propia del hardware, distinta de
las credenciales de las personas.
*En el proyecto:* autentica al ESP32; se rota sin afectar a los usuarios.

**Hash** — Transformación irreversible de un dato (se usa para contraseñas).
*En el proyecto:* las contraseñas no se guardan: las administra el proveedor de
identidad.

**Rotación de claves** — Reemplazar una clave por otra, dejando la anterior
inservible.
*En el proyecto:* se hizo con la clave del dispositivo, que conservaba el valor de
ejemplo publicado.

**Cuenta de servicio** — Identidad técnica que usa un programa para acceder a
servicios en la nube.
*En el proyecto:* es la única que habla con la base de datos.

---

# 4. Base de datos

**Base de datos documental** — Base que guarda **documentos** de estructura
flexible, no tablas con filas y columnas.
*En el proyecto:* Cloud Firestore. **Por eso no es entidad-relación.**

**Cloud Firestore** — Base de datos documental de Firebase (Google).
*En el proyecto:* guarda módulos, cultivos, rangos, lecturas, alertas y usuarios.

**Colección** — Agrupa documentos del mismo tipo (equivale a una "tabla", pero sin
estructura fija).
*En el proyecto:* seis colecciones: `modulos_cultivo`, `perfiles_cultivo`,
`rangos`, `lecturas`, `alertas`, `usuarios`.

**Documento** — Cada registro dentro de una colección (equivale a una "fila").
*En el proyecto:* una lectura, un módulo o un usuario son documentos.

**Campo** — Cada dato dentro de un documento (equivale a una "columna").
*En el proyecto:* `variable`, `valor`, `unidad`, `timestamp`…

**Diccionario de datos** — Documento que describe cada campo: tipo, longitud,
obligatoriedad y reglas.
*En el proyecto:* es la Tabla 11 del entregable.

**Referencia entre colecciones** — Guardar el identificador de un documento de otra
colección.
*En el proyecto:* `perfil_id`, `modulo_id`, `lectura_id` — **es la forma en que una
base documental expresa una relación**.

**Índice** — Estructura que acelera las consultas.
*En el proyecto:* se declararon **5 índices compuestos**; sin ellos las consultas
fallan con error.

**Índice compuesto** — Índice sobre varios campos a la vez.
*En el proyecto:* las consultas que filtran por módulo, variable y fecha lo
necesitan.

**Reglas de seguridad** — Reglas que deciden quién puede leer o escribir en la base
desde un cliente.
*En el proyecto:* cierran **todas** las colecciones al cliente; solo el servicio
accede con su cuenta de servicio.

**Persistencia** — Que los datos sobrevivan al cierre del programa.
*En el proyecto:* los datos viven en la nube, no en el teléfono.

**Repositorio en memoria** — Implementación que guarda los datos en la memoria del
programa (se pierden al cerrarlo).
*En el proyecto:* se usa para las pruebas y para la demostración sin conexión.

---

# 5. Aplicación (frontend y móvil)

**Frontend** — La parte del sistema que ve y usa la persona.
*En el proyecto:* la aplicación Flutter (web y Android).

**Flutter** — Marco de trabajo de Google para construir aplicaciones para varias
plataformas con un solo código.
*En el proyecto:* la misma base de código genera la app web y el APK de Android.

**Dart** — Lenguaje de programación que usa Flutter.
*En el proyecto:* es el lenguaje de la aplicación.

**Widget** — Cada elemento de la interfaz en Flutter (botón, tarjeta, fila…).
*En el proyecto:* todo lo que se ve es un widget; los reutilizas (tarjeta de módulo,
tarjeta de variable).

**Provider** — Biblioteca de Flutter para compartir el estado entre pantallas.
*En el proyecto:* los controladores se comparten así.

**Controlador (`ChangeNotifier`)** — Objeto que guarda el estado y avisa cuando
cambia.
*En el proyecto:* `PanelController`, `HistorialController`, `AlertasController`…

**Estado** — La información que la pantalla muestra en un momento dado.
*En el proyecto:* el panel guarda el módulo vigente, las variables y las alertas.

**Diseño adaptable (responsive)** — Que la interfaz se reorganice según el tamaño
de la pantalla.
*En el proyecto:* RNF-06: sin desplazamiento horizontal entre 320 y 1920 píxeles.

**Compilación (build)** — Traducir el código a algo que la máquina pueda ejecutar.
*En el proyecto:* `flutter build web` y `flutter build apk`.

**APK** — Archivo instalable de una aplicación Android.
*En el proyecto:* 53,8 MB, se instala directamente en el teléfono.

**Sistema operativo mínimo (minSdk)** — Versión mínima de Android que la app
admite.
*En el proyecto:* Android 8.0 (API 26), declarado explícitamente (RNF-04).

**Servicio web (service worker)** — Mecanismo del navegador que guarda la
aplicación para que cargue rápido.
*En el proyecto:* explica por qué a veces se ve la versión anterior hasta recargar
con `Ctrl + Shift + R`.

**Caché** — Copia temporal de datos para no volver a pedirlos.
*En el proyecto:* el navegador guarda la app; por eso conviene probar en ventana
privada.

---

# 6. Hardware y adquisición

**ESP32** — Microcontrolador con conexión WiFi.
*En el proyecto:* es el **módulo de adquisición**: lee los sensores y envía las
lecturas al servicio.

**Sensor** — Dispositivo que mide una magnitud física.
*En el proyecto:* pH, conductividad, temperatura y humedad.

**Actuador** — Dispositivo que **modifica** el entorno (bomba, válvula, ventilador).
*En el proyecto:* quedó **fuera de alcance** el control automático de actuadores.

**Calibración** — Ajustar un instrumento para que mida correctamente.
*En el proyecto:* es una tarea previa al uso de los instrumentos portátiles.

**Instrumento portátil** — Medidor manual (de pH, de conductividad).
*En el proyecto:* se usa en el **registro manual** de mediciones.

**Lectura automática / manual** — Según quién la registra: el dispositivo o una
persona.
*En el proyecto:* el servidor fija ese origen; el cliente no puede declararlo.

**Internet de las Cosas (IoT)** — Objetos conectados a internet que envían datos.
*En el proyecto:* el ESP32 es el componente IoT.

---

# 7. Despliegue e infraestructura

**Despliegue (deploy)** — Poner el sistema a funcionar en un servidor accesible.
*En el proyecto:* servicio en Render + aplicación web en Firebase Hosting.

**Servidor / hosting** — Computadora o servicio que mantiene el sistema disponible.
*En el proyecto:* Render para el servicio; Firebase Hosting para la web.

**Plataforma como servicio (PaaS)** — Servicio que ejecuta tu aplicación sin que
administres el servidor.
*En el proyecto:* Render cumple ese papel.

**Variable de entorno** — Valor de configuración que se lee desde el entorno, no
desde el código.
*En el proyecto:* ahí van los secretos y configuración (entorno, orígenes, claves).

**Secreto** — Dato que no debe publicarse (clave privada, contraseña).
*En el proyecto:* van en variables de entorno, **nunca** en el repositorio.

**Capa gratuita (free tier)** — Plan sin costo con limitaciones.
*En el proyecto:* el servicio se suspende por inactividad (de ahí los 50 segundos).

**Suspensión por inactividad (cold start)** — El servicio se apaga solo y tarda en
responder la primera vez que se lo vuelve a llamar.
*En el proyecto:* la primera petición del día puede tardar hasta **50-60 segundos**;
por eso el RNF-05 los admite.

**Comprobación de salud (health check)** — Dirección que la plataforma consulta para
saber si el servicio está vivo.
*En el proyecto:* `/api/v1/salud` — responde `ok` o `degradado`.

**Repositorio** — Lugar donde se guarda el código y su historia.
*En el proyecto:* GitHub.

**Git** — Sistema de control de versiones.
*En el proyecto:* registra cada cambio del código y de la documentación.

**Confirmación (commit)** — Cada cambio registrado en el historial.
*En el proyecto:* 80+ confirmaciones con mensajes descriptivos.

**Rama (branch)** — Línea de desarrollo independiente.
*En el proyecto:* se trabaja en `main`.

**Subir (push) / traer (pull)** — Enviar tus confirmaciones al repositorio remoto o
traer las ajenas.
*En el proyecto:* el panel sincroniza con GitHub; el servicio se actualiza solo al
subir.

**Historial de avance progresivo** — Que el repositorio muestre el trabajo repartido
en el tiempo, con mensajes claros.
*En el proyecto:* es el **requisito mínimo 5**: 123 confirmaciones en 13 fechas.

**Despliegue automático** — Que al subir cambios, la plataforma publique sola.
*En el proyecto:* está activado en Render ("On Commit").

---

# 8. Requisitos, metodología y documentación

**Requisito** — Necesidad que el sistema debe satisfacer.
*En el proyecto:* 13 funcionales (RF) y 8 no funcionales (RNF).

**Requisito funcional (RF)** — **Qué hace** el sistema.
*En el proyecto:* RF-05 "registrar lecturas del módulo de adquisición".

**Requisito no funcional (RNF)** — **Cómo** lo hace: calidad, seguridad,
rendimiento.
*En el proyecto:* RNF-05 disponibilidad, RNF-02 seguridad, RNF-03 usabilidad…

**Criterio de aceptación** — Condición concreta que permite decir si el requisito
se cumplió.
*En el proyecto:* cada RF tiene el suyo en la tabla de requisitos.

**Métrica de verificación** — Cómo se mide el cumplimiento de un RNF.
*En el proyecto:* "invocación del endpoint de salud tras quince minutos sin uso".

**Alcance** — Lo que el proyecto **sí** incluye (y lo que deja fuera).
*En el proyecto:* un módulo piloto, 6 variables, 2 roles; **sin** control de
actuadores.

**MoSCoW** — Técnica para priorizar requisitos: **M**ust (debe), **S**hould
(debería), **C**ould (podría), **W**on't (no se hará ahora).
*En el proyecto:* se usó para decidir qué quedaba dentro del alcance.

**Caso de uso** — Descripción de una interacción entre un actor y el sistema.
*En el proyecto:* 10 casos de uso (CU-01 a CU-10), dibujados en el diagrama.

**Actor** — Quien interactúa con el sistema (persona o dispositivo).
*En el proyecto:* Administrador, Operador y el Módulo de adquisición (actor no
humano).

**Sprint** — Período corto de trabajo con un objetivo concreto.
*En el proyecto:* 4 sprints semanales, uno por entrega.

**Tablero Kanban** — Tablero con columnas (por hacer, en curso, hecho) para ver el
avance.
*En el proyecto:* está versionado en `docs/TABLERO.md`.

**Bitácora** — Registro del trabajo hecho, con los problemas y sus soluciones.
*En el proyecto:* 26 secciones que documentan cada jornada y cada hallazgo.

**Monografía** — El documento académico del proyecto.
*En el proyecto:* ~16 700 palabras, con formato institucional.

**Entregable (E1, E2, E3, E4)** — Cada producto parcial que se entrega.
*En el proyecto:* la **E1** (perfil del proyecto) ya fue enviada y calificada como
"enviado para calificar".

**Rúbrica** — Tabla con los criterios y puntajes con que se evalúa.
*En el proyecto:* es lo que guía qué hay que demostrar.

**Norma Harvard / ISO 690-2** — Normas para citar fuentes y hacer la bibliografía.
*En el proyecto:* es el formato exigido en la monografía.

**Anexo** — Documento que acompaña a la monografía con evidencia complementaria.
*En el proyecto:* el anexo de evidencias de los 8 requisitos mínimos.

**Patrón arquitectónico** — Solución general y probada para un problema de diseño.
*En el proyecto:* monolito modular con organización en capas.

---

# 9. Cifras clave (para responder con datos)

| Dato | Valor |
|---|---|
| Variables del sistema | **7** |
| Operaciones de la API | **28** |
| Requisitos funcionales | **13** |
| Requisitos no funcionales | **8** |
| Casos de uso | **10** |
| Colecciones en la base | **6** |
| Índices compuestos | **5** |
| Roles del alcance | **2** (Administrador y Operador) |
| Pruebas automáticas del servicio | **87** |
| Confirmaciones en el repositorio | **123** en **13 fechas** |
| Tamaño del archivo instalable | **53,8 MB** |
| Demora admitida al despertar el servicio | **60 s** (RNF-05) |
| Reducción del paquete de iconos | **99,4 %** |

---

## Tres frases para tener a mano

1. **"Nadie accede a la base de datos sin pasar por el servicio."** — Es la regla
   de diseño que explica la arquitectura y la seguridad al mismo tiempo.

2. **"El módulo es la instalación física; el cultivo es la especie con sus rangos."**
   — Es la distinción que ordena todo el modelo de datos.

3. **"El sistema evalúa cada lectura contra el rango del cultivo de su módulo, en el
   servidor."** — Es la frase que resume qué hace el sistema y dónde lo hace.

---

*Documento de estudio. Elaborado el 19 de septiembre de 2026.*
