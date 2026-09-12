import 'package:firebase_auth/firebase_auth.dart';

/// Servicio de autenticación con Firebase Authentication.
///
/// Reemplaza al antiguo AuthService de Supabase. Expone las mismas
/// operaciones (signIn, signUp, signOut) pero usando Firebase Auth
/// con correo y contraseña.
class AuthService {
  AuthService({FirebaseAuth? auth}) : _auth = auth ?? FirebaseAuth.instance;

  final FirebaseAuth _auth;

  /// Instancia interna de FirebaseAuth (para streams y usuario actual).
  FirebaseAuth get auth => _auth;

  /// Usuario actualmente autenticado (null si no hay sesión).
  User? get currentUser => _auth.currentUser;

  /// Stream de cambios de sesión. Emite el usuario cuando inicia/cierra
  /// sesión. Se usa en [AuthGate] para decidir qué pantalla mostrar.
  Stream<User?> get authStateChanges => _auth.authStateChanges();

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
