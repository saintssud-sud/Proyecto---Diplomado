import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/estado_de_vista.dart';
import '../../controllers/perfil_controller.dart';
import '../../models/api/modelos_api.dart';
import '../../services/auth_service.dart';
import '../../widgets/vista_con_estados.dart';
import '../settings_screen.dart';

/// Pantalla 6.1 — Perfil del usuario.
///
/// Los datos vienen del servicio: el perfil se crea al registrarse y el mismo
/// documento es el que el backend lee para autorizar cada petición. Por eso la
/// pantalla permite mantener los datos de contacto, pero **no** el rol ni el
/// estado de la cuenta: eso no es una decisión del propio usuario.
class PerfilScreen extends StatefulWidget {
  const PerfilScreen({super.key});

  @override
  State<PerfilScreen> createState() => _PerfilScreenState();
}

class _PerfilScreenState extends State<PerfilScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        context.read<PerfilController>().cargar();
      }
    });
  }

  Future<void> _editar(PerfilUsuario perfil) async {
    final PerfilController controller = context.read<PerfilController>();
    final _DatosPerfil? datos = await showDialog<_DatosPerfil>(
      context: context,
      builder: (dialogContext) => _DialogoEditarPerfil(perfil: perfil),
    );
    if (datos == null || !mounted) {
      return;
    }

    final ScaffoldMessengerState mensajero = ScaffoldMessenger.of(context);
    try {
      await controller.actualizar(
        nombre: datos.nombre,
        telefono: datos.telefono,
        cargo: datos.cargo,
      );
      mensajero.showSnackBar(
        const SnackBar(content: Text('Perfil actualizado en el servicio.')),
      );
    } catch (error) {
      mensajero.showSnackBar(
        SnackBar(content: Text(FalloDeVista.desde(error).mensaje)),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final PerfilController controller = context.watch<PerfilController>();

    return Scaffold(
      appBar: AppBar(title: const Text('Perfil')),
      body: VistaConEstados<PerfilUsuario>(
        estado: controller.estado,
        datos: controller.perfil,
        errorDeConexion: controller.errorDeConexion,
        mensajeError: controller.mensajeError,
        mensajeVacio: 'La cuenta todavía no tiene un perfil registrado.',
        alReintentar: () => controller.cargar(),
        alMostrarDatos: (BuildContext contexto, PerfilUsuario perfil) {
          return ListView(
            padding: const EdgeInsets.all(16),
            children: <Widget>[
              Center(
                child: Column(
                  children: <Widget>[
                    const CircleAvatar(
                      radius: 40,
                      backgroundColor: Color(0xFF39B54A),
                      child: Icon(Icons.person, color: Colors.white, size: 44),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      perfil.nombre.isEmpty ? perfil.email : perfil.nombre,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    if (perfil.cargo != null && perfil.cargo!.isNotEmpty)
                      Text(
                        perfil.cargo!,
                        style: const TextStyle(color: Colors.grey, fontSize: 14),
                      ),
                    const SizedBox(height: 8),
                    Wrap(
                      alignment: WrapAlignment.center,
                      spacing: 8,
                      children: <Widget>[
                        Chip(
                          avatar: const Icon(Icons.badge_outlined, size: 16),
                          label: Text(perfil.etiquetaRol),
                          visualDensity: VisualDensity.compact,
                        ),
                        Chip(
                          avatar: Icon(
                            perfil.activo
                                ? Icons.check_circle_outline
                                : Icons.block_outlined,
                            size: 16,
                          ),
                          label: Text(perfil.activo ? 'Cuenta activa' : 'Cuenta desactivada'),
                          visualDensity: VisualDensity.compact,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              _DatoTile(
                icon: Icons.alternate_email,
                label: 'Correo',
                valor: perfil.email,
                nota: 'Lo administra Firebase Authentication',
              ),
              _DatoTile(
                icon: Icons.phone_outlined,
                label: 'Teléfono',
                valor: (perfil.telefono ?? '').isEmpty
                    ? 'Sin registrar'
                    : perfil.telefono!,
              ),
              _DatoTile(
                icon: Icons.work_outline,
                label: 'Cargo',
                valor: (perfil.cargo ?? '').isEmpty
                    ? 'Sin registrar'
                    : perfil.cargo!,
              ),
              _DatoTile(
                icon: Icons.fingerprint,
                label: 'Identificador de la cuenta',
                valor: perfil.id,
                nota: 'Es el identificador que usa el servicio para autorizar',
              ),
              const Divider(height: 32),
              ListTile(
                leading: const Icon(Icons.edit_outlined, color: Color(0xFF2E7D32)),
                title: const Text('Editar información'),
                subtitle: const Text('Nombre, teléfono y cargo'),
                trailing: const Icon(Icons.chevron_right, color: Colors.grey),
                onTap: () => _editar(perfil),
              ),
              ListTile(
                leading: const Icon(Icons.lock_outline, color: Color(0xFF2E7D32)),
                title: const Text('Cambiar contraseña'),
                trailing: const Icon(Icons.chevron_right, color: Colors.grey),
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Cambio de contraseña disponible próximamente'),
                    ),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.settings_outlined, color: Color(0xFF2E7D32)),
                title: const Text('Preferencias de app'),
                trailing: const Icon(Icons.chevron_right, color: Colors.grey),
                onTap: () {
                  Navigator.push<void>(
                    context,
                    MaterialPageRoute<void>(
                      builder: (routeContext) => const SettingsScreen(),
                    ),
                  );
                },
              ),
              const Divider(),
              ListTile(
                leading: const Icon(Icons.logout, color: Colors.red),
                title: const Text(
                  'Cerrar sesión',
                  style: TextStyle(color: Colors.red),
                ),
                onTap: () => AuthService().signOut(),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _DatoTile extends StatelessWidget {
  const _DatoTile({
    required this.icon,
    required this.label,
    required this.valor,
    this.nota,
  });

  final IconData icon;
  final String label;
  final String valor;
  final String? nota;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: const Color(0xFF2E7D32)),
      title: Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            valor,
            style: const TextStyle(
              color: Colors.black87,
              fontSize: 15,
              fontWeight: FontWeight.w600,
            ),
          ),
          if (nota != null)
            Text(nota!, style: const TextStyle(color: Colors.grey, fontSize: 11)),
        ],
      ),
    );
  }
}

/// Datos devueltos por el diálogo de edición del perfil.
class _DatosPerfil {
  const _DatosPerfil({this.nombre, this.telefono, this.cargo});

  final String? nombre;
  final String? telefono;
  final String? cargo;
}

class _DialogoEditarPerfil extends StatefulWidget {
  const _DialogoEditarPerfil({required this.perfil});

  final PerfilUsuario perfil;

  @override
  State<_DialogoEditarPerfil> createState() => _DialogoEditarPerfilState();
}

class _DialogoEditarPerfilState extends State<_DialogoEditarPerfil> {
  late final TextEditingController _nombre =
      TextEditingController(text: widget.perfil.nombre);
  late final TextEditingController _telefono =
      TextEditingController(text: widget.perfil.telefono ?? '');
  late final TextEditingController _cargo =
      TextEditingController(text: widget.perfil.cargo ?? '');

  @override
  void dispose() {
    _nombre.dispose();
    _telefono.dispose();
    _cargo.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Editar información'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            TextField(
              controller: _nombre,
              decoration: const InputDecoration(
                labelText: 'Nombre',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _telefono,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(
                labelText: 'Teléfono',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _cargo,
              decoration: const InputDecoration(
                labelText: 'Cargo',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'El rol y el estado de la cuenta los administra el servicio: no se '
              'modifican desde aquí.',
              style: TextStyle(color: Colors.grey, fontSize: 11),
            ),
          ],
        ),
      ),
      actions: <Widget>[
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: () => Navigator.of(context).pop(
            _DatosPerfil(
              nombre: _nombre.text.trim(),
              telefono: _telefono.text.trim(),
              cargo: _cargo.text.trim(),
            ),
          ),
          child: const Text('Guardar'),
        ),
      ],
    );
  }
}
