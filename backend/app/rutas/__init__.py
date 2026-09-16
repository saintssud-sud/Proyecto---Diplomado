"""Rutas de la API, agrupadas bajo el prefijo de versión `/api/v1`."""

from fastapi import APIRouter

from . import (
    alertas,
    exportaciones,
    lecturas,
    modulos,
    perfiles,
    rangos,
    salud,
    usuarios,
)

enrutador_api = APIRouter()

enrutador_api.include_router(salud.enrutador)
enrutador_api.include_router(lecturas.enrutador)
enrutador_api.include_router(modulos.enrutador)
enrutador_api.include_router(perfiles.enrutador)
enrutador_api.include_router(rangos.enrutador)
enrutador_api.include_router(alertas.enrutador)
enrutador_api.include_router(exportaciones.enrutador)
enrutador_api.include_router(usuarios.enrutador)

__all__ = ["enrutador_api"]
