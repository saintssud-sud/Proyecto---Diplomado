"""Pruebas de la validación de datos de entrada (requisito mínimo 8).

Se comprueba en los dos niveles: el esquema rechaza lo que no cumple el
contrato y la API responde con el código 422 y el detalle del campo rechazado.
"""

import pytest
from pydantic import ValidationError

from app.esquemas import LecturaEntrada, LecturaManualEntrada, RangoEntrada

from .conftest import cabecera_dispositivo


# ---------------------------------------------------------------------------
# Validación en el esquema
# ---------------------------------------------------------------------------


def test_lectura_valida_se_acepta():
    lectura = LecturaEntrada(modulo_id="M-1", variable="pH", valor=6.1)
    assert lectura.variable == "ph"
    assert lectura.origen == "automatico"


def test_variable_fuera_del_catalogo_se_rechaza():
    with pytest.raises(ValidationError) as fallo:
        LecturaEntrada(modulo_id="M-1", variable="oxigeno", valor=6.1)
    assert "variable desconocida" in str(fallo.value)


def test_valor_fuera_del_rango_fisico_se_rechaza():
    with pytest.raises(ValidationError) as fallo:
        LecturaEntrada(modulo_id="M-1", variable="ph", valor=15.2)
    assert "debe estar entre" in str(fallo.value)


def test_humedad_mayor_a_cien_se_rechaza():
    with pytest.raises(ValidationError):
        LecturaEntrada(modulo_id="M-1", variable="humedad", valor=120)


def test_unidad_incoherente_se_rechaza():
    with pytest.raises(ValidationError) as fallo:
        LecturaEntrada(modulo_id="M-1", variable="temp_solucion", valor=21.0, unidad="ppm")
    assert "la unidad de temp_solucion" in str(fallo.value)


def test_marca_de_tiempo_en_el_futuro_se_rechaza():
    with pytest.raises(ValidationError) as fallo:
        LecturaEntrada(
            modulo_id="M-1",
            variable="ph",
            valor=6.1,
            timestamp="2030-01-01T00:00:00Z",
        )
    assert "no puede estar en el futuro" in str(fallo.value)


def test_campo_no_declarado_en_el_contrato_se_rechaza():
    with pytest.raises(ValidationError):
        LecturaEntrada(modulo_id="M-1", variable="ph", valor=6.1, rol="admin")


def test_la_lectura_manual_no_admite_declarar_su_origen():
    """El origen lo fija el servidor: el cliente no puede declararse automático."""
    with pytest.raises(ValidationError):
        LecturaManualEntrada(modulo_id="M-1", variable="ph", valor=6.1, origen="automatico")


def test_rango_con_minimo_mayor_o_igual_al_maximo_se_rechaza():
    with pytest.raises(ValidationError) as fallo:
        RangoEntrada(perfil_id="P-1", variable="ph", minimo=6.5, maximo=5.5)
    assert "menor que el máximo" in str(fallo.value)


def test_rango_fuera_del_limite_fisico_se_rechaza():
    with pytest.raises(ValidationError):
        RangoEntrada(perfil_id="P-1", variable="humedad", minimo=40, maximo=150)


# ---------------------------------------------------------------------------
# Validación a través de la API
# ---------------------------------------------------------------------------


def test_la_api_responde_422_con_el_detalle_del_campo(cliente_publico, entorno):
    respuesta = cliente_publico.post(
        "/api/v1/lecturas",
        json={"modulo_id": entorno.modulo_id, "variable": "ph", "valor": 99},
        headers=cabecera_dispositivo(),
    )
    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert cuerpo["codigo"] == "validacion_rechazada"
    assert "valor" in cuerpo["detalle"]["campos"]
    assert "debe estar entre" in cuerpo["detalle"]["campos"]["valor"]


def test_la_api_rechaza_una_variable_desconocida(cliente_publico, entorno):
    respuesta = cliente_publico.post(
        "/api/v1/lecturas",
        json={"modulo_id": entorno.modulo_id, "variable": "oxigeno", "valor": 6.1},
        headers=cabecera_dispositivo(),
    )
    assert respuesta.status_code == 422
    assert "variable" in respuesta.json()["detalle"]["campos"]


def test_la_api_rechaza_un_campo_ajeno_al_contrato(cliente_publico, entorno):
    respuesta = cliente_publico.post(
        "/api/v1/lecturas",
        json={
            "modulo_id": entorno.modulo_id,
            "variable": "ph",
            "valor": 6.1,
            "es_administrador": True,
        },
        headers=cabecera_dispositivo(),
    )
    assert respuesta.status_code == 422
