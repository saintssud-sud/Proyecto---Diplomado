"""Repositorio sobre Cloud Firestore.

Es la implementación que opera en el despliegue real: el backend es el único
componente que accede a la base de datos, con la cuenta de servicio del
proyecto. Las credenciales llegan por variables de entorno y nunca por el
repositorio.

El SDK de administración se importa de forma perezosa, de modo que este módulo
puede importarse y probarse sin tener `firebase-admin` instalado ni credenciales
disponibles.
"""

import json
from datetime import datetime, timezone
from typing import Any

from ..config import Configuracion

COLECCION_LECTURAS = "lecturas"
COLECCION_MODULOS = "modulos_cultivo"
COLECCION_PERFILES = "perfiles_cultivo"
COLECCION_RANGOS = "rangos"
COLECCION_ALERTAS = "alertas"
COLECCION_USUARIOS = "usuarios"


def _normalizar_fecha(valor: Any) -> datetime | None:
    """Devuelve la fecha en UTC con zona horaria explícita."""
    if isinstance(valor, datetime):
        return valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)
    return None


def _clave_antiguedad(documento: dict[str, Any]) -> tuple[str, str]:
    """Clave de orden por antigüedad: la fecha de creación y, como desempate, el id."""
    return (str(documento.get("creado_en") or ""), str(documento.get("id") or ""))


