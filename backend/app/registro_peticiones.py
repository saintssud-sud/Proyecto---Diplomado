"""Registro de una línea por petición.

Requisito de operación del servicio: «una línea por petición: método, ruta,
código y duración». Hasta ahora el servicio no tenía ningún middleware de
registro —solo CORS— y los mensajes sueltos que escribían ``main.py`` y el
repositorio de Firestore al arrancar; de modo que no quedaba constancia de qué
peticiones atendió el servicio ni de cuánto tardó en cada una.

Qué se registra
---------------
Una sola línea por petición HTTP, con cuatro datos y nada más::

    peticion metodo=GET ruta=/api/v1/modulos/{modulo_id} codigo=200 duracion_ms=12.4

La ruta es la **ruta declarada**, con los parámetros entre llaves en lugar de los
identificadores reales: se lee mejor y, sobre todo, evita dejar en el registro el
identificador del módulo, de la lectura o de la cuenta que se consultó.

Qué NO se registra
------------------
Ninguna otra cosa. En particular:

* ni la cabecera ``Authorization`` ni la ``X-Device-Key``: son las credenciales
  de la sesión y del módulo de adquisición;
* ni los cuerpos de petición o de respuesta: el registro de lecturas manuales
  lleva observaciones escritas por personas y el de cuentas, datos personales;
* ni la cadena de consulta: en ``/api/v1/lecturas`` lleva el rango de fechas
  consultado y en ``/api/v1/usuarios`` podría llevar datos de una persona.

El registro no puede tumbar una petición
---------------------------------------
Todo el trabajo de registro está encerrado en ``registrar_peticion``, que no
propaga ninguna excepción: si el registro falla, la petición sigue su curso y
responde con normalidad. Es la única forma de que una herramienta de diagnóstico
no se convierta en un punto de fallo del servicio.

Por qué un middleware ASGI y no ``BaseHTTPMiddleware``
------------------------------------------------------
Este middleware no envuelve el cuerpo de la respuesta en una tarea aparte ni
depende de que el ciclo de vida de la petición llegue al final: escribe la línea
en un bloque ``finally``. Así queda registrada también la petición que termina
en una excepción no prevista, que es justamente la que más interesa ver.
"""

import logging
import time
from typing import Any, Awaitable, Callable

# El registro de la aplicación: el mismo que ya usan `main.py` y el repositorio
# de Firestore. Se escribe con el módulo estándar de Python, sin dependencias.
REGISTRADOR = logging.getLogger("sigvach")

# Formato de la línea. Se declara una sola vez para que local y producción
# escriban exactamente lo mismo y se puedan comparar los registros.
FORMATO_MENSAJE = "peticion metodo=%s ruta=%s codigo=%d duracion_ms=%.1f"

# Formato con que el propio módulo presenta las líneas cuando tiene que
# configurar el manejador él mismo (ver `configurar_registro`).
FORMATO_SALIDA = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"

# Código que se registra cuando la petición termina sin respuesta. FastAPI
# responde 500 en ese caso, así que es el valor que corresponde informar.
CODIGO_SIN_RESPUESTA = 500


def configurar_registro(nivel: str = "INFO") -> None:
    """Deja el registro de la aplicación en condiciones de escribir.

    Hace falta porque el módulo estándar de Python **no escribe nada por su
    cuenta**: hasta que alguien fija un nivel y añade un manejador, un mensaje
    de nivel INFO se descarta y el registro queda vacío. Ni Uvicorn ni Render
    configuran el registro de la aplicación —Uvicorn solo configura el suyo—, de
    modo que sin esta llamada las líneas no se verían ni en local ni en el
    servicio publicado, que es justamente donde hay que verlas.

    El manejador se añade **solo si nadie configuró un manejador todavía**, ni en
    este registro ni en el registro raíz: si el entorno donde corre el servicio
    ya recolecta los mensajes (una plataforma, el propio Uvicorn o una prueba),
    no se duplican las líneas. La llamada es idempotente y no puede impedir el
    arranque: cualquier fallo al configurar se ignora en silencio, porque el
    servicio debe levantar aunque el registro no esté disponible.
    """
    try:
        REGISTRADOR.setLevel(_nivel_valido(nivel))
        if REGISTRADOR.handlers or logging.getLogger().handlers:
            return
        manejador = logging.StreamHandler()
        manejador.setFormatter(logging.Formatter(FORMATO_SALIDA, datefmt=FORMATO_FECHA))
        REGISTRADOR.addHandler(manejador)
    except Exception:  # noqa: BLE001 - el registro no puede impedir el arranque
        pass


