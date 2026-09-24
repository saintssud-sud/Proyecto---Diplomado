"""Configuración del backend de SIGVACH.

Todos los valores se leen del entorno del proceso (o de un archivo `.env` en
desarrollo). Ninguna credencial se escribe en el código ni en el repositorio:
la plantilla de las variables requeridas está en `.env.example`, en la raíz
del proyecto.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Rutas absolutas: el `.env` se busca junto al paquete (`backend/.env`) y en la
# raíz del proyecto, en ese orden, de modo que el servicio arranque igual sin
# importar la carpeta desde la que se ejecute. La raíz tiene precedencia.
# En el despliegue no hay `.env`: las variables llegan del entorno del servicio.
_RAIZ_BACKEND = Path(__file__).resolve().parent.parent
_RAIZ_PROYECTO = _RAIZ_BACKEND.parent


class Configuracion(BaseSettings):
    """Configuración del servicio, resuelta desde variables de entorno."""

    model_config = SettingsConfigDict(
        env_file=(_RAIZ_BACKEND / ".env", _RAIZ_PROYECTO / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    # --- Servicio -----------------------------------------------------------
    entorno: str = Field(
        default="desarrollo",
        validation_alias=AliasChoices("ENTORNO", "ENVIRONMENT"),
    )
    puerto: int = Field(default=8000, validation_alias=AliasChoices("PORT", "PUERTO"))
    origenes_permitidos: str = Field(
        default="http://localhost:8080",
        validation_alias=AliasChoices("ALLOWED_ORIGINS", "ORIGENES_PERMITIDOS"),
    )
    version_api: str = "v1"

    # --- Firebase -----------------------------------------------------------
    proyecto_firebase: str = Field(
        default="",
        validation_alias=AliasChoices("FIREBASE_PROJECT_ID", "PROYECTO_FIREBASE"),
    )
    credenciales_servicio: str = Field(
        default="",
        validation_alias=AliasChoices(
            "FIREBASE_SERVICE_ACCOUNT_JSON", "CREDENCIALES_SERVICIO"
        ),
    )

    # --- Módulo de adquisición (ESP32) --------------------------------------
    clave_dispositivo: str = Field(
        default="",
        validation_alias=AliasChoices("DEVICE_API_KEY", "CLAVE_DISPOSITIVO"),
    )

    # --- Reglas de negocio parametrizables ---------------------------------
    # Los nombres de los roles se leen de la configuración para que la decisión
    # sobre el alcance de roles no obligue a tocar el código de autorización.
    rol_administrador: str = Field(
        default="administrador",
        validation_alias=AliasChoices("ROL_ADMINISTRADOR", "ADMIN_ROLE"),
    )
    rol_operador: str = Field(
        default="operador",
        validation_alias=AliasChoices("ROL_OPERADOR", "OPERATOR_ROLE"),
    )
    rol_invitado: str = Field(
        default="invitado",
        validation_alias=AliasChoices("ROL_INVITADO", "GUEST_ROLE"),
    )
    minutos_tolerancia_reloj: int = Field(
        default=5,
        validation_alias=AliasChoices(
            "MINUTOS_TOLERANCIA_RELOJ", "CLOCK_TOLERANCE_MINUTES"
        ),
    )
    usar_repositorio_en_memoria: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "USAR_REPOSITORIO_EN_MEMORIA", "USE_IN_MEMORY_REPOSITORY"
        ),
    )

    @property
    def origenes(self) -> list[str]:
        """Orígenes permitidos para CORS, a partir de una lista separada por comas."""
        return [origen.strip() for origen in self.origenes_permitidos.split(",") if origen.strip()]

    @property
    def es_produccion(self) -> bool:
        return self.entorno.strip().lower() in {"produccion", "producción", "production"}

    @property
    def roles_administracion(self) -> set[str]:
        """Roles que pueden ejecutar operaciones de administración."""
        return {self.rol_administrador}

    @property
    def roles_operacion(self) -> set[str]:
        """Roles que pueden registrar y consultar datos del cultivo."""
        return {self.rol_administrador, self.rol_operador}

    @property
    def roles_consulta(self) -> set[str]:
        """Roles que pueden consultar la información del cultivo.

        El rol de invitado se suma a los de operación: consulta el panel, el
        historial y las alertas, pero no registra mediciones ni modifica la
        configuración. La distinción se resuelve aquí, en la configuración, para
        que añadir o quitar un rol de solo consulta no obligue a tocar el código
        de autorización.
        """
        return self.roles_operacion | {self.rol_invitado}


@lru_cache
def obtener_configuracion() -> Configuracion:
    """Devuelve la configuración, resolviéndola una sola vez por proceso."""
    return Configuracion()
