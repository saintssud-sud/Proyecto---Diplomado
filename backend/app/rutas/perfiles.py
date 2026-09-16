"""Endpoints de los perfiles de cultivo.

Un perfil agrupa los rangos de referencia de las variables para un tipo de
cultivo (lechuga, tomate, fresa u otro). Los módulos de cultivo se asocian a un
perfil, y los rangos del perfil son los que se aplican al evaluar cada lectura.
"""

from fastapi import APIRouter, Depends, status

from ..dependencias import obtener_repositorio
from ..errores import CODIGO_CONFLICTO, CODIGO_NO_ENCONTRADO, ErrorApi
from ..esquemas import PerfilEntrada, PerfilSalida
from ..repositorios.base import RepositorioDatos
from ..seguridad import UsuarioAutenticado, requiere_administracion, requiere_consulta

enrutador = APIRouter(prefix="/perfiles", tags=["Perfiles de cultivo"])


def _perfil_o_error(repositorio: RepositorioDatos, perfil_id: str) -> dict:
    perfil = repositorio.obtener_perfil(perfil_id)
    if perfil is None:
        raise ErrorApi(
            404,
            CODIGO_NO_ENCONTRADO,
            f"El perfil de cultivo '{perfil_id}' no existe.",
        )
    return perfil


@enrutador.post(
    "",
    response_model=PerfilSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un perfil de cultivo",
)
def crear_perfil(
    entrada: PerfilEntrada,
    _: UsuarioAutenticado = Depends(requiere_administracion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Crea un perfil de cultivo al que luego se le asocian sus rangos."""
    return repositorio.crear_perfil(entrada.model_dump())


@enrutador.get("", response_model=list[PerfilSalida], summary="Listar los perfiles de cultivo")
def listar_perfiles(
    _: UsuarioAutenticado = Depends(requiere_consulta),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> list[dict]:
    """Devuelve los perfiles registrados."""
    return repositorio.listar_perfiles()


@enrutador.get("/{perfil_id}", response_model=PerfilSalida, summary="Consultar un perfil de cultivo")
def obtener_perfil(
    perfil_id: str,
    _: UsuarioAutenticado = Depends(requiere_consulta),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Devuelve un perfil concreto."""
    return _perfil_o_error(repositorio, perfil_id)


@enrutador.delete(
    "/{perfil_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un perfil de cultivo",
)
def eliminar_perfil(
    perfil_id: str,
    _: UsuarioAutenticado = Depends(requiere_administracion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> None:
    """Elimina un perfil sin rangos asociados.

    Si el perfil tiene rangos definidos, se responde con un conflicto: eliminar
    un perfil en uso dejaría a los módulos asociados sin referencia para evaluar
    sus lecturas.
    """
    _perfil_o_error(repositorio, perfil_id)
    if repositorio.listar_rangos(perfil_id=perfil_id):
        raise ErrorApi(
            409,
            CODIGO_CONFLICTO,
            "El perfil tiene rangos de referencia definidos; elimínelos primero.",
        )
    repositorio.eliminar_perfil(perfil_id)
