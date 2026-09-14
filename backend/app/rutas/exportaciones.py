"""Exportación del historial consultado.

El CSV se genera en el servidor y no en el cliente: así el archivo contiene
exactamente las lecturas que el usuario tiene autorización de ver, y no lo que
el cliente decida incluir.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Response

from ..dependencias import obtener_repositorio
from ..repositorios.base import RepositorioDatos
from ..seguridad import UsuarioAutenticado, requiere_operacion
from ..servicios import evaluacion

enrutador = APIRouter(prefix="/exportaciones", tags=["Exportaciones"])


@enrutador.get(
    "/lecturas.csv",
    summary="Exportar en CSV las lecturas resultantes de una consulta",
    response_class=Response,
    responses={200: {"content": {"text/csv": {}}}},
)
def exportar_lecturas(
    modulo_id: str | None = Query(default=None, max_length=64),
    variable: str | None = Query(default=None, max_length=32),
    desde: datetime | None = Query(default=None),
    hasta: datetime | None = Query(default=None),
    limite: int = Query(default=1000, ge=1, le=5000),
    _: UsuarioAutenticado = Depends(requiere_operacion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> Response:
    """Devuelve el historial consultado como archivo descargable."""
    lecturas_consultadas = repositorio.listar_lecturas(
        modulo_id=modulo_id,
        variable=variable.strip().lower() if variable else None,
        desde=desde,
        hasta=hasta,
        limite=limite,
    )
    contenido = evaluacion.generar_csv(lecturas_consultadas)
    marca = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    nombre = f"sigvach-lecturas-{marca}.csv"
    # La marca de orden de bytes (BOM) permite que las herramientas de planilla
    # reconozcan la codificación UTF-8 al abrir el archivo.
    return Response(
        content="\ufeff" + contenido,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )
