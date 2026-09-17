"""Pruebas del nombre del perfil de referencia en la respuesta de módulos.

El servicio devuelve, junto al identificador del perfil, su **nombre**: así las
pantallas pueden mostrar con qué rangos se evalúan las lecturas del módulo sin
cruzar por su cuenta la lista de perfiles. El panel de inicio no disponía de esa
lista, de modo que no podía nombrar el perfil de referencia del módulo vigente.
"""

from .conftest import cabecera


def test_el_listado_de_modulos_incluye_el_nombre_del_perfil(cliente_administrador, entorno):
    respuesta = cliente_administrador.get("/api/v1/modulos", headers=cabecera("admin"))

    assert respuesta.status_code == 200
    modulos = respuesta.json()
    assert modulos, "El entorno de prueba debe traer al menos un módulo"

    modulo = modulos[0]
    assert modulo["perfil_id"] == entorno.perfil_id
    assert modulo["perfil_nombre"] == "Lechuga"


def test_la_consulta_de_un_modulo_incluye_el_nombre_del_perfil(cliente_administrador, entorno):
    listado = cliente_administrador.get(
        "/api/v1/modulos", headers=cabecera("admin")
    ).json()
    modulo_id = listado[0]["id"]

    respuesta = cliente_administrador.get(
        f"/api/v1/modulos/{modulo_id}", headers=cabecera("admin")
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["perfil_nombre"] == "Lechuga"


def test_el_alta_de_un_modulo_devuelve_el_nombre_del_perfil(cliente_administrador, entorno):
    respuesta = cliente_administrador.post(
        "/api/v1/modulos",
        headers=cabecera("admin"),
        json={
            "nombre": "Módulo de prueba",
            "tipo_cultivo": "Acelga",
            "perfil_id": entorno.perfil_id,
            "ubicacion": "Invernadero Sur",
        },
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["perfil_nombre"] == "Lechuga"
    assert cuerpo["tipo_cultivo"] == "Acelga"


def test_un_perfil_inexistente_no_rompe_la_respuesta(cliente_administrador):
    """Sin perfil asociado, el nombre llega vacío en lugar de fallar.

    Es preferible una pantalla que muestre el módulo sin el nombre del perfil a
    una que no muestre nada porque la referencia quedó huérfana.
    """
    respuesta = cliente_administrador.post(
        "/api/v1/modulos",
        headers=cabecera("admin"),
        json={
            "nombre": "Módulo sin perfil válido",
            "tipo_cultivo": "Apio",
            "perfil_id": "perfil-inexistente",
        },
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["perfil_nombre"] == ""
