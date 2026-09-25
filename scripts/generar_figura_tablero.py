# -*- coding: utf-8 -*-
"""Dibuja la captura del tablero Kanban a partir de docs/TABLERO.md.

La plantilla del entregable pide una captura del tablero al cierre de la semana.
La primera version de esa figura se dibujo con las tarjetas escritas a mano
dentro del programa, y por eso quedo congelada en la Semana 1 mientras el
tablero seguia avanzando: el pie de figura decia «Semana 3» y la imagen mostraba
once tarjetas terminadas.

Aqui las tarjetas no se escriben: se leen del tablero versionado. La figura se
regenera en cada entrega y no puede volver a desincronizarse. Antes de dibujar,
el programa comprueba que el tablero sea coherente —que ninguna tarea este en dos
columnas a la vez y que su resumen coincida con lo que hay en las columnas— y se
detiene si no lo es.

Uso:
    python generar_figura_tablero.py
"""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent


def raiz_del_espacio(inicio: Path) -> Path:
    """Encuentra la raíz del espacio de trabajo desde donde esté el programa.

    El mismo programa vive en la raíz del espacio y en `Proyecto SIGVACH/scripts/`
    para quedar versionado, así que no puede dar por hecho dónde está: busca hacia
    arriba la carpeta que contiene el tablero.
    """
    for candidato in (inicio, *inicio.parents):
        if (candidato / "Proyecto SIGVACH" / "docs" / "TABLERO.md").exists():
            return candidato
    raise SystemExit("No se encontró Proyecto SIGVACH/docs/TABLERO.md desde %s" % inicio)


ESPACIO = raiz_del_espacio(RAIZ)
TABLERO = ESPACIO / "Proyecto SIGVACH" / "docs" / "TABLERO.md"
SALIDA = ESPACIO / "Figuras"

VERDE = (57, 181, 74)
VERDE_CLARO = (232, 245, 234)
AZUL = (21, 101, 192)
AZUL_CLARO = (230, 240, 250)
GRIS = (110, 114, 120)
GRIS_CAJA = (240, 241, 243)
GRIS_BORDE = (170, 175, 182)
TEXTO = (45, 45, 45)
BLANCO = (255, 255, 255)
NEGRO_SUAVE = (90, 94, 100)


# ---------------------------------------------------------------------------
# Utilidades de dibujo
# ---------------------------------------------------------------------------

def fuente(tamano: int, negrita: bool = False) -> ImageFont.FreeTypeFont:
    archivo = "arialbd.ttf" if negrita else "arial.ttf"
    return ImageFont.truetype("C:/Windows/Fonts/" + archivo, tamano)


def ancho_texto(dibujo: ImageDraw.ImageDraw, texto: str, tamano: int, negrita: bool = False) -> float:
    caja = dibujo.textbbox((0, 0), texto, font=fuente(tamano, negrita))
    return caja[2] - caja[0]


def texto_centrado(dibujo, texto, x, y, ancho, tamano=18, color=TEXTO, negrita=False) -> None:
    tipografia = fuente(tamano, negrita)
    caja = dibujo.textbbox((0, 0), texto, font=tipografia)
    dibujo.text((x + (ancho - (caja[2] - caja[0])) / 2, y), texto, font=tipografia, fill=color)


def caja(dibujo, x, y, ancho, alto, relleno=BLANCO, borde=GRIS_BORDE, radio=12, grosor=2) -> None:
    dibujo.rounded_rectangle([x, y, x + ancho, y + alto], radius=radio, fill=relleno,
                             outline=borde, width=grosor)


def flecha(dibujo, x1, y1, x2, y2, color=GRIS, grosor=2, punta=11) -> None:
    dibujo.line([x1, y1, x2, y2], fill=color, width=grosor)
    dibujo.polygon([(x2, y2), (x2 - punta, y2 - punta * 0.55), (x2 - punta, y2 + punta * 0.55)], fill=color)


def recortar(texto: str, limite: int) -> str:
    """Acorta un titulo largo sin partir palabras, para las tarjetas compactas."""
    if len(texto) <= limite:
        return texto
    corte = texto[:limite].rsplit(" ", 1)[0]
    return corte + "…"


