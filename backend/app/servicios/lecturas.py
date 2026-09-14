"""Reglas de negocio del dominio de lecturas.

El registro de una lectura es el punto donde el backend ejerce de backend:
comprueba que el módulo exista y esté activo, resuelve el rango vigente de la
variable según el perfil del módulo, evalúa el valor, almacena la lectura y
genera la alerta cuando corresponde. Ninguna de esas decisiones ocurre en la
aplicación Flutter ni en el dispositivo.
"""

from datetime import datetime, timezone
from typing import Any

from ..errores import CODIGO_CONFLICTO, CODIGO_NO_ENCONTRADO, ErrorApi
from ..esquemas import CATALOGO_VARIABLES, LecturaEntrada, LecturaManualEntrada
from ..repositorios.base import RepositorioDatos
from .evaluacion import construir_alerta, evaluar_lectura, requiere_alerta


def _modulo_verificado(repositorio: RepositorioDatos, modulo_id: str) -> dict[str, Any]:
    """Comprueba que el módulo exista y admita lecturas."""
    modulo = repositorio.obtener_modulo(modulo_id)
    if modulo is None:
        raise ErrorApi(
            404,
            CODIGO_NO_ENCONTRADO,
            f"El módulo de cultivo '{modulo_id}' no existe.",
        )
    if modulo.get("activo", True) is False:
        raise ErrorApi(
            409,
            CODIGO_CONFLICTO,
            "El módulo de cultivo está inactivo y no admite nuevas lecturas.",
        )
    return modulo


def registrar(
    repositorio: RepositorioDatos,
    entrada: LecturaEntrada | LecturaManualEntrada,
    origen: str,
) -> dict[str, Any]:
    """Registra una lectura y, si sale del rango vigente, genera su alerta.

    Devuelve el documento de la lectura almacenada, con el estado que se le
    asignó al evaluarla contra el rango del perfil del módulo.
    """
    modulo = _modulo_verificado(repositorio, entrada.modulo_id)
    definicion = CATALOGO_VARIABLES[entrada.variable]

    rango: dict[str, Any] | None = None
    perfil_id = modulo.get("perfil_id")
    if perfil_id:
        rango = repositorio.buscar_rango(str(perfil_id), entrada.variable)

    estado = evaluar_lectura(
        entrada.valor,
        rango.get("minimo") if rango else None,
        rango.get("maximo") if rango else None,
    )

    documento: dict[str, Any] = {
        "modulo_id": entrada.modulo_id,
        "variable": entrada.variable,
        "valor": entrada.valor,
        # La unidad no se toma del cliente: se hereda del catálogo.
        "unidad": definicion.unidad,
        "origen": origen,
        "observacion": entrada.observacion,
        "timestamp": entrada.timestamp or datetime.now(timezone.utc),
        "estado_rango": estado,
    }
    lectura = repositorio.crear_lectura(documento)

    if rango and requiere_alerta(estado):
        repositorio.crear_alerta(construir_alerta(lectura, rango, estado))

    return lectura


def obtener_o_error(repositorio: RepositorioDatos, lectura_id: str) -> dict[str, Any]:
    """Devuelve una lectura o lanza el error 404 correspondiente."""
    lectura = repositorio.obtener_lectura(lectura_id)
    if lectura is None:
        raise ErrorApi(
            404,
            CODIGO_NO_ENCONTRADO,
            f"No existe una lectura con el identificador '{lectura_id}'.",
        )
    return lectura
