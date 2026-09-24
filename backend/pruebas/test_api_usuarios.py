"""Pruebas del perfil del usuario y de la administración de las cuentas.

Cubren el requisito mínimo 2 (autenticación con control de acceso por rol), el
RNF-03 y el requisito funcional RF-02: la aplicación no decide quién es el usuario
ni qué puede hacer. Aquí se comprueba, además, que el perfil propio no sirva de
puerta para elevar privilegios y que la administración de las cuentas solo la
ejerza quien tiene ese rol.
"""

from .conftest import UID_ADMINISTRADOR, UID_OPERADOR, cabecera

# ---------------------------------------------------------------------------
# Consulta del perfil propio
# ---------------------------------------------------------------------------


def test_el_operador_consulta_su_perfil(cliente_con_token):
    respuesta = cliente_con_token.get("/api/v1/usuarios/perfil", headers=cabecera("operador"))

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["id"] == UID_OPERADOR
    assert cuerpo["email"] == "operador@sigvach.com"
    assert cuerpo["rol"] == "operador"
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
        json={"nombre": "Operador Dos", "rol": "administrador"},
        headers=cabecera("operador"),
    )

    assert respuesta.status_code == 422
    guardado = entorno.repositorio.obtener_perfil_usuario(UID_OPERADOR)
    assert guardado is not None
    assert guardado["rol"] == "operador"


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


# ---------------------------------------------------------------------------
# Administración de las cuentas (RF-02)
# ---------------------------------------------------------------------------


def test_el_administrador_lista_las_cuentas(cliente_administrador):
    respuesta = cliente_administrador.get("/api/v1/usuarios")

    assert respuesta.status_code == 200
    correos = {cuenta["email"] for cuenta in respuesta.json()}
    assert {"admin@sigvach.com", "operador@sigvach.com", "invitado@sigvach.com"} <= correos
    # El rol y el estado viajan en el listado: el panel no necesita leer la base.
    assert all("rol" in cuenta and "activo" in cuenta for cuenta in respuesta.json())


def test_el_operador_no_puede_listar_las_cuentas(cliente_operador):
    assert cliente_operador.get("/api/v1/usuarios").status_code == 403


def test_el_administrador_consulta_una_cuenta(cliente_administrador):
    respuesta = cliente_administrador.get("/api/v1/usuarios/%s" % UID_OPERADOR)

    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == UID_OPERADOR
    assert respuesta.json()["rol"] == "operador"


def test_una_cuenta_inexistente_se_responde_404(cliente_administrador):
    assert cliente_administrador.get("/api/v1/usuarios/u-nadie").status_code == 404


def test_el_administrador_cambia_el_rol_de_una_cuenta(cliente_administrador, entorno):
    respuesta = cliente_administrador.patch(
        "/api/v1/usuarios/%s" % UID_OPERADOR, json={"rol": "administrador"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["rol"] == "administrador"
    assert entorno.repositorio.obtener_perfil_usuario(UID_OPERADOR)["rol"] == "administrador"


def test_el_administrador_desactiva_una_cuenta(cliente_administrador, entorno):
    respuesta = cliente_administrador.patch(
        "/api/v1/usuarios/%s" % UID_OPERADOR, json={"activo": False}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["activo"] is False
    assert entorno.repositorio.obtener_perfil_usuario(UID_OPERADOR)["activo"] is False


def test_la_cuenta_desactivada_deja_de_poder_operar(cliente_administrador, cliente_con_token):
    cliente_administrador.patch("/api/v1/usuarios/%s" % UID_OPERADOR, json={"activo": False})

    # La autorización la resuelve el servidor en cada petición, contra el perfil
    # almacenado: por eso se consulta con el cliente que verifica el token de
    # verdad y no con el que sustituye la identidad.
    respuesta = cliente_con_token.get(
        "/api/v1/usuarios/perfil", headers=cabecera("operador")
    )
    assert respuesta.status_code == 403
    assert "desactivada" in respuesta.json()["mensaje"]


def test_el_operador_no_puede_cambiar_roles(cliente_operador, entorno):
    respuesta = cliente_operador.patch(
        "/api/v1/usuarios/%s" % UID_ADMINISTRADOR, json={"rol": "operador"}
    )

    assert respuesta.status_code == 403
    assert entorno.repositorio.obtener_perfil_usuario(UID_ADMINISTRADOR)["rol"] == "administrador"


def test_un_rol_desconocido_se_rechaza(cliente_administrador, entorno):
    respuesta = cliente_administrador.patch(
        "/api/v1/usuarios/%s" % UID_OPERADOR, json={"rol": "superusuario"}
    )

    assert respuesta.status_code == 422
    assert "roles_admitidos" in respuesta.json()["detalle"]
    assert entorno.repositorio.obtener_perfil_usuario(UID_OPERADOR)["rol"] == "operador"


def test_la_administracion_no_puede_quitarse_su_propio_rol(cliente_administrador, entorno):
    respuesta = cliente_administrador.patch(
        "/api/v1/usuarios/%s" % UID_ADMINISTRADOR, json={"rol": "operador"}
    )

    assert respuesta.status_code == 409
    assert entorno.repositorio.obtener_perfil_usuario(UID_ADMINISTRADOR)["rol"] == "administrador"


def test_la_administracion_no_puede_desactivar_su_cuenta(cliente_administrador):
    respuesta = cliente_administrador.patch(
        "/api/v1/usuarios/%s" % UID_ADMINISTRADOR, json={"activo": False}
    )

    assert respuesta.status_code == 409


def test_la_administracion_actualiza_los_datos_de_una_cuenta(cliente_administrador, entorno):
    respuesta = cliente_administrador.patch(
        "/api/v1/usuarios/%s" % UID_OPERADOR,
        json={"nombre": "Operador Uno", "cargo": "Encargado"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Operador Uno"
    guardado = entorno.repositorio.obtener_perfil_usuario(UID_OPERADOR)
    assert guardado["cargo"] == "Encargado"
    assert guardado["rol"] == "operador"


def test_una_actualizacion_sin_datos_se_rechaza(cliente_administrador):
    respuesta = cliente_administrador.patch("/api/v1/usuarios/%s" % UID_OPERADOR, json={})

    assert respuesta.status_code == 400


def test_el_administrador_elimina_una_cuenta(cliente_administrador, cliente_con_token, entorno):
    respuesta = cliente_administrador.delete("/api/v1/usuarios/%s" % UID_OPERADOR)

    assert respuesta.status_code == 204
    assert entorno.repositorio.obtener_perfil_usuario(UID_OPERADOR) is None
    # Sin perfil no hay rol que resolver: la cuenta deja de operar.
    assert (
        cliente_con_token.get(
            "/api/v1/usuarios/perfil", headers=cabecera("operador")
        ).status_code
        == 403
    )


def test_la_administracion_no_puede_eliminar_su_propia_cuenta(cliente_administrador):
    respuesta = cliente_administrador.delete("/api/v1/usuarios/%s" % UID_ADMINISTRADOR)

    assert respuesta.status_code == 409


def test_el_operador_no_puede_eliminar_cuentas(cliente_operador):
    assert cliente_operador.delete("/api/v1/usuarios/%s" % UID_ADMINISTRADOR).status_code == 403
