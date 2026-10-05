# Nota de corrección — Tabla 3 del entregable E3

Documento interno de trabajo. No forma parte de la monografía.
Registra una corrección hecha **después** de la entrega del E3, con la fecha y el motivo.

**Entregable:** E3 · Checkpoint técnico — subido a Moodle el **2 de octubre de 2026 a las 23:14**.
**Corrección:** **4 de octubre de 2026**, por la mañana.

---

## 1. Qué se corrigió

La Tabla 3, «Puntos críticos del proceso actual», en su tercera fila —«Detección tardía de los valores
fuera de rango»—, en la celda del dato del contexto que lo evidencia.

**Es la única celda que cambió en todo el documento.** Se compararon las dos versiones celda por celda
con `_diagnostico/comparar_tabla_3.py`: las filas 1 y 2 de la misma tabla, los demás apartados, las
demás tablas, las figuras y los índices quedaron iguales. El documento sigue teniendo 67 páginas.

### Lo que decía en la versión subida

> Las desviaciones se advertían por su efecto sobre las plantas: las plántulas se estresaban o caían
> (comunicación personal, 2026). Es decir, el aviso llegaba cuando el daño ya se había producido, que
> es precisamente lo que un sistema de alerta temprana evita

### Lo que dice en la versión corregida

> Las desviaciones se advertían por su efecto sobre las plantas: las plántulas se estresaban o caían
> (comunicación personal, 2026), de modo que el aviso llegaba cuando el daño ya se había producido,
> que es precisamente lo que un sistema de alerta temprana evita. Los valores que se detectaron tarde
> quedaron consignados de forma puntual en el informe: el pH llegó a 5,8 en el sistema de raíz
> flotante y a 5,6 en el NFT, la conductividad eléctrica descendió 0,1 mS/cm y la temperatura de la
> solución alcanzó 26 °C (Santos Navarro, 2020).

## 2. Por qué se corrigió

La tutoría pidió que los puntos críticos quedaran respaldados con **los números del piloto** y no sólo
con la afirmación. Las filas 1 y 2 ya traían sus datos —las veintiuna mediciones semanales, la
ausencia de serie histórica— y la fila 3 era la única que quedaba sin cifras.

El dato faltante estaba en el informe del ensayo previo (Santos Navarro, 2020):

| Variable | Valor registrado en el piloto |
|---|---|
| pH | 5,8 en raíz flotante y 5,6 en el NFT |
| Conductividad eléctrica | descenso de 0,1 mS/cm |
| Temperatura de la solución | 26 °C |

## 3. Por qué no se volvió a subir a Moodle

La corrección se hizo al día siguiente del cierre, mientras se instalaba el software para leer las
lecturas de los sensores y el equipo se reinició, lo que hizo perder el trabajo de esa celda. Volver a
subir el archivo habría dado la impresión de una entrega fuera de plazo, así que **se decidió no
resubirlo** y presentar el cambio en la tutoría del viernes 9 de octubre, con las dos versiones a la
vista.

**Consecuencia asumida:** el docente corrige lo que está cargado en la plataforma, así que este
documento no recibirá devolución formal. El archivo corregido se lleva igualmente a la carpeta de
SharePoint del módulo, junto con su nota, para que el cambio quede a la vista.

## 4. Dónde están las dos versiones

| Versión | Archivo |
|---|---|
| La subida a Moodle el 2/10 | `_respaldos/Santos_Freddy_E3-antes-de-la-tabla-3.docx` |
| La corregida (vigente) | `Santos_Freddy_E3.docx` y `.pdf` en la raíz del proyecto |
| Copia versionada en el repositorio | `docs/Santos_Perfil_Proyecto_E3.docx` y `.pdf` |

Confirmación en el historial del repositorio: `2d2cca5` — «Tabla 3 con los numeros del piloto que
pedia la tutoria».

## 5. Cómo se comprueba

```
python _diagnostico/comparar_tabla_3.py
```

El programa abre las dos versiones, muestra la tabla completa de cada una y lista las celdas que
difieren. La salida esperada es una sola diferencia: fila 4, columna 3.
