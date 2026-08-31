import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/preferences_controller.dart';
import '../../models/variable_rango.dart';
import 'variable_detalle_screen.dart';

/// Pantalla 2 — Lista de variables con su estado (Normal / Fuera de rango).
class VariablesScreen extends StatelessWidget {
  const VariablesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final preferences = context.watch<PreferencesController>();

    return ListView(
      padding: const EdgeInsets.all(16),
      children: <Widget>[
        const Text(
          'Variables',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        _VariableCard(
          icon: Icons.thermostat_outlined,
          color: const Color(0xFFE65100),
          label: 'Temperatura',
          valor: preferences.temperature,
          unidad: '°C',
          rango: _rangoDe(preferences, 'Temperatura'),
          onTap: () => _abrirDetalle(context, 'Temperatura'),
        ),
        _VariableCard(
          icon: Icons.water_drop_outlined,
          color: const Color(0xFF1565C0),
          label: 'Humedad',
          valor: preferences.humidity,
          unidad: '%',
          rango: _rangoDe(preferences, 'Humedad'),
          onTap: () => _abrirDetalle(context, 'Humedad'),
        ),
        _VariableCard(
          icon: Icons.science_outlined,
          color: const Color(0xFFC62828),
          label: 'pH',
          valor: preferences.ph,
          unidad: '',
          rango: _rangoDe(preferences, 'pH'),
          onTap: () => _abrirDetalle(context, 'pH'),
        ),
        _VariableCard(
          icon: Icons.eco_outlined,
          color: const Color(0xFF2E7D32),
          label: 'TDS',
          valor: preferences.tds,
          unidad: 'ppm',
          rango: _rangoDe(preferences, 'TDS'),
          onTap: () => _abrirDetalle(context, 'TDS'),
        ),
        _VariableCard(
          icon: Icons.water_drop_outlined,
          color: const Color(0xFF1565C0),
          label: 'Nivel de agua',
          valor: preferences.waterLevel,
          unidad: '%',
          rango: _rangoDe(preferences, 'Nivel de agua'),
          onTap: () => _abrirDetalle(context, 'Nivel de agua'),
        ),
      ],
    );
  }

  VariableRango? _rangoDe(PreferencesController preferences, String nombre) {
    for (final r in preferences.rangos) {
      if (r.variable == nombre) return r;
    }
    return null;
  }

  void _abrirDetalle(BuildContext context, String nombre) {
    Navigator.push<void>(
      context,
      MaterialPageRoute<void>(
        builder: (routeContext) => VariableDetalleScreen(nombre: nombre),
      ),
    );
  }
}

class _VariableCard extends StatelessWidget {
  const _VariableCard({
    required this.icon,
    required this.color,
    required this.label,
    required this.valor,
    required this.unidad,
    required this.rango,
    required this.onTap,
  });

  final IconData icon;
  final Color color;
  final String label;
  final double valor;
  final String unidad;
  final VariableRango? rango;
  final VoidCallback onTap;

  String get _estado {
    if (rango == null) return 'Normal';
    if (valor < rango!.minimo || valor > rango!.maximo) return 'Fuera de rango';
    return 'Normal';
  }

  Color get _estadoColor =>
      _estado == 'Normal' ? const Color(0xFF2E7D32) : Colors.red;

  @override
  Widget build(BuildContext context) {
    final valorTexto = valor == valor.roundToDouble()
        ? valor.toStringAsFixed(0)
        : valor.toStringAsFixed(1);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: Colors.green.withValues(alpha: 0.25)),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: <Widget>[
              Icon(icon, color: color, size: 28),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Text(
                      '$valorTexto $unidad'.trim(),
                      style: TextStyle(
                        color: color,
                        fontSize: 17,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      label,
                      style: const TextStyle(color: Colors.grey, fontSize: 13),
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
                  color: _estadoColor.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  _estado,
                  style: TextStyle(
                    color: _estadoColor,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              const Icon(Icons.chevron_right, color: Colors.grey),
            ],
          ),
        ),
      ),
    );
  }
}
