"""Endpoint de salud del servicio.

Es público y sin autenticación: sirve para comprobar que el servicio responde y
que alcanza la base de datos. Se documenta en el apartado 2.9 como el mecanismo
empleado para verificar el despliegue y para medir el efecto de la suspensión
por inactividad de la capa gratuita (RNF-02).
"""

from fastapi import APIRouter, Depends

from ..config import Configuracion, obtener_configuracion
from ..dependencias import obtener_repositorio
from ..esquemas import SaludSalida
from ..repositorios.base import RepositorioDatos

enrutador = APIRouter(prefix="/salud", tags=["Diagnóstico"])


@enrutador.get("", response_model=SaludSalida, summary="Comprobar el estado del servicio")
def consultar_salud(
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
    configuracion: Configuracion = Depends(obtener_configuracion),
) -> SaludSalida:
    """Informa si el servicio y la base de datos responden."""
    conectada = repositorio.verificar_conexion()
    return SaludSalida(
        estado="ok" if conectada else "degradado",
        version_api=configuracion.version_api,
        entorno=configuracion.entorno,
        base_de_datos="conectada" if conectada else "no disponible",
    )
