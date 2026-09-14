import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:sigvach/controllers/lecturas_controller.dart';
import 'package:sigvach/models/api/modelos_api.dart';
import 'package:sigvach/repositories/api/lecturas_api_repository.dart';
import 'package:sigvach/services/api_cliente.dart';
import 'package:sigvach/services/api_errores.dart';
import 'package:sigvach/widgets/vista_con_estados.dart';

/// Repositorio real construido sobre un servicio simulado.
LecturasApiRepository _repositorio(
  Future<http.Response> Function(http.Request) responder,
) {
  return LecturasApiRepository(
    ApiCliente(
      cliente: MockClient(responder),
      obtenerToken: () async => 'token-de-prueba',
      baseUrl: 'https://api.ejemplo.test',
      espera: const Duration(seconds: 2),
    ),
  );
}

http.Response _json(Object cuerpo, {int estado = 200}) {
  return http.Response.bytes(
    utf8.encode(jsonEncode(cuerpo)),
    estado,
    headers: <String, String>{'content-type': 'application/json'},
  );
}

Map<String, dynamic> _lecturaJson({
  String id = 'L-1',
  String variable = 'ph',
  double valor = 6.1,
  String estadoRango = 'dentro',
  String origen = 'automatico',
}) {
  return <String, dynamic>{
    'id': id,
    'modulo_id': 'M-1',
    'variable': variable,
    'valor': valor,
    'unidad': '',
    'origen': origen,
    'timestamp': '2026-09-13T22:50:00+00:00',
    'estado_rango': estadoRango,
  };
}

