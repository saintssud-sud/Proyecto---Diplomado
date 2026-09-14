import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/historial_controller.dart';
import '../../models/api/modelos_api.dart';
import '../../widgets/vista_con_estados.dart';

/// Pantalla 5.2 — Lista de las mediciones de la consulta vigente.
///
/// Presenta exactamente las lecturas que devolvió el servicio para la variable y
/// el rango elegidos, con su origen y el estado que el servidor asignó a cada
/// valor respecto de su rango de referencia.
class ListaMedicionesScreen extends StatelessWidget {
  const ListaMedicionesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final HistorialController historial = context.watch<HistorialController>();
    final FiltroHistorial filtro = historial.filtro;

    return Scaffold(
      appBar: AppBar(title: const Text('Lista de mediciones')),
      body: VistaConEstados<List<Lectura>>(
        estado: historial.estado,
        datos: historial.lecturas,
        mensajeError: historial.mensajeError,
        errorDeConexion: historial.errorDeConexion,
        alReintentar: () => context.read<HistorialController>().reintentar(),
        tituloVacio: 'Sin mediciones en el periodo',
        mensajeVacio:
            'No hay mediciones de ${nombreDeVariable(filtro.variable)} en el rango elegido.',
        alMostrarDatos: (BuildContext contexto, List<Lectura> lecturas) {
          // La más reciente primero: es el orden en que se consulta el historial.
          final List<Lectura> ordenadas = List<Lectura>.of(lecturas)
            ..sort((Lectura a, Lectura b) => b.timestamp.compareTo(a.timestamp));

          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: ordenadas.length + 1,
            separatorBuilder: (BuildContext _, int __) => const Divider(),
            itemBuilder: (BuildContext contexto, int indice) {
              if (indice == 0) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Text(
                    '${nombreDeVariable(filtro.variable)} · ${ordenadas.length} '
                    '${ordenadas.length == 1 ? 'medición' : 'mediciones'}',
                    style: const TextStyle(fontSize: 13, color: Colors.grey),
                  ),
                );
              }
              return _MedicionFila(lectura: ordenadas[indice - 1]);
            },
          );
        },
      ),
    );
  }
}

/// Fila con una medición: fecha, valor, origen y estado respecto del rango.
class _MedicionFila extends StatelessWidget {
  const _MedicionFila({required this.lectura});

  final Lectura lectura;

  String _fmt(double valor) => valor == valor.roundToDouble()
      ? valor.toStringAsFixed(0)
      : valor.toStringAsFixed(1);

  String get _fecha {
    final DateTime local = lectura.timestamp.toLocal();
    String dos(int valor) => valor.toString().padLeft(2, '0');
    return '${dos(local.day)}/${dos(local.month)}/${local.year} '
        '${dos(local.hour)}:${dos(local.minute)}';
  }

  @override
  Widget build(BuildContext context) {
    final String? estado = lectura.estadoRango;
    final bool fueraDeRango = estado != null && EstadoRango.esFueraDeRango(estado);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Row(
            children: <Widget>[
              Expanded(
                child: Text(
                  _fecha,
                  style: const TextStyle(fontSize: 13, color: Colors.grey),
                ),
              ),
              _Etiqueta(
                texto: lectura.esManual ? 'Manual' : 'Automática',
                color: lectura.esManual
                    ? const Color(0xFF1565C0)
                    : const Color(0xFF2E7D32),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Row(
            children: <Widget>[
              Expanded(
                child: Text(
                  '${_fmt(lectura.valor)} '
                  '${lectura.unidad.isEmpty ? '' : lectura.unidad}'.trim(),
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
              if (estado != null)
                _Etiqueta(
                  texto: EstadoRango.etiqueta(estado),
                  color: fueraDeRango
                      ? const Color(0xFFC62828)
                      : const Color(0xFF2E7D32),
                ),
            ],
          ),
          if (lectura.observacion != null &&
              lectura.observacion!.trim().isNotEmpty) ...<Widget>[
            const SizedBox(height: 4),
            Text(
              lectura.observacion!,
              style: TextStyle(fontSize: 12, color: Colors.grey[700]),
            ),
          ],
        ],
      ),
    );
  }
}

/// Etiqueta corta de origen o de estado.
class _Etiqueta extends StatelessWidget {
  const _Etiqueta({required this.texto, required this.color});

  final String texto;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        texto,
        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: color),
      ),
    );
  }
}
