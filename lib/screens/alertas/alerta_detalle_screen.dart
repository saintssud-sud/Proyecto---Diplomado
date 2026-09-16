import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/alertas_controller.dart';
import '../../controllers/estado_de_vista.dart';
import '../../models/api/modelos_api.dart';
import '../../utils/formato_fecha.dart';

/// Pantalla 4.1 — Detalle de una alerta.
///
/// Muestra el valor que se registró, el rango del perfil, la desviación y la
/// **lectura de origen** (la trazabilidad). La acción de atender la alerta se
/// envía al servicio y después la lista se vuelve a consultar, de modo que lo
/// que se muestra es lo que quedó guardado.
class AlertaDetalleScreen extends StatefulWidget {
  const AlertaDetalleScreen({super.key, required this.alerta});

  final AlertaServidor alerta;

  @override
  State<AlertaDetalleScreen> createState() => _AlertaDetalleScreenState();
}

class _AlertaDetalleScreenState extends State<AlertaDetalleScreen> {
  bool _procesando = false;

  Future<void> _cambiarEstado({required bool atender}) async {
    setState(() => _procesando = true);
    final AlertasController controller = context.read<AlertasController>();
    final ScaffoldMessengerState mensajero = ScaffoldMessenger.of(context);
    final NavigatorState navegador = Navigator.of(context);

    try {
      if (atender) {
        await controller.marcarAtendida(widget.alerta.id);
      } else {
        await controller.marcarActiva(widget.alerta.id);
      }
      if (!mounted) {
        return;
      }
      navegador.pop();
    } catch (error) {
      if (!mounted) {
        return;
      }
      mensajero.showSnackBar(
        SnackBar(content: Text(FalloDeVista.desde(error).mensaje)),
      );
    } finally {
      if (mounted) {
        setState(() => _procesando = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final AlertaServidor alerta = widget.alerta;
    final bool activa = alerta.estaActiva;
    final Color color =
        activa ? const Color(0xFFC62828) : const Color(0xFF2E7D32);

    return Scaffold(
      appBar: AppBar(
        title: Text(alerta.nombreVariable),
        backgroundColor: color,
        foregroundColor: Colors.white,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: <Widget>[
          _Fila(
            etiqueta: 'Estado',
            valor: activa ? 'Activa' : 'Atendida',
            color: color,
          ),
          _Fila(etiqueta: 'Variable', valor: alerta.nombreVariable),
          _Fila(
            etiqueta: 'Valor registrado',
            valor: '${formatearValor(alerta.valor)} ${alerta.unidad}'.trim(),
          ),
          _Fila(
            etiqueta: 'Rango del perfil',
            valor: '${formatearValor(alerta.rangoMinimo)} – '
                '${formatearValor(alerta.rangoMaximo)} ${alerta.unidad}'.trim(),
          ),
          _Fila(
            etiqueta: 'Desviación',
            valor: alerta.desviacion == 'alto'
                ? 'Por encima del rango'
                : (alerta.desviacion == 'bajo'
                    ? 'Por debajo del rango'
                    : 'Sin clasificar'),
          ),
          _Fila(
            etiqueta: 'Fecha de la lectura',
            valor: formatearFechaHora(alerta.timestamp),
          ),
          _Fila(etiqueta: 'Lectura de origen', valor: alerta.lecturaId),
          if (alerta.observacion != null && alerta.observacion!.isNotEmpty)
            _Fila(etiqueta: 'Observación', valor: alerta.observacion!),
          const SizedBox(height: 8),
          const Text(
            'Cada alerta conserva la referencia a la lectura que la originó: el '
            'servicio asigna esa trazabilidad al evaluar el valor contra el rango '
            'de referencia del perfil de cultivo.',
            style: TextStyle(color: Colors.grey, fontSize: 12),
          ),
          const SizedBox(height: 16),
          if (_procesando)
            const Center(child: CircularProgressIndicator())
          else
            FilledButton.icon(
              onPressed: () => _cambiarEstado(atender: activa),
              icon: Icon(activa
                  ? Icons.check_circle_outline
                  : Icons.restore),
              label: Text(activa
                  ? 'Marcar como atendida'
                  : 'Devolver a alertas activas'),
            ),
        ],
      ),
    );
  }
}

class _Fila extends StatelessWidget {
  const _Fila({required this.etiqueta, required this.valor, this.color});

  final String etiqueta;
  final String valor;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            etiqueta,
            style: const TextStyle(color: Colors.grey, fontSize: 12),
          ),
          const SizedBox(height: 2),
          Text(
            valor,
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: color ?? Colors.black87,
            ),
          ),
        ],
      ),
    );
  }
}
