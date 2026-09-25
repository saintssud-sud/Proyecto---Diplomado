import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/perfil_controller.dart';
import '../../models/api/modelos_api.dart';
import '../../models/roles.dart';
import '../../repositories/api/usuarios_api_repository.dart';
import '../../services/api_cliente.dart';
import '../../widgets/max_width_box.dart';

/// Pantalla de administración de usuarios (solo para el rol de administración).
///
/// Muestra las cuentas registradas y permite:
/// - Ver los datos de contacto
/// - Editar los datos (nombre, teléfono, cargo)
/// - Cambiar el rol (administrador / operador)
/// - Activar o desactivar la cuenta
/// - Eliminar el perfil
///
/// **Las operaciones pasan por el servicio, no por la base de datos.** Antes
/// esta pantalla leía la colección `usuarios` directamente desde la aplicación,
/// y dejó de funcionar cuando las reglas de seguridad de Firestore cerraron el
/// acceso directo. Además, esa vía eludía dos protecciones que el servicio sí
/// aplica: que el rol pertenezca al catálogo del sistema y que la administración
/// no pueda quitarse a sí misma el rol ni desactivar su propia cuenta. La
/// autorización se comprueba en el servidor: que el botón esté oculto no es
/// autorización.
class UsuariosAdminScreen extends StatefulWidget {
  const UsuariosAdminScreen({super.key});

  @override
  State<UsuariosAdminScreen> createState() => _UsuariosAdminScreenState();
}

class _UsuariosAdminScreenState extends State<UsuariosAdminScreen> {
  late final UsuariosApiRepository _repositorio;

  Future<List<PerfilUsuario>>? _cuentas;

  @override
  void initState() {
    super.initState();
    _repositorio = UsuariosApiRepository(context.read<ApiCliente>());
    _recargar();
  }

  void _recargar() {
    setState(() {
      _cuentas = _repositorio.listarCuentas();
    });
  }

  /// Lee el error del servicio y devuelve un mensaje presentable.
  String _mensajeDeError(Object error) {
    final texto = error.toString();
    if (texto.contains('403') || texto.toLowerCase().contains('permiso')) {
      return 'La cuenta con la que inició sesión no tiene atribuciones de '
          'administración.';
    }
    return texto;
  }

