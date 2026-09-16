"""Endpoints de las alertas generadas por valores fuera de rango."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, status

from ..dependencias import obtener_repositorio
from ..errores import CODIGO_NO_ENCONTRADO, ErrorApi
from ..esquemas import AlertaActualizacion, AlertaSalida
from ..repositorios.base import RepositorioDatos
from ..seguridad import (
    UsuarioAutenticado,
    requiere_administracion,
    requiere_consulta,
    requiere_operacion,
)

enrutador = APIRouter(prefix="/alertas", tags=["Alertas"])


def _alerta_o_error(repositorio: RepositorioDatos, alerta_id: str) -> dict:
    alerta = repositorio.obtener_alerta(alerta_id)
    if alerta is None:
        raise ErrorApi(
            404,
            CODIGO_NO_ENCONTRADO,
            f"No existe una alerta con el identificador '{alerta_id}'.",
        )
    return alerta


@enrutador.get("", response_model=list[AlertaSalida], summary="Consultar las alertas")
def listar_alertas(
    estado: str | None = Query(default=None, pattern="^(activa|atendida)$"),
    modulo_id: str | None = Query(default=None, max_length=64),
    limite: int = Query(default=100, ge=1, le=500),
    _: UsuarioAutenticado = Depends(requiere_consulta),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> list[dict]:
    """Devuelve las alertas activas, el historial o las de un módulo concreto."""
    return repositorio.listar_alertas(estado=estado, modulo_id=modulo_id, limite=limite)


@enrutador.get("/{alerta_id}", response_model=AlertaSalida, summary="Consultar una alerta")
def obtener_alerta(
    alerta_id: str,
    _: UsuarioAutenticado = Depends(requiere_consulta),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Devuelve una alerta concreta, con la referencia a la lectura que la originó."""
    return _alerta_o_error(repositorio, alerta_id)


@enrutador.patch(
    "/{alerta_id}",
    response_model=AlertaSalida,
    summary="Marcar una alerta como atendida o reactivarla",
)
def actualizar_alerta(
    alerta_id: str,
    entrada: AlertaActualizacion,
    _: UsuarioAutenticado = Depends(requiere_operacion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Cambia el estado de la alerta y deja constancia de cuándo se atendió."""
    _alerta_o_error(repositorio, alerta_id)
    cambios: dict = {"estado": entrada.estado}
    if entrada.observacion is not None:
        cambios["observacion"] = entrada.observacion
    cambios["atendida_en"] = (
        datetime.now(timezone.utc) if entrada.estado == "atendida" else None
    )
    actualizada = repositorio.actualizar_alerta(alerta_id, cambios)
    return actualizada or _alerta_o_error(repositorio, alerta_id)


@enrutador.delete(
    "/{alerta_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una alerta",
)
def eliminar_alerta(
    alerta_id: str,
    _: UsuarioAutenticado = Depends(requiere_administracion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> None:
    """Elimina una alerta del historial; requiere rol de administración."""
    _alerta_o_error(repositorio, alerta_id)
    repositorio.eliminar_alerta(alerta_id)
