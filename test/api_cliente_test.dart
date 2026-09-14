import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:sigvach/config/api_config.dart';
import 'package:sigvach/services/api_cliente.dart';
import 'package:sigvach/services/api_errores.dart';

/// Construye un cliente con un servicio simulado.
ApiCliente _cliente(
  Future<http.Response> Function(http.Request peticion) responder, {
  String? token = 'token-de-prueba',
  String baseUrl = 'https://api.ejemplo.test',
}) {
  return ApiCliente(
    cliente: MockClient(responder),
    obtenerToken: () async => token,
    baseUrl: baseUrl,
    espera: const Duration(seconds: 2),
  );
}

/// Respuesta JSON con el cuerpo ya codificado en UTF-8.
http.Response _json(Object cuerpo, {int estado = 200}) {
  return http.Response.bytes(
    utf8.encode(jsonEncode(cuerpo)),
    estado,
    headers: <String, String>{'content-type': 'application/json'},
  );
}

void main() {
  group('ApiConfig', () {
    test('arma las rutas con el prefijo de versión del contrato', () {
      expect(ApiConfig.ruta('lecturas'), '/api/v1/lecturas');
      expect(ApiConfig.ruta('/lecturas'), '/api/v1/lecturas');
    });
  });

  group('ApiCliente', () {
    test('adjunta el token de identidad en cada petición', () async {
      String? autorizacion;
      final ApiCliente cliente = _cliente((http.Request peticion) async {
        autorizacion = peticion.headers['Authorization'];
        return _json(<String, dynamic>{'id': 'M-1', 'nombre': 'Módulo 1'});
      });

      final Map<String, dynamic> modulo = await cliente.obtenerMapa('/api/v1/modulos/M-1');

      expect(autorizacion, 'Bearer token-de-prueba');
      expect(modulo['nombre'], 'Módulo 1');
    });

    test('sin sesión iniciada falla antes de salir a la red', () async {
      int llamadas = 0;
      final ApiCliente cliente = _cliente(
        (http.Request peticion) async {
          llamadas++;
          return _json(<dynamic>[]);
        },
        token: null,
      );

      try {
        await cliente.obtenerLista('/api/v1/lecturas');
        fail('Se esperaba un ErrorApi por falta de sesión');
      } on ErrorApi catch (error) {
        expect(error.esNoAutenticado, isTrue);
        expect(error.codigo, 'no_autenticado');
      }
      expect(llamadas, 0, reason: 'No debe intentarse la petición sin token');
    });

    test('reconoce el 401 del servicio como sesión no válida', () async {
      final ApiCliente cliente = _cliente(
        (http.Request peticion) async => _json(
          <String, dynamic>{
            'codigo': 'no_autenticado',
            'mensaje': 'El token de identidad no es válido o expiró.',
            'detalle': <String, dynamic>{},
          },
          estado: 401,
        ),
      );

      try {
        await cliente.obtenerLista('/api/v1/lecturas');
        fail('Se esperaba un ErrorApi');
      } on ErrorApi catch (error) {
        expect(error.esNoAutenticado, isTrue);
        expect(error.mensajeParaUsuario, 'El token de identidad no es válido o expiró.');
      }
    });

    test('traduce el 422 e informa el campo rechazado', () async {
      final ApiCliente cliente = _cliente(
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
      );

      try {
        await cliente.crear(
          '/api/v1/lecturas/manual',
          <String, dynamic>{'modulo_id': 'M-1', 'variable': 'ph', 'valor': 99},
        );
        fail('Se esperaba un ErrorApi de validación');
      } on ErrorApi catch (error) {
        expect(error.esValidacion, isTrue);
        expect(error.codigo, 'validacion_rechazada');
        expect(error.campos['valor'], contains('debe estar entre'));
      }
    });

    test('reconoce el 403 como falta de permiso', () async {
      final ApiCliente cliente = _cliente(
        (http.Request peticion) async => _json(
          <String, dynamic>{
            'codigo': 'sin_permiso',
            'mensaje': 'La operación requiere el rol de administrador.',
            'detalle': <String, dynamic>{'rol_actual': 'usuario'},
          },
          estado: 403,
        ),
      );

      try {
        await cliente.crear('/api/v1/modulos', <String, dynamic>{'nombre': 'Módulo 3'});
        fail('Se esperaba un ErrorApi');
      } on ErrorApi catch (error) {
        expect(error.esSinPermiso, isTrue);
        expect(error.mensajeParaUsuario, contains('administrador'));
      }
    });

    test('un fallo de conexión se informa como ErrorConexion y no como rechazo', () async {
      final ApiCliente cliente = _cliente(
        (http.Request peticion) async => throw http.ClientException('sin red'),
      );

      expect(
        cliente.obtenerLista('/api/v1/lecturas'),
        throwsA(isA<ErrorConexion>()),
      );
    });

    test('un tiempo de espera agotado se informa como ErrorConexion', () async {
      final ApiCliente cliente = ApiCliente(
        cliente: MockClient((http.Request peticion) async {
          await Future<void>.delayed(const Duration(milliseconds: 300));
          return _json(<dynamic>[]);
        }),
        obtenerToken: () async => 'token-de-prueba',
        baseUrl: 'https://api.ejemplo.test',
        espera: const Duration(milliseconds: 30),
      );

      expect(
        cliente.obtenerLista('/api/v1/lecturas'),
        throwsA(isA<ErrorConexion>()),
      );
    });

    test('decodifica los acentos en UTF-8 aunque el servicio no declare el juego de caracteres', () async {
      final ApiCliente cliente = _cliente(
        (http.Request peticion) async => http.Response.bytes(
          utf8.encode(
            jsonEncode(<String, dynamic>{
              'nombre': 'Módulo de lechuga',
              'unidad': '°C',
              'variable': 'Temperatura de la solución',
            }),
          ),
          200,
          headers: <String, String>{'content-type': 'application/json'},
        ),
      );

      final Map<String, dynamic> datos = await cliente.obtenerMapa('/api/v1/modulos/M-1');

      expect(datos['nombre'], 'Módulo de lechuga');
      expect(datos['unidad'], '°C');
      expect(datos['variable'], 'Temperatura de la solución');
    });

    test('arma la consulta con los filtros indicados y omite los vacíos', () async {
      Uri? consultada;
      final ApiCliente cliente = _cliente((http.Request peticion) async {
        consultada = peticion.url;
        return _json(<dynamic>[]);
      });

      await cliente.obtenerLista(
        '/api/v1/lecturas',
        parametros: <String, String>{
          'variable': 'ph',
          'desde': '',
          'limite': '50',
        },
      );

      expect(consultada, isNotNull);
      expect(consultada!.path, '/api/v1/lecturas');
      expect(consultada!.queryParameters, <String, String>{'variable': 'ph', 'limite': '50'});
    });

    test('crear envía el cuerpo en JSON', () async {
      String? tipoDeContenido;
      String? cuerpo;
      final ApiCliente cliente = _cliente((http.Request peticion) async {
        tipoDeContenido = peticion.headers['Content-Type'];
        cuerpo = peticion.body;
        return _json(<String, dynamic>{'id': 'L-1'}, estado: 201);
      });

      await cliente.crear(
        '/api/v1/lecturas/manual',
        <String, dynamic>{'modulo_id': 'M-1', 'variable': 'ph', 'valor': 6.1},
      );

      expect(tipoDeContenido, contains('application/json'));
      expect(jsonDecode(cuerpo!), containsPair('variable', 'ph'));
    });

    test('eliminar tolera una respuesta sin cuerpo', () async {
      final ApiCliente cliente = _cliente(
        (http.Request peticion) async => http.Response('', 204),
      );

      await cliente.eliminar('/api/v1/lecturas/L-1');
    });

    test('obtenerBytes devuelve el archivo de exportación', () async {
      final ApiCliente cliente = _cliente(
        (http.Request peticion) async => http.Response.bytes(
          utf8.encode('id,modulo_id,variable\r\nL-1,M-1,ph\r\n'),
          200,
          headers: <String, String>{'content-type': 'text/csv; charset=utf-8'},
        ),
      );

      final List<int> bytes =
          await cliente.obtenerBytes('/api/v1/exportaciones/lecturas.csv');

      expect(utf8.decode(bytes), contains('id,modulo_id,variable'));
    });

    test('una respuesta de error que no es JSON no rompe la interpretación', () async {
      final ApiCliente cliente = _cliente(
        (http.Request peticion) async => http.Response('<html>Bad Gateway</html>', 502),
      );

      try {
        await cliente.obtenerLista('/api/v1/lecturas');
        fail('Se esperaba un ErrorApi');
      } on ErrorApi catch (error) {
        expect(error.estado, 502);
        expect(error.codigo, 'error_desconocido');
        expect(error.mensajeParaUsuario, contains('502'));
      }
    });

    test('si el proveedor de identidad falla, se informa como fallo de conexión', () async {
      int llamadas = 0;
      final ApiCliente cliente = ApiCliente(
        cliente: MockClient((http.Request peticion) async {
          llamadas++;
          return _json(<dynamic>[]);
        }),
        obtenerToken: () async => throw StateError('El proveedor de identidad no está disponible'),
        baseUrl: 'https://api.ejemplo.test',
        espera: const Duration(seconds: 2),
      );

      expect(
        cliente.obtenerLista('/api/v1/lecturas'),
        throwsA(isA<ErrorConexion>()),
      );
      expect(llamadas, 0, reason: 'Sin sesión no debe intentarse la petición');
    });

    test('una respuesta con forma inesperada se informa con claridad', () async {
      final ApiCliente cliente = _cliente(
        (http.Request peticion) async => _json(<String, dynamic>{'id': 'M-1'}),
      );

      try {
        await cliente.obtenerLista('/api/v1/lecturas');
        fail('Se esperaba un ErrorApi por forma inesperada');
      } on ErrorApi catch (error) {
        expect(error.codigo, 'respuesta_inesperada');
      }
    });
  });
}
