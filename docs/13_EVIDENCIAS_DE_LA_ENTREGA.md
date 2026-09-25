# Evidencias de los requisitos mínimos de la entrega

**Proyecto:** SIGVACH — Sistema de Gestión de Variables para Cultivos Hidropónicos
**Módulo 4** · Grupo 3 · Diplomado en Desarrollo Web y Aplicaciones Móviles
**Actualizado:** jueves 17 de septiembre de 2026

Este documento reúne, para cada requisito mínimo de la entrega, **dónde está la
evidencia** y **cómo se comprueba**. Las capturas de pantalla se adjuntan en el
anexo correspondiente; aquí se indica qué debe mostrar cada una.

---

## 1. El sistema está desplegado y es accesible mediante una dirección pública

| Elemento | Dirección |
|---|---|
| Aplicación web publicada | `https://sigvach26-bd.web.app` |
| Servicio publicado | `https://sigvach-api.onrender.com` |
| Documentación interactiva de la API | `https://sigvach-api.onrender.com/docs` |

**Cómo se comprueba**

1. Abrir la dirección de la aplicación web e iniciar sesión con una cuenta del sistema.
2. El panel debe mostrar las seis variables del módulo con sus valores, rangos y estados.
3. Abrir `https://sigvach-api.onrender.com/api/v1/salud`: debe responder
   `{"estado":"ok","version_api":"v1","entorno":"produccion","base_de_datos":"conectada"}`.

**Capturas a adjuntar:** pantalla de inicio de sesión · panel con datos · respuesta de salud.

**Observación honesta:** en la capa gratuita de la plataforma, la instancia se suspende
por inactividad y la primera petición posterior puede demorar hasta cincuenta segundos
(requisito RNF-05, que lo admite de forma explícita).

---

## 2. La autenticación controla el acceso y distingue roles

| Elemento | Dónde |
|---|---|
| Proveedor de identidad | Firebase Authentication (correo y contraseña) |
| Validación del token en el servidor | `backend/app/seguridad.py` |
| Niveles de autorización | consulta · operación · administración |
| Roles del alcance | **administrador** y **operador** |

**Cómo se comprueba**

1. Iniciar sesión con una cuenta de **operador** y abrir la pantalla de usuarios:
   la opción no debe aparecer.
2. Con una cuenta de **administrador**, la misma pantalla sí aparece y permite
   cambiar el rol y el estado de una cuenta.
3. En la API: `POST /api/v1/lecturas/manual` con un token de cuenta deshabilitada
   debe responder `403`.

**Capturas a adjuntar:** sesión iniciada · pantalla de administración de usuarios disponible solo para el administrador.

---

## 3. La persistencia guarda los datos del dominio

| Elemento | Dónde |
|---|---|
| Base de datos | Cloud Firestore, proyecto `sigvach26-bd` |
| Acceso | exclusivamente desde el servicio, con su cuenta de servicio |
| Colecciones | `modulos_cultivo`, `perfiles_cultivo`, `lecturas`, `alertas`, `usuarios` |

**Cómo se comprueba**

1. Registrar una lectura manual desde la aplicación.
2. Recargar y comprobar que la lectura permanece.
3. Reiniciar el servicio en la plataforma y verificar que los datos siguen ahí
   (no se pierden: la persistencia no depende de la memoria del proceso).

**Capturas a adjuntar:** lectura registrada · listado del historial con esa lectura.

---

## 4. La interfaz es adecuada y adaptable

| Elemento | Dónde |
|---|---|
| Diseño de la interfaz | apartado 2.4 de la monografía |
| Requisito | RNF-06: sin desplazamiento horizontal entre 320 y 1920 píxeles |
| Bocetos y figuras | capítulo 2, figuras de interfaz |

**Cómo se comprueba**

1. Abrir la aplicación web y reducir la ventana hasta el ancho de un teléfono.
2. La disposición debe reorganizarse en una columna, sin desplazamiento horizontal.

**Capturas a adjuntar:** la misma pantalla en móvil, tableta y escritorio.

---

## 5. El repositorio tiene historial de avance progresivo

| Elemento | Dato |
|---|---|
| Repositorio | `https://github.com/saintssud-sud/Proyecto---Diplomado` (público: el docente entra sin invitación) |
| Confirmaciones | más de sesenta, en fechas repartidas a lo largo del proyecto |
| Mensajes | descriptivos, con el tipo de cambio y su alcance |
| Tablero de tareas | `docs/TABLERO.md` |

