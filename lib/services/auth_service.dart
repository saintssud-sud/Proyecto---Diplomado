import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';

/// Servicio de autenticación con Firebase Authentication.
///
/// Reemplaza al antiguo AuthService de Supabase. Expone las mismas
/// operaciones (signIn, signUp, signOut) pero usando Firebase Auth
/// con correo y contraseña.
class AuthService {
  AuthService({FirebaseAuth? auth}) : _auth = auth ?? FirebaseAuth.instance;

  final FirebaseAuth _auth;

  /// Aviso que la pantalla de inicio de sesión muestra cuando la sesión se
  /// cerró **por rechazo del servicio** y no por decisión del usuario.
  ///
  /// Es estático a propósito: las pantallas crean sus propias instancias de
  /// [AuthService] y todas comparten la misma sesión de Firebase, así que el
  /// aviso tiene que vivir en el mismo lugar que esa sesión.
  static final ValueNotifier<String?> aviso =
      ValueNotifier<String?>(null);

  /// Instancia interna de FirebaseAuth (para streams y usuario actual).
  FirebaseAuth get auth => _auth;

  /// Usuario actualmente autenticado (null si no hay sesión).
  User? get currentUser => _auth.currentUser;

  /// Stream de cambios de sesión. Emite el usuario cuando inicia/cierra
  /// sesión. Se usa en [AuthGate] para decidir qué pantalla mostrar.
  Stream<User?> get authStateChanges => _auth.authStateChanges();

  /// Cierra la sesión porque el servicio respondió 401.
  ///
  /// Deja el aviso puesto para que quien vuelva a la pantalla de inicio de
  /// sesión entienda por qué se cerró: sin ese mensaje, el usuario ve que lo
  /// sacaron del sistema y no sabe si fue un error suyo.
  Future<void> cerrarSesionPorExpiracion() async {
    aviso.value = 'Tu sesión venció. Volvé a iniciar sesión.';
    await signOut();
  }

  /// Consume el aviso, si había uno. Devuelve el mensaje y lo limpia.
  static String? consumirAviso() {
    final String? mensaje = aviso.value;
    aviso.value = null;
    return mensaje;
  }

  /// Inicia sesión con correo y contraseña.
  Future<void> signIn({required String email, required String password}) async {
    await _auth.signInWithEmailAndPassword(
      email: email.trim(),
      password: password,
    );
  }

  /// Crea una cuenta nueva y guarda el nombre en el perfil (displayName).
  Future<String> signUp({
    required String email,
    required String password,
    String? fullName,
  }) async {
    final credential = await _auth.createUserWithEmailAndPassword(
      email: email.trim(),
      password: password,
    );

    final name = fullName?.trim() ?? '';
    if (name.isNotEmpty) {
      // Guarda el nombre en el perfil del usuario (Firebase Auth).
      await credential.user?.updateDisplayName(name);
      await credential.user?.reload();
    }

    return 'Cuenta creada y sesion iniciada.';
  }

  /// Cierra la sesión actual.
  Future<void> signOut() => _auth.signOut();
}
