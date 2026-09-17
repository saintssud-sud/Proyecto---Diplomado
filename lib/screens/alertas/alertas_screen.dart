import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/alertas_controller.dart';
import '../../controllers/panel_controller.dart';
import '../../models/api/modelos_api.dart';
import '../../utils/formato_fecha.dart';
import '../../widgets/tarjeta_de_modulo.dart';
import '../../widgets/vista_con_estados.dart';
import 'alerta_detalle_screen.dart';

/// Pantalla 4 — Alertas con pestañas Activas / Historial.
///
/// Las alertas se consultan al servicio: las genera el servidor cuando una
/// lectura sale de su rango de referencia. La pantalla no las inventa ni las
/// deduce de los datos locales, de modo que siempre coinciden con el aviso del
/// panel principal.
class AlertasScreen extends StatefulWidget {
  const AlertasScreen({super.key});

  @override
  State<AlertasScreen> createState() => _AlertasScreenState();
}

class _AlertasScreenState extends State<AlertasScreen> {
  /// Módulo con el que se hizo la última consulta.
  String? _moduloConsultado;

  @override
  void initState() {
    super.initState();
    // El módulo de referencia se fija aquí —y no dentro del callback— para que la
    // primera construcción no lo compare contra un valor todavía nulo y lance una
    // segunda consulta idéntica.
    _moduloConsultado = context.read<PanelController>().modulo?.id;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        context.read<AlertasController>().cargar(moduloId: _moduloConsultado);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final AlertasController controller = context.watch<AlertasController>();
    final ModuloCultivo? modulo = context.watch<PanelController>().modulo;

    // Las alertas se consultan para el módulo vigente, igual que el panel: si el
    // usuario cambia de módulo, se vuelven a consultar.
    if (modulo?.id != _moduloConsultado) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted && modulo?.id != _moduloConsultado) {
          _moduloConsultado = modulo?.id;
          context.read<AlertasController>().cargar(moduloId: modulo?.id);
        }
      });
    }

    return VistaConEstados<List<AlertaServidor>>(
      estado: controller.estado,
      datos: <AlertaServidor>[...controller.activas, ...controller.atendidas],
      errorDeConexion: controller.errorDeConexion,
      mensajeError: controller.mensajeError,
      mensajeVacio: 'Todavía no hay alertas. El servicio genera una alerta cada '
          'vez que una lectura sale del rango de su perfil de cultivo.',
      alReintentar: () => controller.cargar(moduloId: _moduloConsultado),
      alMostrarDatos: (BuildContext contexto, List<AlertaServidor> _) {
        return DefaultTabController(
          length: 2,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              const Padding(
                padding: EdgeInsets.fromLTRB(16, 16, 16, 0),
                child: Text(
                  'Alertas',
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                ),
              ),
              if (modulo != null)
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                  child: TarjetaDeModulo(modulo: modulo, margin: EdgeInsets.zero),
                ),
              const TabBar(
                tabs: <Widget>[
                  Tab(text: 'Activas'),
                  Tab(text: 'Historial'),
                ],
                labelColor: Color(0xFF2E7D32),
                unselectedLabelColor: Colors.grey,
                indicatorColor: Color(0xFF2E7D32),
              ),
              Expanded(
                child: TabBarView(
                  children: <Widget>[
                    _ListaAlertas(
                      alertas: controller.activas,
                      vacio: 'No hay alertas activas',
                    ),
                    _ListaAlertas(
                      alertas: controller.atendidas,
                      vacio: 'No hay alertas atendidas todavía',
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _ListaAlertas extends StatelessWidget {
  const _ListaAlertas({required this.alertas, required this.vacio});

  final List<AlertaServidor> alertas;
  final String vacio;

  @override
  Widget build(BuildContext context) {
    if (alertas.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(
            vacio,
            textAlign: TextAlign.center,
            style: const TextStyle(color: Colors.grey),
          ),
        ),
      );
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: alertas
          .map(
            (AlertaServidor alerta) => _AlertaCard(
              alerta: alerta,
              onTap: () {
                Navigator.push<void>(
                  context,
                  MaterialPageRoute<void>(
                    builder: (routeContext) =>
                        AlertaDetalleScreen(alerta: alerta),
                  ),
                );
              },
            ),
          )
          .toList(),
    );
  }
}

/// Tarjeta de una alerta: variable, valor registrado, rango y fecha.
class _AlertaCard extends StatelessWidget {
  const _AlertaCard({required this.alerta, required this.onTap});

  final AlertaServidor alerta;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final bool activa = alerta.estaActiva;
    final Color color =
        activa ? const Color(0xFFC62828) : const Color(0xFF2E7D32);
    final IconData icono =
        activa ? Icons.warning_amber_rounded : Icons.check_circle_outline;
    final String valorTexto =
        '${formatearValor(alerta.valor)} ${alerta.unidad}'.trim();
    final String rangoTexto =
        'Rango del perfil: ${formatearValor(alerta.rangoMinimo)} – '
        '${formatearValor(alerta.rangoMaximo)} ${alerta.unidad}'.trim();

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: color.withValues(alpha: 0.3)),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Icon(icono, color: color, size: 28),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Text(
                      _titulo(alerta),
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Valor registrado: $valorTexto',
                      style: const TextStyle(
                        color: Colors.black87,
                        fontSize: 13,
                      ),
                    ),
                    Text(
                      rangoTexto,
                      style: const TextStyle(color: Colors.grey, fontSize: 13),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${formatearFechaHora(alerta.timestamp)} · '
                      '${activa ? 'Activa' : 'Atendida'}',
                      style: const TextStyle(color: Colors.grey, fontSize: 12),
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

  String _titulo(AlertaServidor alerta) {
    final String variable = alerta.nombreVariable;
    switch (alerta.desviacion) {
      case 'alto':
        return '$variable por encima del rango';
      case 'bajo':
        return '$variable por debajo del rango';
      default:
        return '$variable fuera del rango';
    }
  }
}
