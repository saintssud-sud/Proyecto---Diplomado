"""Pruebas de la memoria intermedia de las consultas de lecturas (RNF-01).

Se comprueba lo que sostiene el requisito y lo que lo hace seguro: que la segunda
consulta igual no vuelva a la base, que la clave distinga cualquier cambio en los
parámetros, que registrar o eliminar una lectura descarte lo memorizado, que la
ventana venza y que un fallo de la memoria no tumbe la petición.
"""

import time
from datetime import datetime, timedelta, timezone

import pytest

from app.repositorios.base import RepositorioDatos
from app.repositorios.cache import RepositorioConCache, clave_consulta
from app.repositorios.memoria import RepositorioMemoria

from .conftest import cabecera_dispositivo

CONSULTA_BASE = {
    "modulo_id": "modulo-1",
    "variable": "ph",
    "desde": datetime(2026, 10, 1, tzinfo=timezone.utc),
    "hasta": datetime(2026, 10, 5, tzinfo=timezone.utc),
    "limite": 200,
}


class _Contador:
    """Repositorio que cuenta las consultas que llegan a la base.

    Es la forma de demostrar el efecto de la memoria sin cronómetro: si la
    segunda consulta igual no incrementa el contador, no se leyó la base.
    """

    def __init__(self, repositorio: RepositorioDatos) -> None:
        self._repositorio = repositorio
        self.consultas = 0

    def listar_lecturas(self, **parametros):
        self.consultas += 1
        return self._repositorio.listar_lecturas(**parametros)

    def __getattr__(self, nombre: str):
        if nombre.startswith("_"):
            raise AttributeError(nombre)
        return getattr(self._repositorio, nombre)


def _lectura(valor: float = 6.1) -> dict:
    return {"modulo_id": "modulo-1", "variable": "ph", "valor": valor, "unidad": ""}


def _con_lecturas(cantidad: int = 3) -> tuple[RepositorioMemoria, _Contador]:
    """Repositorio de memoria con lecturas ya guardadas y su contador de consultas."""
    base = RepositorioMemoria()
    for numero in range(cantidad):
        base.crear_lectura(_lectura(6.0 + numero / 10))
    return base, _Contador(base)


# ---------------------------------------------------------------------------
# La segunda consulta igual no vuelve a la base
# ---------------------------------------------------------------------------


def test_la_segunda_consulta_igual_no_vuelve_a_la_base():
    _, contador = _con_lecturas()
    repositorio = RepositorioConCache(contador)

    primera = repositorio.listar_lecturas(modulo_id="modulo-1", limite=10)
    segunda = repositorio.listar_lecturas(modulo_id="modulo-1", limite=10)

    assert contador.consultas == 1
    assert primera == segunda
    assert len(segunda) == 3


def test_una_consulta_con_otro_parametro_si_vuelve_a_la_base():
    _, contador = _con_lecturas()
    repositorio = RepositorioConCache(contador)

    repositorio.listar_lecturas(modulo_id="modulo-1", limite=10)
    repositorio.listar_lecturas(modulo_id="modulo-1", limite=5)

    # El límite forma parte de la clave: no puede servirse el resultado del otro.
    assert contador.consultas == 2


def test_lo_memorizado_no_se_altera_si_el_llamador_modifica_la_lista():
    _, contador = _con_lecturas()
    repositorio = RepositorioConCache(contador)

    devuelta = repositorio.listar_lecturas(limite=10)
    devuelta.append({"id": "inventado"})
    devuelta.clear()

    assert len(repositorio.listar_lecturas(limite=10)) == 3
    assert contador.consultas == 1


def test_la_memoria_es_de_cada_repositorio_y_no_del_modulo():
    _, contador_uno = _con_lecturas()
    _, contador_dos = _con_lecturas()
    uno = RepositorioConCache(contador_uno)
    dos = RepositorioConCache(contador_dos)

    uno.listar_lecturas(limite=10)
    dos.listar_lecturas(limite=10)

    assert (contador_uno.consultas, contador_dos.consultas) == (1, 1)


# ---------------------------------------------------------------------------
# La clave incluye todos los parámetros de la consulta
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "parametro, otro_valor",
    [
        ("modulo_id", "modulo-2"),
        ("modulo_id", None),
        ("variable", "ec"),
        ("variable", None),
        ("desde", datetime(2026, 10, 2, tzinfo=timezone.utc)),
        ("desde", None),
        ("hasta", datetime(2026, 10, 4, tzinfo=timezone.utc)),
        ("hasta", None),
        ("limite", 5),
        ("limite", 201),
    ],
)
def test_cambiar_un_parametro_produce_otra_clave(parametro, otro_valor):
    distinta = clave_consulta(**{**CONSULTA_BASE, parametro: otro_valor})

    assert distinta != clave_consulta(**CONSULTA_BASE)


