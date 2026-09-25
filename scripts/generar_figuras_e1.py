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
    """Dibuja una flecha con el trazo y la punta bien visibles.

    Las relaciones del modelo se leen en tamaño carta impreso: una línea de dos
    píxeles con una punta de once se pierde al imprimir y la flecha deja de
    distinguirse del borde de la caja. Por eso el trazo va grueso y la punta
    ancha, que es lo que permite seguir la relación de un vistazo.
    """
    if discontinua:
        pasos = 18
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
        dibujo.polygon([(x2, y2), (x2 - signo * punta, y2 - punta * 0.78), (x2 - signo * punta, y2 + punta * 0.78)], fill=color)
    else:
        signo = 1 if y2 > y1 else -1
        dibujo.polygon([(x2, y2), (x2 - punta * 0.78, y2 - signo * punta), (x2 + punta * 0.78, y2 - signo * punta)], fill=color)


def etiqueta(dibujo, texto, x, y, tamano=16, color=GRIS, fondo=BLANCO, negrita=False):
    """Escribe el rótulo de una relación sobre el trazo, con fondo que lo despega.

    El rótulo se centra en el punto medio del trazo —sin corrimiento— y lleva un
    filete del color de la relación, de modo que se lea como parte de la flecha.
    El corrimiento fijo que tenía antes lo empujaba dentro de la caja de destino
    y el «1 : N» quedaba montado encima del primer campo de esa caja.
    """
    ancho = ancho_texto(dibujo, texto, tamano, negrita) + 18
    caja(dibujo, x - ancho / 2, y - tamano / 2 - 7, ancho, tamano + 14, fondo, color, radio=6, grosor=2)
    texto_centrado(dibujo, texto, x - ancho / 2, y - tamano / 2 - 3, ancho, tamano, color, negrita)


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

def tinte(color, factor=0.88):
    """Aclara un color acercándolo al blanco, para el cuerpo de la caja.

    Cada entidad lleva su propio color: la barra del título va saturada con el
    nombre en blanco, y el cuerpo es un tinte claro del mismo tono. Así se
    distingue una colección de otra de un vistazo —que es lo que se busca al
    mirar el modelo— sin perder la legibilidad del texto.
    """
    return tuple(round(componente + (255 - componente) * factor) for componente in color)


ENTIDADES = (
    # (título, x, y, ancho, alto, color, campos)
    # Las coordenadas dejan hueco suficiente entre cajas para que el rótulo de
    # cada relación quepa en el espacio libre y no se monte sobre el vecino.
    ("usuarios", 40, 90, 360, 210, (21, 101, 192), [
        "id  (uid de Authentication)",
        "email · nombre · telefono · cargo",
        "rol: administrador | operador",
        "activo: booleano",
    ]),
    ("perfiles_cultivo", 470, 90, 340, 170, (106, 27, 154), [
        "id · nombre",
        "descripcion",
        "predefinido: booleano",
    ]),
    ("rangos", 890, 90, 360, 190, (0, 105, 92), [
        "id · perfil_id → perfiles_cultivo",
        "variable (catálogo de seis)",
        "minimo · maximo · unidad",
    ]),
    ("modulos_cultivo", 470, 350, 340, 190, (46, 125, 50), [
        "id · nombre · tipo_cultivo",
        "perfil_id → perfiles_cultivo",
        "ubicacion · activo",
    ]),
    ("lecturas", 430, 620, 390, 230, (230, 81, 0), [
        "id · modulo_id → modulos_cultivo",
        "variable · valor · unidad",
        "origen: automatico | manual",
        "registrado_por → usuarios",
        "timestamp · estado_rango",
        "observacion · creado_en",
    ]),
    ("alertas", 920, 620, 340, 252, (198, 40, 40), [
        "id · lectura_id → lecturas",
        "modulo_id · variable",
        "valor · unidad",
        "rango_minimo · rango_maximo",
        "desviacion: bajo | alto",
        "estado: activa | atendida",
        "timestamp · observacion",
    ]),
)


ALTO_TITULO = 40


def dibujar_entidad(dibujo, x, y, ancho, alto, color, titulo, campos):
    """Dibuja una colección: barra de título en color y cuerpo en tono claro.

    La barra se traza redondeada arriba y recta abajo: se dibuja el rectángulo
    redondeado del título y se le cuadra la base con un rectángulo liso encima,
    de modo que la esquina redondeada quede solo donde coincide con el contorno
    del cuadro.
    """
    claro = tinte(color)
    dibujo.rounded_rectangle([x, y, x + ancho, y + alto], radius=12, fill=claro)
    dibujo.rounded_rectangle([x, y, x + ancho, y + ALTO_TITULO], radius=12, fill=color)
    dibujo.rectangle([x, y + ALTO_TITULO - 12, x + ancho, y + ALTO_TITULO], fill=color)
    dibujo.rounded_rectangle([x, y, x + ancho, y + alto], radius=12, outline=color, width=3)
    texto_centrado(dibujo, titulo, x, y + 11, ancho, 19, BLANCO, True)
    for i, campo in enumerate(campos):
        dibujo.text((x + 16, y + ALTO_TITULO + 16 + i * 26), campo, font=fuente(15), fill=TEXTO)


