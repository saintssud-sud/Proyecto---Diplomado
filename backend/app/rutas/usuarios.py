"""Endpoints de las cuentas del sistema.

El perfil de cada cuenta se crea al registrarse y vive en la colección
`usuarios`, con el **uid** de Firebase Authentication como identificador del
documento. El backend lo lee para resolver el rol de cada petición y expone dos
conjuntos de operaciones, con niveles de autorización distintos:

* el **perfil propio**, que el usuario consulta y mantiene sin poder tocar su rol
  ni su estado de activación;
* la **administración de las cuentas**, que permite listarlas, consultarlas,
  modificar sus datos, cambiar su rol, activarlas o desactivarlas y eliminarlas.

La separación es deliberada: son dos recursos y dos esquemas de entrada distintos,
de modo que el contrato —y no solo la interfaz— impida que alguien eleve sus
privilegios. Hasta ahora el panel escribía directamente en la base de datos para
gestionar las cuentas; con estas operaciones esa escritura pasa por el servicio,
que es el único componente que valida y autoriza.
"""

from fastapi import APIRouter, Depends, status

from ..config import Configuracion, obtener_configuracion
from ..dependencias import obtener_repositorio
from ..errores import (
    CODIGO_CONFLICTO,
    CODIGO_NO_ENCONTRADO,
    CODIGO_VALIDACION,
    ErrorApi,
)
from ..esquemas import (
    UsuarioAdministracionActualizacion,
    UsuarioPerfilActualizacion,
    UsuarioPerfilSalida,
)
from ..repositorios.base import RepositorioDatos
from ..seguridad import (
    UsuarioAutenticado,
    requiere_administracion,
    usuario_actual,
)

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


# --------------------------------------------------------------------------- #
# Administración de las cuentas
# --------------------------------------------------------------------------- #
def _roles_admitidos(configuracion: Configuracion) -> set[str]:
    """Roles que el servicio reconoce, según la configuración y no el código."""
    return (
        configuracion.roles_administracion
        | configuracion.roles_operacion
        | {configuracion.rol_invitado}
    )


@enrutador.get(
    "",
    response_model=list[UsuarioPerfilSalida],
    summary="Listar las cuentas registradas",
)
def listar_cuentas(
    _: UsuarioAutenticado = Depends(requiere_administracion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> list[dict]:
    """Devuelve todas las cuentas con su rol y su estado, para el panel de usuarios."""
    return repositorio.listar_perfiles_usuario()


@enrutador.get(
    "/{uid}",
    response_model=UsuarioPerfilSalida,
    summary="Consultar el perfil de una cuenta",
)
def obtener_cuenta(
    uid: str,
    _: UsuarioAutenticado = Depends(requiere_administracion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> dict:
    """Devuelve el perfil de la cuenta indicada."""
    return _perfil_o_error(repositorio, uid)


@enrutador.patch(
    "/{uid}",
    response_model=UsuarioPerfilSalida,
    summary="Modificar los datos, el rol o el estado de una cuenta",
)
def actualizar_cuenta(
    uid: str,
    entrada: UsuarioAdministracionActualizacion,
    administrador: UsuarioAutenticado = Depends(requiere_administracion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
    configuracion: Configuracion = Depends(obtener_configuracion),
) -> dict:
    """Aplica los cambios indicados a la cuenta, con dos protecciones.

    Primero, el rol debe pertenecer a los que el servicio reconoce: un valor
    arbitrario dejaría una cuenta sin atribuciones resolubles. Segundo, la
    administración **no puede quitarse a sí misma** el rol ni desactivar su propia
    cuenta: sin esa comprobación, un descuido dejaría el sistema sin nadie que
    pueda administrarlo.
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

    if "rol" in cambios:
        admitidos = _roles_admitidos(configuracion)
        if cambios["rol"] not in admitidos:
            raise ErrorApi(
                422,
                CODIGO_VALIDACION,
                "El rol indicado no existe en el sistema.",
                {"roles_admitidos": sorted(admitidos)},
            )

    if uid == administrador.uid and ("rol" in cambios or cambios.get("activo") is False):
        raise ErrorApi(
            409,
            CODIGO_CONFLICTO,
            "La administración no puede cambiar su propio rol ni desactivar su cuenta.",
        )

    perfil = repositorio.actualizar_perfil_usuario(uid, cambios)
    if perfil is None:
        raise ErrorApi(
            404,
            CODIGO_NO_ENCONTRADO,
            "No existe una cuenta con el identificador indicado.",
        )
    return perfil


@enrutador.delete(
    "/{uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar el perfil de una cuenta",
)
def eliminar_cuenta(
    uid: str,
    administrador: UsuarioAutenticado = Depends(requiere_administracion),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
) -> None:
    """Elimina el perfil de la cuenta indicada.

    Se elimina el perfil de la base de datos; la credencial de Firebase
    Authentication permanece y queda como limitación declarada del prototipo. La
    cuenta de la propia administración no puede eliminarse a sí misma.
    """
    if uid == administrador.uid:
        raise ErrorApi(
            409,
            CODIGO_CONFLICTO,
            "La administración no puede eliminar su propia cuenta.",
        )
    if not repositorio.eliminar_perfil_usuario(uid):
        raise ErrorApi(
            404,
            CODIGO_NO_ENCONTRADO,
            "No existe una cuenta con el identificador indicado.",
        )