  Future<void> _editar(PerfilUsuario usuario) async {
    final nombre = TextEditingController(text: usuario.nombre);
    final telefono = TextEditingController(text: usuario.telefono ?? '');
    final cargo = TextEditingController(text: usuario.cargo ?? '');

    final guardar = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text('Editar a ${usuario.email}'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
              TextField(
                controller: nombre,
                decoration: const InputDecoration(labelText: 'Nombre'),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: telefono,
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(labelText: 'Teléfono'),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: cargo,
                decoration: const InputDecoration(labelText: 'Cargo'),
              ),
            ],
          ),
        ),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, true),
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFF39B54A),
              foregroundColor: Colors.white,
            ),
            child: const Text('Guardar'),
          ),
        ],
      ),
    );

    if (guardar == true && mounted) {
      try {
        await _repositorio.modificarCuenta(
          usuario.id,
          nombre: nombre.text,
          telefono: telefono.text,
          cargo: cargo.text,
        );
        _aviso('Datos actualizados.');
        _recargar();
      } catch (e) {
        _aviso('No se pudo actualizar: ${_mensajeDeError(e)}');
      }
    }
  }

  Future<void> _cambiarRol(PerfilUsuario usuario) async {
    final nuevo = Roles.alternar(usuario.rol);
    final confirmar = await _confirmar(
      titulo: 'Cambiar rol',
      mensaje: '¿Cambiar a ${usuario.email} de "${usuario.etiquetaRol}" '
          'a "${Roles.etiqueta(nuevo)}"?',
    );
    if (confirmar != true || !mounted) return;
    try {
      await _repositorio.modificarCuenta(usuario.id, rol: nuevo);
      _aviso('Rol actualizado a ${Roles.etiqueta(nuevo)}.');
      _recargar();
    } catch (e) {
      _aviso('No se pudo cambiar el rol: ${_mensajeDeError(e)}');
    }
  }

  Future<void> _cambiarActivo(PerfilUsuario usuario) async {
    try {
      await _repositorio.modificarCuenta(usuario.id, activo: !usuario.activo);
      _aviso(usuario.activo ? 'Cuenta desactivada.' : 'Cuenta activada.');
      _recargar();
    } catch (e) {
      _aviso('No se pudo cambiar el estado: ${_mensajeDeError(e)}');
    }
  }

  Future<void> _eliminar(PerfilUsuario usuario) async {
    final confirmar = await _confirmar(
      titulo: 'Eliminar cuenta',
      mensaje:
          '¿Eliminar el perfil de ${usuario.email}?\n'
          'Esto lo quita del sistema. La credencial de Firebase Authentication '
          'permanece, porque eliminarla exige privilegios de administración del '
          'proveedor que no están en el alcance.',
      peligro: true,
    );
    if (confirmar != true || !mounted) return;
    try {
      await _repositorio.eliminarCuenta(usuario.id);
      _aviso('Perfil eliminado.');
      _recargar();
    } catch (e) {
      _aviso('No se pudo eliminar: ${_mensajeDeError(e)}');
    }
  }

  Future<bool?> _confirmar({
    required String titulo,
    required String mensaje,
    bool peligro = false,
  }) {
    return showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text(titulo),
        content: Text(mensaje),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, true),
            style: FilledButton.styleFrom(
              backgroundColor: peligro ? Colors.red : const Color(0xFF39B54A),
              foregroundColor: Colors.white,
            ),
            child: Text(peligro ? 'Eliminar' : 'Confirmar'),
          ),
        ],
      ),
    );
  }

  void _aviso(String mensaje) {
    if (!mounted) return;
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(mensaje)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Usuarios'),
        actions: <Widget>[
          IconButton(
            tooltip: 'Actualizar',
            icon: const Icon(Icons.refresh),
            onPressed: _recargar,
          ),
        ],
      ),
      body: MaxWidthBox(
        child: FutureBuilder<List<PerfilUsuario>>(
          future: _cuentas,
          builder: (context, snapshot) {
            if (snapshot.hasError) {
              return _estadoDeError(snapshot.error!);
            }
            if (!snapshot.hasData) {
              return const Center(child: CircularProgressIndicator());
            }
            final usuarios = snapshot.data!;
            if (usuarios.isEmpty) {
              return const Center(
                child: Text('Todavía no hay cuentas registradas.'),
              );
            }
            return ListView.separated(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
              itemCount: usuarios.length,
              separatorBuilder: (context, index) => const SizedBox(height: 8),
              itemBuilder: (context, index) =>
                  _tarjetaUsuario(context, usuarios[index]),
            );
          },
        ),
      ),
    );
  }

  /// Estado de error de la vista, con acción de reintento.
  Widget _estadoDeError(Object error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            const Icon(Icons.error_outline, size: 52),
            const SizedBox(height: 12),
            const Text(
              'No se pudo obtener la lista de cuentas',
              style: TextStyle(fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              _mensajeDeError(error),
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.black54),
            ),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: _recargar,
              icon: const Icon(Icons.refresh),
              label: const Text('Reintentar'),
              style: FilledButton.styleFrom(
                backgroundColor: const Color(0xFF39B54A),
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _tarjetaUsuario(BuildContext context, PerfilUsuario usuario) {
    final colorRol = usuario.esAdministrador
        ? const Color(0xFF2E7D32)
        : const Color(0xFF1565C0);
    final yo = context.read<PerfilController>().perfil;
    final soyYo = yo != null && yo.id == usuario.id;

    return Card(
      margin: EdgeInsets.zero,
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Row(
              children: <Widget>[
                CircleAvatar(
                  backgroundColor: colorRol.withValues(alpha: 0.12),
                  child: Icon(Icons.person, color: colorRol),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Text(
                        usuario.nombre.isEmpty ? usuario.email : usuario.nombre,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(
                        usuario.email,
                        style: const TextStyle(
                          fontSize: 12,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                ),
                Chip(
                  label: Text(usuario.etiquetaRol),
                  visualDensity: VisualDensity.compact,
                  backgroundColor: colorRol.withValues(alpha: 0.15),
                  labelStyle: TextStyle(color: colorRol, fontSize: 12),
                ),
              ],
            ),
            const SizedBox(height: 8),
            if ((usuario.cargo ?? '').isNotEmpty ||
                (usuario.telefono ?? '').isNotEmpty) ...<Widget>[
              Text(
                [
                  if ((usuario.cargo ?? '').isNotEmpty) usuario.cargo!,
                  if ((usuario.telefono ?? '').isNotEmpty) usuario.telefono!,
                ].join('  ·  '),
                style: const TextStyle(fontSize: 13, color: Colors.black54),
              ),
              const SizedBox(height: 8),
            ],
            Row(
              children: <Widget>[
                if (!usuario.activo)
                  const Padding(
                    padding: EdgeInsets.only(right: 8),
                    child: Chip(
                      label: Text('Inactiva'),
                      visualDensity: VisualDensity.compact,
                      backgroundColor: Colors.orange,
                      labelStyle: TextStyle(color: Colors.white, fontSize: 11),
                    ),
                  ),
                if (soyYo)
                  const Padding(
                    padding: EdgeInsets.only(right: 8),
                    child: Chip(
                      label: Text('Su cuenta'),
                      visualDensity: VisualDensity.compact,
                      labelStyle: TextStyle(fontSize: 11),
                    ),
                  ),
                const Spacer(),
                IconButton(
                  tooltip: 'Editar datos',
                  icon: const Icon(Icons.edit_outlined),
                  onPressed: () => _editar(usuario),
                ),
                IconButton(
                  tooltip: 'Cambiar rol',
                  icon: const Icon(Icons.admin_panel_settings_outlined),
                  // La administración no puede cambiarse el rol a sí misma: el
                  // servicio lo rechaza con 409.
                  onPressed: soyYo ? null : () => _cambiarRol(usuario),
                ),
                IconButton(
                  tooltip: usuario.activo ? 'Desactivar' : 'Activar',
                  icon: Icon(
                    usuario.activo
                        ? Icons.visibility_off_outlined
                        : Icons.visibility_outlined,
                  ),
                  onPressed: soyYo ? null : () => _cambiarActivo(usuario),
                ),
                IconButton(
                  tooltip: 'Eliminar',
                  icon: const Icon(Icons.delete_outline, color: Colors.red),
                  onPressed: soyYo ? null : () => _eliminar(usuario),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
