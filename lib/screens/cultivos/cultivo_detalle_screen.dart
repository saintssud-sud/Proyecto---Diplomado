import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/preferences_controller.dart';
import '../../models/cultivo.dart';
import 'cultivo_variables_screen.dart';

/// Pantalla 3.1 — Detalle de un cultivo.
class CultivoDetalleScreen extends StatelessWidget {
  const CultivoDetalleScreen({super.key, required this.cultivo});

  final Cultivo cultivo;

  Future<void> _confirmarEliminar(BuildContext context) async {
    final eliminado = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Eliminar cultivo'),
        content: Text(
          '¿Seguro que deseas eliminar "${cultivo.nombre}"? Esta acción no se puede deshacer.',
        ),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, true),
            style: FilledButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Eliminar'),
          ),
        ],
      ),
    );

    if (eliminado == true && context.mounted) {
      await context.read<PreferencesController>().removeCultivo(cultivo.id);
      if (context.mounted) {
        Navigator.of(context).pop();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Detalle de cultivo')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: <Widget>[
          // Cabecera con imagen/nombre/estado.
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFF39B54A),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              children: <Widget>[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: const Icon(
                    Icons.eco_outlined,
                    color: Color(0xFF2E7D32),
                    size: 34,
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Text(
                        cultivo.nombre,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        cultivo.area,
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    cultivo.estado,
                    style: const TextStyle(
                      color: Color(0xFF2E7D32),
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          // Información del cultivo.
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              children: <Widget>[
                _DetalleFila(
                  icon: Icons.location_on_outlined,
                  label: 'Área',
                  value: cultivo.area,
                ),
                const Divider(),
                _DetalleFila(
                  icon: Icons.event,
                  label: 'Fecha de inicio',
                  value: cultivo.fechaInicio,
                ),
                const Divider(),
                _DetalleFila(
                  icon: Icons.shopping_basket_outlined,
                  label: 'Cantidad',
                  value: '${cultivo.cantidad} plantas',
                ),
                const Divider(),
                _DetalleFila(
                  icon: Icons.grid_view,
                  label: 'Módulo',
                  value: '${cultivo.modulo}',
                ),
                const Divider(),
                // Progreso.
                Row(
                  children: <Widget>[
                    const Icon(Icons.trending_up, color: Colors.grey),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Text('Progreso', style: TextStyle(fontSize: 14)),
                    ),
                    Text(
                      '${cultivo.progreso} %',
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF2E7D32),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(6),
                  child: LinearProgressIndicator(
                    value: cultivo.progreso / 100,
                    minHeight: 8,
                    backgroundColor: Colors.green.withValues(alpha: 0.15),
                    color: const Color(0xFF2E7D32),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: () {
              Navigator.push<void>(
                context,
                MaterialPageRoute<void>(
                  builder: (routeContext) =>
                      CultivoVariablesScreen(cultivo: cultivo),
                ),
              );
            },
            icon: const Icon(Icons.science_outlined),
            label: const Text('Ver variables'),
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFF39B54A),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: () => _confirmarEliminar(context),
            icon: const Icon(Icons.delete_outline),
            label: const Text('Eliminar cultivo'),
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.red,
              side: const BorderSide(color: Colors.red),
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
          ),
        ],
      ),
    );
  }
}

class _DetalleFila extends StatelessWidget {
  const _DetalleFila({
    required this.icon,
    required this.label,
    required this.value,
  });

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: <Widget>[
        Icon(icon, color: Colors.grey, size: 20),
        const SizedBox(width: 12),
        Expanded(child: Text(label, style: const TextStyle(fontSize: 14))),
        Text(value, style: const TextStyle(fontWeight: FontWeight.w600)),
      ],
    );
  }
}