def test_dos_instantes_iguales_con_distinto_uso_horario_comparten_clave():
    en_utc = datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc)
    en_hora_local = datetime(2026, 10, 5, 8, 0, tzinfo=timezone(timedelta(hours=-4)))

    assert clave_consulta("modulo-1", "ph", en_utc, None, 200) == clave_consulta(
        "modulo-1", "ph", en_hora_local, None, 200
    )


def test_la_clave_es_estable_entre_llamadas_iguales():
    assert clave_consulta(**CONSULTA_BASE) == clave_consulta(**CONSULTA_BASE)


# ---------------------------------------------------------------------------
# Registrar o eliminar una lectura descarta lo memorizado
# ---------------------------------------------------------------------------


def test_registrar_una_lectura_descarta_la_memoria():
    _, contador = _con_lecturas()
    repositorio = RepositorioConCache(contador)
    assert len(repositorio.listar_lecturas(limite=10)) == 3

    repositorio.crear_lectura(_lectura(6.4))

    lecturas = repositorio.listar_lecturas(limite=10)
    assert contador.consultas == 2
    assert len(lecturas) == 4


def test_anular_una_lectura_descarta_la_memoria():
    base, contador = _con_lecturas()
    repositorio = RepositorioConCache(contador)
    assert len(repositorio.listar_lecturas(limite=10)) == 3

    identificador = base.listar_lecturas(limite=10)[0]["id"]
    anulada = repositorio.anular_lectura(
        identificador, {"anulada": True, "motivo_anulacion": "prueba de anulación"}
    )
    assert anulada is not None and anulada["anulada"] is True

    # El dato no se pierde: sigue estando, marcado como anulado.
    assert any(lectura["id"] == identificador for lectura in repositorio.listar_lecturas(limite=10))
    # Y la memoria se descartó: la consulta siguiente vuelve a leer la base.
    assert contador.consultas == 2


def test_una_escritura_que_falla_no_descarta_lo_memorizado(monkeypatch):
    base, contador = _con_lecturas()
    repositorio = RepositorioConCache(contador)
    repositorio.listar_lecturas(limite=10)

    def _falla_la_escritura(_datos):
        raise RuntimeError("la base rechazó la escritura")

    monkeypatch.setattr(base, "crear_lectura", _falla_la_escritura)

    with pytest.raises(RuntimeError):
        repositorio.crear_lectura(_lectura(6.9))

    # La escritura no llegó a ocurrir, así que lo memorizado sigue siendo cierto.
    assert len(repositorio.listar_lecturas(limite=10)) == 3
    assert contador.consultas == 1


# ---------------------------------------------------------------------------
# El panel ve el dato recién registrado (a través de la API)
# ---------------------------------------------------------------------------


def test_el_panel_ve_la_lectura_del_dispositivo_recien_registrada(
    cliente_publico, cliente_operador, entorno
):
    # La primera consulta queda memorizada: un panel abierto antes del envío.
    assert cliente_operador.get("/api/v1/lecturas").json() == []

    respuesta = cliente_publico.post(
        "/api/v1/lecturas",
        json={"modulo_id": entorno.modulo_id, "variable": "ph", "valor": 6.1},
        headers=cabecera_dispositivo(),
    )
    assert respuesta.status_code == 201

    lecturas = cliente_operador.get("/api/v1/lecturas").json()
    assert len(lecturas) == 1
    assert lecturas[0]["id"] == respuesta.json()["id"]


def test_el_panel_ve_la_lectura_manual_recien_registrada(cliente_operador, entorno):
    assert cliente_operador.get("/api/v1/lecturas").json() == []

    respuesta = cliente_operador.post(
        "/api/v1/lecturas/manual",
        json={"modulo_id": entorno.modulo_id, "variable": "ph", "valor": 6.2},
    )
    assert respuesta.status_code == 201

    assert cliente_operador.get("/api/v1/lecturas").json()[0]["id"] == respuesta.json()["id"]


