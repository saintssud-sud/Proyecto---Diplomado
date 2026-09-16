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
      // 127.0.0.1 y no "localhost": en Windows, "localhost" puede resolverse
      // como IPv6 (::1) y el servicio escucha solo en IPv4, de modo que la
      // petición se rechaza aunque el servicio esté en pie.
      return 'http://127.0.0.1:8011';
    }
    if (defaultTargetPlatform == TargetPlatform.android) {
      // El emulador de Android alcanza al equipo anfitrión por 10.0.2.2.
      return 'http://10.0.2.2:8011';
    }
    return 'http://127.0.0.1:8011';
  }

  /// Prefijo de versión del contrato que consume la aplicación.
  static const String versionApi = 'v1';

  /// Ruta completa de un recurso, incluido el prefijo de versión.
  static String ruta(String recurso) {
    final String limpio = recurso.startsWith('/') ? recurso.substring(1) : recurso;
    return '/api/$versionApi/$limpio';
  }

  /// Tiempo máximo de espera de una petición.
  ///
  /// Se admiten 45 segundos y no 20 porque la **primera** consulta después de
  /// arrancar el servicio abre la conexión con Cloud Firestore, y ese arranque
  /// en frío puede tardar entre 25 y 30 segundos. Un límite menor hacía que la
  /// primera pantalla fallara con «la petición excedió el tiempo de espera»
  /// aunque el servicio estuviera funcionando: el usuario veía un fallo de
  /// conexión donde solo había una espera. Las consultas siguientes responden en
  /// pocos segundos, de modo que el límite amplio solo actúa en ese primer caso.
  static const Duration esperaMaxima = Duration(seconds: 45);
}
