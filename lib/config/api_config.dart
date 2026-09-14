import 'package:flutter/foundation.dart';

/// Configuración de acceso a la API del backend.
///
/// La dirección del servicio se define en tiempo de compilación, no en el
/// código, para que el mismo código fuente apunte al backend local o al
/// desplegado sin necesidad de editarlo:
///
/// ```bash
/// flutter build web --dart-define=API_BASE_URL=https://sigvach-api.onrender.com
/// ```
///
/// Si no se define, se usa una dirección local adecuada al dispositivo:
/// `10.0.2.2` en el emulador de Android (que es como ese emulador ve al equipo
/// anfitrión) y `localhost` en la web y el escritorio.
class ApiConfig {
  const ApiConfig._();

  /// Valor recibido por `--dart-define=API_BASE_URL=...`, vacío si no se definió.
  static const String _definida = String.fromEnvironment('API_BASE_URL');

  /// Dirección base del servicio, sin barra final.
  static String get baseUrl {
    final String elegida = _definida.trim().isNotEmpty ? _definida : _localPorDefecto;
    return elegida.endsWith('/') ? elegida.substring(0, elegida.length - 1) : elegida;
  }

  /// Indica si la dirección provino de la configuración de compilación.
  static bool get estaConfigurada => _definida.trim().isNotEmpty;

  static String get _localPorDefecto {
    if (kIsWeb) {
      return 'http://localhost:8000';
    }
    if (defaultTargetPlatform == TargetPlatform.android) {
      // El emulador de Android alcanza al equipo anfitrión por 10.0.2.2.
      return 'http://10.0.2.2:8000';
    }
    return 'http://localhost:8000';
  }

  /// Prefijo de versión del contrato que consume la aplicación.
  static const String versionApi = 'v1';

  /// Ruta completa de un recurso, incluido el prefijo de versión.
  static String ruta(String recurso) {
    final String limpio = recurso.startsWith('/') ? recurso.substring(1) : recurso;
    return '/api/$versionApi/$limpio';
  }

  /// Tiempo máximo de espera de una petición.
  static const Duration esperaMaxima = Duration(seconds: 20);
}
