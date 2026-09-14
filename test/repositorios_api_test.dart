import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:sigvach/models/api/modelos_api.dart';
import 'package:sigvach/repositories/api/alertas_api_repository.dart';
import 'package:sigvach/repositories/api/lecturas_api_repository.dart';
import 'package:sigvach/repositories/api/modulos_api_repository.dart';
import 'package:sigvach/repositories/api/perfiles_api_repository.dart';
import 'package:sigvach/repositories/api/rangos_api_repository.dart';
import 'package:sigvach/services/api_cliente.dart';
import 'package:sigvach/services/api_errores.dart';
import 'package:sigvach/utils/formato_fecha.dart';

/// Cliente que responde con el servicio simulado indicado.
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

/// Módulo de ejemplo tal como lo devuelve el servicio.
Map<String, dynamic> _moduloJson() => <String, dynamic>{
      'id': 'M-1',
      'nombre': 'Módulo 1',
      'tipo_cultivo': 'Lechuga',
      'perfil_id': 'P-1',
      'ubicacion': 'Invernadero Norte',
      'activo': true,
    };

/// Lectura de ejemplo tal como la devuelve el servicio.
Map<String, dynamic> _lecturaJson() => <String, dynamic>{
      'id': 'L-1',
      'modulo_id': 'M-1',
      'variable': 'ph',
      'valor': 6.1,
      'unidad': '',
      'origen': 'automatico',
      'timestamp': '2026-09-13T22:50:00+00:00',
      'estado_rango': 'dentro',
    };

