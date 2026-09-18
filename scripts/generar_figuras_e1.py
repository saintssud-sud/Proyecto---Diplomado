"""Genera las figuras que exige la plantilla del entregable E1.

    · Figuras/13-tablero-semana-1.png  — tablero Kanban al cierre de la Semana 1 (Figura 1)
    · Figuras/14-modelo-de-datos.png   — modelo de datos del sistema (Figura 4)

Se dibujan por código con PIL, igual que el resto de los diagramas del
documento, y las imágenes quedan listas para insertar.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SALIDA = Path("Figuras")

VERDE = (57, 181, 74)
VERDE_CLARO = (232, 245, 234)
AZUL = (21, 101, 192)
AZUL_CLARO = (230, 240, 250)
NARANJA = (230, 81, 0)
NARANJA_CLARO = (253, 240, 232)
GRIS = (110, 114, 120)
GRIS_CAJA = (240, 241, 243)
GRIS_BORDE = (170, 175, 182)
TEXTO = (45, 45, 45)
BLANCO = (255, 255, 255)
MORADO = (94, 53, 177)
MORADO_CLARO = (237, 231, 246)


def fuente(tamano: int, negrita: bool = False):
    archivo = "arialbd.ttf" if negrita else "arial.ttf"
    return ImageFont.truetype("C:/Windows/Fonts/" + archivo, tamano)


def ancho_texto(dibujo, texto, tamano, negrita=False):
    caja = dibujo.textbbox((0, 0), texto, font=fuente(tamano, negrita))
    return caja[2] - caja[0]


def texto_centrado(dibujo, texto, x, y, ancho, tamano=18, color=TEXTO, negrita=False):
    tipografia = fuente(tamano, negrita)
    caja = dibujo.textbbox((0, 0), texto, font=tipografia)
    dibujo.text((x + (ancho - (caja[2] - caja[0])) / 2, y), texto, font=tipografia, fill=color)


def caja(dibujo, x, y, ancho, alto, relleno=BLANCO, borde=GRIS_BORDE, radio=12, grosor=2):
    dibujo.rounded_rectangle([x, y, x + ancho, y + alto], radius=radio, fill=relleno, outline=borde, width=grosor)


def flecha(dibujo, x1, y1, x2, y2, color=GRIS, grosor=2, punta=11, discontinua=False):
    if discontinua:
        pasos = 14
        for i in range(0, pasos - 1, 2):
            dibujo.line(
                [x1 + (x2 - x1) * i / pasos, y1 + (y2 - y1) * i / pasos,
                 x1 + (x2 - x1) * (i + 1) / pasos, y1 + (y2 - y1) * (i + 1) / pasos],
                fill=color, width=grosor,
            )
    else:
        dibujo.line([x1, y1, x2, y2], fill=color, width=grosor)
    if abs(x2 - x1) >= abs(y2 - y1):
        signo = 1 if x2 > x1 else -1
        dibujo.polygon([(x2, y2), (x2 - signo * punta, y2 - punta * 0.55), (x2 - signo * punta, y2 + punta * 0.55)], fill=color)
    else:
        signo = 1 if y2 > y1 else -1
        dibujo.polygon([(x2, y2), (x2 - punta * 0.55, y2 - signo * punta), (x2 + punta * 0.55, y2 - signo * punta)], fill=color)


def etiqueta(dibujo, texto, x, y, tamano=16, color=GRIS, fondo=BLANCO):
    ancho = ancho_texto(dibujo, texto, tamano) + 14
    caja(dibujo, x - ancho / 2, y - tamano / 2 - 5, ancho, tamano + 10, fondo, fondo, radio=6, grosor=0)
    texto_centrado(dibujo, texto, x - ancho / 2, y - tamano / 2 - 2, ancho, tamano, color)


# ---------------------------------------------------------------------------
# Figura 1 — Tablero Kanban al cierre de la Semana 1
# ---------------------------------------------------------------------------

COLUMNAS = (
    ("BACKLOG", GRIS_CAJA, GRIS_BORDE, [
        "T-14 Consulta y filtrado de lecturas",
        "T-15 Historial y tendencia",
        "T-16 Exportación del historial en CSV",
        "T-17 Gestión de usuarios y roles",
        "T-18 Rol de solo consulta (Invitado)",
        "T-19 Adaptabilidad en tres anchos",
        "T-20 Reglas de seguridad publicadas",
        "T-21 Primer despliegue público",
    ]),
    ("EN CURSO  (límite: 2)", AZUL_CLARO, AZUL, [
        "T-11 E1 · Perfil de proyecto:\ncapítulo 1, metodología\ny requisitos",
        "T-12 Migración de las pantallas\ndel dominio al servicio\n(5 de 7 cerradas)",
    ]),
    ("HECHO", VERDE_CLARO, VERDE, [
        "T-01 Repositorio y README",
        "T-02 Credenciales por entorno",
        "T-03 Autenticación y roles",
        "T-04 API REST /api/v1",
        "T-05 Modelo en Firestore",
        "T-06 Evaluación y alertas",
        "T-07 Panel con cuatro estados",
        "T-08 Clave del dispositivo",
        "T-09 69 pruebas del servicio",
        "T-10 Índices de Firestore",
        "T-13 Perfil de usuario en la API",
    ]),
)


def figura_tablero():
    ancho, alto = 1500, 1020
    imagen = Image.new("RGB", (ancho, alto), BLANCO)
    dibujo = ImageDraw.Draw(imagen)

    texto_centrado(dibujo, "Tablero de tareas SIGVACH — Kanban", 0, 30, ancho, 26, TEXTO, True)
    texto_centrado(
        dibujo,
        "Marco de trabajo: Scrum reducido con sprints de una semana · Límite de trabajo en curso: 2 tarjetas",
        0, 66, ancho, 18, GRIS,
    )

    margen = 40
    ancho_columna = (ancho - 2 * margen - 2 * 24) / 3
    alto_columna = 800
    y_inicio = 118

    for indice, (titulo, relleno_col, borde_col, tarjetas) in enumerate(COLUMNAS):
        x = margen + indice * (ancho_columna + 24)
        caja(dibujo, x, y_inicio, ancho_columna, alto_columna, GRIS_CAJA, GRIS_BORDE, radio=14, grosor=2)
        caja(dibujo, x, y_inicio, ancho_columna, 52, relleno_col, borde_col, radio=14, grosor=2)
        texto_centrado(dibujo, titulo, x, y_inicio + 15, ancho_columna, 19, TEXTO, True)

        y = y_inicio + 68
        for tarjeta in tarjetas:
            lineas = tarjeta.split("\n")
            alto_tarjeta = 32 + 24 * (len(lineas) - 1)
            caja(dibujo, x + 12, y, ancho_columna - 24, alto_tarjeta, BLANCO, borde_col, radio=8, grosor=2)
            for i, linea in enumerate(lineas):
                dibujo.text((x + 24, y + 8 + i * 24), linea, font=fuente(16), fill=TEXTO)
            y += alto_tarjeta + 10

        if indice < 2:
            flecha(dibujo, x + ancho_columna + 4, y_inicio + alto_columna / 2,
                   x + ancho_columna + 20, y_inicio + alto_columna / 2, GRIS, 2)

    texto_centrado(
        dibujo,
        "Estado al cierre de la Semana 1 (15 de septiembre de 2026): 11 tareas terminadas · 2 en curso · 8 en el backlog.",
        0, 940, ancho, 18, GRIS,
    )
    texto_centrado(
        dibujo,
        "Fuente: docs/TABLERO.md del repositorio del proyecto (tablero versionado, reproducible en cada entrega).",
        0, 968, ancho, 16, GRIS,
    )

    imagen.save(SALIDA / "13-tablero-semana-1.png")
    print("Figura generada: 13-tablero-semana-1.png")


# ---------------------------------------------------------------------------
# Figura 4 — Modelo de datos
# ---------------------------------------------------------------------------

ENTIDADES = (
    # (título, x, y, ancho, alto, relleno, borde, campos)
    ("usuarios", 40, 90, 360, 210, MORADO_CLARO, MORADO, [
        "id  (uid de Authentication)",
        "email · nombre · telefono · cargo",
        "rol: admin | usuario | invitado",
        "activo: booleano",
    ]),
    ("perfiles_cultivo", 470, 90, 340, 170, AZUL_CLARO, AZUL, [
        "id · nombre",
        "descripcion",
        "predefinido: booleano",
    ]),
    ("rangos", 880, 90, 360, 190, AZUL_CLARO, AZUL, [
        "id · perfil_id → perfiles_cultivo",
        "variable (catálogo de siete)",
        "minimo · maximo · unidad",
    ]),
    ("modulos_cultivo", 470, 350, 340, 190, VERDE_CLARO, VERDE, [
        "id · nombre · tipo_cultivo",
        "perfil_id → perfiles_cultivo",
        "ubicacion · activo",
    ]),
    ("lecturas", 430, 620, 420, 230, NARANJA_CLARO, NARANJA, [
        "id · modulo_id → modulos_cultivo",
        "variable · valor · unidad",
        "origen: automatico | manual",
        "timestamp · estado_rango",
        "observacion · creado_en",
    ]),
    ("alertas", 900, 620, 340, 230, NARANJA_CLARO, NARANJA, [
        "id · lectura_id → lecturas",
        "modulo_id · variable",
        "valor · rango_minimo · rango_maximo",
        "desviacion: bajo | alto",
        "estado: activa | atendida",
        "timestamp · observacion",
    ]),
)


def figura_modelo_de_datos():
    ancho, alto = 1320, 940
    imagen = Image.new("RGB", (ancho, alto), BLANCO)
    dibujo = ImageDraw.Draw(imagen)

    texto_centrado(dibujo, "Modelo de datos — colecciones y relaciones", 0, 24, ancho, 24, TEXTO, True)

    posiciones = {}
    for titulo, x, y, caja_ancho, caja_alto, relleno, borde, campos in ENTIDADES:
        caja(dibujo, x, y, caja_ancho, caja_alto, relleno, borde, radio=12, grosor=2)
        texto_centrado(dibujo, titulo, x, y + 12, caja_ancho, 20, TEXTO, True)
        dibujo.line([x, y + 44, x + caja_ancho, y + 44], fill=borde, width=1)
        for i, campo in enumerate(campos):
            dibujo.text((x + 16, y + 56 + i * 26), campo, font=fuente(15), fill=TEXTO)
        posiciones[titulo] = (x, y, caja_ancho, caja_alto)

    def conectar(origen, destino, etiqueta_texto, color=GRIS, discontinua=False,
                 desde_lado="abajo", hasta_lado="arriba"):
        x1, y1, w1, h1 = posiciones[origen]
        x2, y2, w2, h2 = posiciones[destino]
        origen_x = x1 + w1 / 2 if desde_lado == "abajo" else x1 + w1
        origen_y = y1 + h1 if desde_lado == "abajo" else y1 + h1 / 2
        destino_x = x2 + w2 / 2 if hasta_lado == "arriba" else x2
        destino_y = y2 if hasta_lado == "arriba" else y2 + h2 / 2
        flecha(dibujo, origen_x, origen_y, destino_x, destino_y, color, 2, 11, discontinua)
        etiqueta(dibujo, etiqueta_texto, (origen_x + destino_x) / 2 + 34, (origen_y + destino_y) / 2, 15, color)

    # Relaciones del dominio.
    conectar("perfiles_cultivo", "rangos", "1 : N", AZUL, False, "derecha", "izquierda")
    conectar("perfiles_cultivo", "modulos_cultivo", "1 : N  (perfil asociado)", VERDE)
    conectar("modulos_cultivo", "lecturas", "1 : N", NARANJA)
    conectar("lecturas", "alertas", "1 : 0..1", NARANJA)
    # El rango evalúa la lectura y el usuario autoriza el acceso.
    x1, y1, w1, h1 = posiciones["rangos"]
    x2, y2, w2, h2 = posiciones["lecturas"]
    flecha(dibujo, x1 + 40, y1 + h1, x2 + w2 - 60, y2, AZUL, 2, 11, True)
    etiqueta(dibujo, "evalúa la lectura", (x1 + 40 + x2 + w2 - 60) / 2, (y1 + h1 + y2) / 2, 15, AZUL)

    texto_centrado(
        dibujo,
        "El perfil de cultivo define los rangos; el módulo se asocia a un perfil; cada lectura se evalúa contra el rango de su variable; la alerta referencia la lectura que la originó.",
        0, 878, ancho, 17, GRIS,
    )

    imagen.save(SALIDA / "14-modelo-de-datos.png")
    print("Figura generada: 14-modelo-de-datos.png")


def main() -> None:
    SALIDA.mkdir(exist_ok=True)
    figura_tablero()
    figura_modelo_de_datos()
    print("Figuras escritas en", SALIDA.resolve())


if __name__ == "__main__":
    main()
