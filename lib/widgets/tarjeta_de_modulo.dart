import 'package:flutter/material.dart';

import '../models/api/modelos_api.dart';

/// Tarjeta con los datos de un módulo de cultivo.
///
/// Se usa en **dos** lugares: la pantalla de módulos, donde cada tarjeta lleva
/// sus acciones, y el panel de inicio, donde resume el módulo vigente.
///
/// Compartir el componente tiene una razón concreta: antes solo la pantalla de
/// módulos detallaba el cultivo, el perfil de referencia y la ubicación, de modo
/// que el panel mostraba el mismo módulo con menos información que la pantalla
/// que lo administra. Un usuario que llegaba al panel no podía saber con qué
/// rangos se estaban evaluando las lecturas que veía.
class TarjetaDeModulo extends StatelessWidget {
  const TarjetaDeModulo({
    super.key,
    required this.modulo,
    this.acciones,
    this.mostrarNombreDelPerfil = true,
    this.margin = const EdgeInsets.only(bottom: 12),
  });

  final ModuloCultivo modulo;

  /// Widget situado a la derecha de la tarjeta: el menú de acciones en la
  /// pantalla de módulos, o nada en el panel de inicio.
  final Widget? acciones;

  /// Si se muestra el renglón del perfil de referencia.
  ///
  /// El panel de inicio lo oculta cuando coincide con el tipo de cultivo, para
  /// no repetir dos veces el mismo dato.
  final bool mostrarNombreDelPerfil;

  final EdgeInsets margin;

  @override
  Widget build(BuildContext context) {
    final bool activo = modulo.activo;
    final Color color =
        activo ? const Color(0xFF2E7D32) : const Color(0xFF757575);
    final String? ubicacion = modulo.ubicacion;
    final bool mostrarPerfil = mostrarNombreDelPerfil &&
        modulo.perfilNombre.isNotEmpty &&
        modulo.perfilNombre != modulo.tipoCultivo;

    return Card(
      margin: margin,
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
                  if (mostrarPerfil)
                    InfoDeModulo(
                      icon: Icons.science_outlined,
                      text: modulo.perfilNombre,
                    ),
                  if (ubicacion != null && ubicacion.isNotEmpty)
                    InfoDeModulo(icon: Icons.place_outlined, text: ubicacion),
                ],
              ),
            ),
            if (acciones != null) acciones!,
          ],
        ),
      ),
    );
  }
}

/// Renglón con ícono y texto: los datos secundarios de un módulo.
class InfoDeModulo extends StatelessWidget {
  const InfoDeModulo({super.key, required this.icon, required this.text});

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
