# Evidencia de pruebas

Esta carpeta guarda la **salida de los ejecutores de pruebas**, con la fecha en el nombre del
archivo. Es la evidencia que pide el apartado 2.8: un informe que se puede volver a ejecutar, no
una captura sin fecha.

---

## Última ejecución · martes 29 de septiembre de 2026

| Batería | Comando | Resultado | Informe |
|---|---|---|---|
| Servicio (API) | `.venv\Scripts\python.exe -m pytest backend -q --no-header -p no:cacheprovider` | **106 pruebas, 0 fallos, 0 errores** (7,24 s) | `pytest-2026-09-29.txt` y `pytest-2026-09-29.xml` |
| Aplicación | `flutter test` | **96 pruebas, todas en verde** | `flutter-test-2026-09-29.txt` |
| Análisis estático | `flutter analyze` | **Sin observaciones** | `flutter-analyze-2026-09-29.txt` |

**Total: 202 pruebas automatizadas**, 106 del servicio y 96 de la aplicación.

El informe `.xml` es el formato JUnit, de modo que los números se pueden leer sin abrir el texto
(`tests`, `failures`, `errors`, `time`).

---

## Cómo se vuelven a ejecutar

```powershell
# Servicio (desde la raíz del repositorio)
.venv\Scripts\python.exe -m pytest backend -q --no-header -p no:cacheprovider --junitxml="evidencia\pytest-AAAA-MM-DD.xml"

# Aplicación (desde la raíz del repositorio)
flutter test
flutter analyze
```

Se guardan con la fecha del día en el nombre, de modo que el historial de informes muestre la
progresión del proyecto y no una sola foto.

---

## Qué cubre cada batería

**Servicio (106 casos).** El contrato de la API contra un repositorio en memoria: camino feliz y
error de cada operación, la validación con su formato de error único, la autorización por rol
(401 sin token, 403 con el rol equivocado), el rechazo de campos ajenos al contrato y las reglas de
negocio, como no poder cambiar el rol desde el perfil propio.

**Aplicación (96 casos).** El cliente de la API, los repositorios, los controladores de las
pantallas, los roles, los estados de carga, vacío y error, el encabezado del menú y el resumen del
clima. Incluye los tres casos nuevos del cierre de sesión: que un 401 del servicio cierre la sesión
local y muestre el motivo, y que un fallo de conexión **no** la cierre.

---

## Archivos temporales

La carpeta `_tmp/` sólo existe mientras corre `pytest` con `--basetemp`, y su contenido no se
versiona.
