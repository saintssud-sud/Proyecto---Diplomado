"""Proveedores de dependencias de la aplicación.

El repositorio se resuelve una sola vez por proceso: en producción es el de
Cloud Firestore y en desarrollo o en las pruebas puede ser el de memoria.

El repositorio activo queda envuelto por la memoria intermedia de las consultas
de lecturas (`SEGUNDOS_CACHE_LECTURAS`, diez segundos por omisión). Se envuelve
aquí, en el único lugar donde se elige la implementación, y no dentro de cada
repositorio: así la memoria vale igual para los dos y ningún llamador cambia.
"""

from fastapi import Depends

from .config import Configuracion, obtener_configuracion
from .repositorios.base import RepositorioDatos
from .repositorios.cache import RepositorioConCache
from .repositorios.firestore import RepositorioFirestore
from .repositorios.memoria import RepositorioMemoria

_repositorio: RepositorioDatos | None = None


def obtener_repositorio(
    configuracion: Configuracion = Depends(obtener_configuracion),
) -> RepositorioDatos:
    """Devuelve el repositorio de datos activo, con su memoria de lecturas."""
    global _repositorio
    if _repositorio is None:
        if configuracion.usar_repositorio_en_memoria:
            base: RepositorioDatos = RepositorioMemoria()
        else:
            base = RepositorioFirestore(configuracion)
        _repositorio = RepositorioConCache(base, segundos=configuracion.segundos_cache_lecturas)
    return _repositorio


def restablecer_repositorio() -> None:
    """Descarta el repositorio activo; se usa en las pruebas."""
    global _repositorio
    _repositorio = None
