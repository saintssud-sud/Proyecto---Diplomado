# 📓 Bitácora — Sesión del martes 22 de septiembre de 2026

**Proyecto:** SIGVACH — Sistema de Gestión de Variables para Cultivos Hidropónicos
**Grupo:** 3 · **Entrega E2:** sábado 26/09 · **Defensa:** martes 13/10 a las 17:00
**Objetivo de la sesión:** atender las observaciones de la tutoría T2 y **verificar
contra los documentos originales** cada afirmación que el trabajo atribuye a los
antecedentes institucionales.

---

## 1. Punto de partida

| Pieza | Estado al comenzar |
|---|---|
| Entregable E1 | **Entregado** (perfil de proyecto, 39 páginas, PDF) |
| Observaciones de la tutoría T2 | 26 observaciones recibidas, clasificadas en 12 de redacción, 5 del sistema, 4 de datos y 5 de riesgos |
| Datos del ensayo previo | Incorporados como **comunicación personal**, a partir del testimonio del autor del ensayo |
| Antecedentes institucionales | Citados en la monografía y en el entregable, **sin contrastar** contra los documentos originales |
| Repositorio | 2 confirmaciones locales pendientes de subir |

La valoración de la tutoría fue: *"Es uno de los perfiles más completos del grupo… Lo
que queda son inconsistencias internas entre tablas y un Capítulo 1 sin números.
Ninguna obliga a replantear el alcance."*

---

## 2. El problema que resolvió esta sesión

Una de esas "inconsistencias internas" tenía una causa concreta: **el trabajo afirmaba
cosas sobre los antecedentes que no habían sido comprobadas en las fuentes**. Se decía,
por ejemplo, que en el ensayo previo las mediciones "no quedaron registradas en el
informe" y que por eso "la información medida se perdió".

Al revisar el documento original, esa afirmación **no se sostiene**: el informe **sí**
consigna los rangos de referencia y varios valores medidos. Lo que no conserva es **la
serie de las lecturas**. La diferencia no es menor: cambiar "no se registró nada" por
"se midió y se corrigió con el dato, pero no se conservó la serie" describe con
precisión el problema que el sistema resuelve, y además queda respaldado por la fuente
en lugar de depender solo del testimonio.

---

## 3. Verificación de los antecedentes

Se extrajo el texto íntegro de los dos documentos y se buscó en él cada afirmación
citada, apartado por apartado (`pdftotext -layout`).

| Fuente | Archivo | Extensión |
|---|---|---|
| Santos Navarro, C. M. (2020) — espinaca, NFT contra raíz flotante | `41644_MARCO_TEORICO.pdf` | 58 páginas |
| Tejerina Pinto, A. D. (2018) — lechuga, raíz flotante | `39483_MARCO_TEORICO.pdf` | 73 páginas |

### 3.1 Santos Navarro (2020)

| Afirmación del trabajo | Apartado de la fuente | Veredicto |
|---|---|---|
| Comparó la espinaca en NFT y en raíz flotante | §1.1 y §2.2 | ✅ Confirmado |
| Siguió el pH, la conductividad y la temperatura con rangos de referencia | §1.2.6.3, §1.2.6.4 y §2.5.10 a §2.5.12 | ✅ Confirmado |
| Renovó la solución **cada 15 días** ante sus desviaciones | §2.5.9 (literal) | ✅ Confirmado |
| Usó instrumentos portátiles | §2.1.7: pH metro y conductímetro | ✅ Confirmado |
| Las mediciones "no quedaron registradas" y "se perdió" la información | El informe registra pH 5,8 (raíz flotante) y 5,6 (NFT), la reducción de 0,1 mS/cm y 26 °C | ⚠️ **Impreciso: lo no conservado es la serie** |
| La solución se renovaba "al concluir el período de desarrollo" | Contradice §2.5.9 | ⚠️ **No coincide** |
| Tabla 1: variables = "peso, **volumen** y desarrollo foliar" | §2.7 y §3.1: germinación, largo, ancho y número de hojas, peso y rendimiento | ⚠️ **Impreciso** |
| "No es posible saber con qué instrumento se midió" | §2.1.7 enumera los instrumentos | ⚠️ **Impreciso** |

**Valores que aporta el informe** (útiles para el Capítulo 1, que la tutoría señaló
"sin números"): pH 5,8 en raíz flotante y 5,6 en NFT; conductividad reducida
0,1 mS/cm a partir del tercer día; temperatura de la solución de 26 °C como máxima del
ciclo; renovación total cada 15 días.

### 3.2 Tejerina Pinto (2018)

| Afirmación del trabajo | Apartado de la fuente | Veredicto |
|---|---|---|
| Lechuga en raíz flotante, dos variedades | §2.1.4.1, §2.1.4.2 y §3.3.3 | ✅ Confirmado |
| Grand Rapids Tbr y Morada Criolla | §3.3.3 (factor B) y objetivo general | ✅ Confirmado |
| Oxigenación manual (una y dos veces al día) y automatizada | §3.3.3 (factor A) | ✅ Confirmado |
| Prendimiento, tamaño y número de hojas, largo de raíces y diámetro del tallo | §3.3.4 y §3.6.1 a §3.6.5 | ✅ Confirmado |
| Registro manual, sin herramienta informática | §3.6.1 "se contó de forma manual"; calibre y regla | ✅ Confirmado |

Con esto se retiró la nota de revisión que pedía comprobar la grafía de las variedades:
la fuente usa esa grafía en su título, en sus objetivos y en sus encabezados.

---

## 4. Correcciones aplicadas