void main() {
  group('ModulosApiRepository', () {
    test('lista los módulos y los convierte en modelos', () async {
      Uri? consultada;
      final ModulosApiRepository repositorio = ModulosApiRepository(
        _cliente((http.Request peticion) async {
          consultada = peticion.url;
          return _json(<Map<String, dynamic>>[_moduloJson()]);
        }),
      );

      final List<ModuloCultivo> modulos = await repositorio.listar();

      expect(consultada!.path, '/api/v1/modulos');
      expect(modulos, hasLength(1));
      expect(modulos.first.nombre, 'Módulo 1');
      expect(modulos.first.tipoCultivo, 'Lechuga');
      expect(modulos.first.perfilId, 'P-1');
      expect(modulos.first.ubicacion, 'Invernadero Norte');
      expect(modulos.first.activo, isTrue);
    });

    test('el filtro por estado viaja como parámetro de consulta', () async {
      Uri? consultada;
      final ModulosApiRepository repositorio = ModulosApiRepository(
        _cliente((http.Request peticion) async {
          consultada = peticion.url;
          return _json(<Map<String, dynamic>>[]);
        }),
      );

      await repositorio.listar(activo: true);

      expect(consultada!.queryParameters, <String, String>{'activo': 'true'});
    });

    test('al crear envía los nombres de campo del contrato', () async {
      String? cuerpo;
      final ModulosApiRepository repositorio = ModulosApiRepository(
        _cliente((http.Request peticion) async {
          cuerpo = peticion.body;
          return _json(_moduloJson(), estado: 201);
        }),
      );

      await repositorio.crear(
        nombre: 'Módulo 1',
        tipoCultivo: 'Lechuga',
        perfilId: 'P-1',
        ubicacion: 'Invernadero Norte',
      );

      final Map<String, dynamic> enviado =
          jsonDecode(cuerpo!) as Map<String, dynamic>;
      expect(enviado['tipo_cultivo'], 'Lechuga');
      expect(enviado['perfil_id'], 'P-1');
      expect(enviado.keys, isNot(contains('tipoCultivo')));
    });

    test('al modificar envía únicamente los campos indicados', () async {
      String? cuerpo;
      String? metodo;
      final ModulosApiRepository repositorio = ModulosApiRepository(
        _cliente((http.Request peticion) async {
          cuerpo = peticion.body;
          metodo = peticion.method;
          return _json(_moduloJson());
        }),
      );

      await repositorio.actualizar('M-1', activo: false);

      expect(metodo, 'PATCH');
      expect(jsonDecode(cuerpo!), <String, dynamic>{'activo': false});
    });

    test('sin campos para modificar no se consulta al servicio', () async {
      int llamadas = 0;
      final ModulosApiRepository repositorio = ModulosApiRepository(
        _cliente((http.Request peticion) async {
          llamadas++;
          return _json(_moduloJson());
        }),
      );

      await expectLater(
        repositorio.actualizar('M-1'),
        throwsA(isA<ArgumentError>()),
      );
      expect(llamadas, 0);
    });

    test('eliminar usa el método DELETE sobre el recurso', () async {
      String? metodo;
      String? camino;
      final ModulosApiRepository repositorio = ModulosApiRepository(
        _cliente((http.Request peticion) async {
          metodo = peticion.method;
          camino = peticion.url.path;
          return http.Response('', 204);
        }),
      );

      await repositorio.eliminar('M-1');

      expect(metodo, 'DELETE');
      expect(camino, '/api/v1/modulos/M-1');
    });

    test('el conflicto al eliminar un módulo con lecturas llega como ErrorApi', () async {
      final ModulosApiRepository repositorio = ModulosApiRepository(
        _cliente(
          (http.Request peticion) async => _json(
            <String, dynamic>{
              'codigo': 'conflicto',
              'mensaje': 'El módulo tiene lecturas registradas; desactívelo en lugar de eliminarlo.',
              'detalle': <String, dynamic>{},
            },
            estado: 409,
          ),
        ),
      );

      try {
        await repositorio.eliminar('M-1');
        fail('Se esperaba un ErrorApi de conflicto');
      } on ErrorApi catch (error) {
        expect(error.esConflicto, isTrue);
        expect(error.mensajeParaUsuario, contains('desactívelo'));
      }
    });
  });

  group('LecturasApiRepository', () {
    test('convierte la lectura, incluida su marca de tiempo y su estado', () async {
      final LecturasApiRepository repositorio = LecturasApiRepository(
        _cliente((http.Request peticion) async => _json(<Map<String, dynamic>>[_lecturaJson()])),
      );

      final List<Lectura> lecturas = await repositorio.listar();

      expect(lecturas, hasLength(1));
      final Lectura lectura = lecturas.first;
      expect(lectura.variable, 'ph');
      expect(lectura.valor, 6.1);
      expect(lectura.esManual, isFalse);
      expect(lectura.estadoRango, EstadoRango.dentro);
      expect(lectura.timestamp.toUtc().hour, 22);
      expect(lectura.timestamp.toUtc().day, 13);
    });

    test('los filtros de consulta se arman solo con lo indicado', () async {
      Uri? consultada;
      final LecturasApiRepository repositorio = LecturasApiRepository(
        _cliente((http.Request peticion) async {
          consultada = peticion.url;
          return _json(<Map<String, dynamic>>[]);
        }),
      );

      await repositorio.listar(
        moduloId: 'M-1',
        variable: 'ph',
        desde: DateTime.utc(2026, 9, 1),
        limite: 50,
      );

      expect(consultada!.path, '/api/v1/lecturas');
      expect(consultada!.queryParameters['modulo_id'], 'M-1');
      expect(consultada!.queryParameters['variable'], 'ph');
      expect(consultada!.queryParameters['limite'], '50');
      expect(consultada!.queryParameters['desde'], contains('2026-09-01'));
      expect(consultada!.queryParameters.containsKey('hasta'), isFalse);
    });

    test('el registro manual no declara el origen: lo fija el servidor', () async {
      String? cuerpo;
      String? camino;
      final LecturasApiRepository repositorio = LecturasApiRepository(
        _cliente((http.Request peticion) async {
          cuerpo = peticion.body;
          camino = peticion.url.path;
          return _json(<String, dynamic>{
            ..._lecturaJson(),
            'origen': 'manual',
            'estado_rango': 'alto',
          }, estado: 201);
        }),
      );

      final Lectura lectura = await repositorio.registrarManual(
        moduloId: 'M-1',
        variable: 'ph',
        valor: 7.4,
        observacion: 'medición con kit colorimétrico',
      );

      expect(camino, '/api/v1/lecturas/manual');
      final Map<String, dynamic> enviado =
          jsonDecode(cuerpo!) as Map<String, dynamic>;
      expect(enviado.containsKey('origen'), isFalse);
      expect(enviado['valor'], 7.4);
      expect(enviado['observacion'], 'medición con kit colorimétrico');
      expect(lectura.esManual, isTrue);
      expect(lectura.estadoRango, EstadoRango.alto);
    });

    test('el resumen devuelve promedio, máximo y mínimo', () async {
      final LecturasApiRepository repositorio = LecturasApiRepository(
        _cliente(
          (http.Request peticion) async => _json(<Map<String, dynamic>>[
            <String, dynamic>{
              'variable': 'ph',
              'unidad': '',
              'cantidad': 3,
              'promedio': 6.0,
              'maximo': 6.6,
              'minimo': 5.4,
            },
          ]),
        ),
      );

      final List<ResumenVariable> resumen = await repositorio.resumen();

      expect(resumen, hasLength(1));
      expect(resumen.first.cantidad, 3);
      expect(resumen.first.promedio, 6.0);
      expect(resumen.first.nombreVariable, 'pH');
    });

    test('la exportación viaja al recurso de exportaciones y devuelve el archivo', () async {
      String? camino;
      final LecturasApiRepository repositorio = LecturasApiRepository(
        _cliente((http.Request peticion) async {
          camino = peticion.url.path;
          return http.Response.bytes(
            utf8.encode('id,modulo_id,variable\r\nL-1,M-1,ph\r\n'),
            200,
            headers: <String, String>{'content-type': 'text/csv; charset=utf-8'},
          );
        }),
      );

      final List<int> bytes = await repositorio.exportarCsv(moduloId: 'M-1');

      expect(camino, '/api/v1/exportaciones/lecturas.csv');
      expect(utf8.decode(bytes), contains('L-1,M-1,ph'));
    });

    test('el rechazo por validación llega con el campo señalado', () async {
      final LecturasApiRepository repositorio = LecturasApiRepository(
        _cliente(
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
        await repositorio.registrarManual(moduloId: 'M-1', variable: 'ph', valor: 99);
        fail('Se esperaba un ErrorApi de validación');
      } on ErrorApi catch (error) {
        expect(error.esValidacion, isTrue);
        expect(error.campos['valor'], contains('debe estar entre'));
      }
    });
  });

  group('RangosApiRepository', () {
    test('crea el rango con los nombres de campo del contrato', () async {
      String? cuerpo;
      final RangosApiRepository repositorio = RangosApiRepository(
        _cliente((http.Request peticion) async {
          cuerpo = peticion.body;
          return _json(<String, dynamic>{
            'id': 'R-1',
            'perfil_id': 'P-1',
            'variable': 'ph',
            'minimo': 5.5,
            'maximo': 6.5,
            'unidad': '',
          }, estado: 201);
        }),
      );

      final RangoReferencia rango = await repositorio.crear(
        perfilId: 'P-1',
        variable: 'ph',
        minimo: 5.5,
        maximo: 6.5,
      );

      expect(jsonDecode(cuerpo!), <String, dynamic>{
        'perfil_id': 'P-1',
        'variable': 'ph',
        'minimo': 5.5,
        'maximo': 6.5,
      });
      expect(rango.nombreVariable, 'pH');
    });

    test('sin límites que modificar no se consulta al servicio', () async {
      final RangosApiRepository repositorio = RangosApiRepository(
        _cliente((http.Request peticion) async => _json(<String, dynamic>{})),
      );

      await expectLater(
        repositorio.actualizar('R-1'),
        throwsA(isA<ArgumentError>()),
      );
    });

    test('el rango duplicado en el perfil se informa como conflicto', () async {
      final RangosApiRepository repositorio = RangosApiRepository(
        _cliente(
          (http.Request peticion) async => _json(
            <String, dynamic>{
              'codigo': 'conflicto',
              'mensaje': 'El perfil ya tiene un rango definido para la variable ph.',
              'detalle': <String, dynamic>{},
            },
            estado: 409,
          ),
        ),
      );

      try {
        await repositorio.crear(perfilId: 'P-1', variable: 'ph', minimo: 1, maximo: 2);
        fail('Se esperaba un ErrorApi de conflicto');
      } on ErrorApi catch (error) {
        expect(error.esConflicto, isTrue);
      }
    });
  });

  group('AlertasApiRepository', () {
    test('convierte la alerta con la referencia a su lectura', () async {
      final AlertasApiRepository repositorio = AlertasApiRepository(
        _cliente(
          (http.Request peticion) async => _json(<Map<String, dynamic>>[
            <String, dynamic>{
              'id': 'A-1',
              'lectura_id': 'L-1',
              'modulo_id': 'M-1',
              'variable': 'ph',
              'valor': 7.4,
              'unidad': '',
              'rango_minimo': 5.5,
              'rango_maximo': 6.5,
              'estado': 'activa',
              'desviacion': 'alto',
              'timestamp': '2026-09-13T22:50:00+00:00',
            },
          ]),
        ),
      );

      final List<AlertaServidor> alertas = await repositorio.listar(estado: 'activa');

      expect(alertas, hasLength(1));
      expect(alertas.first.lecturaId, 'L-1');
      expect(alertas.first.estaActiva, isTrue);
      expect(alertas.first.nombreVariable, 'pH');
      expect(alertas.first.rangoMaximo, 6.5);
    });

    test('atender una alerta envía el estado y la observación', () async {
      String? cuerpo;
      final AlertasApiRepository repositorio = AlertasApiRepository(
        _cliente((http.Request peticion) async {
          cuerpo = peticion.body;
          return _json(<String, dynamic>{
            'id': 'A-1',
            'lectura_id': 'L-1',
            'modulo_id': 'M-1',
            'variable': 'ph',
            'valor': 7.4,
            'rango_minimo': 5.5,
            'rango_maximo': 6.5,
            'estado': 'atendida',
            'timestamp': '2026-09-13T22:50:00+00:00',
          });
        }),
      );

      final AlertaServidor alerta =
          await repositorio.marcarAtendida('A-1', observacion: 'solución ajustada');

      expect(jsonDecode(cuerpo!), <String, dynamic>{
        'estado': 'atendida',
        'observacion': 'solución ajustada',
      });
      expect(alerta.estaActiva, isFalse);
    });
  });

  group('PerfilesApiRepository', () {
    test('lista y convierte los perfiles de cultivo', () async {
      final PerfilesApiRepository repositorio = PerfilesApiRepository(
        _cliente(
          (http.Request peticion) async => _json(<Map<String, dynamic>>[
            <String, dynamic>{
              'id': 'P-1',
              'nombre': 'Lechuga',
              'descripcion': 'Perfil predefinido',
              'predefinido': true,
            },
          ]),
        ),
      );

      final List<PerfilCultivo> perfiles = await repositorio.listar();

      expect(perfiles, hasLength(1));
      expect(perfiles.first.nombre, 'Lechuga');
      expect(perfiles.first.predefinido, isTrue);
    });
  });

  group('Modelos del contrato', () {
    test('reconoce los estados fuera de rango', () {
      expect(EstadoRango.esFueraDeRango(EstadoRango.alto), isTrue);
      expect(EstadoRango.esFueraDeRango(EstadoRango.bajo), isTrue);
      expect(EstadoRango.esFueraDeRango(EstadoRango.dentro), isFalse);
      expect(EstadoRango.esFueraDeRango(EstadoRango.sinRango), isFalse);
      expect(EstadoRango.etiqueta(EstadoRango.alto), 'Por encima del rango');
    });

    test('traduce los códigos de variable a nombres presentables', () {
      expect(nombreDeVariable('temp_solucion'), 'Temperatura de la solución');
      expect(unidadDeVariable('humedad'), '%');
      expect(nombreDeVariable('desconocida'), 'desconocida');
    });

    test('un valor no numérico se informa como error de contrato', () {
      expect(
        () => Lectura.fromJson(<String, dynamic>{
          'id': 'L-1',
          'modulo_id': 'M-1',
          'variable': 'ph',
          'valor': 'seis',
          'timestamp': '2026-09-13T22:50:00Z',
        }),
        throwsA(isA<ErrorDeContrato>()),
      );
    });

    test('una marca de tiempo inválida se informa como error de contrato', () {
      expect(
        () => Lectura.fromJson(<String, dynamic>{
          'id': 'L-1',
          'modulo_id': 'M-1',
          'variable': 'ph',
          'valor': 6.1,
          'timestamp': 'ayer',
        }),
        throwsA(isA<ErrorDeContrato>()),
      );
    });
  });

  group('Formato de fechas', () {
    test('presenta la fecha y la hora en el formato de la interfaz', () {
      expect(formatearFechaHora(DateTime(2026, 9, 13, 15, 5)), '13/09/2026 03:05 p. m.');
      expect(formatearFechaHora(DateTime(2026, 9, 13, 0, 30)), '13/09/2026 12:30 a. m.');
      expect(formatearFecha(DateTime(2026, 9, 13)), '13/09/2026');
      expect(formatearHora(DateTime(2026, 9, 13, 12, 0)), '12:00 p. m.');
    });

    test('no agrega decimales innecesarios a los valores', () {
      expect(formatearValor(6), '6');
      expect(formatearValor(6.24), '6.2');
    });
  });
}
