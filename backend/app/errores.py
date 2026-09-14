"""Formato único de error de la API.

Conforme al contrato documentado en el apartado 2.4.4 de la monografía, toda
respuesta de error tiene la misma forma::

    {"codigo": "...", "mensaje": "...", "detalle": {...}}

y se acompaña del código HTTP correspondiente: 400, 401, 403, 404, 409 o 422.
"""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as ErrorHttpStarlette

CODIGO_DATOS_INVALIDOS = "datos_invalidos"
CODIGO_NO_AUTENTICADO = "no_autenticado"
CODIGO_SIN_PERMISO = "sin_permiso"
CODIGO_NO_ENCONTRADO = "no_encontrado"
CODIGO_CONFLICTO = "conflicto"
CODIGO_VALIDACION = "validacion_rechazada"
CODIGO_ERROR_INTERNO = "error_interno"


class ErrorApi(Exception):
    """Error de la API con el formato uniforme del contrato."""

    def __init__(
        self,
        estado: int,
        codigo: str,
        mensaje: str,
        detalle: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(mensaje)
        self.estado = estado
        self.codigo = codigo
        self.mensaje = mensaje
        self.detalle = detalle or {}


def cuerpo_error(codigo: str, mensaje: str, detalle: dict[str, Any] | None = None) -> dict[str, Any]:
    """Construye el cuerpo de una respuesta de error."""
    return {"codigo": codigo, "mensaje": mensaje, "detalle": detalle or {}}


def _detalle_de_validacion(error: RequestValidationError) -> dict[str, Any]:
    """Convierte los errores de validación en un detalle legible por campo."""
    campos: dict[str, str] = {}
    for fallo in error.errors():
        # La ubicación llega como ("body", "valor"); se conserva el último tramo.
        ruta = [str(parte) for parte in fallo.get("loc", ()) if parte not in ("body", "query", "path")]
        campo = ".".join(ruta) or "cuerpo"
        campos[campo] = fallo.get("msg", "valor no admitido")
    return {"campos": campos}


def registrar_manejadores_de_error(app: FastAPI) -> None:
    """Registra en la aplicación los manejadores que dan formato a los errores."""

    @app.exception_handler(ErrorApi)
    async def _manejar_error_api(_: Request, excepcion: ErrorApi) -> JSONResponse:
        return JSONResponse(
            status_code=excepcion.estado,
            content=cuerpo_error(excepcion.codigo, excepcion.mensaje, excepcion.detalle),
        )

    @app.exception_handler(RequestValidationError)
    async def _manejar_validacion(_: Request, excepcion: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=cuerpo_error(
                CODIGO_VALIDACION,
                "La petición no cumple el contrato: revise los campos señalados.",
                _detalle_de_validacion(excepcion),
            ),
        )

    @app.exception_handler(ErrorHttpStarlette)
    async def _manejar_error_http(_: Request, excepcion: ErrorHttpStarlette) -> JSONResponse:
        codigos = {
            400: CODIGO_DATOS_INVALIDOS,
            401: CODIGO_NO_AUTENTICADO,
            403: CODIGO_SIN_PERMISO,
            404: CODIGO_NO_ENCONTRADO,
            409: CODIGO_CONFLICTO,
            422: CODIGO_VALIDACION,
        }
        return JSONResponse(
            status_code=excepcion.status_code,
            content=cuerpo_error(
                codigos.get(excepcion.status_code, CODIGO_ERROR_INTERNO),
                str(excepcion.detail),
            ),
        )

    @app.exception_handler(Exception)
    async def _manejar_error_no_previsto(_: Request, excepcion: Exception) -> JSONResponse:
        # El detalle técnico no se expone al cliente; queda en el registro del servidor.
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=cuerpo_error(
                CODIGO_ERROR_INTERNO,
                "Ocurrió un error no previsto al procesar la petición.",
            ),
        )
