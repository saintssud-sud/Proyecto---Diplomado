"""Datos de demostración para el modo sin credenciales.

Cuando el servicio se ejecuta con `USAR_REPOSITORIO_EN_MEMORIA=true` no hay
Firebase ni sensores: esta semilla carga un perfil de cultivo, dos módulos, sus
rangos de referencia y un historial de lecturas para que el sistema pueda
recorrerse completo.

Las lecturas se registran con el **mismo servicio que usa la ingesta real**
(`servicios.lecturas.registrar`), de modo que la semilla no inventa alertas: las
genera la misma lógica que las generará en producción cuando un valor salga de
su rango. Eso hace que el modo de demostración sea también una prueba de la
regla de negocio.
"""

from datetime import datetime, timedelta, timezone

from .esquemas import LecturaEntrada
from .repositorios.base import RepositorioDatos
from .servicios import lecturas as servicio_lecturas

# Identificadores fijos: permiten referirse a ellos en la documentación y en la
# demostración sin tener que consultarlos antes.
PERFIL_ID = 'perfil-lechuga'
MODULO_ID = 'modulo-1'
MODULO_INACTIVO_ID = 'modulo-2'

RANGOS = (
    ('ph', 5.5, 6.5),
    ('ec', 1.2, 1.8),
    ('tds', 600.0, 900.0),
    ('temp_solucion', 15.0, 25.0),
    ('temp_ambiental', 15.0, 25.0),
    ('humedad', 50.0, 80.0),
)

# Lecturas de ejemplo: (variable, valor, horas atrás, origen, observación).
# Se incluyen valores dentro y fuera de rango para que la demostración muestre
# tanto el estado normal como las alertas.
LECTURAS = (
    ('ph', 6.1, 1, 'automatico', None),
    ('temp_solucion', 21.4, 2, 'automatico', None),
    ('humedad', 68.0, 3, 'automatico', None),
    ('ph', 6.3, 6, 'automatico', None),
    ('ec', 1.5, 8, 'automatico', None),
    ('ph', 7.4, 10, 'automatico', None),
    ('ec', 2.3, 12, 'automatico', None),
    ('humedad', 42.0, 14, 'automatico', None),
    ('temp_solucion', 18.9, 20, 'automatico', None),
    ('ph', 6.0, 26, 'manual', 'Medición con kit colorimétrico'),
    ('tds', 780.0, 30, 'automatico', None),
    ('ph', 6.2, 36, 'automatico', None),
)


def sembrar_demostracion(repositorio: RepositorioDatos) -> bool:
    """Carga los datos de demostración si el repositorio está vacío.

    Devuelve `True` si sembró y `False` si ya había datos, de modo que reiniciar
    el servicio no duplique el historial.
    """
    if repositorio.listar_perfiles():
        return False

    repositorio.crear_perfil(
        {
            'id': PERFIL_ID,
            'nombre': 'Lechuga',
            'descripcion': 'Perfil de referencia del modo de demostración',
            'predefinido': True,
        }
    )

    repositorio.crear_modulo(
        {
            'id': MODULO_ID,
            'nombre': 'Módulo 1',
            'tipo_cultivo': 'Lechuga',
            'perfil_id': PERFIL_ID,
            'ubicacion': 'Invernadero Norte',
            'activo': True,
        }
    )

    repositorio.crear_modulo(
        {
            'id': MODULO_INACTIVO_ID,
            'nombre': 'Módulo 2',
            'tipo_cultivo': 'Lechuga',
            'perfil_id': PERFIL_ID,
            'ubicacion': 'Invernadero Sur',
            'activo': False,
        }
    )

    for variable, minimo, maximo in RANGOS:
        repositorio.crear_rango(
            {
                'perfil_id': PERFIL_ID,
                'variable': variable,
                'minimo': minimo,
                'maximo': maximo,
            }
        )

    ahora = datetime.now(timezone.utc)
    for indice, (variable, valor, horas, origen, observacion) in enumerate(LECTURAS):
        entrada = LecturaEntrada(
            modulo_id=MODULO_ID,
            variable=variable,
            valor=valor,
            timestamp=ahora - timedelta(hours=horas),
            observacion=observacion,
        )
        servicio_lecturas.registrar(repositorio, entrada, origen=origen)

    return True
