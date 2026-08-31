import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../../controllers/preferences_controller.dart';
import '../../screens/settings_screen.dart';

/// Pantalla 6.1 — Perfil del usuario (nombre y cargo persistentes).
class PerfilScreen extends StatelessWidget {
  const PerfilScreen({super.key});

  Future<void> _editar(BuildContext context) async {
    final p = context.read<PreferencesController>();
    final nombre = TextEditingController(text: p.perfilNombre);
    final cargo = TextEditingController(text: p.perfilCargo);

    final guardar = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Editar información'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            TextField(
              controller: nombre,
              decoration: const InputDecoration(labelText: 'Nombre'),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: cargo,
              decoration: const InputDecoration(labelText: 'Cargo'),
            ),
          ],
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
      await p.setPerfilNombre(nombre.text);
      await p.setPerfilCargo(cargo.text);
    }
  }

  @override
  Widget build(BuildContext context) {
    final preferences = context.watch<PreferencesController>();

    return Scaffold(
      appBar: AppBar(title: const Text('Perfil')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: <Widget>[
          // Cabecera del perfil.
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
                  preferences.perfilNombre,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  preferences.perfilCargo,
                  style: const TextStyle(color: Colors.grey, fontSize: 14),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          ListTile(
            leading: const Icon(Icons.edit_outlined, color: Color(0xFF2E7D32)),
            title: const Text('Editar información'),
            trailing: const Icon(Icons.chevron_right, color: Colors.grey),
            onTap: () => _editar(context),
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
            leading: const Icon(
              Icons.settings_outlined,
              color: Color(0xFF2E7D32),
            ),
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
            onTap: () => Supabase.instance.client.auth.signOut(),
          ),
        ],
      ),
    );
  }
}
