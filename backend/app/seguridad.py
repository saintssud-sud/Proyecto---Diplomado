"""Autenticación y autorización.

Dos identidades distintas acceden a la API:

* las **personas**, que presentan el token de identidad que emite Firebase
  Authentication al iniciar sesión;
* el **módulo de adquisición** (ESP32), que presenta su propia clave de
  dispositivo en la cabecera `X-Device-Key` y nunca credenciales de usuario.

La autorización por rol se resuelve siempre aquí, en el servidor. Que la
interfaz oculte una acción es una comodidad de uso, no un control de acceso.
"""

from dataclasses import dataclass
from hmac import compare_digest

from fastapi import Depends, Header

from .config import Configuracion, obtener_configuracion
from .dependencias import obtener_repositorio
from .errores import (
    CODIGO_ERROR_INTERNO,
    CODIGO_NO_AUTENTICADO,
    CODIGO_SIN_PERMISO,
    ErrorApi,
)
from .repositorios.base import RepositorioDatos


@dataclass(frozen=True)
class UsuarioAutenticado:
    """Identidad verificada de quien realiza la petición."""

    uid: str
    correo: str
    rol: str


def _verificar_token_identidad(token: str) -> dict:
    """Verifica el token contra Firebase Authentication."""
    try:
        from firebase_admin import auth as auth_firebase
    except ModuleNotFoundError as excepcion:  # pragma: no cover - depende del entorno
        raise ErrorApi(
            500,
            CODIGO_ERROR_INTERNO,
            "El servidor no tiene disponible el verificador de identidad.",
        ) from excepcion
    try:
        return auth_firebase.verify_id_token(token)
    except Exception as excepcion:
        raise ErrorApi(
            401,
            CODIGO_NO_AUTENTICADO,
            "El token de identidad no es válido o expiró.",
        ) from excepcion


def usuario_actual(
    autorizacion: str | None = Header(default=None, alias="Authorization"),
    repositorio: RepositorioDatos = Depends(obtener_repositorio),
    configuracion: Configuracion = Depends(obtener_configuracion),
) -> UsuarioAutenticado:
    """Resuelve la identidad del usuario a partir del token de la cabecera."""
    if not autorizacion or not autorizacion.lower().startswith("bearer "):
        raise ErrorApi(
            401,
            CODIGO_NO_AUTENTICADO,
            "Falta el token de identidad en la cabecera Authorization.",
        )

    token = autorizacion.split(" ", 1)[1].strip()
    try:
        datos = _verificar_token_identidad(token)
    except ErrorApi:
        # Error ya tipificado por el verificador (token inválido, servicio caído).
        raise
    except Exception as excepcion:
        # Cualquier fallo inesperado del verificador se resuelve como acceso
        # denegado: es preferible negar el acceso a exponer un error interno.
        raise ErrorApi(
            401,
            CODIGO_NO_AUTENTICADO,
            "El token de identidad no es válido o expiró.",
        ) from excepcion

    uid = str(datos.get("uid") or datos.get("user_id") or "")
    correo = str(datos.get("email") or "")

    perfil = repositorio.obtener_perfil_usuario(uid) if uid else None
    if perfil is None:
        raise ErrorApi(
            403,
            CODIGO_SIN_PERMISO,
            "La cuenta no tiene un perfil registrado en el sistema.",
        )
    if perfil.get("activo") is False:
        raise ErrorApi(
            403,
            CODIGO_SIN_PERMISO,
            "La cuenta está desactivada; comuníquese con el administrador.",
        )

    rol = str(perfil.get("rol") or configuracion.rol_operador)
    return UsuarioAutenticado(uid=uid, correo=correo or str(perfil.get("email") or ""), rol=rol)


def requiere_administracion(
    usuario: UsuarioAutenticado = Depends(usuario_actual),
    configuracion: Configuracion = Depends(obtener_configuracion),
) -> UsuarioAutenticado:
    """Exige un rol con atribuciones de administración."""
    if usuario.rol not in configuracion.roles_administracion:
        raise ErrorApi(
            403,
            CODIGO_SIN_PERMISO,
            "La operación requiere el rol de administrador.",
            {
                "rol_requerido": sorted(configuracion.roles_administracion),
                "rol_actual": usuario.rol,
            },
        )
    return usuario


def requiere_operacion(
    usuario: UsuarioAutenticado = Depends(usuario_actual),
    configuracion: Configuracion = Depends(obtener_configuracion),
) -> UsuarioAutenticado:
    """Exige un rol con atribuciones de operación sobre el cultivo."""
    if usuario.rol not in configuracion.roles_operacion:
        raise ErrorApi(
            403,
            CODIGO_SIN_PERMISO,
            "La operación requiere un rol habilitado para operar sobre el cultivo.",
            {
                "rol_requerido": sorted(configuracion.roles_operacion),
                "rol_actual": usuario.rol,
            },
        )
    return usuario


def dispositivo_autorizado(
    clave: str | None = Header(default=None, alias="X-Device-Key"),
    configuracion: Configuracion = Depends(obtener_configuracion),
) -> str:
    """Autentica al módulo de adquisición mediante su clave de dispositivo."""
    esperada = configuracion.clave_dispositivo
    if not esperada:
        raise ErrorApi(
            500,
            CODIGO_ERROR_INTERNO,
            "El servicio no tiene configurada la clave del módulo de adquisición.",
        )
    if not clave or not compare_digest(clave, esperada):
        raise ErrorApi(
            401,
            CODIGO_NO_AUTENTICADO,
            "La clave del módulo de adquisición no es válida.",
        )
    return "dispositivo"