void main() {
  group('LecturasController · estados de la vista', () {
    test('pasa por carga y termina con datos', () async {
      final LecturasController controlador = LecturasController(
        _repositorio((http.Request peticion) async =>
            _json(<Map<String, dynamic>>[_lecturaJson()])),
      );

      final List<EstadoVista> estados = <EstadoVista>[];
      controlador.addListener(() => estados.add(controlador.estado));

      await controlador.cargar();

      expect(estados.first, EstadoVista.cargando);
      expect(controlador.estado, EstadoVista.conDatos);
      expect(controlador.lecturas, hasLength(1));
      expect(controlador.mensajeError, isNull);
    });

    test('sin resultados queda en estado vacío y no en error', () async {
      final LecturasController controlador = LecturasController(
        _repositorio((http.Request peticion) async => _json(<dynamic>[])),
      );

      await controlador.cargar();

      expect(controlador.estado, EstadoVista.vacio);
      expect(controlador.lecturas, isEmpty);
      expect(controlador.mensajeError, isNull);
    });

    test('un fallo de conexión queda como error de conexión', () async {
      final LecturasController controlador = LecturasController(
        _repositorio((http.Request peticion) async => throw http.ClientException('sin red')),
      );

      await controlador.cargar();

      expect(controlador.estado, EstadoVista.error);
      expect(controlador.errorDeConexion, isTrue);
      expect(
        controlador.mensajeError,
        'No se pudo comunicar con el servidor. Revise la conexión e intente nuevamente.',
      );
    });

    test('un rechazo del servidor queda como error del servidor, no de conexión', () async {
      final LecturasController controlador = LecturasController(
        _repositorio(
          (http.Request peticion) async => _json(
            <String, dynamic>{
              'codigo': 'sin_permiso',
              'mensaje': 'La operación requiere un rol habilitado para operar sobre el cultivo.',
              'detalle': <String, dynamic>{},
            },
            estado: 403,
          ),
        ),
      );

      await controlador.cargar();

      expect(controlador.estado, EstadoVista.error);
      expect(controlador.errorDeConexion, isFalse);
      expect(controlador.mensajeError, contains('rol habilitado'));
    });

    test('una respuesta que no cumple el contrato queda como error con reintento', () async {
      final LecturasController controlador = LecturasController(
        _repositorio((http.Request peticion) async => _json(<dynamic>[
              <String, dynamic>{'id': 'L-1', 'variable': 'ph'},
            ])),
      );

      await controlador.cargar();

      expect(controlador.estado, EstadoVista.error);
      expect(controlador.errorDeConexion, isTrue);
      expect(controlador.mensajeError, contains('no pudo interpretarse'));
    });

    test('reintentar vuelve a consultar el servicio', () async {
      int llamadas = 0;
      final LecturasController controlador = LecturasController(
        _repositorio((http.Request peticion) async {
          llamadas++;
          if (llamadas == 1) {
            throw http.ClientException('sin red');
          }
          return _json(<Map<String, dynamic>>[_lecturaJson()]);
        }),
      );

      await controlador.cargar();
      expect(controlador.estado, EstadoVista.error);

      await controlador.reintentar();
      expect(controlador.estado, EstadoVista.conDatos);
      expect(llamadas, 2);
    });

    test('los filtros vigentes se conservan al reintentar y se pueden limpiar', () async {
      final List<Uri> consultas = <Uri>[];
      final LecturasController controlador = LecturasController(
        _repositorio((http.Request peticion) async {
          consultas.add(peticion.url);
          return _json(<dynamic>[]);
        }),
      );

      await controlador.cargar(variable: 'ph', moduloId: 'M-1');
      await controlador.reintentar();
      await controlador.cargar(limpiarFiltros: true);

      expect(consultas.first.queryParameters['variable'], 'ph');
      expect(consultas.first.queryParameters['modulo_id'], 'M-1');
      expect(consultas[1].queryParameters['variable'], 'ph');
      expect(consultas.last.queryParameters.containsKey('variable'), isFalse);
      expect(controlador.variable, isNull);
      expect(controlador.moduloId, isNull);
    });

    test('identifica las lecturas fuera de rango según el estado del servidor', () async {
      final LecturasController controlador = LecturasController(
        _repositorio(
          (http.Request peticion) async => _json(<Map<String, dynamic>>[
            _lecturaJson(id: 'L-1', estadoRango: 'dentro'),
            _lecturaJson(id: 'L-2', valor: 7.4, estadoRango: 'alto'),
            _lecturaJson(id: 'L-3', valor: 5.1, estadoRango: 'bajo'),
            _lecturaJson(id: 'L-4', variable: 'humedad', estadoRango: 'sin_rango'),
          ]),
        ),
      );

      await controlador.cargar();

      expect(controlador.fueraDeRango, hasLength(2));
      expect(
        controlador.fueraDeRango.map((Lectura lectura) => lectura.id),
        <String>['L-2', 'L-3'],
      );
    });
  });

  group('LecturasController · registro manual y eliminación', () {
    test('el registro manual incorpora la lectura al listado', () async {
      final LecturasController controlador = LecturasController(
        _repositorio((http.Request peticion) async {
          if (peticion.method == 'POST') {
            return _json(_lecturaJson(id: 'L-9', origen: 'manual'), estado: 201);
          }
          return _json(<Map<String, dynamic>>[_lecturaJson()]);
        }),
      );

      await controlador.cargar();
      final Lectura nueva = await controlador.registrarManual(
        moduloId: 'M-1',
        variable: 'ph',
        valor: 6.2,
      );

      expect(nueva.esManual, isTrue);
      expect(controlador.lecturas.first.id, 'L-9');
      expect(controlador.estado, EstadoVista.conDatos);
    });

    test('el rechazo por validación se propaga con el campo señalado', () async {
      final LecturasController controlador = LecturasController(
        _repositorio(
          (http.Request peticion) async => _json(
            <String, dynamic>{
              'codigo': 'validacion_rechazada',
              'mensaje': 'La petición no cumple el contrato: revise los campos señalados.',
              'detalle': <String, dynamic>{
                'campos': <String, String>{'valor': 'ph debe estar entre 0.0 y 14.0'},
              },
            },
            estado: 422,
          ),
        ),
      );

      try {
        await controlador.registrarManual(moduloId: 'M-1', variable: 'ph', valor: 99);
        fail('Se esperaba un ErrorApi de validación');
      } on ErrorApi catch (error) {
        expect(error.esValidacion, isTrue);
        expect(error.campos['valor'], contains('debe estar entre'));
      }
    });

    test('al eliminar la última lectura la vista queda vacía', () async {
      final LecturasController controlador = LecturasController(
        _repositorio((http.Request peticion) async {
          if (peticion.method == 'DELETE') {
            return http.Response('', 204);
          }
          return _json(<Map<String, dynamic>>[_lecturaJson()]);
        }),
      );

      await controlador.cargar();
      await controlador.eliminar('L-1');

      expect(controlador.lecturas, isEmpty);
      expect(controlador.estado, EstadoVista.vacio);
    });
  });

  group('La pantalla ante una caída de la conexión', () {
    testWidgets(
      'muestra el estado de error con el mensaje propio y ofrece reintentar',
      (WidgetTester tester) async {
        bool conectado = false;
        final LecturasController controlador = LecturasController(
          _repositorio((http.Request peticion) async {
            if (!conectado) {
              throw http.ClientException('sin red');
            }
            return _json(<Map<String, dynamic>>[_lecturaJson()]);
          }),
        );

        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: ListenableBuilder(
                listenable: controlador,
                builder: (BuildContext contexto, Widget? hijo) => VistaConEstados<List<Lectura>>(
                  estado: controlador.estado,
                  datos: controlador.lecturas,
                  errorDeConexion: controlador.errorDeConexion,
                  mensajeError: controlador.mensajeError,
                  mensajeVacio: 'Registre la primera lectura para ver información aquí.',
                  alReintentar: () => controlador.cargar(),
                  alMostrarDatos: (BuildContext contexto, List<Lectura> lecturas) =>
                      Text('${lecturas.length} lecturas'),
                ),
              ),
            ),
          ),
        );

        // Estado inicial: la consulta está en curso.
        expect(find.byType(CircularProgressIndicator), findsOneWidget);

        // La conexión falla: el usuario ve por qué y qué puede hacer.
        await controlador.cargar();
        await tester.pump();
        expect(find.text('No se pudo conectar con el servidor'), findsOneWidget);
        expect(find.text('Reintentar'), findsOneWidget);

        // Vuelve la conexión y el reintento muestra los datos.
        conectado = true;
        await tester.tap(find.text('Reintentar'));
        await tester.pump();
        await tester.pump();
        expect(find.text('1 lecturas'), findsOneWidget);
        expect(find.text('No se pudo conectar con el servidor'), findsNothing);
      },
    );
  });
}
