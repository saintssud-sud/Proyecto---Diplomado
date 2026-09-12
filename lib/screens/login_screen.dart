import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/preferences_controller.dart';
import '../repositories/usuario_repository.dart';
import '../services/auth_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _cargoController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  bool _registerMode = false;
  bool _busy = false;
  bool _showPassword = false;
  String? _message;

  @override
  void dispose() {
    _nameController.dispose();
    _lastNameController.dispose();
    _phoneController.dispose();
    _cargoController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _busy = true;
      _message = null;
    });

    try {
      final service = AuthService();
      final userRepo = UsuarioRepository();

      if (_registerMode) {
        final result = await service.signUp(
          email: _emailController.text,
          password: _passwordController.text,
          fullName: _nombreCompleto,
        );
        // Guarda el perfil (datos personales + rol) en Firestore.
        final uid = AuthService().currentUser?.uid;
        if (uid != null) {
          await userRepo.crearPerfilInicial(
            uid: uid,
            email: _emailController.text,
            nombre: _nombreCompleto,
            telefono: _phoneController.text,
            cargo: _cargoController.text,
          );
        }
        // Guarda el nombre tambien en preferencias locales para que el
        // saludo del Home lo muestre de inmediato.
        final name = _nombreCompleto;
        if (name.isNotEmpty && mounted) {
          await context.read<PreferencesController>().setName(name);
        }
        if (mounted) {
          setState(() => _message = result);
        }
      } else {
        await service.signIn(
          email: _emailController.text,
          password: _passwordController.text,
        );
        // Usuarios que ya existian (creados antes del perfil en Firestore):
        // si no tienen documento de perfil, se crea uno con su email.
        final uid = AuthService().currentUser?.uid;
        if (uid != null) {
          final existe = await userRepo.obtenerPorUid(uid);
          if (existe == null) {
            final nombre = AuthService().currentUser?.displayName ?? '';
            await userRepo.crearPerfilInicial(
              uid: uid,
              email: _emailController.text,
              nombre: nombre,
            );
            if (nombre.isNotEmpty && mounted) {
              await context.read<PreferencesController>().setName(nombre);
            }
          }
        }
      }
    } on FirebaseAuthException catch (error) {
      if (mounted) {
        setState(() => _message = _mensajeError(error.code));
      }
    } catch (error) {
      if (mounted) {
        setState(() => _message = 'Error: $error');
      }
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  /// Nombre completo (nombres + apellidos) en una sola cadena.
  String get _nombreCompleto {
    final n = _nameController.text.trim();
    final a = _lastNameController.text.trim();
    if (n.isEmpty) return a;
    if (a.isEmpty) return n;
    return '$n $a';
  }

  /// Traduce los códigos de error de Firebase Auth a mensajes claros.
  static String _mensajeError(String code) {
    switch (code) {
      case 'invalid-credential':
      case 'wrong-password':
      case 'user-not-found':
      case 'invalid-email':
        return 'Correo o contraseña incorrectos.';
      case 'email-already-in-use':
        return 'Ya existe una cuenta con ese correo.';
      case 'weak-password':
        return 'La contraseña es demasiado débil.';
      case 'user-disabled':
        return 'La cuenta fue deshabilitada.';
      case 'too-many-requests':
        return 'Demasiados intentos. Espera un momento y vuelve a intentar.';
      case 'operation-not-allowed':
        return 'El registro con correo no está habilitado en Firebase.';
      default:
        return 'No se pudo completar la acción. Código: $code';
    }
  }

  static const Color _headerGreen = Color(0xFF39B54A);
  static const Color _actionGreen = Color(0xFF39B54A);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F3F5),
      body: SingleChildScrollView(
        child: Column(
          children: <Widget>[
            // Encabezado verde con logo y etiqueta.
            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(24, 64, 24, 44),
              decoration: const BoxDecoration(
                color: _headerGreen,
                borderRadius: BorderRadius.vertical(
                  bottom: Radius.circular(40),
                ),
              ),
              child: Column(
                children: <Widget>[
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(22),
                    ),
                    child: Image.asset(
                      'assets/images/logo.png',
                      width: 96,
                      height: 96,
                      fit: BoxFit.contain,
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'SI.G.VA.C.H.',
                    style: TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 1,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    _registerMode
                        ? 'Crea tu cuenta para continuar'
                        : 'Inicia sesión para continuar',
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 14, color: Colors.white70),
                  ),
                ],
              ),
            ),
            // Formulario.
            Padding(
              padding: const EdgeInsets.all(24),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 440),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: <Widget>[
                      const SizedBox(height: 8),
                      if (_registerMode) ...<Widget>[
                        TextFormField(
                          controller: _nameController,
                          textCapitalization: TextCapitalization.words,
                          decoration: InputDecoration(
                            labelText: 'Nombres',
                            prefixIcon: const Icon(Icons.badge_outlined),
                            filled: true,
                            fillColor: Colors.white,
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: BorderSide.none,
                            ),
                          ),
                          validator: (value) {
                            if (value == null || value.trim().isEmpty) {
                              return 'Ingresa tus nombres';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _lastNameController,
                          textCapitalization: TextCapitalization.words,
                          decoration: InputDecoration(
                            labelText: 'Apellidos',
                            prefixIcon: const Icon(Icons.badge_outlined),
                            filled: true,
                            fillColor: Colors.white,
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: BorderSide.none,
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _phoneController,
                          keyboardType: TextInputType.phone,
                          decoration: InputDecoration(
                            labelText: 'Teléfono',
                            prefixIcon: const Icon(Icons.phone_outlined),
                            filled: true,
                            fillColor: Colors.white,
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: BorderSide.none,
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _cargoController,
                          textCapitalization: TextCapitalization.words,
                          decoration: InputDecoration(
                            labelText: 'Cargo (opcional)',
                            prefixIcon: const Icon(Icons.work_outline),
                            filled: true,
                            fillColor: Colors.white,
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: BorderSide.none,
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),
                      ],
                      TextFormField(
                        controller: _emailController,
                        decoration: InputDecoration(
                          labelText: 'Usuario',
                          prefixIcon: const Icon(Icons.person_outline),
                          filled: true,
                          fillColor: Colors.white,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide.none,
                          ),
                        ),
                        validator: (value) {
                          if (value == null || !value.contains('@')) {
                            return 'Correo invalido';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _passwordController,
                        obscureText: !_showPassword,
                        decoration: InputDecoration(
                          labelText: 'Contraseña',
                          prefixIcon: const Icon(Icons.lock_outline),
                          suffixIcon: IconButton(
                            icon: Icon(
                              _showPassword
                                  ? Icons.visibility_outlined
                                  : Icons.visibility_off_outlined,
                            ),
                            onPressed: () {
                              setState(() => _showPassword = !_showPassword);
                            },
                          ),
                          filled: true,
                          fillColor: Colors.white,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide.none,
                          ),
                        ),
                        validator: (value) {
                          if (value == null || value.length < 6) {
                            return 'Minimo 6 caracteres';
                          }
                          return null;
                        },
                      ),
                      if (_message != null) ...<Widget>[
                        const SizedBox(height: 12),
                        Text(
                          _message!,
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.error,
                          ),
                        ),
                      ],
                      // Espaciador que conserva la distancia que ocupaba
                      // la fila "Recordarme" (checkbox ~48px).
                      const SizedBox(height: 48),
                      const SizedBox(height: 8),
                      FilledButton.icon(
                        onPressed: _busy ? null : _submit,
                        icon: const Icon(Icons.login),
                        label: Text(
                          _busy
                              ? 'Procesando...'
                              : (_registerMode
                                    ? 'Registrarme'
                                    : 'Iniciar Sesión'),
                        ),
                        style: FilledButton.styleFrom(
                          backgroundColor: _actionGreen,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          textStyle: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                      const SizedBox(height: 4),
                      TextButton(
                        onPressed: _busy
                            ? null
                            : () {
                                setState(() {
                                  _registerMode = !_registerMode;
                                  _message = null;
                                });
                              },
                        child: Text(
                          _registerMode
                              ? 'Ya tengo cuenta'
                              : 'Crear una cuenta',
                          style: const TextStyle(color: _actionGreen),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
