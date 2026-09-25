import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sigvach/widgets/encabezado_del_menu.dart';

/// Envuelve el encabezado en el mínimo necesario para presentarlo en una prueba.
Widget _envolver(Widget hijo) => MaterialApp(home: Scaffold(body: hijo));

void main() {
  group('Encabezado del menú lateral', () {
    testWidgets('saluda con el nombre de la cuenta y muestra su rol', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        _envolver(
          const EncabezadoDeMenu(
            nombre: 'Mateo Santos',
            etiquetaRol: 'Administrador',
          ),
        ),
      );

      expect(find.text('Hola, Mateo Santos'), findsOneWidget);
      expect(find.text('Administrador'), findsOneWidget);
    });

    testWidgets('presenta el rol de operación tal como llega del catálogo', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        _envolver(
          const EncabezadoDeMenu(nombre: 'Ana Quispe', etiquetaRol: 'Operador'),
        ),
      );

      expect(find.text('Hola, Ana Quispe'), findsOneWidget);
      expect(find.text('Operador'), findsOneWidget);
      // El widget no clasifica por su cuenta: si la etiqueta es de operación,
      // la de administración no aparece.
      expect(find.text('Administrador'), findsNothing);
    });

    testWidgets('mientras el rol no se conoce no supone ninguno', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        _envolver(const EncabezadoDeMenu(nombre: 'Mateo Santos')),
      );

      expect(find.text('Hola, Mateo Santos'), findsOneWidget);
      expect(find.text('Administrador'), findsNothing);
      expect(find.text('Operador'), findsNothing);
      expect(find.text('Sin rol'), findsNothing);
    });
  });
}
