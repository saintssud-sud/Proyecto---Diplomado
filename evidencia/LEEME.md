# Evidencia de pruebas

Esta carpeta guarda la **salida de los ejecutores de pruebas**, con la fecha en el nombre del
archivo. Es la evidencia que pide el apartado 2.8: un informe que se puede volver a ejecutar, no
una captura sin fecha.

---

## Última ejecución · lunes 5 de octubre de 2026

| Batería | Comando | Resultado | Informe |
|---|---|---|---|
| Servicio (API) | `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` | **119 pruebas, 0 fallos, 0 errores** (8,94 s) | `pytest-2026-10-05.txt` |
| Aplicación | `flutter test` | **96 pruebas, todas en verde** | `flutter-test-2026-10-05.txt` |
| Análisis estático | `flutter analyze` | **Sin observaciones** | `flutter-analyze-2026-10-05.txt` |

**Total: 215 pruebas automatizadas**, 119 del servicio y 96 de la aplicación.

El servicio pasó de 106 a 119 casos el 5 de octubre: los trece nuevos comprueban el **registro de
una línea por petición** (que se escriba una sola línea por petición, con método, ruta declarada,
código y duración, y que no registre cabeceras de autorización, cuerpos ni la cadena de consulta).

> Los informes del 29 de septiembre (`pytest-2026-09-29`, `flutter-test-2026-09-29`,
> `flutter-analyze-2026-09-29`) se conservan como historial. Dicen 202 pruebas porque son anteriores
> a los trece casos nuevos: el número vigente es **215**.

---

## Cómo se vuelven a ejecutar

```powershell
# Servicio (desde la raíz del repositorio)
.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --junitxml="evidencia\pytest-AAAA-MM-DD.xml"

# Aplicación (desde la raíz del repositorio)
flutter test
flutter analyze
```

Se guardan con la fecha del día en el nombre, de modo que el historial de informes muestre la
progresión del proyecto y no una sola foto.

---

## Qué cubre cada batería

**Servicio (119 casos).** El contrato de la API contra un repositorio en memoria: camino feliz y
error de cada operación, la validación con su formato de error único, la autorización por rol
(401 sin token, 403 con el rol equivocado), el rechazo de campos ajenos al contrato, las reglas de
negocio —como no poder cambiar el rol desde el perfil propio— y, desde el 5 de octubre, el registro
de una línea por petición.

**Aplicación (96 casos).** El cliente de la API, los repositorios, los controladores de las
pantallas, los roles, los estados de carga, vacío y error, el encabezado del menú y el resumen del
clima. Incluye los tres casos del cierre de sesión: que un 401 del servicio cierre la sesión local y
muestre el motivo, y que un fallo de conexión **no** la cierre.

---

## Las demás evidencias

| Archivo | Qué demuestra |
|---|---|
| `cuentas-de-prueba-2026-09-29.txt` | Las dos cuentas `@proyecto.test`, una por rol: 401 sin token, 403 al operador, 200 al mismo operador en una ruta que le corresponde y 200 al administrador |
| `reglas-firestore-2026-09-29.txt` | Que las reglas publicadas coinciden con las del repositorio y que la escalada de privilegios quedó cerrada: el intento de cambiarse el propio rol responde 403 `PERMISSION_DENIED` |
| `despliegue-web-2026-09-29.txt` | Que la aplicación publicada pide los datos al servicio publicado, que coincide con la compilación local, que la ruta de salud responde y que el origen está autorizado |
| `seis-variables-publicadas-2026-10-04.txt` | Un ciclo completo del módulo publicado al servicio, con el certificado TLS validado y las seis variables confirmadas |
| `restauracion-2026-10-05.txt` | La prueba de restauración del respaldo: qué se exportó, qué se restauró en un módulo de prueba, cómo el servidor evaluó cada lectura contra su rango —una quedó fuera y generó su alerta—, qué se borró después y la comprobación de que no se perdió ningún dato real |

---

## Archivos temporales

La carpeta `_tmp/` sólo existe mientras corre `pytest` con `--basetemp`, y su contenido no se
versiona. La carpeta `respaldos/` guarda las copias de la base y tampoco se versiona: sus archivos
llevan fecha en el nombre y se conservan aparte.
