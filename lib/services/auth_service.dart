import 'package:supabase_flutter/supabase_flutter.dart';

class AuthService {
  AuthService(this.client);

  final SupabaseClient client;

  Future<void> signIn({required String email, required String password}) async {
    await client.auth.signInWithPassword(
      email: email.trim(),
      password: password,
    );
  }

  Future<String> signUp({
    required String email,
    required String password,
    String? fullName,
  }) async {
    final response = await client.auth.signUp(
      email: email.trim(),
      password: password,
      // Guarda el nombre en los metadatos del usuario (auth.users).
      data: (fullName == null || fullName.trim().isEmpty)
          ? null
          : {'full_name': fullName.trim()},
    );

    if (response.session == null) {
      return 'Cuenta creada. Revisa tu correo si la confirmacion esta activa.';
    }

    return 'Cuenta creada y sesion iniciada.';
  }

  Future<void> signOut() => client.auth.signOut();
}
