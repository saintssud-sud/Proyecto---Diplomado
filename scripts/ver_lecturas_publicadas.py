# -*- coding: utf-8 -*-
"""Muestra en la PC las lecturas que el modulo publica en el servicio.

Para que sirve
--------------
El modulo publica sus seis variables cada cinco minutos desde cualquier lugar
donde haya WiFi. Este visor pide esas lecturas al **servicio publicado** y las
muestra en una tabla que se refresca sola, marcando lo que esta fuera del rango
configurado en el sistema.

Se consulta el servicio y no el puerto serie a proposito: asi se ve lo mismo que
ve cualquier usuario del panel, funciona aunque el modulo este lejos, y no se
pelea con el cable USB (solo un programa puede tener COM6 a la vez, y el bufer
del controlador se traba cuando el modulo imprime su traza de WiFi).

Uso
---
    python ver_lecturas_publicadas.py                 (refresca cada 15 segundos)
    python ver_lecturas_publicadas.py --cada 5
    python ver_lecturas_publicadas.py --una-vez       (una sola tabla, para evidencia)

Las credenciales se leen de un archivo fuera del repositorio
(%USERPROFILE%\\credenciales-sigvach\\operador.txt). Si no existe, se piden una
vez y se guardan ahi: nunca quedan dentro del proyecto.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SERVICIO = "https://sigvach-api.onrender.com"
CLAVE_WEB_FIREBASE = "AIzaSyDA41lEpw0T6a7bTPq-dVab2lK8aOUHvDg"
MODULO_POR_DEFECTO = "v6wrYSXxeHyttf3prDd7"
BOLIVIA = timezone(timedelta(hours=-4))
ARCHIVO_CREDENCIALES = Path(
    os.environ.get("CREDENCIALES_OPERADOR")
    or Path(os.environ.get("USERPROFILE", str(Path.home()))) / "credenciales-sigvach" / "operador.txt"
)
SIN_RANGO = "sin rango configurado"
MINUTOS_PARA_CONSIDERAR_EN_LINEA = 12


class Sesion:
    """Mantiene el token de identidad y lo renueva cuando vence."""

    def __init__(self, correo: str, clave: str):
        self.correo = correo
        self.clave = clave
        self.token = ""

    def ingresar(self) -> None:
        cuerpo = json.dumps(
            {"email": self.correo, "password": self.clave, "returnSecureToken": True}
        ).encode()
        peticion = urllib.request.Request(
            "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=%s"
            % CLAVE_WEB_FIREBASE,
            headers={"Content-Type": "application/json"},
            data=cuerpo,
        )
        try:
            with urllib.request.urlopen(peticion, timeout=60) as respuesta:
                self.token = json.loads(respuesta.read())["idToken"]
        except urllib.error.HTTPError as error:
            detalle = error.read(200).decode("utf-8", "replace")
            raise SystemExit("No se pudo iniciar sesion (%s): %s" % (error.code, detalle))
        except Exception as error:  # noqa: BLE001 - se informa al usuario
            raise SystemExit("No se pudo iniciar sesion: %s: %s" % (type(error).__name__, error))

    def pedir(self, ruta: str, publico: bool = False):
        """Devuelve (codigo, cuerpo). Si el token vencio, se renueva una vez."""
        for intento in (1, 2):
            cabeceras = {"Accept": "application/json"}
            if not publico:
                cabeceras["Authorization"] = "Bearer %s" % self.token
            peticion = urllib.request.Request("%s%s" % (SERVICIO, ruta), headers=cabeceras)
            try:
                with urllib.request.urlopen(peticion, timeout=90) as respuesta:
                    return respuesta.status, respuesta.read()
            except urllib.error.HTTPError as error:
                cuerpo = error.read()
                if error.code in (401, 403) and intento == 1 and not publico:
                    self.ingresar()
                    continue
                return error.code, cuerpo
        return 0, b""


def leer_credenciales() -> tuple[str, str]:
    if ARCHIVO_CREDENCIALES.exists():
        datos = {}
        for linea in ARCHIVO_CREDENCIALES.read_text(encoding="utf-8").splitlines():
            if "=" in linea and not linea.strip().startswith("#"):
                nombre, valor = linea.split("=", 1)
                datos[nombre.strip()] = valor.strip()
        if datos.get("correo") and datos.get("clave"):
            return datos["correo"], datos["clave"]

    print("Primera vez: se necesitan las credenciales de un usuario del sistema.")
    print("Quedaran guardadas en %s (fuera del proyecto)." % ARCHIVO_CREDENCIALES)
    print("")
    correo = input("Correo   : ").strip()
    clave = getpass.getpass("Contrasena: ").strip()
    if not correo or not clave:
        raise SystemExit("Sin credenciales no se puede consultar el servicio.")
    ARCHIVO_CREDENCIALES.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVO_CREDENCIALES.write_text(
        "# Credenciales del visor de lecturas. No se versionan.\ncorreo=%s\nclave=%s\n" % (correo, clave),
        encoding="utf-8",
    )
    print("Guardadas en %s" % ARCHIVO_CREDENCIALES)
    return correo, clave


def rangos(sesion: Sesion) -> dict[str, tuple[float, float, str]]:
    codigo, cuerpo = sesion.pedir("/api/v1/rangos")
    if codigo != 200:
        return {}
    try:
        lista = json.loads(cuerpo)
    except json.JSONDecodeError:
        return {}
    return {
        item["variable"]: (float(item["minimo"]), float(item["maximo"]), item.get("unidad", ""))
        for item in lista
        if "variable" in item and "minimo" in item and "maximo" in item
    }


def momento(valor) -> datetime | None:
    if not valor:
        return None
    try:
        return datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
    except ValueError:
        return None


def hace(marca: datetime | None) -> str:
    if marca is None:
        return "sin fecha"
    segundos = (datetime.now(timezone.utc) - marca).total_seconds()
    if segundos < 90:
        return "hace %d s" % max(int(segundos), 0)
    minutos = segundos / 60
    if minutos < 90:
        return "hace %d min" % int(minutos)
    return "hace %.1f h" % (minutos / 60)


def tabla(sesion: Sesion, modulo: str, limite: int) -> list[str]:
    codigo_salud, cuerpo_salud = sesion.pedir("/api/v1/salud", publico=True)
    try:
        salud = json.loads(cuerpo_salud) if codigo_salud == 200 else {}
    except json.JSONDecodeError:
        salud = {}

    codigo, cuerpo = sesion.pedir("/api/v1/lecturas?modulo_id=%s&limite=%d" % (modulo, limite))
    lineas: list[str] = []
    lineas.append("SIGVACH - lecturas publicadas por el modulo")
    lineas.append("Servicio : %s" % SERVICIO)
    lineas.append("Actualizado: %s (hora local)" % datetime.now(BOLIVIA).strftime("%Y-%m-%d %H:%M:%S"))
    if codigo_salud == 200:
        lineas.append("Estado del servicio: %s | base de datos: %s" % (
            salud.get("estado", "?"), salud.get("base_de_datos", "?")
        ))
    else:
        lineas.append("Estado del servicio: no respondio (HTTP %s)" % codigo_salud)
    lineas.append("")

    if codigo != 200:
        lineas.append("No se pudieron leer las lecturas (HTTP %s)." % codigo)
        lineas.append(cuerpo[:200].decode("utf-8", "replace"))
        return lineas

    lecturas = json.loads(cuerpo)
    if not lecturas:
        lineas.append("El servicio no tiene lecturas de este modulo todavia.")
        return lineas

    ultimas: dict[str, dict] = {}
    for lectura in lecturas:  # vienen de la mas nueva a la mas vieja
        ultimas.setdefault(lectura.get("variable", "?"), lectura)

    mas_nueva = max((momento(item.get("timestamp")) for item in lecturas if momento(item.get("timestamp"))), default=None)
    edad = (datetime.now(timezone.utc) - mas_nueva).total_seconds() / 60 if mas_nueva else None
    en_linea = edad is not None and edad <= MINUTOS_PARA_CONSIDERAR_EN_LINEA
    lineas.append("Modulo %s" % modulo)
    lineas.append("Ultima publicacion: %s%s" % (
        hace(mas_nueva),
        "   -> EN LINEA" if en_linea else "   -> SIN PUBLICAR (revise WiFi del modulo)",
    ))
    lineas.append("")

    definidos = rangos(sesion)
    lineas.append("%-16s %9s %-7s %-18s %-7s %s" % (
        "VARIABLE", "VALOR", "UNIDAD", "RANGO CONFIGURADO", "ESTADO", "PUBLICADA"
    ))
    lineas.append("-" * 82)
    dentro = 0
    for variable in sorted(ultimas):
        lectura = ultimas[variable]
        try:
            valor = float(lectura.get("valor"))
        except (TypeError, ValueError):
            valor = None
        rango = definidos.get(variable)
        if rango:
            minimo, maximo, _ = rango
            rango_texto = "%.2f - %.2f" % (minimo, maximo)
            if valor is None:
                estado = "sin dato"
            elif minimo <= valor <= maximo:
                estado = "DENTRO"
                dentro += 1
            else:
                estado = "FUERA"
        else:
            rango_texto = SIN_RANGO
            estado = "--"
        lineas.append("%-16s %9s %-7s %-18s %-7s %s" % (
            variable,
            "sin dato" if valor is None else "%.2f" % valor,
            lectura.get("unidad", ""),
            rango_texto,
            estado,
            hace(momento(lectura.get("timestamp"))),
        ))
    lineas.append("-" * 82)
    lineas.append("%d variables | %d dentro del rango configurado" % (len(ultimas), dentro))
    lineas.append("")
    lineas.append("Ctrl+C para salir.")
    return lineas


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:  # pragma: no cover - solo en consolas antiguas
        pass

    analizador = argparse.ArgumentParser(description="Visor de las lecturas publicadas por el modulo")
    analizador.add_argument("--modulo", default=MODULO_POR_DEFECTO, help="identificador del modulo")
    analizador.add_argument("--cada", type=int, default=15, help="segundos entre refrescos")
    analizador.add_argument("--limite", type=int, default=60, help="cuantas lecturas se piden al servicio")
    analizador.add_argument("--una-vez", action="store_true", help="muestra una tabla y termina")
    argumentos = analizador.parse_args()

    correo, clave = leer_credenciales()
    sesion = Sesion(correo, clave)
    sesion.ingresar()

    try:
        while True:
            lineas = tabla(sesion, argumentos.modulo, argumentos.limite)
            if not argumentos.una_vez:
                os.system("cls" if os.name == "nt" else "clear")
            print("\n".join(lineas))
            if argumentos.una_vez:
                return 0
            time.sleep(max(argumentos.cada, 3))
    except KeyboardInterrupt:
        print("")
        print("Visor detenido.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