class RepositorioFirestore:
    """Implementación del repositorio sobre Cloud Firestore."""

    def __init__(self, configuracion: Configuracion) -> None:
        self._configuracion = configuracion
        self._cliente = None

    # --- Inicialización -----------------------------------------------------
    def _obtener_cliente(self):
        """Inicializa el SDK en la primera operación y reutiliza el cliente."""
        if self._cliente is not None:
            return self._cliente

        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            if self._configuracion.credenciales_servicio:
                datos = json.loads(self._configuracion.credenciales_servicio)
                credencial = credentials.Certificate(datos)
            else:
                # Alternativa: GOOGLE_APPLICATION_CREDENTIALS apuntando al archivo.
                credencial = credentials.ApplicationDefault()
            opciones = (
                {"projectId": self._configuracion.proyecto_firebase}
                if self._configuracion.proyecto_firebase
                else None
            )
            firebase_admin.initialize_app(credencial, opciones)

        self._cliente = firestore.client()
        return self._cliente

    def _coleccion(self, nombre: str):
        return self._obtener_cliente().collection(nombre)

    @staticmethod
    def _documento(instantanea) -> dict[str, Any] | None:
        if not instantanea.exists:
            return None
        datos = instantanea.to_dict() or {}
        datos["id"] = instantanea.id
        for campo in ("timestamp", "creado_en", "atendida_en"):
            if campo in datos:
                datos[campo] = _normalizar_fecha(datos[campo])
        return datos

    # --- Lecturas -----------------------------------------------------------
    def crear_lectura(self, datos: dict[str, Any]) -> dict[str, Any]:
        documento = dict(datos)
        documento.pop("id", None)
        documento.setdefault("creado_en", datetime.now(timezone.utc))
        referencia = self._coleccion(COLECCION_LECTURAS).document()
        referencia.set(documento)
        return {**documento, "id": referencia.id}

    def obtener_lectura(self, lectura_id: str) -> dict[str, Any] | None:
        return self._documento(self._coleccion(COLECCION_LECTURAS).document(lectura_id).get())

    def listar_lecturas(
        self,
        modulo_id: str | None = None,
        variable: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limite: int = 500,
    ) -> list[dict[str, Any]]:
        consulta = self._coleccion(COLECCION_LECTURAS)
        # Los filtros por igualdad y por rango de fechas requieren un índice
        # compuesto en Firestore; se documenta en el archivo README del backend.
        if modulo_id:
            consulta = consulta.where("modulo_id", "==", modulo_id)
        if variable:
            consulta = consulta.where("variable", "==", variable)
        if desde:
            consulta = consulta.where("timestamp", ">=", desde)
        if hasta:
            consulta = consulta.where("timestamp", "<=", hasta)
        consulta = consulta.order_by("timestamp", direction="DESCENDING").limit(limite)
        return [self._documento(instantanea) for instantanea in consulta.stream()]  # type: ignore[misc]

    def eliminar_lectura(self, lectura_id: str) -> bool:
        referencia = self._coleccion(COLECCION_LECTURAS).document(lectura_id)
        if not referencia.get().exists:
            return False
        referencia.delete()
        return True

    # --- Módulos de cultivo -------------------------------------------------
    def crear_modulo(self, datos: dict[str, Any]) -> dict[str, Any]:
        documento = {**datos, "creado_en": datetime.now(timezone.utc)}
        documento.pop("id", None)
        referencia = self._coleccion(COLECCION_MODULOS).document()
        referencia.set(documento)
        return {**documento, "id": referencia.id}

    def obtener_modulo(self, modulo_id: str) -> dict[str, Any] | None:
        return self._documento(self._coleccion(COLECCION_MODULOS).document(modulo_id).get())

    def listar_modulos(self, activo: bool | None = None) -> list[dict[str, Any]]:
        """Lista los módulos ordenados por fecha de creación.

        El orden se resuelve aquí, en memoria, y no con un ordenamiento de
        Firestore: el criterio debe ser la antigüedad —la aplicación presenta el
        primer módulo como módulo vigente y el alfabético anteponía un módulo
        creado después si su nombre se escribía con otra grafía— y así no depende
        de un índice compuesto ni del juego de caracteres.
        """
        consulta = self._coleccion(COLECCION_MODULOS)
        if activo is not None:
            consulta = consulta.where("activo", "==", activo)
        documentos = [self._documento(instantanea) for instantanea in consulta.stream()]  # type: ignore[misc]
        return sorted(documentos, key=_clave_antiguedad)

    def actualizar_modulo(self, modulo_id: str, cambios: dict[str, Any]) -> dict[str, Any] | None:
        referencia = self._coleccion(COLECCION_MODULOS).document(modulo_id)
        if not referencia.get().exists:
            return None
        referencia.update(cambios)
        return self._documento(referencia.get())

    def eliminar_modulo(self, modulo_id: str) -> bool:
        referencia = self._coleccion(COLECCION_MODULOS).document(modulo_id)
        if not referencia.get().exists:
            return False
        referencia.delete()
        return True

    # --- Perfiles de cultivo ------------------------------------------------
    def crear_perfil(self, datos: dict[str, Any]) -> dict[str, Any]:
        documento = {**datos, "creado_en": datetime.now(timezone.utc)}
        documento.pop("id", None)
        referencia = self._coleccion(COLECCION_PERFILES).document()
        referencia.set(documento)
        return {**documento, "id": referencia.id}

    def obtener_perfil(self, perfil_id: str) -> dict[str, Any] | None:
        return self._documento(self._coleccion(COLECCION_PERFILES).document(perfil_id).get())

    def listar_perfiles(self) -> list[dict[str, Any]]:
        consulta = self._coleccion(COLECCION_PERFILES).order_by("nombre")
        return [self._documento(instantanea) for instantanea in consulta.stream()]  # type: ignore[misc]

    def eliminar_perfil(self, perfil_id: str) -> bool:
        referencia = self._coleccion(COLECCION_PERFILES).document(perfil_id)
        if not referencia.get().exists:
            return False
        referencia.delete()
        return True

    # --- Rangos de referencia ----------------------------------------------
    def crear_rango(self, datos: dict[str, Any]) -> dict[str, Any]:
        documento = {**datos, "creado_en": datetime.now(timezone.utc)}
        documento.pop("id", None)
        referencia = self._coleccion(COLECCION_RANGOS).document()
        referencia.set(documento)
        return {**documento, "id": referencia.id}

    def obtener_rango(self, rango_id: str) -> dict[str, Any] | None:
        return self._documento(self._coleccion(COLECCION_RANGOS).document(rango_id).get())

    def buscar_rango(self, perfil_id: str, variable: str) -> dict[str, Any] | None:
        consulta = (
            self._coleccion(COLECCION_RANGOS)
            .where("perfil_id", "==", perfil_id)
            .where("variable", "==", variable)
            .limit(1)
        )
        for instantanea in consulta.stream():
            return self._documento(instantanea)
        return None

    def listar_rangos(self, perfil_id: str | None = None) -> list[dict[str, Any]]:
        consulta = self._coleccion(COLECCION_RANGOS)
        if perfil_id:
            consulta = consulta.where("perfil_id", "==", perfil_id)
        return [self._documento(instantanea) for instantanea in consulta.stream()]  # type: ignore[misc]

    def actualizar_rango(self, rango_id: str, cambios: dict[str, Any]) -> dict[str, Any] | None:
        referencia = self._coleccion(COLECCION_RANGOS).document(rango_id)
        if not referencia.get().exists:
            return None
        referencia.update(cambios)
        return self._documento(referencia.get())

    def eliminar_rango(self, rango_id: str) -> bool:
        referencia = self._coleccion(COLECCION_RANGOS).document(rango_id)
        if not referencia.get().exists:
            return False
        referencia.delete()
        return True

    # --- Alertas ------------------------------------------------------------
    def crear_alerta(self, datos: dict[str, Any]) -> dict[str, Any]:
        documento = {**datos, "creado_en": datetime.now(timezone.utc)}
        documento.pop("id", None)
        referencia = self._coleccion(COLECCION_ALERTAS).document()
        referencia.set(documento)
        return {**documento, "id": referencia.id}

    def obtener_alerta(self, alerta_id: str) -> dict[str, Any] | None:
        return self._documento(self._coleccion(COLECCION_ALERTAS).document(alerta_id).get())

    def listar_alertas(
        self,
        estado: str | None = None,
        modulo_id: str | None = None,
        limite: int = 200,
    ) -> list[dict[str, Any]]:
        consulta = self._coleccion(COLECCION_ALERTAS)
        if estado:
            consulta = consulta.where("estado", "==", estado)
        if modulo_id:
            consulta = consulta.where("modulo_id", "==", modulo_id)
        consulta = consulta.order_by("timestamp", direction="DESCENDING").limit(limite)
        return [self._documento(instantanea) for instantanea in consulta.stream()]  # type: ignore[misc]

    def actualizar_alerta(self, alerta_id: str, cambios: dict[str, Any]) -> dict[str, Any] | None:
        referencia = self._coleccion(COLECCION_ALERTAS).document(alerta_id)
        if not referencia.get().exists:
            return None
        referencia.update(cambios)
        return self._documento(referencia.get())

    def eliminar_alerta(self, alerta_id: str) -> bool:
        referencia = self._coleccion(COLECCION_ALERTAS).document(alerta_id)
        if not referencia.get().exists:
            return False
        referencia.delete()
        return True

    # --- Usuarios -----------------------------------------------------------
    def obtener_perfil_usuario(self, uid: str) -> dict[str, Any] | None:
        """Lee el perfil del usuario (con su rol) creado por la aplicación."""
        return self._documento(self._coleccion(COLECCION_USUARIOS).document(uid).get())

    def actualizar_perfil_usuario(
        self, uid: str, cambios: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Modifica los datos del perfil; devuelve None si no existe.

        El identificador del documento es el uid que emite Firebase
        Authentication, de modo que el perfil y la sesión no puedan desalinearse.
        """
        referencia = self._coleccion(COLECCION_USUARIOS).document(uid)
        instantanea = referencia.get()
        if not instantanea.exists:
            return None
        referencia.update(cambios)
        return self.obtener_perfil_usuario(uid)

    # --- Diagnóstico --------------------------------------------------------
    def verificar_conexion(self) -> bool:
        try:
            next(self._coleccion(COLECCION_LECTURAS).limit(1).stream(), None)
            return True
        except Exception:
            return False
