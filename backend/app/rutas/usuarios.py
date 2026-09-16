"""Endpoints del perfil del usuario que realiza la petición.

El perfil de cada cuenta se crea al registrarse y vive en la colección
`usuarios`, con el **uid** de Firebase Authentication como identificador del
documento. Hasta ahora el backend solo lo leía —para resolver el rol de cada
petición—; con estas operaciones el propio usuario puede consultarlo y mantener
sus datos de contacto sin que la aplicación tenga que escribir en la base.

Lo que **no** se expone aquí es deliberado: cambiar el rol o el estado de
activación es una atribución de administración y se resuelve en su propio
recurso. Un usuario no puede elevar sus privilegios ni reactivar su cuenta
modificando su perfil.
"""

from fastapi import APIRouter, Depends

from ..dependencias import obtener_repositorio
from ..errores import CODIGO_NO_ENCONTRADO, ErrorApi
from ..esquemas import UsuarioPerfilActualizacion, UsuarioPerfilSalida
from ..repositorios.base import RepositorioDatos
from ..seguridad import UsuarioAutenticado, usuario_actual

enrutador = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def _perfil_o_error(repositorio: RepositorioDatos, uid: str) -> dict:
    """Devuelve el perfil del usuario o responde que no existe.

    La autorización ya garantiza que el perfil exista y esté habilitado
    (`usuario_actual` lo comprueba antes); esta comprobación cubre el caso de
    que el documento desaparezca entre la autorización y la consulta.
    """
    perfil = repositorio.obtener_perfil_usuario(uid)
    if perfil is None:
        raise ErrorApi(
            404,
            CODIGO_NO_ENCONTRADO,
            "La cuenta no tiene un perfil registrado en el sistema.",
        )
    return perfil


@enrutador.get(
    "/perfil",
    response_model=UsuarioPerfilSalida,
    summary="Consultar el perfil de la cuenta que realiza la petición",
)
def obtener_mi_perfil(
    usuario: UsuarioAutenticado = Depends(usuario_actual),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Devuelve el perfil del usuario autenticado.

    El rol que se informa es el que el **servicio** resolvió para esta petición,
    no un valor que el cliente pueda proponer.
    """
    perfil = _perfil_o_error(repositorio, usuario.uid)
    perfil["rol"] = usuario.rol
    return perfil


@enrutador.patch(
    "/perfil",
    response_model=UsuarioPerfilSalida,
    summary="Actualizar los datos personales del usuario autenticado",
)
def actualizar_mi_perfil(
    entrada: UsuarioPerfilActualizacion,
    usuario: UsuarioAutenticado = Depends(usuario_actual),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Modifica los datos de contacto del usuario autenticado.

    Solo se aplican los campos enviados; el rol, el estado de activación y el
    correo no forman parte del esquema de entrada, de modo que ningún cliente
    pueda modificarlos por esta vía.
    """
    cambios = {
        campo: valor
        for campo, valor in entrada.model_dump(exclude_unset=True).items()
        if valor is not None
    }
    if not cambios:
        raise ErrorApi(
            400,
            "solicitud_invalida",
            "No se indicó ningún dato para modificar.",
        )

    perfil = repositorio.actualizar_perfil_usuario(usuario.uid, cambios)
    if perfil is None:
        raise ErrorApi(
            404,
            CODIGO_NO_ENCONTRADO,
            "La cuenta no tiene un perfil registrado en el sistema.",
        )
    perfil["rol"] = usuario.rol
    return perfil
