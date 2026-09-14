import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/historial_controller.dart';
import '../../models/api/modelos_api.dart';
import '../../widgets/vista_con_estados.dart';

/// Pantalla 5.1 — Gráfica histórica de la variable consultada.
///
/// La gráfica no filtra ni resume por su cuenta: pide al servicio la variable y
/// el periodo elegidos, y presenta la serie y el resumen que este devuelve. Los
/// períodos rápidos de la parte superior son atajos de ese mismo filtro, de modo
/// que lo que se ve en pantalla siempre corresponde a una consulta real.
class GraficaHistoricaScreen extends StatelessWidget {
  const GraficaHistoricaScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final HistorialController historial = context.watch<HistorialController>();
    final FiltroHistorial filtro = historial.filtro;
    final String unidad = historial.resumen?.unidad ?? unidadDeVariable(filtro.variable);
    final int? seleccionado = _periodoSeleccionado(filtro);

    return Scaffold(
      appBar: AppBar(title: const Text('Gráfica Histórica')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: <Widget>[
          Text(
            '${nombreDeVariable(filtro.variable)} (${unidad == '' ? 'sin unidad' : unidad})',
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(
            _descripcionDelPeriodo(filtro),
            style: TextStyle(fontSize: 13, color: Colors.grey[700]),
          ),
          const SizedBox(height: 12),
          // Períodos rápidos: aplican un rango de fechas sobre la consulta.
          Row(
            children: List<Widget>.generate(_periodos.length, (int indice) {
              final bool esElActual = indice == seleccionado;
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: ChoiceChip(
                  label: Text(_periodos[indice].etiqueta),
                  selected: esElActual,
                  onSelected: (_) {
                    final DateTime ahora = DateTime.now();
                    context.read<HistorialController>().seleccionarPeriodo(
                          desde: _desdeHaceMeses(_periodos[indice].meses, ahora),
                          hasta: ahora,
                        );
                  },
                  selectedColor: const Color(0xFF39B54A),
                  labelStyle: TextStyle(
                    color: esElActual ? Colors.white : Colors.black87,
                  ),
                ),
              );
            }),
          ),
          const SizedBox(height: 16),
          VistaConEstados<List<Lectura>>(
            estado: historial.estado,
            datos: historial.lecturas,
            mensajeError: historial.mensajeError,
            errorDeConexion: historial.errorDeConexion,
            alReintentar: () => context.read<HistorialController>().reintentar(),
            tituloVacio: 'Sin mediciones en el periodo',
            mensajeVacio:
                'No hay mediciones de esta variable en el rango elegido. Pruebe con un periodo más amplio.',
            alMostrarDatos: (BuildContext contexto, List<Lectura> lecturas) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: <Widget>[
                  _Grafica(valores: _valores(historial)),
                  const SizedBox(height: 8),
                  Text(
                    lecturas.length == 1
                        ? 'Se muestra 1 medición: hacen falta al menos dos para trazar la línea.'
                        : 'Serie de ${lecturas.length} mediciones, de la más antigua a la más reciente.',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                  const SizedBox(height: 16),
                  _ResumenDelPeriodo(resumen: historial.resumen),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  /// Valores de la serie, ordenados cronológicamente.
  static List<double> _valores(HistorialController historial) {
    return historial.serieCronologica
        .map((Lectura lectura) => lectura.valor)
        .toList(growable: false);
  }
}

/// Período rápido ofrecido sobre la gráfica.
class _Periodo {
  const _Periodo(this.etiqueta, this.meses);

  final String etiqueta;
  final int meses;
}

const List<_Periodo> _periodos = <_Periodo>[
  _Periodo('3 meses', 3),
  _Periodo('6 meses', 6),
  _Periodo('1 año', 12),
];

/// Fecha de hace [meses], normalizada por el propio constructor de `DateTime`.
DateTime _desdeHaceMeses(int meses, DateTime ahora) {
  return DateTime(ahora.year, ahora.month - meses, ahora.day);
}

/// Índice del período rápido que corresponde al filtro vigente, o nulo si el
/// rango no proviene de ninguno de ellos.
int? _periodoSeleccionado(FiltroHistorial filtro) {
  final DateTime? desde = filtro.desde;
  if (desde == null) {
    return null;
  }
  final DateTime ahora = DateTime.now();
  for (int indice = 0; indice < _periodos.length; indice++) {
    final DateTime esperado = _desdeHaceMeses(_periodos[indice].meses, ahora);
    if (desde.year == esperado.year &&
        desde.month == esperado.month &&
        desde.day == esperado.day) {
      return indice;
    }
  }
  return null;
}

/// Texto del periodo consultado.
String _descripcionDelPeriodo(FiltroHistorial filtro) {
  final String? desde = _fecha(filtro.desde);
  final String? hasta = _fecha(filtro.hasta);
  if (desde == null && hasta == null) {
    return 'Todo el historial registrado';
  }
  return 'Del ${desde ?? 'inicio'} al ${hasta ?? 'hoy'}';
}

String? _fecha(DateTime? fecha) {
  if (fecha == null) {
    return null;
  }
  final DateTime local = fecha.toLocal();
  return '${local.day.toString().padLeft(2, '0')}/'
      '${local.month.toString().padLeft(2, '0')}/${local.year}';
}

/// Gráfica de la serie, o una nota si todavía no alcanzan los puntos.
class _Grafica extends StatelessWidget {
  const _Grafica({required this.valores});

  final List<double> valores;

  @override
  Widget build(BuildContext context) {
    if (valores.length < 2) {
      return Container(
        height: 120,
        alignment: Alignment.center,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          valores.isEmpty
              ? 'Sin valores para graficar.'
              : 'Con una sola medición no se puede trazar una línea; se muestra su valor en el resumen.',
          textAlign: TextAlign.center,
          style: TextStyle(color: Colors.grey[700]),
        ),
      );
    }

    return Container(
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
    );
  }
}

/// Resumen del periodo tal como lo devuelve el servicio.
class _ResumenDelPeriodo extends StatelessWidget {
  const _ResumenDelPeriodo({required this.resumen});

  final ResumenVariable? resumen;

  @override
  Widget build(BuildContext context) {
    final ResumenVariable? datos = resumen;
    if (datos == null) {
      return Text(
        'El servicio no devolvió el resumen del periodo.',
        style: TextStyle(fontSize: 13, color: Colors.grey[700]),
      );
    }

    final String sufijo = datos.unidad.isEmpty ? '' : ' ${datos.unidad}';
    String fmt(double valor) => valor == valor.roundToDouble()
        ? valor.toStringAsFixed(0)
        : valor.toStringAsFixed(1);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(
          'Resumen del periodo (${datos.cantidad} mediciones)',
          style: const TextStyle(fontSize: 13, color: Colors.grey),
        ),
        const SizedBox(height: 8),
        Row(
          children: <Widget>[
            Expanded(
              child: _ResumenCard(
                label: 'Promedio',
                valor: '${fmt(datos.promedio)}$sufijo',
                color: const Color(0xFF2E7D32),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: _ResumenCard(
                label: 'Máximo',
                valor: '${fmt(datos.maximo)}$sufijo',
                color: const Color(0xFFE65100),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: _ResumenCard(
                label: 'Mínimo',
                valor: '${fmt(datos.minimo)}$sufijo',
                color: const Color(0xFF1565C0),
              ),
            ),
          ],
        ),
      ],
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
