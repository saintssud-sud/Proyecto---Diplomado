import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/estado_de_vista.dart';
import '../controllers/panel_controller.dart';
import '../controllers/preferences_controller.dart';
import '../models/api/modelos_api.dart';
import '../services/api_errores.dart';
import '../services/auth_service.dart';
import '../utils/formato_fecha.dart';
import '../widgets/max_width_box.dart';
import '../widgets/vista_con_estados.dart';
import 'ajustes/ajustes_screen.dart';
import 'alertas/alertas_screen.dart';
import 'cultivos/cultivos_screen.dart';
import 'historial/historial_screen.dart';
import 'variables/variables_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _tabIndex = 0;

  void _onTabSelected(int index) {
    setState(() => _tabIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    final preferences = context.watch<PreferencesController>();
    // Nombre del usuario autenticado en Firebase (displayName o correo).
    final authUser = AuthService().currentUser;
    final fireName = (authUser?.displayName ?? '').trim();
    final emailName = (authUser?.email?.split('@').first ?? '').trim();
    final name = fireName.isNotEmpty
        ? fireName
        : emailName.isNotEmpty
        ? emailName
        : (preferences.name.isEmpty ? 'Diplomante' : preferences.name);

    return Scaffold(
      backgroundColor: const Color(0xFFF2F3F5),
      appBar: AppBar(
        backgroundColor: const Color(0xFF39B54A),
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        title: const Text(
          'SIGVACH',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: <Widget>[
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Actualizar',
            onPressed: () => context.read<PanelController>().cargar(),
          ),
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            tooltip: 'Alertas',
            onPressed: () => _onTabSelected(3),
          ),
        ],
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: <Widget>[
            DrawerHeader(
              decoration: const BoxDecoration(color: Color(0xFF39B54A)),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.end,
                children: <Widget>[
                  Row(
                    children: <Widget>[
                      Container(
                        padding: const EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Image.asset(
                          'assets/images/logo.png',
                          width: 42,
                          height: 42,
                          fit: BoxFit.contain,
                        ),
                      ),
                      const SizedBox(width: 12),
                      const Text(
                        'SI.G.VA.C.H.',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                          fontSize: 17,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Hola, $name',
                    style: const TextStyle(color: Colors.white, fontSize: 14),
                  ),
                ],
              ),
            ),
            const Padding(
              padding: EdgeInsets.fromLTRB(16, 16, 16, 0),
              child: Text(
                'Sistema de Gestión de Variables '
                'para Cultivos Hidropónicos',
                style: TextStyle(
                  color: Colors.black54,
                  fontSize: 13,
                  height: 1.4,
                ),
              ),
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.logout),
              title: const Text('Cerrar sesión'),
              onTap: () {
                Navigator.of(context).pop();
                AuthService().signOut();
              },
            ),
          ],
        ),
      ),
      body: IndexedStack(
        index: _tabIndex,
        children: <Widget>[
          const _PanelView(),
          const VariablesScreen(),
          const CultivosScreen(),
          const AlertasScreen(),
          const HistorialScreen(),
          const AjustesScreen(),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _tabIndex,
        onTap: _onTabSelected,
        type: BottomNavigationBarType.fixed,
        selectedItemColor: const Color(0xFF39B54A),
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Inicio'),
          BottomNavigationBarItem(
            icon: Icon(Icons.show_chart),
            label: 'Variables',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.eco_outlined),
            label: 'Cultivos',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.notifications_outlined),
            label: 'Alertas',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history),
            label: 'Historial',
          ),
          BottomNavigationBarItem(icon: Icon(Icons.settings), label: 'Ajustes'),
        ],
      ),
    );
  }
}

/// Panel principal: presenta el estado de las variables del módulo.
///
/// Consume la API a través de [PanelController] y resuelve los cuatro estados
/// de la vista. Al registrarse una medición, el servidor evalúa cada valor
/// contra su rango y genera las alertas que correspondan; el panel se vuelve a
/// consultar para reflejar ese resultado.
class _PanelView extends StatefulWidget {
  const _PanelView();

