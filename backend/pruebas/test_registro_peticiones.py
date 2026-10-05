"""Pruebas del registro de una línea por petición.

El requisito es de operación, y estas pruebas lo comprueban tal como lo pide la
cátedra: **una** línea por petición, con método, ruta, código y duración; sin
credenciales, sin cuerpos y sin la cadena de consulta; y sin que el registro
pueda tumbar una petición.
"""

import logging

from app import registro_peticiones
from app.registro_peticiones import _ruta_declarada

from .conftest import UID_ADMINISTRADOR, cabecera


def _lineas(caplog) -> list[str]:
    """Devuelve solo las líneas que escribió el middleware de registro."""
    return [
        registro.getMessage()
        for registro in caplog.records
        if registro.name == "sigvach"
        and registro.getMessage().startswith("peticion ")
    ]


def _preparar(caplog) -> None:
    """Deja el registro capturando lo que escriba la aplicación."""
    caplog.set_level(logging.INFO, logger="sigvach")


# ---------------------------------------------------------------------------
# Una línea por petición, con los cuatro datos
# ---------------------------------------------------------------------------


def test_cada_peticion_deja_una_linea_con_los_cuatro_datos(cliente_publico, caplog):
    _preparar(caplog)

    assert cliente_publico.get("/api/v1/salud").status_code == 200
    assert cliente_publico.get("/api/v1/salud").status_code == 200

    lineas = _lineas(caplog)
    assert len(lineas) == 2, "se esperaba una línea por petición: %r" % (lineas,)
    assert lineas[0].startswith("peticion metodo=GET ruta=/api/v1/salud codigo=200 duracion_ms=")
    assert lineas[1].startswith("peticion metodo=GET ruta=/api/v1/salud codigo=200 duracion_ms=")


def test_la_duracion_se_informa_en_milisegundos(cliente_publico, caplog):
    _preparar(caplog)

    cliente_publico.get("/api/v1/salud")

    linea = _lineas(caplog)[0]
    duracion = float(linea.rsplit("duracion_ms=", 1)[1])
    assert duracion >= 0.0
    # Una petición atendida por el repositorio en memoria tarda milisegundos, no
    # segundos: si el valor viniera en segundos el número sería del orden de 0,01.
    assert duracion < 1000.0


def test_se_registra_el_metodo_de_la_peticion(cliente_operador, entorno, caplog):
    _preparar(caplog)

    cliente_operador.post(
        "/api/v1/lecturas/manual",
        json={"modulo_id": entorno.modulo_id, "variable": "ph", "valor": 6.0},
        headers=cabecera("operador"),
    )

    linea = _lineas(caplog)[0]
    assert "metodo=POST" in linea
    assert "codigo=201" in linea


# ---------------------------------------------------------------------------
# La ruta se registra declarada, sin los identificadores
# ---------------------------------------------------------------------------


def test_la_ruta_no_lleva_el_identificador_del_recurso(cliente_operador, entorno, caplog):
    _preparar(caplog)

    cliente_operador.get("/api/v1/modulos/%s" % entorno.modulo_id)

    linea = _lineas(caplog)[0]
    assert "ruta=/api/v1/modulos/{modulo_id}" in linea
    assert entorno.modulo_id not in linea


def test_la_ruta_de_la_cuenta_no_lleva_el_identificador_de_la_persona(
    cliente_administrador, caplog
):
    _preparar(caplog)

    cliente_administrador.get("/api/v1/usuarios/%s" % UID_ADMINISTRADOR)

    linea = _lineas(caplog)[0]
    assert "ruta=/api/v1/usuarios/{uid}" in linea
    assert UID_ADMINISTRADOR not in linea


def test_la_ruta_declarada_cambia_los_identificadores_por_su_nombre():
    alcance = {
        "path": "/api/v1/modulos/M-1/lecturas/L-9",
        "path_params": {"modulo_id": "M-1", "lectura_id": "L-9"},
    }
    assert _ruta_declarada(alcance) == "/api/v1/modulos/{modulo_id}/lecturas/{lectura_id}"


