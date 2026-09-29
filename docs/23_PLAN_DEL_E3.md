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
| **403 con el rol equivocado** | La lógica está ✓, pero **no se ha probado** | Probar con el token del **Operador** (falta su contraseña) |

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
| Al menos una **suite automatizada con su reporte en el repositorio** | ✓ Existen **199 pruebas** (106 del servicio y 93 de la aplicación) | **Correrlas y versionar los reportes** |
| Tabla del **2.8** con camino feliz y error de cada Must, más 401 y 403 | ✗ | **Construirla** |

### Documento

| Lo que pide | Estado |
|---|---|
| Capítulos 1 y 2, apartados **2.1 a 2.8** completos en borrador | Tenemos **2.2 a 2.6** ✓. Faltan **2.1** (está en la monografía), **2.7 Seguridad** y **2.8 Pruebas** |

### Repositorio

| Lo que pide | Estado | Qué falta |
|---|---|---|
| Commits en días distintos | ✓ 14 días | — |
| Pruebas y reportes versionados | ✗ | Subirlos con el documento |
| README al día | Casi ✓ | Dice **90 casos** cuando hay **106**, y **no documenta el comando de `flutter test`** |

---

## 2. La lista del docente, verificada

| Verificación | Estado |
|---|---|
| Sin token, una ruta protegida responde **401** | ✓ Comprobado contra el servicio publicado |
| Con el rol equivocado, responde **403** | ✗ Falta probarlo: necesitamos el token del Operador |
| Un dato inválido responde **400 o 422** con el formato de la API | ✓ Comprobado (rechaza la variable desconocida con el detalle del campo) |
| Todos los Must funcionan **en línea** | ✓ Verificado en los recursos; falta el recorrido uno por uno con evidencia |
| Las pruebas automatizadas **corren** con el comando del campo de texto | Falta documentar el comando de la aplicación |
| Cada fila de la tabla **2.8** tiene evidencia | ✗ Por construir |
| **No hay secretos** en el repositorio | ✓ Verificado con `scripts/verificar_sin_secretos.py` |

---

## 3. El plan, día por día

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
- Actualizar el **README**: las dos órdenes de pruebas y el conteo real.
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
