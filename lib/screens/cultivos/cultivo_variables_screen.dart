import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/preferences_controller.dart';
import '../../models/cultivo.dart';

/// Pantalla 3.2 — Variables del cultivo.
class CultivoVariablesScreen extends StatelessWidget {
  const CultivoVariablesScreen({super.key, required this.cultivo});

  final Cultivo cultivo;

  static String _fmt(double value) {
    return value == value.roundToDouble()
        ? value.toStringAsFixed(0)
        : value.toStringAsFixed(1);
  }

  @override
  Widget build(BuildContext context) {
    final preferences = context.watch<PreferencesController>();

    return Scaffold(
      appBar: AppBar(title: Text('${cultivo.nombre} — Variables')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: <Widget>[
          _VariableTile(
            icon: Icons.thermostat_outlined,
            color: const Color(0xFFE65100),
            label: 'Temperatura',
            value: '${_fmt(preferences.temperature)} °C',
            detalle: 'Normal',
          ),
          _VariableTile(
            icon: Icons.water_drop_outlined,
            color: const Color(0xFF1565C0),
            label: 'Humedad',
            value: '${_fmt(preferences.humidity)} %',
            detalle: 'Normal',
          ),
          _VariableTile(
            icon: Icons.science_outlined,
            color: const Color(0xFFC62828),
            label: 'pH',
            value: _fmt(preferences.ph),
            detalle: 'Rango 5.5 - 6.5',
          ),
          _VariableTile(
            icon: Icons.eco_outlined,
            color: const Color(0xFF2E7D32),
            label: 'TDS',
            value: '${_fmt(preferences.tds)} ppm',
            detalle: 'Normal',
          ),
          _VariableTile(
            icon: Icons.water_drop_outlined,
            color: const Color(0xFF1565C0),
            label: 'Nivel de agua',
            value: '${_fmt(preferences.waterLevel)} %',
            detalle: 'Normal',
          ),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Historial disponible próximamente'),
                ),
              );
            },
            icon: const Icon(Icons.history),
            label: const Text('Ver historial'),
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFF39B54A),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
          ),
        ],
      ),
    );
  }
}

class _VariableTile extends StatelessWidget {
  const _VariableTile({
    required this.icon,
    required this.color,
    required this.label,
    required this.value,
    required this.detalle,
  });

  final IconData icon;
  final Color color;
  final String label;
  final String value;
  final String detalle;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.green.withValues(alpha: 0.25)),
      ),
      child: Row(
        children: <Widget>[
          Icon(icon, color: color, size: 26),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text(
                  label,
                  style: const TextStyle(color: Colors.grey, fontSize: 13),
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: TextStyle(
                    color: color,
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
          ),
          Text(
            detalle,
            style: const TextStyle(
              color: Color(0xFF2E7D32),
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
