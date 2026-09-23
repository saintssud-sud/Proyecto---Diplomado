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
| A. Redacción y consistencia | 12 | Verificación de antecedentes, fuentes con URL y fecha, datos reales en el Capítulo 1, coherencia MoSCoW, métricas de los RNF, diccionario del entregable, versiones y plataforma de despliegue, contrato con las rutas de perfiles (A-1, A-2, A-3, A-5, A-6, A-7, A-8, A-9 y A-10) | A-4 (requiere el dato del autor), A-11 y A-12 |
| B. Cambios en el sistema | 5 | Dispositivo simulado, reintento con memoria, consumo de la base (B-3, B-4 y B-5) y trazabilidad de quién registró la lectura (B-2) | B-1 (operaciones de administración de usuarios en el servicio) |
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

## 8. El dispositivo simulado (lo que faltaba para el E2)

El entregable E2 pide la aplicación contra la API publicada con **dispositivo
simulado**: sin ESP32 construido, el camino automático de las lecturas quedaba sin
demostrar. Se escribió `scripts/simulador_dispositivo.py`, que **ocupa el lugar del
dispositivo**: se autentica con la clave del módulo de adquisición (`X-Device-Key`) y
publica lecturas por el mismo endpoint, con el mismo cuerpo y la misma validación que
usará el firmware, de modo que el servicio no distingue una lectura simulada de una
real. La clave se lee del `.env` y nunca se imprime.

**Verificación 1 — envío normal y alerta.** Contra el servicio local en modo de
demostración (sin escribir en la base real), un ciclo de las siete variables con el pH
forzado a 4,3:

| Comprobación | Resultado |
|---|---|
| Lecturas almacenadas por el servicio | **7 de 7** (201) |
| Estado evaluado de las seis variables con rango | `dentro` |
| Estado del pH forzado (rango 5,5 a 6,5) | **`bajo`** → genera la alerta |
| Variable sin rango configurado (`nivel_agua`) | `sin_rango`, sin alerta inventada |

**Verificación 2 — arranque en frío.** Se inició el simulador **antes** que el servicio
y el servicio se levantó cuatro segundos después. El primer ciclo no pudo enviar y las
lecturas **quedaron en la memoria del dispositivo**; en el ciclo siguiente se
**recuperaron con su valor original** (pH 6,31 y EC 1,57) y el resumen cerró con cero
lecturas sin enviar. Es el comportamiento que debe implementar el firmware y que la
tutoría señaló como riesgo (observación B-4).

**Verificación 3 — reglas del servicio.** El conjunto de pruebas automatizadas quedó en
**87 casos aprobados** en 3,27 s, incluidos los dos que fijan la regla de la alerta: una
lectura fuera de rango genera **exactamente una** alerta y una lectura dentro del rango
no genera ninguna. *(Al cierre de la sesión, con las tres pruebas de trazabilidad del
apartado 9, el conjunto queda en 90 casos.)*

### 8.1 Consumo de la base de datos

