import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/cultivos_controller.dart';
import '../../controllers/estado_de_vista.dart';
import '../../models/api/modelos_api.dart';
import '../../utils/formato_fecha.dart';
import '../../widgets/vista_con_estados.dart';

/// Catálogo de cultivos.
///
/// Un **cultivo** es la especie que se siembra —lechuga, acelga, apio— y con él
/// se definen los **rangos de referencia** de cada variable. El **módulo** es la
/// instalación física donde están los sensores y se asocia a uno de estos
/// cultivos: sus lecturas se evalúan contra los rangos del cultivo asociado.
class CultivosCatalogoScreen extends StatefulWidget {
  const CultivosCatalogoScreen({super.key});

  @override
  State<CultivosCatalogoScreen> createState() => _CultivosCatalogoScreenState();
}

class _CultivosCatalogoScreenState extends State<CultivosCatalogoScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        context.read<CultivosController>().cargar();
      }
    });
  }

  Future<void> _agregar() async {
    final CultivosController controller = context.read<CultivosController>();

    final _DatosCultivo? datos = await showDialog<_DatosCultivo>(
      context: context,
      builder: (dialogContext) => const _DialogoNuevoCultivo(),
    );
    if (datos == null || !mounted) {
      return;
    }

    final ScaffoldMessengerState mensajero = ScaffoldMessenger.of(context);
    try {
      await controller.crear(
        nombre: datos.nombre,
        descripcion: datos.descripcion,
        rangos: datos.rangos,
      );
      mensajero.showSnackBar(
        SnackBar(content: Text('Cultivo "${datos.nombre}" registrado en el servicio.')),
      );
    } catch (error) {
      mensajero.showSnackBar(
        SnackBar(content: Text(FalloDeVista.desde(error).mensaje)),
      );
    }
  }

  Future<void> _eliminar(CultivoConRangos cultivo) async {
    final CultivosController controller = context.read<CultivosController>();

    final bool? confirmado = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text('Eliminar ${cultivo.nombre}'),
        content: Text(
          'Se eliminará el cultivo y sus ${cultivo.rangos.length} rangos de referencia. '
          'Los módulos que lo tuvieran asociado quedarían sin rangos para evaluar sus lecturas.',
        ),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(dialogContext).pop(true),
            style: FilledButton.styleFrom(backgroundColor: const Color(0xFFC62828)),
            child: const Text('Eliminar'),
          ),
        ],
      ),
    );
    if (confirmado != true || !mounted) {
      return;
    }

    final ScaffoldMessengerState mensajero = ScaffoldMessenger.of(context);
    try {
      await controller.eliminar(cultivo);
      mensajero.showSnackBar(
        const SnackBar(content: Text('Cultivo eliminado del servicio.')),
      );
    } catch (error) {
      mensajero.showSnackBar(
        SnackBar(content: Text(FalloDeVista.desde(error).mensaje)),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final CultivosController controller = context.watch<CultivosController>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Cultivos'),
        actions: <Widget>[
          IconButton(
            tooltip: 'Actualizar la lista',
            onPressed: () => controller.cargar(),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: VistaConEstados<List<CultivoConRangos>>(
        estado: controller.estado,
        datos: controller.cultivos,
        errorDeConexion: controller.errorDeConexion,
        mensajeError: controller.mensajeError,
        mensajeVacio: 'Todavía no hay cultivos registrados. Registre el primero con '
            'su nombre y sus rangos de referencia.',
        alReintentar: () => controller.cargar(),
        alMostrarDatos: (BuildContext contexto, List<CultivoConRangos> cultivos) {
          return ListView(
            padding: const EdgeInsets.all(16),
            children: <Widget>[
              const Text(
                'Cultivos',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              const Text(
                'Cada cultivo define los rangos de referencia de las siete variables. '
                'El módulo de cultivo se asocia a uno de ellos y sus lecturas se '
                'evalúan contra esos rangos.',
                style: TextStyle(color: Colors.grey, fontSize: 13),
              ),
              const SizedBox(height: 12),
              for (final CultivoConRangos cultivo in cultivos)
                _CultivoCard(
                  cultivo: cultivo,
                  onEliminar: () => _eliminar(cultivo),
                ),
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: _agregar,
                icon: const Icon(Icons.add),
                label: const Text('Añadir cultivo'),
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
        },
      ),
    );
  }
}

class _CultivoCard extends StatelessWidget {
  const _CultivoCard({required this.cultivo, required this.onEliminar});

  final CultivoConRangos cultivo;
  final VoidCallback onEliminar;

  @override
  Widget build(BuildContext context) {
    final bool predefinido = cultivo.perfil.predefinido;
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: Colors.green.withValues(alpha: 0.25)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            const Icon(Icons.eco_outlined, color: Color(0xFF2E7D32), size: 28),
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
                      if (predefinido)
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 3,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.green.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: const Text(
                            'Predefinido',
                            style: TextStyle(
                              color: Color(0xFF2E7D32),
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                    ],
                  ),
                  if (cultivo.descripcion != null &&
                      cultivo.descripcion!.isNotEmpty) ...<Widget>[
                    const SizedBox(height: 2),
                    Text(
                      cultivo.descripcion!,
                      style: const TextStyle(color: Colors.grey, fontSize: 13),
                    ),
                  ],
                  const SizedBox(height: 6),
                  Text(
                    cultivo.rangos.isEmpty
                        ? cultivo.resumenRangos
                        : '${cultivo.rangos.length} rangos · ${cultivo.resumenRangos}',
                    style: const TextStyle(color: Colors.black87, fontSize: 12),
                  ),
                ],
              ),
            ),
            IconButton(
              tooltip: 'Eliminar cultivo',
              onPressed: onEliminar,
              icon: const Icon(Icons.delete_outline, color: Color(0xFFC62828)),
            ),
          ],
        ),
      ),
    );
  }
}

