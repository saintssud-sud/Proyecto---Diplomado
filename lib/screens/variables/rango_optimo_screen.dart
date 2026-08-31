import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/preferences_controller.dart';
import '../../models/variable_rango.dart';

/// Pantalla 2.2 — Rangos óptimos de una variable (persistente).
class RangoOptimoScreen extends StatefulWidget {
  const RangoOptimoScreen({super.key, required this.nombre});

  final String nombre;

  @override
  State<RangoOptimoScreen> createState() => _RangoOptimoScreenState();
}

class _RangoOptimoScreenState extends State<RangoOptimoScreen> {
  late final TextEditingController _minimo;
  late final TextEditingController _maximo;
  late final TextEditingController _unidad;

  @override
  void initState() {
    super.initState();
    final p = context.read<PreferencesController>();
    VariableRango? rango;
    for (final r in p.rangos) {
      if (r.variable == widget.nombre) {
        rango = r;
        break;
      }
    }
    _minimo = TextEditingController(text: rango?.minimo.toString() ?? '0');
    _maximo = TextEditingController(text: rango?.maximo.toString() ?? '0');
    _unidad = TextEditingController(text: rango?.unidad ?? '');
  }

  @override
  void dispose() {
    _minimo.dispose();
    _maximo.dispose();
    _unidad.dispose();
    super.dispose();
  }

  Future<void> _guardar() async {
    final p = context.read<PreferencesController>();
    final rango = VariableRango(
      variable: widget.nombre,
      minimo: double.tryParse(_minimo.text.replaceAll(',', '.')) ?? 0,
      maximo: double.tryParse(_maximo.text.replaceAll(',', '.')) ?? 0,
      unidad: _unidad.text.trim(),
    );
    await p.updateRango(rango);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Rangos guardados correctamente')),
      );
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Rangos de ${widget.nombre}')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: <Widget>[
          TextField(
            controller: _minimo,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: const InputDecoration(
              labelText: 'Valor mínimo',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 14),
          TextField(
            controller: _maximo,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: const InputDecoration(
              labelText: 'Valor máximo',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 14),
          TextField(
            controller: _unidad,
            decoration: const InputDecoration(
              labelText: 'Unidad',
              hintText: 'Ej. °C, %, ppm',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 24),
          FilledButton.icon(
            onPressed: _guardar,
            icon: const Icon(Icons.save_outlined),
            label: const Text('Guardar cambios'),
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
