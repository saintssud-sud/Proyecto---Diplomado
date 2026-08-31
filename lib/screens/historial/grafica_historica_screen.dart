import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/preferences_controller.dart';
import '../../models/medicion.dart';

/// Pantalla 5.1 — Gráfica histórica de una variable.
class GraficaHistoricaScreen extends StatefulWidget {
  const GraficaHistoricaScreen({super.key, required this.variable});

  final String variable;

  @override
  State<GraficaHistoricaScreen> createState() => _GraficaHistoricaScreenState();
}

class _GraficaHistoricaScreenState extends State<GraficaHistoricaScreen> {
  int _periodo = 0; // 0: 3 meses, 1: 6 meses, 2: 1 año

  static const List<String> _periodos = <String>['3 meses', '6 meses', '1 año'];

  double _valorDe(Medicion m) {
    switch (widget.variable) {
      case 'Humedad':
        return m.humedad;
      case 'pH':
        return m.ph;
      case 'TDS':
        return m.tds;
      default:
        return m.temperatura;
    }
  }

  String get _unidad {
    switch (widget.variable) {
      case 'Humedad':
        return '%';
      case 'pH':
        return '';
      case 'TDS':
        return 'ppm';
      default:
        return '°C';
    }
  }

  List<Medicion> _filtrar(List<Medicion> todas) {
    // Simula el filtro por periodo (en un proyecto real se filtra por fecha).
    if (_periodo == 0) {
      return todas.take(3).toList();
    } else if (_periodo == 1) {
      return todas.take(4).toList();
    }
    return todas;
  }

  @override
  Widget build(BuildContext context) {
    final preferences = context.watch<PreferencesController>();
    final mediciones = _filtrar(preferences.mediciones);
    final valores = mediciones.map(_valorDe).toList();

    final promedio = valores.isEmpty
        ? 0.0
        : valores.reduce((a, b) => a + b) / valores.length;
    final maximo = valores.isEmpty
        ? 0.0
        : valores.reduce((a, b) => a > b ? a : b);
    final minimo = valores.isEmpty
        ? 0.0
        : valores.reduce((a, b) => a < b ? a : b);

    String fmt(double v) =>
        v == v.roundToDouble() ? v.toStringAsFixed(0) : v.toStringAsFixed(1);

    return Scaffold(
      appBar: AppBar(title: const Text('Gráfica Histórica')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: <Widget>[
          Text(
            '${widget.variable} (${_unidad})'.trim(),
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          // Selector de periodo.
          Row(
            children: List<Widget>.generate(_periodos.length, (index) {
              final seleccionado = index == _periodo;
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: ChoiceChip(
                  label: Text(_periodos[index]),
                  selected: seleccionado,
                  onSelected: (_) => setState(() => _periodo = index),
                  selectedColor: const Color(0xFF39B54A),
                  labelStyle: TextStyle(
                    color: seleccionado ? Colors.white : Colors.black87,
                  ),
                ),
              );
            }),
          ),
          const SizedBox(height: 16),
          // Gráfica.
          Container(
            height: 220,
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
            ),
            child: CustomPaint(
              size: Size.infinite,
              painter: _LineChartPainter(valores: valores),
            ),
          ),
          const SizedBox(height: 16),
          // Resumen.
          Row(
            children: <Widget>[
              Expanded(
                child: _ResumenCard(
                  label: 'Promedio',
                  valor: '${fmt(promedio)} ${_unidad}'.trim(),
                  color: const Color(0xFF2E7D32),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _ResumenCard(
                  label: 'Máximo',
                  valor: '${fmt(maximo)} ${_unidad}'.trim(),
                  color: const Color(0xFFE65100),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _ResumenCard(
                  label: 'Mínimo',
                  valor: '${fmt(minimo)} ${_unidad}'.trim(),
                  color: const Color(0xFF1565C0),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _ResumenCard extends StatelessWidget {
  const _ResumenCard({
    required this.label,
    required this.valor,
    required this.color,
  });

  final String label;
  final String valor;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: <Widget>[
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
          const SizedBox(height: 4),
          Text(
            valor,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: color,
              fontSize: 15,
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }
}

class _LineChartPainter extends CustomPainter {
  _LineChartPainter({required this.valores});

  final List<double> valores;

  @override
  void paint(Canvas canvas, Size size) {
    if (valores.length < 2) return;

    final paintLinea = Paint()
      ..color = const Color(0xFF39B54A)
      ..strokeWidth = 2.5
      ..style = PaintingStyle.stroke;

    final paintPunto = Paint()..color = const Color(0xFF2E7D32);

    final paintEje = Paint()
      ..color = Colors.grey.shade300
      ..strokeWidth = 1;

    final min = valores.reduce((a, b) => a < b ? a : b);
    final max = valores.reduce((a, b) => a > b ? a : b);
    final rango = (max - min).abs() < 0.001 ? 1.0 : (max - min);

    const padding = 12.0;
    final w = size.width - padding * 2;
    final h = size.height - padding * 2;

    // Ejes.
    canvas.drawLine(
      Offset(padding, padding),
      Offset(padding, padding + h),
      paintEje,
    );
    canvas.drawLine(
      Offset(padding, padding + h),
      Offset(padding + w, padding + h),
      paintEje,
    );

    final path = Path();
    for (var i = 0; i < valores.length; i++) {
      final x = padding + (i / (valores.length - 1)) * w;
      final y = padding + h - ((valores[i] - min) / rango) * h;
      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
      canvas.drawCircle(Offset(x, y), 3.5, paintPunto);
    }
    canvas.drawPath(path, paintLinea);
  }

  @override
  bool shouldRepaint(covariant _LineChartPainter oldDelegate) {
    return oldDelegate.valores != valores;
  }
}
