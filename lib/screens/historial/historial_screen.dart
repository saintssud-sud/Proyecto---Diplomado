import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/preferences_controller.dart';
import 'grafica_historica_screen.dart';
import 'lista_mediciones_screen.dart';

/// Pantalla 5 — Consultar historial por rango de fechas.
class HistorialScreen extends StatefulWidget {
  const HistorialScreen({super.key});

  @override
  State<HistorialScreen> createState() => _HistorialScreenState();
}

class _HistorialScreenState extends State<HistorialScreen> {
  static const List<String> _variables = <String>[
    'Temperatura',
    'Humedad',
    'pH',
    'TDS',
  ];

  String _variable = 'Temperatura';
  DateTime? _fechaInicio;
  DateTime? _fechaFin;

  Future<void> _elegirFecha(bool esInicio) async {
    final fecha = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(2025),
      lastDate: DateTime.now(),
    );
    if (fecha == null) return;
    setState(() {
      if (esInicio) {
        _fechaInicio = fecha;
      } else {
        _fechaFin = fecha;
      }
    });
  }

  String _fmt(DateTime? fecha) {
    if (fecha == null) return 'Sin seleccionar';
    return '${fecha.day.toString().padLeft(2, '0')}/'
        '${fecha.month.toString().padLeft(2, '0')}/'
        '${fecha.year}';
  }

  @override
  Widget build(BuildContext context) {
    final preferences = context.watch<PreferencesController>();

    return ListView(
      padding: const EdgeInsets.all(16),
      children: <Widget>[
        const Text(
          'Historial',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          'Consultar Historial',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 12),
        // Variable a consultar.
        DropdownButtonFormField<String>(
          initialValue: _variable,
          decoration: const InputDecoration(
            labelText: 'Variable',
            border: OutlineInputBorder(),
          ),
          items: _variables
              .map((v) => DropdownMenuItem<String>(value: v, child: Text(v)))
              .toList(),
          onChanged: (value) {
            if (value != null) setState(() => _variable = value);
          },
        ),
        const SizedBox(height: 14),
        // Rango de fechas.
        Text('Rango de fecha:', style: TextStyle(color: Colors.grey[700])),
        const SizedBox(height: 8),
        Row(
          children: <Widget>[
            Expanded(
              child: OutlinedButton(
                onPressed: () => _elegirFecha(true),
                child: Text('Inicio: ${_fmt(_fechaInicio)}'),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: OutlinedButton(
                onPressed: () => _elegirFecha(false),
                child: Text('Fin: ${_fmt(_fechaFin)}'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        Text(
          'Variación de fecha',
          style: TextStyle(fontSize: 13, color: Colors.grey[600]),
        ),
        const SizedBox(height: 14),
        // Acciones.
        Row(
          children: <Widget>[
            Expanded(
              child: FilledButton.icon(
                onPressed: () {
                  Navigator.push<void>(
                    context,
                    MaterialPageRoute<void>(
                      builder: (routeContext) =>
                          GraficaHistoricaScreen(variable: _variable),
                    ),
                  );
                },
                icon: const Icon(Icons.show_chart),
                label: const Text('Ver gráfica'),
                style: FilledButton.styleFrom(
                  backgroundColor: const Color(0xFF39B54A),
                  foregroundColor: Colors.white,
                ),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () {
                  Navigator.push<void>(
                    context,
                    MaterialPageRoute<void>(
                      builder: (routeContext) => const ListaMedicionesScreen(),
                    ),
                  );
                },
                icon: const Icon(Icons.list_alt),
                label: const Text('Mediciones'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),
        const Text(
          'Valores actuales',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 10),
        _ValorActual(
          label: 'Temperatura',
          valor: preferences.temperature,
          unidad: '°C',
        ),
        _ValorActual(
          label: 'Humedad',
          valor: preferences.humidity,
          unidad: '%',
        ),
        _ValorActual(label: 'pH', valor: preferences.ph, unidad: ''),
        _ValorActual(label: 'TDS', valor: preferences.tds, unidad: 'ppm'),
      ],
    );
  }
}

class _ValorActual extends StatelessWidget {
  const _ValorActual({
    required this.label,
    required this.valor,
    required this.unidad,
  });

  final String label;
  final double valor;
  final String unidad;

  @override
  Widget build(BuildContext context) {
    final texto = valor == valor.roundToDouble()
        ? valor.toStringAsFixed(0)
        : valor.toStringAsFixed(1);
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: <Widget>[
          Expanded(child: Text(label)),
          Text(
            '$texto $unidad'.trim(),
            style: const TextStyle(
              fontWeight: FontWeight.w600,
              color: Color(0xFF2E7D32),
            ),
          ),
        ],
      ),
    );
  }
}
