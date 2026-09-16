import 'package:flutter/material.dart';

import 'alertas_screen.dart';

/// Pantalla de alertas como destino propio de navegación.
///
/// La lista de alertas se consulta desde el icono de notificaciones de la barra
/// superior, de modo que el menú inferior pueda dedicar su espacio al catálogo de
/// cultivos. La pantalla reutiliza el contenido de [AlertasScreen], que es el
/// mismo que se presentaba como pestaña del menú: un solo componente, dos formas
/// de llegar a él, sin duplicar la lógica.
class PantallaAlertas extends StatelessWidget {
  const PantallaAlertas({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F3F5),
      appBar: AppBar(
        backgroundColor: const Color(0xFF39B54A),
        foregroundColor: Colors.white,
        title: const Text(
          'Alertas',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
      body: const AlertasScreen(),
    );
  }
}
