"""Mide el rendimiento del servicio publicado y deja el informe con fecha.

Para qué existe
---------------
El requisito **RNF-01 (Rendimiento)** pide dos cosas medibles:

    · la API debe responder el **95 % de las consultas en 800 ms o menos**;
    · el panel debe mostrar el estado de las variables en **3 segundos o menos**.

Una medición sin número no se defiende, y un número sin el método tampoco: este
programa hace la primera parte y deja escrito con qué herramienta, cuántas
consultas y cuántos registros se midió.

Detalle importante sobre la capa gratuita: el servicio se suspende por
inactividad y la primera petición puede tardar hasta un minuto. Por eso se hace
un **calentamiento** antes de medir, y el informe lo declara: sin eso, la primera
consulta arruinaría la estadística y el número no describiría el sistema en uso.

Uso
---
    python scripts/medir_rendimiento.py --correo operador@proyecto.test --clave "SIGVACH.Ope.2026"

Las credenciales se pasan por línea de órdenes y no se guardan en ningún archivo.

Medir el antes y el después
---------------------------
Se mide siempre la misma máquina contra el mismo servicio: comparar el servicio
local con el publicado no diría nada del cambio, porque la red y la capa gratuita
pesan más que la optimización. Por eso hay tres opciones más:

    --servicio  dirección que se mide (por omisión, el servicio publicado);
    --sufijo    sufijo del nombre del informe, para distinguir el antes del después;
    --nota      una línea libre que queda escrita en el informe (por ejemplo, con
                qué configuración se midió y contra qué servicio).

El «antes» de la memoria intermedia se mide con la memoria desactivada, en el
mismo servicio y con el mismo comando:

    # Antes (sin memoria intermedia)
    $env:SEGUNDOS_CACHE_LECTURAS="0"; uvicorn app.main:app --port 8011
    python scripts/medir_rendimiento.py --servicio http://127.0.0.1:8011 \
        --sufijo -antes --correo ... --clave "..." --consultas 20 --limite 200

    # Después (con la memoria intermedia en su valor por omisión)
    python scripts/medir_rendimiento.py --servicio http://127.0.0.1:8011 \
        --sufijo -despues --correo ... --clave "..." --consultas 20 --limite 200
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

CLAVE_WEB_FIREBASE = "AIzaSyDA41lEpw0T6a7bTPq-dVab2lK8aOUHvDg"
SERVICIO = "https://sigvach-api.onrender.com"
LIMITE_OBJETIVO_MS = 800
SALIDA = Path(__file__).resolve().parent.parent / "evidencia"


def pedir(url: str, cabeceras: dict[str, str] | None = None, cuerpo: bytes | None = None):
    """Hace una petición y devuelve (segundos, código, bytes de la respuesta)."""
    peticion = urllib.request.Request(url, headers=cabeceras or {}, data=cuerpo)
    inicio = time.perf_counter()
    try:
        with urllib.request.urlopen(peticion, timeout=90) as respuesta:
            datos = respuesta.read()
            codigo = respuesta.status
    except urllib.error.HTTPError as error:
        datos = error.read()
        codigo = error.code
    return time.perf_counter() - inicio, codigo, datos


def ingresar(correo: str, clave: str) -> str:
    cuerpo = json.dumps(
        {"email": correo, "password": clave, "returnSecureToken": True}
    ).encode()
    _, codigo, datos = pedir(
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=%s"
        % CLAVE_WEB_FIREBASE,
        {"Content-Type": "application/json"},
        cuerpo,
    )
    if codigo != 200:
        raise SystemExit("No se pudo iniciar sesión (%s): %s" % (codigo, datos[:200]))
    return json.loads(datos)["idToken"]


def main() -> None:
    analizador = argparse.ArgumentParser(description="Mide el RNF-01 en el servicio publicado")
    analizador.add_argument("--correo", required=True)
    analizador.add_argument("--clave", required=True)
    analizador.add_argument("--consultas", type=int, default=20)
    analizador.add_argument("--limite", type=int, default=200)
    analizador.add_argument("--ruta", default="/api/v1/lecturas")
    analizador.add_argument(
        "--servicio",
        default=SERVICIO,
        help="Dirección del servicio que se mide (por omisión, el publicado)",
    )
    analizador.add_argument(
        "--sufijo",
        default="",
        help="Sufijo del nombre del informe, para distinguir el antes del después",
    )
    analizador.add_argument(
        "--nota",
        default="",
        help="Línea libre que queda escrita en el informe, con el contexto de la medición",
    )
    argumentos = analizador.parse_args()

    SALIDA.mkdir(parents=True, exist_ok=True)
    servicio = argumentos.servicio.rstrip("/")
    token = ingresar(argumentos.correo, argumentos.clave)
    cabeceras = {"Authorization": "Bearer %s" % token, "Accept": "application/json"}
    url = "%s%s?limite=%d" % (servicio, argumentos.ruta, argumentos.limite)

    lineas: list[str] = []
    lineas.append("INFORME DE RENDIMIENTO — RNF-01")
    lineas.append("Fecha    : %s" % datetime.now().strftime("%Y-%m-%d %H:%M"))
    lineas.append("Servicio : %s" % servicio)
    lineas.append("Consulta : GET %s?limite=%d" % (argumentos.ruta, argumentos.limite))
    lineas.append("Herramienta: este programa (urllib de Python 3), cronometraje con perf_counter")
    lineas.append("Objetivo : el 95 %% de las consultas en %d ms o menos" % LIMITE_OBJETIVO_MS)
    if argumentos.nota:
        lineas.append("Nota     : %s" % argumentos.nota)
    lineas.append("")

    # Calentamiento: despierta la instancia suspendida y no se mide.
    segundos_caliente, codigo, datos_caliente = pedir(url, cabeceras)
    lineas.append(
        "Calentamiento (no se mide): %.2f s, HTTP %s" % (segundos_caliente, codigo)
    )
    if codigo != 200:
        lineas.append("  AVISO: el calentamiento no respondió 200; la medición puede no servir.")
    registros = len(json.loads(datos_caliente)) if codigo == 200 else 0
    lineas.append("  registros devueltos por la consulta: %d" % registros)
    lineas.append("")

    tiempos: list[float] = []
    codigos: list[int] = []
    for numero in range(1, argumentos.consultas + 1):
        segundos, codigo, _ = pedir(url, cabeceras)
        tiempos.append(segundos)
        codigos.append(codigo)
        lineas.append(
            "  consulta %2d: %6.0f ms   HTTP %s" % (numero, segundos * 1000, codigo)
        )

    milisegundos = sorted(t * 1000 for t in tiempos)
    indice_p95 = max(0, int(round(0.95 * len(milisegundos))) - 1)
    p95 = milisegundos[indice_p95]
    dentro = sum(1 for valor in milisegundos if valor <= LIMITE_OBJETIVO_MS)

    lineas.append("")
    lineas.append("RESULTADOS (en milisegundos)")
    lineas.append("  consultas medidas      : %d" % len(milisegundos))
    lineas.append("  respuestas 200         : %d" % codigos.count(200))
    lineas.append("  mínima                 : %.0f" % milisegundos[0])
    lineas.append("  mediana                : %.0f" % statistics.median(milisegundos))
    lineas.append("  promedio               : %.0f" % statistics.mean(milisegundos))
    lineas.append("  percentil 95           : %.0f" % p95)
    lineas.append("  máxima                 : %.0f" % milisegundos[-1])
    lineas.append("  dentro del objetivo    : %d de %d (%.0f %%)"
                  % (dentro, len(milisegundos), 100 * dentro / len(milisegundos)))
    lineas.append("")
    veredicto = (
        "CUMPLE" if p95 <= LIMITE_OBJETIVO_MS and codigos.count(200) == len(codigos)
        else "NO CUMPLE"
    )
    lineas.append(
        "CONCLUSIÓN: %s el RNF-01 en su parte de API (percentil 95 = %.0f ms, objetivo %d ms)."
        % (veredicto, p95, LIMITE_OBJETIVO_MS)
    )
    lineas.append("")
    lineas.append("QUEDA PENDIENTE la otra mitad del RNF-01: que el panel muestre el estado de")
    lineas.append("las variables en 3 segundos o menos con conexión móvil. Esa medición se hace")
    lineas.append("en el navegador, con la pestaña de red abierta, y se guarda como captura fechada.")

    nombre = "rendimiento-%s-limite-%d%s.txt" % (
        datetime.now().strftime("%Y-%m-%d"),
        argumentos.limite,
        argumentos.sufijo,
    )
    (SALIDA / nombre).write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas))
    print("\nInforme guardado en evidencia/%s" % nombre)


if __name__ == "__main__":
    main()