**Cómo se comprueba:** abrir el repositorio y revisar el historial de confirmaciones
y el archivo del tablero.

**Capturas a adjuntar:** listado de confirmaciones con fechas · tablero de tareas.

---

## 6. El repositorio documenta cómo ejecutar el proyecto

| Elemento | Dónde |
|---|---|
| Instrucciones generales | `README.md` del repositorio |
| Contrato de la API | `https://sigvach-api.onrender.com/docs` |
| Guías de puesta en marcha | `docs/01_WINDOWS_SIN_DOLOR.md`, `docs/02_LINUX_MX_SIN_DOLOR.md` |

**Cómo se comprueba:** seguir las instrucciones del README en un equipo distinto.

**Captura a adjuntar:** el README con las instrucciones.

---

## 7. Las credenciales y claves no están en el repositorio

| Elemento | Dónde |
|---|---|
| Plantilla de variables | `.env.example` (sin valores reales) |
| Exclusiones | `.gitignore`: `.env`, `lib/firebase_options.dart`, `android/app/google-services.json`, `firebase-adminsdk*.json`, almacenes de claves |
| Revisión del historial | búsqueda de claves privadas, contraseñas y claves de dispositivo en todas las confirmaciones, con resultado negativo |
| Verificador reproducible | `scripts/verificar_acceso_directo.py` |

**Cómo se comprueba**

1. `git ls-files` no muestra ningún archivo de credenciales.
2. La búsqueda en el historial no encuentra material secreto.
3. Las reglas de seguridad se verifican con el programa: sin credenciales, las
   cinco colecciones responden `403`; con la cuenta de servicio, `200`.

**Documento de respaldo:** `docs/12_VERIFICACION_SEGURIDAD.md`.

**Captura a adjuntar:** la salida del verificador de acceso directo.

---

## 8. Las entradas se validan en el servidor

| Elemento | Dónde |
|---|---|
| Esquemas de validación | `backend/app/esquemas.py` |
| Respuesta ante un dato inválido | código `422` con el campo que no cumple la condición |
| Pruebas automáticas | `backend/pruebas/` (ochenta y tres casos) |

**Cómo se comprueba**

1. En `https://sigvach-api.onrender.com/docs`, ejecutar `POST /api/v1/lecturas/manual`
   con un valor fuera del rango admitido o con un campo faltante.
2. La respuesta debe ser `422` indicando el campo observado.

**Capturas a adjuntar:** petición inválida y respuesta del servicio.

---

## Anexos del repositorio

| Anexo | Contenido |
|---|---|
| `docs/10_DESPLIEGUE.md` | Plan de despliegue |
| `docs/11_AUDITORIA_CUMPLIMIENTO.md` | Auditoría de cumplimiento |
| `docs/12_VERIFICACION_SEGURIDAD.md` | Verificación de las reglas de seguridad |
| `docs/13_EVIDENCIAS_DE_LA_ENTREGA.md` | Este documento |
| `docs/BITACORA_MARTES_2026-09-15.md` | Bitácora de trabajo, con los hallazgos y sus correcciones |

---

## Archivo instalable de Android (APK)

| Dato | Valor |
|---|---|
| Archivo | `build/app/outputs/flutter-apk/app-release.apk` |
| Tamaño | 53,8 MB |
| Compilación | `flutter build apk --release --dart-define=API_BASE_URL=https://sigvach-api.onrender.com` |
| Firma | Con la clave de depuración (ver la nota de revisión del apartado 2.7 de la monografía) |
| Requisito de sistema | Android 8.0 (API 26) o superior, conforme al RNF-04 |

El archivo se compila apuntando al **servicio publicado**, de modo que la aplicación
instalada funciona desde cualquier red con acceso a internet y no requiere que el
equipo del autor esté encendido.

**Cómo se instala**

1. Copiar el archivo al teléfono (cable, almacenamiento o mensajería).
2. Abrirlo desde el teléfono y aceptar la instalación de aplicaciones de origen desconocido.
3. Iniciar sesión con una cuenta del sistema y comprobar que el panel muestra las
   variables del módulo con sus valores y estados.

**Observaciones de la compilación**

- La compilación descarta los recursos no utilizados: el paquete de iconos se
  redujo un 99,4 % (de 1.645.184 a 10.184 bytes).
- Los complementos `firebase_auth` y `firebase_core` aplican hoy el complemento
  Gradle de Kotlin de forma directa; una versión próxima de Flutter pedirá migrarlos
  al complemento integrado. Se deja constancia como tarea de mantenimiento y no
  afecta al funcionamiento actual.