def test_una_ruta_sin_coincidencia_se_registra_tal_como_llego():
    # Sin parámetros capturados —un 404, por ejemplo— no hay identificador que
    # ocultar y la ruta es el dato que dice qué se pidió.
    assert _ruta_declarada({"path": "/api/v1/no-existe"}) == "/api/v1/no-existe"


# ---------------------------------------------------------------------------
# Nada de datos sensibles
# ---------------------------------------------------------------------------


def test_no_se_registran_credenciales_ni_la_cadena_de_consulta(cliente_administrador, caplog):
    _preparar(caplog)

    cliente_administrador.get(
        "/api/v1/lecturas?variable=ph&desde=2026-01-01T00:00:00Z&limite=5",
        headers={"Authorization": "Bearer token-que-no-debe-quedar-registrado"},
    )

    texto = " ".join(_lineas(caplog))
    assert texto, "la petición tenía que dejar su línea"
    for dato in (
        "token-que-no-debe-quedar-registrado",
        "Authorization",
        "Bearer",
        "variable=ph",
        "desde=",
        "limite=5",
        "?",
    ):
        assert dato not in texto, "el registro no debe contener %r: %s" % (dato, texto)


def test_no_se_registra_el_cuerpo_de_la_peticion(cliente_operador, entorno, caplog):
    _preparar(caplog)

    cliente_operador.post(
        "/api/v1/lecturas/manual",
        json={
            "modulo_id": entorno.modulo_id,
            "variable": "ph",
            "valor": 6.0,
            "observacion": "texto-escrito-por-una-persona",
        },
        headers=cabecera("operador"),
    )

    texto = " ".join(_lineas(caplog))
    assert "texto-escrito-por-una-persona" not in texto


# ---------------------------------------------------------------------------
# El registro nunca rompe una petición
# ---------------------------------------------------------------------------


def test_un_fallo_del_registro_no_rompe_la_peticion(cliente_publico, monkeypatch):
    class RegistradorQueFalla:
        """Registrador que falla en todo lo que se le pide."""

        def info(self, *_, **__):
            raise RuntimeError("el registro no está disponible")

        def warning(self, *_, **__):
            raise RuntimeError("el registro no está disponible")

    monkeypatch.setattr(registro_peticiones, "REGISTRADOR", RegistradorQueFalla())

    respuesta = cliente_publico.get("/api/v1/salud")

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"


def test_un_fallo_del_registro_no_oculta_el_error_de_la_peticion(cliente_publico, monkeypatch):
    class RegistradorQueFalla:
        def info(self, *_, **__):
            raise RuntimeError("el registro no está disponible")

    monkeypatch.setattr(registro_peticiones, "REGISTRADOR", RegistradorQueFalla())

    respuesta = cliente_publico.get("/api/v1/modulos")

    # La petición sin identidad falla por autorización, no por el registro.
    assert respuesta.status_code == 401
    assert respuesta.json()["codigo"] == "no_autenticado"


# ---------------------------------------------------------------------------
# También se registra lo que sale mal
# ---------------------------------------------------------------------------


def test_la_peticion_sin_ruta_deja_su_linea_con_el_404(cliente_publico, caplog):
    _preparar(caplog)

    assert cliente_publico.get("/api/v1/no-existe").status_code == 404

    linea = _lineas(caplog)[0]
    assert "codigo=404" in linea
    assert "ruta=/api/v1/no-existe" in linea


def test_la_peticion_rechazada_deja_su_linea_con_el_codigo_del_rechazo(
    cliente_publico, entorno, caplog
):
    _preparar(caplog)

    # Sin clave de dispositivo: el servicio responde 401 y la línea lo refleja.
    respuesta = cliente_publico.post(
        "/api/v1/lecturas",
        json={"modulo_id": entorno.modulo_id, "variable": "ph", "valor": 6.1},
    )
    assert respuesta.status_code == 401

    assert "codigo=401" in _lineas(caplog)[0]
