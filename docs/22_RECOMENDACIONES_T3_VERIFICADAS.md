# Recomendaciones de la tutoría T3 — verificación y plan

**Fuente:** `Recomendaciones_E2_T3.txt` · M.Sc. Ing. Isaac Lange Aguilar · 28 de septiembre de 2026
**Documento revisado por el docente:** `Santos_Freddy_E2.pdf` (48 páginas)
**Plazo del E3:** **sábado 3 de octubre, 23:59**

---

## 1. La valoración

El docente considera esta entrega **«la más sólida del grupo»**, y destaca tres cosas que van más
allá de lo pedido: el ESP32 publicando lecturas reales por HTTPS con clave propia, la evaluación
contra el rango vigente con generación de alertas, y las 202 pruebas automatizadas. También valora
que el apartado 2.6 cuente **dificultades verdaderas** con su resolución.

Sus observaciones son **de ajuste**, no de fondo. Eso es importante: no hay que rehacer nada, hay
que afinar.

---

## 2. Cada recomendación, ya verificada contra el documento

| # | Recomendación del docente | Estado comprobado | Qué hacer |
|---|---|---|---|
| 1 | **2.4.4:** `DELETE /api/v1/lecturas/{id}` contradice A-01 y RNF-08 | **Confirmado**: está en la **Tabla 17** («DELETE · Administrador») | Quitarlo, o cambiarlo por **anulación con motivo** (que es lo coherente con «no se altera una lectura») |
| 2 | **2.4.1:** Open-Meteo sigue en la Tabla 10 y no responde a ningún RF | **Confirmado**: en la **Tabla 10** aparece como «Servicio externo de contexto» | Quitarlo de la Tabla 10. En la **Tabla 18** ya figura como *fuera del alcance evaluado* ✓, así que ahí no hay nada que tocar |
| 3 | **2.6.3:** la quinta dificultad (permisos del entorno) es del equipo, no del sistema | **Confirmado**: es la quinta («El entorno de desarrollo impedía ejecutar el analizador…») | Quitarla. Las otras cuatro se quedan: son las mejores del apartado |
| 4 | **2.6.4:** la Figura 7 está al límite de 20 líneas | La figura está **dentro** del límite ✓ | Nada por ahora; solo vigilar si el fragmento crece |
| 5 | Las cuentas de evaluación no deben ir en la monografía | **Confirmado**: están en el apartado «Acceso para la evaluación» y en la **Tabla 19** | **Quitarlas del documento**; se quedan en el campo de texto de Moodle y en el README |
| 6 | Estimar el consumo diario de Firestore y anotarlo en 2.6 o 2.9 | **No está en el documento** ✗ | Añadirlo (ver el cálculo abajo) |
| 7 | **Ámbito:** nombrar el módulo piloto y su ubicación en el objetivo general y la Tabla 1 | **Pendiente** — es la observación **A-4** | Se cierra con la **maqueta física** que se monta esta semana |
| 8 | **Tabla 3** con números del piloto | **Parcial**: la primera fila ya dice «tres veces al día» | Completar con **mediciones por semana (21)**, **días entre renovaciones (15)** y **detecciones tardías** (dato a confirmar con el tutor) |
| 9 | **Verificación en vivo en T3:** salud, login de los dos roles, una lectura fuera de rango que dispare la alerta, y el operador **sin permiso** para editar rangos | ✓ **Todo probado.** El operador quedó comprobado el 29/09: contra el servicio publicado, `GET /api/v1/usuarios` responde **403** con su sesión y **200** con la del administrador (`evidencia/cuentas-de-prueba-2026-09-29.txt`) | Falta la captura del rechazo desde la interfaz |
| 10 | Confirmar que el firmware **reintenta y guarda** las lecturas no enviadas durante el arranque | La cola existe ✓ (el arranque informa «COLA: Memoria de pendientes lista») | Demostrarlo en vivo: apagar el WiFi, dejar que se acumulen lecturas y devolverlo |
| 11 | **E3:** llevar las pruebas al **2.8** con la tabla de casos (feliz y error por cada Must, 401 y 403) y los reportes de `pytest` y `flutter test` versionados | Las **202 pruebas ya existen y sus reportes están versionados** ✓; falta la evidencia ordenada en el documento | Es la tarea principal del E3 |

### El cálculo del consumo de Firestore (para el punto 6)

| Concepto | Valor |
|---|---|
| Intervalo real de envío | **5 minutos** |
| Ciclos por día | 24 h × 12 = **288** |
| Variables por ciclo | **5** |
| **Escrituras por día** | 288 × 5 = **1 440** |
| Cuota gratuita de Firestore | 20 000 escrituras/día |
| **Consumo** | **7,2 %** de la cuota diaria |

Si se suman las alertas que genera una lectura fuera de rango y los reintentos de la cola, el
consumo se queda **por debajo del 10 %**, que es el margen que ya se venía declarando.

---

## 3. Plan hacia el E3 (sábado 3 de octubre, 23:59)

### A. El documento (lo más pesado, y lo que más puntúa)

1. **Partir del E2** y crear la versión del E3 (mismo documento acumulativo, como pide la consigna).
2. Aplicar los **seis ajustes**: quitar el `DELETE` de lecturas y su fila, quitar Open-Meteo de la
   Tabla 10, quitar la quinta dificultad del 2.6.3, quitar las cuentas de evaluación, añadir el
   cálculo del consumo, y completar la Tabla 3.
3. **Nombrar el módulo piloto** en el objetivo general y en la Tabla 1 (cierra A-4).

### B. El apartado 2.8, que es nuevo para el E3

- **Tabla de casos**: por cada requisito **Must**, el caso feliz y el caso de error.
- Los **401 y 403** como casos propios (sin token, con token de rol insuficiente).
- **Reporte de `pytest`** y de **`flutter test`** ejecutados y **versionados en el repositorio**.
- Las tensiones de calibración medidas con los patrones (pH y TDS), cuando estén.

### C. El sistema, antes de la tutoría

- **Probar el rol Operador**: que pueda leer y **no** pueda editar rangos (recomendación 9).
- **Demostrar la cola de pendientes**: apagar el WiFi, acumular, reconectar.
- **Calibrar el pH** si el electrodo revive el miércoles, y el **TDS** con el patrón.

### D. Lo que hay que preguntarle al tutor

Está en `21_PREGUNTAS_PARA_LA_TUTORIA.md`, y lo urgente es: **A-11 y A-12** (que no quedaron
registradas), el **ámbito del módulo piloto** (A-4) y el **número de detecciones tardías** de la
Tabla 3.

---

## 4. Lo que no hay que tocar

Para no perder tiempo ni estropear lo que ya está bien:

- El **apartado 2.6** en general: el docente lo elogió explícitamente.
- Las **cuatro dificultades** que quedan tras quitar la quinta.
- La **Tabla 18**, donde Open-Meteo ya está declarado fuera de alcance.
- El **sistema desplegado**: funciona y está verificado; las correcciones son del documento.
