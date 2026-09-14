"""Convierte un documento Markdown a Word (.docx) con formato.

Uso:
    python scripts/md_a_docx.py docs/BITACORA_MARTES_2026-09-08.md docs/BITACORA_MARTES_2026-09-08.docx

    # Con el formato institucional del trabajo final (Arial 12, interlineado 1,5,
    # margenes de 4 y 3 cm, papel carta):
    python scripts/md_a_docx.py monografia.md monografia.docx --institucional

Genera una portada con logo (si existe assets/images/logo.png), estilos de
títulos, párrafos, listas, tablas y bloques de código.

La opción `--institucional` aplica el formato exigido por el *Formato para la
Elaboración del Trabajo Final de Diplomado*: los títulos quedan con los estilos
Título 1, 2 y 3 de Word, de modo que el índice de contenido y la numeración se
generen solos. Las páginas preliminares (portada, contratapa, hoja de aprobación,
hoja de advertencia, dedicatoria, agradecimientos e índices) se completan en Word:
la plantilla oficial describe su contenido.
"""
import os
import re
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


# ---------- utilidades de estilo ----------
VERDE = RGBColor(0x39, 0xB5, 0x4A)
VERDE_OSCURO = RGBColor(0x2E, 0x7D, 0x32)
GRIS = RGBColor(0x55, 0x55, 0x55)
AZUL_CODIGO = RGBColor(0x1F, 0x3B, 0x73)

# Ruta del logo (relativa a la raíz del proyecto)
LOGO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "images", "logo.png",
)


def _quitar_markdown(texto: str) -> str:
    """Limpia marcado Markdown básico (negrita, itálica, código, enlaces)."""
    texto = re.sub(r"\*\*(.+?)\*\*", r"\1", texto)  # **negrita**
    texto = re.sub(r"\*(.+?)\*", r"\1", texto)  # *itálica*
    texto = re.sub(r"`(.+?)`", r"\1", texto)  # `codigo`
    texto = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", texto)  # [texto](url)
    return texto.strip()


def _configurar_titulo_por_defecto(doc: Document) -> None:
    """Aplica el color verde de marca a los estilos de títulos."""
    for nombre, tamano in [("Heading 1", 17), ("Heading 2", 14), ("Heading 3", 12.5)]:
        try:
            estilo = doc.styles[nombre]
            estilo.font.color.rgb = VERDE_OSCURO
            estilo.font.name = "Calibri"
            estilo.font.size = Pt(tamano)
            estilo.font.bold = True
        except KeyError:
            pass


def _quitar_markdown(texto: str) -> str:
    """Limpia marcado Markdown básico (negrita, itálica, código, enlaces)."""
    texto = re.sub(r"\*\*(.+?)\*\*", r"\1", texto)  # **negrita**
    texto = re.sub(r"\*(.+?)\*", r"\1", texto)  # *itálica*
    texto = re.sub(r"`(.+?)`", r"\1", texto)  # `codigo`
    texto = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", texto)  # [texto](url)
    return texto.strip()


def _normalizar_logo() -> str | None:
    """Devuelve la ruta de un logo real (PNG). Convierte con Pillow si el
    archivo tiene extensión .png pero su contenido es JPEG."""
    if not os.path.exists(LOGO):
        return None
    with open(LOGO, "rb") as f:
        cabecera = f.read(3)
    if cabecera == b"\x89PN":  # PNG real
        return LOGO
    # Contenido no PNG (p. ej. JPEG con nombre .png): convertir a PNG real.
    try:
        from PIL import Image as PILImage

        tmp = os.path.join(os.path.dirname(LOGO), "_logo_real.png")
        with PILImage.open(LOGO) as im:
            im.save(tmp, "PNG")
        return tmp
    except Exception as e:  # noqa: BLE001
        print(f"Aviso: no se pudo normalizar el logo ({e}).")
        return None


