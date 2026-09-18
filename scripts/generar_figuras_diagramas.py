"""Genera los diagramas técnicos del documento monográfico.

Produce, como imágenes listas para insertar en el documento, los diagramas que
los Lineamientos Técnicos exigen en los apartados 2.3.4 y 2.4.4:

    · arquitectura de componentes del sistema (apartado 2.4.1);
    · casos de uso (apartado 2.3.4);
    · secuencia del registro de una lectura (apartados 2.4.4 y 2.6).

Se ejecutan con el entorno del proyecto:

    Proyecto SIGVACH\\.venv\\Scripts\\python.exe generar_figuras_diagramas.py

Las imágenes quedan en `Figuras/`. El código fuente de los mismos diagramas en
notación Mermaid está en `Diagramas Mermaid - Modulo 4.md`: sirve para editar el
contenido, mientras que estas imágenes son las que se insertan en el documento.

Los diagramas se dibujan por código —y no a mano— conforme al punto 5 de los
Lineamientos, y se verifican midiendo la geometría: que ningún texto exceda su
contenedor y que nada quede fuera del lienzo.
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


def fuente(tamano: int, negrita: bool = False):
    archivo = "arialbd.ttf" if negrita else "arial.ttf"
    return ImageFont.truetype("C:/Windows/Fonts/" + archivo, tamano)


def ancho_texto(dibujo, texto, tamano, negrita=False):
    caja = dibujo.textbbox((0, 0), texto, font=fuente(tamano, negrita))
    return caja[2] - caja[0]


def texto_centrado(dibujo, texto, x, y, ancho, tamano=20, color=TEXTO, negrita=False):
    tipografia = fuente(tamano, negrita)
    caja = dibujo.textbbox((0, 0), texto, font=tipografia)
    dibujo.text(
        (x + (ancho - (caja[2] - caja[0])) / 2, y),
        texto,
        font=tipografia,
        fill=color,
    )


def caja(dibujo, x, y, ancho, alto, relleno=BLANCO, borde=GRIS_BORDE, radio=14, grosor=2):
    dibujo.rounded_rectangle([x, y, x + ancho, y + alto], radius=radio, fill=relleno, outline=borde, width=grosor)


def caja_con_texto(dibujo, x, y, ancho, alto, lineas, tamano=20, relleno=BLANCO, borde=GRIS_BORDE, color=TEXTO, negrita=False):
    caja(dibujo, x, y, ancho, alto, relleno, borde)
    alto_linea = tamano + 8
    inicio = y + (alto - len(lineas) * alto_linea) / 2 + 2
    for indice, linea in enumerate(lineas):
        texto_centrado(dibujo, linea, x, inicio + indice * alto_linea, ancho, tamano, color, negrita)


def flecha(dibujo, x1, y1, x2, y2, color=GRIS, grosor=3, punta=12, discontinua=False):
    if discontinua:
        pasos = 12
        for i in range(0, pasos, 2):
            ax = x1 + (x2 - x1) * i / pasos
            ay = y1 + (y2 - y1) * i / pasos
            bx = x1 + (x2 - x1) * (i + 1) / pasos
            by = y1 + (y2 - y1) * (i + 1) / pasos
            dibujo.line([ax, ay, bx, by], fill=color, width=grosor)
    else:
        dibujo.line([x1, y1, x2, y2], fill=color, width=grosor)
    if abs(x2 - x1) >= abs(y2 - y1):
        signo = 1 if x2 > x1 else -1
        dibujo.polygon(
            [(x2, y2), (x2 - signo * punta, y2 - punta * 0.55), (x2 - signo * punta, y2 + punta * 0.55)],
            fill=color,
        )
    else:
        signo = 1 if y2 > y1 else -1
        dibujo.polygon(
            [(x2, y2), (x2 - punta * 0.55, y2 - signo * punta), (x2 + punta * 0.55, y2 - signo * punta)],
            fill=color,
        )


def etiqueta(dibujo, texto, x, y, tamano=17, color=GRIS, fondo=BLANCO):
    ancho = ancho_texto(dibujo, texto, tamano) + 16
    caja(dibujo, x - ancho / 2, y - tamano / 2 - 6, ancho, tamano + 12, fondo, fondo, radio=6, grosor=0)
    texto_centrado(dibujo, texto, x - ancho / 2, y - tamano / 2 - 2, ancho, tamano, color)


# ---------------------------------------------------------------------------
# 1. Arquitectura de componentes (apartado 2.4.1)
# ---------------------------------------------------------------------------

def diagrama_arquitectura():
    ancho, alto = 1400, 1000
    imagen = Image.new("RGB", (ancho, alto), BLANCO)
    dibujo = ImageDraw.Draw(imagen)

    centro = ancho / 2
    ancho_caja = 560
    x_centro = centro - ancho_caja / 2

    # Niveles apilados de arriba hacia abajo.
    caja_con_texto(
        dibujo, x_centro, 110, ancho_caja, 110,
        ["Nivel de adquisición", "Módulo ESP32 y sensores"], 22, VERDE_CLARO, VERDE, negrita=True,
    )
    caja_con_texto(
        dibujo, x_centro, 400, ancho_caja, 130,
        ["Nivel de servicio", "API REST /api/v1", "valida · autoriza · decide"], 22, BLANCO, VERDE, negrita=True,
    )
    caja_con_texto(
        dibujo, x_centro, 720, ancho_caja, 110,
        ["Nivel de datos", "Cloud Firestore"], 22, GRIS_CAJA, GRIS_BORDE, negrita=True,
    )

    flecha(dibujo, centro, 220, centro, 388)
    etiqueta(dibujo, "HTTPS + clave de dispositivo", centro, 304, 18)
    flecha(dibujo, centro, 530, centro, 708)
    etiqueta(dibujo, "SDK de administración con cuenta de servicio", centro, 619, 18)

    # Presentación, a la izquierda.
    caja_con_texto(
        dibujo, 90, 400, 300, 130,
        ["Nivel de presentación", "Aplicación Flutter", "Android y web"], 20, AZUL_CLARO, AZUL, negrita=True,
    )
    flecha(dibujo, 390, 465, x_centro - 6, 465)
    etiqueta(dibujo, "HTTPS + token", 452, 437, 17)

    # Identidad, a la derecha.
    caja_con_texto(
        dibujo, ancho - 390, 400, 300, 130,
        ["Firebase", "Authentication"], 20, NARANJA_CLARO, NARANJA, negrita=True,
    )
    flecha(dibujo, ancho - 396, 465, x_centro + ancho_caja + 6, 465)
    etiqueta(dibujo, "verifica el token", ancho - 452, 437, 17)

    texto_centrado(
        dibujo,
        "El nivel de servicio es el único que accede a la base de datos: la aplicación y el dispositivo nunca la tocan.",
        0, 900, ancho, 19, GRIS,
    )

    imagen.save(SALIDA / "10-arquitectura-de-componentes.png")
    print("Figura generada: 10-arquitectura-de-componentes.png")


# ---------------------------------------------------------------------------
# 2. Casos de uso (apartado 2.3.4)
# ---------------------------------------------------------------------------

IZQUIERDA = [
    "CU-01 Iniciar sesión",
    "CU-04 Consultar el panel",
    "CU-05 Consultar historial",
    "CU-08 Configurar rangos",
    "CU-09 Gestionar módulos",
    "CU-10 Gestionar usuarios",
]
DERECHA = [
    "CU-02 Registrar lectura automática",
    "CU-03 Registrar lectura manual",
    "CU-06 Atender una alerta",
    "CU-07 Exportar el historial",
]

# Cada actor con los casos que alcanza, como pares (columna, índice).
ADMINISTRADOR = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]
OPERADOR = [(1, 1), (1, 2), (1, 3), (0, 0), (0, 1), (0, 2)]
DISPOSITIVO = (1, 0)

GRIS_SUAVE = (203, 207, 213)


def diagrama_casos_de_uso():
    ancho, alto = 1500, 1080
    imagen = Image.new("RGB", (ancho, alto), BLANCO)
    dibujo = ImageDraw.Draw(imagen)

    # Sistema.
    caja(dibujo, 390, 130, 720, 900, GRIS_CAJA, GRIS_BORDE, radio=22)
    texto_centrado(dibujo, "SI.G.VA.C.H.", 390, 96, 720, 24, TEXTO, True)

    alto_caso = 74
    separacion = 44
    ancho_caso = 316
    # La columna izquierda agrupa los casos de consulta y de administración; la
    # derecha, los de registro y atención. El desfase vertical de la derecha
    # mantiene las dos columnas centradas entre sí.
    arriba = {0: 200, 1: 318}
    for columna, casos in ((0, IZQUIERDA), (1, DERECHA)):
        for indice, caso in enumerate(casos):
            x = 420 + columna * 360
            y = arriba[columna] + indice * (alto_caso + separacion)
            caja(dibujo, x, y, ancho_caso, alto_caso, BLANCO, VERDE, radio=alto_caso // 2)
            texto_centrado(dibujo, caso, x + 8, y + 24, ancho_caso - 16, 18)

    def centro_caso(referencia):
        columna, indice = referencia
        x = 420 + columna * 360 + ancho_caso / 2
        y = arriba[columna] + indice * (alto_caso + separacion) + alto_caso / 2
        return x, y

    def unir(x_actor, y_actor, referencia, color=GRIS, grosor=2):
        """Asocia un actor con un caso: línea continua, como pide la notación UML.

        El trazo termina siempre en el borde del caso **más próximo al actor**, de
        modo que ninguna línea atraviese el óvalo del caso de uso.
        """
        x, y = centro_caso(referencia)
        desde_la_izquierda = x_actor < ancho / 2
        borde = (x - ancho_caso / 2 - 6) if desde_la_izquierda else (x + ancho_caso / 2 + 6)
        flecha(dibujo, x_actor, y_actor, borde, y, color, grosor)

    # Administrador (izquierda): los casos de administración y de consulta.
    caja_con_texto(dibujo, 40, 440, 250, 140, ["Administrador"], 22, VERDE_CLARO, VERDE, negrita=True)
    for referencia in ADMINISTRADOR:
        unir(292, 510, referencia)

    # Operador (derecha): registra, atiende y exporta, y además consulta.
    caja_con_texto(dibujo, ancho - 290, 440, 250, 140, ["Operador"], 22, AZUL_CLARO, AZUL, negrita=True)
    for referencia in OPERADOR:
        if referencia[0] == 1:
            unir(ancho - 292, 510, referencia)
        else:
            # Los casos que comparte con la administración se trazan tenues para
            # que la lectura del diagrama no se sature de líneas cruzadas.
            unir(ancho - 292, 530, referencia, GRIS_SUAVE, 2)

    # Módulo de adquisición: la lectura automática, su único caso de uso.
    caja_con_texto(
        dibujo, ancho - 290, 40, 250, 140, ["Módulo de", "adquisición"], 20, NARANJA_CLARO, NARANJA, negrita=True,
    )
    unir(ancho - 292, 110, DISPOSITIVO, NARANJA, 3)

    texto_centrado(
        dibujo,
        "Cada caso de uso corresponde a un requisito funcional del apartado 2.3.2.",
        0, 1004, ancho, 18, GRIS,
    )
    texto_centrado(
        dibujo,
        "El Administrador configura el sistema; el Operador registra las mediciones, atiende las alertas y consulta.",
        0, 1036, ancho, 18, GRIS,
    )

    imagen.save(SALIDA / "11-casos-de-uso.png")
    print("Figura generada: 11-casos-de-uso.png")


# ---------------------------------------------------------------------------
# 3. Secuencia del registro de una lectura (apartados 2.4.4 y 2.6)
# ---------------------------------------------------------------------------

PARTICIPANTES = ["Módulo de adquisición", "API del servicio", "Base de datos", "Regla de negocio"]

MENSAJES = [
    (0, 1, "POST /api/v1/lecturas con X-Device-Key, variable, valor y marca de tiempo", "ida"),
    (1, 1, "verifica la clave y valida los datos de entrada", "propio"),
    (1, 0, "401 o 422 con el campo rechazado; no se almacena nada", "vuelta"),
    (1, 2, "consulta el módulo y el rango vigente de su perfil", "ida"),
    (2, 1, "módulo y rango de referencia", "vuelta"),
    (1, 3, "evalúa el valor contra el rango", "ida"),
    (3, 1, "estado del valor: dentro, bajo o alto", "vuelta"),
    (1, 2, "almacena la lectura con su estado y su origen", "ida"),
    (1, 2, "crea la alerta referenciada a la lectura", "ida"),
    (1, 0, "201 con la lectura almacenada", "vuelta"),
]


def diagrama_secuencia():
    ancho, alto = 1500, 1180
    imagen = Image.new("RGB", (ancho, alto), BLANCO)
    dibujo = ImageDraw.Draw(imagen)

    margen = 60
    ancho_carril = (ancho - 2 * margen) / len(PARTICIPANTES)
    centros = [margen + ancho_carril * (i + 0.5) for i in range(len(PARTICIPANTES))]

    for indice, (participante, centro) in enumerate(zip(PARTICIPANTES, centros)):
        color = VERDE if indice in (0, 3) else (BLANCO if indice == 1 else GRIS_CAJA)
        caja_con_texto(dibujo, centro - 165, 40, 330, 86, [participante], 19, color, VERDE if indice == 1 else GRIS_BORDE, negrita=True)
        y_fin = 1080
        for paso in range(120, y_fin, 16):
            dibujo.line([centro, paso, centro, paso + 8], fill=GRIS_BORDE, width=1)

    # Marco de la condición y de la opción.
    caja(dibujo, margen - 10, 214, ancho - 2 * margen + 20, 214, BLANCO, GRIS_BORDE, radio=8, grosor=2)
    etiqueta(dibujo, "alt  La petición no es válida", margen + 70, 214, 17, GRIS, BLANCO)
    caja(dibujo, margen - 10, 786, ancho - 2 * margen + 20, 108, BLANCO, GRIS_BORDE, radio=8, grosor=2)
    etiqueta(dibujo, "opt  El valor quedó fuera del rango", margen + 130, 786, 17, GRIS, BLANCO)

    y = 170
    for origen, destino, texto, tipo in MENSAJES:
        if tipo == "propio":
            x = centros[origen]
            dibujo.line([x, y, x + 60, y, x + 60, y + 26, x + 4, y + 26], fill=GRIS, width=2)
            flecha(dibujo, x + 12, y + 26, x + 2, y + 26, GRIS, 2)
            dibujo.text((x + 76, y + 2), texto, font=fuente(17), fill=GRIS)
        else:
            color = VERDE if tipo == "ida" else NARANJA
            flecha(dibujo, centros[origen], y, centros[destino], y, color, 2, 11, tipo == "vuelta")
            medio = (centros[origen] + centros[destino]) / 2
            etiqueta(dibujo, texto, medio, y - 14, 17, color)
        y += 62

    texto_centrado(
        dibujo,
        "El servicio valida, decide y almacena; el dispositivo solo mide y publica.",
        0, 1120, ancho, 18, GRIS,
    )

    imagen.save(SALIDA / "12-secuencia-del-registro.png")
    print("Figura generada: 12-secuencia-del-registro.png")


def main() -> None:
    SALIDA.mkdir(exist_ok=True)
    diagrama_arquitectura()
    diagrama_casos_de_uso()
    diagrama_secuencia()
    print("Diagramas escritos en", SALIDA.resolve())


if __name__ == "__main__":
    main()
