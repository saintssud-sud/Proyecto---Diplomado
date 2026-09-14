"""Reglas de negocio del sistema, expresadas como funciones puras.

Este módulo concentra lo que la aplicación Flutter no debe decidir: la
evaluación de una lectura contra su rango de referencia, la decisión de
generar una alerta y el resumen de una serie de lecturas. Al ser funciones sin
efectos secundarios, se prueban de forma directa (ver `pruebas/test_evaluacion.py`).
"""

from datetime import datetime
from typing import Any, Iterable, Sequence

ESTADO_BAJO = "bajo"
ESTADO_DENTRO = "dentro"
ESTADO_ALTO = "alto"
ESTADO_SIN_RANGO = "sin_rango"


def evaluar_lectura(valor: float, minimo: float | None, maximo: float | None) -> str:
    """Devuelve el estado de una lectura respecto de su rango de referencia.

    Si no hay rango configurado para la variable, el estado es `sin_rango`:
    la ausencia de referencia no es un valor fuera de rango.
    """
    if minimo is None or maximo is None:
        return ESTADO_SIN_RANGO
    if valor < minimo:
        return ESTADO_BAJO
    if valor > maximo:
        return ESTADO_ALTO
    return ESTADO_DENTRO


def requiere_alerta(estado: str) -> bool:
    """Una alerta se genera únicamente cuando el valor sale del rango."""
    return estado in (ESTADO_BAJO, ESTADO_ALTO)


def construir_alerta(
    lectura: dict[str, Any],
    rango: dict[str, Any],
    estado: str,
) -> dict[str, Any]:
    """Construye el documento de alerta asociado a una lectura fuera de rango.

    Cada alerta conserva la referencia a la lectura que la originó, de modo que
    la trazabilidad exigida por RNF-08 se sostiene en los datos y no en el orden
    de las pantallas.
    """
    return {
        "lectura_id": lectura["id"],
        "modulo_id": lectura["modulo_id"],
        "variable": lectura["variable"],
        "valor": lectura["valor"],
        "unidad": lectura.get("unidad", ""),
        "rango_minimo": rango["minimo"],
        "rango_maximo": rango["maximo"],
        "estado": "activa",
        "desviacion": estado,
        "timestamp": lectura["timestamp"],
        "observacion": None,
    }


def resumen_serie(valores: Sequence[float]) -> dict[str, Any] | None:
    """Promedio, máximo y mínimo de una serie. Devuelve None si está vacía."""
    if not valores:
        return None
    return {
        "cantidad": len(valores),
        "promedio": round(sum(valores) / len(valores), 3),
        "maximo": max(valores),
        "minimo": min(valores),
    }


def generar_csv(lecturas: Iterable[dict[str, Any]]) -> str:
    """Exporta las lecturas consultadas en CSV, con encabezados estables."""
    encabezados = ["id", "modulo_id", "variable", "valor", "unidad", "origen", "timestamp"]
    lineas = [",".join(encabezados)]
    for lectura in lecturas:
        marca = lectura.get("timestamp")
        if isinstance(marca, datetime):
            marca = marca.isoformat()
        fila = [
            str(lectura.get("id", "")),
            str(lectura.get("modulo_id", "")),
            str(lectura.get("variable", "")),
            str(lectura.get("valor", "")),
            str(lectura.get("unidad", "")),
            str(lectura.get("origen", "")),
            str(marca or ""),
        ]
        lineas.append(",".join(_escapar_csv(campo) for campo in fila))
    return "\r\n".join(lineas) + "\r\n"


def _escapar_csv(campo: str) -> str:
    """Escapa un campo cuando contiene coma, comilla o salto de línea."""
    if any(caracter in campo for caracter in (",", '"', "\n", "\r")):
        return '"' + campo.replace('"', '""') + '"'
    return campo
