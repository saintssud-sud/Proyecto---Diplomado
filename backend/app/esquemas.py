"""Esquemas de entrada y salida de la API, con la validación de datos.

La validación de los datos de entrada es un requisito mínimo del producto
(requisito 8) y reside aquí, en el servidor: el cliente puede equivocarse o
puede ser manipulado, y ninguna de las dos situaciones debe llegar a la base
de datos.

Convención de nombres: los esquemas de entrada terminan en `Entrada` y los de
salida en `Salida`.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from .config import obtener_configuracion


@dataclass(frozen=True)
class DefinicionVariable:
    """Catálogo de una variable gestionada: nombre, unidad y límites físicos."""

    codigo: str
    nombre: str
    unidad: str
    minimo: float
    maximo: float


# Catálogo de variables gestionadas por el sistema. Los límites son físicos
# (lo que el sensor puede entregar y tiene sentido almacenar), no agronómicos:
# los rangos agronómicos de referencia son configurables y viven en los perfiles
# de cultivo.
CATALOGO_VARIABLES: dict[str, DefinicionVariable] = {
    "ph": DefinicionVariable("ph", "pH", "", 0.0, 14.0),
    "tds": DefinicionVariable("tds", "Sólidos disueltos totales", "ppm", 0.0, 5000.0),
    "ec": DefinicionVariable("ec", "Conductividad eléctrica", "mS/cm", 0.0, 20.0),
    "temp_solucion": DefinicionVariable(
        "temp_solucion", "Temperatura de la solución nutritiva", "°C", -10.0, 60.0
    ),
    "temp_ambiental": DefinicionVariable(
        "temp_ambiental", "Temperatura ambiental", "°C", -20.0, 70.0
    ),
    "humedad": DefinicionVariable("humedad", "Humedad relativa", "%", 0.0, 100.0),
    "nivel_agua": DefinicionVariable("nivel_agua", "Nivel de agua", "cm", 0.0, 200.0),
}

ORIGENES = ("automatico", "manual")
ESTADOS_ALERTA = ("activa", "atendida")


def definicion_de_variable(codigo: str) -> DefinicionVariable | None:
    """Devuelve la definición de una variable del catálogo, o None si no existe."""
    return CATALOGO_VARIABLES.get(codigo.strip().lower())


def _normalizar_variable(valor: str) -> str:
    """Valida que la variable exista en el catálogo y la devuelve normalizada."""
    codigo = valor.strip().lower()
    if codigo not in CATALOGO_VARIABLES:
        admitidas = ", ".join(sorted(CATALOGO_VARIABLES))
        raise ValueError(f"variable desconocida; se admiten: {admitidas}")
    return codigo


class _BaseEntrada(BaseModel):
    """Base común: se rechazan los campos no declarados en el contrato."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class _LecturaBase(_BaseEntrada):
    """Campos y validaciones comunes a toda lectura, cualquiera sea su origen."""

    modulo_id: str = Field(min_length=1, max_length=64)
    variable: str = Field(min_length=2, max_length=32)
    valor: float
    timestamp: datetime | None = None
    observacion: str | None = Field(default=None, max_length=200)

    @field_validator("variable")
    @classmethod
    def _variable_del_catalogo(cls, valor: str) -> str:
        return _normalizar_variable(valor)

    @field_validator("timestamp")
    @classmethod
    def _marca_de_tiempo_coherente(cls, valor: datetime | None) -> datetime | None:
        if valor is None:
            return valor
        if valor.tzinfo is None:
            valor = valor.replace(tzinfo=timezone.utc)
        tolerancia = timedelta(minutes=obtener_configuracion().minutos_tolerancia_reloj)
        if valor > datetime.now(timezone.utc) + tolerancia:
            raise ValueError("la marca de tiempo no puede estar en el futuro")
        return valor

    @field_validator("valor")
    @classmethod
    def _valor_en_rango_fisico(cls, valor: float, info: ValidationInfo) -> float:
        """Comprueba el valor contra los límites físicos de su variable.

        Se valida en el campo `valor` y no a nivel de modelo para que el error
        señale el campo rechazado: el detalle del 422 debe indicar qué corregir.
        """
        definicion = CATALOGO_VARIABLES.get(str(info.data.get("variable", "")))
        if definicion is None:
            # El validador de `variable` ya informó el problema.
            return valor
        if not (definicion.minimo <= valor <= definicion.maximo):
            unidad = f" {definicion.unidad}" if definicion.unidad else ""
            raise ValueError(
                f"{definicion.codigo} debe estar entre {definicion.minimo} y "
                f"{definicion.maximo}{unidad}"
            )
        return valor


