# -*- coding: utf-8 -*-
"""Simulador del módulo de adquisición (ESP32) — SI.G.VA.C.H.

Este programa **hace de dispositivo**: se autentica con la clave del módulo de
adquisición (`X-Device-Key`) y publica lecturas en el servicio, exactamente como
lo hará el ESP32. Sirve para dos cosas:

1. **Demostrar el flujo completo** sin hardware: la lectura entra por la misma
   puerta que usará el dispositivo, se almacena y se evalúa contra el rango del
   perfil de cultivo, de modo que una alerta aparece en el panel de la aplicación.
2. **Probar el comportamiento del dispositivo** ante las condiciones reales del
   servicio: el arranque en frío de la capa gratuita (hasta 60 s en la primera
   petición) y los cortes momentáneos. El programa **guarda en memoria** las
   lecturas que no pudo enviar y las reintenta, que es lo que debe hacer el
   firmware para no perder mediciones.

Uso
---
    # Un envío de las siete variables (el más útil para la demostración)
    python scripts/simulador_dispositivo.py --modulo MOD-001 --ciclos 1

    # Envío continuo cada 30 s, contra el servicio publicado
    python scripts/simulador_dispositivo.py --url https://sigvach-api.onrender.com \\
        --modulo MOD-001 --intervalo 30

    # Forzar un valor fuera de rango para que se genere una alerta
    python scripts/simulador_dispositivo.py --modulo MOD-001 --ciclos 1 --fuera-de-rango ph

    # Ver los módulos registrados (para saber qué pasar en --modulo)
    python scripts/simulador_dispositivo.py --listar-modulos

La clave se lee del entorno (`DEVICE_API_KEY`) o de los archivos `.env` del
proyecto. **Nunca se escribe en el código ni se imprime en pantalla.**
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
ARCHIVOS_ENV = (RAIZ_PROYECTO / "backend" / ".env", RAIZ_PROYECTO / ".env")

RUTA_LECTURAS = "/api/v1/lecturas"
RUTA_MODULOS = "/api/v1/modulos"

# Valor de referencia y dispersión de cada variable, con sus límites físicos.
# Los valores se generan alrededor del centro con una dispersión pequeña, para
# que la serie se vea como una medición real y no como una constante.
PERFILES = {
    "ph": ("pH", "", 6.10, 0.18, 0.0, 14.0),
    "tds": ("Sólidos disueltos totales", "ppm", 780.0, 25.0, 0.0, 5000.0),
    "ec": ("Conductividad eléctrica", "mS/cm", 1.60, 0.06, 0.0, 20.0),
    "temp_solucion": ("Temperatura de la solución", "°C", 21.0, 0.7, -10.0, 60.0),
    "temp_ambiental": ("Temperatura ambiental", "°C", 24.0, 1.2, -20.0, 70.0),
    "humedad": ("Humedad relativa", "%", 62.0, 3.0, 0.0, 100.0),
}

# Valor que se envía cuando se pide forzar una desviación. Está fuera de los
# rangos agronómicos habituales de los perfiles de cultivo, de modo que el
# servicio debe generar la alerta correspondiente.
FUERA_DE_RANGO = {
    "ph": 4.30,
    "tds": 1650.0,
    "ec": 3.60,
    "temp_solucion": 31.5,
    "temp_ambiental": 39.0,
    "humedad": 24.0,
}


# --------------------------------------------------------------------------- #
# Configuración
# --------------------------------------------------------------------------- #
def leer_env(ruta: Path) -> dict[str, str]:
    """Lee un archivo .env de forma tolerante (sin dependencias externas)."""
    valores: dict[str, str] = {}
    if not ruta.exists():
        return valores
    for linea in ruta.read_text(encoding="utf-8", errors="replace").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        nombre, valor = linea.split("=", 1)
        valores[nombre.strip()] = valor.strip().strip('"').strip("'")
    return valores


def obtener_clave(argumento: str | None) -> str:
    """Resuelve la clave del dispositivo: argumento, entorno o .env."""
    if argumento:
        return argumento
    if os.environ.get("DEVICE_API_KEY"):
        return os.environ["DEVICE_API_KEY"].strip()
    for ruta in ARCHIVOS_ENV:
        valor = leer_env(ruta).get("DEVICE_API_KEY", "")
        if valor:
            return valor
    return ""


def peticion(url: str, metodo: str, cuerpo: dict | None, clave: str | None, espera: float):
    """Realiza una petición HTTP y devuelve (código, cuerpo decodificado)."""
    datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
    cabeceras = {"Content-Type": "application/json"}
    if clave:
        cabeceras["X-Device-Key"] = clave
    peticion_http = urllib.request.Request(url, data=datos, headers=cabeceras, method=metodo)
    try:
        with urllib.request.urlopen(peticion_http, timeout=espera) as respuesta:
            return respuesta.status, respuesta.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", "replace")
    except Exception as error:  # noqa: BLE001 - se informa y se reintenta
        return 0, "%s: %s" % (type(error).__name__, error)


def listar_modulos(url: str, clave_servicio: str) -> int:
    """Muestra los módulos registrados, para saber qué pasar en --modulo.

    Se consulta la base de datos con la cuenta de servicio (el servicio
    publicado exige un token de usuario para esta ruta, que el simulador no
    tiene). Es una ayuda de operación, no parte de la demostración.
    """
    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import service_account
    except ModuleNotFoundError:
        print("Para listar los módulos hace falta el paquete google-auth.")
        return 1

    ruta_clave = Path(
        os.environ.get("CREDENCIALES_SERVICIO")
        or r"C:\Users\FREDDY\credenciales-sigvach\serviceAccountKey.json"
    )
    if not ruta_clave.exists():
        print("No se encontró la credencial de servicio en %s" % ruta_clave)
        return 1

    proyecto = os.environ.get("FIREBASE_PROJECT_ID", "sigvach26-bd")
    base = "https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents" % proyecto
    credencial = service_account.Credentials.from_service_account_file(
        str(ruta_clave), scopes=["https://www.googleapis.com/auth/datastore"]
    )
    credencial.refresh(Request())

    peticion_http = urllib.request.Request(
        "%s/modulos_cultivo?pageSize=20" % base,
        headers={"Authorization": "Bearer %s" % credencial.token},
    )
    try:
        with urllib.request.urlopen(peticion_http, timeout=45) as respuesta:
            cuerpo = respuesta.read().decode("utf-8", "replace")
    except Exception as error:  # noqa: BLE001
        print("No se pudo consultar la base: %s" % error)
        return 1

    documentos = json.loads(cuerpo).get("documents", [])
    if not documentos:
        print("No hay módulos registrados todavía. Créelos desde la aplicación.")
        return 1
    print("Módulos registrados (use el identificador de la última columna):")
    print("")
    print("  %-26s %-22s %s" % ("NOMBRE", "TIPO DE CULTIVO", "IDENTIFICADOR"))
    for documento in documentos:
        campos = documento.get("fields", {})
        nombre = campos.get("nombre", {}).get("stringValue", "(sin nombre)")
        tipo = campos.get("tipo_cultivo", {}).get("stringValue", "")
        identificador = documento["name"].rsplit("/", 1)[-1]
        print("  %-26s %-22s %s" % (nombre[:26], tipo[:22], identificador))
    print("")
    print("Ejemplo:  python scripts/simulador_dispositivo.py --modulo %s --ciclos 1"
          % documentos[0]["name"].rsplit("/", 1)[-1])
    return 0


# --------------------------------------------------------------------------- #
# Generación de lecturas
# --------------------------------------------------------------------------- #
def generar_valor(variable: str, forzada: str | None) -> float:
    """Genera el valor de una variable; si está forzada, devuelve el de desviación."""
    _, _, centro, dispersion, minimo, maximo = PERFILES[variable]
    if forzada == variable:
        valor = FUERA_DE_RANGO[variable]
    else:
        valor = random.gauss(centro, dispersion)
    return round(max(minimo, min(maximo, valor)), 2)


def preparar_lecturas(modulo: str, variables: list[str], forzada: str | None) -> list[dict]:
    """Arma el cuerpo de las lecturas de un ciclo, una por variable."""
    momento = datetime.now(timezone.utc).isoformat()
    return [
        {
            "modulo_id": modulo,
            "variable": variable,
            "valor": generar_valor(variable, forzada),
            "unidad": PERFILES[variable][1],
            "timestamp": momento,
        }
        for variable in variables
    ]


# --------------------------------------------------------------------------- #
# Programa principal
# --------------------------------------------------------------------------- #
def main() -> int:
    analizador = argparse.ArgumentParser(
        description="Simula el módulo de adquisición (ESP32) de SI.G.VA.C.H.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    analizador.add_argument("--url", default=os.environ.get("SIGVACH_API", "http://127.0.0.1:8011"),
                            help="Dirección del servicio (por omisión, el servicio local)")
    analizador.add_argument("--modulo", default="", help="Identificador del módulo de cultivo")
    analizador.add_argument("--clave", default=None, help="Clave del dispositivo (por omisión, del .env)")
    analizador.add_argument("--variable", action="append", default=[],
                            help="Enviar solo esta variable (se puede repetir)")
    analizador.add_argument("--fuera-de-rango", default=None, choices=sorted(PERFILES),
                            help="Forzar esta variable fuera de rango, para generar una alerta")
    analizador.add_argument("--intervalo", type=float, default=30.0,
                            help="Segundos entre ciclos de envío (por omisión, 30)")
    analizador.add_argument("--ciclos", type=int, default=0,
                            help="Cantidad de ciclos; 0 significa sin límite")
    analizador.add_argument("--reintentos", type=int, default=4,
                            help="Intentos por lectura cuando el servicio no responde")
    analizador.add_argument("--espera-reintento", type=float, default=5.0,
                            help="Segundos antes del primer reintento; luego se duplica hasta 30")
    analizador.add_argument("--espera", type=float, default=75.0,
                            help="Espera máxima por petición, en segundos (cubre el arranque en frío)")
    analizador.add_argument("--listar-modulos", action="store_true",
                            help="Mostrar los módulos registrados y salir")
    argumentos = analizador.parse_args()

    if argumentos.listar_modulos:
        return listar_modulos(argumentos.url, argumentos.clave or "")

    clave = obtener_clave(argumentos.clave)
    if not clave:
        print("Falta la clave del dispositivo.")
        print("Defínala en el archivo .env del proyecto (DEVICE_API_KEY) o pásela con --clave.")
        return 1
    if not argumentos.modulo:
        print("Falta el módulo de cultivo. Use --modulo o consulte --listar-modulos.")
        return 1

    variables = argumentos.variable or list(PERFILES)
    desconocidas = [v for v in variables if v not in PERFILES]
    if desconocidas:
        print("Variable no reconocida: %s" % ", ".join(desconocidas))
        print("Admitidas: %s" % ", ".join(sorted(PERFILES)))
        return 1

    base = argumentos.url.rstrip("/")
    print("=" * 78)
    print(" Simulador del módulo de adquisición — SI.G.VA.C.H.")
    print("=" * 78)
    print("  Servicio:        %s" % base)
    print("  Módulo:          %s" % argumentos.modulo)
    print("  Variables:       %s" % ", ".join(variables))
    print("  Clave:           %d caracteres (no se muestra)" % len(clave))
    print("  Intervalo:       %s" % ("un solo ciclo" if argumentos.ciclos == 1
                                     else "%.0f s" % argumentos.intervalo))
    if argumentos.fuera_de_rango:
        print("  Desviación:      %s = %s (debe generar alerta)"
              % (argumentos.fuera_de_rango, FUERA_DE_RANGO[argumentos.fuera_de_rango]))
    print("")
    print("  El dispositivo guarda en memoria las lecturas que no puede enviar y")
    print("  las reintenta: así no se pierde ninguna medición si el servicio")
    print("  está arrancando (hasta 60 s en la capa gratuita) o se corta la red.")
    print("")

    pendientes: list[dict] = []
    estadisticas = {"intentadas": 0, "almacenadas": 0, "desviadas": 0,
                    "reintentadas": 0, "rechazadas": 0}
    ciclo = 0

    try:
        while argumentos.ciclos == 0 or ciclo < argumentos.ciclos:
            ciclo += 1
            print("[%s] ciclo %d" % (datetime.now().strftime("%H:%M:%S"), ciclo))

            # Primero se intenta vaciar lo que quedó en memoria del dispositivo.
            if pendientes:
                print("  quedan %d lecturas en memoria: se reintentan" % len(pendientes))
                pendientes = enviar_pendientes(pendientes, base, clave, argumentos, estadisticas)

            for lectura in preparar_lecturas(argumentos.modulo, variables, argumentos.fuera_de_rango):
                pendientes = enviar_lectura(lectura, base, clave, argumentos, estadisticas, pendientes)

            print("")
            if argumentos.ciclos == 0 or ciclo < argumentos.ciclos:
                time.sleep(argumentos.intervalo)
    except KeyboardInterrupt:
        print("")
        print("  Interrumpido por el usuario.")

    print("=" * 78)
    print(" Resumen")
    print("=" * 78)
    print("  Lecturas intentadas:                  %d" % estadisticas["intentadas"])
    print("  Almacenadas por el servicio (201):    %d" % estadisticas["almacenadas"])
    print("  Con estado fuera de rango:            %d" % estadisticas["desviadas"])
    print("  Recuperadas tras reintentar:          %d" % estadisticas["reintentadas"])
    print("  Rechazadas por el contrato (422):     %d" % estadisticas["rechazadas"])
    print("  Sin enviar (quedaron en memoria):     %d" % len(pendientes))
    print("")
    return 0 if not pendientes else 2


def enviar_pendientes(pendientes: list[dict], base: str, clave: str, argumentos, estadisticas) -> list[dict]:
    """Reintenta las lecturas guardadas; devuelve las que siguen sin enviarse."""
    restantes: list[dict] = []
    for lectura in pendientes:
        estadisticas["intentadas"] += 1
        codigo, _ = peticion("%s%s" % (base, RUTA_LECTURAS), "POST", lectura, clave, argumentos.espera)
        if codigo == 201:
            estadisticas["almacenadas"] += 1
            estadisticas["reintentadas"] += 1
            print("    recuperada: %-14s %s" % (lectura["variable"], lectura["valor"]))
        elif codigo in (0, 500, 502, 503, 504):
            restantes.append(lectura)
        else:
            estadisticas["rechazadas"] += 1
    return restantes


def enviar_lectura(lectura: dict, base: str, clave: str, argumentos, estadisticas, pendientes: list[dict]):
    """Envía una lectura con reintentos; si no lo logra, la deja en memoria."""
    variable = lectura["variable"]
    _, unidad, _, _, _, _ = PERFILES[variable]
    espera_reintento = argumentos.espera_reintento

    for intento in range(1, argumentos.reintentos + 1):
        estadisticas["intentadas"] += 1
        codigo, cuerpo = peticion("%s%s" % (base, RUTA_LECTURAS), "POST", lectura, clave, argumentos.espera)

        if codigo == 201:
            datos = json.loads(cuerpo) if cuerpo.strip().startswith("{") else {}
            estado = datos.get("estado_rango") or "sin_rango"
            estadisticas["almacenadas"] += 1
            if estado in ("bajo", "alto"):
                estadisticas["desviadas"] += 1
            print("    %-15s %8s %-6s  201  %s" % (variable, lectura["valor"], unidad, estado))
            return pendientes

        if codigo == 401:
            print("")
            print("  La clave del dispositivo fue rechazada (401).")
            print("  Revise DEVICE_API_KEY en el .env y que coincida con la del servicio.")
            raise SystemExit(1)

        if codigo == 422:
            estadisticas["rechazadas"] += 1
            print("    %-15s rechazada por el contrato (422): %s" % (variable, cuerpo[:110]))
            return pendientes

        # Servicio arrancando, red corta o error del servidor: se reintenta.
        print("    %-15s intento %d/%d sin respuesta (código %s); reintento en %.0f s"
              % (variable, intento, argumentos.reintentos, codigo or "sin conexión", espera_reintento))
        if intento < argumentos.reintentos:
            time.sleep(espera_reintento)
            espera_reintento = min(espera_reintento * 2, 30.0)

    print("    %-15s queda en la memoria del dispositivo" % variable)
    pendientes.append(lectura)
    return pendientes


if __name__ == "__main__":
    sys.exit(main())
