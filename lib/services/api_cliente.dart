import 'dart:async';
import 'dart:convert';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import 'api_errores.dart';

/// Devuelve el token de identidad de la sesión actual, o `null` si no hay sesión.
typedef ObtenerToken = Future<String?> Function();

/// Cliente de la API del backend.
///
/// Concentra tres responsabilidades: adjuntar el token de identidad a cada
/// petición, traducir las respuestas de error del contrato a [ErrorApi] y
/// distinguir el fallo de conexión ([ErrorConexion]) del rechazo del servidor.
/// Las pantallas no arman cabeceras ni interpretan códigos: piden datos y
/// reciben datos o una excepción con un mensaje presentable.
class ApiCliente {
  ApiCliente({
    http.Client? cliente,
    ObtenerToken? obtenerToken,
    String? baseUrl,
    Duration? espera,
  })  : _cliente = cliente ?? http.Client(),
        _obtenerToken = obtenerToken ?? _tokenDeFirebase,
        _baseUrl = _sinBarraFinal(baseUrl ?? ApiConfig.baseUrl),
        _espera = espera ?? ApiConfig.esperaMaxima;

  final http.Client _cliente;
  final ObtenerToken _obtenerToken;
  final String _baseUrl;
  final Duration _espera;

  /// Dirección base que está utilizando el cliente.
  String get baseUrl => _baseUrl;

  static Future<String?> _tokenDeFirebase() async =>
      FirebaseAuth.instance.currentUser?.getIdToken();

  static String _sinBarraFinal(String valor) =>
      valor.endsWith('/') ? valor.substring(0, valor.length - 1) : valor;

  /// Libera el cliente HTTP subyacente.
  void cerrar() => _cliente.close();

  // --- Operaciones del contrato -------------------------------------------

  /// Consulta un recurso y devuelve el cuerpo ya decodificado.
  Future<dynamic> obtener(
    String ruta, {
    Map<String, String>? parametros,
    bool autenticada = true,
  }) {
    return _enviar('GET', ruta, parametros: parametros, autenticada: autenticada);
  }

  /// Consulta un recurso que devuelve un objeto.
  Future<Map<String, dynamic>> obtenerMapa(
    String ruta, {
    Map<String, String>? parametros,
    bool autenticada = true,
  }) async {
    final dynamic datos =
        await _enviar('GET', ruta, parametros: parametros, autenticada: autenticada);
    return _comoMapa(datos);
  }

  /// Consulta un recurso que devuelve una lista de objetos.
  Future<List<Map<String, dynamic>>> obtenerLista(
    String ruta, {
    Map<String, String>? parametros,
    bool autenticada = true,
  }) async {
    final dynamic datos =
        await _enviar('GET', ruta, parametros: parametros, autenticada: autenticada);
    if (datos is List) {
      return datos.whereType<Map<String, dynamic>>().toList(growable: false);
    }
    throw _respuestaInesperada();
  }

  /// Crea un recurso.
  Future<Map<String, dynamic>> crear(
    String ruta,
    Map<String, dynamic> cuerpo, {
    bool autenticada = true,
  }) async {
    final dynamic datos =
        await _enviar('POST', ruta, cuerpo: cuerpo, autenticada: autenticada);
    return _comoMapa(datos);
  }

  /// Modifica parcialmente un recurso.
  Future<Map<String, dynamic>> actualizar(
    String ruta,
    Map<String, dynamic> cuerpo, {
    bool autenticada = true,
  }) async {
    final dynamic datos =
        await _enviar('PATCH', ruta, cuerpo: cuerpo, autenticada: autenticada);
    return _comoMapa(datos);
  }

  /// Elimina un recurso.
  Future<void> eliminar(String ruta, {bool autenticada = true}) async {
    await _enviar('DELETE', ruta, autenticada: autenticada);
  }

  /// Descarga un recurso binario, como la exportación en CSV.
  Future<List<int>> obtenerBytes(
    String ruta, {
    Map<String, String>? parametros,
    bool autenticada = true,
  }) async {
    final http.Response respuesta = await _ejecutar(
      'GET',
      ruta,
      parametros: parametros,
      autenticada: autenticada,
    );
    if (respuesta.statusCode >= 400) {
      throw _errorDesdeRespuesta(respuesta);
    }
    return respuesta.bodyBytes;
  }

  // --- Interno ------------------------------------------------------------

  Future<dynamic> _enviar(
    String metodo,
    String ruta, {
    Map<String, String>? parametros,
    Object? cuerpo,
    bool autenticada = true,
  }) async {
    final http.Response respuesta = await _ejecutar(
      metodo,
      ruta,
      parametros: parametros,
      cuerpo: cuerpo,
      autenticada: autenticada,
    );
    if (respuesta.statusCode >= 400) {
      throw _errorDesdeRespuesta(respuesta);
    }
    return _decodificar(respuesta);
  }

