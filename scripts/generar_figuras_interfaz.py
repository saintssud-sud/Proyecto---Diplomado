"""Genera las figuras de la interfaz del documento monográfico.

Produce bocetos de pantalla (wireframes de baja fidelidad) del sistema
SI.G.VA.C.H. y una figura con los cuatro estados de una vista que consume datos.
Se ejecutan con el entorno del proyecto:

    Proyecto SIGVACH\\.venv\\Scripts\\python.exe generar_figuras_interfaz.py

Las imágenes quedan en la carpeta `Figuras/`, listas para insertar en el
documento con su título arriba y su fuente debajo, conforme al punto 5 de los
Lineamientos Técnicos (diagramas legibles, elaborados con herramientas y no a
mano).

Sobre el nivel de detalle: son bocetos deliberadamente esquemáticos. No
reproducen datos ni colores definitivos; su función es documentar la
distribución de cada pantalla y los elementos que contiene. Las capturas del
sistema funcionando son las que evidencian la implementación.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SALIDA = Path("Figuras")
ANCHO, ALTO = 880, 1260
MARGEN = 28

VERDE = (57, 181, 74)
VERDE_CLARO = (232, 245, 234)
GRIS_FONDO = (242, 243, 245)
GRIS_CAJA = (232, 234, 237)
GRIS_BORDE = (196, 200, 206)
GRIS_TEXTO = (110, 114, 120)
TEXTO = (58, 58, 58)
BLANCO = (255, 255, 255)
ROJO = (198, 40, 40)
NARANJA = (230, 81, 0)

FUENTES = {
    "titulo": ("C:/Windows/Fonts/arialbd.ttf", 30),
    "subtitulo": ("C:/Windows/Fonts/arialbd.ttf", 22),
    "texto": ("C:/Windows/Fonts/arial.ttf", 20),
    "pequena": ("C:/Windows/Fonts/arial.ttf", 17),
    "chica": ("C:/Windows/Fonts/arial.ttf", 15),
    # Los íconos se dibujan con la tipografía de emojis del sistema: Arial no
    # incluye esos símbolos y aparecerían como cuadraditos.
    "icono": ("C:/Windows/Fonts/seguiemj.ttf", 26),
    "icono_chico": ("C:/Windows/Fonts/seguiemj.ttf", 18),
}


def fuente(nombre: str):
    ruta, tamano = FUENTES[nombre]
    return ImageFont.truetype(ruta, tamano)


def centrar(dibujo, texto, x, ancho, y, tipo="texto", color=TEXTO):
    tipografia = fuente(tipo)
    caja = dibujo.textbbox((0, 0), texto, font=tipografia)
    dibujo.text((x + (ancho - (caja[2] - caja[0])) / 2, y), texto, font=tipografia, fill=color)


def caja(dibujo, x, y, ancho, alto, relleno=BLANCO, borde=GRIS_BORDE, radio=14, grosor=2):
    dibujo.rounded_rectangle(
        [x, y, x + ancho, y + alto], radius=radio, fill=relleno, outline=borde, width=grosor
    )


def campo(dibujo, x, y, ancho, etiqueta):
    caja(dibujo, x, y, ancho, 62)
    dibujo.text((x + 16, y + 21), etiqueta, font=fuente("texto"), fill=GRIS_TEXTO)


def boton(dibujo, x, y, ancho, etiqueta, relleno=VERDE, color_texto=BLANCO, alto=58):
    dibujo.rounded_rectangle([x, y, x + ancho, y + alto], radius=29, fill=relleno)
    centrar(dibujo, etiqueta, x, ancho, y + (alto - 24) / 2, "subtitulo", color_texto)


def barra_superior(dibujo, titulo, iconos=2):
    dibujo.rectangle([0, 0, ANCHO, 96], fill=VERDE)
    centrar(dibujo, titulo, 0, ANCHO, 32, "titulo", BLANCO)
    for indice in range(iconos):
        x = ANCHO - 62 - indice * 58
        dibujo.ellipse([x, 34, x + 28, 62], outline=BLANCO, width=3)


def barra_inferior(dibujo, secciones, activa=0):
    y = ALTO - 92
    dibujo.rectangle([0, y, ANCHO, ALTO], fill=BLANCO)
    dibujo.line([0, y, ANCHO, y], fill=GRIS_BORDE, width=2)
    paso = ANCHO / len(secciones)
    for indice, seccion in enumerate(secciones):
        color = VERDE if indice == activa else GRIS_TEXTO
        centro = paso * indice + paso / 2
        dibujo.rounded_rectangle(
            [centro - 14, y + 16, centro + 14, y + 44],
            radius=6,
            outline=color,
            width=3,
        )
        centrar(dibujo, seccion, paso * indice, paso, y + 52, "chica", color)


def tarjeta_variable(dibujo, x, y, ancho, nombre, valor, estado, color_estado=VERDE):
    caja(dibujo, x, y, ancho, 132)
    dibujo.ellipse([x + 16, y + 20, x + 48, y + 52], outline=GRIS_BORDE, width=3)
    dibujo.text((x + 16, y + 64), valor, font=fuente("subtitulo"), fill=color_estado)
    dibujo.text((x + 16, y + 94), nombre, font=fuente("chica"), fill=GRIS_TEXTO)
    ancho_chip = 108
    dibujo.rounded_rectangle(
        [x + ancho - ancho_chip - 14, y + 20, x + ancho - 14, y + 46],
        radius=13,
        fill=VERDE_CLARO if color_estado == VERDE else (253, 233, 230),
    )
    centrar(
        dibujo,
        estado,
        x + ancho - ancho_chip - 14,
        ancho_chip,
        y + 25,
        "chica",
        color_estado,
    )


def fila_lista(dibujo, x, y, ancho, titulo, detalle, alto=104):
    caja(dibujo, x, y, ancho, alto)
    dibujo.ellipse([x + 18, y + 26, x + 54, y + 62], outline=GRIS_BORDE, width=3)
    dibujo.text((x + 70, y + 22), titulo, font=fuente("subtitulo"), fill=TEXTO)
    dibujo.text((x + 70, y + 56), detalle, font=fuente("pequena"), fill=GRIS_TEXTO)
    dibujo.polygon(
        [(x + ancho - 40, y + 44), (x + ancho - 22, y + 44), (x + ancho - 31, y + 60)],
        fill=GRIS_BORDE,
    )


def pantalla(nombre, titulo, secciones, dibujar, activa=0, iconos=2):
    """Compone una pantalla: cabecera, contenido y barra inferior.

    El contenido se dibuja en una capa aparte y se centra verticalmente en el
    espacio disponible, de modo que una pantalla con pocos elementos no quede
    pegada a la cabecera con un hueco al pie.
    """
    imagen = Image.new("RGB", (ANCHO, ALTO), GRIS_FONDO)
    dibujo = ImageDraw.Draw(imagen)
    barra_superior(dibujo, titulo, iconos)
    barra_inferior(dibujo, secciones, activa)

    alto_capa = ALTO - 96 - 92
    capa = Image.new("RGBA", (ANCHO, alto_capa), (0, 0, 0, 0))
    dibujar(ImageDraw.Draw(capa))

    caja = capa.getbbox()
    if caja:
        alto_contenido = caja[3] - caja[1]
        sobrante = max(0, alto_capa - alto_contenido)
        desplazamiento = 96 + sobrante // 2 - caja[1]
        imagen.paste(capa, (0, desplazamiento), capa)

    imagen.save(SALIDA / nombre)
    print(f"Figura generada: {nombre}  (contenido de {alto_contenido if caja else 0} px en {alto_capa} px disponibles)")


SECCIONES = ["Inicio", "Variables", "Módulo", "Cultivos", "Historial", "Ajustes"]


def dibujar_acceso(dibujo):
    y = 190
    caja(dibujo, MARGEN, y, ANCHO - 2 * MARGEN, 150, GRIS_CAJA, GRIS_BORDE)
    centrar(dibujo, "Logotipo del sistema", MARGEN, ANCHO - 2 * MARGEN, y + 62, "texto", GRIS_TEXTO)
    y += 190
    centrar(dibujo, "Acceso al sistema", MARGEN, ANCHO - 2 * MARGEN, y, "titulo")
    y += 70
    campo(dibujo, MARGEN, y, ANCHO - 2 * MARGEN, "Correo electrónico")
    y += 84
    campo(dibujo, MARGEN, y, ANCHO - 2 * MARGEN, "Contraseña")
    y += 100
    boton(dibujo, MARGEN, y, ANCHO - 2 * MARGEN, "Iniciar sesión")
    y += 84
    centrar(dibujo, "¿No tiene cuenta? Regístrese", MARGEN, ANCHO - 2 * MARGEN, y, "pequena", GRIS_TEXTO)


def tarjeta_modulo(dibujo, x, y, ancho, nombre, activo=True, ubicacion=None):
    """Tarjeta del módulo vigente: nombre, estado, cultivo y ubicación."""
    alto = 132 if ubicacion else 104
    caja(dibujo, x, y, ancho, alto, BLANCO, VERDE)

    # Recuadro del ícono, como en la aplicación.
    caja(dibujo, x + 18, y + 20, 64, 64, VERDE_CLARO, VERDE_CLARO, radio=16, grosor=1)
    centrar(dibujo, "\U0001F33F", x + 18, 64, y + 36, "icono", VERDE)

    dibujo.text((x + 100, y + 22), nombre, font=fuente("subtitulo"), fill=TEXTO)
    caja(dibujo, x + ancho - 150, y + 24, 128, 40, VERDE_CLARO, VERDE_CLARO, radio=20, grosor=1)
    centrar(dibujo, "Activo" if activo else "Inactivo", x + ancho - 150, 128, y + 32, "pequena", VERDE)
    dibujo.text((x + 100, y + 60), "Cultivo: Lechuga", font=fuente("pequena"), fill=GRIS_TEXTO)
    if ubicacion:
        dibujo.text((x + 100, y + 88), "Ubicación: " + ubicacion, font=fuente("pequena"), fill=GRIS_TEXTO)


def dibujar_panel(dibujo):
    y = 130
    caja(dibujo, MARGEN, y, ANCHO - 2 * MARGEN, 104, (253, 236, 231), NARANJA)
    dibujo.text((MARGEN + 24, y + 22), "Sistema con alertas", font=fuente("subtitulo"), fill=NARANJA)
    dibujo.text(
        (MARGEN + 24, y + 56),
        "Algunos parámetros están fuera de rango",
        font=fuente("pequena"),
        fill=NARANJA,
    )
    y += 128

    # Selector del módulo vigente: el panel consulta un módulo por vez.
    # La etiqueta va arriba del campo para que no se superponga con el valor.
    dibujo.text((MARGEN + 4, y), "Módulo de cultivo", font=fuente("chica"), fill=GRIS_TEXTO)
    caja(dibujo, MARGEN, y + 22, ANCHO - 2 * MARGEN, 58)
    dibujo.text((MARGEN + 16, y + 38), "Módulo 1", font=fuente("texto"), fill=TEXTO)
    dibujo.text((ANCHO - MARGEN - 40, y + 40), "▼", font=fuente("pequena"), fill=GRIS_TEXTO)
    y += 96

    # Tarjeta del módulo: cultivo, perfil de referencia y ubicación.
    tarjeta_modulo(dibujo, MARGEN, y, ANCHO - 2 * MARGEN, "Módulo 1", True, "Invernadero Norte")
    y += 150

    ancho = (ANCHO - 2 * MARGEN - 16) / 2
    filas = [
        ("Temperatura", "24,5 °C", "Normal", VERDE),
        ("Humedad", "65 %", "Normal", VERDE),
        ("pH", "7,4", "Fuera de rango", ROJO),
        ("TDS", "850 ppm", "Normal", VERDE),
        ("Nivel de agua", "78 cm", "Normal", VERDE),
        ("EC", "1,5 mS/cm", "Normal", VERDE),
    ]
    for indice, (nombre, valor, estado, color) in enumerate(filas):
        columna = indice % 2
        fila = indice // 2
        tarjeta_variable(
            dibujo,
            MARGEN + columna * (ancho + 16),
            y + fila * 144,
            ancho,
            nombre,
            valor,
            estado,
            color,
        )
    y += 3 * 144 + 8
    boton(dibujo, ANCHO - MARGEN - 300, y, 300, "Registrar medición", VERDE_CLARO, VERDE)
    y += 76
    dibujo.text((MARGEN, y + 8), "Última actualización:", font=fuente("pequena"), fill=GRIS_TEXTO)
    dibujo.text((ANCHO - MARGEN - 240, y + 8), "17/09/2026 10:04 a. m.", font=fuente("pequena"), fill=TEXTO)


def dibujar_variables(dibujo):
    y = 130
    centrar(dibujo, "Variables", MARGEN, ANCHO - 2 * MARGEN, y, "titulo")
    y += 66
    ancho = (ANCHO - 2 * MARGEN - 16) / 2
    datos = [
        ("Temperatura", "24,5 °C", "Normal", VERDE),
        ("Humedad", "65 %", "Normal", VERDE),
        ("pH", "7,4", "Fuera de rango", ROJO),
        ("TDS", "850 ppm", "Normal", VERDE),
        ("Nivel de agua", "78 cm", "Sin rango", GRIS_TEXTO),
        ("EC", "1,5 mS/cm", "Normal", VERDE),
    ]
    for indice, (nombre, valor, estado, color) in enumerate(datos):
        tarjeta_variable(
            dibujo,
            MARGEN + (indice % 2) * (ancho + 16),
            y + (indice // 2) * 144,
            ancho,
            nombre,
            valor,
            estado,
            color,
        )


def dibujar_cultivos(dibujo):
    y = 130
    centrar(dibujo, "Módulo de cultivo", MARGEN, ANCHO - 2 * MARGEN, y, "titulo")
    y += 62
    for titulo, detalle in [
        ("Módulo 1", "Lechuga · Invernadero Norte · activo"),
        ("Módulo 2", "Acelga · Invernadero Norte · activo"),
        ("Módulo 3", "Apio · Invernadero Norte · activo"),
    ]:
        fila_lista(dibujo, MARGEN, y, ANCHO - 2 * MARGEN, titulo, detalle)
        y += 120
    boton(dibujo, MARGEN, y + 10, ANCHO - 2 * MARGEN, "Agregar módulo de cultivo")


def dibujar_lecturas(dibujo):
    y = 130
    centrar(dibujo, "Lecturas", MARGEN, ANCHO - 2 * MARGEN, y, "titulo")
    y += 62
    dibujo.text((MARGEN, y), "Módulo: Módulo 1 · Variable: pH", font=fuente("pequena"), fill=GRIS_TEXTO)
    y += 38
    for titulo, detalle in [
        ("pH 6,1 · 14/09 10:04", "Origen: automático"),
        ("pH 7,4 · 14/09 08:20", "Origen: automático · fuera de rango"),
        ("pH 6,0 · 13/09 19:40", "Origen: manual · observación"),
    ]:
        fila_lista(dibujo, MARGEN, y, ANCHO - 2 * MARGEN, titulo, detalle)
        y += 120
    boton(dibujo, MARGEN, y + 6, ANCHO - 2 * MARGEN, "Registrar lectura manual")


def dibujar_rangos(dibujo):
    y = 130
    centrar(dibujo, "Rangos y perfiles", MARGEN, ANCHO - 2 * MARGEN, y, "titulo")
    y += 62
    dibujo.text((MARGEN, y), "Perfil: Lechuga (predefinido)", font=fuente("texto"), fill=TEXTO)
    y += 46
    for variable, rango in [
        ("pH", "5,5 – 6,5"),
        ("Conductividad eléctrica", "1,2 – 1,8 mS/cm"),
        ("Temperatura de la solución", "15 – 25 °C"),
        ("Humedad relativa", "50 – 80 %"),
    ]:
        fila_lista(dibujo, MARGEN, y, ANCHO - 2 * MARGEN, variable, "Rango: " + rango)
        y += 120
    boton(dibujo, MARGEN, y + 6, ANCHO - 2 * MARGEN, "Agregar rango de referencia")


def dibujar_historial(dibujo):
    y = 130
    centrar(dibujo, "Historial y alertas", MARGEN, ANCHO - 2 * MARGEN, y, "titulo")
    y += 62
    campo(dibujo, MARGEN, y, ANCHO - 2 * MARGEN, "Variable: pH")
    y += 80
    ancho = (ANCHO - 2 * MARGEN - 16) / 2
    campo(dibujo, MARGEN, y, ancho, "Desde: 01/09/2026")
    campo(dibujo, MARGEN + ancho + 16, y, ancho, "Hasta: 14/09/2026")
    y += 92
    caja(dibujo, MARGEN, y, ANCHO - 2 * MARGEN, 210)
    centrar(dibujo, "Gráfica de tendencia", MARGEN, ANCHO - 2 * MARGEN, y + 20, "pequena", GRIS_TEXTO)
    puntos = [
        (MARGEN + 40, y + 170),
        (MARGEN + 140, y + 130),
        (MARGEN + 240, y + 150),
        (MARGEN + 340, y + 90),
        (MARGEN + 440, y + 120),
        (MARGEN + 540, y + 70),
        (MARGEN + 640, y + 110),
        (MARGEN + 740, y + 140),
    ]
    dibujo.line(puntos, fill=VERDE, width=4)
    y += 236
    dibujo.text(
        (MARGEN, y),
        "Promedio 6,1 · Máximo 7,4 · Mínimo 5,2 · 42 lecturas",
        font=fuente("pequena"),
        fill=TEXTO,
    )
    y += 44
    boton(dibujo, MARGEN, y, ancho, "Exportar CSV", GRIS_CAJA, TEXTO)
    boton(dibujo, MARGEN + ancho + 16, y, ancho, "Ver alertas", GRIS_CAJA, TEXTO)


def dibujar_usuarios(dibujo):
    y = 130
    centrar(dibujo, "Usuarios (administración)", MARGEN, ANCHO - 2 * MARGEN, y, "titulo")
    y += 62
    dibujo.text(
        (MARGEN, y),
        "Solo visible para el perfil Administrador",
        font=fuente("pequena"),
        fill=GRIS_TEXTO,
    )
    y += 40
    for titulo, detalle in [
        ("Administrador", "admin@sigvach.com · rol administrador · activo"),
        ("Operador", "operador@sigvach.com · rol operador · activo"),
        ("Usuario dado de baja", "baja@sigvach.com · rol operador · inactivo"),
    ]:
        fila_lista(dibujo, MARGEN, y, ANCHO - 2 * MARGEN, titulo, detalle)
        y += 120
    boton(dibujo, MARGEN, y + 6, ANCHO - 2 * MARGEN, "Editar rol y estado", GRIS_CAJA, TEXTO)


def figura_estados():
    """Los cuatro estados de una vista que consume datos, en una sola figura."""
    ancho_panel, alto_panel = 620, 460
    separacion = 30
    columnas, filas = 2, 2
    ancho = columnas * ancho_panel + (columnas + 1) * separacion
    alto = filas * alto_panel + (filas + 1) * separacion
    imagen = Image.new("RGB", (ancho, alto), BLANCO)
    dibujo = ImageDraw.Draw(imagen)

    def panel(columna, fila, titulo, contenido, color=VERDE):
        x = separacion + columna * (ancho_panel + separacion)
        y = separacion + fila * (alto_panel + separacion)
        caja(dibujo, x, y, ancho_panel, alto_panel, GRIS_FONDO, GRIS_BORDE)
        dibujo.rectangle([x, y, x + ancho_panel, y + 56], fill=color)
        centrar(dibujo, titulo, x, ancho_panel, y + 15, "subtitulo", BLANCO)
        contenido(x, y + 56)

    def cargando(x, y):
        dibujo.ellipse([x + ancho_panel / 2 - 34, y + 130, x + ancho_panel / 2 + 34, y + 198], outline=VERDE, width=6)
        centrar(dibujo, "Cargando información…", x, ancho_panel, y + 230, "texto", GRIS_TEXTO)

    def con_datos(x, y):
        tarjeta_variable(dibujo, x + 40, y + 40, ancho_panel - 80, "pH", "6,1", "Normal", VERDE)
        tarjeta_variable(dibujo, x + 40, y + 190, ancho_panel - 80, "Humedad", "65 %", "Normal", VERDE)
        centrar(dibujo, "Es el caso de uso principal", x, ancho_panel, y + 348, "pequena", GRIS_TEXTO)

    def vacio(x, y):
        # El estado vacío conserva el encabezado del módulo y ofrece registrar la
        # primera medición: sin esa acción, un módulo recién creado no podía
        # poblarse desde la aplicación.
        caja(dibujo, x + 30, y + 24, ancho_panel - 60, 64, BLANCO, GRIS_BORDE, radio=12)
        dibujo.text((x + 46, y + 40), "Módulo de cultivo", font=fuente("chica"), fill=GRIS_TEXTO)
        dibujo.text((x + 46, y + 60), "Módulo 3", font=fuente("pequena"), fill=TEXTO)
        dibujo.rounded_rectangle(
            [x + ancho_panel / 2 - 34, y + 110, x + ancho_panel / 2 + 34, y + 172],
            radius=10,
            outline=VERDE,
            width=5,
        )
        centrar(dibujo, "Todavía no hay información", x, ancho_panel, y + 192, "subtitulo", TEXTO)
        centrar(
            dibujo,
            "El módulo todavía no tiene lecturas registradas",
            x,
            ancho_panel,
            y + 228,
            "pequena",
            GRIS_TEXTO,
        )
        boton(
            dibujo,
            x + ancho_panel / 2 - 160,
            y + 268,
            320,
            "Registrar la primera medición",
            VERDE,
            BLANCO,
        )
        boton(dibujo, x + ancho_panel / 2 - 110, y + 340, 220, "Actualizar", VERDE_CLARO, VERDE)

    def error(x, y):
        dibujo.line([x + ancho_panel / 2 - 34, y + 96, x + ancho_panel / 2 + 34, y + 164], fill=ROJO, width=5)
        dibujo.line([x + ancho_panel / 2 + 34, y + 96, x + ancho_panel / 2 - 34, y + 164], fill=ROJO, width=5)
        centrar(dibujo, "No se pudo conectar con el servidor", x, ancho_panel, y + 192, "subtitulo", ROJO)
        centrar(
            dibujo,
            "Revise la conexión e intente nuevamente.",
            x,
            ancho_panel,
            y + 236,
            "pequena",
            GRIS_TEXTO,
        )
        boton(dibujo, x + ancho_panel / 2 - 110, y + 300, 220, "Reintentar", VERDE_CLARO, VERDE)

    panel(0, 0, "1 · Cargando", cargando, GRIS_TEXTO)
    panel(1, 0, "2 · Con datos", con_datos, VERDE)
    panel(0, 1, "3 · Vacío", vacio, GRIS_TEXTO)
    panel(1, 1, "4 · Con error", error, ROJO)

    imagen.save(SALIDA / "08-estados-de-una-vista.png")
    print("Figura generada: 08-estados-de-una-vista.png")


def main() -> None:
    SALIDA.mkdir(exist_ok=True)

    pantalla("01-acceso.png", "SIGVACH", SECCIONES, dibujar_acceso, -1)
    pantalla("02-panel-principal.png", "SIGVACH", SECCIONES, dibujar_panel, 0)
    pantalla("03-variables.png", "SIGVACH", SECCIONES, dibujar_variables, 1)
    pantalla("04-modulos.png", "SIGVACH", SECCIONES, dibujar_cultivos, 2)
    pantalla("05-lecturas.png", "SIGVACH", SECCIONES, dibujar_lecturas, 1)
    pantalla("06-rangos-y-perfiles.png", "SIGVACH", SECCIONES, dibujar_rangos, 5)
    pantalla("07-historial-y-alertas.png", "SIGVACH", SECCIONES, dibujar_historial, 4)
    pantalla("09-usuarios.png", "SIGVACH", SECCIONES, dibujar_usuarios, 5)

    figura_estados()
    print("Figuras escritas en", SALIDA.resolve())


if __name__ == "__main__":
    main()
