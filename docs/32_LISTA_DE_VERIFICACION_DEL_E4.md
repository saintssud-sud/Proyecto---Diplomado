# Lista de verificación del E4 — contra la consigna y la plenaria P4

Documento interno de trabajo. No forma parte de la monografía.
Fuentes: la tarea `E4.docx` (consigna y lista previa al envío) y la plenaria
`P4_Pruebas_Despliegue_Defensa_Modulo4.pdf`. Estado al **5 de octubre de 2026**.

Leyenda: ✅ cumple · 🟡 a medias o por verificar · ❌ falta

---

## 1. Documento

| Requisito de la consigna | Estado | Qué falta |
|---|---|---|
| Preliminares, Capítulos 1, 2 (2.1 a 2.9) y 3, bibliografía y anexos | 🟡 el cuerpo está armado; **los anexos no están dentro del documento** | Incorporar los anexos A a F al documento del E4 |
| Lo observado en el E3, corregido | ✅ la Tabla 3 corregida, y el E3 corregido cargado en SharePoint | — |
| Formato institucional | 🟡 tipografía, interlineado y márgenes bien; **falta numeración romana y sobra papel A4** | Numeración romana hasta el Capítulo 1 y todo en carta |
| **De 30 a 40 páginas sin preliminares ni anexos** | ❌ **≈ 70 páginas** | Camino A: bajar a ≈ 45 y consultar al tutor el viernes |
| Resumen de 300 palabras como máximo | ✅ 290 palabras | — |
| Preliminares completos: portada, índices de **contenido, tablas, figuras y anexos** | 🟡 hay índice de contenido | Verificar y generar los índices de tablas, figuras y anexos |
| **Numeración romana hasta el Capítulo 1** | ❌ hoy todo en arábiga | Corregir |
| Una conclusión por objetivo específico, con grado de cumplimiento y evidencia | 🟡 el Capítulo 3 existe | Actualizar las evidencias con la tabla de pruebas real y llenar el marcador del ámbito del piloto |
| Manual de usuario, **organizado por tareas**, con capturas de producción y una sección por rol | ❌ el manual actual está organizado **por pantallas** | Reorganizar por tareas, capturar en producción con datos ficticios, agregar preguntas frecuentes y mensajes de error |
| Manual de instalación y despliegue | 🟡 existe | **Prueba de fuego: otra persona sigue el manual y el sistema levanta** |
| Anexos: repositorio, URL o APK, diagramas legibles | 🟡 repositorio sí; falta la dirección pública y el APK | Completar el anexo de dirección pública |
| Sin restos ni marcas de plantilla | 🟡 el E3 no tiene marcadores; el Capítulo 3 traído del borrador tiene uno | Llenar el marcador y volver a verificar con `python _diagnostico/marcadores_del_documento.py` |

**Nota de la plenaria:** un objetivo cumplido a medias se declara así. El ejemplo que da es
«Parcial: 22 de 24 casos aprobados; CP-11 y CP-17 siguen abiertos y pasan a recomendaciones».
El tribunal valora la precisión, no el optimismo.

---

## 2. Sistema y despliegue verificado

| Requisito | Estado | Qué falta |
|---|---|---|
| El sistema funciona hoy en producción, con un usuario de prueba por rol | 🟡 funciona; falta la verificación formal | Probar desde **otro dispositivo, en incógnito**, con las dos cuentas |
| Los ocho requisitos mínimos del punto 4 de los Lineamientos | 🟡 verificados en la auditoría del 14/09 | Pasada de verificación contra el sistema en vivo, uno por uno |
| **Monitoreo de disponibilidad activo** sobre `/api/v1/salud` | 🟡 **el 5/10 quedó creado el flujo `monitoreo.yml`**, que consulta cada 15 minutos desde los servidores de GitHub y falla si el servicio o la base de datos no responden; el historial de ejecuciones del repositorio es la página de estado pública | Sumar el servicio dedicado (UptimeRobot o Better Stack) con su enlace en 2.9 |
| Errores registrados: cada 500 con ruta, hora y traza, sin datos sensibles | ❌ sin declarar | Configurar o declarar la limitación en 2.9 |
| Una línea de registro por petición: método, ruta, código y duración | ❌ por verificar | Verificar en el backend y documentarlo |
| Tiempos de respuesta medidos en producción | ❌ pendiente (CP-24) | Medir **antes y después** de la corrección, con el número |
| Respaldo de la base con **una restauración probada** | ❌ pendiente | Exportar, restaurar en un entorno de prueba y dejar la constancia |
| Límites del plan declarados en 2.9 | ✅ escritos | — |
| Pipeline de integración y despliegue | ✅ GitHub Actions con dos trabajos | Verificar el historial de ejecuciones y citarlo en 2.9 |

---

## 3. Entrega

| Requisito | Estado | Qué falta |
|---|---|---|
| Documento **en PDF** con el nombre `Apellido_Nombre_E4.pdf` | ❌ | Exportar como `Santos_Freddy_E4.pdf`, con los manuales dentro como anexos |
| APK firmado o enlace, si el sistema es móvil | 🟡 | Decidir si se entrega el APK o se declara la web |
| Datos en el campo de texto de la entrega | ❌ | Preparar las seis líneas: frontend, ruta de salud, repositorio, dos usuarios de prueba, monitoreo |
| Sin credenciales de la base, claves de servicio ni contenido del `.env` | ✅ verificado en el repositorio | — |
| Cuestionario Q4 | ❌ | Es actividad aparte, vale el 5 % y **no admite atraso** |

