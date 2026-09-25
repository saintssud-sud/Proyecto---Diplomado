import 'package:flutter/material.dart';

/// Encabezado del menú lateral: identifica al sistema y a la cuenta que tiene
/// la sesión iniciada.
///
/// Recibe el nombre y la etiqueta del rol **ya resueltos**. El widget no conoce
/// ningún nombre de rol ni lo deduce del correo: el rol lo determina el servicio
/// y aquí solo se presenta el texto que ese rol recibe en el catálogo. Por eso,
/// cuando la etiqueta no se conoce —al cargar o sin conexión— el distintivo no
/// se dibuja en lugar de mostrar un valor supuesto.
class EncabezadoDeMenu extends StatelessWidget {
  const EncabezadoDeMenu({super.key, required this.nombre, this.etiquetaRol});

  /// Nombre presentable de la cuenta con la sesión iniciada.
  final String nombre;

  /// Texto del rol —por ejemplo «Administrador»— o `null` si aún no se conoce.
  final String? etiquetaRol;

  @override
  Widget build(BuildContext context) {
    final String? rol = etiquetaRol;

    return DrawerHeader(
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
                'SI.G.VA.C.H.',
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
            'Hola, $nombre',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
          if (rol != null) ...<Widget>[
            const SizedBox(height: 6),
            _EtiquetaDeRol(texto: rol),
          ],
        ],
      ),
    );
  }
}

/// Distintivo con el tipo de rol de la cuenta.
class _EtiquetaDeRol extends StatelessWidget {
  const _EtiquetaDeRol({required this.texto});

  final String texto;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.22),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withValues(alpha: 0.65)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          const Icon(Icons.badge_outlined, size: 14, color: Colors.white),
          const SizedBox(width: 6),
          Text(
            texto,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
