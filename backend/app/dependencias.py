"""Proveedores de dependencias de la aplicación.

El repositorio se resuelve una sola vez por proceso: en producción es el de
Cloud Firestore y en desarrollo o en las pruebas puede ser el de memoria.
"""

from fastapi import Depends

from .config import Configuracion, obtener_configuracion
from .repositorios.base import RepositorioDatos
from .repositorios.firestore import RepositorioFirestore
from .repositorios.memoria import RepositorioMemoria

_repositorio: RepositorioDatos | None = None


def obtener_repositorio(
    configuracion: Configuracion = Depends(obtener_configuracion),
) -> RepositorioDatos:
    """Devuelve el repositorio de datos activo."""
    global _repositorio
    if _repositorio is None:
        if configuracion.usar_repositorio_en_memoria:
            _repositorio = RepositorioMemoria()
        else:
            _repositorio = RepositorioFirestore(configuracion)
    return _repositorio


def restablecer_repositorio() -> None:
    """Descarta el repositorio activo; se usa en las pruebas."""
    global _repositorio
    _repositorio = None
