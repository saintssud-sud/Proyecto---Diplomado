"""Pruebas de la semilla del modo de demostración."""

from app.repositorios.memoria import RepositorioMemoria
from app.semilla import MODULO_ID, MODULO_INACTIVO_ID, PERFIL_ID, RANGOS, sembrar_demostracion


def test_siembra_perfil_modulos_rangos_y_lecturas():
    repositorio = RepositorioMemoria()

    sembrado = sembrar_demostracion(repositorio)

    assert sembrado is True
    perfil = repositorio.obtener_perfil(PERFIL_ID)
    assert perfil is not None
    assert perfil['nombre'] == 'Lechuga'
    assert perfil['predefinido'] is True

    assert repositorio.obtener_modulo(MODULO_ID)['activo'] is True
    assert repositorio.obtener_modulo(MODULO_INACTIVO_ID)['activo'] is False

    assert len(repositorio.listar_rangos(perfil_id=PERFIL_ID)) == len(RANGOS)
    assert len(repositorio.listar_lecturas(modulo_id=MODULO_ID, limite=100)) == 12


def test_las_lecturas_fuera_de_rango_de_la_semilla_generan_sus_alertas():
    repositorio = RepositorioMemoria()
    sembrar_demostracion(repositorio)

    alertas = repositorio.listar_alertas()

    # La semilla incluye tres valores fuera de rango: pH 7.4, EC 2.3 y humedad 42.
    assert len(alertas) == 3
    assert all(alerta['estado'] == 'activa' for alerta in alertas)
    assert sorted(alerta['variable'] for alerta in alertas) == ['ec', 'humedad', 'ph']


def test_cada_alerta_de_la_semilla_conserva_su_lectura():
    repositorio = RepositorioMemoria()
    sembrar_demostracion(repositorio)

    for alerta in repositorio.listar_alertas():
        assert repositorio.obtener_lectura(alerta['lectura_id']) is not None


def test_el_historial_de_la_semilla_incluye_una_lectura_manual():
    repositorio = RepositorioMemoria()
    sembrar_demostracion(repositorio)

    lecturas = repositorio.listar_lecturas(modulo_id=MODULO_ID, limite=100)
    manuales = [lectura for lectura in lecturas if lectura['origen'] == 'manual']

    assert len(manuales) == 1
    assert manuales[0]['observacion']


def test_no_vuelve_a_sembrar_si_ya_hay_datos():
    repositorio = RepositorioMemoria()

    assert sembrar_demostracion(repositorio) is True
    assert sembrar_demostracion(repositorio) is False
    assert len(repositorio.listar_lecturas(modulo_id=MODULO_ID, limite=100)) == 12
