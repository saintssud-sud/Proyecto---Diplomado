# Verificación de los antecedentes institucionales

**Proyecto:** SI.G.VA.C.H. · Grupo 3 · Freddy Carlo Santos Navarro
**Fecha:** 22 de septiembre de 2026
**Motivo:** comprobar, contra los documentos originales, cada afirmación que la
monografía y el entregable atribuyen a los dos antecedentes de la Universidad
Autónoma "Juan Misael Saracho".

> Este documento responde a la observación de la tutoría sobre las **inconsistencias
> internas** entre lo que se afirma y lo que las fuentes respaldan. Toda afirmación
> citada en la monografía y en el entregable quedó contrastada con el apartado
> correspondiente de la fuente, y las que no se sostenían fueron corregidas.

---

## 1. Fuentes verificadas

| N.º | Fuente | Archivo revisado | Extensión |
|---|---|---|---|
| 1 | **Santos Navarro, C. M. (2020)**. *Comparación del cultivo de la espinaca (Spinacia oleracea L.) en el sistema hidropónico NFT y el sistema hidropónico de raíz flotante*. Tesis de licenciatura, UAJMS. | `41644_MARCO_TEORICO.pdf` | 58 páginas |
| 2 | **Tejerina Pinto, A. D. (2018)**. *Hidroponía de raíz flotante en dos variedades de lechuga con bajo costo y diferentes niveles de oxigenación manual y automatizada*. Tesis de licenciatura, UAJMS. | `39483_MARCO_TEORICO.pdf` | 73 páginas |

## 2. Método

1. Se extrajo el texto íntegro de cada documento (`pdftotext -layout`) a los archivos
   `verificacion_antecedentes/santos_navarro_2020.txt` y
   `verificacion_antecedentes/tejerina_2018.txt`, para poder repetir cualquier
   búsqueda sobre el texto completo y no sobre una lectura parcial.
2. Se localizaron los apartados que respaldan (o contradicen) cada afirmación citada.
3. Se anotó el veredicto: **confirmado**, **impreciso** o **no confirmado**.
4. Se corrigieron los tramos imprecisos o no confirmados en la monografía, en los
   borradores por capítulo y en el entregable, y se regeneraron sus archivos.

---

## 3. Santos Navarro (2020): qué se verificó

| Afirmación del documento | Lo que dice la fuente | Veredicto |
|---|---|---|
| Comparó el cultivo de **espinaca** (*Spinacia oleracea* L.) en los sistemas **NFT y de raíz flotante**. | §1.1: "Cultivo de la espinaca… Nombre científico: *Spinacia oleracea* L.". §2.2: "se comparó el sistema hidropónico NFT con el sistema hidropónico de raíz flotante… para determinar cuál de estos tratamientos da el mayor rendimiento en el cultivo de la espinaca". | **Confirmado** |
| Realizó **seguimiento del pH, de la conductividad eléctrica y de la temperatura de la solución** mediante **rangos de referencia**. | §1.2.6.3 a §1.2.6.4: rangos de pH 5,0 a 6,5 y de CE 1,5 a 2,5 mS/cm, con tablas de referencia; §2.5.10 a §2.5.12: "Se tomaron datos luego de preparar la solución nutritiva… alcanzando un pH de 5,8 en el sistema hidropónico de raíz flotante y un pH 5,6 en el sistema hidropónico de NFT"; "Se tomaron datos de la conductividad eléctrica, teniendo como resultado cambios a partir del tercer día, con reducción de 0.1 ms/cm"; "Se tomaron datos de la temperatura por día de la solución nutritiva teniendo como resultado 26 °C, que fue la temperatura más alta en el ciclo del cultivo". | **Confirmado** |
| Renovó la solución **cada 15 días** ante sus desviaciones. | §2.5.9: "Para este experimento o investigación se renovó la solución nutritiva de cada tratamiento, **cada 15 días** debido al descenso o aumento del pH y de la conductividad eléctrica en los tratamientos". | **Confirmado** (literal) |
| Las mediciones se hicieron con **instrumentos portátiles**. | §2.1.7, materiales de laboratorio: "pH metro", "Conductímetro"; §1.2.6.4: "medidor portátil denominado conductímetro". | **Confirmado** |
| Las variables de la solución **"no quedaron registradas en el informe"** y **"la información medida se perdió"**. | El informe **sí** consigna los rangos de referencia y valores puntuales (pH 5,8 y 5,6; reducción de 0,1 mS/cm; 26 °C). Lo que no conserva es **la serie completa de las lecturas**. | ⚠️ **Impreciso** |
| La solución "se renovaba **al concluir el período de desarrollo**". | Contradice §2.5.9, que documenta la renovación **cada 15 días**. | ⚠️ **No coincide** |
| Tabla 1: variables del antecedente = "**Rendimiento**: peso, **volumen** y desarrollo foliar". | La palabra *volumen* no figura como variable. Las variables de respuesta son §2.7 y §3.1: germinación, largo de hoja, ancho de hoja, número de hojas, peso de hojas y rendimiento (kg/m²). | ⚠️ **Impreciso** |
| "No es posible… **saber con qué instrumento se midió**". | §2.1.7 **sí** enumera los instrumentos (pH metro y conductímetro). | ⚠️ **Impreciso** |

