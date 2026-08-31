import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/preferences_controller.dart';
import '../../models/alerta.dart';

/// Pantalla 4.1 — Detalle de una alerta.
class AlertaDetalleScreen extends StatelessWidget {
  const AlertaDetalleScreen({super.key, required this.alerta});

  final Alerta alerta;

  @override
  Widget build(BuildContext context) {
    final color = alerta.critica ? Colors.red : const Color(0xFF2E7D32);
    final icono = alerta.critica
        ? Icons.warning_amber_rounded
        : Icons.check_circle_outline;

    return Scaffold(
      appBar: AppBar(title: const Text('Detalle de alerta')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: <Widget>[
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: color.withValues(alpha: 0.4)),
            ),
            child: Column(
              children: <Widget>[
                Icon(icono, color: color, size: 44),
                const SizedBox(height: 12),
                Text(
                  alerta.titulo,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: color,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                Text(alerta.nivelActual, style: const TextStyle(fontSize: 15)),
                Text(
                  alerta.rangoPermitido,
                  style: const TextStyle(fontSize: 15),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              children: <Widget>[
                Row(
                  children: <Widget>[
                    const Icon(Icons.event, color: Colors.grey, size: 20),
                    const SizedBox(width: 10),
                    const Text('Fecha', style: TextStyle(fontSize: 14)),
                    const Spacer(),
                    Text(
                      alerta.fecha,
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
                const Divider(),
                Row(
                  children: <Widget>[
                    const Icon(
                      Icons.info_outline,
                      color: Colors.grey,
                      size: 20,
                    ),
                    const SizedBox(width: 10),
                    const Text('Estado', style: TextStyle(fontSize: 14)),
                    const Spacer(),
                    Text(
                      alerta.estado,
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                        color: color,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          if (alerta.estado == 'Activa')
            FilledButton.icon(
              onPressed: () async {
                await context
                    .read<PreferencesController>()
                    .marcarAlertaResuelta(alerta.id);
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Alerta marcada como resuelta'),
                    ),
                  );
                  Navigator.of(context).pop();
                }
              },
              icon: const Icon(Icons.done),
              label: const Text('Marcar como resuelta'),
              style: FilledButton.styleFrom(
                backgroundColor: const Color(0xFF39B54A),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
            ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Historial completo disponible próximamente'),
                ),
              );
            },
            icon: const Icon(Icons.history),
            label: const Text('Ver historial'),
            style: OutlinedButton.styleFrom(
              foregroundColor: const Color(0xFF39B54A),
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
          ),
        ],
      ),
    );
  }
}