def envolver(dibujo, texto: str, ancho_max: float, tamano: int, max_lineas: int) -> list[str]:
    """Reparte el texto en lineas que quepan en el ancho dado."""
    lineas: list[str] = []
    actual = ""
    for palabra in texto.split():
        prueba = (actual + " " + palabra).strip()
        if ancho_texto(dibujo, prueba, tamano) <= ancho_max or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    if len(lineas) > max_lineas:
        sobrantes = lineas[max_lineas - 1:]
        lineas = lineas[:max_lineas - 1] + [recortar(" ".join(sobrantes), len(" ".join(sobrantes)) - 1)]
    return lineas


# ---------------------------------------------------------------------------
# Lectura del tablero
# ---------------------------------------------------------------------------

def celdas(linea: str) -> list[str]:
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def sin_marcas(texto: str) -> str:
    """Quita las marcas de énfasis de Markdown: en la figura se imprimen literales."""
    return texto.replace("**", "").replace("`", "").strip()


def es_fila_de_tabla(linea: str) -> bool:
    return linea.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", linea.strip())


class Tablero:
    def __init__(self, ruta: Path) -> None:
        self.ruta = ruta
        self.marco = ""
        self.wip = 2
        self.backlog: list[dict] = []
        self.en_curso: list[dict] = []
        self.hecho: list[tuple[str, list[dict]]] = []
        self.semana_cierre = ""
        self.fecha_cierre = ""
        self.resumen: tuple[int, int, int] | None = None
        self._leer()

    def _leer(self) -> None:
        lineas = self.ruta.read_text(encoding="utf-8").splitlines()
        seccion = None
        semana_actual: str | None = None

        for linea in lineas:
            texto = linea.strip()

            if texto.startswith("**Marco de trabajo:**"):
                self.marco = texto.split("**", 2)[-1].lstrip(":").split(",")[0].strip()
            if texto.startswith("**Límite de trabajo en curso"):
                numero = re.search(r"(\d+)", texto.split(":", 1)[-1])
                if numero:
                    self.wip = int(numero.group(1))
            if texto.startswith("## 📊"):
                fecha = re.search(r"al (.+)$", texto)
                if fecha:
                    self.fecha_cierre = fecha.group(1).strip()
            if texto.startswith("**Estado al cierre de la Semana"):
                coincidencia = re.search(
                    r"Semana (\d+):\**\s*(\d+) tareas terminadas\s*·\s*(\d+) en curso\s*·\s*(\d+) en el backlog",
                    texto,
                )
                if coincidencia:
                    self.semana_cierre = "Semana " + coincidencia.group(1)
                    self.resumen = (int(coincidencia.group(2)), int(coincidencia.group(3)),
                                    int(coincidencia.group(4)))
            if texto.startswith("## 📋"):
                seccion, semana_actual = "backlog", None
                continue
            if texto.startswith("## 🔄"):
                seccion, semana_actual = "en_curso", None
                continue
            if texto.startswith("## ✅"):
                seccion, semana_actual = "hecho", None
                continue
            if texto.startswith("### Semana"):
                semana_actual = texto.lstrip("# ").strip()
                self.hecho.append((semana_actual, []))
                continue
            if not es_fila_de_tabla(texto):
                continue

            partes = celdas(texto)
            if partes and partes[0] == "ID":
                continue
            if not partes or not re.match(r"^T-\d+", partes[0]):
                continue

            tarea = {
                "id": partes[0],
                "titulo": sin_marcas(partes[1]),
                "resto": [sin_marcas(p) for p in partes[2:]],
            }
            if seccion == "backlog":
                self.backlog.append(tarea)
            elif seccion == "en_curso":
                self.en_curso.append(tarea)
            elif seccion == "hecho" and self.hecho:
                self.hecho[-1][1].append(tarea)

    @property
    def total_hecho(self) -> int:
        return sum(len(tareas) for _, tareas in self.hecho)

    def comprobar(self) -> None:
        """Verifica que el tablero sea coherente antes de dibujarlo."""
        vistas: dict[str, list[str]] = {}
        for tarea in self.backlog:
            vistas.setdefault(tarea["id"], []).append("Backlog")
        for tarea in self.en_curso:
            vistas.setdefault(tarea["id"], []).append("En curso")
        for _, tareas in self.hecho:
            for tarea in tareas:
                vistas.setdefault(tarea["id"], []).append("Hecho")

        repetidas = {i: c for i, c in vistas.items() if len(c) > 1}
        if repetidas:
            detalle = " · ".join("%s en %s" % (i, " y ".join(c)) for i, c in repetidas.items())
            raise SystemExit("Tablero incoherente: una tarea no puede estar en dos columnas (%s)" % detalle)

        if self.resumen is None:
            raise SystemExit("No se encontro la linea de estado al cierre de la semana en el tablero.")

        contado = (self.total_hecho, len(self.en_curso), len(self.backlog))
        if contado != self.resumen:
            raise SystemExit(
                "Tablero incoherente: las columnas suman %d terminadas, %d en curso y %d en el backlog, "
                "pero el resumen declara %d, %d y %d." % (contado + self.resumen)
            )
        if len(vistas) != sum(contado):
            raise SystemExit("Tablero incoherente: hay tareas sin columna o columnas sin tareas.")


