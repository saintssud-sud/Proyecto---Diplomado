import 'package:flutter/material.dart';

/// Estado de una vista que consume datos del servicio.
///
/// Son cuatro y se diseñan, no se improvisan: el usuario debe saber siempre si
/// la información está en camino, si llegó, si todavía no existe o si la
/// operación falló.
enum EstadoVista {
  /// La petición está en curso.
  cargando,

  /// Llegaron datos y hay algo que mostrar.
  conDatos,

  /// La petición fue exitosa pero no hay información todavía.
  vacio,

  /// La operación no pudo completarse.
  error,
}

/// Presenta una vista según su estado.
///
/// Envuelve el contenido real de cada pantalla y resuelve los tres estados que
/// no son el caso feliz. Distingue de forma explícita el **fallo de conexión**
/// del **rechazo del servidor**: son dos situaciones con soluciones distintas
/// para el usuario, y presentar el mismo mensaje para ambas lo deja sin saber
/// qué hacer.
class VistaConEstados<T> extends StatelessWidget {
  const VistaConEstados({
    super.key,
    required this.estado,
    required this.alMostrarDatos,
    required this.mensajeVacio,
    this.datos,
    this.mensajeError,
    this.errorDeConexion = false,
    this.alReintentar,
    this.mensajeCargando = 'Cargando información…',
    this.tituloVacio = 'Todavía no hay información',
    this.contenidoVacio,
  });

  /// Estado actual de la vista.
  final EstadoVista estado;

  /// Datos a presentar cuando el estado es [EstadoVista.conDatos].
  final T? datos;

  /// Construye el contenido real de la pantalla con los datos recibidos.
  final Widget Function(BuildContext contexto, T datos) alMostrarDatos;

  /// Explica al usuario qué hacer para que haya información.
  ///
  /// Un estado vacío sin indicación deja al usuario sin saber si el sistema
  /// falló o si simplemente aún no registró nada.
  final String mensajeVacio;

  /// Mensaje del estado de error; si no se indica, se usa uno según el tipo.
  final String? mensajeError;

  /// Indica si el error fue de conexión y no un rechazo del servidor.
  final bool errorDeConexion;

  /// Acción de reintento; si es nula, el estado de error no ofrece el botón.
  final VoidCallback? alReintentar;

  final String mensajeCargando;
  final String tituloVacio;

  /// Contenido propio para el estado vacío.
  ///
  /// Se usa cuando «no hay datos» no basta como respuesta: el panel, por
  /// ejemplo, ofrece en ese caso cambiar de módulo de cultivo, porque el módulo
  /// vigente puede estar sin lecturas mientras otro sí las tiene.
  final Widget Function(BuildContext contexto)? contenidoVacio;

  @override
  Widget build(BuildContext context) {
    switch (estado) {
      case EstadoVista.cargando:
        return _Centrado(
          icono: null,
          titulo: null,
          mensaje: mensajeCargando,
          progreso: true,
        );

      case EstadoVista.conDatos:
        final T? contenido = datos;
        if (contenido == null) {
          return _Centrado(
            icono: Icons.info_outline,
            titulo: 'Sin información',
            mensaje: 'El servicio no devolvió datos para esta consulta.',
            alReintentar: alReintentar,
          );
        }
        return alMostrarDatos(context, contenido);

      case EstadoVista.vacio:
        // Una pantalla puede necesitar algo más que el mensaje cuando no hay
        // datos: por ejemplo, el panel ofrece elegir otro módulo de cultivo, que
        // es la salida natural si el módulo vigente todavía no tiene lecturas.
        if (contenidoVacio != null) {
          return contenidoVacio!(context);
        }
        return _Centrado(
          icono: Icons.inbox_outlined,
          titulo: tituloVacio,
          mensaje: mensajeVacio,
          alReintentar: alReintentar,
          etiquetaAccion: 'Actualizar',
        );

      case EstadoVista.error:
        return _Centrado(
          icono: errorDeConexion ? Icons.cloud_off : Icons.error_outline,
          titulo: errorDeConexion
              ? 'No se pudo conectar con el servidor'
              : 'La operación no pudo completarse',
          mensaje: mensajeError ?? _mensajeDeErrorPorDefecto,
          pista: errorDeConexion
              ? 'Revise la conexión e intente nuevamente.'
              : 'Si el problema continúa, comuníquese con el administrador.',
          alReintentar: alReintentar,
          etiquetaAccion: 'Reintentar',
        );
    }
  }

  String get _mensajeDeErrorPorDefecto => errorDeConexion
      ? 'La petición no llegó al servidor.'
      : 'El servidor rechazó la operación.';
}

/// Contenido centrado que usan los estados que no muestran datos.
class _Centrado extends StatelessWidget {
  const _Centrado({
    required this.mensaje,
    this.icono,
    this.titulo,
    this.pista,
    this.alReintentar,
    this.etiquetaAccion = 'Reintentar',
    this.progreso = false,
  });

  final String mensaje;
  final IconData? icono;
  final String? titulo;
  final String? pista;
  final VoidCallback? alReintentar;
  final String etiquetaAccion;
  final bool progreso;

  @override
  Widget build(BuildContext context) {
    final ThemeData tema = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            if (progreso) ...<Widget>[
              const CircularProgressIndicator(),
              const SizedBox(height: 16),
            ] else if (icono != null) ...<Widget>[
              Icon(icono, size: 48, color: tema.colorScheme.primary),
              const SizedBox(height: 12),
            ],
            if (titulo != null) ...<Widget>[
              Text(
                titulo!,
                textAlign: TextAlign.center,
                style: tema.textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
            ],
            Text(
              mensaje,
              textAlign: TextAlign.center,
              style: tema.textTheme.bodyMedium,
            ),
            if (pista != null) ...<Widget>[
              const SizedBox(height: 8),
              Text(
                pista!,
                textAlign: TextAlign.center,
                style: tema.textTheme.bodySmall,
              ),
            ],
            if (alReintentar != null) ...<Widget>[
              const SizedBox(height: 20),
              FilledButton.tonalIcon(
                onPressed: alReintentar,
                icon: const Icon(Icons.refresh),
                label: Text(etiquetaAccion),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
