import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../controllers/preferences_controller.dart';
import '../../models/alerta.dart';
import 'alerta_detalle_screen.dart';

/// Pantalla 4 — Alertas con pestañas Activas / Historial.
class AlertasScreen extends StatelessWidget {
  const AlertasScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final preferences = context.watch<PreferencesController>();
    final activas = preferences.alertas
        .where((a) => a.estado == 'Activa')
        .toList();
    final historial = preferences.alertas
        .where((a) => a.estado == 'Resuelta')
        .toList();

    return DefaultTabController(
      length: 2,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          const Padding(
            padding: EdgeInsets.fromLTRB(16, 16, 16, 0),
            child: Text(
              'Alertas',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
          ),
          const TabBar(
            tabs: <Widget>[
              Tab(text: 'Activas'),
              Tab(text: 'Historial'),
            ],
            labelColor: Color(0xFF2E7D32),
            unselectedLabelColor: Colors.grey,
            indicatorColor: Color(0xFF2E7D32),
          ),
          Expanded(
            child: TabBarView(
              children: <Widget>[
                _ListaAlertas(
                  alertas: activas,
                  vacio: 'No hay alertas activas',
                ),
                _ListaAlertas(
                  alertas: historial,
                  vacio: 'No hay alertas en el historial',
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ListaAlertas extends StatelessWidget {
  const _ListaAlertas({required this.alertas, required this.vacio});

  final List<Alerta> alertas;
  final String vacio;

  @override
  Widget build(BuildContext context) {
    if (alertas.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(
            vacio,
            textAlign: TextAlign.center,
            style: const TextStyle(color: Colors.grey),
          ),
        ),
      );
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: alertas
          .map(
            (alerta) => _AlertaCard(
              alerta: alerta,
              onTap: () {
                Navigator.push<void>(
                  context,
                  MaterialPageRoute<void>(
                    builder: (routeContext) =>
                        AlertaDetalleScreen(alerta: alerta),
                  ),
                );
              },
            ),
          )
          .toList(),
    );
  }
}

class _AlertaCard extends StatelessWidget {
  const _AlertaCard({required this.alerta, required this.onTap});

  final Alerta alerta;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final critica = alerta.critica;
    final color = critica ? Colors.red : const Color(0xFF2E7D32);
    final icono = critica
        ? Icons.warning_amber_rounded
        : Icons.check_circle_outline;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: color.withValues(alpha: 0.3)),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Icon(icono, color: color, size: 28),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Text(
                      alerta.titulo,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      alerta.nivelActual,
                      style: const TextStyle(
                        color: Colors.black87,
                        fontSize: 13,
                      ),
                    ),
                    Text(
                      alerta.rangoPermitido,
                      style: const TextStyle(color: Colors.grey, fontSize: 13),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      alerta.fecha,
                      style: const TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: Colors.grey),
            ],
          ),
        ),
      ),
    );
  }
}