  Future<http.Response> _ejecutar(
    String metodo,
    String ruta, {
    Map<String, String>? parametros,
    Object? cuerpo,
    bool autenticada = true,
    Duration? espera,
  }) async {
    final Map<String, String> cabeceras = <String, String>{
      'Accept': 'application/json',
      if (cuerpo != null) 'Content-Type': 'application/json; charset=utf-8',
    };

    if (autenticada) {
      final String? token;
      try {
        token = await _obtenerToken();
      } catch (error) {
        // Si el proveedor de identidad no está disponible, el acceso se niega
        // con un mensaje claro en lugar de propagar un error inesperado.
        throw ErrorConexion(
          'No se pudo obtener la sesión del usuario.',
          causa: error,
        );
      }
      if (token == null || token.isEmpty) {
        // Se resuelve antes de salir a la red: sin sesión no hay nada que pedir.
        throw const ErrorApi(
          estado: 401,
          codigo: 'no_autenticado',
          mensaje: 'No hay una sesión iniciada.',
        );
      }
      cabeceras['Authorization'] = 'Bearer $token';
    }

    final Uri uri = _uri(ruta, parametros);
    try {
      return await _peticion(metodo, uri, cabeceras, cuerpo).timeout(espera ?? _espera);
    } on TimeoutException catch (error) {
      throw ErrorConexion('La petición excedió el tiempo de espera.', causa: error);
    } on http.ClientException catch (error) {
      throw ErrorConexion('Falló la conexión con el servicio.', causa: error);
    } on Exception catch (error) {
      // Cubre los errores de socket y de resolución de nombres.
      throw ErrorConexion('No se pudo completar la petición.', causa: error);
    }
  }

  Future<http.Response> _peticion(
    String metodo,
    Uri uri,
    Map<String, String> cabeceras,
    Object? cuerpo,
  ) {
    final String? datos = cuerpo == null ? null : jsonEncode(cuerpo);
    switch (metodo) {
      case 'GET':
        return _cliente.get(uri, headers: cabeceras);
      case 'POST':
        return _cliente.post(uri, headers: cabeceras, body: datos);
      case 'PATCH':
        return _cliente.patch(uri, headers: cabeceras, body: datos);
      case 'DELETE':
        return _cliente.delete(uri, headers: cabeceras, body: datos);
      default:
        throw ArgumentError.value(metodo, 'metodo', 'Método HTTP no admitido');
    }
  }

  Uri _uri(String ruta, Map<String, String>? parametros) {
    final String camino = ruta.startsWith('/') ? ruta : '/$ruta';
    final Uri base = Uri.parse('$_baseUrl$camino');
    if (parametros == null || parametros.isEmpty) {
      return base;
    }
    final Map<String, String> conValor = <String, String>{
      for (final MapEntry<String, String> entrada in parametros.entries)
        if (entrada.value.isNotEmpty) entrada.key: entrada.value,
    };
    if (conValor.isEmpty) {
      return base;
    }
    return base.replace(
      queryParameters: <String, String>{...base.queryParameters, ...conValor},
    );
  }

  dynamic _decodificar(http.Response respuesta) {
    if (respuesta.bodyBytes.isEmpty) {
      return null;
    }
    // Se decodifica explícitamente como UTF-8: el servicio no declara el juego
    // de caracteres en la cabecera y http asumiría latin-1, lo que rompería
    // los acentos de los mensajes.
    final String texto = utf8.decode(respuesta.bodyBytes, allowMalformed: true).trim();
    if (texto.isEmpty) {
      return null;
    }
    try {
      return jsonDecode(texto);
    } on FormatException catch (error) {
      throw ErrorConexion(
        'El servicio devolvió una respuesta que no pudo interpretarse.',
        causa: error,
      );
    }
  }

  ErrorApi _errorDesdeRespuesta(http.Response respuesta) {
    dynamic cuerpo;
    try {
      cuerpo = _decodificar(respuesta);
    } on ErrorConexion {
      cuerpo = null;
    }

    if (cuerpo is Map<String, dynamic>) {
      return ErrorApi(
        estado: respuesta.statusCode,
        codigo: cuerpo['codigo']?.toString() ?? 'error_desconocido',
        mensaje: cuerpo['mensaje']?.toString() ?? 'La operación no pudo completarse.',
        campos: _camposDe(cuerpo['detalle']),
      );
    }

    return ErrorApi(
      estado: respuesta.statusCode,
      codigo: 'error_desconocido',
      mensaje: 'La operación no pudo completarse (código ${respuesta.statusCode}).',
    );
  }

  /// Extrae el detalle por campo de la respuesta de validación.
  Map<String, String> _camposDe(Object? detalle) {
    if (detalle is Map && detalle['campos'] is Map) {
      final Map<dynamic, dynamic> campos = detalle['campos'] as Map<dynamic, dynamic>;
      return campos.map(
        (dynamic clave, dynamic valor) =>
            MapEntry<String, String>(clave.toString(), valor.toString()),
      );
    }
    return const <String, String>{};
  }

  Map<String, dynamic> _comoMapa(dynamic datos) {
    if (datos is Map<String, dynamic>) {
      return datos;
    }
    throw _respuestaInesperada();
  }

  ErrorApi _respuestaInesperada() => const ErrorApi(
        estado: 200,
        codigo: 'respuesta_inesperada',
        mensaje: 'El servidor devolvió una respuesta con una forma no esperada.',
      );
}
