import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/estado_de_vista.dart';
import '../../controllers/modulos_controller.dart';
import '../../models/api/modelos_api.dart';
import '../../widgets/vista_con_estados.dart';

/// Pantalla 3 — Módulos o zonas de cultivo.
///
/// Un módulo es la unidad física del sistema: tipo de cultivo, perfil de
/// referencia y estado de activación. Se consulta y se registra en el servicio,
/// de modo que el módulo que se ve aquí es el mismo que el panel usa para
/// evaluar las lecturas.
class CultivosScreen extends StatefulWidget {
  const CultivosScreen({super.key});

  @override
  State<CultivosScreen> createState() => _CultivosScreenState();
}

class _CultivosScreenState extends State<CultivosScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        context.read<ModulosController>().cargar();
      }
    });
  }

  Future<void> _agregar() async {
    final ModulosController controller = context.read<ModulosController>();

    if (controller.perfiles.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Primero debe existir un perfil de cultivo con sus rangos.'),
        ),
      );
      return;
    }

    final _DatosModulo? datos = await showDialog<_DatosModulo>(
      context: context,
      builder: (dialogContext) => _DialogoModulo(
        perfiles: controller.perfiles,
      ),
    );
    if (datos == null || !mounted) {
      return;
    }

    final ScaffoldMessengerState mensajero = ScaffoldMessenger.of(context);
    try {
      await controller.crear(
        nombre: datos.nombre,
        tipoCultivo: datos.tipoCultivo,
        perfilId: datos.perfilId,
        ubicacion: datos.ubicacion,
      );
      mensajero.showSnackBar(
        const SnackBar(content: Text('Módulo registrado en el servicio.')),
      );
    } catch (error) {
      mensajero.showSnackBar(
        SnackBar(content: Text(FalloDeVista.desde(error).mensaje)),
      );
    }
  }

  /// Abre el diálogo de edición con los datos vigentes del módulo.
  Future<void> _editar(ModuloCultivo modulo) async {
    final ModulosController controller = context.read<ModulosController>();

    final _DatosModulo? datos = await showDialog<_DatosModulo>(
      context: context,
      builder: (dialogContext) => _DialogoModulo(
        perfiles: controller.perfiles,
        modulo: modulo,
      ),
    );
    if (datos == null || !mounted) {
      return;
    }

    final ScaffoldMessengerState mensajero = ScaffoldMessenger.of(context);
    try {
      await controller.editar(
        modulo,
        nombre: datos.nombre,
        tipoCultivo: datos.tipoCultivo,
        perfilId: datos.perfilId,
        ubicacion: datos.ubicacion,
      );
      mensajero.showSnackBar(
        const SnackBar(content: Text('Módulo modificado en el servicio.')),
      );
    } catch (error) {
      mensajero.showSnackBar(
        SnackBar(content: Text(FalloDeVista.desde(error).mensaje)),
      );
    }
  }

  /// Confirma y elimina un módulo.
  ///
  /// El servicio decide si la eliminación es admisible: si el módulo tiene
  /// lecturas registradas la rechaza, y ese rechazo se muestra tal cual, porque
  /// es una regla del dominio y no un fallo de la aplicación.
  Future<void> _eliminar(ModuloCultivo modulo) async {
    final ModulosController controller = context.read<ModulosController>();

    final bool? confirmado = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text('Eliminar ${modulo.nombre}'),
        content: const Text(
          'El módulo se eliminará del servicio. Si tiene lecturas registradas, '
          'la operación será rechazada para no perder el historial.',
        ),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(dialogContext).pop(true),
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFFC62828),
            ),
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
      await controller.eliminar(modulo);
      mensajero.showSnackBar(
        const SnackBar(content: Text('Módulo eliminado del servicio.')),
      );
    } catch (error) {
      mensajero.showSnackBar(
        SnackBar(content: Text(FalloDeVista.desde(error).mensaje)),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final ModulosController controller = context.watch<ModulosController>();

    return Scaffold(
      body: VistaConEstados<List<ModuloCultivo>>(
        estado: controller.estado,
        datos: controller.modulos,
        errorDeConexion: controller.errorDeConexion,
        mensajeError: controller.mensajeError,
        mensajeVacio: 'No hay módulos de cultivo registrados. Cree uno para '
            'comenzar a registrar variables.',
        alReintentar: () => controller.cargar(),
        alMostrarDatos: (BuildContext contexto, List<ModuloCultivo> modulos) {
          return ListView(
            padding: const EdgeInsets.all(16),
            children: <Widget>[
              Row(
                children: <Widget>[
                  const Expanded(
                    child: Text(
                      'Módulo de cultivo',
                      style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                    ),
                  ),
                  IconButton(
                    tooltip: 'Actualizar la lista',
                    onPressed: () => controller.cargar(),
                    icon: const Icon(Icons.refresh, color: Color(0xFF2E7D32)),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              const Text(
                'El módulo es la instalación física donde están los sensores. Se asocia '
                'a un cultivo —lechuga, acelga, apio— y son los rangos de ese cultivo '
                'los que se aplican al evaluar cada lectura. Los cultivos se '
                'administran en Ajustes → Cultivos.',
                style: TextStyle(color: Colors.grey, fontSize: 13),
              ),
              const SizedBox(height: 12),
              for (final ModuloCultivo modulo in modulos)
                _ModuloCard(
                  modulo: modulo,
                  perfil: controller.nombrePerfil(modulo.perfilId),
                  onAlternarActivacion: () =>
                      controller.cambiarActivacion(modulo),
                  onEditar: () => _editar(modulo),
                  onEliminar: () => _eliminar(modulo),
                ),
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: _agregar,
                icon: const Icon(Icons.add),
                label: const Text('Agregar módulo de cultivo'),
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

class _ModuloCard extends StatelessWidget {
  const _ModuloCard({
    required this.modulo,
    required this.perfil,
    required this.onAlternarActivacion,
    required this.onEditar,
    required this.onEliminar,
  });

  final ModuloCultivo modulo;
  final String perfil;
  final VoidCallback onAlternarActivacion;
  final VoidCallback onEditar;
  final VoidCallback onEliminar;

  @override
  Widget build(BuildContext context) {
    final bool activo = modulo.activo;
    final Color color =
        activo ? const Color(0xFF2E7D32) : const Color(0xFF757575);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: color.withValues(alpha: 0.3)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(Icons.eco_outlined, color: color),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Row(
                    children: <Widget>[
                      Expanded(
                        child: Text(
                          modulo.nombre,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 3,
                        ),
                        decoration: BoxDecoration(
                          color: color.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          activo ? 'Activo' : 'Inactivo',
                          style: TextStyle(
                            color: color,
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    modulo.tipoCultivo,
                    style: const TextStyle(color: Colors.grey, fontSize: 13),
                  ),
                  const SizedBox(height: 6),
                  _InfoChip(icon: Icons.science_outlined, text: perfil),
                  if (modulo.ubicacion != null && modulo.ubicacion!.isNotEmpty)
                    _InfoChip(
                      icon: Icons.place_outlined,
                      text: modulo.ubicacion!,
                    ),
                ],
              ),
            ),
            PopupMenuButton<String>(
              tooltip: 'Acciones del módulo',
              icon: const Icon(Icons.more_vert, color: Colors.grey),
              onSelected: (String accion) {
                if (accion == 'editar') {
                  onEditar();
                } else if (accion == 'activacion') {
                  onAlternarActivacion();
                } else if (accion == 'eliminar') {
                  onEliminar();
                }
              },
              itemBuilder: (BuildContext contexto) => <PopupMenuEntry<String>>[
                const PopupMenuItem<String>(
                  value: 'editar',
                  child: ListTile(
                    dense: true,
                    leading: Icon(Icons.edit_outlined),
                    title: Text('Editar módulo'),
                  ),
                ),
                PopupMenuItem<String>(
                  value: 'activacion',
                  child: ListTile(
                    dense: true,
                    leading: Icon(
                      activo
                          ? Icons.pause_circle_outline
                          : Icons.play_circle_outline,
                    ),
                    title: Text(activo ? 'Desactivar módulo' : 'Activar módulo'),
                  ),
                ),
                const PopupMenuItem<String>(
                  value: 'eliminar',
                  child: ListTile(
                    dense: true,
                    leading: Icon(Icons.delete_outline, color: Color(0xFFC62828)),
                    title: Text(
                      'Eliminar módulo',
                      style: TextStyle(color: Color(0xFFC62828)),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  const _InfoChip({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 4),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Icon(icon, size: 15, color: Colors.grey),
          const SizedBox(width: 4),
          Text(text, style: const TextStyle(fontSize: 12, color: Colors.black87)),
        ],
      ),
    );
  }
}

/// Datos devueltos por el diálogo de alta o edición de un módulo.
class _DatosModulo {
  const _DatosModulo({
    required this.nombre,
    required this.tipoCultivo,
    required this.perfilId,
    this.ubicacion,
  });

  final String nombre;
  final String tipoCultivo;
  final String perfilId;
  final String? ubicacion;
}

/// Formulario de un módulo de cultivo.
///
/// Sirve para las dos operaciones: sin [modulo] da de alta uno nuevo y con
/// [modulo] parte de los datos vigentes para modificarlo. El formulario es el
/// mismo porque los campos son los mismos; lo que cambia es el punto de partida.
class _DialogoModulo extends StatefulWidget {
  const _DialogoModulo({required this.perfiles, this.modulo});

  final List<PerfilCultivo> perfiles;
  final ModuloCultivo? modulo;

  @override
  State<_DialogoModulo> createState() => _DialogoModuloState();
}

class _DialogoModuloState extends State<_DialogoModulo> {
  late final TextEditingController _nombre =
      TextEditingController(text: widget.modulo?.nombre ?? '');
  late final TextEditingController _tipo =
      TextEditingController(text: widget.modulo?.tipoCultivo ?? 'Lechuga');
  late final TextEditingController _ubicacion =
      TextEditingController(text: widget.modulo?.ubicacion ?? '');
  late String _perfilId = widget.modulo?.perfilId ?? widget.perfiles.first.id;
  String? _error;

  bool get _esEdicion => widget.modulo != null;

  @override
  void dispose() {
    _nombre.dispose();
    _tipo.dispose();
    _ubicacion.dispose();
    super.dispose();
  }

  void _guardar() {
    if (_nombre.text.trim().isEmpty) {
      setState(() => _error = 'Escriba el nombre del módulo.');
      return;
    }
    if (_tipo.text.trim().isEmpty) {
      setState(() => _error = 'Escriba el tipo de cultivo.');
      return;
    }
    Navigator.of(context).pop(
      _DatosModulo(
        nombre: _nombre.text.trim(),
        tipoCultivo: _tipo.text.trim(),
        perfilId: _perfilId,
        ubicacion: _ubicacion.text.trim(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(
        _esEdicion ? 'Editar ${widget.modulo!.nombre}' : 'Agregar módulo de cultivo',
      ),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            TextField(
              controller: _nombre,
              decoration: const InputDecoration(
                labelText: 'Nombre',
                hintText: 'Ej. Módulo 3',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _tipo,
              decoration: const InputDecoration(
                labelText: 'Tipo de cultivo',
                hintText: 'Ej. Lechuga',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              initialValue: _perfilId,
              decoration: const InputDecoration(
                labelText: 'Cultivo',
                border: OutlineInputBorder(),
              ),
              items: widget.perfiles
                  .map(
                    (PerfilCultivo perfil) => DropdownMenuItem<String>(
                      value: perfil.id,
                      child: Text(perfil.nombre),
                    ),
                  )
                  .toList(),
              onChanged: (String? valor) {
                if (valor != null) {
                  setState(() => _perfilId = valor);
                }
              },
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _ubicacion,
              decoration: const InputDecoration(
                labelText: 'Ubicación (opcional)',
                hintText: 'Ej. Invernadero Este',
                border: OutlineInputBorder(),
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
      ),
      actions: <Widget>[
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: _guardar,
          child: Text(_esEdicion ? 'Guardar cambios' : 'Guardar'),
        ),
      ],
    );
  }
}