def test_la_segunda_consulta_igual_por_la_api_sale_de_la_memoria(cliente_operador, entorno):
    primera = cliente_operador.get("/api/v1/lecturas?limite=5").json()

    # Se escribe directamente en la base, sin pasar por el envoltorio: si la
    # segunda consulta volviera a la base, vería esta lectura.
    entorno.repositorio.crear_lectura(_lectura(6.7))

    segunda = cliente_operador.get("/api/v1/lecturas?limite=5").json()

    assert primera == []
    assert segunda == primera
    assert len(entorno.repositorio.listar_lecturas(limite=5)) == 1


# ---------------------------------------------------------------------------
# La ventana vence y la memoria se puede desactivar
# ---------------------------------------------------------------------------


def test_lo_memorizado_vence_al_terminar_la_ventana():
    _, contador = _con_lecturas()
    repositorio = RepositorioConCache(contador, segundos=0.05)

    repositorio.listar_lecturas(limite=10)
    time.sleep(0.08)
    repositorio.listar_lecturas(limite=10)

    assert contador.consultas == 2


def test_con_cero_segundos_la_memoria_queda_desactivada():
    _, contador = _con_lecturas()
    repositorio = RepositorioConCache(contador, segundos=0)

    repositorio.listar_lecturas(limite=10)
    repositorio.listar_lecturas(limite=10)

    # Es el modo con el que se mide el «antes» de optimizar.
    assert contador.consultas == 2
    assert repositorio.memoria.activa is False


def test_lo_vencido_no_se_acumula_en_la_memoria():
    _, contador = _con_lecturas(cantidad=1)
    repositorio = RepositorioConCache(contador, segundos=0.05)

    for limite in range(1, 6):
        repositorio.listar_lecturas(limite=limite)
        time.sleep(0.06)

    repositorio.listar_lecturas(limite=99)

    assert repositorio.memoria.tamano == 1


# ---------------------------------------------------------------------------
# Un fallo de la memoria no puede tumbar la petición
# ---------------------------------------------------------------------------


def _falla(*_argumentos, **_opciones):
    raise RuntimeError("memoria no disponible")


def test_un_fallo_de_la_memoria_al_consultar_devuelve_el_dato_de_la_base(monkeypatch):
    _, contador = _con_lecturas()
    repositorio = RepositorioConCache(contador)
    monkeypatch.setattr(repositorio.memoria, "obtener", _falla)
    monkeypatch.setattr(repositorio.memoria, "guardar", _falla)

    assert len(repositorio.listar_lecturas(limite=10)) == 3
    assert contador.consultas == 1


def test_un_fallo_de_la_memoria_al_descartar_obliga_a_consultar_la_base(monkeypatch):
    _, contador = _con_lecturas()
    repositorio = RepositorioConCache(contador)
    assert len(repositorio.listar_lecturas(limite=10)) == 3

    monkeypatch.setattr(repositorio.memoria, "descartar", _falla)

    lectura = repositorio.crear_lectura(_lectura(6.5))
    assert lectura["id"]

    # No se pudo descartar lo memorizado, así que la memoria queda fuera de
    # servicio y la consulta siguiente lee la base: se ve la lectura nueva.
    assert len(repositorio.listar_lecturas(limite=10)) == 4
    assert contador.consultas == 2


# ---------------------------------------------------------------------------
# El envoltorio es un repositorio más
# ---------------------------------------------------------------------------


def test_el_envoltorio_cumple_la_interfaz_de_repositorio():
    repositorio = RepositorioConCache(RepositorioMemoria())

    assert isinstance(repositorio, RepositorioDatos)

    # El resto de las colecciones atraviesa el envoltorio sin tocarse.
    perfil = repositorio.crear_perfil({"nombre": "Lechuga"})
    assert repositorio.obtener_perfil(perfil["id"])["nombre"] == "Lechuga"
    modulo = repositorio.crear_modulo({"nombre": "Módulo 1", "activo": True})
    assert [modulo["id"]] == [item["id"] for item in repositorio.listar_modulos()]
    assert repositorio.verificar_conexion() is True


def test_el_envoltorio_no_inventa_operaciones_que_no_existen():
    repositorio = RepositorioConCache(RepositorioMemoria())

    with pytest.raises(AttributeError):
        repositorio._no_existe
    with pytest.raises(AttributeError):
        repositorio.no_existe


def test_la_memoria_se_resuelve_por_defecto_con_la_ventana_configurada():
    repositorio = RepositorioConCache(RepositorioMemoria())

    assert repositorio.memoria.activa is True