class LecturaEntrada(_LecturaBase):
    """Lectura enviada por el módulo de adquisición al publicar una medición."""

    unidad: str | None = Field(default=None, max_length=16)
    origen: Literal["automatico", "manual"] = "automatico"

    @field_validator("unidad")
    @classmethod
    def _unidad_coherente(cls, unidad: str | None, info: ValidationInfo) -> str | None:
        """Si el cliente declara la unidad, debe coincidir con la del catálogo."""
        if unidad is None:
            return unidad
        definicion = CATALOGO_VARIABLES.get(str(info.data.get("variable", "")))
        if definicion is not None and unidad.strip() != definicion.unidad:
            raise ValueError(
                f"la unidad de {definicion.codigo} es '{definicion.unidad}' y se recibió "
                f"'{unidad}'"
            )
        return unidad


class LecturaManualEntrada(_LecturaBase):
    """Lectura registrada por un usuario con instrumentos portátiles.

    El origen no se acepta desde el cliente: el servidor lo fija como `manual`,
    de modo que una lectura no pueda declararse automática sin serlo.
    """


class ModuloEntrada(_BaseEntrada):
    """Módulo o zona de cultivo."""

    nombre: str = Field(min_length=2, max_length=60)
    tipo_cultivo: str = Field(min_length=2, max_length=40)
    perfil_id: str = Field(min_length=1, max_length=64)
    ubicacion: str | None = Field(default=None, max_length=120)
    activo: bool = True


class ModuloActualizacion(_BaseEntrada):
    """Modificación parcial de un módulo de cultivo."""

    nombre: str | None = Field(default=None, min_length=2, max_length=60)
    tipo_cultivo: str | None = Field(default=None, min_length=2, max_length=40)
    perfil_id: str | None = Field(default=None, min_length=1, max_length=64)
    ubicacion: str | None = Field(default=None, max_length=120)
    activo: bool | None = None


class RangoEntrada(_BaseEntrada):
    """Rango de referencia de una variable dentro de un perfil de cultivo."""

    perfil_id: str = Field(min_length=1, max_length=64)
    variable: str = Field(min_length=2, max_length=32)
    minimo: float
    maximo: float

    @field_validator("variable")
    @classmethod
    def _variable_del_catalogo(cls, valor: str) -> str:
        return _normalizar_variable(valor)

    @field_validator("maximo")
    @classmethod
    def _rango_coherente(cls, maximo: float, info: ValidationInfo) -> float:
        """Verifica la coherencia del rango y su pertenencia al límite físico."""
        minimo = info.data.get("minimo")
        definicion = CATALOGO_VARIABLES.get(str(info.data.get("variable", "")))
        if minimo is not None and minimo >= maximo:
            raise ValueError("el mínimo del rango debe ser menor que el máximo")
        if definicion is not None and minimo is not None:
            if minimo < definicion.minimo or maximo > definicion.maximo:
                unidad = f" {definicion.unidad}" if definicion.unidad else ""
                raise ValueError(
                    f"el rango de {definicion.codigo} debe estar comprendido entre "
                    f"{definicion.minimo} y {definicion.maximo}{unidad}"
                )
        return maximo


class RangoActualizacion(_BaseEntrada):
    """Modificación parcial de un rango de referencia."""

    minimo: float | None = None
    maximo: float | None = None


class AlertaActualizacion(_BaseEntrada):
    """Cambio de estado de una alerta."""

    estado: Literal["activa", "atendida"]
    observacion: str | None = Field(default=None, max_length=200)


class UsuarioPerfilActualizacion(_BaseEntrada):
    """Datos personales que el propio usuario puede modificar.

    Solo admite los datos de contacto y el cargo. El **rol** y el estado de
    activación quedan fuera del esquema a propósito: no se rechazan con un
    mensaje, simplemente no existen como campos de entrada, de modo que un
    cliente no pueda elevar sus propios privilegios ni reactivarse.
    """

    nombre: str | None = Field(default=None, min_length=2, max_length=80)
    telefono: str | None = Field(default=None, max_length=30)
    cargo: str | None = Field(default=None, max_length=60)


