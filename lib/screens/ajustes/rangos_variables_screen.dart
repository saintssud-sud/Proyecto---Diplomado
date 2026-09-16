import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/estado_de_vista.dart';
import '../../controllers/rangos_controller.dart';
import '../../models/api/modelos_api.dart';
import '../../utils/formato_fecha.dart';
import '../../widgets/vista_con_estados.dart';

/// Lista de rangos de referencia, accesible desde Ajustes.
///
/// Los rangos se consultan al servicio: son los valores contra los que el
/// servidor evalúa cada lectura, de modo que editarlos aquí cambia la
/// evaluación de las lecturas siguientes y no un dato local de la aplicación.
class RangosVariablesScreen extends StatefulWidget {
  const RangosVariablesScreen({super.key});

  @override
  State<RangosVariablesScreen> createState() => _RangosVariablesScreenState();
}

class _RangosVariablesScreenState extends State<RangosVariablesScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        context.read<RangosController>().cargar();
      }
    });
  }

  Future<void> _editar(RangoReferencia rango) async {
    final RangosController controller = context.read<RangosController>();
    final _Limites? limites = await showDialog<_Limites>(
      context: context,
      builder: (dialogContext) => _DialogoEditarRango(
        rango: rango,
        nombrePerfil: controller.nombrePerfil(rango.perfilId),
      ),
    );
    if (limites == null || !mounted) {
      return;
    }

    final ScaffoldMessengerState mensajero = ScaffoldMessenger.of(context);
    try {
      await controller.actualizar(
        rango,
        minimo: limites.minimo,
        maximo: limites.maximo,
      );
      mensajero.showSnackBar(
        const SnackBar(content: Text('Rango actualizado en el servicio.')),
      );
    } catch (error) {
      mensajero.showSnackBar(
        SnackBar(content: Text(FalloDeVista.desde(error).mensaje)),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final RangosController controller = context.watch<RangosController>();

    return Scaffold(
      appBar: AppBar(title: const Text('Rangos de variables')),
      body: VistaConEstados<List<RangoReferencia>>(
        estado: controller.estado,
        datos: controller.rangos,
        errorDeConexion: controller.errorDeConexion,
        mensajeError: controller.mensajeError,
        mensajeVacio: 'El cultivo todavía no tiene rangos de referencia definidos.',
        alReintentar: () => controller.cargar(),
        alMostrarDatos: (BuildContext contexto, List<RangoReferencia> rangos) {
          return ListView(
            padding: const EdgeInsets.all(16),
            children: <Widget>[
              const Text(
                'Rangos de referencia',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              const Text(
                'Son los valores con los que el servicio evalúa cada lectura. '
                'Toque un rango para modificarlo.',
                style: TextStyle(color: Colors.grey, fontSize: 13),
              ),
              const SizedBox(height: 12),
              for (final RangoReferencia rango in rangos)
                _RangoTile(
                  rango: rango,
                  perfil: controller.nombrePerfil(rango.perfilId),
                  onTap: () => _editar(rango),
                ),
            ],
          );
        },
      ),
    );
  }
}

class _RangoTile extends StatelessWidget {
  const _RangoTile({
    required this.rango,
    required this.perfil,
    required this.onTap,
  });

  final RangoReferencia rango;
  final String perfil;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final String unidad = rango.unidad;
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: ListTile(
        leading: const Icon(Icons.tune, color: Color(0xFF2E7D32)),
        title: Text(
          rango.nombreVariable,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Text(
          '${formatearValor(rango.minimo)} – ${formatearValor(rango.maximo)} '
          '$unidad · $perfil'
              .trim(),
        ),
        trailing: const Icon(Icons.edit_outlined, color: Colors.grey),
        onTap: onTap,
      ),
    );
  }
}

/// Límites devueltos por el diálogo de edición.
class _Limites {
  const _Limites({required this.minimo, required this.maximo});

  final double minimo;
  final double maximo;
}

class _DialogoEditarRango extends StatefulWidget {
  const _DialogoEditarRango({required this.rango, required this.nombrePerfil});

  final RangoReferencia rango;
  final String nombrePerfil;

  @override
  State<_DialogoEditarRango> createState() => _DialogoEditarRangoState();
}

class _DialogoEditarRangoState extends State<_DialogoEditarRango> {
  late final TextEditingController _minimo =
      TextEditingController(text: formatearValor(widget.rango.minimo));
  late final TextEditingController _maximo =
      TextEditingController(text: formatearValor(widget.rango.maximo));
  String? _error;

  @override
  void dispose() {
    _minimo.dispose();
    _maximo.dispose();
    super.dispose();
  }

  void _guardar() {
    final double? minimo = double.tryParse(_minimo.text.trim().replaceAll(',', '.'));
    final double? maximo = double.tryParse(_maximo.text.trim().replaceAll(',', '.'));

    if (minimo == null || maximo == null) {
      setState(() => _error = 'Escriba los dos límites como números.');
      return;
    }
    if (minimo >= maximo) {
      setState(() => _error = 'El mínimo debe ser menor que el máximo.');
      return;
    }
    Navigator.of(context).pop(_Limites(minimo: minimo, maximo: maximo));
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Rango de ${widget.rango.nombreVariable}'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            'Cultivo: ${widget.nombrePerfil}',
            style: const TextStyle(color: Colors.grey, fontSize: 13),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _minimo,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: InputDecoration(
              labelText: 'Mínimo ${widget.rango.unidad}'.trim(),
              border: const OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _maximo,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: InputDecoration(
              labelText: 'Máximo ${widget.rango.unidad}'.trim(),
              border: const OutlineInputBorder(),
            ),
          ),
          if (_error != null) ...<Widget>[
            const SizedBox(height: 10),
            Text(
              _error!,
              style: const TextStyle(color: Color(0xFFC62828), fontSize: 12),
            ),
          ],
        ],
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
