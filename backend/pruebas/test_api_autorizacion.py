"""Pruebas de autenticación y autorización.

Corresponden al requisito mínimo 2 (autenticación con control de acceso por rol)
y al RNF-03: ninguna operación debe resolverse por lo que decida el cliente.
"""

from .conftest import cabecera, cabecera_dispositivo

# ---------------------------------------------------------------------------
# Autenticación de usuarios
# ---------------------------------------------------------------------------


def test_sin_token_se_responde_401(cliente_con_token):
    respuesta = cliente_con_token.get("/api/v1/lecturas")
    assert respuesta.status_code == 401
    assert respuesta.json() == {
        "codigo": "no_autenticado",
        "mensaje": "Falta el token de identidad en la cabecera Authorization.",
        "detalle": {},
    }


def test_con_cabecera_mal_formada_se_responde_401(cliente_con_token):
    respuesta = cliente_con_token.get("/api/v1/lecturas", headers={"Authorization": "token-suelto"})
    assert respuesta.status_code == 401


def test_con_token_no_reconocido_se_responde_401(cliente_con_token):
    respuesta = cliente_con_token.get(
        "/api/v1/lecturas", headers={"Authorization": "Bearer token-falsificado"}
    )
    assert respuesta.status_code == 401
    assert respuesta.json()["codigo"] == "no_autenticado"


def test_token_valido_con_perfil_habilitado_accede(cliente_con_token):
    respuesta = cliente_con_token.get("/api/v1/lecturas", headers=cabecera("operador"))
    assert respuesta.status_code == 200


def test_un_usuario_desactivado_no_puede_operar(cliente_con_token):
    respuesta = cliente_con_token.get("/api/v1/lecturas", headers=cabecera("inactivo"))
    assert respuesta.status_code == 403
    assert "desactivada" in respuesta.json()["mensaje"]


def test_un_token_sin_perfil_registrado_se_rechaza(cliente_con_token):
    respuesta = cliente_con_token.get("/api/v1/lecturas", headers=cabecera("sin-perfil"))
    assert respuesta.status_code == 403
    assert "perfil registrado" in respuesta.json()["mensaje"]


# ---------------------------------------------------------------------------
# Autorización por rol
# ---------------------------------------------------------------------------


def test_el_operador_no_puede_crear_modulos(cliente_con_token, entorno):
    respuesta = cliente_con_token.post(
        "/api/v1/modulos",
        json={"nombre": "Módulo 3", "tipo_cultivo": "Tomate", "perfil_id": entorno.perfil_id},
        headers=cabecera("operador"),
    )
    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "sin_permiso"
    assert respuesta.json()["detalle"]["rol_actual"] == "usuario"


def test_el_operador_no_puede_modificar_rangos(cliente_con_token, entorno):
    rango = entorno.repositorio.buscar_rango(entorno.perfil_id, "ph")
    respuesta = cliente_con_token.patch(
        f"/api/v1/rangos/{rango['id']}", json={"maximo": 7.5}, headers=cabecera("operador")
    )
    assert respuesta.status_code == 403


def test_el_administrador_puede_crear_modulos(cliente_con_token, entorno):
    respuesta = cliente_con_token.post(
        "/api/v1/modulos",
        json={"nombre": "Módulo 3", "tipo_cultivo": "Tomate", "perfil_id": entorno.perfil_id},
        headers=cabecera("admin"),
    )
    assert respuesta.status_code == 201


def test_el_operador_si_puede_registrar_lecturas_manuales(cliente_con_token, entorno):
    respuesta = cliente_con_token.post(
        "/api/v1/lecturas/manual",
        json={"modulo_id": entorno.modulo_id, "variable": "ph", "valor": 6.3},
        headers=cabecera("operador"),
    )
    assert respuesta.status_code == 201


def test_el_administrador_puede_modificar_rangos(cliente_con_token, entorno):
    rango = entorno.repositorio.buscar_rango(entorno.perfil_id, "ph")
    respuesta = cliente_con_token.patch(
        f"/api/v1/rangos/{rango['id']}", json={"maximo": 6.8}, headers=cabecera("admin")
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["maximo"] == 6.8


def test_el_dispositivo_no_puede_consultar_lecturas(cliente_con_token, entorno):
    """La clave del dispositivo sirve para publicar lecturas, no para leerlas."""
    respuesta = cliente_con_token.get(
        "/api/v1/lecturas", headers=cabecera_dispositivo()
    )
    assert respuesta.status_code == 401


# ---------------------------------------------------------------------------
# Diagnóstico
# ---------------------------------------------------------------------------


def test_el_endpoint_de_salud_es_publico(cliente_publico):
    respuesta = cliente_publico.get("/api/v1/salud")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "ok"
    assert cuerpo["version_api"] == "v1"
    assert cuerpo["base_de_datos"] == "conectada"


def test_la_documentacion_del_contrato_esta_publicada(cliente_publico):
    respuesta = cliente_publico.get("/api/v1/openapi.json")
    assert respuesta.status_code == 200
    rutas = respuesta.json()["paths"]
    for ruta in ("/api/v1/salud", "/api/v1/lecturas", "/api/v1/modulos", "/api/v1/rangos", "/api/v1/alertas"):
        assert ruta in rutas