def figura_modelo_de_datos():
    ancho, alto = 1320, 940
    imagen = Image.new("RGB", (ancho, alto), BLANCO)
    dibujo = ImageDraw.Draw(imagen)

    texto_centrado(dibujo, "Modelo de datos — colecciones y relaciones", 0, 24, ancho, 24, TEXTO, True)

    posiciones = {}
    colores = {}
    for titulo, x, y, caja_ancho, caja_alto, color, campos in ENTIDADES:
        dibujar_entidad(dibujo, x, y, caja_ancho, caja_alto, color, titulo, campos)
        posiciones[titulo] = (x, y, caja_ancho, caja_alto)
        colores[titulo] = color

    def hay_choque(centro_x, centro_y, ancho_rotulo, alto_rotulo=30):
        """Indica si una etiqueta en esa posición se montaría sobre una caja."""
        x0, x1 = centro_x - ancho_rotulo / 2, centro_x + ancho_rotulo / 2
        y0, y1 = centro_y - alto_rotulo / 2, centro_y + alto_rotulo / 2
        if x0 < 8 or x1 > ancho - 8 or y0 < 8 or y1 > alto - 8:
            return True
        for caja_x, caja_y, caja_ancho, caja_alto in posiciones.values():
            if x1 > caja_x and x0 < caja_x + caja_ancho and y1 > caja_y and y0 < caja_y + caja_alto:
                return True
        return False

    def conectar(origen, destino, etiqueta_texto, color=GRIS, discontinua=False,
                 desde_lado="abajo", hasta_lado="arriba"):
        x1, y1, w1, h1 = posiciones[origen]
        x2, y2, w2, h2 = posiciones[destino]
        origen_x = x1 + w1 / 2 if desde_lado == "abajo" else x1 + w1
        origen_y = y1 + h1 if desde_lado == "abajo" else y1 + h1 / 2
        destino_x = x2 + w2 / 2 if hasta_lado == "arriba" else x2
        destino_y = y2 if hasta_lado == "arriba" else y2 + h2 / 2
        flecha(dibujo, origen_x, origen_y, destino_x, destino_y, color, 5, 26, discontinua)
        etiqueta_relacion(etiqueta_texto, origen_x, origen_y, destino_x, destino_y, color)

    def etiqueta_relacion(texto, origen_x, origen_y, destino_x, destino_y, color):
        """Coloca el rótulo al costado del trazo, sin fondo y sin taparlo.

        El rótulo se aparta en perpendicular al sentido de la flecha —de modo que
        queda por encima de las flechas horizontales y a la derecha de las
        verticales— y, si en ese lado se montaría sobre una caja, se prueba el
        lado contrario. Va escrito en el color de su relación y sin recuadro, que
        es como se lee en los diagramas de modelo de datos.
        """
        delta_x, delta_y = destino_x - origen_x, destino_y - origen_y
        largo = (delta_x ** 2 + delta_y ** 2) ** 0.5
        ancho_rotulo = ancho_texto(dibujo, texto, 16, True)
        medio_x, medio_y = (origen_x + destino_x) / 2, (origen_y + destino_y) / 2

        elegido = None
        for signo in (1, -1):
            perpendicular_x = signo * delta_y / largo
            perpendicular_y = -signo * delta_x / largo
            separacion = (
                abs(perpendicular_x) * ancho_rotulo / 2 + abs(perpendicular_y) * 15 + 16
            )
            centro_x = medio_x + perpendicular_x * separacion
            centro_y = medio_y + perpendicular_y * separacion
            if not hay_choque(centro_x, centro_y, ancho_rotulo):
                elegido = (centro_x, centro_y)
                break
        if elegido is None:
            # Los dos lados están ocupados: se aparta más y se acepta el primero.
            elegido = (medio_x, medio_y - 44)
        texto_centrado(dibujo, texto, elegido[0] - ancho_rotulo / 2, elegido[1] - 9,
                       ancho_rotulo, 16, color, True)

    # Relaciones del dominio. Cada flecha lleva el color de la colección de la que
    # sale, de modo que siguiendo un color se ven sus relaciones de un vistazo.
    conectar("perfiles_cultivo", "rangos", "1 : N", colores["perfiles_cultivo"], False, "derecha", "izquierda")
    conectar("perfiles_cultivo", "modulos_cultivo", "1 : N  (perfil asociado)", colores["perfiles_cultivo"])
    conectar("modulos_cultivo", "lecturas", "1 : N", colores["modulos_cultivo"])
    # Lecturas y alertas son cajas vecinas: la relación va por el hueco que queda
    # entre ambas y no en diagonal por encima de ellas.
    conectar("lecturas", "alertas", "1 : 0..1", colores["lecturas"], False, "derecha", "izquierda")
    # El usuario que registró la lectura manual. Sin esta relación, la caja de
    # usuarios quedaba suelta en el diagrama aunque el diccionario declara la
    # referencia `registrado_por`.
    conectar("usuarios", "lecturas", "1 : N  (registro manual)", colores["usuarios"], True, "abajo", "izquierda")
    # El rango evalúa la lectura y el usuario autoriza el acceso. Esta relación no
    # une dos cajas vecinas sino que cruza el diagrama en diagonal.
    x1, y1, w1, h1 = posiciones["rangos"]
    x2, y2, w2, h2 = posiciones["lecturas"]
    inicio_x, inicio_y = x1 + 40, y1 + h1
    # La punta no apunta al centro de la caja de lecturas sino un poco a su
    # derecha: si bajara hasta el centro, el trazo entraría en el vértice
    # inferior derecho de la caja de módulos, que es la caja que queda en medio.
    fin_x, fin_y = x2 + w2 - 20, y2
    flecha(dibujo, inicio_x, inicio_y, fin_x, fin_y, colores["rangos"], 5, 26, True)
    etiqueta_relacion("evalúa la lectura", inicio_x, inicio_y, fin_x, fin_y, colores["rangos"])

    texto_centrado(
        dibujo,
        "El perfil de cultivo define los rangos; el módulo se asocia a un perfil; cada lectura se evalúa contra el rango de su variable; la alerta referencia la lectura que la originó.",
        0, 892, ancho, 17, GRIS,
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