def _agregar_portada(doc: Document, titulo_archivo: str, logo_real: str | None) -> None:
    """Agrega una portada con logo, nombre del proyecto y fecha."""
    # Fecha desde el nombre del archivo (p. ej. BITACORA_MARTES_2026-09-08)
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", titulo_archivo)
    fecha = ""
    if m:
        meses = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
        ]
        anio, mes, dia = m.groups()
        fecha = f"{int(dia)} de {meses[int(mes) - 1]} de {anio}"

    for _ in range(4):
        doc.add_paragraph()

    # Logo (si existe)
    if logo_real:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(logo_real, width=Inches(1.4))
        doc.add_paragraph()

    # Nombre del proyecto
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("SI.G.VA.C.H.")
    _configurar_fuente(run, tamano=30, negrita=True, color=VERDE)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Sistema de Gestión de Variables para Cultivos Hidropónicos")
    _configurar_fuente(run, tamano=13, color=GRIS)

    doc.add_paragraph()
    doc.add_paragraph()

    # Título del documento
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    titulo = titulo_archivo.replace(".docx", "").replace("_", " ")
    run = p.add_run(titulo)
    _configurar_fuente(run, tamano=20, negrita=True, color=VERDE_OSCURO)

    if fecha:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(fecha)
        _configurar_fuente(run, tamano=13, color=GRIS)

    # Salto de página para empezar el contenido
    doc.add_page_break()


def _es_fila_tabla(linea: str) -> bool:
    return linea.strip().startswith("|") and linea.strip().endswith("|")


def _parsear_fila_tabla(linea: str) -> list[str]:
    celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
    return [_quitar_markdown(c) for c in celdas]


def _es_separador_tabla(linea: str) -> bool:
    return bool(re.match(r"^\s*\|?[\s:|-]+\|?\s*$", linea)) and "-" in linea


def _configurar_fuente(run, tamano=11, negrita=False, color=None, mono=False):
    run.font.size = Pt(tamano)
    run.bold = negrita
    if mono:
        run.font.name = "Consolas"
        r = run._element.rPr
        rFonts = r.find(qn("w:rFonts"))
        if rFonts is not None:
            rFonts.set(qn("w:ascii"), "Consolas")
            rFonts.set(qn("w:hAnsi"), "Consolas")
    if color:
        run.font.color.rgb = color


def _es_imagen_vertical(ruta: str) -> bool:
    """Indica si la imagen es más alta que ancha, para elegir su ancho al insertarla."""
    try:
        from PIL import Image

        with Image.open(ruta) as imagen:
            ancho, alto = imagen.size
        return alto > ancho
    except Exception:
        return False


def _insertar_figura(doc, ruta: str, epigrafe: str, fuente: str, cuerpo: int) -> None:
    """Inserta una imagen centrada con su epígrafe debajo.

    El formato institucional pide el epígrafe **debajo** de la figura (a
    diferencia de las tablas, cuyo título va encima). El ancho se elige según la
    orientación: las imágenes verticales —los bocetos de pantalla— se insertan a
    7 cm para que no ocupen una página entera, y las horizontales a 14 cm, que es
    el ancho útil de la caja de texto.
    """
    ancho_cm = 7.0 if _es_imagen_vertical(ruta) else 14.0
    parrafo = doc.add_paragraph()
    parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    parrafo.add_run().add_picture(ruta, width=Cm(ancho_cm))

    if epigrafe:
        # El epígrafe llega como «Figura N. Descripción»: se destaca la
        # identificación y se deja la descripción en cursiva.
        texto_epigrafe = doc.add_paragraph()
        texto_epigrafe.alignment = WD_ALIGN_PARAGRAPH.CENTER
        identificacion, _, descripcion = epigrafe.partition(". ")
        run = texto_epigrafe.add_run(identificacion + ".")
        _configurar_fuente(run, tamano=11, negrita=True)
        if descripcion:
            run = texto_epigrafe.add_run(" " + descripcion)
            _configurar_fuente(run, tamano=11)
            run.italic = True

    if fuente:
        texto_fuente = doc.add_paragraph()
        texto_fuente.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = texto_fuente.add_run(fuente)
        _configurar_fuente(run, tamano=10, color=GRIS)
        run.italic = True


