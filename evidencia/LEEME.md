# Evidencia de pruebas

Esta carpeta guarda la **salida de los ejecutores de pruebas**, con la fecha en el nombre del
archivo. Es la evidencia que pide el apartado 2.8: un informe que se puede volver a ejecutar, no
una captura sin fecha.

---

## Última ejecución · lunes 5 de octubre de 2026

| Batería | Comando | Resultado | Informe |
|---|---|---|---|
| Servicio (API) | `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` | **149 pruebas, 0 fallos, 0 errores** (8,76 s) | `pytest-2026-10-05-memoria-lecturas.txt` |
| Aplicación | `flutter test` | **96 pruebas, todas en verde** | `flutter-test-2026-10-05.txt` |
| Análisis estático | `flutter analyze` | **Sin observaciones** | `flutter-analyze-2026-10-05.txt` |

**Total: 245 pruebas automatizadas**, 149 del servicio y 96 de la aplicación.

El servicio pasó de 106 a 119 casos el 5 de octubre: los trece nuevos comprueban el **registro de
una línea por petición** (que se escriba una sola línea por petición, con método, ruta declarada,
código y duración, y que no registre cabeceras de autorización, cuerpos ni la cadena de consulta).
Ese día llegó a 149: los treinta últimos comprueban la **memoria intermedia de las consultas de
lecturas** que sostiene el RNF-01 (que la segunda consulta igual no vuelva a la base, que la clave
distinga cualquier cambio de parámetros, que registrar o eliminar descarte lo memorizado, que la
ventana venza y que un fallo de la memoria no tumbe la petición).

> Los informes del 29 de septiembre (`pytest-2026-09-29`, `flutter-test-2026-09-29`,
> `flutter-analyze-2026-09-29`) se conservan como historial. Dicen 202 pruebas porque son anteriores
> a los trece casos nuevos del registro de peticiones: el número vigente es **245**.

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

**Servicio (149 casos).** El contrato de la API contra un repositorio en memoria: camino feliz y
error de cada operación, la validación con su formato de error único, la autorización por rol
(401 sin token, 403 con el rol equivocado), el rechazo de campos ajenos al contrato, las reglas de
negocio —como no poder cambiar el rol desde el perfil propio—, el registro de una línea por
petición y, desde el 5 de octubre, la memoria intermedia de las consultas de lecturas.

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

## Rendimiento (RNF-01) · antes y después de la memoria intermedia

La medición se hace siempre con el mismo programa, las mismas credenciales, el mismo número de
consultas (20) y los mismos límites (200 y 5 registros):

```powershell
.venv\Scripts\python.exe scripts\medir_rendimiento.py --correo operador@proyecto.test `
    --clave "SIGVACH.Ope.2026" --consultas 20 --limite 200 `
    --servicio http://127.0.0.1:8011 --sufijo -antes-local --nota "..."
```

| Archivo | Qué mide |
|---|---|
| `rendimiento-2026-10-05-limite-200-antes-publicado.txt` | El «antes», contra el **servicio publicado** (`https://sigvach-api.onrender.com`): mediana 878 ms, percentil 95 1.461 ms, 2 de 20 dentro del objetivo. Es el informe que dejó el incumplimiento por escrito y se conserva tal como se midió |
| `rendimiento-2026-10-05-limite-200-antes-local.txt` | El mismo «antes» en **local**, con `SEGUNDOS_CACHE_LECTURAS=0` (memoria desactivada): mediana 963 ms, percentil 95 1.429 ms, 2 de 20 |
| `rendimiento-2026-10-05-limite-200-despues-local.txt` | El «después» en **local**, con la memoria activa: mediana 363 ms, percentil 95 856 ms, 15 de 20 |
| `rendimiento-2026-10-05-limite-200-despues-local-2.txt` | La misma corrida, repetida con la traza de la memoria activada (`NIVEL_REGISTRO=DEBUG`): mediana 503 ms, percentil 95 696 ms, **20 de 20**. La traza deja constancia de que las veinte consultas salieron de la memoria y solo el calentamiento leyó la base |
| `rendimiento-2026-10-05-limite-200-despues-local-3.txt` | La misma corrida por tercera vez, con el servicio recién arrancado: mediana 468 ms, percentil 95 741 ms, **20 de 20** |
| `rendimiento-2026-10-05-limite-5-antes-local.txt` · `...-limite-5-despues-local.txt` | El tamaño que usa el panel (5 registros): mediana 537 → 263 ms, percentil 95 561 → 405 ms, 20 de 20 en los dos casos |
| `rendimiento-2026-10-05-comparacion.txt` | La tabla del antes y el después, con el método y la explicación de lo que queda |

**La comparación es local contra local.** El servicio publicado todavía ejecuta el código anterior,
porque el cambio no está desplegado: comparar una medición local con una del servicio publicado
mediría la red y la capa gratuita, no la optimización. El «antes» local reproduce el problema del
publicado —misma mediana, mismo percentil 95, mismas 2 de 20 consultas dentro del objetivo—, que es
lo que hace válida la comparación. Volver a medir contra el servicio publicado queda pendiente del
despliegue.

---

## Archivos temporales

La carpeta `_tmp/` sólo existe mientras corre `pytest` con `--basetemp`, y su contenido no se
versiona. La carpeta `respaldos/` guarda las copias de la base y tampoco se versiona: sus archivos
llevan fecha en el nombre y se conservan aparte.
