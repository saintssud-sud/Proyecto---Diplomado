import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/preferences_controller.dart';
import '../../models/variable_rango.dart';
import '../variables/rango_optimo_screen.dart';

/// Lista de rangos de variables, accesible desde Ajustes.
class RangosVariablesScreen extends StatelessWidget {
  const RangosVariablesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final preferences = context.watch<PreferencesController>();

    return Scaffold(
      appBar: AppBar(title: const Text('Rangos de variables')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: preferences.rangos.map((rango) {
          return _RangoTile(
            rango: rango,
            onTap: () {
              Navigator.push<void>(
                context,
                MaterialPageRoute<void>(
                  builder: (routeContext) =>
                      RangoOptimoScreen(nombre: rango.variable),
                ),
              );
            },
          );
        }).toList(),
      ),
    );
  }
}

class _RangoTile extends StatelessWidget {
  const _RangoTile({required this.rango, required this.onTap});

  final VariableRango rango;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: ListTile(
        title: Text(
          rango.variable,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Text(
          '${rango.minimo} - ${rango.maximo} ${rango.unidad}'.trim(),
        ),
        trailing: const Icon(Icons.chevron_right, color: Colors.grey),
        onTap: onTap,
      ),
    );
  }
}
