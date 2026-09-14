"""Endpoints de lecturas: recepción del dispositivo, registro manual y consulta."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from ..dependencias import obtener_repositorio
from ..errores import CODIGO_VALIDACION, ErrorApi
from ..esquemas import (
    CATALOGO_VARIABLES,
    LecturaEntrada,
    LecturaManualEntrada,
    LecturaSalida,
    ResumenVariable,
)
from ..repositorios.base import RepositorioDatos
from ..seguridad import UsuarioAutenticado, dispositivo_autorizado, requiere_administracion, requiere_operacion
from ..servicios import evaluacion, lecturas

enrutador = APIRouter(prefix="/lecturas", tags=["Lecturas"])


def _variable_valida(variable: str | None) -> str | None:
    """Valida el filtro por variable contra el catálogo."""
    if variable is None:
        return None
    codigo = variable.strip().lower()
    if codigo not in CATALOGO_VARIABLES:
        admitidas = ", ".join(sorted(CATALOGO_VARIABLES))
        raise ErrorApi(
            422,
            CODIGO_VALIDACION,
            f"La variable '{variable}' no pertenece al catálogo.",
            {"variables_admitidas": admitidas},
        )
    return codigo


@enrutador.post(
    "",
    response_model=LecturaSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una lectura enviada por el módulo de adquisición",
    dependencies=[Depends(dispositivo_autorizado)],
)
def registrar_desde_dispositivo(
    entrada: LecturaEntrada,
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Recibe una lectura del ESP32, autenticada con la clave de dispositivo."""
    return lecturas.registrar(repositorio, entrada, origen="automatico")


@enrutador.post(
    "/manual",
    response_model=LecturaSalida,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar manualmente una lectura medida con instrumentos portátiles",
)
def registrar_manualmente(
    entrada: LecturaManualEntrada,
    _: UsuarioAutenticado = Depends(requiere_operacion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Registra una lectura manual: el origen lo fija el servidor, no el cliente."""
    return lecturas.registrar(repositorio, entrada, origen="manual")


@enrutador.get(
    "",
    response_model=list[LecturaSalida],
    summary="Consultar lecturas por módulo, variable y rango de fechas",
)
def consultar_lecturas(
    modulo_id: str | None = Query(default=None, max_length=64),
    variable: str | None = Query(default=None, max_length=32),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    limite: int = Query(default=200, ge=1, le=1000),
    _: UsuarioAutenticado = Depends(requiere_operacion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> list[dict]:
    """Devuelve las lecturas que satisfacen los tres filtros aplicados."""
    return repositorio.listar_lecturas(
        modulo_id=modulo_id,
        variable=_variable_valida(variable),
        desde=desde,
        hasta=hasta,
        limite=limite,
    )


@enrutador.get(
    "/resumen",
    response_model=list[ResumenVariable],
    summary="Promedio, máximo y mínimo por variable en el periodo consultado",
)
def resumir_lecturas(
    modulo_id: str | None = Query(default=None, max_length=64),
    variable: str | None = Query(default=None, max_length=32),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    _: UsuarioAutenticado = Depends(requiere_operacion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> list[dict]:
    """Resume la serie consultada; es el cálculo que sostiene el gráfico de tendencia."""
    lecturas_consultadas = repositorio.listar_lecturas(
        modulo_id=modulo_id,
        variable=_variable_valida(variable),
        desde=desde,
        hasta=hasta,
        limite=1000,
    )

    por_variable: dict[str, list[dict]] = {}
    for lectura in lecturas_consultadas:
        por_variable.setdefault(str(lectura["variable"]), []).append(lectura)

    resumen = []
    for codigo, registros in sorted(por_variable.items()):
        calculo = evaluacion.resumen_serie([float(registro["valor"]) for registro in registros])
        if calculo is None:
            continue
        resumen.append(
            {
                "variable": codigo,
                "unidad": str(registros[0].get("unidad", "")),
                **calculo,
            }
        )
    return resumen


@enrutador.get(
    "/{lectura_id}",
    response_model=LecturaSalida,
    summary="Consultar una lectura por su identificador",
)
def obtener_lectura(
    lectura_id: str,
    _: UsuarioAutenticado = Depends(requiere_operacion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Devuelve una lectura concreta."""
    return lecturas.obtener_o_error(repositorio, lectura_id)


@enrutador.delete(
    "/{lectura_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una lectura",
)
def eliminar_lectura(
    lectura_id: str,
    _: UsuarioAutenticado = Depends(requiere_administracion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> None:
    """Elimina una lectura; la operación queda reservada a la administración."""
    lecturas.obtener_o_error(repositorio, lectura_id)
    repositorio.eliminar_lectura(lectura_id)
