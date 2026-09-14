"""Endpoints de los rangos de referencia.

Un rango pertenece a un perfil de cultivo y a una variable, y es el valor de
referencia contra el que el servidor evalúa cada lectura recibida.
"""

from fastapi import APIRouter, Depends, Query, status

from ..dependencias import obtener_repositorio
from ..errores import CODIGO_CONFLICTO, CODIGO_NO_ENCONTRADO, ErrorApi
from ..esquemas import CATALOGO_VARIABLES, RangoActualizacion, RangoEntrada, RangoSalida, _normalizar_variable
from ..repositorios.base import RepositorioDatos
from ..seguridad import UsuarioAutenticado, requiere_administracion, requiere_operacion

enrutador = APIRouter(prefix="/rangos", tags=["Rangos de referencia"])


def _rango_o_error(repositorio: RepositorioDatos, rango_id: str) -> dict:
    rango = repositorio.obtener_rango(rango_id)
    if rango is None:
        raise ErrorApi(
            404,
            CODIGO_NO_ENCONTRADO,
            f"No existe un rango con el identificador '{rango_id}'.",
        )
    return rango


def _con_unidad(rango: dict) -> dict:
    """Agrega la unidad del catálogo a la representación del rango."""
    definicion = CATALOGO_VARIABLES.get(str(rango.get("variable", "")))
    return {**rango, "unidad": definicion.unidad if definicion else ""}


@enrutador.post(
    "",
    response_model=RangoSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Definir el rango de referencia de una variable en un perfil",
)
def crear_rango(
    entrada: RangoEntrada,
    _: UsuarioAutenticado = Depends(requiere_administracion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Crea el rango; no se admite más de un rango por perfil y variable."""
    if repositorio.obtener_perfil(entrada.perfil_id) is None:
        raise ErrorApi(
            404,
            CODIGO_NO_ENCONTRADO,
            f"El perfil de cultivo '{entrada.perfil_id}' no existe.",
        )
    if repositorio.buscar_rango(entrada.perfil_id, entrada.variable) is not None:
        raise ErrorApi(
            409,
            CODIGO_CONFLICTO,
            f"El perfil ya tiene un rango definido para la variable '{entrada.variable}'.",
        )
    return _con_unidad(repositorio.crear_rango(entrada.model_dump()))


@enrutador.get(
    "",
    response_model=list[RangoSalida],
    summary="Listar los rangos de referencia",
)
def listar_rangos(
    perfil_id: str | None = Query(default=None, max_length=64),
    variable: str | None = Query(default=None, max_length=32),
    _: UsuarioAutenticado = Depends(requiere_operacion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> list[dict]:
    """Devuelve los rangos, opcionalmente filtrados por perfil y variable."""
    rangos = repositorio.listar_rangos(perfil_id=perfil_id)
    if variable:
        codigo = _normalizar_variable(variable)
        rangos = [rango for rango in rangos if rango.get("variable") == codigo]
    return [_con_unidad(rango) for rango in rangos]


@enrutador.get("/{rango_id}", response_model=RangoSalida, summary="Consultar un rango de referencia")
def obtener_rango(
    rango_id: str,
    _: UsuarioAutenticado = Depends(requiere_operacion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Devuelve un rango concreto."""
    return _con_unidad(_rango_o_error(repositorio, rango_id))


@enrutador.patch(
    "/{rango_id}",
    response_model=RangoSalida,
    summary="Modificar un rango de referencia",
)
def actualizar_rango(
    rango_id: str,
    entrada: RangoActualizacion,
    _: UsuarioAutenticado = Depends(requiere_administracion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Modifica el rango, revalidando la coherencia entre mínimo y máximo."""
    actual = _rango_o_error(repositorio, rango_id)
    cambios = entrada.model_dump(exclude_unset=True)
    if not cambios:
        raise ErrorApi(400, "datos_invalidos", "La petición no contiene ningún campo para modificar.")

    candidato = {
        "perfil_id": actual["perfil_id"],
        "variable": actual["variable"],
        "minimo": cambios.get("minimo", actual["minimo"]),
        "maximo": cambios.get("maximo", actual["maximo"]),
    }
    # Se reutiliza el esquema de entrada para aplicar las mismas validaciones.
    validado = RangoEntrada(**candidato)

    actualizado = repositorio.actualizar_rango(
        rango_id, {"minimo": validado.minimo, "maximo": validado.maximo}
    )
    return _con_unidad(actualizado or actual)


@enrutador.delete(
    "/{rango_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un rango de referencia",
)
def eliminar_rango(
    rango_id: str,
    _: UsuarioAutenticado = Depends(requiere_administracion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> None:
    """Elimina un rango de referencia."""
    _rango_o_error(repositorio, rango_id)
    repositorio.eliminar_rango(rango_id)
