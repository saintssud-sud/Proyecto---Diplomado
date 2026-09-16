"""Endpoints de los módulos o zonas de cultivo."""

from fastapi import APIRouter, Depends, Query, status

from ..dependencias import obtener_repositorio
from ..errores import CODIGO_CONFLICTO, CODIGO_NO_ENCONTRADO, ErrorApi
from ..esquemas import ModuloActualizacion, ModuloEntrada, ModuloSalida
from ..repositorios.base import RepositorioDatos
from ..seguridad import UsuarioAutenticado, requiere_administracion, requiere_consulta

enrutador = APIRouter(prefix="/modulos", tags=["Módulos de cultivo"])


def _modulo_o_error(repositorio: RepositorioDatos, modulo_id: str) -> dict:
    modulo = repositorio.obtener_modulo(modulo_id)
    if modulo is None:
        raise ErrorApi(
            404,
            CODIGO_NO_ENCONTRADO,
            f"El módulo de cultivo '{modulo_id}' no existe.",
        )
    return modulo


@enrutador.post(
    "",
    response_model=ModuloSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un módulo o zona de cultivo",
)
def crear_modulo(
    entrada: ModuloEntrada,
    _: UsuarioAutenticado = Depends(requiere_administracion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Crea un módulo asociado a un tipo de cultivo y a un perfil de referencia."""
    return repositorio.crear_modulo(entrada.model_dump())


@enrutador.get(
    "",
    response_model=list[ModuloSalida],
    summary="Listar los módulos de cultivo",
)
def listar_modulos(
    activo: bool | None = Query(default=None, description="Filtra por módulos activos o inactivos"),
    _: UsuarioAutenticado = Depends(requiere_consulta),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> list[dict]:
    """Devuelve los módulos registrados."""
    return repositorio.listar_modulos(activo=activo)


@enrutador.get(
    "/{modulo_id}",
    response_model=ModuloSalida,
    summary="Consultar un módulo de cultivo",
)
def obtener_modulo(
    modulo_id: str,
    _: UsuarioAutenticado = Depends(requiere_consulta),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Devuelve un módulo concreto."""
    return _modulo_o_error(repositorio, modulo_id)


@enrutador.patch(
    "/{modulo_id}",
    response_model=ModuloSalida,
    summary="Modificar un módulo de cultivo",
)
def actualizar_modulo(
    modulo_id: str,
    entrada: ModuloActualizacion,
    _: UsuarioAutenticado = Depends(requiere_administracion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Aplica únicamente los campos presentes en la petición."""
    _modulo_o_error(repositorio, modulo_id)
    cambios = entrada.model_dump(exclude_unset=True)
    if not cambios:
        raise ErrorApi(
            400,
            "datos_invalidos",
            "La petición no contiene ningún campo para modificar.",
        )
    return repositorio.actualizar_modulo(modulo_id, cambios)


@enrutador.delete(
    "/{modulo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un módulo de cultivo",
)
def eliminar_modulo(
    modulo_id: str,
    _: UsuarioAutenticado = Depends(requiere_administracion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> None:
    """Elimina un módulo solo si no tiene lecturas asociadas.

    Si las tiene, la respuesta indica desactivarlo en lugar de eliminarlo: el
    historial de un módulo con lecturas no debe perderse por un borrado.
    """
    _modulo_o_error(repositorio, modulo_id)
    if repositorio.listar_lecturas(modulo_id=modulo_id, limite=1):
        raise ErrorApi(
            409,
            CODIGO_CONFLICTO,
            "El módulo tiene lecturas registradas; desactívelo en lugar de eliminarlo.",
        )
    repositorio.eliminar_modulo(modulo_id)
