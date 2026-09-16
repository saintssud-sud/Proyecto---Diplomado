"""Pruebas del rol de solo consulta (Invitado).

El proyecto documenta tres roles —Administrador, Operador e Invitado— y el
servicio debe hacerlos efectivos: el Invitado consulta el panel, el historial y
las alertas, pero no registra mediciones ni modifica configuración alguna. La
decisión se resuelve en el servidor, de modo que ocultar una acción en la
interfaz sea una comodidad y no el control de acceso.
"""

from .conftest import UID_INVITADO, cabecera, cabecera_dispositivo

# ---------------------------------------------------------------------------
# El Invitado consulta
# ---------------------------------------------------------------------------


def test_el_invitado_puede_consultar_las_lecturas(cliente_con_token):
    respuesta = cliente_con_token.get("/api/v1/lecturas", headers=cabecera("invitado"))
    assert respuesta.status_code == 200


def test_el_invitado_puede_consultar_los_modulos(cliente_con_token):
    respuesta = cliente_con_token.get("/api/v1/modulos", headers=cabecera("invitado"))
    assert respuesta.status_code == 200


def test_el_invitado_puede_consultar_los_rangos(cliente_con_token):
    respuesta = cliente_con_token.get("/api/v1/rangos", headers=cabecera("invitado"))
    assert respuesta.status_code == 200


def test_el_invitado_puede_consultar_las_alertas(cliente_con_token):
    respuesta = cliente_con_token.get("/api/v1/alertas", headers=cabecera("invitado"))
    assert respuesta.status_code == 200


def test_el_invitado_puede_exportar_el_historial(cliente_con_token):
    respuesta = cliente_con_token.get(
        "/api/v1/exportaciones/lecturas.csv", headers=cabecera("invitado")
    )
    assert respuesta.status_code == 200


def test_el_invitado_puede_consultar_su_propio_perfil(cliente_con_token):
    respuesta = cliente_con_token.get("/api/v1/usuarios/perfil", headers=cabecera("invitado"))
    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == UID_INVITADO
    assert respuesta.json()["rol"] == "invitado"


# ---------------------------------------------------------------------------
# El Invitado no escribe
# ---------------------------------------------------------------------------


def test_el_invitado_no_puede_registrar_una_lectura_manual(cliente_con_token, entorno):
    respuesta = cliente_con_token.post(
        "/api/v1/lecturas/manual",
        json={"modulo_id": entorno.modulo_id, "variable": "ph", "valor": 6.0},
        headers=cabecera("invitado"),
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "sin_permiso"
    assert respuesta.json()["detalle"]["rol_actual"] == "invitado"
    assert "operar" in respuesta.json()["mensaje"]


def test_el_invitado_no_puede_atender_una_alerta(cliente_con_token, entorno):
    # Se genera una alerta con una lectura fuera de rango enviada por el dispositivo.
    cliente_con_token.post(
        "/api/v1/lecturas",
        json={"modulo_id": entorno.modulo_id, "variable": "ph", "valor": 7.4},
        headers=cabecera_dispositivo(),
    )
    alerta = entorno.repositorio.listar_alertas()[0]

    respuesta = cliente_con_token.patch(
        "/api/v1/alertas/%s" % alerta["id"],
        json={"estado": "atendida"},
        headers=cabecera("invitado"),
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["detalle"]["rol_actual"] == "invitado"


def test_el_invitado_no_puede_crear_modulos(cliente_con_token, entorno):
    respuesta = cliente_con_token.post(
        "/api/v1/modulos",
        json={"nombre": "Módulo 4", "tipo_cultivo": "Lechuga", "perfil_id": entorno.perfil_id},
        headers=cabecera("invitado"),
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["detalle"]["rol_actual"] == "invitado"


def test_el_invitado_no_puede_modificar_rangos(cliente_con_token, entorno):
    rango = entorno.repositorio.listar_rangos()[0]

    respuesta = cliente_con_token.patch(
        "/api/v1/rangos/%s" % rango["id"],
        json={"minimo": 5.0},
        headers=cabecera("invitado"),
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["detalle"]["rol_actual"] == "invitado"


def test_el_invitado_no_puede_eliminar_lecturas(cliente_con_token, entorno):
    respuesta = cliente_con_token.delete(
        "/api/v1/lecturas/lectura-inexistente", headers=cabecera("invitado")
    )

    # El nivel de autorización se comprueba antes que la existencia del recurso.
    assert respuesta.status_code == 403


# ---------------------------------------------------------------------------
# El nivel de operación sigue funcionando
# ---------------------------------------------------------------------------


def test_el_operador_conserva_sus_atribuciones(cliente_con_token, entorno):
    respuesta = cliente_con_token.post(
        "/api/v1/lecturas/manual",
        json={"modulo_id": entorno.modulo_id, "variable": "ph", "valor": 6.1},
        headers=cabecera("operador"),
    )

    assert respuesta.status_code == 201