> **Observación para la defensa.** El aparato experimental de este antecedente es el
> más cercano al proyecto: mide y corrige las mismas variables que gestiona
> SI.G.VA.C.H., y lo hace **a mano y sin conservar la serie**. Eso es exactamente el
> vacío que el sistema cubre, y ahora está respaldado por el propio informe, no solo
> por el testimonio del autor.

---

## 4. Tejerina Pinto (2018): qué se verificó

| Afirmación del documento | Lo que dice la fuente | Veredicto |
|---|---|---|
| Estudió la **lechuga** en un sistema hidropónico de **raíz flotante**. | Título y objetivos; §2.1.1 a §2.1.9 dedicados a *Lactuca sativa* L.; §2.1.4.1 "Grand Rapids Tbr" y §2.1.4.2 "Morada Criolla". | **Confirmado** |
| Dos variedades: **Grand Rapids Tbr** y **Morada Criolla**. | §3.3.3, factor B: "B1: Lechuga Morada Criolla", "B2: Lechuga Grand Rapids Tbr"; objetivo general: "lechuga Grand Rapids Tbr y lechuga Morada Criolla". | **Confirmado** (grafía de la fuente; aparecen variantes internas como "Grand Rapids Tb" y "Criolla Morada") |
| Distintos niveles de **oxigenación manual y automatizada**. | §3.3.3, factor A: "A1: Oxigenación manual una vez al día", "A2: Oxigenación manual dos vez al día", "A3: Oxigenación Automatizada". | **Confirmado** |
| Evaluó **prendimiento, número y tamaño de hojas, largo de raíces y diámetro del tallo**. | §3.3.4: "Porcentaje de prendimiento, Tamaño de hoja, Cantidad de hojas por planta, Tamaño de raíz, Diámetro del tallo"; §3.6.4 "Largo de raíces"; §3.6.5 "Diámetro del tallo". | **Confirmado** |
| El trabajo **no aborda la gestión de esas variables mediante una herramienta informática**. | No hay software ni sistema informático en el documento: §3.6.1 "se contó de forma manual"; §3.6.3 y §3.6.5 mediciones con calibre y regla. | **Confirmado** |
| Tabla 1: "Registro manual; sin herramienta informática". | Igual que el punto anterior. | **Confirmado** |

---

## 5. Correcciones aplicadas

| Documento | Tramo | Corrección |
|---|---|---|
| Monografía | §1.1.3, párrafo de antecedentes | Se retira la nota de revisión sobre la grafía de las variedades (verificada en la fuente). Se precisa que el análisis del antecedente se concentró en las **variables de respuesta** del cultivo. |
| Monografía | §1.1.3, **Tabla 1** | Fila de Santos Navarro: se reemplaza "peso, volumen y desarrollo foliar" por las variables reales y se corrige el vacío declarado: el informe **sí** documenta la solución, pero **no conserva la serie de las lecturas**. |
| Monografía | §1.1.3, párrafo de síntesis | Se reemplaza "las variables… no quedaron registradas en el informe" por la descripción verificada, **con los valores del informe** (pH 5,8 y 5,6; −0,1 mS/cm; 26 °C). |
| Monografía | §1.2, párrafo del ensayo previo | Se nombra el cultivo (espinaca), se precisa que la serie no se conservó y se corrige la renovación de la solución a **cada quince días**, como documenta el informe. |
| Monografía | §1.2, puntos críticos 1 y 2 | "no se conserva la serie de las mediciones"; se retira el argumento del instrumento, que sí figura en el informe. |
| Monografía | Bibliografía, nota de comunicación personal | Se precisa que lo no conservado es la serie de lecturas, no toda la información. |
| Borradores por capítulo | `Capitulo 1 - Introduccion`, `Capitulo I - Mejorado` | Se retiran las notas de revisión y se precisa el registro del antecedente. |
| Entregable E1 | Párrafo de antecedentes | Se describe lo verificado: medición con pHmetro y conductímetro, corrección en el momento y serie no conservada. |
| Entregable E1 | Tabla de puntos críticos, puntos 1 y 2 | Punto 1: renovación **cada quince días** y serie no conservada. Punto 2: se retira el argumento del instrumento y se precisa qué no se puede reconstruir. |

**Archivos regenerados:** `Monografia - Borrador Completo (Diplomado) - institucional.docx`,
`Santos_Perfil_Proyecto_E1.docx`, `Santos_Perfil_Proyecto_E1.pdf` (39 páginas) y sus copias
en `Proyecto SIGVACH/docs/`.

---

## 6. Pendientes que dependen del autor

| # | Punto | Por qué |
|---|---|---|
| 1 | **Renovación de la solución:** el informe documenta **cada 15 días**; la comunicación personal indicó "al concluir el período de desarrollo". | Son dos datos distintos para el mismo ensayo. Se dejó el dato documentado y conviene confirmar con el autor del ensayo si hubo también una renovación total al final. |
| 2 | **Ámbito del módulo piloto.** El entregable menciona "el módulo de cultivo piloto" y no existe un módulo físico construido. | Hay que decidir cómo nombrarlo (el ensayo de referencia, el ámbito de la Facultad, un módulo previsto) para el objetivo general y el apartado 1.2, conforme a la recomendación A-4 de la tutoría. |

---

*Documento de trabajo. La extracción de texto y las búsquedas quedan guardadas en
`verificacion_antecedentes/` para poder repetir la comprobación en cualquier momento.*
