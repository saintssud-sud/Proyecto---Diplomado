import '../services/api_errores.dart';

/// Traducción de un fallo de la capa de API a lo que la vista debe presentar.
///
/// Los controladores no interpretan excepciones cada uno por su cuenta: piden
/// esta traducción, de modo que todos los mensajes del sistema sean coherentes.
/// La distinción importante es si el fallo fue **de conexión** —la petición no
/// llegó al servidor y reintentar puede resolverlo— o un **rechazo del
/// servidor**, que exige corregir algo antes de volver a intentarlo.
class FalloDeVista {
  const FalloDeVista(this.mensaje, {required this.deConexion});

  /// Mensaje presentable al usuario.
  final String mensaje;

  /// Indica si el origen del fallo fue la conexión.
  final bool deConexion;

  /// Traduce cualquier error de la capa de API.
  static FalloDeVista desde(Object error) {
    if (error is ErrorConexion) {
      return FalloDeVista(error.mensajeParaUsuario, deConexion: true);
    }
    if (error is ErrorApi) {
      return FalloDeVista(error.mensajeParaUsuario, deConexion: false);
    }
    if (error is ErrorDeContrato) {
      return const FalloDeVista(
        'La respuesta del servidor no pudo interpretarse. Vuelva a intentarlo.',
        deConexion: true,
      );
    }
    return const FalloDeVista(
      'Ocurrió un error no previsto. Vuelva a intentarlo.',
      deConexion: true,
    );
  }
}
