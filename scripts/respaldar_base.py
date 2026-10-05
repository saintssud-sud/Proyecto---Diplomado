# -*- coding: utf-8 -*-
"""Respaldo de los datos del dominio a un archivo JSON fechado.

Para qué sirve
--------------
La cátedra pide «respaldo de la base: copia periódica y una restauración probada
al menos una vez». Este script cubre la primera mitad: hace una **copia de los
datos del dominio** —no de los archivos de la base— y la deja en un archivo JSON
fechado, dentro de la carpeta ``respaldos/`` del proyecto (que el ``.gitignore``
excluye, porque un respaldo no se versiona).

Cómo obtiene los datos
----------------------
Pide los datos a la **API REST publicada**, con las mismas credenciales y los
mismos permisos que usaría una persona desde el panel. No se conecta a Cloud
Firestore ni usa la cuenta de servicio: no las necesita. Esto tiene dos
consecuencias que conviene tener presentes:

* el respaldo queda limitado a lo que la API expone, que es exactamente el
  dominio del sistema: perfiles de cultivo, módulos, rangos de referencia,
  lecturas y alertas;
* el respaldo pasa por la validación y la autorización del servicio, de modo que
  lo que se guarda es lo que el sistema considera datos válidos, y no un estado
  intermedio de la base.

Toda la copia se hace con permisos de **consulta**: este script no crea, modifica
ni borra nada.

Qué exporta
-----------
* ``perfiles``: todos los perfiles de cultivo (con sus rangos de referencia).
* ``rangos``: todos los rangos de referencia, que son los que permiten volver a
  evaluar las lecturas restauradas.
* ``modulos``: todos los módulos o zonas de cultivo, con el perfil al que están
  asociados.
* ``lecturas``: las del módulo de la maqueta (``v6wrYSXxeHyttf3prDd7``,
  «Maqueta NFT - Lechuga»), paginadas para no depender del límite de la API.
* ``alertas``: las del mismo módulo.

Los tres primeros son colecciones cortas y se copian enteras porque son la
referencia del resto; las lecturas y las alertas se acotan al módulo de la
maqueta, que es el que tiene datos en producción. El módulo se puede cambiar con
``--modulo``.

Dos límites de la API que quedan anotados en el propio respaldo
--------------------------------------------------------------
1. La consulta de **alertas por módulo** responde HTTP 500 en el servicio
   publicado, porque falta el índice compuesto ``(modulo_id, timestamp)`` en
   ``firestore.indexes.json``. Mientras no se corrija, este script consulta las
   alertas por estado, que sí está indexado, y suma las dos listas.
2. La API no ofrece paginación para alertas: como mucho devuelve 500 por
   consulta. Las lecturas sí se paginan, de modo que el respaldo de lecturas
   está completo; el de alertas puede quedar corto y el script lo advierte.

Cuando alguno de esos límites se alcanza, el archivo del respaldo lo dice en su
lista ``avisos``: un respaldo que omite datos en silencio no sirve como respaldo.

Las credenciales no están en el repositorio
-------------------------------------------
Se leen de un archivo que vive **fuera** del proyecto:

    C:\\Users\\<usuario>\\credenciales-sigvach\\operador.txt

con dos líneas, ``correo=`` y ``clave=``. La ruta se puede cambiar con la
variable de entorno ``CREDENCIALES_OPERADOR`` (la misma que usa
``scripts/ver_lecturas_publicadas.py``). La carpeta de salida se puede cambiar
con ``--carpeta`` o con ``CARPETA_RESPALDOS``. Ningún valor de ese archivo se
escribe en el repositorio ni se imprime por pantalla.

Uso
---
    python scripts/respaldar_base.py
    python scripts/respaldar_base.py --modulo v6wrYSXxeHyttf3prDd7
    python scripts/respaldar_base.py --carpeta D:\\respaldos-sigvach

Ejecución periódica (la «copia periódica» del requisito)
-------------------------------------------------------
Una vez al día, con el Programador de tareas de Windows::

    schtasks /create /tn "SIGVACH - respaldo diario" /sc daily /st 23:30 ^
      /tr "python \"D:\\SIGVACH-Monograf\\Proyecto SIGVACH\\scripts\\respaldar_base.py\""

y en Linux, con cron::

    30 23 * * * cd /ruta/al/proyecto && python3 scripts/respaldar_base.py >> respaldos/respaldo.log 2>&1

El script no pide datos por teclado a propósito: si no encuentra las
credenciales, falla con un mensaje claro en lugar de quedarse esperando —una
tarea programada no tiene a nadie que responda.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SERVICIO = "https://sigvach-api.onrender.com"
# Clave del cliente web de Firebase: es pública por diseño (viaja en el paquete
# web publicado) y sirve para lo mismo que el formulario de acceso del panel:
# cambiar el correo y la clave de una persona por un token de identidad. No es
# un secreto del proyecto y no da acceso a la base de datos.
CLAVE_WEB_FIREBASE = "AIzaSyDA41lEpw0T6a7bTPq-dVab2lK8aOUHvDg"
MODULO_MAQUETA = "v6wrYSXxeHyttf3prDd7"
BOLIVIA = timezone(timedelta(hours=-4))

ARCHIVO_CREDENCIALES = Path(
    os.environ.get("CREDENCIALES_OPERADOR")
    or Path(os.environ.get("USERPROFILE", str(Path.home())))
    / "credenciales-sigvach"
    / "operador.txt"
)
CARPETA_RESPALDOS = Path(
    os.environ.get("CARPETA_RESPALDOS")
    or Path(__file__).resolve().parent.parent / "respaldos"
)

# Límites de la API (apiv1/rutas/lecturas.py) y de este script.
LIMITE_LECTURAS = 1000  # máximo que admite la API por petición
MAXIMO_PAGINAS = 20  # tope de seguridad: 20 000 lecturas
LIMITE_ALERTAS = 500  # máximo que admite la API por petición

# Reintentos: la capa gratuita del servicio se duerme y tarda hasta un minuto en
# despertar; además la conexión se corta de vez en cuando durante el arranque.
INTENTOS = 4
ESPERAS = (5, 15, 30)  # segundos entre intento e intento
CODIGOS_PASAJEROS = (502, 503, 504)
ESPERA_PETICION = 180  # segundos


class Respuesta:
    """Respuesta del servicio: código HTTP y cuerpo ya interpretado."""

    def __init__(self, codigo: int, texto: str) -> None:
        self.codigo = codigo
        self.texto = texto
        try:
            self.datos = json.loads(texto)
        except (json.JSONDecodeError, ValueError):
            self.datos = None

    @property
    def correcta(self) -> bool:
        return self.codigo == 200

    def fragmento(self, limite: int = 200) -> str:
        """Devuelve un fragmento del cuerpo, para informar de un fallo."""
        return " ".join(self.texto.split())[:limite]


def leer_credenciales(ruta: Path) -> tuple[str, str]:
    """Lee el correo y la clave del archivo local, fuera del repositorio.

    No se admiten credenciales escritas en el repositorio ni pasadas por la línea
    de órdenes: la primera quedaría versionada y la segunda, en el historial del
    intérprete. Si el archivo no está, se explica dónde se esperaba y con qué
    variable de entorno se cambia la ruta.
    """
    if not ruta.exists():
        raise SystemExit(
            "No se encontró el archivo de credenciales: %s\n"
            "Debe tener dos líneas, 'correo=' y 'clave=', de una cuenta del sistema.\n"
            "La ruta se cambia con la variable de entorno CREDENCIALES_OPERADOR." % ruta
        )

    datos: dict[str, str] = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if "=" in linea and not linea.strip().startswith("#"):
            nombre, valor = linea.split("=", 1)
            datos[nombre.strip()] = valor.strip()

    if not datos.get("correo") or not datos.get("clave"):
        raise SystemExit(
            "El archivo %s no tiene las líneas 'correo=' y 'clave='." % ruta
        )
    return datos["correo"], datos["clave"]


class Sesion:
    """Sesión contra el servicio publicado, con reintentos y renovación del token.

    El token que emite Firebase Authentication vence al cabo de una hora; como el
    respaldo puede tardar (la primera llamada despierta el servicio), se renueva
    la sesión cuando el servicio responde 401 o 403 en lugar de darse por vencido.
    """

    def __init__(self, correo: str, clave: str, servicio: str = SERVICIO) -> None:
        self.correo = correo
        self.clave = clave
        self.servicio = servicio.rstrip("/")
        self.token = ""

    def ingresar(self) -> None:
        """Cambia el correo y la clave por un token de identidad."""
        cuerpo = json.dumps(
            {"email": self.correo, "password": self.clave, "returnSecureToken": True}
        ).encode()
        peticion = urllib.request.Request(
            "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
            "?key=%s" % CLAVE_WEB_FIREBASE,
            headers={"Content-Type": "application/json"},
            data=cuerpo,
        )
        try:
            with urllib.request.urlopen(peticion, timeout=ESPERA_PETICION) as respuesta:
                self.token = json.loads(respuesta.read())["idToken"]
        except urllib.error.HTTPError as error:
            detalle = error.read(200).decode("utf-8", "replace")
            raise SystemExit(
                "No se pudo iniciar sesión en el servicio (HTTP %s): %s"
                % (error.code, detalle)
            )
        except Exception as error:  # noqa: BLE001 - se informa y se termina
            raise SystemExit(
                "No se pudo iniciar sesión: %s: %s" % (type(error).__name__, error)
            )

    def pedir(self, ruta: str, metodo: str = "GET", cuerpo: dict | None = None,
              reintentar: bool = True) -> Respuesta:
        """Pide una ruta de la API y devuelve la respuesta, reintentando si falla.

        Se reintenta lo que puede ser pasajero: la conexión cortada o vencida
        —frecuente mientras el servicio despierta— y las respuestas 502, 503 y
        504, que son las que devuelve la plataforma durante un reinicio.

        ``reintentar=False`` se usa en las escrituras: repetir un POST cuyo
        resultado no se llegó a leer puede duplicar el registro. Quien escribe
        debe comprobar después qué quedó guardado, en lugar de reintentar a
        ciegas.
        """
        intentos = INTENTOS if reintentar else 1
        renovaciones = 0
        ultimo_error = ""
        intento = 0
        while intento < intentos:
            if intento:
                espera = ESPERAS[min(intento - 1, len(ESPERAS) - 1)]
                print(
                    "  ... %s. Reintento %d de %d en %d s."
                    % (ultimo_error, intento + 1, intentos, espera)
                )
                time.sleep(espera)
            intento += 1

            if not self.token:
                self.ingresar()

            cabeceras = {
                "Accept": "application/json",
                "Authorization": "Bearer %s" % self.token,
            }
            datos = None
            if cuerpo is not None:
                datos = json.dumps(cuerpo).encode("utf-8")
                cabeceras["Content-Type"] = "application/json"

            peticion = urllib.request.Request(
                "%s%s" % (self.servicio, ruta),
                headers=cabeceras,
                data=datos,
                method=metodo,
            )
            try:
                with urllib.request.urlopen(
                    peticion, timeout=ESPERA_PETICION
                ) as respuesta:
                    return Respuesta(respuesta.status, respuesta.read().decode("utf-8", "replace"))
            except urllib.error.HTTPError as error:
                texto = error.read().decode("utf-8", "replace")
                if error.code in (401, 403) and renovaciones < 1:
                    # El token venció: se renueva y se repite. La renovación no
                    # consume intento, porque no es un fallo del servicio sino el
                    # vencimiento normal del token (una hora).
                    self.token = ""
                    renovaciones += 1
                    intento -= 1
                    ultimo_error = "la sesión venció (HTTP %d)" % error.code
                    continue
                if reintentar and error.code in CODIGOS_PASAJEROS:
                    ultimo_error = "el servicio respondió HTTP %d" % error.code
                    continue
                return Respuesta(error.code, texto)
            except Exception as error:  # noqa: BLE001 - se reintenta
                ultimo_error = "%s: %s" % (type(error).__name__, error)
                if not reintentar:
                    # La escritura pudo haber llegado al servicio: no se repite,
                    # se informa (código 0) para que quien llama compruebe qué
                    # quedó guardado.
                    return Respuesta(0, ultimo_error)

        raise SystemExit(
            "No se pudo consultar %s después de %d intentos (%s)."
            % (ruta, intentos, ultimo_error)
        )


def exigir(respuesta: Respuesta, ruta: str) -> object:
    """Devuelve el cuerpo de una respuesta correcta; si no lo es, termina."""
    if not respuesta.correcta:
        raise SystemExit(
            "El servicio respondió HTTP %s en %s: %s"
            % (respuesta.codigo, ruta, respuesta.fragmento())
        )
    return respuesta.datos


def listar(sesion: Sesion, ruta: str, que: str) -> list:
    """Pide una colección y comprueba que la respuesta sea una lista."""
    datos = exigir(sesion.pedir(ruta), ruta)
    if not isinstance(datos, list):
        raise SystemExit("La respuesta de %s no es una lista (%s)." % (ruta, que))
    return datos


def momento(valor: object) -> datetime | None:
    """Interpreta una marca de tiempo ISO de la API."""
    if not valor:
        return None
    try:
        return datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
    except ValueError:
        return None


def lecturas_del_modulo(sesion: Sesion, modulo_id: str) -> tuple[list, list]:
    """Exporta las lecturas del módulo, paginando si hay más que el límite.

    La API devuelve las lecturas de la más nueva a la más vieja y admite filtrar
    por fecha de corte (``hasta``). Cuando una página viene llena se pide la
    siguiente con ``hasta`` igual a la marca de tiempo más vieja ya recibida: el
    corte es inclusivo, así que la propia marca de tiempo se repite y los
    registros se descartan por identificador. Es preferible repetir uno que
    perderlo.
    """
    lecturas: dict[str, dict] = {}
    avisos: list[str] = []
    hasta: str | None = None

    for pagina in range(1, MAXIMO_PAGINAS + 1):
        ruta = "/api/v1/lecturas?modulo_id=%s&limite=%d" % (modulo_id, LIMITE_LECTURAS)
        if hasta:
            ruta += "&hasta=%s" % urllib.parse.quote(hasta)
        recibidas = listar(sesion, ruta, "lecturas")
        nuevas = 0
        for lectura in recibidas:
            identificador = str(lectura.get("id") or "")
            if identificador and identificador not in lecturas:
                nuevas += 1
            lecturas[identificador] = lectura

        print(
            "  lecturas: página %d, %d recibidas, %d nuevas (total %d)"
            % (pagina, len(recibidas), nuevas, len(lecturas))
        )

        if len(recibidas) < LIMITE_LECTURAS:
            break
        if not nuevas:
            avisos.append(
                "La página %d no aportó lecturas nuevas; puede haber más registros "
                "con la misma marca de tiempo." % pagina
            )
            break

        marcas = [momento(lectura.get("timestamp")) for lectura in recibidas]
        marcas = [marca for marca in marcas if marca is not None]
        if not marcas:
            avisos.append("No se pudo paginar: las lecturas no traen marca de tiempo.")
            break
        hasta = min(marcas).isoformat()
    else:
        avisos.append(
            "Se alcanzó el tope de %d páginas; el respaldo de lecturas puede estar "
            "incompleto." % MAXIMO_PAGINAS
        )

    return list(lecturas.values()), avisos


def alertas_del_modulo(sesion: Sesion, modulo_id: str) -> tuple[list, list]:
    """Exporta las alertas del módulo.

    La consulta natural es ``/alertas?modulo_id=...``, pero en el servicio
    publicado esa consulta responde **HTTP 500**: `firestore.indexes.json`
    declara los índices compuestos de la colección ``alertas`` para
    ``(estado, modulo_id, timestamp)`` y ``(estado, timestamp)``, y no para
    ``(modulo_id, timestamp)``, que es el que esa consulta necesita. Firestore
    rechaza entonces la consulta y el servicio responde 500.

    Mientras eso no se corrija, se consulta por estado —activa y atendida—, que
    es una forma que el índice declarado sí admite, y se juntan las dos listas.
    El hecho queda anotado en los avisos del respaldo, porque un respaldo que
    omite algo sin decirlo no sirve como respaldo.
    """
    ruta_directa = "/api/v1/alertas?modulo_id=%s&limite=%d" % (modulo_id, LIMITE_ALERTAS)
    respuesta = sesion.pedir(ruta_directa)
    if respuesta.correcta and isinstance(respuesta.datos, list):
        alertas = respuesta.datos
        avisos = []
        if len(alertas) >= LIMITE_ALERTAS:
            avisos.append(
                "Las alertas del módulo llegaron al límite de %d de la API y esta no "
                "ofrece paginación para alertas: puede haber más." % LIMITE_ALERTAS
            )
        return alertas, avisos

    avisos = [
        "La consulta de alertas por módulo (%s) respondió HTTP %s: %s. Se usó la "
        "consulta por estado, que sí está indexada."
        % (ruta_directa, respuesta.codigo, respuesta.fragmento(120))
    ]
    print("  La consulta por módulo falló (HTTP %s). Se consulta por estado." % respuesta.codigo)

    por_identificador: dict[str, dict] = {}
    for estado in ("activa", "atendida"):
        ruta = "/api/v1/alertas?estado=%s&modulo_id=%s&limite=%d" % (
            estado,
            modulo_id,
            LIMITE_ALERTAS,
        )
        recibidas = listar(sesion, ruta, "alertas")
        print("  alertas %-9s: %d" % (estado, len(recibidas)))
        if len(recibidas) >= LIMITE_ALERTAS:
            avisos.append(
                "Las alertas en estado '%s' llegaron al límite de %d de la API: puede "
                "haber más." % (estado, LIMITE_ALERTAS)
            )
        for alerta in recibidas:
            por_identificador[str(alerta.get("id") or "")] = alerta

    return list(por_identificador.values()), avisos


def exportar(sesion: Sesion, modulo_id: str) -> tuple[dict, list]:
    """Arma el contenido del respaldo consultando la API publicada."""
    avisos: list[str] = []

    print("Consultando perfiles, módulos y rangos...")
    perfiles = listar(sesion, "/api/v1/perfiles", "perfiles de cultivo")
    modulos = listar(sesion, "/api/v1/modulos", "módulos de cultivo")
    rangos = listar(sesion, "/api/v1/rangos", "rangos de referencia")

    modulo = next(
        (m for m in modulos if str(m.get("id")) == modulo_id),
        None,
    )
    if modulo is None:
        avisos.append(
            "El módulo %s no aparece en la lista de módulos del servicio." % modulo_id
        )

    print("Consultando las lecturas del módulo %s..." % modulo_id)
    lecturas, avisos_lecturas = lecturas_del_modulo(sesion, modulo_id)
    avisos.extend(avisos_lecturas)

    print("Consultando las alertas del módulo %s..." % modulo_id)
    alertas, avisos_alertas = alertas_del_modulo(sesion, modulo_id)
    avisos.extend(avisos_alertas)

    # Las lecturas se guardan de la más nueva a la más vieja, como las devuelve
    # el servicio, y las de las páginas anteriores se ordenan por la misma marca.
    lecturas.sort(key=lambda item: str(item.get("timestamp") or ""), reverse=True)

    generado = datetime.now(timezone.utc)
    respaldo = {
        "formato": "sigvach-respaldo-1",
        "generado_en": generado.isoformat(),
        "generado_en_hora_local": generado.astimezone(BOLIVIA).isoformat(),
        "servicio": sesion.servicio,
        "origen": "API REST publicada (sin acceso directo a la base de datos)",
        "modulo_maqueta": modulo_id,
        "nombre_del_modulo_maqueta": (modulo or {}).get("nombre", ""),
        "perfil_del_modulo_maqueta": (modulo or {}).get("perfil_id", ""),
        "conteo": {
            "perfiles": len(perfiles),
            "modulos": len(modulos),
            "rangos": len(rangos),
            "lecturas": len(lecturas),
            "alertas": len(alertas),
        },
        "avisos": avisos,
        "perfiles": perfiles,
        "modulos": modulos,
        "rangos": rangos,
        "lecturas": lecturas,
        "alertas": alertas,
    }
    return respaldo, avisos


def nombre_del_archivo(momento_local: datetime) -> str:
    """Nombre del respaldo: la fecha y la hora, para no pisar el anterior."""
    return "respaldo-sigvach-%s.json" % momento_local.strftime("%Y-%m-%d_%H%M%S")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:  # pragma: no cover - solo en consolas antiguas
        pass

    analizador = argparse.ArgumentParser(
        description="Respalda los datos del dominio a un archivo JSON fechado"
    )
    analizador.add_argument(
        "--modulo",
        default=MODULO_MAQUETA,
        help="identificador del módulo cuyas lecturas y alertas se respaldan",
    )
    analizador.add_argument(
        "--carpeta",
        default=str(CARPETA_RESPALDOS),
        help="carpeta donde se guarda el respaldo (por omisión, respaldos/)",
    )
    analizador.add_argument(
        "--credenciales",
        default=str(ARCHIVO_CREDENCIALES),
        help="archivo local con las credenciales, fuera del repositorio",
    )
    analizador.add_argument(
        "--servicio", default=SERVICIO, help="dirección del servicio a respaldar"
    )
    argumentos = analizador.parse_args()

    correo, clave = leer_credenciales(Path(argumentos.credenciales))

    print("=== RESPALDO DE SIGVACH ===")
    print("  servicio : %s" % argumentos.servicio)
    print("  módulo   : %s" % argumentos.modulo)
    print("  cuenta   : %s" % correo)
    print("")

    sesion = Sesion(correo, clave, argumentos.servicio)
    print("Iniciando sesión en el servicio...")
    sesion.ingresar()
    print("  sesión iniciada.")

    respaldo, avisos = exportar(sesion, argumentos.modulo)

    # La carpeta se crea aquí y no antes: si el respaldo falla, no queda una
    # carpeta vacía que parezca un respaldo hecho.
    carpeta = Path(argumentos.carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    ahora_local = datetime.now(BOLIVIA)
    archivo = carpeta / nombre_del_archivo(ahora_local)
    archivo.write_text(
        json.dumps(respaldo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    conteo = respaldo["conteo"]
    print("")
    print("=== RESPALDO TERMINADO ===")
    print("  archivo  : %s" % archivo.resolve())
    print("  tamaño   : %d bytes" % archivo.stat().st_size)
    print("  fecha    : %s (hora local, Bolivia)" % ahora_local.strftime("%Y-%m-%d %H:%M:%S"))
    print("  registros exportados:")
    for nombre, etiqueta in (
        ("perfiles", "perfiles de cultivo"),
        ("modulos", "módulos de cultivo"),
        ("rangos", "rangos de referencia"),
        ("lecturas", "lecturas del módulo"),
        ("alertas", "alertas del módulo"),
    ):
        print("    %-22s %5d" % (etiqueta, conteo[nombre]))
    print("    %-22s %5d" % ("TOTAL", sum(conteo.values())))

    if avisos:
        print("")
        print("  AVISOS:")
        for aviso in avisos:
            print("    - %s" % aviso)

    print("")
    print("  El respaldo no se versiona: la carpeta 'respaldos/' está en .gitignore.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
