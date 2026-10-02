# Plan del E3 · Checkpoint técnico

**Cierre:** sábado **3 de octubre de 2026, 23:59** (se admiten 72 h de atraso, con −10 puntos por día)
**Entrega:** `Santos_Freddy_E3.pdf` + los datos en el campo de texto de la tarea
**Cuestionario Q3:** aparte, 5 % de la nota, cierra a la misma hora y **no admite atraso**

---

## 1. Qué pide el E3, y cómo estamos en cada punto

### Autenticación

| Lo que pide | Estado | Qué falta |
|---|---|---|
| Login con contraseñas en **hash** | ✓ Las gestiona **Firebase Authentication**: el servicio nunca ve ni almacena la contraseña | Explicarlo en **2.7** |
| Sesión o token **que vence** | ✓ El token de identidad de Firebase caduca cada hora | Explicarlo en 2.7 |
| Un **401 que devuelve al login** | ✗ **Encontrado: la aplicación define `esNoAutenticado` pero no lo usa en ninguna parte.** Ante un 401 muestra un error, no devuelve al login | **Implementarlo** (cambio de código) |

### Autorización por rol

| Lo que pide | Estado | Qué falta |
|---|---|---|
| La API verifica el rol **en cada ruta** | ✓ Se resuelve en `backend/app/seguridad.py`, con dependencias por ruta: `requiere_administracion`, `requiere_operacion` y `requiere_consulta`. No depende de la interfaz | Documentarlo en 2.7 |
| Las cuentas nuevas nacen con el **menor privilegio** | ✓ Doble garantía: la aplicación registra con `Roles.porDefecto = operador`, y el servicio, si el perfil no trae rol, asigna `rol_operador` | Documentarlo en 2.7 |
| **403 con el rol equivocado** | ✓ **Probado el 29/09**: con la sesión del Operador, `GET /api/v1/usuarios` responde **403**, y con la del Administrador responde **200**. La medición quedó en `evidencia/cuentas-de-prueba-2026-09-29.txt` | Falta la captura desde la interfaz |

### Validación doble

| Lo que pide | Estado |
|---|---|
| En el servidor, con **formato de error único** | ✓ Pydantic devuelve 422 con la estructura `codigo`, `mensaje`, `detalle.campos` |
| En el cliente, por usabilidad | ✓ Los formularios validan antes de enviar |

### Todos los Must en producción

Los siete requisitos Must son **RF-01, RF-03, RF-05, RF-06, RF-08, RF-09 y RF-11**. Hay que
comprobar **uno por uno** que funcionan en la URL pública, y dejar la evidencia.

**Y una corrección pendiente en el código**, no solo en el documento:

> `DELETE /api/v1/lecturas/{id}` **existe en el servicio** (`rutas/lecturas.py`, línea 161) y
> contradice la trazabilidad que declaramos (A-01 y RNF-08). Quitarlo del documento ya está hecho;
> falta **decidir qué se hace con el endpoint**: eliminarlo, o convertirlo en **anulación con
> motivo** (que es lo coherente con «no se altera una lectura»).

### Pruebas con evidencia

| Lo que pide | Estado | Qué falta |
|---|---|---|
| Al menos una **suite automatizada con su reporte en el repositorio** | ✓ **202 pruebas** (106 del servicio y 96 de la aplicación), ejecutadas el 29/09 con sus reportes versionados | — |
| Tabla del **2.8** con camino feliz y error de cada Must, más 401 y 403 | ✗ | **Construirla**, ya con las **31 capturas fechadas** de `evidencia/capturas-2026-09-30/` |

### Documento

| Lo que pide | Estado |
|---|---|
| Capítulos 1 y 2, apartados **2.1 a 2.8** completos en borrador | Tenemos **2.2 a 2.6** ✓. Faltan **2.1** (está en la monografía), **2.7 Seguridad** y **2.8 Pruebas** |

### Repositorio

| Lo que pide | Estado | Qué falta |
|---|---|---|
| Commits en días distintos | ✓ **161 confirmaciones en 17 días distintos** | — |
| Pruebas y reportes versionados | ✓ `evidencia/pytest-2026-09-29.txt` y `evidencia/flutter-test-2026-09-29.txt` | — |
| README al día | ✓ Documenta las dos órdenes de pruebas y el conteo real: **106 del servicio y 96 de la aplicación** | — |

---

## 2. La lista del docente, verificada