def _nivel_valido(nivel: str) -> int:
    """Traduce el nivel configurado a su valor numérico, con INFO como reserva."""
    texto = str(nivel or "").strip().upper()
    if texto.isdigit():
        return int(texto)
    valor = logging.getLevelName(texto)
    return valor if isinstance(valor, int) else logging.INFO


def registrar_peticion(alcance: dict[str, Any], codigo: int, duracion_ms: float) -> None:
    """Escribe la línea de una petición ya atendida.

    No propaga ninguna excepción: el registro es un servicio auxiliar y no puede
    convertirse en la causa de que una petición falle. Si algo va mal, la
    petición ya se atendió y su respuesta ya salió; lo único que se pierde es la
    línea.
    """
    try:
        REGISTRADOR.info(
            FORMATO_MENSAJE,
            _sin_saltos(alcance.get("method") or "-"),
            _ruta_declarada(alcance),
            codigo,
            duracion_ms,
        )
    except Exception:  # noqa: BLE001 - el registro nunca puede tumbar una petición
        pass


def _sin_saltos(valor: Any) -> str:
    """Reduce el valor a una sola línea.

    El requisito es una línea por petición: si un dato trajera un salto de línea
    o un tabulador —una ruta manipulada, por ejemplo— la línea se partiría en dos
    y el registro dejaría de poder leerse con un filtro por línea.
    """
    return " ".join(str(valor).split())


def _ruta_declarada(alcance: dict[str, Any]) -> str:
    """Devuelve la ruta declarada, sin los identificadores de la petición.

    Starlette resuelve la ruta durante el despacho y deja los parámetros
    capturados en ``scope["path_params"]``, sobre el mismo diccionario que recibe
    este middleware. Leyéndolos después de atender la petición se puede
    reconstruir la plantilla: cada tramo de la ruta que coincide con el valor de
    un parámetro se sustituye por el nombre de ese parámetro, de modo que
    ``/api/v1/usuarios/AbC123`` se registre como ``/api/v1/usuarios/{uid}``.

    Si no hubo coincidencia con ninguna ruta —por ejemplo, un 404— no hay
    parámetros que sustituir y se registra la ruta tal como llegó: en ese caso no
    hay identificador de recurso que ocultar, y la ruta es el dato que permite
    saber qué se pidió.
    """
    ruta = str(alcance.get("path") or "-")
    parametros = alcance.get("path_params")
    if not parametros:
        return _sin_saltos(ruta)

    nombres_por_valor: dict[str, list[str]] = {}
    for nombre, valor in parametros.items():
        nombres_por_valor.setdefault(str(valor), []).append(str(nombre))

    partes = ruta.split("/")
    for indice, parte in enumerate(partes):
        if not parte:
            continue
        nombres = nombres_por_valor.get(parte)
        if nombres:
            partes[indice] = "{%s}" % nombres.pop(0)
    return _sin_saltos("/".join(partes))


class MiddlewareRegistroPeticiones:
    """Middleware ASGI que escribe una línea por cada petición HTTP.

    Se instala con ``aplicacion.add_middleware(MiddlewareRegistroPeticiones)``. El
    alcance distinto de HTTP —el ciclo de vida del arranque, por ejemplo— se deja
    pasar sin registrar: no es una petición y no tiene método, ruta ni código.
    """

    def __init__(self, aplicacion: Callable[..., Awaitable[None]]) -> None:
        self.aplicacion = aplicacion

    async def __call__(
        self,
        alcance: dict[str, Any],
        recibir: Callable[..., Awaitable[Any]],
        enviar: Callable[..., Awaitable[None]],
    ) -> None:
        if alcance.get("type") != "http":
            await self.aplicacion(alcance, recibir, enviar)
            return

        inicio = time.perf_counter()
        # Valor de partida: si la petición termina sin que se haya anunciado una
        # respuesta, es que falló, y 500 es lo que recibe el cliente.
        codigo = CODIGO_SIN_RESPUESTA

        async def enviar_anotando_el_codigo(mensaje: dict[str, Any]) -> None:
            nonlocal codigo
            if mensaje.get("type") == "http.response.start":
                codigo = int(mensaje.get("status") or codigo)
            await enviar(mensaje)

        try:
            await self.aplicacion(alcance, recibir, enviar_anotando_el_codigo)
        finally:
            # En `finally` para que la línea se escriba también cuando la
            # petición termina en una excepción no prevista.
            registrar_peticion(
                alcance, codigo, (time.perf_counter() - inicio) * 1000.0
            )
