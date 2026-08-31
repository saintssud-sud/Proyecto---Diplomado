import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../services/auth_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  bool _registerMode = false;
  bool _busy = false;
  bool _showPassword = false;
  bool _rememberMe = false;
  String? _message;

  @override
  void dispose() {
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
      final service = AuthService(Supabase.instance.client);

      if (_registerMode) {
        final result = await service.signUp(
          email: _emailController.text,
          password: _passwordController.text,
        );
        if (mounted) {
          setState(() => _message = result);
        }
      } else {
        await service.signIn(
          email: _emailController.text,
          password: _passwordController.text,
        );
      }
    } on AuthException catch (error) {
      if (mounted) {
        setState(() => _message = error.message);
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
                    'S.I.G.V.A.C.H.',
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
                      Row(
                        children: <Widget>[
                          Checkbox(
                            value: _rememberMe,
                            activeColor: _actionGreen,
                            onChanged: (value) {
                              setState(() => _rememberMe = value ?? false);
                            },
                          ),
                          const Text('Recordarme'),
                        ],
                      ),
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
