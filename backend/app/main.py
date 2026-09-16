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
from .config import Configuracion, obtener_configuracion
from .errores import registrar_manejadores_de_error
from .dependencias import obtener_repositorio
from .rutas import enrutador_api
from .semilla import sembrar_demostracion


def asegurar_sdk_firebase(configuracion: Configuracion) -> None:
    """Inicializa el SDK de Firebase una sola vez por proceso.

    El SDK lo necesitan **dos** componentes: el repositorio de Firestore y la
    verificación del token de identidad de Firebase Authentication. Por eso se
    inicializa aquí, al arrancar, y no de forma perezosa dentro del repositorio:
    de lo contrario la primera petición autenticada llega antes de que exista el
    SDK y el servicio responde 401 con un mensaje que oculta la causa real.

    Sin credenciales configuradas, la demostración sigue funcionando: se deja
    constancia en el registro y el servicio continúa con el repositorio en memoria.
    """
    import json
    import logging

    import firebase_admin
    from firebase_admin import credentials

    if firebase_admin._apps:
        return

    # Se deja constancia, sin exponer la clave, de si las credenciales llegaron:
    # es el primer dato que hay que mirar cuando el servicio arranca en la nube y
    # no puede acceder a la base de datos.
    logging.getLogger("sigvach").info(
        "Firebase: proyecto='%s', credenciales de servicio %s",
        configuracion.proyecto_firebase or "(sin indicar)",
        "presentes (%d caracteres)" % len(configuracion.credenciales_servicio)
        if configuracion.credenciales_servicio
        else "AUSENTES (se intentara con las credenciales por defecto)",
    )

    try:
        if configuracion.credenciales_servicio:
            datos = json.loads(configuracion.credenciales_servicio)
            credencial = credentials.Certificate(datos)
        else:
            # Alternativa: GOOGLE_APPLICATION_CREDENTIALS apuntando al archivo.
            credencial = credentials.ApplicationDefault()
        opciones = (
            {"projectId": configuracion.proyecto_firebase}
            if configuracion.proyecto_firebase
            else None
        )
        firebase_admin.initialize_app(credencial, opciones)
    except Exception as error:  # noqa: BLE001 - la demostración debe seguir en pie
        logging.getLogger("sigvach").warning(
            "No se pudo inicializar el SDK de Firebase al arrancar: %s: %s",
            type(error).__name__,
            error,
        )

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
    """Prepara el SDK de Firebase y, si corresponde, los datos de demostración.

    El SDK se inicializa **siempre** al arrancar, antes de atender la primera
    petición: la verificación del token de identidad de Firebase Authentication
    lo necesita, y hasta ahora solo se inicializaba de forma perezosa al tocar
    Firestore, lo que hacía que la primera petición autenticada fallara con 401.

    Con `USAR_REPOSITORIO_EN_MEMORIA=true` el servicio arranca sin credenciales,
    de modo que el sistema pueda recorrerse completo en la demostración o en una
    revisión del tribunal sin depender de Firebase ni de los sensores. En ese
    caso, si hay credenciales configuradas, también se inicializa el SDK y el
    inicio de sesión de los usuarios sigue funcionando.
    """
    configuracion = obtener_configuracion()
    asegurar_sdk_firebase(configuracion)
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
