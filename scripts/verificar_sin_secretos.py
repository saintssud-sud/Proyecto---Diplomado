# -*- coding: utf-8 -*-
"""Comprueba que el repositorio no exponga datos que no deben publicarse.

El repositorio es publico y lo revisa el docente, de modo que hay tres cosas que
nunca deben aparecer versionadas: la clave del dispositivo, las credenciales del
WiFi y las claves privadas de la cuenta de servicio de Firebase.

El script aprovecha que esos valores **si existen en el equipo**, aunque no se
versionen:

  · la clave del dispositivo esta en el archivo `.env`;
  · el nombre y la clave del WiFi estan en `hardware/firmware/main/configuracion.h`.

Asi no hay que adivinar ningun valor: se leen de donde estan y se busca ese
texto exacto en los archivos que el repositorio versiona y en todo el historial.

Tambien distingue un caso que a primera vista parece un problema y no lo es: la
**clave web de Firebase** en `lib/firebase_options.dart` y en
`google-services.json` es publica por diseno (viaja en la aplicacion que la usa),
de modo que se informa como esperada y no como fallo.

Uso:
    python scripts/verificar_sin_secretos.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

ENV = RAIZ / ".env"
CONFIGURACION = RAIZ / "hardware" / "firmware" / "main" / "configuracion.h"

# Archivos donde la clave web de Firebase es legitima y esperada.
CON_CLAVE_WEB_PERMITIDA = {
    "lib/firebase_options.dart",
    "android/app/google-services.json",
    ".env.example",
}

# Restos de credenciales que no deben versionarse nunca.
PROHIBIDOS = (
    ("clave privada de cuenta de servicio", "BEGIN PRIVATE KEY"),
    ("identificador de clave privada", "private_key_id"),
    ("contenido de una cuenta de servicio", '"type": "service_account"'),
)

# Asignaciones que solo son un problema si llevan un valor DE VERDAD.
#
# Ojo con esto: buscar solo el nombre de la variable daria falsos positivos,
# porque las plantillas (`.env.example` y `configuracion.ejemplo.h`) contienen
# justamente esos nombres con valores de ejemplo. Lo que delata un secreto es la
# asignacion con un valor real, no el nombre.
ASIGNACIONES = (
    ("nombre de la red WiFi", r'#define[ \t]+NOMBRE_WIFI[ \t]+"([^"]*)"'),
    ("clave de la red WiFi", r'#define[ \t]+CLAVE_WIFI[ \t]+"([^"]*)"'),
    ("clave del dispositivo en el firmware", r'#define[ \t]+CLAVE_DISPOSITIVO[ \t]+"([^"]*)"'),
    ("clave del dispositivo en el entorno", r'(?m)^[ \t]*DEVICE_API_KEY[ \t]*=[ \t]*(\S+)'),
    ("credencial de Firebase en el entorno", r'(?m)^[ \t]*FIREBASE_SERVICE_ACCOUNT_JSON[ \t]*=[ \t]*(\S+)'),
)

# Textos que identifican un valor de ejemplo y no un secreto.
#
# El patron de las asignaciones usa [ \t] y no \s a proposito: con \s se puede
# cruzar el salto de linea y, en una linea vacia, tomar como valor el NOMBRE de
# la variable siguiente. Ese error daba un falso positivo en `.env.example`.
MARCADORES = ("ESCRIBE-AQUI", "PEGAR-AQUI", "CLAVE-DE-TU", "NOMBRE-DE-TU",
              "TU-API", "TU-RED", "AQUI-LA-CLAVE", "cambiar-por", "CAMBIAR-POR",
              "cambiar por", "CAMBIAR POR", "ejemplo", "EJEMPLO", "demo", "DEMO")

TAMANO_MAXIMO = 400_000  # no se leen archivos mas grandes que esto


def git(*argumentos: str) -> tuple[int, str]:
    """Ejecuta git en la raiz del proyecto."""
    resultado = subprocess.run(
        ["git", "-C", str(RAIZ), *argumentos],
        capture_output=True, text=True, errors="replace",
    )
    return resultado.returncode, resultado.stdout


def archivos_versionados() -> list[str]:
    codigo, salida = git("ls-files")
    if codigo != 0:
        raise SystemExit("No se pudo consultar git. Ejecuta el script dentro del repositorio.")
    return [linea.strip() for linea in salida.splitlines() if linea.strip()]


def leer_valor(ruta: Path, etiqueta: str, desde_define: bool = False) -> tuple[str, str] | None:
    """Extrae el valor de una credencial del equipo, si existe."""
    if not ruta.exists():
        return None
    patron_define = '#define %s' % etiqueta
    for linea in ruta.read_text(encoding="utf-8", errors="replace").splitlines():
        limpia = linea.strip()
        if desde_define:
            if limpia.startswith(patron_define):
                valor = limpia.split('"')[1] if '"' in limpia else ""
                if valor and "ESCRIBE-AQUI" not in valor and "PEGAR-AQUI" not in valor:
                    return etiqueta, valor
        else:
            if limpia.startswith(etiqueta + "="):
                valor = limpia.split("=", 1)[1].strip().strip('"')
                if valor:
                    return etiqueta, valor
    return None


def main() -> int:
    print("=== VERIFICACION DE SECRETOS EN EL REPOSITORIO ===")
    print("")

    versionados = archivos_versionados()
    print("Archivos versionados: %d" % len(versionados))
    print("")

    fallos: list[str] = []
    avisos: list[str] = []

    # --- 1) que no se versione ningun .env --------------------------------
    print("=== 1) ARCHIVOS DE ENTORNO VERSIONADOS ===")
    entornos = [f for f in versionados
                if Path(f).name.startswith(".env") and Path(f).name != ".env.example"]
    if entornos:
        fallos.append("hay archivos de entorno versionados: %s" % ", ".join(entornos))
        print("  FALLA: %s" % ", ".join(entornos))
    else:
        print("  CORRECTO: ningun .env versionado (solo la plantilla .env.example).")

    # --- 2) valores reales del equipo, buscados en lo versionado ----------
    print("")
    print("=== 2) CREDENCIALES DEL EQUIPO QUE NO DEBEN ESTAR VERSIONADAS ===")
    credenciales = []
    for ruta, etiqueta, define in ((ENV, "DEVICE_API_KEY", False),
                                   (CONFIGURACION, "NOMBRE_WIFI", True),
                                   (CONFIGURACION, "CLAVE_WIFI", True)):
        hallada = leer_valor(ruta, etiqueta, define)
        if hallada:
            credenciales.append(hallada)
            print("  leida del equipo: %s (%d caracteres, no se muestra)" % (etiqueta, len(hallada[1])))
        else:
            print("  no se pudo leer: %s (no pasa nada: se omite su busqueda)" % etiqueta)

    if not credenciales:
        print("  AVISO: no se encontro ninguna credencial en el equipo; solo se revisaron los patrones.")

    for etiqueta, valor in credenciales:
        encontrados = []
        for archivo in versionados:
            ruta = RAIZ / archivo
            try:
                if ruta.stat().st_size > TAMANO_MAXIMO:
                    continue
                texto = ruta.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if valor in texto:
                encontrados.append(archivo)
        if encontrados:
            fallos.append("%s aparece en: %s" % (etiqueta, ", ".join(encontrados)))
            print("  FALLA: %s aparece en %s" % (etiqueta, ", ".join(encontrados)))
        else:
            print("  CORRECTO: %s no aparece en ningun archivo versionado." % etiqueta)

        # --- 3) y tampoco en el historial ----------------------------------
        codigo, salida = git("log", "--all", "-S", valor, "--oneline")
        commits = [l for l in salida.splitlines() if l.strip()]
        if commits:
            fallos.append("%s aparece en el historial (%d confirmacion/es)" % (etiqueta, len(commits)))
            print("  FALLA: %s aparece en el historial de git (%d confirmacion/es):" % (etiqueta, len(commits)))
            for linea in commits[:5]:
                print("     %s" % linea.strip())
        else:
            print("  CORRECTO: %s no aparece en el historial." % etiqueta)

    # --- 4) restos de credenciales por patron -----------------------------
    print("")
    print("=== 3) PATRONES QUE NUNCA DEBEN APARECER ===")
    for etiqueta, patron in PROHIBIDOS:
        encontrados = []
        for archivo in versionados:
            ruta = RAIZ / archivo
            try:
                if ruta.stat().st_size > TAMANO_MAXIMO:
                    continue
                texto = ruta.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if patron in texto:
                encontrados.append(archivo)
        if encontrados:
            fallos.append("%s (%s) en: %s" % (etiqueta, patron, ", ".join(encontrados)))
            print("  FALLA: %s -> %s" % (etiqueta, ", ".join(encontrados)))
        else:
            print("  CORRECTO: sin rastros de %s." % etiqueta)

    # --- 5) asignaciones con valor real ------------------------------------
    print("")
    print("=== 4) ASIGNACIONES CON VALOR REAL (las plantillas no cuentan) ===")
    for etiqueta, patron in ASIGNACIONES:
        encontrados = []
        for archivo in versionados:
            ruta = RAIZ / archivo
            try:
                if ruta.stat().st_size > TAMANO_MAXIMO:
                    continue
                texto = ruta.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for coincidencia in re.finditer(patron, texto):
                valor = coincidencia.group(1).strip()
                if not valor or any(marcador in valor for marcador in MARCADORES):
                    continue
                encontrados.append(archivo)
                break
        if encontrados:
            fallos.append("%s con valor real en: %s" % (etiqueta, ", ".join(encontrados)))
            print("  FALLA: %s -> %s" % (etiqueta, ", ".join(encontrados)))
        else:
            print("  CORRECTO: sin %s con valor real." % etiqueta)

    # --- 6) la clave web de Firebase, donde es legitima -------------------
    print("")
    print("=== 5) CLAVE WEB DE FIREBASE (PUBLICA POR DISENO) ===")
    fuera_de_sitio = []
    donde = set()
    for archivo in versionados:
        ruta = RAIZ / archivo
        try:
            if ruta.stat().st_size > TAMANO_MAXIMO:
                continue
            texto = ruta.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if "AIzaSy" in texto:
            donde.add(archivo)
            if archivo not in CON_CLAVE_WEB_PERMITIDA:
                fuera_de_sitio.append(archivo)
    if donde:
        print("  aparece en: %s" % ", ".join(sorted(donde)))
    if fuera_de_sitio:
        avisos.append("la clave web de Firebase aparece fuera de los archivos previstos: %s"
                      % ", ".join(fuera_de_sitio))
        print("  AVISO: ademas aparece en %s" % ", ".join(fuera_de_sitio))
    else:
        print("  CORRECTO: solo en los archivos donde es esperada y publica.")

    # --- conclusion -------------------------------------------------------
    print("")
    print("=== CONCLUSION ===")
    if avisos:
        print("  Avisos (%d):" % len(avisos))
        for aviso in avisos:
            print("    - %s" % aviso)
    if fallos:
        print("  Hay %d problema(s):" % len(fallos))
        for fallo in fallos:
            print("    - %s" % fallo)
        print("")
        print("  No subas el repositorio hasta resolverlo: una credencial publicada")
        print("  sigue siendo publica aunque se borre despues, porque queda en el historial.")
        return 1

    print("  El repositorio no expone la clave del dispositivo, ni las credenciales del")
    print("  WiFi, ni claves privadas. La clave web de Firebase esta donde corresponde.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
