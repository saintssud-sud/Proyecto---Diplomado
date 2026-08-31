import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/preferences_controller.dart';
import '../../models/cultivo.dart';
import 'cultivo_detalle_screen.dart';

/// Pantalla 3 — Lista de cultivos.
class CultivosScreen extends StatelessWidget {
  const CultivosScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final preferences = context.watch<PreferencesController>();
    final cultivos = preferences.cultivos;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: <Widget>[
        const Text(
          'Cultivos',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        if (cultivos.isEmpty)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 32),
            child: Text(
              'No hay cultivos. Agrega uno para comenzar.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey),
            ),
          )
        else
          ...cultivos.map(
            (cultivo) => _CultivoCard(
              cultivo: cultivo,
              onTap: () {
                Navigator.push<void>(
                  context,
                  MaterialPageRoute<void>(
                    builder: (routeContext) =>
                        CultivoDetalleScreen(cultivo: cultivo),
                  ),
                );
              },
            ),
          ),
        const SizedBox(height: 16),
        FilledButton.icon(
          onPressed: () => _showAddDialog(context),
          icon: const Icon(Icons.add),
          label: const Text('Agregar cultivo'),
          style: FilledButton.styleFrom(
            backgroundColor: const Color(0xFF39B54A),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _showAddDialog(BuildContext context) async {
    final nombre = TextEditingController();
    final area = TextEditingController();
    final cantidad = TextEditingController();
    final modulo = TextEditingController();

    final guardar = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Agregar cultivo'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
              TextField(
                controller: nombre,
                decoration: const InputDecoration(
                  labelText: 'Nombre',
                  hintText: 'Ej. Lechuga',
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: area,
                decoration: const InputDecoration(
                  labelText: 'Área',
                  hintText: 'Ej. Invernadero Norte',
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: cantidad,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Cantidad',
                  hintText: 'Ej. 48',
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: modulo,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Módulo',
                  hintText: 'Ej. 4',
                ),
              ),
            ],
          ),
        ),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, true),
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFF39B54A),
              foregroundColor: Colors.white,
            ),
            child: const Text('Guardar'),
          ),
        ],
      ),
    );

    if (guardar == true && context.mounted) {
      final nuevo = Cultivo(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        nombre: nombre.text.trim().isEmpty ? 'Cultivo' : nombre.text.trim(),
        area: area.text.trim().isEmpty ? 'Sin área' : area.text.trim(),
        estado: 'Activo',
        cantidad: int.tryParse(cantidad.text) ?? 1,
        modulo: int.tryParse(modulo.text) ?? 1,
        fechaInicio:
            '${DateTime.now().day.toString().padLeft(2, '0')}/'
            '${DateTime.now().month.toString().padLeft(2, '0')}/'
            '${DateTime.now().year}',
        progreso: 0,
      );
      await context.read<PreferencesController>().addCultivo(nuevo);
    }
  }
}

class _CultivoCard extends StatelessWidget {
  const _CultivoCard({required this.cultivo, required this.onTap});

  final Cultivo cultivo;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
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
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.green.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.eco_outlined, color: Color(0xFF2E7D32)),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Row(
                      children: <Widget>[
                        Expanded(
                          child: Text(
                            cultivo.nombre,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 3,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.green.withValues(alpha: 0.15),
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
                    const SizedBox(height: 2),
                    Text(
                      cultivo.area,
                      style: const TextStyle(color: Colors.grey, fontSize: 13),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: <Widget>[
                        _InfoChip(
                          icon: Icons.grid_view,
                          text: 'Módulo ${cultivo.modulo}',
                        ),
                        const SizedBox(width: 8),
                        _InfoChip(
                          icon: Icons.shopping_basket_outlined,
                          text: '${cultivo.cantidad} plantas',
                        ),
                      ],
                    ),
                  ],
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

class _InfoChip extends StatelessWidget {
  const _InfoChip({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        Icon(icon, size: 15, color: Colors.grey),
        const SizedBox(width: 4),
        Text(text, style: const TextStyle(fontSize: 12, color: Colors.black87)),
      ],
    );
  }
}
