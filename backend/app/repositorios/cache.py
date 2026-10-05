"""Memoria intermedia (caché) de las consultas de lecturas.

Por qué existe
--------------
La medición del **RNF-01** del 5 de octubre de 2026 dejó el incumplimiento por
escrito: con 200 registros en una sola consulta, la mediana fue de 878 ms y el
percentil 95 de 1.461 ms, contra un objetivo de 800 ms. El costo no estaba en el
filtrado —el repositorio ya empuja todos los filtros a Firestore y usa el índice
compuesto—, sino en leer y serializar muchos documentos en **cada** petición, y
el panel repite la misma consulta cada pocos segundos.

Qué hace
--------
Guarda el resultado de `listar_lecturas` durante unos segundos y lo devuelve tal
cual cuando vuelve a pedirse la misma consulta. La ventana es corta y se ajusta
con `SEGUNDOS_CACHE_LECTURAS` (diez segundos por omisión): el módulo de
adquisición publica cada cinco minutos y medio, de modo que diez segundos de
antigüedad no sacrifican frescura.

Cómo se mantiene veraz
----------------------
· La clave de la memoria incluye **todos** los parámetros de la consulta (módulo,
  variable, fechas y límite): dos consultas que difieran en cualquiera de ellos no
  comparten resultado.
· Al registrar o eliminar una lectura se descarta lo memorizado, de modo que el
  panel muestre el dato recién registrado y no uno viejo.
· Ninguna operación de la memoria puede tumbar una petición: si algo falla se deja
  constancia en el registro y se consulta la base como antes de que existiera.
"""

import logging
from datetime import datetime, timezone
from threading import Lock
from time import monotonic
from typing import Any

from .base import RepositorioDatos

# Diez segundos: suficiente para absorber la ráfaga de consultas iguales que el
# panel repite al abrir el historial, y muy por debajo del intervalo con que el
# módulo de adquisición publica lecturas nuevas.
SEGUNDOS_POR_OMISION = 10.0

ClaveConsulta = tuple[str, str, str, str, int]


def _texto_fecha(valor: datetime | None) -> str:
    """Fecha de la consulta en texto y en UTC, para que forme parte de la clave.

    Se normaliza a UTC a propósito: el mismo instante expresado con otro uso
    horario —o sin uso horario— tiene que producir la misma clave, porque la base
    devolvería el mismo resultado.
    """
    if valor is None:
        return ""
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc).isoformat()


def clave_consulta(
    modulo_id: str | None = None,
    variable: str | None = None,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    limite: int = 500,
) -> ClaveConsulta:
    """Clave de la memoria: los cinco parámetros que definen una consulta.

    Es una función aparte para poder comprobarla en las pruebas: si algún
    parámetro quedara fuera de la clave, dos consultas distintas compartirían
    resultado y el servicio devolvería datos de otra consulta.
    """
    return (modulo_id or "", variable or "", _texto_fecha(desde), _texto_fecha(hasta), int(limite))


class MemoriaLecturas:
    """Memoria intermedia de las consultas de lecturas, con vencimiento por tiempo."""

    def __init__(self, segundos: float = SEGUNDOS_POR_OMISION) -> None:
        self._segundos = max(0.0, float(segundos))
        self._entradas: dict[ClaveConsulta, tuple[float, list[dict[str, Any]]]] = {}
        self._cerrojo = Lock()

    @property
    def activa(self) -> bool:
        """Con cero segundos la memoria queda desactivada y todo va a la base."""
        return self._segundos > 0

    @property
    def tamano(self) -> int:
        """Cuántas consultas hay memorizadas ahora mismo; se expone para las pruebas."""
        with self._cerrojo:
            return len(self._entradas)

    def obtener(self, clave: ClaveConsulta) -> list[dict[str, Any]] | None:
        """Devuelve lo memorizado para esa consulta, o None si no hay nada vigente."""
        if not self.activa:
            return None
        momento = monotonic()
        with self._cerrojo:
            entrada = self._entradas.get(clave)
            if entrada is None:
                return None
            vence_en, valor = entrada
            if vence_en <= momento:
                self._entradas.pop(clave, None)
                return None
            # Se entrega una copia de la lista: quien la reciba puede ordenarla o
            # recortarla sin alterar lo que hay memorizado.
            return list(valor)

    def guardar(self, clave: ClaveConsulta, valor: list[dict[str, Any]]) -> None:
        """Memoriza el resultado de una consulta durante la ventana configurada."""
        if not self.activa:
            return
        momento = monotonic()
        with self._cerrojo:
            # Se aprovecha para descartar lo vencido: así la memoria no crece con
            # una entrada por cada combinación de filtros que se haya consultado.
            vencidas = [
                clave_vieja
                for clave_vieja, (vence_en, _) in self._entradas.items()
                if vence_en <= momento
            ]
            for clave_vieja in vencidas:
                self._entradas.pop(clave_vieja, None)
            self._entradas[clave] = (momento + self._segundos, valor)

    def descartar(self) -> int:
        """Descarta todo lo memorizado de la colección; devuelve cuántas consultas había.

        Se llama al registrar o eliminar una lectura: a partir de ahí cualquier
        consulta memorizada puede estar diciendo algo que ya no es cierto.
        """
        with self._cerrojo:
            cuantas = len(self._entradas)
            self._entradas.clear()
            return cuantas