  @override
  State<_PanelView> createState() => _PanelViewState();
}

class _PanelViewState extends State<_PanelView> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        context.read<PanelController>().cargar();
      }
    });
  }

  String _mensajeVacio(PanelController panel) {
    if (panel.modulosDisponibles.isEmpty) {
      return 'No hay módulos de cultivo activos. Cree uno en la sección '
          'Cultivos para comenzar a registrar variables.';
    }
    if (panel.modulo == null) {
      return 'No hay un módulo seleccionado. Elija uno para ver sus variables.';
    }
    return 'El módulo ${panel.modulo!.nombre} todavía no tiene lecturas '
        'registradas. Registre la primera medición o espere el envío del '
        'módulo de adquisición.';
  }

  Future<void> _registrarMedicion() async {
    final PanelController panel = context.read<PanelController>();
    final Map<String, double>? valores = await showDialog<Map<String, double>>(
      context: context,
      builder: (BuildContext dialogContext) =>
          _DialogoMedicion(variables: panel.variables),
    );
    if (valores == null || valores.isEmpty || !mounted) {
      return;
    }

    final ScaffoldMessengerState mensajero = ScaffoldMessenger.of(context);
    try {
      final int registradas = await panel.registrarMedicion(valores);
      mensajero.showSnackBar(
        SnackBar(
          content: Text(
            registradas == 1
                ? 'Lectura registrada y evaluada por el servidor'
                : '$registradas lecturas registradas y evaluadas por el servidor',
          ),
        ),
      );
    } on ErrorApi catch (error) {
      // El servidor rechazó la operación: se informa el campo señalado.
      final String campos = error.campos.keys.isEmpty
          ? ''
          : ' Revise: ${error.campos.keys.join(', ')}.';
      mensajero.showSnackBar(
        SnackBar(content: Text('${error.mensajeParaUsuario}$campos')),
      );
    } catch (error) {
      mensajero.showSnackBar(
        SnackBar(content: Text(FalloDeVista.desde(error).mensaje)),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final PanelController panel = context.watch<PanelController>();

    return MaxWidthBox(
      child: VistaConEstados<List<EstadoDeVariable>>(
        estado: panel.estado,
        datos: panel.variables,
        errorDeConexion: panel.errorDeConexion,
        mensajeError: panel.mensajeError,
        mensajeVacio: _mensajeVacio(panel),
        alReintentar: () => panel.cargar(),
        alMostrarDatos: (BuildContext contexto, List<EstadoDeVariable> variables) {
          return ListView(
            padding: const EdgeInsets.all(16),
            children: <Widget>[
              _StatusBanner(hayAlertas: panel.alertasActivas > 0),
              const SizedBox(height: 12),
              _EncabezadoModulo(panel: panel),
              const SizedBox(height: 12),
              ..._filasDeVariables(variables),
              Align(
                alignment: Alignment.centerRight,
                child: TextButton.icon(
                  onPressed: _registrarMedicion,
                  icon: const Icon(Icons.add_circle_outline, size: 18),
                  label: const Text('Registrar medición'),
                ),
              ),
              const SizedBox(height: 4),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: <Widget>[
                  const Text(
                    'Última actualización:',
                    style: TextStyle(color: Colors.grey, fontSize: 13),
                  ),
                  Text(
                    panel.ultimaLectura == null
                        ? 'Sin lecturas'
                        : formatearFechaHora(panel.ultimaLectura!),
                    style: const TextStyle(
                      color: Colors.black87,
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ],
          );
        },
      ),
    );
  }

  List<Widget> _filasDeVariables(List<EstadoDeVariable> variables) {
    final List<Widget> filas = <Widget>[];
    for (int indice = 0; indice < variables.length; indice += 2) {
      final EstadoDeVariable izquierda = variables[indice];
      final EstadoDeVariable? derecha =
          indice + 1 < variables.length ? variables[indice + 1] : null;
      filas.add(
        Row(
          children: <Widget>[
            Expanded(child: _TarjetaVariable(variable: izquierda)),
            const SizedBox(width: 12),
            Expanded(
              child: derecha == null
                  ? const SizedBox.shrink()
                  : _TarjetaVariable(variable: derecha),
            ),
          ],
        ),
      );
      filas.add(const SizedBox(height: 12));
    }
    return filas;
  }
}

/// Nombre del módulo en uso y selector, cuando hay más de uno.
class _EncabezadoModulo extends StatelessWidget {
  const _EncabezadoModulo({required this.panel});

  final PanelController panel;

  @override
  Widget build(BuildContext context) {
    final ModuloCultivo? modulo = panel.modulo;
    if (modulo == null) {
      return const SizedBox.shrink();
    }

    final String detalle = <String>[
      modulo.tipoCultivo,
      if ((modulo.ubicacion ?? '').isNotEmpty) modulo.ubicacion!,
    ].join(' · ');

    if (panel.modulosDisponibles.length <= 1) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            modulo.nombre,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          Text(detalle, style: const TextStyle(color: Colors.grey, fontSize: 13)),
        ],
      );
    }

    return Row(
      children: <Widget>[
        Expanded(
          child: DropdownButtonFormField<String>(
            initialValue: modulo.id,
            decoration: const InputDecoration(
              labelText: 'Módulo de cultivo',
              border: OutlineInputBorder(),
            ),
            items: panel.modulosDisponibles
                .map(
                  (ModuloCultivo opcion) => DropdownMenuItem<String>(
                    value: opcion.id,
                    child: Text(opcion.nombre),
                  ),
                )
                .toList(),
            onChanged: (String? seleccionado) {
              if (seleccionado != null) {
                panel.seleccionarModulo(seleccionado);
              }
            },
          ),
        ),
      ],
    );
  }
}

/// Tarjeta de una variable: último valor, nombre y estado.
class _TarjetaVariable extends StatelessWidget {
  const _TarjetaVariable({required this.variable});

  final EstadoDeVariable variable;

  static const Map<String, IconData> _iconos = <String, IconData>{
    'ph': Icons.science_outlined,
    'tds': Icons.eco_outlined,
    'ec': Icons.bolt_outlined,
    'temp_solucion': Icons.thermostat_outlined,
    'temp_ambiental': Icons.thermostat_outlined,
    'humedad': Icons.water_drop_outlined,
    'nivel_agua': Icons.water_drop_outlined,
  };

  static const Map<String, Color> _colores = <String, Color>{
    'ph': Color(0xFFC62828),
    'tds': Color(0xFF2E7D32),
    'ec': Color(0xFF00695C),
    'temp_solucion': Color(0xFFE65100),
    'temp_ambiental': Color(0xFFEF6C00),
    'humedad': Color(0xFF1565C0),
    'nivel_agua': Color(0xFF0277BD),
  };

  @override
  Widget build(BuildContext context) {
    final Color color = _colores[variable.codigo] ?? Colors.grey;
    final IconData icono = _iconos[variable.codigo] ?? Icons.insights;
    final bool fuera = variable.fueraDeRango;
    final Color colorEstado = fuera
        ? Colors.red
        : (variable.tieneRango ? const Color(0xFF2E7D32) : Colors.grey);

    final String valor = variable.tieneValor
        ? '${formatearValor(variable.valor!)} ${variable.unidad}'.trim()
        : '—';
    final String rango = variable.tieneRango
        ? 'Rango: ${formatearValor(variable.minimo!)} – '
            '${formatearValor(variable.maximo!)} ${variable.unidad}'.trim()
        : 'Sin rango configurado';

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: fuera ? Colors.red.withValues(alpha: 0.4) : const Color(0xFF39B54A).withValues(alpha: 0.25),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Row(
            children: <Widget>[
              Icon(icono, color: color, size: 24),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  valor,
                  style: TextStyle(
                    color: color,
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            variable.nombre,
            style: const TextStyle(color: Colors.grey, fontSize: 12),
          ),
          const SizedBox(height: 6),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
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
          const SizedBox(height: 4),
          Text(
            rango,
            style: const TextStyle(color: Colors.grey, fontSize: 11),
          ),
        ],
      ),
    );
  }
}

