import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:sigvach/controllers/panel_controller.dart';
import 'package:sigvach/repositories/api/alertas_api_repository.dart';
import 'package:sigvach/repositories/api/lecturas_api_repository.dart';
import 'package:sigvach/repositories/api/modulos_api_repository.dart';
import 'package:sigvach/repositories/api/rangos_api_repository.dart';
import 'package:sigvach/services/api_cliente.dart';
import 'package:sigvach/services/api_errores.dart';
import 'package:sigvach/widgets/vista_con_estados.dart';

ApiCliente _cliente(Future<http.Response> Function(http.Request) responder) {
  return ApiCliente(
    cliente: MockClient(responder),
    obtenerToken: () async => 'token-de-prueba',
    baseUrl: 'https://api.ejemplo.test',
    espera: const Duration(seconds: 2),
  );
}

http.Response _json(Object cuerpo, {int estado = 200}) {
  return http.Response.bytes(
    utf8.encode(jsonEncode(cuerpo)),
    estado,
    headers: <String, String>{'content-type': 'application/json'},
  );
}

Map<String, dynamic> _moduloJson({String id = 'M-1', String nombre = 'Módulo 1'}) {
  return <String, dynamic>{
    'id': id,
    'nombre': nombre,
    'tipo_cultivo': 'Lechuga',
    'perfil_id': 'P-1',
    'ubicacion': 'Invernadero Norte',
    'activo': true,
  };
}

Map<String, dynamic> _lecturaJson({
  required String variable,
  required double valor,
  required String estadoRango,
  required String timestamp,
  String unidad = '',
}) {
  return <String, dynamic>{
    'id': 'L-$variable-$timestamp',
    'modulo_id': 'M-1',
    'variable': variable,
    'valor': valor,
    'unidad': unidad,
    'origen': 'automatico',
    'timestamp': timestamp,
    'estado_rango': estadoRango,
  };
}

Map<String, dynamic> _rangoJson(String variable, double minimo, double maximo, [String unidad = '']) {
  return <String, dynamic>{
    'id': 'R-$variable',
    'perfil_id': 'P-1',
    'variable': variable,
    'minimo': minimo,
    'maximo': maximo,
    'unidad': unidad,
  };
}

/// Panel armado sobre un servicio simulado que responde por ruta.
PanelController _panel({
  List<Map<String, dynamic>>? modulos,
  List<Map<String, dynamic>>? lecturas,
  List<Map<String, dynamic>>? rangos,
  List<Map<String, dynamic>>? alertas,
  http.Response Function()? respuestaManual,
}) {
  final List<Map<String, dynamic>> listaModulos = modulos ?? <Map<String, dynamic>>[_moduloJson()];
  final List<Map<String, dynamic>> listaLecturas = lecturas ?? <Map<String, dynamic>>[];
  final List<Map<String, dynamic>> listaRangos = rangos ?? <Map<String, dynamic>>[];
  final List<Map<String, dynamic>> listaAlertas = alertas ?? <Map<String, dynamic>>[];

  final ApiCliente cliente = _cliente((http.Request peticion) async {
    final String camino = peticion.url.path;
    if (peticion.method == 'POST' && camino.endsWith('/lecturas/manual')) {
      if (respuestaManual != null) {
        return respuestaManual();
      }
      return _json(<String, dynamic>{
        'id': 'L-nueva',
        'modulo_id': 'M-1',
        'variable': 'ph',
        'valor': 6.2,
        'unidad': '',
        'origen': 'manual',
        'timestamp': '2026-09-14T10:00:00Z',
        'estado_rango': 'dentro',
      }, estado: 201);
    }
    if (camino == '/api/v1/modulos') {
      return _json(listaModulos);
    }
    if (camino == '/api/v1/lecturas') {
      return _json(listaLecturas);
    }
    if (camino == '/api/v1/rangos') {
      return _json(listaRangos);
    }
    if (camino == '/api/v1/alertas') {
      return _json(listaAlertas);
    }
    return http.Response('recurso no encontrado', 404);
  });

  return PanelController(
    modulos: ModulosApiRepository(cliente),
    lecturas: LecturasApiRepository(cliente),
    rangos: RangosApiRepository(cliente),
    alertas: AlertasApiRepository(cliente),
  );
}

