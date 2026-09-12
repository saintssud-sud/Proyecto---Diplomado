import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/usuario_controller.dart';
import '../../services/auth_service.dart';
import 'opciones_screen.dart';
import 'perfil_screen.dart';
import 'rangos_variables_screen.dart';
import 'usuarios_admin_screen.dart';

/// Pantalla 6 — Menú de Ajustes.
class AjustesScreen extends StatelessWidget {
  const AjustesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final usuarioController = context.watch<UsuarioController>();
    final esAdmin = usuarioController.esAdmin;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: <Widget>[
        const Text(
          'Ajustes',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        _OpcionTile(
          icon: Icons.person_outline,
          title: 'Perfil',
          onTap: () => _push(context, const PerfilScreen()),
        ),
        _OpcionTile(
          icon: Icons.tune,
          title: 'Rangos de variables',
          onTap: () => _push(context, const RangosVariablesScreen()),
        ),
        _OpcionTile(
          icon: Icons.notifications_outlined,
          title: 'Notificaciones',
          onTap: () => _push(
            context,
            const OpcionesScreen(
              titulo: 'Notificaciones',
              icono: Icons.notifications_outlined,
              descripcion:
                  'Configura las notificaciones de alertas de tus variables.',
            ),
          ),
        ),
        _OpcionTile(
          icon: Icons.bluetooth,
          title: 'Dispositivos (BT/ID)',
          onTap: () => _push(
            context,
            const OpcionesScreen(
              titulo: 'Dispositivos (BT/ID)',
              icono: Icons.bluetooth,
              descripcion:
                  'Vincula sensores por Bluetooth o por ID de dispositivo.',
            ),
          ),
        ),
        if (esAdmin)
          _OpcionTile(
            icon: Icons.group_outlined,
            title: 'Usuarios (admin)',
            onTap: () => _push(context, const UsuariosAdminScreen()),
          ),
        _OpcionTile(
          icon: Icons.security_outlined,
          title: 'Seguridad',
          onTap: () => _push(
            context,
            const OpcionesScreen(
              titulo: 'Seguridad',
              icono: Icons.security_outlined,
              descripcion:
                  'Opciones de seguridad de la cuenta y del dispositivo.',
            ),
          ),
        ),
        _OpcionTile(
          icon: Icons.info_outline,
          title: 'Acerca de SIGVACH',
          onTap: () => _push(
            context,
            const OpcionesScreen(
              titulo: 'Acerca de SIGVACH',
              icono: Icons.eco_outlined,
              descripcion:
                  'Sistema Integral de Gestión y Visualización de Variables '
                  'para Cultivo Hidropónico.\nVersión 1.0.0',
            ),
          ),
        ),
        const Divider(),
        _OpcionTile(
          icon: Icons.logout,
          title: 'Cerrar sesión',
          color: Colors.red,
          onTap: () => AuthService().signOut(),
        ),
      ],
    );
  }

  void _push(BuildContext context, Widget pantalla) {
    Navigator.push<void>(
      context,
      MaterialPageRoute<void>(builder: (routeContext) => pantalla),
    );
  }
}

class _OpcionTile extends StatelessWidget {
  const _OpcionTile({
    required this.icon,
    required this.title,
    required this.onTap,
    this.color,
  });

  final IconData icon;
  final String title;
  final VoidCallback onTap;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final iconColor = color ?? const Color(0xFF2E7D32);
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: iconColor.withValues(alpha: 0.12),
          child: Icon(icon, color: iconColor),
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
        trailing: const Icon(Icons.chevron_right, color: Colors.grey),
        onTap: onTap,
      ),
    );
  }
}
