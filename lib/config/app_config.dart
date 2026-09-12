/// Configuración de la aplicación.
///
/// Antes este proyecto dependía de Supabase (URL + publishable key) que se
/// cargaban con --dart-define o desde un asset. Desde la migración a
/// Firebase/Firestore la configuración va incrustada en
/// `lib/firebase_options.dart`, así que ya no hace falta cargar claves en
/// tiempo de ejecución.
class AppConfig {
  const AppConfig({this.firebaseReady = true, this.modeLabel = 'FIREBASE'});

  /// Indica si Firebase se inicializó correctamente al arrancar.
  final bool firebaseReady;

  /// Etiqueta de modo que se muestra en la pantalla de preferencias.
  final String modeLabel;

  bool get isConfigured => firebaseReady;
}
