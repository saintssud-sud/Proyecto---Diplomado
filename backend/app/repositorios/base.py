"""Interfaz del repositorio de datos.

El backend no conoce la base de datos: conoce esta interfaz. Eso permite dos
implementaciones intercambiables —una sobre Cloud Firestore y otra en memoria—
y, sobre todo, permite probar las reglas de negocio y la validación sin
depender de un servicio externo ni de credenciales.
"""

from datetime import datetime
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class RepositorioDatos(Protocol):
    """Operaciones de persistencia que el backend necesita del dominio."""

    # --- Lecturas -----------------------------------------------------------
    def crear_lectura(self, datos: dict[str, Any]) -> dict[str, Any]: ...

    def obtener_lectura(self, lectura_id: str) -> dict[str, Any] | None: ...

    def listar_lecturas(
        self,
        modulo_id: str | None = None,
        variable: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limite: int = 500,
    ) -> list[dict[str, Any]]: ...

    def eliminar_lectura(self, lectura_id: str) -> bool: ...

    # --- Módulos de cultivo -------------------------------------------------
    def crear_modulo(self, datos: dict[str, Any]) -> dict[str, Any]: ...

    def obtener_modulo(self, modulo_id: str) -> dict[str, Any] | None: ...

    def listar_modulos(self, activo: bool | None = None) -> list[dict[str, Any]]: ...

    def actualizar_modulo(self, modulo_id: str, cambios: dict[str, Any]) -> dict[str, Any] | None: ...

    def eliminar_modulo(self, modulo_id: str) -> bool: ...

    # --- Perfiles de cultivo ------------------------------------------------
    def crear_perfil(self, datos: dict[str, Any]) -> dict[str, Any]: ...

    def obtener_perfil(self, perfil_id: str) -> dict[str, Any] | None: ...

    def listar_perfiles(self) -> list[dict[str, Any]]: ...

    def eliminar_perfil(self, perfil_id: str) -> bool: ...

    # --- Rangos de referencia ----------------------------------------------
    def crear_rango(self, datos: dict[str, Any]) -> dict[str, Any]: ...

    def obtener_rango(self, rango_id: str) -> dict[str, Any] | None: ...

    def buscar_rango(self, perfil_id: str, variable: str) -> dict[str, Any] | None: ...

    def listar_rangos(self, perfil_id: str | None = None) -> list[dict[str, Any]]: ...

    def actualizar_rango(self, rango_id: str, cambios: dict[str, Any]) -> dict[str, Any] | None: ...

    def eliminar_rango(self, rango_id: str) -> bool: ...

    # --- Alertas ------------------------------------------------------------
    def crear_alerta(self, datos: dict[str, Any]) -> dict[str, Any]: ...

    def obtener_alerta(self, alerta_id: str) -> dict[str, Any] | None: ...

    def listar_alertas(
        self,
        estado: str | None = None,
        modulo_id: str | None = None,
        limite: int = 200,
    ) -> list[dict[str, Any]]: ...

    def actualizar_alerta(self, alerta_id: str, cambios: dict[str, Any]) -> dict[str, Any] | None: ...

    def eliminar_alerta(self, alerta_id: str) -> bool: ...

    # --- Usuarios -----------------------------------------------------------
    # El perfil del usuario (con su rol) lo crea la aplicación al registrarse;
    # el backend lo lee para resolver la autorización de cada petición.
    def obtener_perfil_usuario(self, uid: str) -> dict[str, Any] | None: ...

    # --- Diagnóstico --------------------------------------------------------
    def verificar_conexion(self) -> bool: ...
