import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/preferences_controller.dart';
import '../../models/variable_rango.dart';
import 'rango_optimo_screen.dart';

/// Pantalla 2.1 — Detalle de una variable.
class VariableDetalleScreen extends StatelessWidget {
  const VariableDetalleScreen({super.key, required this.nombre});

  final String nombre;

  IconData get _icono {
    switch (nombre) {
      case 'Temperatura':
        return Icons.thermostat_outlined;
      case 'Humedad':
        return Icons.water_drop_outlined;
      case 'pH':
        return Icons.science_outlined;
      case 'TDS':
        return Icons.eco_outlined;
      default:
        return Icons.water_drop_outlined;
    }
  }

  Color get _color {
    switch (nombre) {
      case 'Temperatura':
        return const Color(0xFFE65100);
      case 'Humedad':
        return const Color(0xFF1565C0);
      case 'pH':
        return const Color(0xFFC62828);
      case 'TDS':
        return const Color(0xFF2E7D32);
      default:
        return const Color(0xFF1565C0);
    }
  }

  double _valor(PreferencesController p) {
    switch (nombre) {
      case 'Temperatura':
        return p.temperature;
      case 'Humedad':
        return p.humidity;
      case 'pH':
        return p.ph;
      case 'TDS':
        return p.tds;
      default:
        return p.waterLevel;
    }
  }

  String get _unidad {
    switch (nombre) {
      case 'Temperatura':
        return '°C';
      case 'Humedad':
        return '%';
      case 'pH':
        return '';
      case 'TDS':
        return 'ppm';
      default:
        return '%';
    }
  }

  VariableRango? _rango(PreferencesController p) {
    for (final r in p.rangos) {
      if (r.variable == nombre) return r;
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final preferences = context.watch<PreferencesController>();
    final valor = _valor(preferences);
    final rango = _rango(preferences);
    final fuera =
        rango != null && (valor < rango.minimo || valor > rango.maximo);
    final estado = fuera ? 'Fuera de rango' : 'Normal';
    final estadoColor = fuera ? Colors.red : const Color(0xFF2E7D32);
    final valorTexto = valor == valor.roundToDouble()
        ? valor.toStringAsFixed(0)
        : valor.toStringAsFixed(1);

    return Scaffold(
      appBar: AppBar(title: Text(nombre)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: <Widget>[
          // Tarjeta principal del valor.
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.green.withValues(alpha: 0.25)),
            ),
            child: Column(
              children: <Widget>[
                Icon(_icono, color: _color, size: 44),
                const SizedBox(height: 12),
                Text(
                  '$valorTexto ${_unidad}'.trim(),
                  style: TextStyle(
                    color: _color,
                    fontSize: 40,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 6),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: estadoColor.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    estado,
                    style: TextStyle(
                      color: estadoColor,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                if (rango != null) ...<Widget>[
                  const SizedBox(height: 12),
                  Text(
                    'Rango óptimo: ${rango.minimo} - ${rango.maximo} ${rango.unidad}'
                        .trim(),
                    style: const TextStyle(color: Colors.grey, fontSize: 13),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: 16),
          // Última actualización.
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: <Widget>[
                const Icon(Icons.schedule, color: Colors.grey, size: 20),
                const SizedBox(width: 10),
                const Text('Actualizado el', style: TextStyle(fontSize: 14)),
                const Spacer(),
                Text(
                  preferences.lastUpdate,
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          // Semana.
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: const <Widget>[
                Text('Lun'),
                Text('Mar'),
                Text('Mié'),
                Text('Jue'),
                Text('Vie'),
                Text('Sáb'),
                Text('Dom'),
              ],
            ),
          ),
          const SizedBox(height: 20),
          FilledButton.icon(
            onPressed: () {
              Navigator.push<void>(
                context,
                MaterialPageRoute<void>(
                  builder: (routeContext) => RangoOptimoScreen(nombre: nombre),
                ),
              );
            },
            icon: const Icon(Icons.tune),
            label: const Text('Cambiar variable'),
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