class RepositorioConCache:
    """Repositorio que memoriza las consultas de lecturas de otro repositorio.

    Se envuelve el repositorio de datos en lugar de repetir la memoria dentro de
    cada implementación: así la memoria vale igual sobre Cloud Firestore —el
    servicio desplegado— y sobre el repositorio en memoria que usan las pruebas y
    el modo de demostración.

    La memoria es de **esta instancia** y no del módulo: dos repositorios —por
    ejemplo, el de dos pruebas— no comparten resultados.

    La interfaz completa se escribe aquí, como en las otras dos implementaciones, en
    lugar de delegarla con `__getattr__`: `isinstance` contra la interfaz de
    `repositorios.base` —y el verificador de tipos— no ven lo que se resuelve por
    esa vía, y este envoltorio tiene que poder usarse en cualquier lugar donde se
    espere un repositorio.
    """

    def __init__(
        self, repositorio: RepositorioDatos, segundos: float = SEGUNDOS_POR_OMISION
    ) -> None:
        self._repositorio = repositorio
        self._memoria = MemoriaLecturas(segundos)
        # Queda en falso si la memoria no se pudo descartar tras una escritura: a
        # partir de ahí lo memorizado puede no ser cierto y se va siempre a la
        # base, que es el camino de antes de que la memoria existiera.
        self._memoria_util = True

    @property
    def memoria(self) -> MemoriaLecturas:
        """La memoria de esta instancia; se expone para poder comprobarla en las pruebas."""
        return self._memoria

    # --- Lecturas (lo único que se memoriza) --------------------------------
    def listar_lecturas(
        self,
        modulo_id: str | None = None,
        variable: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limite: int = 500,
    ) -> list[dict[str, Any]]:
        if not self._memoria_util:
            return self._consultar_la_base(modulo_id, variable, desde, hasta, limite)

        clave = clave_consulta(modulo_id, variable, desde, hasta, limite)

        try:
            memorizado = self._memoria.obtener(clave)
        except Exception as error:  # noqa: BLE001 - la memoria no puede tumbar la consulta
            memorizado = None
            self._avisar("consultar", error)
        if memorizado is not None:
            self._anotar(acierto=True)
            return memorizado

        lecturas = self._consultar_la_base(modulo_id, variable, desde, hasta, limite)
        try:
            self._memoria.guardar(clave, lecturas)
        except Exception as error:  # noqa: BLE001 - igual que arriba: la consulta ya está hecha
            self._avisar("guardar", error)
        self._anotar(acierto=False)
        # Se devuelve una copia, igual que cuando el dato sale de la memoria: la
        # lista que queda guardada no puede salir de aquí, porque quien la reciba
        # puede ordenarla o recortarla y alteraría lo memorizado.
        return list(lecturas)

    def crear_lectura(self, datos: dict[str, Any]) -> dict[str, Any]:
        lectura = self._repositorio.crear_lectura(datos)
        # Después de escribir, y no antes: si la escritura falla, lo memorizado
        # sigue siendo cierto y no se paga el costo de volver a leer la base.
        self._descartar()
        return lectura

    def eliminar_lectura(self, lectura_id: str) -> bool:
        eliminada = self._repositorio.eliminar_lectura(lectura_id)
        self._descartar()
        return eliminada

    def obtener_lectura(self, lectura_id: str) -> dict[str, Any] | None:
        return self._repositorio.obtener_lectura(lectura_id)

    # --- Módulos de cultivo -------------------------------------------------
    def crear_modulo(self, datos: dict[str, Any]) -> dict[str, Any]:
        return self._repositorio.crear_modulo(datos)

    def obtener_modulo(self, modulo_id: str) -> dict[str, Any] | None:
        return self._repositorio.obtener_modulo(modulo_id)

    def listar_modulos(self, activo: bool | None = None) -> list[dict[str, Any]]:
        return self._repositorio.listar_modulos(activo)

    def actualizar_modulo(self, modulo_id: str, cambios: dict[str, Any]) -> dict[str, Any] | None:
        return self._repositorio.actualizar_modulo(modulo_id, cambios)

    def eliminar_modulo(self, modulo_id: str) -> bool:
        return self._repositorio.eliminar_modulo(modulo_id)

    # --- Perfiles de cultivo ------------------------------------------------
    def crear_perfil(self, datos: dict[str, Any]) -> dict[str, Any]:
        return self._repositorio.crear_perfil(datos)

    def obtener_perfil(self, perfil_id: str) -> dict[str, Any] | None:
        return self._repositorio.obtener_perfil(perfil_id)

    def listar_perfiles(self) -> list[dict[str, Any]]:
        return self._repositorio.listar_perfiles()

    def eliminar_perfil(self, perfil_id: str) -> bool:
        return self._repositorio.eliminar_perfil(perfil_id)

    # --- Rangos de referencia ----------------------------------------------
    def crear_rango(self, datos: dict[str, Any]) -> dict[str, Any]:
        return self._repositorio.crear_rango(datos)

    def obtener_rango(self, rango_id: str) -> dict[str, Any] | None:
        return self._repositorio.obtener_rango(rango_id)

    def buscar_rango(self, perfil_id: str, variable: str) -> dict[str, Any] | None:
        return self._repositorio.buscar_rango(perfil_id, variable)

    def listar_rangos(self, perfil_id: str | None = None) -> list[dict[str, Any]]:
        return self._repositorio.listar_rangos(perfil_id)

    def actualizar_rango(self, rango_id: str, cambios: dict[str, Any]) -> dict[str, Any] | None:
        return self._repositorio.actualizar_rango(rango_id, cambios)

    def eliminar_rango(self, rango_id: str) -> bool:
        return self._repositorio.eliminar_rango(rango_id)

    # --- Alertas ------------------------------------------------------------
    def crear_alerta(self, datos: dict[str, Any]) -> dict[str, Any]:
        return self._repositorio.crear_alerta(datos)

    def obtener_alerta(self, alerta_id: str) -> dict[str, Any] | None:
        return self._repositorio.obtener_alerta(alerta_id)

    def listar_alertas(
        self,
        estado: str | None = None,
        modulo_id: str | None = None,
        limite: int = 200,
    ) -> list[dict[str, Any]]:
        return self._repositorio.listar_alertas(estado, modulo_id, limite)

    def actualizar_alerta(self, alerta_id: str, cambios: dict[str, Any]) -> dict[str, Any] | None:
        return self._repositorio.actualizar_alerta(alerta_id, cambios)

    def eliminar_alerta(self, alerta_id: str) -> bool:
        return self._repositorio.eliminar_alerta(alerta_id)

    # --- Usuarios -----------------------------------------------------------
    def obtener_perfil_usuario(self, uid: str) -> dict[str, Any] | None:
        return self._repositorio.obtener_perfil_usuario(uid)

    def listar_perfiles_usuario(self) -> list[dict[str, Any]]:
        return self._repositorio.listar_perfiles_usuario()

    def actualizar_perfil_usuario(
        self, uid: str, cambios: dict[str, Any]
    ) -> dict[str, Any] | None:
        return self._repositorio.actualizar_perfil_usuario(uid, cambios)

    def eliminar_perfil_usuario(self, uid: str) -> bool:
        return self._repositorio.eliminar_perfil_usuario(uid)

    # --- Diagnóstico --------------------------------------------------------
    def verificar_conexion(self) -> bool:
        return self._repositorio.verificar_conexion()

    # --- Utilidades internas ------------------------------------------------
    def _consultar_la_base(
        self,
        modulo_id: str | None,
        variable: str | None,
        desde: datetime | None,
        hasta: datetime | None,
        limite: int,
    ) -> list[dict[str, Any]]:
        """Consulta el repositorio envuelto: es el camino de siempre, sin memoria."""
        return self._repositorio.listar_lecturas(
            modulo_id=modulo_id,
            variable=variable,
            desde=desde,
            hasta=hasta,
            limite=limite,
        )

    def _descartar(self) -> None:
        try:
            self._memoria.descartar()
        except Exception as error:  # noqa: BLE001 - la lectura nueva ya quedó registrada
            # Descartar es lo que mantiene veraz a la memoria: si no se pudo, se
            # deja fuera de servicio. La corrección manda sobre el rendimiento.
            self._memoria_util = False
            self._avisar("descartar", error)

    @staticmethod
    def _anotar(acierto: bool) -> None:
        """Deja constancia de si la consulta salió de la memoria o de la base.

        Sin esta línea, una consulta lenta no se puede atribuir: la respuesta es
        la misma por los dos caminos y solo se distinguen midiendo. Va en nivel de
        depuración porque la línea de operación es la del middleware —una por
        petición—, y esta solo hace falta al analizar el rendimiento.
        """
        logging.getLogger("sigvach").debug(
            "memoria de lecturas: %s", "acierto" if acierto else "fallo (se consulto la base)"
        )

    @staticmethod
    def _avisar(operacion: str, error: Exception) -> None:
        # Sin tildes, como el resto de las líneas de registro del servicio: el
        # registro se lee en canalizaciones y en la consola de la plataforma.
        logging.getLogger("sigvach").warning(
            "La memoria de lecturas fallo al %s y se consulto la base: %s: %s",
            operacion,
            type(error).__name__,
            error,
        )