Cada envío escribe **siete documentos** (uno por variable) más la alerta cuando
corresponde. La capa gratuita de Cloud Firestore admite **20 000 escrituras y 50 000
lecturas por día**, 1 GiB almacenado y 10 GiB de salida al mes
([cuotas y límites](https://docs.cloud.google.com/firestore/quotas)).

| Intervalo | Documentos por día | % de la cuota de escritura |
|---|---|---|
| 30 segundos | 20 160 | **101 % — la excede** |
| 1 minuto | 10 080 | 50 % |
| **5 minutos** | **2 016** | **10 %** |
| 10 minutos | 1 008 | 5 % |

**Decisión:** el intervalo de referencia del prototipo se fija en **cinco minutos**, que
consume una décima parte de la cuota y deja margen para las alertas y las consultas del
panel. El almacenamiento no es el factor limitante: unos 30 MB al mes.

El detalle, el guion de la demostración y las pruebas quedaron en
`docs/16_SIMULADOR_DEL_DISPOSITIVO.md`.

---

## 9. Observaciones de redacción atendidas

Además de la verificación de los antecedentes, se resolvieron las observaciones de
coherencia interna del documento. Cada una obligó a **decidir**, no solo a redactar:

| # | Observación de la tutoría | Decisión tomada |
|---|---|---|
| **A-1** | El contexto de ubicación y clima (Open-Meteo y geolocator) no responde a ningún requisito | Se declara **fuera del alcance evaluado**: se conserva como funcionalidad complementaria del proyecto acumulativo, sin requisito ni criterio de aceptación, y se retira de la categoría «Could» |
| **A-2** | «Correo» y «Excel/PDF» figuraban como «Could» en una tabla de capacidades fuera de alcance | Se declaran **capacidades diferidas** (trabajo futuro) y el título de la tabla distingue unas de otras: tres excluidas y dos diferidas |
| **A-3** | RF-04 era «Could», pero RF-09 y el diccionario dependen de él | El catálogo de las siete variables se declara **dato inicial del sistema** —vive en la definición del servicio y se carga con los datos de demostración—, de modo que RF-04 pasa a «Should» y nada depende de un requisito diferido |
| **A-6** | El apartado 2.4.1 justificaba el patrón con el RNF-07, que decía otra cosa | El RNF-07 se alinea con lo que efectivamente justifica: contrato versionado, formato único de error y módulos con responsabilidades separadas |
| **A-7** | RNF-02, RNF-07 y RNF-08 tenían método de inspección, no métrica | Los tres pasan a tener **métrica verificable**: cero credenciales en el repositorio y su historial, 100 % de respuestas 401 y 403 donde corresponde, cinco colecciones cerradas al cliente anónimo, 28 operaciones en el contrato y 100 % de lecturas con origen, autor y marca de tiempo |
| **A-8** | El entregable solo detallaba la colección `lecturas` | Se describen las demás colecciones del modelo documental con sus campos: `modulos_cultivo`, `perfiles_cultivo`, `rangos`, `alertas` y `usuarios` |
| **A-9** | Faltaban las versiones del servicio y el despliegue decía «previsto» | Se consignan **FastAPI 0.141.1, uvicorn 0.52.4 y firebase-admin 7.5.0** sobre Python 3.13, y se nombra **Render en capa gratuita** y Firebase Hosting, que son las plataformas en uso |
| **A-10** | El contrato del entregable no incluía las rutas de perfiles | Se agrega la fila de `/api/v1/perfiles` y se reproduce el contrato real de la versión 1 |

**Trazabilidad de quién registró la lectura (B-2).** El RNF-08 pedía conservar el
dispositivo o el usuario que registró cada lectura, y el modelo solo guardaba el
origen. Se incorporó el campo `registrado_por`, que **resuelve el servidor**: en el
registro manual guarda el identificador del usuario de la sesión y en el envío del
módulo de adquisición queda nulo, porque la lectura ya está identificada por su módulo
y su origen automático. El contrato rechaza que el cliente declare ese campo, de modo
que nadie puede atribuir una medición a otra persona. La decisión se acompaña de
**tres pruebas nuevas**: el conjunto del servicio queda en **90 casos aprobados**.

El detalle de cada cambio, con los archivos regenerados, está en el plan de acción
(`Recomendaciones E1 - plan de accion.md`) y en el informe de verificación
(`docs/15_VERIFICACION_DE_LOS_ANTECEDENTES.md`).

---

## 10. Próximos pasos

| # | Tarea | Cuándo |
|---|---|---|
| 1 | Crear módulos, perfiles y rangos reales en la base publicada y ensayar el guion del E2 | Antes del sábado 26 |
| 2 | Implementar en el servicio las operaciones de administración de usuarios (RF-02 y B-1) | Antes del sábado 26 |
| 3 | Cerrar A-4 (ámbito del módulo piloto), A-11 y A-12 con el tutor | Durante la semana |
| 4 | Guion de la demostración y plan de contingencia para la defensa | Antes del 13/10 |

---

*Bitácora de la sesión del martes 22 de septiembre de 2026. Los datos citados en los
apartados 3 y 4 provienen de los documentos originales de cada antecedente y de la
verificación registrada en `docs/15_VERIFICACION_DE_LOS_ANTECEDENTES.md`.*