void main() {
  group('PanelController · composición del panel', () {
    test('arma una entrada por variable del catálogo con su último valor y su rango', () async {
      final PanelController panel = _panel(
        lecturas: <Map<String, dynamic>>[
          _lecturaJson(variable: 'ph', valor: 6.1, estadoRango: 'dentro', timestamp: '2026-09-14T10:00:00Z'),
          _lecturaJson(variable: 'ph', valor: 5.2, estadoRango: 'bajo', timestamp: '2026-09-14T08:00:00Z'),
        ],
        rangos: <Map<String, dynamic>>[_rangoJson('ph', 5.5, 6.5)],
      );

      await panel.cargar();

      expect(panel.estado, EstadoVista.conDatos);
      expect(panel.variables, hasLength(6));
      final EstadoDeVariable ph = panel.variables.firstWhere((EstadoDeVariable v) => v.codigo == 'ph');
      expect(ph.valor, 6.1, reason: 'Se toma el valor más reciente');
      expect(ph.minimo, 5.5);
      expect(ph.maximo, 6.5);
      expect(ph.fueraDeRango, isFalse);
      expect(ph.etiquetaEstado, 'Normal');
    });

    test('marca como fuera de rango la variable que el servidor evaluó así', () async {
      final PanelController panel = _panel(
        lecturas: <Map<String, dynamic>>[
          _lecturaJson(variable: 'ec', valor: 2.3, estadoRango: 'alto', timestamp: '2026-09-14T10:00:00Z'),
        ],
        rangos: <Map<String, dynamic>>[_rangoJson('ec', 1.2, 1.8, 'mS/cm')],
      );

      await panel.cargar();

      final EstadoDeVariable ec = panel.variables.firstWhere((EstadoDeVariable v) => v.codigo == 'ec');
      expect(ec.fueraDeRango, isTrue);
      expect(ec.etiquetaEstado, 'Por encima del rango');
      expect(panel.hayVariablesFueraDeRango, isTrue);
    });

    test('una variable sin rango configurado no se considera fuera de rango', () async {
      final PanelController panel = _panel(
        lecturas: <Map<String, dynamic>>[
          _lecturaJson(variable: 'humedad', valor: 42, estadoRango: 'sin_rango', timestamp: '2026-09-14T10:00:00Z', unidad: '%'),
        ],
      );

      await panel.cargar();

      final EstadoDeVariable humedad = panel.variables.firstWhere((EstadoDeVariable v) => v.codigo == 'humedad');
      expect(humedad.tieneRango, isFalse);
      expect(humedad.fueraDeRango, isFalse);
      expect(humedad.etiquetaEstado, 'Sin rango configurado');
      expect(humedad.unidad, '%', reason: 'La unidad del servidor tiene prioridad');
    });

    test('las variables sin lecturas quedan sin valor y con la fecha en nulo', () async {
      final PanelController panel = _panel(
        lecturas: <Map<String, dynamic>>[
          _lecturaJson(variable: 'ph', valor: 6.1, estadoRango: 'dentro', timestamp: '2026-09-14T10:00:00Z'),
        ],
      );

      await panel.cargar();

      final EstadoDeVariable tds = panel.variables.firstWhere((EstadoDeVariable v) => v.codigo == 'tds');
      expect(tds.tieneValor, isFalse);
      expect(tds.fecha, isNull);
      expect(tds.etiquetaEstado, 'Sin lecturas');
    });

    test('registra la fecha de la última lectura', () async {
      final PanelController panel = _panel(
        lecturas: <Map<String, dynamic>>[
          _lecturaJson(variable: 'ph', valor: 6.1, estadoRango: 'dentro', timestamp: '2026-09-14T10:00:00Z'),
          _lecturaJson(variable: 'ec', valor: 1.5, estadoRango: 'dentro', timestamp: '2026-09-14T04:00:00Z'),
        ],
      );

      await panel.cargar();

      expect(panel.ultimaLectura!.toUtc().hour, 10);
      expect(panel.modulo!.nombre, 'Módulo 1');
    });

    test('cuenta las alertas activas del módulo', () async {
      final PanelController panel = _panel(
        lecturas: <Map<String, dynamic>>[
          _lecturaJson(variable: 'ph', valor: 7.4, estadoRango: 'alto', timestamp: '2026-09-14T10:00:00Z'),
        ],
        alertas: <Map<String, dynamic>>[
          <String, dynamic>{
            'id': 'A-1',
            'lectura_id': 'L-1',
            'modulo_id': 'M-1',
            'variable': 'ph',
            'valor': 7.4,
            'rango_minimo': 5.5,
            'rango_maximo': 6.5,
            'estado': 'activa',
            'timestamp': '2026-09-14T10:00:00Z',
          },
        ],
      );

      await panel.cargar();

      expect(panel.alertasActivas, 1);
    });
  });

  group('PanelController · estados de la vista', () {
    test('sin módulos activos queda en estado vacío y no en error', () async {
      final PanelController panel = _panel(modulos: <Map<String, dynamic>>[]);

      await panel.cargar();

      expect(panel.estado, EstadoVista.vacio);
      expect(panel.modulo, isNull);
      expect(panel.variables, isEmpty);
      expect(panel.mensajeError, isNull);
    });

    test('un módulo sin lecturas queda en estado vacío', () async {
      final PanelController panel = _panel();

      await panel.cargar();

      expect(panel.estado, EstadoVista.vacio);
      expect(panel.modulo, isNotNull);
      expect(panel.variables, hasLength(6));
    });

    test('un fallo de conexión queda como error de conexión', () async {
      final ApiCliente cliente = _cliente(
        (http.Request peticion) async => throw http.ClientException('sin red'),
      );
      final PanelController panel = PanelController(
        modulos: ModulosApiRepository(cliente),
        lecturas: LecturasApiRepository(cliente),
        rangos: RangosApiRepository(cliente),
        alertas: AlertasApiRepository(cliente),
      );

      await panel.cargar();

      expect(panel.estado, EstadoVista.error);
      expect(panel.errorDeConexion, isTrue);
      expect(panel.mensajeError, contains('No se pudo comunicar con el servidor'));
    });

    test('un rechazo del servidor queda como error del servidor', () async {
      final ApiCliente cliente = _cliente(
        (http.Request peticion) async => _json(
          <String, dynamic>{
            'codigo': 'sin_permiso',
            'mensaje': 'La operación requiere un rol habilitado para operar sobre el cultivo.',
            'detalle': <String, dynamic>{},
          },
          estado: 403,
        ),
      );
      final PanelController panel = PanelController(
        modulos: ModulosApiRepository(cliente),
        lecturas: LecturasApiRepository(cliente),
        rangos: RangosApiRepository(cliente),
        alertas: AlertasApiRepository(cliente),
      );

      await panel.cargar();

      expect(panel.estado, EstadoVista.error);
      expect(panel.errorDeConexion, isFalse);
      expect(panel.mensajeError, contains('rol habilitado'));
    });

    test('reintentar recupera el panel cuando el servicio vuelve a responder', () async {
      bool disponible = false;
      final ApiCliente cliente = _cliente((http.Request peticion) async {
        if (!disponible) {
          throw http.ClientException('sin red');
        }
        final String camino = peticion.url.path;
        if (camino == '/api/v1/modulos') {
          return _json(<Map<String, dynamic>>[_moduloJson()]);
        }
        if (camino == '/api/v1/lecturas') {
          return _json(<Map<String, dynamic>>[
            _lecturaJson(variable: 'ph', valor: 6.1, estadoRango: 'dentro', timestamp: '2026-09-14T10:00:00Z'),
          ]);
        }
        return _json(<Map<String, dynamic>>[]);
      });
      final PanelController panel = PanelController(
        modulos: ModulosApiRepository(cliente),
        lecturas: LecturasApiRepository(cliente),
        rangos: RangosApiRepository(cliente),
        alertas: AlertasApiRepository(cliente),
      );

      await panel.cargar();
      expect(panel.estado, EstadoVista.error);

      disponible = true;
      await panel.reintentar();

      expect(panel.estado, EstadoVista.conDatos);
      expect(panel.variables.firstWhere((EstadoDeVariable v) => v.codigo == 'ph').valor, 6.1);
    });
  });

  group('PanelController · registro de una medición', () {
    test('envía solo las variables completadas y devuelve cuántas registró', () async {
      final List<String> enviadas = <String>[];
      final ApiCliente cliente = _cliente((http.Request peticion) async {
        if (peticion.method == 'POST') {
          enviadas.add(peticion.body);
          return _json(<String, dynamic>{
            'id': 'L-nueva',
            'modulo_id': 'M-1',
            'variable': 'ph',
            'valor': 6.2,
            'unidad': '',
            'origen': 'manual',
            'timestamp': '2026-09-14T10:00:00Z',
            'estado_rango': 'dentro',
          }, estado: 201);
        }
        final String camino = peticion.url.path;
        if (camino == '/api/v1/modulos') {
          return _json(<Map<String, dynamic>>[_moduloJson()]);
        }
        if (camino == '/api/v1/lecturas') {
          return _json(<Map<String, dynamic>>[
            _lecturaJson(variable: 'ph', valor: 6.2, estadoRango: 'dentro', timestamp: '2026-09-14T10:00:00Z'),
          ]);
        }
        return _json(<Map<String, dynamic>>[]);
      });
      final PanelController panel = PanelController(
        modulos: ModulosApiRepository(cliente),
        lecturas: LecturasApiRepository(cliente),
        rangos: RangosApiRepository(cliente),
        alertas: AlertasApiRepository(cliente),
      );

      await panel.cargar();
      final int registradas = await panel.registrarMedicion(
        <String, double>{'ph': 6.2, 'humedad': 68},
        observacion: 'medición con instrumentos portátiles',
      );

      expect(registradas, 2);
      expect(enviadas, hasLength(2));
      expect(enviadas.first.contains('"origen"'), isFalse);
      expect(enviadas.first.contains('"variable":"ph"'), isTrue);
      expect(enviadas.last.contains('"variable":"humedad"'), isTrue);
      expect(enviadas.last.contains('medición con instrumentos portátiles'), isTrue);
      expect(panel.estado, EstadoVista.conDatos);
    });

    test('el rechazo por validación se propaga con el campo señalado', () async {
      final PanelController panel = _panel(
        respuestaManual: () => _json(
          <String, dynamic>{
            'codigo': 'validacion_rechazada',
            'mensaje': 'La petición no cumple el contrato: revise los campos señalados.',
            'detalle': <String, dynamic>{
              'campos': <String, String>{'valor': 'ph debe estar entre 0.0 y 14.0'},
            },
          },
          estado: 422,
        ),
      );

      await panel.cargar();

      try {
        await panel.registrarMedicion(<String, double>{'ph': 99});
        fail('Se esperaba un ErrorApi de validación');
      } on ErrorApi catch (error) {
        expect(error.esValidacion, isTrue);
        expect(error.campos['valor'], contains('debe estar entre'));
      }
    });

    test('sin módulo seleccionado no se intenta registrar', () async {
      final PanelController panel = _panel(modulos: <Map<String, dynamic>>[]);
      await panel.cargar();

      expect(
        panel.registrarMedicion(<String, double>{'ph': 6.1}),
        throwsA(isA<StateError>()),
      );
    });

    test('sin valores no se intenta registrar', () async {
      final PanelController panel = _panel();
      await panel.cargar();

      expect(
        panel.registrarMedicion(<String, double>{}),
        throwsA(isA<ArgumentError>()),
      );
    });
  });

  group('PanelController · selección de módulo', () {
    test('permite cambiar entre los módulos disponibles', () async {
      final List<String> consultas = <String>[];
      final ApiCliente cliente = _cliente((http.Request peticion) async {
        final String camino = peticion.url.path;
        if (camino == '/api/v1/modulos') {
          return _json(<Map<String, dynamic>>[
            _moduloJson(id: 'M-1', nombre: 'Módulo 1'),
            _moduloJson(id: 'M-2', nombre: 'Módulo 2'),
          ]);
        }
        if (camino == '/api/v1/lecturas') {
          consultas.add(peticion.url.queryParameters['modulo_id'] ?? '');
          return _json(<Map<String, dynamic>>[]);
        }
        return _json(<Map<String, dynamic>>[]);
      });
      final PanelController panel = PanelController(
        modulos: ModulosApiRepository(cliente),
        lecturas: LecturasApiRepository(cliente),
        rangos: RangosApiRepository(cliente),
        alertas: AlertasApiRepository(cliente),
      );

      await panel.cargar();
      expect(panel.modulo!.id, 'M-1', reason: 'Por defecto se usa el primer módulo');

      await panel.seleccionarModulo('M-2');

      expect(panel.modulo!.id, 'M-2');
      expect(consultas.last, 'M-2');
    });
  });
}
