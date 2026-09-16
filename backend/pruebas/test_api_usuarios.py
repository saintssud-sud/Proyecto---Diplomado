"""Pruebas del perfil del usuario.

Cubren el requisito mínimo 2 (autenticación con control de acceso por rol) y el
RNF-03: la aplicación no decide quién es el usuario ni qué puede hacer. Aquí se
comprueba, además, que el perfil propio no sirva de puerta para elevar
privilegios.
"""

from .conftest import UID_OPERADOR, cabecera

# ---------------------------------------------------------------------------
# Consulta del perfil propio
# ---------------------------------------------------------------------------


def test_el_operador_consulta_su_perfil(cliente_con_token):
    respuesta = cliente_con_token.get("/api/v1/usuarios/perfil", headers=cabecera("operador"))

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["id"] == UID_OPERADOR
    assert cuerpo["email"] == "operador@sigvach.com"
    assert cuerpo["rol"] == "usuario"
    assert cuerpo["activo"] is True


def test_sin_token_no_se_puede_consultar_el_perfil(cliente_con_token):
    respuesta = cliente_con_token.get("/api/v1/usuarios/perfil")

    assert respuesta.status_code == 401
    assert respuesta.json()["codigo"] == "no_autenticado"


def test_una_cuenta_sin_perfil_no_puede_consultarlo(cliente_con_token):
    respuesta = cliente_con_token.get(
        "/api/v1/usuarios/perfil", headers=cabecera("sin-perfil")
    )

    assert respuesta.status_code == 403
    assert "perfil registrado" in respuesta.json()["mensaje"]


def test_una_cuenta_desactivada_no_puede_consultar_su_perfil(cliente_con_token):
    respuesta = cliente_con_token.get(
        "/api/v1/usuarios/perfil", headers=cabecera("inactivo")
    )

    assert respuesta.status_code == 403
    assert "desactivada" in respuesta.json()["mensaje"]


# ---------------------------------------------------------------------------
# Actualización de los datos personales
# ---------------------------------------------------------------------------


def test_el_usuario_actualiza_sus_datos_de_contacto(cliente_con_token, entorno):
    respuesta = cliente_con_token.patch(
        "/api/v1/usuarios/perfil",
        json={"nombre": "Operador Dos", "telefono": "77712345", "cargo": "Técnico"},
        headers=cabecera("operador"),
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Operador Dos"
    assert cuerpo["telefono"] == "77712345"
    assert cuerpo["cargo"] == "Técnico"

    # El cambio quedó guardado en el repositorio, no solo en la respuesta.
    guardado = entorno.repositorio.obtener_perfil_usuario(UID_OPERADOR)
    assert guardado is not None
    assert guardado["nombre"] == "Operador Dos"


def test_la_actualizacion_parcial_no_borra_los_demas_datos(cliente_con_token, entorno):
    cliente_con_token.patch(
        "/api/v1/usuarios/perfil",
        json={"nombre": "Operador Dos", "telefono": "77712345"},
        headers=cabecera("operador"),
    )

    respuesta = cliente_con_token.patch(
        "/api/v1/usuarios/perfil",
        json={"cargo": "Supervisor"},
        headers=cabecera("operador"),
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["cargo"] == "Supervisor"
    assert cuerpo["nombre"] == "Operador Dos"
    assert cuerpo["telefono"] == "77712345"


def test_una_peticion_sin_datos_se_rechaza(cliente_con_token):
    respuesta = cliente_con_token.patch(
        "/api/v1/usuarios/perfil", json={}, headers=cabecera("operador")
    )

    assert respuesta.status_code == 400
    assert "ningún dato" in respuesta.json()["mensaje"]


def test_no_se_puede_cambiar_el_rol_desde_el_perfil_propio(cliente_con_token, entorno):
    """El rol no es un campo del esquema: la petición ni siquiera se acepta."""
    respuesta = cliente_con_token.patch(
        "/api/v1/usuarios/perfil",
        json={"nombre": "Operador Dos", "rol": "admin"},
        headers=cabecera("operador"),
    )

    assert respuesta.status_code == 422
    guardado = entorno.repositorio.obtener_perfil_usuario(UID_OPERADOR)
    assert guardado is not None
    assert guardado["rol"] == "usuario"


def test_no_se_puede_cambiar_el_estado_de_activacion_propio(cliente_con_token, entorno):
    """La activación es una atribución de administración, no del propio usuario."""
    respuesta = cliente_con_token.patch(
        "/api/v1/usuarios/perfil",
        json={"nombre": "Operador Dos", "activo": False},
        headers=cabecera("operador"),
    )

    assert respuesta.status_code == 422
    guardado = entorno.repositorio.obtener_perfil_usuario(UID_OPERADOR)
    assert guardado is not None
    assert guardado["activo"] is True


def test_el_nombre_demasiado_corto_se_rechaza(cliente_con_token):
    respuesta = cliente_con_token.patch(
        "/api/v1/usuarios/perfil",
        json={"nombre": "A"},
        headers=cabecera("operador"),
    )

    assert respuesta.status_code == 422
