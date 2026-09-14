"""Pruebas del contrato de lecturas: recepción, evaluación, alertas y consulta."""

from .conftest import CLAVE_DISPOSITIVO, cabecera_dispositivo


def _lectura(entorno, valor: float, variable: str = "ph") -> dict:
    return {"modulo_id": entorno.modulo_id, "variable": variable, "valor": valor}


# ---------------------------------------------------------------------------
# Recepción desde el módulo de adquisición
# ---------------------------------------------------------------------------


def test_lectura_valida_se_almacena_con_su_estado(cliente_publico, entorno):
    respuesta = cliente_publico.post(
        "/api/v1/lecturas", json=_lectura(entorno, 6.1), headers=cabecera_dispositivo()
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["variable"] == "ph"
    assert cuerpo["estado_rango"] == "dentro"
    assert cuerpo["origen"] == "automatico"
    # La unidad se hereda del catálogo, no se toma del cliente.
    assert cuerpo["unidad"] == ""
    assert cuerpo["id"]


def test_sin_clave_de_dispositivo_se_responde_401(cliente_publico, entorno):
    respuesta = cliente_publico.post("/api/v1/lecturas", json=_lectura(entorno, 6.1))
    assert respuesta.status_code == 401
    assert respuesta.json()["codigo"] == "no_autenticado"
    assert entorno.repositorio.listar_lecturas() == []


def test_con_clave_de_dispositivo_invalida_se_responde_401(cliente_publico, entorno):
    respuesta = cliente_publico.post(
        "/api/v1/lecturas",
        json=_lectura(entorno, 6.1),
        headers=cabecera_dispositivo("clave-equivocada"),
    )
    assert respuesta.status_code == 401
    assert entorno.repositorio.listar_lecturas() == []


def test_lectura_a_un_modulo_inexistente_se_responde_404(cliente_publico):
    respuesta = cliente_publico.post(
        "/api/v1/lecturas",
        json={"modulo_id": "M-inexistente", "variable": "ph", "valor": 6.1},
        headers=cabecera_dispositivo(),
    )
    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "no_encontrado"


def test_lectura_a_un_modulo_inactivo_se_responde_409(cliente_publico, entorno):
    respuesta = cliente_publico.post(
        "/api/v1/lecturas",
        json={"modulo_id": entorno.modulo_inactivo_id, "variable": "ph", "valor": 6.1},
        headers=cabecera_dispositivo(),
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "conflicto"


# ---------------------------------------------------------------------------
# Evaluación contra el rango y generación de alertas
# ---------------------------------------------------------------------------


def test_lectura_fuera_de_rango_genera_una_alerta(cliente_publico, cliente_operador, entorno):
    respuesta = cliente_publico.post(
        "/api/v1/lecturas", json=_lectura(entorno, 7.4), headers=cabecera_dispositivo()
    )
    assert respuesta.status_code == 201
    lectura = respuesta.json()
    assert lectura["estado_rango"] == "alto"

    alertas = cliente_operador.get("/api/v1/alertas", params={"estado": "activa"}).json()
    assert len(alertas) == 1
    assert alertas[0]["lectura_id"] == lectura["id"]
    assert alertas[0]["rango_maximo"] == 6.5


def test_lectura_dentro_de_rango_no_genera_alerta(cliente_publico, cliente_operador, entorno):
    cliente_publico.post(
        "/api/v1/lecturas", json=_lectura(entorno, 6.0), headers=cabecera_dispositivo()
    )
    assert cliente_operador.get("/api/v1/alertas").json() == []


def test_variable_sin_rango_configurado_no_genera_alerta(cliente_publico, entorno):
    respuesta = cliente_publico.post(
        "/api/v1/lecturas",
        json=_lectura(entorno, 72.0, variable="humedad"),
        headers=cabecera_dispositivo(),
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["estado_rango"] == "sin_rango"
    assert entorno.repositorio.listar_alertas() == []


def test_cada_lectura_fuera_de_rango_produce_exactamente_una_alerta(cliente_publico, entorno):
    for valor in (7.4, 7.9):
        cliente_publico.post(
            "/api/v1/lecturas", json=_lectura(entorno, valor), headers=cabecera_dispositivo()
        )
    assert len(entorno.repositorio.listar_alertas()) == 2


# ---------------------------------------------------------------------------
# Registro manual y consulta
# ---------------------------------------------------------------------------


def test_registro_manual_queda_con_origen_manual(cliente_operador, entorno):
    respuesta = cliente_operador.post(
        "/api/v1/lecturas/manual",
        json={
            "modulo_id": entorno.modulo_id,
            "variable": "ph",
            "valor": 6.2,
            "observacion": "medición con kit colorimétrico",
        },
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["origen"] == "manual"


def test_consulta_filtrada_por_variable(cliente_publico, cliente_operador, entorno):
    cliente_publico.post(
        "/api/v1/lecturas", json=_lectura(entorno, 6.0), headers=cabecera_dispositivo()
    )
    cliente_publico.post(
        "/api/v1/lecturas",
        json=_lectura(entorno, 70.0, variable="humedad"),
        headers=cabecera_dispositivo(),
    )
    respuesta = cliente_operador.get("/api/v1/lecturas", params={"variable": "humedad"})
    assert respuesta.status_code == 200
    lecturas = respuesta.json()
    assert len(lecturas) == 1
    assert lecturas[0]["variable"] == "humedad"


def test_consulta_con_variable_inexistente_se_responde_422(cliente_operador):
    respuesta = cliente_operador.get("/api/v1/lecturas", params={"variable": "oxigeno"})
    assert respuesta.status_code == 422
    assert "variables_admitidas" in respuesta.json()["detalle"]


def test_resumen_de_la_serie_consultada(cliente_publico, cliente_operador, entorno):
    for valor in (6.0, 6.6, 5.4):
        cliente_publico.post(
            "/api/v1/lecturas", json=_lectura(entorno, valor), headers=cabecera_dispositivo()
        )
    resumen = cliente_operador.get("/api/v1/lecturas/resumen").json()
    assert len(resumen) == 1
    assert resumen[0]["variable"] == "ph"
    assert resumen[0]["cantidad"] == 3
    assert resumen[0]["promedio"] == 6.0
    assert resumen[0]["maximo"] == 6.6
    assert resumen[0]["minimo"] == 5.4


# ---------------------------------------------------------------------------
# Exportación
# ---------------------------------------------------------------------------


def test_exportacion_csv_contiene_las_lecturas_consultadas(cliente_publico, cliente_operador, entorno):
    cliente_publico.post(
        "/api/v1/lecturas", json=_lectura(entorno, 6.0), headers=cabecera_dispositivo()
    )
    respuesta = cliente_operador.get("/api/v1/exportaciones/lecturas.csv")
    assert respuesta.status_code == 200
    assert "text/csv" in respuesta.headers["content-type"]
    assert "attachment" in respuesta.headers["content-disposition"]
    contenido = respuesta.text
    assert "id,modulo_id,variable,valor,unidad,origen,timestamp" in contenido
    assert entorno.modulo_id in contenido


# ---------------------------------------------------------------------------
# Eliminación
# ---------------------------------------------------------------------------


def test_eliminar_lectura_requiere_rol_de_administracion(cliente_publico, cliente_operador, cliente_administrador, entorno):
    creada = cliente_publico.post(
        "/api/v1/lecturas", json=_lectura(entorno, 6.0), headers=cabecera_dispositivo()
    ).json()

    assert cliente_operador.delete(f"/api/v1/lecturas/{creada['id']}").status_code == 403
    assert cliente_administrador.delete(f"/api/v1/lecturas/{creada['id']}").status_code == 204
    assert cliente_administrador.get(f"/api/v1/lecturas/{creada['id']}").status_code == 404


def test_no_se_puede_eliminar_un_modulo_con_lecturas(cliente_publico, cliente_administrador, entorno):
    cliente_publico.post(
        "/api/v1/lecturas", json=_lectura(entorno, 6.0), headers=cabecera_dispositivo()
    )
    respuesta = cliente_administrador.delete(f"/api/v1/modulos/{entorno.modulo_id}")
    assert respuesta.status_code == 409
    assert "desactívelo" in respuesta.json()["mensaje"]
