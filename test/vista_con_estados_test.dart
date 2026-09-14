import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sigvach/widgets/vista_con_estados.dart';

/// Envuelve la vista en el mínimo necesario para poder presentarla en una prueba.
Widget _envolver(Widget hijo) => MaterialApp(home: Scaffold(body: hijo));

/// Vista de prueba que presenta la cantidad de elementos recibidos.
Widget _vistaDeEjemplo({
  required EstadoVista estado,
  List<String>? datos,
  String? mensajeError,
  bool errorDeConexion = false,
  VoidCallback? alReintentar,
}) {
  return VistaConEstados<List<String>>(
    estado: estado,
    datos: datos,
    errorDeConexion: errorDeConexion,
    mensajeError: mensajeError,
    alReintentar: alReintentar,
    mensajeVacio: 'Registre la primera lectura del módulo para ver información aquí.',
    alMostrarDatos: (BuildContext contexto, List<String> valores) =>
        Text('${valores.length} elementos'),
  );
}

void main() {
  group('Estado de carga', () {
    testWidgets('informa que la información está en camino', (WidgetTester tester) async {
      await tester.pumpWidget(_envolver(_vistaDeEjemplo(estado: EstadoVista.cargando)));

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('Cargando información…'), findsOneWidget);
    });
  });

  group('Estado con datos', () {
    testWidgets('presenta el contenido con los datos recibidos', (WidgetTester tester) async {
      await tester.pumpWidget(
        _envolver(
          _vistaDeEjemplo(
            estado: EstadoVista.conDatos,
            datos: <String>['uno', 'dos', 'tres'],
          ),
        ),
      );

      expect(find.text('3 elementos'), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });

    testWidgets(
      'si el estado dice con datos pero no llegaron, lo informa en lugar de fallar',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          _envolver(_vistaDeEjemplo(estado: EstadoVista.conDatos)),
        );

        expect(find.text('Sin información'), findsOneWidget);
      },
    );
  });

  group('Estado vacío', () {
    testWidgets('explica qué hacer para que haya información', (WidgetTester tester) async {
      await tester.pumpWidget(_envolver(_vistaDeEjemplo(estado: EstadoVista.vacio)));

      expect(find.text('Todavía no hay información'), findsOneWidget);
      expect(
        find.text('Registre la primera lectura del módulo para ver información aquí.'),
        findsOneWidget,
      );
    });

    testWidgets('con acción de reintento ofrece actualizar', (WidgetTester tester) async {
      int intentos = 0;
      await tester.pumpWidget(
        _envolver(
          _vistaDeEjemplo(
            estado: EstadoVista.vacio,
            alReintentar: () => intentos++,
          ),
        ),
      );

      expect(find.text('Actualizar'), findsOneWidget);
      await tester.tap(find.text('Actualizar'));
      expect(intentos, 1);
    });

    testWidgets('sin acción de reintento no ofrece botón', (WidgetTester tester) async {
      await tester.pumpWidget(_envolver(_vistaDeEjemplo(estado: EstadoVista.vacio)));

      expect(find.byType(FilledButton), findsNothing);
    });
  });

  group('Estado de error', () {
    testWidgets(
      'un fallo de conexión se presenta como tal e indica revisar la conexión',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          _envolver(
            _vistaDeEjemplo(
              estado: EstadoVista.error,
              errorDeConexion: true,
              mensajeError:
                  'No se pudo comunicar con el servidor. Revise la conexión e intente nuevamente.',
              alReintentar: () {},
            ),
          ),
        );

        expect(find.text('No se pudo conectar con el servidor'), findsOneWidget);
        expect(
          find.text(
            'No se pudo comunicar con el servidor. Revise la conexión e intente nuevamente.',
          ),
          findsOneWidget,
        );
        expect(find.text('Revise la conexión e intente nuevamente.'), findsOneWidget);
        expect(find.text('Reintentar'), findsOneWidget);
      },
    );

    testWidgets(
      'un rechazo del servidor se presenta distinto: no se le pide revisar la conexión',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          _envolver(
            _vistaDeEjemplo(
              estado: EstadoVista.error,
              errorDeConexion: false,
              mensajeError: 'La operación requiere el rol de administrador.',
            ),
          ),
        );

        expect(find.text('La operación no pudo completarse'), findsOneWidget);
        expect(find.text('La operación requiere el rol de administrador.'), findsOneWidget);
        expect(find.text('Revise la conexión e intente nuevamente.'), findsNothing);
        expect(find.textContaining('comuníquese con el administrador'), findsOneWidget);
      },
    );

    testWidgets('al reintentar se vuelve a intentar la operación', (WidgetTester tester) async {
      int intentos = 0;
      await tester.pumpWidget(
        _envolver(
          _vistaDeEjemplo(
            estado: EstadoVista.error,
            errorDeConexion: true,
            alReintentar: () => intentos++,
          ),
        ),
      );

      await tester.tap(find.text('Reintentar'));
      expect(intentos, 1);
    });

    testWidgets('sin mensaje del servicio usa uno según el tipo de fallo', (WidgetTester tester) async {
      await tester.pumpWidget(
        _envolver(_vistaDeEjemplo(estado: EstadoVista.error, errorDeConexion: true)),
      );

      expect(find.text('La petición no llegó al servidor.'), findsOneWidget);
    });
  });
}