Las seis líneas del campo de texto, tal como las pide la consigna:

```
Frontend (URL pública o enlace al APK): https://...
API (ruta de salud): https://.../api/v1/salud
Repositorio: https://...
Usuario de prueba · rol 1: correo / contraseña (datos ficticios)
Usuario de prueba · rol 2: correo / contraseña (datos ficticios)
Monitoreo: servicio usado y enlace a la página de estado, si es pública
```

---

## 4. Defensa técnica (T5, martes 13 a las 17:00)

**Doce minutos por persona: siete de demostración y cinco de preguntas, con cronómetro.** La
demostración se corta a los siete minutos, esté donde esté, y se ensaya en la tutoría del viernes.

| Momento | Tiempo | Qué se muestra |
|---|---|---|
| Problema y usuario | 0:00 – 1:00 | Quién usa el sistema, qué hacía antes y qué dato lo prueba |
| Flujo Must en producción | 1:00 – 4:30 | Login con el usuario de prueba y el flujo completo, en la URL pública |
| Seguridad en vivo | 4:30 – 5:30 | Un rol intenta lo que no le corresponde y la API responde 403 |
| Evidencia | 5:30 – 7:00 | Tabla de pruebas, repositorio con historial y monitoreo en línea |
| Preguntas | 7:00 – 12:00 | Sobre el código, el esquema y las decisiones, con el sistema abierto |

### Rúbrica — 100 puntos, vale el 20 % de la nota del módulo

| Criterio | Puntos | Qué se exige |
|---|---|---|
| Sistema en producción | 25 | El flujo Must completo funciona en la URL pública con el usuario de prueba |
| **Dominio técnico** | **30** | Explica y ubica en el repositorio el código, el esquema y sus decisiones, **y hace un cambio simple si se le pide** |
| Seguridad demostrada | 15 | Muestra en vivo el 401 y el 403, y explica dónde se hace cumplir el rol |
| Pruebas y evidencia | 10 | Muestra la tabla de pruebas y **ejecuta al menos una prueba automatizada** |
| Respuesta a preguntas | 15 | Responde con precisión, reconoce lo que falta y lo sostiene con el sistema abierto |
| Tiempo y claridad | 5 | Demostración dentro de los siete minutos, en el orden del protocolo |

> **Regla de la defensa: quien no ejecuta ni explica su sistema, no aprueba.** La falta de dominio
> técnico anula el componente, con independencia de quién haya escrito el código. Usar asistentes
> está permitido; no entender lo entregado, no.

### Las ocho preguntas, para preparar con el sistema abierto

| # | Pregunta | Respuesta nuestra |
|---|---|---|
| 1 | ¿Dónde se verifica el rol? | En el backend, con la dependencia de autorización por rol; se muestra la ruta del código y el 403 en vivo |
| 2 | ¿Qué pasa si el token vence? | La API responde 401 y el cliente muestra el mensaje y pide volver a entrar |
| 3 | ¿Cómo guarda las contraseñas? | No las guarda: las administra el proveedor de identidad; el sistema no almacena contraseñas |
| 4 | ¿Dónde están los secretos? | En variables de entorno de la plataforma; se muestra el `.env.example` con los nombres, nunca los valores |
| 5 | ¿Por qué este stack? | Cada tecnología contra el requisito que atiende, por su identificador |
| 6 | ¿Cómo sabe que funciona? | Una fila de la tabla de pruebas con su evidencia |
| 7 | ¿Qué pasa si se cae? | Monitoreo de disponibilidad, respaldo de la base y el procedimiento de redespliegue |
| 8 | ¿Qué quedó pendiente? | Lo declarado como fuera de alcance y las recomendaciones, sin esconderlo |

### El día de la defensa

- [ ] Sistema abierto **30 minutos antes**: la capa gratuita despierta y la base no está pausada.
- [ ] Un usuario de prueba por rol (hacen falta dos cuentas para mostrar el 403).
- [ ] Pantalla compartida, audio y cámara probados antes del turno.
- [ ] Una prueba automatizada lista, **con el comando ya escrito en la terminal**.
- [ ] Repositorio y documento abiertos, en el esquema, el contrato y la tabla de pruebas.
- [ ] Cronómetro propio, con los siete minutos ya ensayados.

---

## 5. Lo que hay que sumar al plan de la semana

Estos puntos **no estaban** en el plan y salen de la lectura de la consigna y de la plenaria:

1. **Monitoreo con un servicio externo.** **Hecho el 5/10**: el flujo `monitoreo.yml` consulta la ruta
   de salud cada 15 minutos desde los servidores de GitHub, y su historial de ejecuciones queda como
   página de estado pública. Falta sumar el servicio dedicado, que además avisa por correo, con su
   enlace declarado en 2.9. Dos vías: si una falla, la otra queda.
2. **Respaldo de la base con una restauración probada.** No alcanza con tener copia.
3. **Prueba de fuego del manual de instalación**, hecha por otra persona.
4. **Reorganizar el manual de usuario por tareas**, no por pantallas, y capturarlo en producción.
5. **Índices de tablas, figuras y anexos** en los preliminares.
6. **Verificar que haya una línea de registro por petición** (o declararlo como limitación).
7. **Preparar las seis líneas del campo de texto** de la entrega.
8. **Practicar el cambio en vivo** de código y la ejecución de una prueba automatizada, porque la
   rúbrica le da 30 puntos al dominio técnico y la regla de la defensa es explícita.
