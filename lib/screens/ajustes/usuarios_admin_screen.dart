import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/usuario_controller.dart';
import '../../models/usuario_perfil.dart';
import '../../repositories/usuario_repository.dart';
import '../../widgets/max_width_box.dart';

/// Pantalla de administración de usuarios (solo para rol admin).
///
/// Muestra la lista de usuarios registrados (desde Firestore) y permite:
/// - Ver datos personales
/// - Editar datos (nombre, teléfono, cargo)
/// - Cambiar el rol (admin / usuario)
/// - Activar / desactivar
/// - Eliminar el perfil
class UsuariosAdminScreen extends StatefulWidget {
  const UsuariosAdminScreen({super.key});

  @override
  State<UsuariosAdminScreen> createState() => _UsuariosAdminScreenState();
}

class _UsuariosAdminScreenState extends State<UsuariosAdminScreen> {
  final UsuarioRepository _repository = UsuarioRepository();

  Future<void> _editar(UsuarioPerfil usuario) async {
    final nombre = TextEditingController(text: usuario.nombre);
    final telefono = TextEditingController(text: usuario.telefono);
    final cargo = TextEditingController(text: usuario.cargo);

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

    if (guardar == true && context.mounted) {
      final uid = usuario.uid ?? '';
      try {
        await _repository.actualizarDatos(
          uid: uid,
          nombre: nombre.text,
          telefono: telefono.text,
          cargo: cargo.text,
        );
        _aviso('Datos actualizados.');
      } catch (e) {
        _aviso('No se pudo actualizar: $e');
      }
    }
  }

  Future<void> _cambiarRol(UsuarioPerfil usuario) async {
    final nuevo = usuario.rol == 'admin' ? 'usuario' : 'admin';
    final confirmar = await _confirmar(
      titulo: 'Cambiar rol',
      mensaje: '¿Cambiar a ${usuario.email} de "${usuario.rol}" a "$nuevo"?',
    );
    if (confirmar != true || !mounted) return;
    final uid = usuario.uid ?? '';
    try {
      await _repository.cambiarRol(uid: uid, rol: nuevo);
      _aviso('Rol actualizado a $nuevo.');
    } catch (e) {
      _aviso('No se pudo cambiar el rol: $e');
    }
  }

  Future<void> _cambiarActivo(UsuarioPerfil usuario) async {
    final uid = usuario.uid ?? '';
    try {
      await _repository.cambiarActivo(uid: uid, activo: !usuario.activo);
      _aviso(usuario.activo ? 'Usuario desactivado.' : 'Usuario activado.');
    } catch (e) {
      _aviso('No se pudo cambiar el estado: $e');
    }
  }

  Future<void> _eliminar(UsuarioPerfil usuario) async {
    final confirmar = await _confirmar(
      titulo: 'Eliminar usuario',
      mensaje:
          '¿Eliminar el perfil de ${usuario.email}?\n'
          'Esto lo quita del sistema. (La cuenta de Firebase Auth no se '
          'borra; requiere Cloud Functions).',
      peligro: true,
    );
    if (confirmar != true || !mounted) return;
    final uid = usuario.uid ?? '';
    try {
      await _repository.eliminar(uid);
      _aviso('Perfil eliminado.');
    } catch (e) {
      _aviso('No se pudo eliminar: $e');
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
      appBar: AppBar(title: const Text('Usuarios')),
      body: MaxWidthBox(
        child: StreamBuilder<List<UsuarioPerfil>>(
          stream: _repository.verTodos(),
          builder: (context, snapshot) {
            if (snapshot.hasError) {
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      const Icon(Icons.error_outline, size: 52),
                      const SizedBox(height: 12),
                      Text('Error: ${snapshot.error}'),
                    ],
                  ),
                ),
              );
            }
            if (!snapshot.hasData) {
              return const Center(child: CircularProgressIndicator());
            }
            final usuarios = snapshot.data!;
            if (usuarios.isEmpty) {
              return const Center(
                child: Text('Todavía no hay usuarios registrados.'),
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

  Widget _tarjetaUsuario(BuildContext context, UsuarioPerfil usuario) {
    final colorRol = usuario.esAdmin
        ? const Color(0xFF2E7D32)
        : const Color(0xFF1565C0);
    final soyYo = usuario.uid == context.read<UsuarioController>().perfil?.uid;

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
                  label: Text(usuario.rol),
                  visualDensity: VisualDensity.compact,
                  backgroundColor: colorRol.withValues(alpha: 0.15),
                  labelStyle: TextStyle(color: colorRol, fontSize: 12),
                ),
              ],
            ),
            const SizedBox(height: 8),
            if (usuario.cargo.isNotEmpty ||
                usuario.telefono.isNotEmpty) ...<Widget>[
              Text(
                [
                  if (usuario.cargo.isNotEmpty) usuario.cargo,
                  if (usuario.telefono.isNotEmpty) usuario.telefono,
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
                      label: Text('Inactivo'),
                      visualDensity: VisualDensity.compact,
                      backgroundColor: Colors.orange,
                      labelStyle: TextStyle(color: Colors.white, fontSize: 11),
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
                  onPressed: () => _cambiarRol(usuario),
                ),
                IconButton(
                  tooltip: usuario.activo ? 'Desactivar' : 'Activar',
                  icon: Icon(
                    usuario.activo
                        ? Icons.visibility_off_outlined
                        : Icons.visibility_outlined,
                  ),
                  onPressed: () => _cambiarActivo(usuario),
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