| Documento | Tramo | Corrección |
|---|---|---|
| Monografía | §1.1.3 | Se retira la nota de revisión de la grafía; se precisa que el antecedente analizó **variables de respuesta** |
| Monografía | §1.1.3, Tabla 1 | Fila de Santos Navarro: variables reales en lugar de "peso, volumen y desarrollo foliar"; el vacío pasa a ser **la serie no conservada** |
| Monografía | §1.1.3, síntesis | Se reemplaza "no quedaron registradas" por la descripción verificada, **con los valores del informe** |
| Monografía | §1.2 | Se nombra el cultivo (espinaca); la serie no conservada; la renovación pasa a **cada quince días**, como documenta la fuente |
| Monografía | §1.2, puntos críticos 1 y 2 | "no se conserva la serie de las mediciones"; se retira el argumento del instrumento |
| Monografía | Bibliografía | La nota de comunicación personal precisa qué es lo que no se conservó |
| Borradores | `Capitulo 1 - Introduccion`, `Capitulo I - Mejorado` | Se retiran las notas de revisión y se precisa el registro del antecedente |
| Entregable E1 | Párrafo de antecedentes | Descripción verificada: medición con pHmetro y conductímetro, corrección en el momento y serie no conservada |
| Entregable E1 | Puntos críticos 1 y 2 | Renovación cada quince días; se retira el argumento del instrumento |

**Archivos regenerados:**

| Archivo | Resultado |
|---|---|
| `Monografia - Borrador Completo (Diplomado) - institucional.docx` | Regenerado con el conversor institucional |
| `Santos_Perfil_Proyecto_E1.docx` / `.pdf` | Regenerados: **39 páginas**, 656 KB |
| `Proyecto SIGVACH/docs/Santos_Perfil_Proyecto_v1.docx` / `.pdf` | Copias del repositorio actualizadas |
| `Proyecto SIGVACH/docs/15_VERIFICACION_DE_LOS_ANTECEDENTES.md` / `.docx` | **Nuevo**: informe de la verificación, afirmación por afirmación |
| `Recomendaciones E1 - plan de accion.md` / `.docx` | Actualizado con el estado de cada observación |

**Trazabilidad.** El texto extraído de cada documento quedó guardado en
`verificacion_antecedentes/` (`santos_navarro_2020.txt` y `tejerina_2018.txt`), de modo
que cualquier comprobación puede repetirse sobre el texto completo. Se conservan
respaldos del entregable y de la monografía anteriores a esta corrección.

---

## 5. Estado de las observaciones de la tutoría

| Grupo | Total | Atendidas | Pendientes |
|---|---|---|---|
| A. Redacción y consistencia | 12 | Verificación de antecedentes, fuentes con URL y fecha, datos reales en el Capítulo 1 | A-1, A-2, A-3, A-4, A-6, A-7, A-8, A-9, A-10, A-12 |
| B. Cambios en el sistema | 5 | — | B-1 a B-5 (incluye el **simulador del dispositivo**, requisito del E2) |
| C. Datos del autor | 4 | Mediciones por semana (21) y renovación de la solución | El número de detecciones tardías; el ámbito del módulo piloto |
| D. Riesgos y limpieza | 5 | Clave del dispositivo rotada e historial revisado | Datos ficticios, hoja de verificación, figuras |

---

## 6. Dos puntos que requieren confirmación del autor

1. **Renovación de la solución.** El informe documenta la renovación **cada 15 días**;
   el testimonio del autor indicó "al concluir el período de desarrollo". Se dejó el
   dato documentado, porque es el verificable, y conviene confirmar si además hubo una
   renovación total al final del ciclo.
2. **Ámbito del módulo piloto.** El entregable menciona "el módulo de cultivo piloto" y
   no existe un módulo físico construido. Hay que decidir cómo se nombra el ámbito (el
   ensayo de referencia, la Facultad, un módulo previsto) para el objetivo general y el
   apartado 1.2, que es lo que pide la recomendación A-4.

---

## 7. Herramientas empleadas

| Herramienta | Para qué |
|---|---|
| `pdftotext -layout` | Extraer el texto íntegro de los dos documentos originales |
| `scripts/md_a_docx.py` | Regenerar la monografía institucional y los documentos de trabajo |
| `exportar_e1_pdf.ps1` | Exportar el entregable a PDF y copiarlo al repositorio |
| `corregir_antecedentes_verificados.py` | Aplicar las correcciones a la monografía y a los borradores, con respaldo previo |
| `corregir_antecedentes_e1.py` | Aplicar las correcciones al entregable |

> **Nota técnica.** El primer intento de extracción con Word dejó una instancia
> bloqueada que después impedía automatizar Word (`0x800706BE`). Se cerraron las
> instancias y se optó por `pdftotext`, que además conserva la disposición del texto y
> es reproducible desde la línea de comandos.

---

## 8. Próximos pasos

| # | Tarea | Cuándo |
|---|---|---|
| 1 | **Simulador del dispositivo** que envía lecturas con la clave, para el flujo completo del E2 | Antes del sábado 26 |
| 2 | Reintento y memoria en el dispositivo ante los 60 s de arranque en frío del servicio | Antes del sábado 26 |
| 3 | Cálculo del consumo diario de Firestore y su documentación | Antes del sábado 26 |
| 4 | Resto de las observaciones de redacción (A-1, A-2, A-3, A-6, A-7, A-8, A-9, A-10) | Durante la semana |
| 5 | Guion de la demostración y plan de contingencia para la defensa | Antes del 13/10 |

---

*Bitácora de la sesión del martes 22 de septiembre de 2026. Los datos citados en los
apartados 3 y 4 provienen de los documentos originales de cada antecedente y de la
verificación registrada en `docs/15_VERIFICACION_DE_LOS_ANTECEDENTES.md`.*
