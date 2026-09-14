"""Punto de entrada del backend.

Ejecución en local::

    uvicorn app.main:app --reload --port 8000

Documentación navegable del contrato (OpenAPI): http://localhost:8000/docs
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import obtener_configuracion
from .errores import registrar_manejadores_de_error
from .dependencias import obtener_repositorio
from .rutas import enrutador_api
from .semilla import sembrar_demostracion

DESCRIPCION = """
API del sistema SI.G.VA.C.H. (Sistema de Gestión de Variables para Cultivos Hidropónicos).

El backend concentra la validación de los datos, la autorización por rol y las reglas
de negocio; es el único componente que accede a Cloud Firestore. La documentación que
sigue es el contrato de la API descrito en el apartado 2.4.4 de la monografía.

Identidades admitidas:
* **Usuarios**: token de identidad de Firebase Authentication en la cabecera `Authorization`.
* **Módulo de adquisición**: clave de dispositivo en la cabecera `X-Device-Key`.
"""


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI) -> AsyncIterator[None]:
    """Prepara los datos de demostración cuando no hay base de datos real.

    Con `USAR_REPOSITORIO_EN_MEMORIA=true` el servicio arranca sin credenciales,
    de modo que el sistema pueda recorrerse completo en la demostración o en una
    revisión del tribunal sin depender de Firebase ni de los sensores.
    """
    configuracion = obtener_configuracion()
    if configuracion.usar_repositorio_en_memoria:
        sembrar_demostracion(obtener_repositorio(configuracion))
    yield


def crear_aplicacion() -> FastAPI:
    """Construye la aplicación con sus rutas, su CORS y sus manejadores de error."""
    configuracion = obtener_configuracion()

    aplicacion = FastAPI(
        title="SIGVACH — API",
        description=DESCRIPCION,
        version=__version__,
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=ciclo_de_vida,
    )

    aplicacion.add_middleware(
        CORSMiddleware,
        allow_origins=configuracion.origenes,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Device-Key"],
    )

    registrar_manejadores_de_error(aplicacion)
    aplicacion.include_router(enrutador_api, prefix="/api/v1")

    @aplicacion.get("/", include_in_schema=False)
    def raiz() -> dict[str, str]:
        """Respuesta informativa para comprobar que el servicio está en pie."""
        return {
            "servicio": "SIGVACH API",
            "version_api": configuracion.version_api,
            "documentacion": "/docs",
        }

    return aplicacion


app = crear_aplicacion()
