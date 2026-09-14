"""Configuración común de las pruebas.

Las pruebas no dependen de Firebase ni de credenciales: sustituyen el
repositorio por el de memoria y la verificación del token por una identidad
fija. Lo que se prueba es la lógica del backend —validación, autorización,
evaluación de rangos y formato de las respuestas—, que es justamente la parte
que debe funcionar sin depender del cliente.
"""

from dataclasses import dataclass

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Configuracion, obtener_configuracion
from app.dependencias import obtener_repositorio
from app.main import crear_aplicacion
from app.repositorios.memoria import RepositorioMemoria
from app import seguridad
from app.seguridad import UsuarioAutenticado, usuario_actual

CLAVE_DISPOSITIVO = "clave-de-prueba-del-dispositivo"
UID_ADMINISTRADOR = "u-admin"
UID_OPERADOR = "u-operador"
UID_INACTIVO = "u-inactivo"


@dataclass
class Entorno:
    """Entorno de prueba con los datos mínimos del dominio ya cargados."""

    repositorio: RepositorioMemoria
    configuracion: Configuracion
    perfil_id: str
    modulo_id: str
    modulo_inactivo_id: str


@pytest.fixture
def entorno() -> Entorno:
    """Repositorio en memoria con un perfil, un módulo, un rango y tres usuarios."""
    repositorio = RepositorioMemoria()

    perfil = repositorio.crear_perfil({"nombre": "Lechuga", "predefinido": True})
    modulo = repositorio.crear_modulo(
        {
            "nombre": "Módulo 1",
            "tipo_cultivo": "Lechuga",
            "perfil_id": perfil["id"],
            "activo": True,
        }
    )
    modulo_inactivo = repositorio.crear_modulo(
        {
            "nombre": "Módulo 2",
            "tipo_cultivo": "Lechuga",
            "perfil_id": perfil["id"],
            "activo": False,
        }
    )
    repositorio.crear_rango(
        {"perfil_id": perfil["id"], "variable": "ph", "minimo": 5.5, "maximo": 6.5}
    )
    repositorio.registrar_perfil_usuario(
        UID_ADMINISTRADOR,
        {"email": "admin@sigvach.com", "rol": "admin", "activo": True, "nombre": "Administrador"},
    )
    repositorio.registrar_perfil_usuario(
        UID_OPERADOR,
        {"email": "operador@sigvach.com", "rol": "usuario", "activo": True, "nombre": "Operador"},
    )
    repositorio.registrar_perfil_usuario(
        UID_INACTIVO,
        {"email": "inactivo@sigvach.com", "rol": "usuario", "activo": False, "nombre": "Inactivo"},
    )

    configuracion = Configuracion(
        clave_dispositivo=CLAVE_DISPOSITIVO,
        origenes_permitidos="http://localhost:8080",
        usar_repositorio_en_memoria=True,
    )

    return Entorno(
        repositorio=repositorio,
        configuracion=configuracion,
        perfil_id=perfil["id"],
        modulo_id=modulo["id"],
        modulo_inactivo_id=modulo_inactivo["id"],
    )


def _aplicacion(entorno: Entorno, identidad: UsuarioAutenticado | None) -> FastAPI:
    """Crea la aplicación con el repositorio y la configuración de prueba."""
    aplicacion = crear_aplicacion()
    aplicacion.dependency_overrides[obtener_configuracion] = lambda: entorno.configuracion
    aplicacion.dependency_overrides[obtener_repositorio] = lambda: entorno.repositorio
    if identidad is not None:
        aplicacion.dependency_overrides[usuario_actual] = lambda: identidad
    return aplicacion


@pytest.fixture
def cliente_publico(entorno: Entorno) -> TestClient:
    """Cliente sin identidad: no se sustituye la verificación del token."""
    return TestClient(_aplicacion(entorno, None))


@pytest.fixture
def cliente_operador(entorno: Entorno) -> TestClient:
    """Cliente autenticado con el rol de operación."""
    identidad = UsuarioAutenticado(uid=UID_OPERADOR, correo="operador@sigvach.com", rol="usuario")
    return TestClient(_aplicacion(entorno, identidad))


@pytest.fixture
def cliente_administrador(entorno: Entorno) -> TestClient:
    """Cliente autenticado con el rol de administración."""
    identidad = UsuarioAutenticado(uid=UID_ADMINISTRADOR, correo="admin@sigvach.com", rol="admin")
    return TestClient(_aplicacion(entorno, identidad))


@pytest.fixture
def cliente_con_token(entorno: Entorno, monkeypatch) -> TestClient:
    """Cliente que ejecuta la verificación de identidad real, con verificador simulado.

    Se sustituye únicamente la llamada a Firebase Authentication: el resto del
    camino —lectura del perfil, comprobación de que la cuenta esté activa y
    resolución del rol— se ejecuta tal como lo hará en producción.
    """

    def _verificador_simulado(token: str) -> dict:
        identidades = {
            "token-admin": (UID_ADMINISTRADOR, "admin@sigvach.com"),
            "token-operador": (UID_OPERADOR, "operador@sigvach.com"),
            "token-inactivo": (UID_INACTIVO, "inactivo@sigvach.com"),
            "token-sin-perfil": ("u-desconocido", "nadie@sigvach.com"),
        }
        if token not in identidades:
            raise ValueError("token no reconocido por el verificador simulado")
        uid, correo = identidades[token]
        return {"uid": uid, "email": correo}

    monkeypatch.setattr(seguridad, "_verificar_token_identidad", _verificador_simulado)
    return TestClient(_aplicacion(entorno, None))


def cabecera(rol: str) -> dict[str, str]:
    """Cabecera de autorización para uno de los tokens del verificador simulado."""
    return {"Authorization": f"Bearer token-{rol}"}


def cabecera_dispositivo(clave: str = CLAVE_DISPOSITIVO) -> dict[str, str]:
    """Cabecera de autenticación del módulo de adquisición."""
    return {"X-Device-Key": clave}