/// Datos devueltos por el diálogo de alta de un cultivo.
class _DatosCultivo {
  const _DatosCultivo({
    required this.nombre,
    this.descripcion,
    this.rangos = const <RangoNuevo>[],
  });

  final String nombre;
  final String? descripcion;
  final List<RangoNuevo> rangos;
}

class _DialogoNuevoCultivo extends StatefulWidget {
  const _DialogoNuevoCultivo();

  @override
  State<_DialogoNuevoCultivo> createState() => _DialogoNuevoCultivoState();
}

class _DialogoNuevoCultivoState extends State<_DialogoNuevoCultivo> {
  final TextEditingController _nombre = TextEditingController();
  final TextEditingController _descripcion = TextEditingController();

  /// Un par de campos por variable del catálogo: mínimo y máximo.
  final Map<String, TextEditingController> _minimos = <String, TextEditingController>{
    for (final VariableCatalogo variable in catalogoVariables)
      variable.codigo: TextEditingController(),
  };
  final Map<String, TextEditingController> _maximos = <String, TextEditingController>{
    for (final VariableCatalogo variable in catalogoVariables)
      variable.codigo: TextEditingController(),
  };
  String? _error;

  @override
  void dispose() {
    _nombre.dispose();
    _descripcion.dispose();
    for (final TextEditingController control in _minimos.values) {
      control.dispose();
    }
    for (final TextEditingController control in _maximos.values) {
      control.dispose();
    }
    super.dispose();
  }

  double? _numero(TextEditingController control) {
    final String texto = control.text.trim().replaceAll(',', '.');
    if (texto.isEmpty) {
      return null;
    }
    return double.tryParse(texto);
  }

  void _guardar() {
    if (_nombre.text.trim().length < 2) {
      setState(() => _error = 'Escriba el nombre del cultivo (dos letras como mínimo).');
      return;
    }

    final List<RangoNuevo> rangos = <RangoNuevo>[];
    for (final VariableCatalogo variable in catalogoVariables) {
      final TextEditingController minimo = _minimos[variable.codigo]!;
      final TextEditingController maximo = _maximos[variable.codigo]!;
      final bool vacios = minimo.text.trim().isEmpty && maximo.text.trim().isEmpty;
      if (vacios) {
        continue;
      }
      final double? valorMinimo = _numero(minimo);
      final double? valorMaximo = _numero(maximo);
      if (valorMinimo == null || valorMaximo == null) {
        setState(() => _error =
            'Complete el mínimo y el máximo de ${variable.nombre}, o deje los dos campos vacíos.');
        return;
      }
      if (valorMinimo >= valorMaximo) {
        setState(() => _error =
            'En ${variable.nombre} el mínimo debe ser menor que el máximo.');
        return;
      }
      rangos.add(
        RangoNuevo(variable: variable.codigo, minimo: valorMinimo, maximo: valorMaximo),
      );
    }

    Navigator.of(context).pop(
      _DatosCultivo(
        nombre: _nombre.text.trim(),
        descripcion: _descripcion.text.trim(),
        rangos: rangos,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Añadir cultivo'),
      content: SizedBox(
        width: 420,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              const Text(
                'Indique el nombre del cultivo y, si lo conoce, el rango de '
                'referencia de cada variable. Los rangos que deje vacíos no se '
                'enviarán; el servidor valida que estén dentro de los límites '
                'físicos de cada variable.',
                style: TextStyle(color: Colors.black54, fontSize: 12),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _nombre,
                decoration: const InputDecoration(
                  labelText: 'Nombre del cultivo',
                  hintText: 'Ej. Acelga',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: _descripcion,
                decoration: const InputDecoration(
                  labelText: 'Descripción (opcional)',
                  hintText: 'Ej. Hoja verde, ciclo corto',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Rangos de referencia por variable',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
              ),
              const SizedBox(height: 8),
              for (final VariableCatalogo variable in catalogoVariables)
                Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: Row(
                    children: <Widget>[
                      Expanded(
                        flex: 4,
                        child: Text(
                          '${variable.nombre} ${variable.unidad}'.trim(),
                          style: const TextStyle(fontSize: 13, color: Colors.black87),
                        ),
                      ),
                      Expanded(
                        flex: 2,
                        child: TextField(
                          controller: _minimos[variable.codigo],
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          decoration: const InputDecoration(
                            labelText: 'Mín.',
                            isDense: true,
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        flex: 2,
                        child: TextField(
                          controller: _maximos[variable.codigo],
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          decoration: const InputDecoration(
                            labelText: 'Máx.',
                            isDense: true,
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              if (_error != null) ...<Widget>[
                const SizedBox(height: 6),
                Text(
                  _error!,
                  style: const TextStyle(color: Color(0xFFC62828), fontSize: 12),
                ),
              ],
            ],
          ),
        ),
      ),
      actions: <Widget>[
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancelar'),
        ),
        FilledButton(onPressed: _guardar, child: const Text('Guardar')),
      ],
    );
  }
}
