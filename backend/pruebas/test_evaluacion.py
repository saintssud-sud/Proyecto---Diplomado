"""Pruebas de las reglas de negocio del dominio (funciones puras)."""

from datetime import datetime, timezone

from app.servicios import evaluacion


def test_lectura_dentro_del_rango():
    assert evaluacion.evaluar_lectura(6.0, 5.5, 6.5) == evaluacion.ESTADO_DENTRO


def test_lectura_por_debajo_del_minimo():
    assert evaluacion.evaluar_lectura(5.4, 5.5, 6.5) == evaluacion.ESTADO_BAJO


def test_lectura_por_encima_del_maximo():
    assert evaluacion.evaluar_lectura(6.6, 5.5, 6.5) == evaluacion.ESTADO_ALTO


def test_lectura_en_el_limite_exacto_se_considera_dentro():
    assert evaluacion.evaluar_lectura(5.5, 5.5, 6.5) == evaluacion.ESTADO_DENTRO
    assert evaluacion.evaluar_lectura(6.5, 5.5, 6.5) == evaluacion.ESTADO_DENTRO


def test_sin_rango_configurado_no_hay_estado_fuera_de_rango():
    estado = evaluacion.evaluar_lectura(11.2, None, None)
    assert estado == evaluacion.ESTADO_SIN_RANGO
    assert evaluacion.requiere_alerta(estado) is False


def test_solo_los_valores_fuera_de_rango_generan_alerta():
    assert evaluacion.requiere_alerta(evaluacion.ESTADO_BAJO) is True
    assert evaluacion.requiere_alerta(evaluacion.ESTADO_ALTO) is True
    assert evaluacion.requiere_alerta(evaluacion.ESTADO_DENTRO) is False
    assert evaluacion.requiere_alerta(evaluacion.ESTADO_SIN_RANGO) is False


def test_la_alerta_conserva_la_referencia_a_la_lectura():
    lectura = {
        "id": "L-1",
        "modulo_id": "M-1",
        "variable": "ph",
        "valor": 7.4,
        "unidad": "",
        "timestamp": datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc),
    }
    rango = {"minimo": 5.5, "maximo": 6.5}
    alerta = evaluacion.construir_alerta(lectura, rango, evaluacion.ESTADO_ALTO)
    assert alerta["lectura_id"] == "L-1"
    assert alerta["modulo_id"] == "M-1"
    assert alerta["estado"] == "activa"
    assert alerta["desviacion"] == evaluacion.ESTADO_ALTO
    assert alerta["rango_maximo"] == 6.5


def test_resumen_de_serie_vacia():
    assert evaluacion.resumen_serie([]) is None


def test_resumen_calcula_promedio_maximo_y_minimo():
    resumen = evaluacion.resumen_serie([6.0, 6.6, 5.4, 6.0])
    assert resumen["cantidad"] == 4
    assert resumen["promedio"] == 6.0
    assert resumen["maximo"] == 6.6
    assert resumen["minimo"] == 5.4


def test_csv_incluye_encabezados_y_escapa_campos_con_coma():
    lecturas = [
        {
            "id": "L-1",
            "modulo_id": "M-1",
            "variable": "ph",
            "valor": 6.1,
            "unidad": "",
            "origen": "automatico",
            "timestamp": datetime(2026, 9, 14, 10, 0, tzinfo=timezone.utc),
        },
        {
            "id": "L-2",
            "modulo_id": "M-1",
            "variable": "temp_solucion",
            "valor": 21.5,
            "unidad": "°C",
            "origen": "manual",
            "observacion": "medición con termómetro, inicio de ciclo",
            "timestamp": datetime(2026, 9, 14, 10, 5, tzinfo=timezone.utc),
        },
    ]
    contenido = evaluacion.generar_csv(lecturas)
    lineas = contenido.strip().splitlines()
    assert lineas[0].startswith("id,modulo_id,variable,valor,unidad,origen,timestamp")
    assert "L-1" in lineas[1]
    assert contenido.endswith("\r\n")


def test_csv_no_incluye_campos_ajenos_a_lo_consultado():
    contenido = evaluacion.generar_csv([])
    assert contenido.strip() == "id,modulo_id,variable,valor,unidad,origen,timestamp"
