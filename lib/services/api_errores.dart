/// Errores de la capa de API.
///
/// El sistema distingue dos situaciones que no deben confundirse en la interfaz:
/// que la operación haya sido **rechazada por el servidor** y que la petición
/// **no haya podido completarse** por un problema de conexión. Son dos mensajes
/// distintos porque exigen dos acciones distintas del usuario.
library;

/// Error devuelto por la API con el formato del contrato del backend.
///
/// El backend responde `{"codigo": "...", "mensaje": "...", "detalle": {...}}`
/// con el código HTTP correspondiente. Cuando la respuesta es de validación
/// (422), [campos] contiene el detalle por campo rechazado, listo para mostrar
/// junto al dato que el usuario debe corregir.
class ErrorApi implements Exception {
  const ErrorApi({
    required this.estado,
    required this.codigo,
    required this.mensaje,
    this.campos = const <String, String>{},
  });

  /// Código HTTP de la respuesta.
  final int estado;

  /// Código estable definido por el contrato (`no_autenticado`, `sin_permiso`,
  /// `no_encontrado`, `conflicto`, `validacion_rechazada`, `datos_invalidos`).
  final String codigo;

  /// Mensaje redactado por el servidor.
  final String mensaje;

  /// Detalle por campo rechazado, en las respuestas de validación.
  final Map<String, String> campos;

  /// El token de identidad falta, es inválido o expiró.
  bool get esNoAutenticado => estado == 401;

  /// La cuenta no tiene permiso para la operación solicitada.
  bool get esSinPermiso => estado == 403;

  /// El recurso solicitado no existe.
  bool get esNoEncontrado => estado == 404;

  /// La operación entra en conflicto con el estado actual del sistema.
  bool get esConflicto => estado == 409;

  /// Los datos enviados no cumplen el contrato.
  bool get esValidacion => estado == 422;

  /// Mensaje que puede presentarse al usuario sin exponer detalles técnicos.
  String get mensajeParaUsuario => mensaje.trim().isNotEmpty
      ? mensaje
      : 'La operación no pudo completarse.';

  @override
  String toString() => 'ErrorApi($estado, $codigo): $mensaje';
}

/// Error de conexión: la petición no llegó a completarse.
///
/// Se produce cuando no hay red, cuando el servicio no responde o cuando la
/// respuesta tarda más de lo admitido. No es un rechazo del servidor: el
/// servidor puede no haberse enterado de la petición.
class ErrorConexion implements Exception {
  const ErrorConexion(this.mensaje, {this.causa});

  final String mensaje;

  /// Excepción original, útil en el registro pero no para el usuario.
  final Object? causa;

  /// Mensaje orientado al usuario, con la acción que puede tomar.
  String get mensajeParaUsuario =>
      'No se pudo comunicar con el servidor. Revise la conexión e intente nuevamente.';

  @override
  String toString() => 'ErrorConexion: $mensaje';
}
