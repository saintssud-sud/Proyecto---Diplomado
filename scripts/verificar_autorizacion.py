# -*- coding: utf-8 -*-
"""Comprueba en vivo la autorización del servicio, para mostrarlo en la tutoría.

Hace las comprobaciones que el docente pidió ver en la tutoría T4, contra el servicio
publicado y con las dos cuentas de prueba:

  1. Una ruta de administración sin token            -> 401
  2. La misma ruta con la cuenta de operador          -> 403
  3. La misma ruta con la cuenta de administrador     -> 200
  4. Una lectura del dispositivo con clave inválida   -> 401
  5. El monitor de salud del despliegue               -> 200

No escribe nada en la base de datos: el envío con clave inválida se rechaza antes de
llegar al repositorio.

Uso:
    python scripts/verificar_autorizacion.py
    python scripts/verificar_autorizacion.py --servicio http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EVIDENCIA = RAIZ / "evidencia"
SERVICIO_PUBLICADO = "https://sigvach-api.onrender.com"
CUENTA_ADMINISTRADOR = ("administrador@proyecto.test", "SIGVACH.Adm.2026")
CUENTA_OPERADOR = ("operador@proyecto.test", "SIGVACH.Ope.2026")

# La clave pública del proyecto web no se repite: se toma del programa de medición,
# que ya la declara.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from medir_rendimiento import CLAVE_WEB_FIREBASE  # noqa: E402


def pedir(url, cabeceras=None, cuerpo=None, metodo=None):
    peticion = urllib.request.Request(url, headers=cabeceras or {}, data=cuerpo, method=metodo)
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(peticion, timeout=120) as respuesta:
            return respuesta.status, respuesta.read().decode("utf-8", "replace"), time.perf_counter() - t0
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", "replace"), time.perf_counter() - t0
    except Exception as error:  # noqa: BLE001
        return 0, "%s: %s" % (type(error).__name__, error), time.perf_counter() - t0


def ingresar(correo: str, clave: str) -> str:
    cuerpo = json.dumps({"email": correo, "password": clave, "returnSecureToken": True}).encode()
    codigo, datos, _ = pedir(
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=%s"
        % CLAVE_WEB_FIREBASE,
        {"Content-Type": "application/json"},
        cuerpo,
    )
    if codigo != 200:
        raise SystemExit("No se pudo iniciar sesión con %s (%s): %s" % (correo, codigo, datos[:200]))
    return json.loads(datos)["idToken"]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("--servicio", default=SERVICIO_PUBLICADO)
    analizador.add_argument("--clave-administrador", default=CUENTA_ADMINISTRADOR[1])
    analizador.add_argument("--clave-operador", default=CUENTA_OPERADOR[1])
    argumentos = analizador.parse_args()
    servicio = argumentos.servicio.rstrip("/")

    lineas: list[str] = []
    def anotar(texto: str = "") -> None:
        print(texto)
        lineas.append(texto)

    anotar("VERIFICACIÓN DE LA AUTORIZACIÓN DEL SERVICIO")
    anotar("Fecha    : %s" % datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M"))
    anotar("Servicio : %s" % servicio)
    anotar("=" * 72)

    anotar("")
    anotar("Sesiones de prueba:")
    token_administrador = ingresar(CUENTA_ADMINISTRADOR[0], argumentos.clave_administrador)
    anotar("   %-32s rol administrador" % CUENTA_ADMINISTRADOR[0])
    token_operador = ingresar(CUENTA_OPERADOR[0], argumentos.clave_operador)
    anotar("   %-32s rol operador" % CUENTA_OPERADOR[0])

    ruta = "%s/api/v1/usuarios" % servicio
    anotar("")
    anotar("La ruta de administración es GET /api/v1/usuarios.")
    anotar("")

    resultados = []

    codigo, datos, segundos = pedir(ruta, {"Accept": "application/json"})
    anotar("1. SIN TOKEN")
    anotar("   -> HTTP %d en %.0f ms   %s" % (codigo, segundos * 1000,
                                             "correcto" if codigo == 401 else "REVISAR"))
    anotar("   respuesta: %s" % datos[:150])
    resultados.append(codigo == 401)

    codigo, datos, segundos = pedir(ruta, {"Authorization": "Bearer %s" % token_operador,
                                           "Accept": "application/json"})
    anotar("")
    anotar("2. CON LA CUENTA DE OPERADOR")
    anotar("   -> HTTP %d en %.0f ms   %s" % (codigo, segundos * 1000,
                                             "correcto" if codigo == 403 else "REVISAR"))
    anotar("   respuesta: %s" % datos[:200])
    resultados.append(codigo == 403)

    codigo, datos, segundos = pedir(ruta, {"Authorization": "Bearer %s" % token_administrador,
                                           "Accept": "application/json"})
    cuantos = len(json.loads(datos)) if codigo == 200 else 0
    anotar("")
    anotar("3. CON LA CUENTA DE ADMINISTRADOR")
    anotar("   -> HTTP %d en %.0f ms, %d cuentas   %s"
           % (codigo, segundos * 1000, cuantos, "correcto" if codigo == 200 else "REVISAR"))
    resultados.append(codigo == 200)

    # 4. el módulo de adquisición con una clave que no es la suya
    cuerpo = json.dumps({
        "modulo_id": "modulo-1",
        "variable": "ph",
        "valor": 6.2,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }).encode()
    codigo, datos, segundos = pedir(
        "%s/api/v1/lecturas" % servicio,
        {"Content-Type": "application/json", "X-Device-Key": "clave-invalida-de-prueba"},
        cuerpo,
    )
    anotar("")
    anotar("4. LECTURA DEL DISPOSITIVO CON CLAVE INVÁLIDA")
    anotar("   -> HTTP %d en %.0f ms   %s" % (codigo, segundos * 1000,
                                             "correcto" if codigo == 401 else "REVISAR"))
    anotar("   respuesta: %s" % datos[:200])
    anotar("   (no se registra nada: el rechazo ocurre antes de tocar la base)")
    resultados.append(codigo == 401)

    # 5. el monitor del despliegue
    codigo, datos, segundos = pedir("%s/api/v1/salud" % servicio, {"Accept": "application/json"})
    anotar("")
    anotar("5. MONITOR DEL DESPLIEGUE")
    anotar("   -> HTTP %d en %.0f ms   %s" % (codigo, segundos * 1000,
                                             "correcto" if codigo == 200 else "REVISAR"))
    anotar("   respuesta: %s" % datos[:200])
    resultados.append(codigo == 200)

    anotar("")
    anotar("=" * 72)
    anotar("RESULTADO: %d de %d comprobaciones con el resultado esperado."
           % (sum(resultados), len(resultados)))

    EVIDENCIA.mkdir(exist_ok=True)
    destino = EVIDENCIA / ("autorizacion-%s.txt" % datetime.now().strftime("%Y-%m-%d"))
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("")
    print("Evidencia guardada en %s" % destino.relative_to(RAIZ))
    return 0 if all(resultados) else 1


if __name__ == "__main__":
    raise SystemExit(main())