# ---------------------------------------------------------------------------
# Figura
# ---------------------------------------------------------------------------

ANCHO, ALTO = 1500, 1020
MARGEN = 36
SEPARACION = 24
Y_COLUMNAS = 100
ALTO_COLUMNA = 850
ALTO_ENCABEZADO = 52


def tarjeta(dibujo, x, y, ancho, lineas, detalles, tamano, color_borde, alto_linea=22,
            tamano_detalle=13):
    alto = 10 + alto_linea * len(lineas) + 18 * len(detalles) + 8
    caja(dibujo, x, y, ancho, alto, BLANCO, color_borde, radio=8, grosor=2)
    desplazamiento = 10
    for linea in lineas:
        dibujo.text((x + 14, y + desplazamiento), linea, font=fuente(tamano), fill=TEXTO)
        desplazamiento += alto_linea
    for detalle in detalles:
        dibujo.text((x + 14, y + desplazamiento), detalle, font=fuente(tamano_detalle), fill=NEGRO_SUAVE)
        desplazamiento += 18
    return alto


def figura_tablero(tablero: Tablero) -> Path:
    imagen = Image.new("RGB", (ANCHO, ALTO), BLANCO)
    dibujo = ImageDraw.Draw(imagen)

    texto_centrado(dibujo, "Tablero de tareas SIGVACH — Kanban", 0, 26, ANCHO, 26, TEXTO, True)
    texto_centrado(
        dibujo,
        "%s · Límite de trabajo en curso: %d tarjetas" % (tablero.marco, tablero.wip),
        0, 62, ANCHO, 18, GRIS,
    )

    ancho_backlog, ancho_curso = 330, 330
    ancho_hecho = ANCHO - 2 * MARGEN - 2 * SEPARACION - ancho_backlog - ancho_curso
    columnas = (
        ("BACKLOG  (%d tarjetas)" % len(tablero.backlog), ancho_backlog, GRIS_CAJA, GRIS_BORDE),
        ("EN CURSO  (límite: %d)" % tablero.wip, ancho_curso, AZUL_CLARO, AZUL),
        ("HECHO  (%d tarjetas)" % tablero.total_hecho, ancho_hecho, VERDE_CLARO, VERDE),
    )

    limites = []
    for indice, (titulo, ancho_columna, relleno, borde) in enumerate(columnas):
        x = MARGEN + sum(c[1] for c in columnas[:indice]) + indice * SEPARACION
        limites.append((x, ancho_columna, borde))
        caja(dibujo, x, Y_COLUMNAS, ancho_columna, ALTO_COLUMNA, GRIS_CAJA, GRIS_BORDE, radio=14, grosor=2)
        caja(dibujo, x, Y_COLUMNAS, ancho_columna, ALTO_ENCABEZADO, relleno, borde, radio=14, grosor=2)
        tamano_titulo = 19 if ancho_texto(dibujo, titulo, 19, True) <= ancho_columna - 24 else 16
        texto_centrado(dibujo, titulo, x, Y_COLUMNAS + 16, ancho_columna, tamano_titulo, TEXTO, True)
        if indice < 2:
            flecha(dibujo, x + ancho_columna + 4, Y_COLUMNAS + ALTO_COLUMNA / 2,
                   x + ancho_columna + 20, Y_COLUMNAS + ALTO_COLUMNA / 2)

    tope = Y_COLUMNAS + ALTO_ENCABEZADO + 16
    fondo = Y_COLUMNAS + ALTO_COLUMNA - 12

    # --- Backlog: caben pocas tarjetas, con el titulo completo y su prioridad ---
    x, ancho_columna, borde = limites[0]
    y = tope
    for tarea in tablero.backlog:
        lineas = envolver(dibujo, tarea["titulo"], ancho_columna - 52, 16, 3)
        detalle = " · ".join(t for t in tarea["resto"] if t)
        alto = tarjeta(dibujo, x + 12, y, ancho_columna - 24, lineas, [detalle], 16, borde)
        y += alto + 10

    # --- En curso: con el responsable y la fecha de inicio ---
    x, ancho_columna, borde = limites[1]
    y = tope
    for tarea in tablero.en_curso:
        lineas = envolver(dibujo, tarea["titulo"], ancho_columna - 52, 16, 3)
        detalle = " · ".join(t for t in tarea["resto"] if t)
        alto = tarjeta(dibujo, x + 12, y, ancho_columna - 24, lineas, [detalle], 16, borde)
        y += alto + 10

    # --- Hecho: una tarjeta compacta por tarea, agrupadas por semana ---
    x, ancho_columna, borde = limites[2]
    alto_subtitulo = 26
    separacion_tarjeta = 3
    disponible = fondo - tope - alto_subtitulo * len(tablero.hecho)
    total_tarjetas = tablero.total_hecho
    alto_tarjeta = min(
        22,
        int((disponible - separacion_tarjeta * max(0, total_tarjetas - 1)) / max(1, total_tarjetas)),
    )
    if alto_tarjeta < 15:
        raise SystemExit(
            "No caben %d tarjetas terminadas en la columna: habria que acortar la lista "
            "o agrupar las semanas anteriores." % total_tarjetas
        )

    y = tope
    for nombre_semana, tareas in tablero.hecho:
        dibujo.text((x + 14, y + 4), "%s · %d tarjetas" % (nombre_semana, len(tareas)),
                    font=fuente(14, True), fill=borde)
        y += alto_subtitulo
        for tarea in tareas:
            caja(dibujo, x + 12, y, ancho_columna - 24, alto_tarjeta, BLANCO, borde, radio=6, grosor=2)
            etiqueta = "%s  %s" % (tarea["id"], tarea["titulo"])
            while ancho_texto(dibujo, etiqueta, 13) > ancho_columna - 56 and len(etiqueta) > 20:
                etiqueta = recortar(etiqueta, len(etiqueta) - 6)
            dibujo.text((x + 22, y + (alto_tarjeta - 15) / 2), etiqueta, font=fuente(13), fill=TEXTO)
            y += alto_tarjeta + separacion_tarjeta

    terminadas, en_curso, backlog = tablero.resumen
    texto_centrado(
        dibujo,
        "Estado al cierre de la %s (%s): %d tareas terminadas · %d en curso · %d en el backlog."
        % (tablero.semana_cierre, tablero.fecha_cierre, terminadas, en_curso, backlog),
        0, 958, ANCHO, 18, GRIS,
    )
    texto_centrado(
        dibujo,
        "Fuente: docs/TABLERO.md del repositorio del proyecto. La figura se regenera desde el tablero en cada entrega.",
        0, 986, ANCHO, 16, GRIS,
    )

    SALIDA.mkdir(exist_ok=True)
    destino = SALIDA / ("13-tablero-%s.png" % tablero.semana_cierre.lower().replace(" ", "-"))
    imagen.save(destino)
    return destino


def main() -> None:
    tablero = Tablero(TABLERO)
    tablero.comprobar()
    print("Tablero: %s" % TABLERO.relative_to(RAIZ))
    print("  Marco        : %s" % tablero.marco)
    print("  Backlog      : %d" % len(tablero.backlog))
    print("  En curso     : %d" % len(tablero.en_curso))
    print("  Hecho        : %d" % tablero.total_hecho)
    for nombre, tareas in tablero.hecho:
        print("      %-28s %2d" % (nombre, len(tareas)))
    print("  Coherencia   : correcta (ninguna tarea en dos columnas)")
    print("Figura generada: %s" % figura_tablero(tablero).relative_to(RAIZ))


if __name__ == "__main__":
    main()
