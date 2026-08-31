import 'package:flutter/material.dart';

/// Pantalla genérica para las opciones de Ajustes que aún no tienen
/// desarrollo completo (Notificaciones, Dispositivos, Usuarios, Seguridad,
/// Acerca de SIGVACH).
class OpcionesScreen extends StatelessWidget {
  const OpcionesScreen({
    super.key,
    required this.titulo,
    required this.icono,
    required this.descripcion,
  });

  final String titulo;
  final IconData icono;
  final String descripcion;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(titulo)),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              Icon(icono, size: 72, color: const Color(0xFF39B54A)),
              const SizedBox(height: 16),
              Text(
                titulo,
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 10),
              Text(
                descripcion,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.grey, fontSize: 14),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
