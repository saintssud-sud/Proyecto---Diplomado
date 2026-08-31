import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../config/app_config.dart';
import '../controllers/preferences_controller.dart';
import '../widgets/max_width_box.dart';
import 'about_adaptation_screen.dart';
import 'ajustes/ajustes_screen.dart';
import 'alertas/alertas_screen.dart';
import 'context/context_lab_screen.dart';
import 'cultivos/cultivos_screen.dart';
import 'historial/historial_screen.dart';
import 'records_screen.dart';
import 'settings_screen.dart';
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
    final config = context.watch<AppConfig>();
    final preferences = context.watch<PreferencesController>();
    // Prioriza el nombre guardado en Supabase (full_name) al registrarse.
    final supabaseUser = Supabase.instance.client.auth.currentUser;
    final supabaseName =
        (supabaseUser?.userMetadata?['full_name'] as String?)?.trim() ?? '';
    final name = supabaseName.isNotEmpty
        ? supabaseName
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
                        'S.I.G.V.A.C.H.',
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
            _DrawerItem(
              icon: Icons.storage_outlined,
              title: '1. Mis registros',
              subtitle: 'CRUD de la Sesion 1',
              onTap: () {
                Navigator.push<void>(
                  context,
                  MaterialPageRoute<void>(
                    builder: (routeContext) => const RecordsScreen(),
                  ),
                );
              },
            ),
            _DrawerItem(
              icon: Icons.public,
              title: '2. Conexion con el mundo',
              subtitle: 'Future + API + JSON + error + GPS + mapa',
              onTap: () {
                Navigator.push<void>(
                  context,
                  MaterialPageRoute<void>(
                    builder: (routeContext) => const ContextLabScreen(),
                  ),
                );
              },
            ),
            _DrawerItem(
              icon: Icons.tune,
              title: '3. Preferencias',
              subtitle: 'Persistencia local',
              onTap: () {
                Navigator.push<void>(
                  context,
                  MaterialPageRoute<void>(
                    builder: (routeContext) => const SettingsScreen(),
                  ),
                );
              },
            ),
            _DrawerItem(
              icon: Icons.design_services_outlined,
              title: '4. Adaptar a mi proyecto',
              subtitle: 'API y hardware deben resolver tu problema',
              onTap: () {
                Navigator.push<void>(
                  context,
                  MaterialPageRoute<void>(
                    builder: (routeContext) => const AboutAdaptationScreen(),
                  ),
                );
              },
            ),
            const Divider(),
            if (config.useSupabase)
              ListTile(
                leading: const Icon(Icons.logout),
                title: const Text('Cerrar sesion'),
                onTap: () {
                  Navigator.of(context).pop();
                  Supabase.instance.client.auth.signOut();
                },
              ),
          ],
        ),
      ),
      body: IndexedStack(
        index: _tabIndex,
        children: <Widget>[
          _DashboardView(preferences: preferences),
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

class _DrawerItem extends StatelessWidget {
  const _DrawerItem({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: CircleAvatar(child: Icon(icon)),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }
}

class _DashboardView extends StatelessWidget {
  const _DashboardView({required this.preferences});

  final PreferencesController preferences;

  static String _fmt(double value) {
    return value == value.roundToDouble()
        ? value.toStringAsFixed(0)
        : value.toStringAsFixed(1);
  }

  Future<void> _editarValores(BuildContext context) async {
    final p = context.read<PreferencesController>();
    final temp = TextEditingController(text: p.temperature.toString());
    final hum = TextEditingController(text: p.humidity.toString());
    final ph = TextEditingController(text: p.ph.toString());
    final tds = TextEditingController(text: p.tds.toString());
    final agua = TextEditingController(text: p.waterLevel.toString());

    final guardar = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Editar valores'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
              TextField(
                controller: temp,
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                decoration: const InputDecoration(
                  labelText: 'Temperatura (°C)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: hum,
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                decoration: const InputDecoration(
                  labelText: 'Humedad (%)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: ph,
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                decoration: const InputDecoration(
                  labelText: 'pH',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: tds,
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                decoration: const InputDecoration(
                  labelText: 'TDS (ppm)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: agua,
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                decoration: const InputDecoration(
                  labelText: 'Nivel de agua (%)',
                  border: OutlineInputBorder(),
                ),
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
      await p.actualizarValores(
        temperatura:
            double.tryParse(temp.text.replaceAll(',', '.')) ?? p.temperature,
        humedad: double.tryParse(hum.text.replaceAll(',', '.')) ?? p.humidity,
        ph: double.tryParse(ph.text.replaceAll(',', '.')) ?? p.ph,
        tds: double.tryParse(tds.text.replaceAll(',', '.')) ?? p.tds,
        nivelAgua:
            double.tryParse(agua.text.replaceAll(',', '.')) ?? p.waterLevel,
      );
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Valores actualizados y guardados')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaxWidthBox(
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: <Widget>[
          _StatusBanner(
            hayAlertas: preferences.alertas.any((a) => a.estado == 'Activa'),
          ),
          const SizedBox(height: 16),
          Row(
            children: <Widget>[
              Expanded(
                child: _MetricCard(
                  icon: Icons.thermostat_outlined,
                  color: const Color(0xFFE65100),
                  label: 'Temperatura',
                  value: '${_fmt(preferences.temperature)} °C',
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _MetricCard(
                  icon: Icons.water_drop_outlined,
                  color: const Color(0xFF1565C0),
                  label: 'Humedad',
                  value: '${_fmt(preferences.humidity)} %',
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: <Widget>[
              Expanded(
                child: _MetricCard(
                  icon: Icons.science_outlined,
                  color: const Color(0xFFC62828),
                  label: 'pH',
                  value: _fmt(preferences.ph),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _MetricCard(
                  icon: Icons.eco_outlined,
                  color: const Color(0xFF2E7D32),
                  label: 'TDS',
                  value: '${_fmt(preferences.tds)} ppm',
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _MetricCard(
            icon: Icons.water_drop_outlined,
            color: const Color(0xFF1565C0),
            label: 'Nivel de agua',
            value: '${_fmt(preferences.waterLevel)} %',
          ),
          const SizedBox(height: 8),
          Align(
            alignment: Alignment.centerRight,
            child: TextButton.icon(
              onPressed: () => _editarValores(context),
              icon: const Icon(Icons.edit_outlined, size: 18),
              label: const Text('Editar valores'),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: <Widget>[
              const Text(
                'Última actualización:',
                style: TextStyle(color: Colors.grey, fontSize: 13),
              ),
              Text(
                preferences.lastUpdate,
                style: const TextStyle(
                  color: Colors.black87,
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ],
      ),
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

class _MetricCard extends StatelessWidget {
  const _MetricCard({
    required this.icon,
    required this.color,
    required this.label,
    required this.value,
  });

  final IconData icon;
  final Color color;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.green.withValues(alpha: 0.25)),
      ),
      child: Row(
        children: <Widget>[
          Icon(icon, color: color, size: 28),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text(
                  value,
                  style: TextStyle(
                    color: color,
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  label,
                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