/// Diálogo para registrar a mano las variables que se hayan medido.
///
/// Solo se envían las variables que el usuario completa: dejar un campo vacío
/// no registra una lectura con valor cero, que sería un dato falso.
class _DialogoMedicion extends StatefulWidget {
  const _DialogoMedicion({required this.variables});

  final List<EstadoDeVariable> variables;

  @override
  State<_DialogoMedicion> createState() => _DialogoMedicionState();
}

class _DialogoMedicionState extends State<_DialogoMedicion> {
  late final Map<String, TextEditingController> _controles =
      <String, TextEditingController>{
    for (final EstadoDeVariable variable in widget.variables)
      variable.codigo: TextEditingController(),
  };

  @override
  void dispose() {
    for (final TextEditingController control in _controles.values) {
      control.dispose();
    }
    super.dispose();
  }

  void _guardar() {
    final Map<String, double> valores = <String, double>{};
    _controles.forEach((String codigo, TextEditingController control) {
      final String texto = control.text.trim().replaceAll(',', '.');
      if (texto.isEmpty) {
        return;
      }
      final double? valor = double.tryParse(texto);
      if (valor != null) {
        valores[codigo] = valor;
      }
    });
    Navigator.of(context).pop(valores);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Registrar medición'),
      content: SizedBox(
        width: 380,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
              const Padding(
                padding: EdgeInsets.only(bottom: 12),
                child: Text(
                  'Complete únicamente las variables que haya medido. El '
                  'servidor evaluará cada valor contra su rango de referencia.',
                  style: TextStyle(fontSize: 12, color: Colors.black54),
                ),
              ),
              for (final EstadoDeVariable variable in widget.variables)
                Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: TextField(
                    controller: _controles[variable.codigo],
                    keyboardType: const TextInputType.numberWithOptions(
                      decimal: true,
                    ),
                    decoration: InputDecoration(
                      labelText: '${variable.nombre} ${variable.unidad}'.trim(),
                      helperText: variable.tieneRango
                          ? 'Rango: ${formatearValor(variable.minimo!)} – '
                              '${formatearValor(variable.maximo!)} ${variable.unidad}'
                              .trim()
                          : 'Sin rango configurado',
                      border: const OutlineInputBorder(),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
      actions: <Widget>[
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: _guardar,
          style: FilledButton.styleFrom(
            backgroundColor: const Color(0xFF39B54A),
            foregroundColor: Colors.white,
          ),
          child: const Text('Guardar'),
        ),
      ],
    );
  }
}

class _StatusBanner extends StatelessWidget {
  const _StatusBanner({required this.hayAlertas});

  final bool hayAlertas;

  @override
  Widget build(BuildContext context) {
    final color = hayAlertas
        ? const Color(0xFFE65100)
        : const Color(0xFF2E7D32);
    final icono = hayAlertas ? Icons.warning_amber_rounded : Icons.check_circle;
    final titulo = hayAlertas ? 'Sistema con alertas' : 'Sistema normal';
    final subtitulo = hayAlertas
        ? 'Algunos parámetros están fuera de rango'
        : 'Todo dentro del rango óptimo';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: <Widget>[
          Icon(icono, color: color, size: 32),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text(
                  titulo,
                  style: TextStyle(
                    color: color,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 2),
                Text(subtitulo, style: TextStyle(color: color, fontSize: 13)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
