# -*- coding: utf-8 -*-
"""Genera el diagrama de conexionado del módulo de adquisición (ESP32 + sensores).

Se dibuja con Pillow, sin dependencias gráficas externas, para poder regenerarlo
cuando cambie alguna pieza del montaje. La salida queda en
`Prototipo ESP32/diagrama de conexionado.png`.

Criterios de dibujo:
  · el color del cable indica su función y coincide con el color del recuadro del
    pin en cada sensor: la correspondencia se lee sin ambigüedad;
  · cada red tiene su propio canal vertical, de modo que los cables no se encimen;
  · el divisor de tensión del pH se marca sobre el cable y se detalla en un panel
    aparte, para no llenar el área de cables con símbolos;
  · las piezas que NO se conectan a la placa se declaran aparte, para que nadie las
    conecte por error.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ANCHO, ALTO = 2400, 2380
SALIDA = Path(__file__).resolve().parent / "diagrama de conexionado.png"

ROJO = (198, 40, 40)        # 5 V
NARANJA = (230, 110, 10)    # 3,3 V
NEGRO = (30, 30, 30)        # masa
AZUL = (21, 101, 192)       # señal analógica
VERDE = (27, 120, 55)       # señal digital
GRIS = (150, 150, 150)      # no se usa
TINTA = (33, 33, 33)
AZUL_OSCURO = (20, 40, 110)
FONDO_CAJA = (240, 244, 248)
FONDO_PLACA = (226, 232, 240)

FUENTE = r"C:\Windows\Fonts\arial.ttf"
FUENTE_NEGRITA = r"C:\Windows\Fonts\arialbd.ttf"


def fuente(tamano: int, negrita: bool = False):
    return ImageFont.truetype(FUENTE_NEGRITA if negrita else FUENTE, tamano)


def caja(dibujo, x1, y1, x2, y2, relleno, borde=TINTA, grosor=3, radio=18):
    dibujo.rounded_rectangle([x1, y1, x2, y2], radius=radio, fill=relleno,
                             outline=borde, width=grosor)


def texto(dibujo, x, y, contenido, tamano=26, color=TINTA, negrita=False, centrado=False):
    f = fuente(tamano, negrita)
    if centrado:
        x = x - dibujo.textlength(contenido, font=f) / 2
    dibujo.text((x, y), contenido, font=f, fill=color)


def cable(dibujo, puntos, color, grosor=5):
    dibujo.line(puntos, fill=color, width=grosor, joint="curve")


def union(dibujo, x, y, color, radio=9):
    dibujo.ellipse([x - radio, y - radio, x + radio, y + radio], fill=color)


def masa(dibujo, x, y):
    """Símbolo de masa: tres barras decrecientes."""
    dibujo.line([x - 34, y, x + 34, y], fill=NEGRO, width=6)
    dibujo.line([x - 22, y + 13, x + 22, y + 13], fill=NEGRO, width=6)
    dibujo.line([x - 11, y + 26, x + 11, y + 26], fill=NEGRO, width=6)


COLOR_PIN = {"analógica": AZUL, "digital": VERDE, "5 V": ROJO, "3,3 V": NARANJA, "masa": NEGRO}

# --------------------------------------------------------------------------- #
#  Lienzo, título y leyenda
# --------------------------------------------------------------------------- #
imagen = Image.new("RGB", (ANCHO, ALTO), "white")
d = ImageDraw.Draw(imagen)

texto(d, 80, 40, "SI.G.VA.C.H. — Conexionado del módulo de adquisición", 52, AZUL_OSCURO, True)
texto(d, 80, 105, "ESP32 sobre placa de expansión · seis variables automáticas · el nivel de agua se registra de forma manual",
      28, TINTA)
d.line([80, 152, ANCHO - 80, 152], fill=(200, 200, 200), width=3)

x_leyenda = 80
for color, etiqueta in [
    (ROJO, "5 V (placas de pH y TDS)"),
    (NARANJA, "3,3 V (DS18B20 y DHT22)"),
    (NEGRO, "Masa común (GND)"),
    (AZUL, "Señal analógica"),
    (VERDE, "Señal digital"),
]:
    d.rectangle([x_leyenda, 182, x_leyenda + 46, 202], fill=color)
    texto(d, x_leyenda + 58, 174, etiqueta, 24, TINTA)
    x_leyenda += 58 + int(d.textlength(etiqueta, font=fuente(24))) + 55

# --------------------------------------------------------------------------- #
#  Placa de expansión (izquierda)
# --------------------------------------------------------------------------- #
caja(d, 80, 260, 700, 1620, FONDO_PLACA, (60, 70, 90), 4)
texto(d, 110, 282, "Placa de expansión + ESP32", 32, AZUL_OSCURO, True)
caja(d, 120, 340, 660, 520, (38, 50, 56), (20, 20, 20), 3, 10)
texto(d, 145, 370, "ESP32-WROOM-32", 34, (255, 255, 255), True)
texto(d, 145, 415, "(38 pines)", 26, (200, 210, 215))
texto(d, 145, 455, "USB / DC 6,5–16 V", 24, (200, 210, 215))
texto(d, 110, 560, "Pines que se usan (guiarse por el rótulo):", 26, TINTA, True)

PINES = [
    ("SVP  ·  GPIO 36", "analógica", 640),
    ("SVN  ·  GPIO 39", "analógica", 740),
    ("P32", "digital", 850),
    ("P33", "digital", 950),
    ("5V", "5 V", 1070),
    ("3,3V", "3,3 V", 1170),
    ("GND", "masa", 1270),
]
for etiqueta, funcion, y in PINES:
    color = COLOR_PIN[funcion]
    caja(d, 400, y - 26, 660, y + 26, (255, 255, 255), color, 4, 10)
    texto(d, 420, y - 18, etiqueta, 28, TINTA, True)
    union(d, 660, y, color, 8)

texto(d, 110, 1350, "No se usan:", 26, TINTA, True)
for i, etiqueta in enumerate(["P25 · P26 (ultrasónico, fuera del montaje)",
                              "P34 · P35 · P12 · P13 · P14 · P27"]):
    caja(d, 110, 1390 + i * 66, 660, 1446 + i * 66, (245, 245, 245), GRIS, 2, 10)
    texto(d, 130, 1402 + i * 66, etiqueta, 24, (110, 110, 110))
texto(d, 110, 1540, "El orden físico en la placa es otro;", 22, (110, 110, 110))
texto(d, 110, 1568, "guiarse siempre por el rótulo del pin.", 22, (110, 110, 110))

# --------------------------------------------------------------------------- #
#  Sensores (derecha)
# --------------------------------------------------------------------------- #
SENSORES = [
    ("PH-4502C  +  electrodo BNC", "pH de la solución", 260, 610, [
        ("V+", "5 V", 380),
        ("G", "masa", 450),
        ("Po", "analógica", 520),
    ]),
    ("TDS Meter V1.0  +  sonda", "sólidos disueltos y conductividad", 650, 1000, [
        ("VCC", "5 V", 780),
        ("GND", "masa", 850),
        ("AOUT", "analógica", 920),
    ]),
    ("DS18B20", "temperatura de la solución", 1040, 1390, [
        ("rojo · VDD", "3,3 V", 1170),
        ("amarillo · datos", "digital", 1240),
        ("negro · GND", "masa", 1310),
    ]),
    ("AM2302  ·  DHT22", "temperatura ambiental y humedad (sensor del cable)", 1430, 1780, [
        ("rojo · VDD", "3,3 V", 1560),
        ("amarillo · datos", "digital", 1630),
        ("negro · GND", "masa", 1700),
    ]),
]

for titulo, subtitulo, y1, y2, pines in SENSORES:
    caja(d, 1560, y1, 2330, y2, FONDO_CAJA, (90, 100, 120), 4)
    texto(d, 1590, y1 + 20, titulo, 32, AZUL_OSCURO, True)
    texto(d, 1590, y1 + 62, subtitulo, 24, (95, 95, 95))
    for pin, funcion, y in pines:
        color = COLOR_PIN[funcion]
        caja(d, 1580, y - 24, 1830, y + 24, (255, 255, 255), color, 4, 10)
        texto(d, 1600, y - 16, pin, 26, TINTA, True)

# --------------------------------------------------------------------------- #
#  Cables: un canal vertical por red
# --------------------------------------------------------------------------- #
CANAL = {"5 V": 1010, "masa": 1080, "3,3 V": 980, "analógica": 1330, "digital": 1430}
CANAL_PH = 1240


def conectar(funcion, y_origen, y_destino, etiqueta_origen):
    color = COLOR_PIN[funcion]
    canal = CANAL[funcion]
    cable(d, [(660, y_origen), (canal, y_origen), (canal, y_destino), (1580, y_destino)], color)
    if etiqueta_origen:
        texto(d, 674, y_origen - 34, etiqueta_origen, 22, color, True)


conectar("5 V", 1070, 380, "5V")            # → PH-4502C
conectar("5 V", 1070, 780, None)            # → TDS Meter
conectar("3,3 V", 1170, 1170, "3,3V")       # → DS18B20
conectar("3,3 V", 1170, 1560, None)         # → DHT22
conectar("masa", 1270, 450, "GND")          # → PH-4502C
for y_destino in (850, 1310, 1700):         # → TDS, DS18B20 y DHT22
    conectar("masa", 1270, y_destino, None)
conectar("analógica", 740, 920, "SVN")      # → TDS AOUT
conectar("digital", 850, 1240, "P32")       # → DS18B20
conectar("digital", 950, 1630, "P33")       # → DHT22

# --- Señal del pH, con el divisor de tensión marcado sobre el cable -----------
cable(d, [(1580, 520), (1460, 520)], AZUL)
caja(d, 1310, 485, 1460, 555, (255, 255, 255), AZUL, 3, 10)
texto(d, 1385, 502, "DIVISOR ÷2", 26, AZUL, True, centrado=True)
cable(d, [(1310, 520), (CANAL_PH, 520), (CANAL_PH, 640), (660, 640)], AZUL)
texto(d, 674, 640 - 34, "SVP (GPIO 36)", 22, AZUL, True)
texto(d, 1280, 700, "ver detalle al pie", 22, (110, 110, 110))

# --- Resistencia de pull-up del AM2302, entre datos y 3,3 V -------------------
cable(d, [(1980, 1560), (1980, 1573)], NARANJA, 5)
caja(d, 1958, 1573, 2002, 1617, (255, 255, 255), TINTA, 3, 6)
cable(d, [(1980, 1617), (1980, 1630)], VERDE, 5)
union(d, 1980, 1560, NARANJA)
union(d, 1980, 1630, VERDE)
texto(d, 2016, 1578, "10 kΩ", 22, TINTA, True)
texto(d, 2016, 1612, "pull-up obligatorio", 22, (110, 110, 110))

# --------------------------------------------------------------------------- #
#  Recuadros inferiores
# --------------------------------------------------------------------------- #
caja(d, 80, 1850, 780, 2030, (255, 247, 240), (200, 120, 40), 4)
texto(d, 105, 1866, "NO se conectan a la placa", 28, (170, 90, 10), True)
texto(d, 105, 1912, "· Bomba 12 V (540 L/h): va a la red", 23, TINTA)
texto(d, 105, 1947, "  eléctrica o a un temporizador.", 23, TINTA)
texto(d, 105, 1982, "· Ultrasónico HC-SR04 y sonda NTC.", 23, TINTA)

caja(d, 810, 1850, 1560, 2030, (240, 248, 240), (40, 120, 60), 4)
texto(d, 835, 1866, "Antes de conectar, medir con el multímetro", 28, (25, 90, 45), True)
texto(d, 835, 1912, "1. Pin «3,3V» contra GND  →  3,3 V.", 23, TINTA)
texto(d, 835, 1947, "2. Pin «5V» contra GND  →  5 V.", 23, TINTA)
texto(d, 835, 1982, "3. Todavía sin sensores conectados.", 23, TINTA)

caja(d, 1590, 1850, 2330, 2030, (245, 240, 255), (110, 80, 180), 4)
texto(d, 1615, 1866, "No olvidar", 28, (90, 60, 160), True)
texto(d, 1615, 1912, "· Masa común: todos los GND al mismo", 23, TINTA)
texto(d, 1615, 1947, "  punto de la placa.", 23, TINTA)
texto(d, 1615, 1982, "· El pH y el TDS van a SVP y SVN.", 23, TINTA)

# --------------------------------------------------------------------------- #
#  Detalle del divisor de tensión del pH
# --------------------------------------------------------------------------- #
caja(d, 80, 2060, 2330, 2360, (238, 246, 255), AZUL, 4)
texto(d, 105, 2076, "Detalle del divisor de tensión del pH", 30, AZUL_OSCURO, True)
texto(d, 105, 2112, "La salida del PH-4502C llega a 5 V; el ESP32 tolera 3,3 V.", 24, TINTA)

linea_y = 2180
# Tramo de entrada, con la primera resistencia
texto(d, 130, linea_y + 26, "Po  (PH-4502C)", 22, AZUL, True)
cable(d, [(130, linea_y), (330, linea_y)], AZUL)
caja(d, 330, linea_y - 20, 430, linea_y + 20, (255, 255, 255), TINTA, 3, 6)
texto(d, 440, linea_y + 26, "10 kΩ", 22, TINTA, True)
# Punto de unión: una rama sigue a SVP y la otra baja a masa
cable(d, [(430, linea_y), (1180, linea_y)], AZUL)
union(d, 700, linea_y, AZUL)
texto(d, 900, linea_y - 48, "SVP · GPIO 36", 22, AZUL, True)
# Rama a masa, con la segunda resistencia
cable(d, [(700, linea_y), (700, linea_y + 22)], AZUL)
caja(d, 682, linea_y + 22, 718, linea_y + 92, (255, 255, 255), TINTA, 3, 6)
texto(d, 736, linea_y + 38, "10 kΩ", 22, TINTA, True)
cable(d, [(700, linea_y + 92), (700, linea_y + 112)], NEGRO)
masa(d, 700, linea_y + 116)
texto(d, 640, linea_y + 152, "GND", 22, NEGRO, True)

# Explicación, a la derecha del esquema
texto(d, 1300, 2140, "Cómo se conecta", 26, TINTA, True)
for i, linea in enumerate([
    "1. Del pin «Po» sale un cable a la primera resistencia.",
    "2. La unión de las dos resistencias va al pin «SVP».",
    "3. La segunda resistencia baja a GND.",
    "4. Sirven dos resistencias iguales, de 4,7 a 22 kΩ.",
]):
    texto(d, 1300, 2180 + i * 36, linea, 23, TINTA)

imagen.save(SALIDA)
imagen.save(SALIDA.with_suffix(".pdf"), resolution=200)
print("Diagrama generado:", SALIDA)
print("Versión para imprimir:", SALIDA.with_suffix(".pdf"))
print("Tamaño:", imagen.size)
