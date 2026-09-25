import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/panel_controller.dart';
import '../../models/api/modelos_api.dart';
import '../../utils/formato_fecha.dart';
import '../../widgets/tarjeta_de_modulo.dart';
import '../../widgets/vista_con_estados.dart';

/// Pantalla 2 — Estado de las variables del módulo.
///
/// Consume el servicio a través de [PanelController], el mismo que alimenta el
/// panel principal: la lista se construye con el **catálogo completo** de
/// variables (siete) y con la **última lectura** y el **rango de referencia**
/// que entrega el servidor, de modo que esta pantalla y el panel nunca puedan
/// mostrar datos distintos.
class VariablesScreen extends StatelessWidget {
  const VariablesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final PanelController panel = context.watch<PanelController>();

    return VistaConEstados<List<EstadoDeVariable>>(
      estado: panel.estado,
      datos: panel.variables,
      errorDeConexion: panel.errorDeConexion,
      mensajeError: panel.mensajeError,
      mensajeVacio: 'El módulo todavía no tiene lecturas registradas. '
          'Registre una medición desde el panel principal.',
      alReintentar: () => panel.cargar(),
      // El estado vacío también muestra el módulo: si la pantalla informa que no
      // hay lecturas, debe decir de qué módulo habla y con qué rangos se van a
      // evaluar cuando lleguen.
      contenidoVacio: (BuildContext contexto) => ListView(
        padding: const EdgeInsets.all(16),
        children: <Widget>[
          _encabezado(panel),
          const SizedBox(height: 28),
          const Icon(Icons.inbox_outlined, size: 46, color: Colors.grey),
          const SizedBox(height: 10),
          const Text(
            'El módulo todavía no tiene lecturas registradas.\n'
            'Registre la primera medición desde el panel principal.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey),
          ),
          const SizedBox(height: 16),
          Center(
            child: OutlinedButton.icon(
              onPressed: () => panel.cargar(),
              icon: const Icon(Icons.refresh, size: 18),
              label: const Text('Actualizar'),
            ),
          ),
        ],
      ),
      alMostrarDatos: (BuildContext contexto, List<EstadoDeVariable> variables) {
        return ListView(
          padding: const EdgeInsets.all(16),
          children: <Widget>[
            _encabezado(panel),
            const SizedBox(height: 12),
            for (final EstadoDeVariable variable in variables)
              _VariableCard(variable: variable),
          ],
        );
      },
    );
  }

  /// Encabezado de la pantalla: título y detalle del módulo vigente.
  ///
  /// Se usa el mismo componente de tarjeta que el panel principal y la pantalla
  /// de módulos, de modo que el módulo se vea igual en los tres lugares y el
  /// usuario reconozca de un vistazo sobre qué cultivo está mirando los datos.
  Widget _encabezado(PanelController panel) {
    final ModuloCultivo? modulo = panel.modulo;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        const Text(
          'Variables',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 4),
        Text(
          modulo == null
              ? 'Sin módulo seleccionado'
              : 'Datos del servicio · evaluados contra los rangos del cultivo',
          style: const TextStyle(color: Colors.grey, fontSize: 13),
        ),
        if (modulo != null) ...<Widget>[
          const SizedBox(height: 12),
          TarjetaDeModulo(modulo: modulo, margin: EdgeInsets.zero),
        ],
      ],
    );
  }
}

/// Tarjeta de una variable: valor, nombre, rango de referencia y estado.
///
/// El estado no lo calcula la interfaz: viene del servidor, que evaluó el valor
/// contra el rango vigente del perfil de cultivo.
class _VariableCard extends StatelessWidget {
  const _VariableCard({required this.variable});

  final EstadoDeVariable variable;

  static const Map<String, IconData> _iconos = <String, IconData>{
    'ph': Icons.science_outlined,
    'tds': Icons.eco_outlined,
    'ec': Icons.bolt_outlined,
    'temp_solucion': Icons.thermostat_outlined,
    'temp_ambiental': Icons.thermostat,
    'humedad': Icons.water_drop_outlined,
  };

  static const Map<String, Color> _colores = <String, Color>{
    'ph': Color(0xFFC62828),
    'tds': Color(0xFF2E7D32),
    'ec': Color(0xFF00838F),
    'temp_solucion': Color(0xFFE65100),
    'temp_ambiental': Color(0xFFEF6C00),
    'humedad': Color(0xFF1565C0),
  };

  @override
  Widget build(BuildContext context) {
    final IconData icono = _iconos[variable.codigo] ?? Icons.tune;
    final Color color = _colores[variable.codigo] ?? Colors.blueGrey;

    final bool hayValor = variable.tieneValor;
    final bool fueraDeRango = variable.fueraDeRango;
    final Color colorEstado = !hayValor
        ? Colors.grey
        : (fueraDeRango ? const Color(0xFFC62828) : const Color(0xFF2E7D32));

    final String valorTexto = hayValor ? formatearValor(variable.valor!) : '—';
    final String unidad = hayValor ? variable.unidad : '';
    final String rangoTexto = variable.tieneRango
        ? 'Rango: ${formatearValor(variable.minimo!)} – '
            '${formatearValor(variable.maximo!)} ${variable.unidad}'.trim()
        : 'Sin rango configurado';
    final String fechaTexto =
        hayValor && variable.fecha != null ? formatearFechaHora(variable.fecha!) : '';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: fueraDeRango
              ? const Color(0xFFC62828).withValues(alpha: 0.4)
              : Colors.green.withValues(alpha: 0.25),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: <Widget>[
            Icon(icono, color: color, size: 28),
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
                    variable.nombre,
                    style: const TextStyle(color: Colors.grey, fontSize: 13),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    fechaTexto.isEmpty ? rangoTexto : '$rangoTexto · $fechaTexto',
                    style: const TextStyle(color: Colors.grey, fontSize: 11),
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: colorEstado.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                variable.etiquetaEstado,
                style: TextStyle(
                  color: colorEstado,
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
