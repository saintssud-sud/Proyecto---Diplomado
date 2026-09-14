"""Verificador estructural del código Dart.

Existe porque en este entorno el analizador de Flutter no puede ejecutarse: la
herramienta necesita escribir fuera del proyecto y el entorno de ejecución lo
impide. Este verificador no sustituye al analizador —no comprueba tipos—, pero
detecta los tres defectos que más veces han aparecido al escribir las pantallas:

1. Un delimitador sin cerrar, que rompe el archivo completo.
2. Una importación relativa que ya no resuelve porque el archivo se movió.
3. Un campo declarado que nadie lee, que el analizador marca como `unused_field`.

Uso:

    python Proyecto SIGVACH/scripts/verificar_dart.py

Sin argumentos recorre `lib/` y `test/` del proyecto. Con rutas, revisa solo
esas. Con `--autoprueba`, se revisa a sí mismo contra los dos archivos de prueba
que viven en `scripts/` y comprueba que encuentra exactamente los defectos que
esos archivos tienen a propósito: un verificador que no encuentra nada también
podría estar simplemente roto, que es lo que le ocurrió a la primera versión.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Defectos que los archivos de prueba tienen a propósito, y que el verificador
# debe encontrar. Si alguno dejara de aparecer, el verificador estaría roto.
AUTOPRUEBA = {
    "scripts/_prueba_del_verificador.dart.txt": [
        "la importación 'paquete_que_no_existe.dart' no resuelve",
        "la importación '../ruta/inexistente.dart' no resuelve",
        "la clase _Caja declara 'sobrante' y nunca lo lee",
    ],
    "scripts/_prueba_del_verificador_delimitadores.dart.txt": [
        "'(' cerrado con '}'",
        "sin cerrar",
    ],
}

ABRE = {"(": ")", "[": "]", "{": "}"}
CIERRA = {v: k for k, v in ABRE.items()}


def quitar_literales(texto: str) -> str:
    """Enmascara cadenas y comentarios conservando la longitud del texto.

    Las cadenas y los comentarios pueden contener llaves y paréntesis sin que
    estos cuenten como estructura. Se sustituye su contenido por espacios —no se
    elimina— para que las posiciones del texto enmascarado coincidan con las del
    original: sin eso, cualquier tramo extraído por posición quedaría desfasado en
    cuanto apareciera una cadena antes, que es exactamente el defecto que tuvo la
    primera versión de este verificador.
    """
    salida = list(texto)
    i = 0
    largo = len(texto)

    def enmascarar(desde: int, hasta: int) -> None:
        for k in range(desde, min(hasta, largo)):
            if texto[k] != "\n":
                salida[k] = " "

    while i < largo:
        # Comentario de línea.
        if texto.startswith("//", i):
            fin = texto.find("\n", i)
            fin = largo if fin == -1 else fin
            enmascarar(i, fin)
            i = fin
            continue

        # Comentario de bloque (Dart permite anidarlos).
        if texto.startswith("/*", i):
            profundidad = 1
            j = i + 2
            while j < largo and profundidad > 0:
                if texto.startswith("/*", j):
                    profundidad += 1
                    j += 2
                elif texto.startswith("*/", j):
                    profundidad -= 1
                    j += 2
                else:
                    j += 1
            enmascarar(i, j)
            i = j
            continue

        crudo = texto[i] in "rR" and i + 1 < largo and texto[i + 1] in "\"'"
        posicion = i + 1 if crudo else i

        if posicion < largo and texto[posicion] in "\"'":
            comilla = texto[posicion]
            triple = texto.startswith(comilla * 3, posicion)
            cierre = comilla * (3 if triple else 1)
            j = posicion + len(cierre)
            while j < largo:
                if not crudo and texto[j] == "\\":
                    j += 2
                    continue
                if texto.startswith(cierre, j):
                    j += len(cierre)
                    break
                j += 1
            enmascarar(i, j)
            i = j
            continue

        i += 1

    return "".join(salida)


def verificar_delimitadores(ruta: Path, texto: str) -> list[str]:
    """Comprueba que cada delimitador cierre en el orden correcto."""
    plano = quitar_literales(texto)
    pila: list[tuple[str, int]] = []
    problemas: list[str] = []

    for posicion, caracter in enumerate(plano):
        if caracter in ABRE:
            pila.append((caracter, posicion))
        elif caracter in CIERRA:
            if not pila:
                problemas.append(
                    f"cierre '{caracter}' sin apertura (posición {posicion})"
                )
                continue
            abierto, _ = pila.pop()
            if ABRE[abierto] != caracter:
                problemas.append(
                    f"'{abierto}' cerrado con '{caracter}' (posición {posicion})"
                )

    for abierto, posicion in pila:
        problemas.append(f"'{abierto}' abierto en la posición {posicion} sin cerrar")

    return problemas


def verificar_importaciones(ruta: Path, texto: str) -> list[str]:
    """Comprueba que cada importación relativa apunte a un archivo existente."""
    problemas: list[str] = []
    for coincidencia in re.finditer(r"^import\s+'([^']+)'", texto, re.MULTILINE):
        destino = coincidencia.group(1)
        if destino.startswith("dart:") or destino.startswith("package:"):
            continue
        resuelto = (ruta.parent / destino).resolve()
        if not resuelto.exists():
            problemas.append(f"la importación '{destino}' no resuelve")
    return problemas


def bloques_de_clase(texto: str) -> list[tuple[str, str]]:
    """Devuelve el nombre y el cuerpo de cada clase declarada en el archivo."""
    plano = quitar_literales(texto)
    bloques: list[tuple[str, str]] = []

    for coincidencia in re.finditer(r"\bclass\s+(\w+)[^{]*\{", plano):
        nombre = coincidencia.group(1)
        inicio = coincidencia.end()
        profundidad = 1
        i = inicio
        while i < len(plano) and profundidad > 0:
            if plano[i] == "{":
                profundidad += 1
            elif plano[i] == "}":
                profundidad -= 1
            i += 1
        # El cuerpo se toma del texto original para poder citar nombres reales.
        bloques.append((nombre, texto[inicio : i - 1]))

    return bloques


def verificar_campos_sin_uso(ruta: Path, texto: str) -> list[str]:
    """Detecta campos que se declaran y nunca se leen.

    Un campo es privado —y por tanto no puede leerse desde fuera de la
    biblioteca— cuando su nombre empieza con guion bajo o cuando pertenece a una
    clase cuyo nombre empieza con guion bajo. En ambos casos el analizador avisa
    si nadie lo lee; el segundo es el que más se escapa al revisar a mano, porque
    el nombre del campo parece público.

    Los usos se cuentan en **todo el archivo** y no solo dentro de la clase: en
    Dart cada archivo es una biblioteca, así que un campo privado no puede leerse
    desde otro archivo, pero sí desde otra clase del mismo archivo. Contarlos
    solo dentro de la clase marcaba como no leídos los campos de un objeto de
    datos que otra clase del archivo consulta.
    """
    problemas: list[str] = []

    for nombre_clase, cuerpo in bloques_de_clase(texto):
        clase_privada = nombre_clase.startswith("_")
        declaraciones = re.findall(
            r"^\s*(?:final|const|late\s+final|var)\s+[\w<>?,\s\.]+\s+(\w+)\s*;",
            cuerpo,
            re.MULTILINE,
        )
        for campo in declaraciones:
            if not campo.startswith("_") and not clase_privada:
                continue

            patron = rf"\b{re.escape(campo)}\b"
            # Usos en todo el archivo.
            total = len(re.findall(patron, texto))
            # Se descuentan la declaración y los parámetros `this.campo`.
            total -= len(re.findall(rf"\bthis\.{re.escape(campo)}\b", texto))
            total -= len(
                re.findall(
                    rf"^\s*(?:final|const|late\s+final|var)\s+[\w<>?,\s\.]+\s+{re.escape(campo)}\s*;",
                    texto,
                    re.MULTILINE,
                )
            )

            if total <= 0:
                problemas.append(
                    f"la clase {nombre_clase} declara '{campo}' y nunca lo lee"
                )

    return problemas


def mostrar(archivo: Path) -> str:
    """Ruta del archivo relativa al proyecto, o tal cual si está fuera."""
    try:
        return str(archivo.relative_to(RAIZ))
    except ValueError:
        return str(archivo)


def autoprueba() -> int:
    """Comprueba que el verificador encuentra los defectos de los archivos de prueba."""
    fallos = 0
    for relativa, esperados in AUTOPRUEBA.items():
        archivo = RAIZ / relativa
        texto = archivo.read_text(encoding="utf-8")
        encontrados: list[str] = []
        encontrados += verificar_delimitadores(archivo, texto)
        encontrados += verificar_importaciones(archivo, texto)
        encontrados += verificar_campos_sin_uso(archivo, texto)

        for esperado in esperados:
            if any(esperado in hallazgo for hallazgo in encontrados):
                print(f"[ok] {relativa}: detecta «{esperado}»")
            else:
                fallos += 1
                print(f"[X]  {relativa}: NO detecta «{esperado}»")

    if fallos:
        print(f"\nLa autoprueba falló en {fallos} caso(s): el verificador no es fiable.")
        return 1

    print("\nLa autoprueba pasa: el verificador detecta lo que debe detectar.")
    return 0


def main(argumentos: list[str]) -> int:
    if argumentos and argumentos[0] == "--autoprueba":
        return autoprueba()

    if argumentos:
        archivos = [Path(a).resolve() for a in argumentos]
    else:
        archivos = sorted(
            list((RAIZ / "lib").rglob("*.dart")) + list((RAIZ / "test").rglob("*.dart"))
        )

    fallos = 0
    for archivo in archivos:
        texto = archivo.read_text(encoding="utf-8")
        problemas: list[str] = []
        problemas += verificar_delimitadores(archivo, texto)
        problemas += verificar_importaciones(archivo, texto)
        problemas += verificar_campos_sin_uso(archivo, texto)

        if problemas:
            fallos += len(problemas)
            print(f"[X] {mostrar(archivo)}")
            for problema in problemas:
                print(f"      - {problema}")

    if fallos:
        print(f"\n{fallos} problema(s) en {len(archivos)} archivo(s).")
        return 1

    print(f"Sin problemas estructurales en {len(archivos)} archivo(s) Dart.")
    return 0


if __name__ == "__main__":
    # La consola de Windows no usa UTF-8 por omisión y los mensajes llevan
    # acentos: sin esto, la salida se ve con caracteres cambiados.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main(sys.argv[1:]))