# ---------- construcción del documento ----------
def _configurar_titulos_institucionales(doc) -> None:
    """Ajusta los estilos de título al formato institucional.

    Se aplica después de la configuración por defecto del script, que escribe los
    títulos en otra familia tipográfica y en verde; el formato del trabajo final
    pide la misma familia del cuerpo y texto en negro.
    """
    for nombre, tamano in (
        ("Heading 1", 14),
        ("Heading 2", 13),
        ("Heading 3", 12),
        ("Heading 4", 12),
        ("Heading 5", 12),
    ):
        try:
            titulo = doc.styles[nombre]
        except KeyError:
            continue
        titulo.font.name = "Arial"
        titulo.font.size = Pt(tamano)
        titulo.font.bold = True
        titulo.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        titulo.paragraph_format.space_before = Pt(12)
        titulo.paragraph_format.space_after = Pt(6)
        titulo.paragraph_format.line_spacing = 1.5


def convertir(md_path: str, docx_path: str, formato_institucional: bool = False) -> None:
    with open(md_path, encoding="utf-8") as f:
        lineas = f.read().splitlines()

    doc = Document()

    # Tamaño del cuerpo: 12 puntos en el formato institucional, 11 en el resto.
    cuerpo = 12 if formato_institucional else 11

    if formato_institucional:
        # Formato institucional: papel carta y margenes de 4 cm a la izquierda y
        # 3 cm en el resto.
        seccion = doc.sections[0]
        seccion.left_margin = Cm(4)
        seccion.right_margin = Cm(3)
        seccion.top_margin = Cm(3)
        seccion.bottom_margin = Cm(3)
        seccion.page_width = Cm(21.59)
        seccion.page_height = Cm(27.94)

    # Estilo base
    estilo = doc.styles["Normal"]
    estilo.font.name = "Arial" if formato_institucional else "Calibri"
    estilo.font.size = Pt(cuerpo)
    if formato_institucional:
        estilo.paragraph_format.line_spacing = 1.5
        estilo.paragraph_format.space_after = Pt(8)

    # Portada (normaliza el logo por si el .png es en realidad JPEG)
    logo_real = _normalizar_logo()
    _agregar_portada(doc, os.path.basename(docx_path), logo_real)
    if logo_real and logo_real != LOGO and os.path.exists(logo_real):
        os.remove(logo_real)
    _configurar_titulo_por_defecto(doc)
    if formato_institucional:
        _configurar_titulos_institucionales(doc)

    i = 0
    while i < len(lineas):
        linea = lineas[i]
        texto = linea.rstrip()

        # Figura: ![Figura N. Descripción | Fuente: ...](ruta/de/la/imagen.png)
        figura = re.match(r"^!\[(?P<alt>[^\]]*)\]\((?P<ruta>[^)]+)\)\s*$", texto.strip())
        if figura:
            ruta_imagen = figura.group("ruta")
            epigrafe, _, fuente_texto = figura.group("alt").partition("|")
            if os.path.exists(ruta_imagen):
                _insertar_figura(
                    doc,
                    ruta_imagen,
                    epigrafe.strip(),
                    fuente_texto.strip(),
                    cuerpo,
                )
            else:
                # Si la imagen no está, se deja constancia en el documento en
                # lugar de romper la conversión.
                aviso = doc.add_paragraph()
                aviso.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = aviso.add_run("[Falta la imagen: %s]" % ruta_imagen)
                _configurar_fuente(run, tamano=cuerpo, color=RGBColor(0xC0, 0x00, 0x00))
            i += 1
            continue

        # Tabla
        if _es_fila_tabla(texto):
            filas = []
            while i < len(lineas) and (_es_fila_tabla(lineas[i]) or _es_separador_tabla(lineas[i])):
                if _es_fila_tabla(lineas[i]) and not _es_separador_tabla(lineas[i]):
                    filas.append(_parsear_fila_tabla(lineas[i]))
                i += 1
            if filas:
                ncols = max(len(f) for f in filas)
                tabla = doc.add_table(rows=len(filas), cols=ncols)
                tabla.style = "Table Grid"
                tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
                for r, fila in enumerate(filas):
                    for c, celda in enumerate(fila):
                        parrafo = tabla.cell(r, c).paragraphs[0]
                        run = parrafo.add_run(celda)
                        _configurar_fuente(run, tamano=10, negrita=(r == 0))
                doc.add_paragraph()
            continue

        # Bloque de código ``` ```
        if texto.strip().startswith("```"):
            i += 1
            codigo = []
            while i < len(lineas) and not lineas[i].strip().startswith("```"):
                codigo.append(lineas[i])
                i += 1
            i += 1  # cierra ```
            parrafo = doc.add_paragraph()
            parrafo.paragraph_format.left_indent = Pt(18)
            shade = parrafo._p.get_or_add_pPr()
            shd = shade.makeelement(qn("w:shd"), {qn("w:val"): "clear", qn("w:fill"): "F2F2F2"})
            shade.append(shd)
            run = parrafo.add_run("\n".join(codigo))
            _configurar_fuente(run, tamano=10 if formato_institucional else 9, color=AZUL_CODIGO, mono=True)
            doc.add_paragraph()
            continue

        # Títulos. En el formato institucional, el capítulo queda como Título 1 y
        # sus apartados como Título 2 y 3, que es la jerarquía que el índice de
        # contenido espera; en el resto de los documentos se mantiene el nivel
        # anterior, con el título general en el estilo «Title».
        base = 1 if formato_institucional else 0
        if texto.startswith("# "):
            doc.add_heading(_quitar_markdown(texto[2:]), level=base)
        elif texto.startswith("## "):
            doc.add_heading(_quitar_markdown(texto[3:]), level=base + 1)
        elif texto.startswith("### "):
            doc.add_heading(_quitar_markdown(texto[4:]), level=base + 2)
        elif texto.startswith("#### "):
            doc.add_heading(_quitar_markdown(texto[5:]), level=base + 3)
        elif texto.startswith("##### "):
            doc.add_heading(_quitar_markdown(texto[6:]), level=base + 4)
        elif texto.startswith("- ") or texto.startswith("* "):
            # viñeta (con sangría según cantidad de espacios previos)
            contenido = _quitar_markdown(texto[2:])
            parrafo = doc.add_paragraph(style="List Bullet")
            run = parrafo.add_run(contenido)
            _configurar_fuente(run, tamano=cuerpo)
        elif re.match(r"^\s*\d+\.\s", texto):
            contenido = _quitar_markdown(re.sub(r"^\s*\d+\.\s", "", texto))
            parrafo = doc.add_paragraph(style="List Number")
            run = parrafo.add_run(contenido)
            _configurar_fuente(run, tamano=cuerpo)
        elif texto.strip() == "":
            pass  # línea en blanco -> la gestiona el párrafo anterior
        elif re.match(r"^---+$", texto.strip()):
            # separador horizontal
            p = doc.add_paragraph()
            run = p.add_run("_" * 60)
            _configurar_fuente(run, tamano=9, color=GRIS)
        else:
            # párrafo normal
            parrafo = doc.add_paragraph()
            run = parrafo.add_run(_quitar_markdown(texto))
            _configurar_fuente(run, tamano=cuerpo)
        i += 1

    doc.save(docx_path)
    print(f"OK -> {docx_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python md_a_docx.py <entrada.md> <salida.docx> [--institucional]")
        sys.exit(1)
    convertir(sys.argv[1], sys.argv[2], "--institucional" in sys.argv[3:])