class PerfilEntrada(_BaseEntrada):
    """Perfil de cultivo con sus rangos de referencia."""

    nombre: str = Field(min_length=2, max_length=60)
    descripcion: str | None = Field(default=None, max_length=200)
    predefinido: bool = False


# ---------------------------------------------------------------------------
# Esquemas de salida
# ---------------------------------------------------------------------------


class _BaseSalida(BaseModel):
    model_config = ConfigDict(extra="ignore")


class SaludSalida(_BaseSalida):
    estado: str
    version_api: str
    entorno: str
    base_de_datos: str


class LecturaSalida(_BaseSalida):
    id: str
    modulo_id: str
    variable: str
    valor: float
    unidad: str
    origen: str
    # Identificador del usuario que registró la lectura; nulo cuando la envió el
    # módulo de adquisición, porque entonces la lectura queda identificada por su
    # módulo y su origen automático.
    registrado_por: str | None = None
    timestamp: datetime
    estado_rango: str | None = None
    # La observación se registra con la medición manual y forma parte de su
    # trazabilidad: se devuelve para que el cliente pueda mostrarla.
    observacion: str | None = None


class ModuloSalida(_BaseSalida):
    id: str
    nombre: str
    tipo_cultivo: str
    perfil_id: str
    # Nombre del perfil de referencia, resuelto por el servicio.
    #
    # Se incluye para que las pantallas puedan mostrar con qué rangos se evalúan
    # las lecturas del módulo sin tener que cruzar la lista de perfiles: la
    # pantalla de módulos ya lo hacía en el cliente, y el panel de inicio no
    # disponía de esa lista, de modo que no podía nombrar el perfil. El servicio
    # es quien conoce la relación, así que la resuelve él.
    perfil_nombre: str = ""
    ubicacion: str | None = None
    activo: bool = True


class PerfilSalida(_BaseSalida):
    id: str
    nombre: str
    descripcion: str | None = None
    predefinido: bool = False


class RangoSalida(_BaseSalida):
    id: str
    perfil_id: str
    variable: str
    minimo: float
    maximo: float
    unidad: str


class AlertaSalida(_BaseSalida):
    id: str
    lectura_id: str
    modulo_id: str
    variable: str
    valor: float
    rango_minimo: float
    rango_maximo: float
    estado: str
    timestamp: datetime
    observacion: str | None = None
    # Unidad de la variable y sentido de la desviación: el documento de la alerta
    # ya los guarda, y el cliente los presenta en la lista de alertas.
    unidad: str = ""
    desviacion: str | None = None


class ResumenVariable(_BaseSalida):
    variable: str
    unidad: str
    cantidad: int
    promedio: float
    maximo: float
    minimo: float


class UsuarioPerfilSalida(_BaseSalida):
    """Perfil de una cuenta del sistema.

    El identificador es el **uid** de Firebase Authentication: es el mismo valor
    con el que el servicio resuelve la autorización, de modo que la aplicación no
    necesita guardar por su cuenta la correspondencia entre la sesión y el perfil.

    Se usa tanto para el perfil propio —lo que devuelven `/usuarios/perfil`— como
    para las cuentas que consulta la administración.
    """

    id: str
    email: str = ""
    nombre: str = ""
    rol: str = ""
    activo: bool = True
    telefono: str | None = None
    cargo: str | None = None


class UsuarioAdministracionActualizacion(_BaseEntrada):
    """Cambios que la administración puede aplicar al perfil de una cuenta.

    Incluye el rol y el estado de activación, que **no** forman parte del esquema
    del perfil propio. Son dos esquemas distintos y no uno con campos opcionales
    para que el contrato impida por sí mismo la elevación de privilegios: quien
    quiera modificar su rol tiene que pasar por la operación de administración,
    que exige el rol correspondiente.
    """

    nombre: str | None = Field(default=None, min_length=2, max_length=60)
    telefono: str | None = Field(default=None, max_length=30)
    cargo: str | None = Field(default=None, max_length=60)
    rol: str | None = Field(default=None, min_length=2, max_length=20)
    activo: bool | None = None
