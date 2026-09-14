"""Repositorio en memoria.

Se usa en las pruebas automatizadas y permite ejecutar el backend en local sin
credenciales de Firebase (con `USAR_REPOSITORIO_EN_MEMORIA=true`). Su
comportamiento frente al contrato es el mismo que el del repositorio de
Cloud Firestore: misma firma, mismas reglas de orden y de filtrado.
"""

from datetime import datetime, timezone
from threading import Lock
from typing import Any
from uuid import uuid4

COLECCIONES = ("lecturas", "modulos", "perfiles", "rangos", "alertas", "usuarios")


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


class RepositorioMemoria:
    """Implementación del repositorio sobre diccionarios en memoria."""

    def __init__(self) -> None:
        self._datos: dict[str, dict[str, dict[str, Any]]] = {
            coleccion: {} for coleccion in COLECCIONES
        }
        self._cerrojo = Lock()

    # --- Utilidades internas ------------------------------------------------
    def _insertar(self, coleccion: str, datos: dict[str, Any]) -> dict[str, Any]:
        with self._cerrojo:
            identificador = datos.get("id") or uuid4().hex
            documento = {**datos, "id": identificador}
            documento.setdefault("creado_en", _ahora())
            self._datos[coleccion][identificador] = documento
            return dict(documento)

    def _actualizar(
        self, coleccion: str, identificador: str, cambios: dict[str, Any]
    ) -> dict[str, Any] | None:
        with self._cerrojo:
            documento = self._datos[coleccion].get(identificador)
            if documento is None:
                return None
            documento.update(cambios)
            return dict(documento)

    def _eliminar(self, coleccion: str, identificador: str) -> bool:
        with self._cerrojo:
            return self._datos[coleccion].pop(identificador, None) is not None

    def _listar(self, coleccion: str) -> list[dict[str, Any]]:
        with self._cerrojo:
            return [dict(documento) for documento in self._datos[coleccion].values()]

    # --- Lecturas -----------------------------------------------------------
    def crear_lectura(self, datos: dict[str, Any]) -> dict[str, Any]:
        return self._insertar("lecturas", datos)

    def obtener_lectura(self, lectura_id: str) -> dict[str, Any] | None:
        documento = self._datos["lecturas"].get(lectura_id)
        return dict(documento) if documento else None

    def listar_lecturas(
        self,
        modulo_id: str | None = None,
        variable: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limite: int = 500,
    ) -> list[dict[str, Any]]:
        resultado = []
        for lectura in self._listar("lecturas"):
            if modulo_id and lectura.get("modulo_id") != modulo_id:
                continue
            if variable and lectura.get("variable") != variable:
                continue
            marca = lectura.get("timestamp")
            if desde and marca and marca < desde:
                continue
            if hasta and marca and marca > hasta:
                continue
            resultado.append(lectura)
        # Orden descendente por marca de tiempo: lo más reciente primero.
        resultado.sort(key=lambda item: item.get("timestamp") or _ahora(), reverse=True)
        return resultado[:limite]

    def eliminar_lectura(self, lectura_id: str) -> bool:
        return self._eliminar("lecturas", lectura_id)

    # --- Módulos de cultivo -------------------------------------------------
    def crear_modulo(self, datos: dict[str, Any]) -> dict[str, Any]:
        return self._insertar("modulos", datos)

    def obtener_modulo(self, modulo_id: str) -> dict[str, Any] | None:
        documento = self._datos["modulos"].get(modulo_id)
        return dict(documento) if documento else None

    def listar_modulos(self, activo: bool | None = None) -> list[dict[str, Any]]:
        modulos = self._listar("modulos")
        if activo is not None:
            modulos = [modulo for modulo in modulos if modulo.get("activo", True) is activo]
        modulos.sort(key=lambda item: item.get("nombre", ""))
        return modulos

    def actualizar_modulo(self, modulo_id: str, cambios: dict[str, Any]) -> dict[str, Any] | None:
        return self._actualizar("modulos", modulo_id, cambios)

    def eliminar_modulo(self, modulo_id: str) -> bool:
        return self._eliminar("modulos", modulo_id)

    # --- Perfiles de cultivo ------------------------------------------------
    def crear_perfil(self, datos: dict[str, Any]) -> dict[str, Any]:
        return self._insertar("perfiles", datos)

    def obtener_perfil(self, perfil_id: str) -> dict[str, Any] | None:
        documento = self._datos["perfiles"].get(perfil_id)
        return dict(documento) if documento else None

    def listar_perfiles(self) -> list[dict[str, Any]]:
        perfiles = self._listar("perfiles")
        perfiles.sort(key=lambda item: item.get("nombre", ""))
        return perfiles

    def eliminar_perfil(self, perfil_id: str) -> bool:
        return self._eliminar("perfiles", perfil_id)

    # --- Rangos de referencia ----------------------------------------------
    def crear_rango(self, datos: dict[str, Any]) -> dict[str, Any]:
        return self._insertar("rangos", datos)

    def obtener_rango(self, rango_id: str) -> dict[str, Any] | None:
        documento = self._datos["rangos"].get(rango_id)
        return dict(documento) if documento else None

    def buscar_rango(self, perfil_id: str, variable: str) -> dict[str, Any] | None:
        for rango in self._listar("rangos"):
            if rango.get("perfil_id") == perfil_id and rango.get("variable") == variable:
                return rango
        return None

    def listar_rangos(self, perfil_id: str | None = None) -> list[dict[str, Any]]:
        rangos = self._listar("rangos")
        if perfil_id:
            rangos = [rango for rango in rangos if rango.get("perfil_id") == perfil_id]
        rangos.sort(key=lambda item: (item.get("perfil_id", ""), item.get("variable", "")))
        return rangos

    def actualizar_rango(self, rango_id: str, cambios: dict[str, Any]) -> dict[str, Any] | None:
        return self._actualizar("rangos", rango_id, cambios)

    def eliminar_rango(self, rango_id: str) -> bool:
        return self._eliminar("rangos", rango_id)

    # --- Alertas ------------------------------------------------------------
    def crear_alerta(self, datos: dict[str, Any]) -> dict[str, Any]:
        return self._insertar("alertas", datos)

    def obtener_alerta(self, alerta_id: str) -> dict[str, Any] | None:
        documento = self._datos["alertas"].get(alerta_id)
        return dict(documento) if documento else None

    def listar_alertas(
        self,
        estado: str | None = None,
        modulo_id: str | None = None,
        limite: int = 200,
    ) -> list[dict[str, Any]]:
        alertas = self._listar("alertas")
        if estado:
            alertas = [alerta for alerta in alertas if alerta.get("estado") == estado]
        if modulo_id:
            alertas = [alerta for alerta in alertas if alerta.get("modulo_id") == modulo_id]
        alertas.sort(key=lambda item: item.get("timestamp") or _ahora(), reverse=True)
        return alertas[:limite]

    def actualizar_alerta(self, alerta_id: str, cambios: dict[str, Any]) -> dict[str, Any] | None:
        return self._actualizar("alertas", alerta_id, cambios)

    def eliminar_alerta(self, alerta_id: str) -> bool:
        return self._eliminar("alertas", alerta_id)

    # --- Usuarios -----------------------------------------------------------
    def registrar_perfil_usuario(self, uid: str, datos: dict[str, Any]) -> dict[str, Any]:
        """Alta del perfil de un usuario; se usa en las pruebas del backend."""
        with self._cerrojo:
            documento = {**datos, "id": uid}
            self._datos["usuarios"][uid] = documento
            return dict(documento)

    def obtener_perfil_usuario(self, uid: str) -> dict[str, Any] | None:
        documento = self._datos["usuarios"].get(uid)
        return dict(documento) if documento else None

    # --- Diagnóstico --------------------------------------------------------
    def verificar_conexion(self) -> bool:
        return True
