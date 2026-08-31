import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/preferences_controller.dart';

/// Pantalla 5.2 — Lista de mediciones históricas.
class ListaMedicionesScreen extends StatelessWidget {
  const ListaMedicionesScreen({super.key});

  String _fmt(double v) =>
      v == v.roundToDouble() ? v.toStringAsFixed(0) : v.toStringAsFixed(1);

  @override
  Widget build(BuildContext context) {
    final preferences = context.watch<PreferencesController>();
    final mediciones = preferences.mediciones.reversed.toList();

    return Scaffold(
      appBar: AppBar(title: const Text('Lista de mediciones')),
      body: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: mediciones.length,
        separatorBuilder: (_, _) => const Divider(),
        itemBuilder: (context, index) {
          final m = mediciones[index];
          return _MedicionFila(
            fecha: m.fechaHora,
            temperatura: '${_fmt(m.temperatura)} °C',
            humedad: '${_fmt(m.humedad)} %',
            ph: _fmt(m.ph),
            tds: '${_fmt(m.tds)} ppm',
          );
        },
      ),
    );
  }
}

class _MedicionFila extends StatelessWidget {
  const _MedicionFila({
    required this.fecha,
    required this.temperatura,
    required this.humedad,
    required this.ph,
    required this.tds,
  });

  final String fecha;
  final String temperatura;
  final String humedad;
  final String ph;
  final String tds;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(fecha, style: const TextStyle(fontSize: 13, color: Colors.grey)),
          const SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: <Widget>[
              _Mini(label: 'T°', valor: temperatura),
              _Mini(label: 'Hum', valor: humedad),
              _Mini(label: 'pH', valor: ph),
              _Mini(label: 'TDS', valor: tds),
            ],
          ),
        ],
      ),
    );
  }
}

class _Mini extends StatelessWidget {
  const _Mini({required this.label, required this.valor});

  final String label;
  final String valor;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
        const SizedBox(height: 2),
        Text(
          valor,
          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
        ),
      ],
    );
  }
}
