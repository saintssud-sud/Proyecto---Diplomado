"""Pruebas del orden de los módulos de cultivo.

El orden importa más de lo que parece: la aplicación presenta el **primer módulo
de la lista** como módulo vigente. Con el orden alfabético, un módulo creado
después para verificar el alta —y escrito con otra grafía, por ejemplo sin
tilde— se anteponía al módulo original del cultivo, y el panel abría entonces un
módulo sin lecturas. El criterio se fijó en la **antigüedad**, que es estable
frente a renombrados y grafías.
"""

from datetime import datetime, timedelta, timezone

from .conftest import cabecera

BASE = datetime.now(timezone.utc)


def test_los_modulos_se_ordenan_por_fecha_de_creacion(entorno):
    repositorio = entorno.repositorio
    repositorio.crear_modulo(
        {
            "nombre": "Modulo 3",
            "tipo_cultivo": "Lechuga",
            "perfil_id": entorno.perfil_id,
            "activo": True,
            "creado_en": BASE + timedelta(days=2),
        }
    )
    repositorio.crear_modulo(
        {
            "nombre": "Álvarez",
            "tipo_cultivo": "Lechuga",
            "perfil_id": entorno.perfil_id,
            "activo": True,
            "creado_en": BASE + timedelta(days=3),
        }
    )

    nombres = [modulo["nombre"] for modulo in repositorio.listar_modulos(activo=True)]

    # El módulo creado primero encabeza la lista, aunque su nombre empiece por "M".
    assert nombres[0] == "Módulo 1"
    assert nombres[-1] == "Álvarez"


def test_la_api_devuelve_primero_el_modulo_mas_antiguo(cliente_administrador, entorno):
    entorno.repositorio.crear_modulo(
        {
            "nombre": "Modulo 3",
            "tipo_cultivo": "Lechuga",
            "perfil_id": entorno.perfil_id,
            "activo": True,
            "creado_en": BASE + timedelta(days=5),
        }
    )

    respuesta = cliente_administrador.get("/api/v1/modulos", headers=cabecera("admin"))

    assert respuesta.status_code == 200
    assert respuesta.json()[0]["nombre"] == "Módulo 1"
