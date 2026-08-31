import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../config/app_config.dart';
import '../controllers/preferences_controller.dart';
import '../widgets/max_width_box.dart';
import '../widgets/mode_banner.dart';
import 'about_adaptation_screen.dart';
import 'context/context_lab_screen.dart';
import 'records_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final config = context.watch<AppConfig>();
    final preferences = context.watch<PreferencesController>();
    final name = preferences.name.isEmpty ? 'Diplomante' : preferences.name;

    return Scaffold(
      backgroundColor: const Color(0xFFF2F3F5),
      appBar: AppBar(
        backgroundColor: const Color(0xFF39B54A),
        foregroundColor: Colors.white,
        elevation: 0,
        title: const Text(
          'Dashboard Principal',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
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
      body: Column(
        children: <Widget>[
          const ModeBanner(),
          Expanded(
            child: MaxWidthBox(
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: <Widget>[
                  const _WelcomeBanner(),
                  const SizedBox(height: 16),
                  const Text(
                    'Valores actuales del laboratorio',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 12),
                  GridView.count(
                    crossAxisCount: 2,
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    mainAxisSpacing: 12,
                    crossAxisSpacing: 12,
                    childAspectRatio: 1.15,
                    children: const <Widget>[
                      _MetricCard(
                        icon: Icons.thermostat,
                        color: Color(0xFF2E7D32),
                        bgColor: Color(0xFFE8F5E9),
                        label: 'Temperatura',
                        value: '22.8',
                        unit: '°C',
                      ),
                      _MetricCard(
                        icon: Icons.science_outlined,
                        color: Color(0xFFC62828),
                        bgColor: Color(0xFFFFEBEE),
                        label: 'pH',
                        value: '5.9',
                        unit: '',
                      ),
                      _MetricCard(
                        icon: Icons.graphic_eq,
                        color: Color(0xFFE65100),
                        bgColor: Color(0xFFFFF3E0),
                        label: 'Conductividad',
                        value: '1.59',
                        unit: 'mS/cm',
                      ),
                      _MetricCard(
                        icon: Icons.water_drop_outlined,
                        color: Color(0xFF1565C0),
                        bgColor: Color(0xFFE3F2FD),
                        label: 'Nivel de Agua',
                        value: '72',
                        unit: '%',
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  const _SystemStatusCard(),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
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

class _WelcomeBanner extends StatelessWidget {
  const _WelcomeBanner();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF39B54A),
        borderRadius: BorderRadius.circular(16),
      ),
      child: const Row(
        children: <Widget>[
          CircleAvatar(
            radius: 26,
            backgroundColor: Colors.white24,
            child: Icon(Icons.insights, color: Colors.white, size: 30),
          ),
          SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text(
                  'Bienvenido de nuevo',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 2),
                Text(
                  'Estos son los valores actuales de tu laboratorio',
                  style: TextStyle(color: Colors.white70, fontSize: 12),
                ),
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
    required this.bgColor,
    required this.label,
    required this.value,
    required this.unit,
  });

  final IconData icon;
  final Color color;
  final Color bgColor;
  final String label;
  final String value;
  final String unit;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: <Widget>[
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: bgColor,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: color, size: 22),
              ),
              const Icon(Icons.more_vert, color: Colors.grey, size: 18),
            ],
          ),
          const Spacer(),
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 13)),
          const SizedBox(height: 4),
          Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: <Widget>[
              Text(
                value,
                style: TextStyle(
                  color: color,
                  fontSize: 24,
                  fontWeight: FontWeight.w800,
                ),
              ),
              if (unit.isNotEmpty) ...<Widget>[
                const SizedBox(width: 3),
                Text(unit, style: TextStyle(color: color, fontSize: 13)),
              ],
            ],
          ),
        ],
      ),
    );
  }
}

class _SystemStatusCard extends StatelessWidget {
  const _SystemStatusCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(
            'Estado del sistema',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 12),
          _StatusRow(
            icon: Icons.check_circle,
            color: Color(0xFF2E7D32),
            text: 'Sensores operativos',
          ),
          SizedBox(height: 10),
          _StatusRow(
            icon: Icons.check_circle,
            color: Color(0xFF2E7D32),
            text: 'Sincronización en línea',
          ),
          SizedBox(height: 10),
          _StatusRow(
            icon: Icons.notifications_active,
            color: Color(0xFFE65100),
            text: '3 alertas de la última semana',
          ),
        ],
      ),
    );
  }
}

class _StatusRow extends StatelessWidget {
  const _StatusRow({
    required this.icon,
    required this.color,
    required this.text,
  });

  final IconData icon;
  final Color color;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: <Widget>[
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 10),
        Expanded(child: Text(text, style: const TextStyle(fontSize: 14))),
      ],
    );
  }
}