| Verificación | Estado |
|---|---|
| Sin token, una ruta protegida responde **401** | ✓ Comprobado contra el servicio publicado |
| Con el rol equivocado, responde **403** | ✓ Comprobado con la sesión del Operador contra el servicio publicado: `GET /api/v1/usuarios` responde 403, y 200 con la del Administrador |
| Un dato inválido responde **400 o 422** con el formato de la API | ✓ Comprobado (rechaza la variable desconocida con el detalle del campo) |
| Todos los Must funcionan **en línea** | ✓ Verificado en los recursos; falta el recorrido uno por uno con evidencia |
| Las pruebas automatizadas **corren** con el comando del campo de texto | ✓ El README documenta las dos: `python -m pytest` desde `backend/` (106) y `flutter test` desde la raíz (96) |
| Cada fila de la tabla **2.8** tiene evidencia | ✗ Por construir; las capturas fechadas ya están reunidas |
| **No hay secretos** en el repositorio | ✓ Verificado con `scripts/verificar_sin_secretos.py` |

---

## 3. El plan, día por día

> **Estado al viernes 2 de octubre.** Los tres primeros días se cumplieron. El electrodo revivió con
> el remojo y quedó **calibrado** con los patrones de 4,01 y 6,86 —1520 mV y 1280 mV—, el firmware
> ya publica el **pH** y el módulo está midiendo **las seis variables** en producción. Las pruebas se
> corrieron el 29/09 (**202**, sin fallos) y sus reportes están versionados, el README quedó al día y
> el recorrido del nivel funcional quedó capturado en **31 capturas fechadas** en
> `evidencia/capturas-2026-09-30/`. Lo que resta es trabajo de documento: los apartados **2.7**,
> **2.8** y **2.1**, la regeneración del `.docx` y el **PDF**.

### Martes 29 (hoy)

- Decidir el destino del **`DELETE` de lecturas** (quitar o anular con motivo) y aplicarlo en el
  código.
- **Implementar el 401 que devuelve al login** en la aplicación.
- Empezar a escribir el **apartado 2.7 (Seguridad)**.
- (En paralelo, lo del módulo: el pull-up, el divisor ÷2 y la comprobación de 24 h del electrodo.)

### Miércoles 30

- **La decisión del electrodo** y, si revive, la **calibración con los patrones** → alimenta el 2.8.
- Seguir con el 2.7.

### Jueves 1

- **Firmware:** la conversión a pH y la publicación de la variable, para cerrar los Must.
- **Correr las pruebas** (`pytest` y `flutter test`) y **guardar los reportes** en el repositorio.
- Empezar la **tabla del 2.8** con los casos ya verificados.

### Viernes 2

- Cerrar **2.7 y 2.8**, y añadir el **2.1** que falta.
- **Verificar los siete Must en línea**, uno por uno, con su evidencia.
- ~~Actualizar el README: las dos órdenes de pruebas y el conteo real.~~ **Hecho.**
- Generar el **PDF** y revisar el documento completo.

### Sábado 3

- **Revisión final** con la lista del docente, las siete casillas.
- Subir el PDF y escribir los datos en el campo de texto (¡con **dos** usuarios de prueba!).

---

## 4. Lo que necesito de ti

1. **La contraseña de la cuenta Operador** (`tecnico@gmail.com`). Sin ella no se puede verificar el
   **403**, que es un requisito explícito: el docente pide **un usuario de prueba por rol**.
2. **La decisión sobre el `DELETE` de lecturas**: ¿se quita el endpoint, o se convierte en
   anulación con motivo?

---

## 5. Los datos que hay que poner en el campo de texto de la tarea

```
Frontend (URL pública): https://sigvach26-bd.web.app
API (ruta de salud): https://sigvach-api.onrender.com/api/v1/salud
Repositorio: https://github.com/saintssud-sud/Proyecto---Diplomado
Usuario de prueba · rol 1 (administrador): mateosantos@yahoo.es / 654321
Usuario de prueba · rol 2 (operador): tecnico@gmail.com / (por confirmar)
Pruebas automatizadas: (comando) — reporte en (ruta del repositorio)
```

---

## 6. Lo que NO hay que hacer

El apartado **2.9 (Despliegue)**, el **Capítulo 3**, los **manuales** y el **monitoreo** son del
**E4**. Si ya están, se suman; no restan. Así que no hay que dedicarles tiempo esta semana.
