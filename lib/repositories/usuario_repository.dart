import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';

import '../models/roles.dart';
import '../models/usuario_perfil.dart';

/// Repositorio de usuarios sobre Cloud Firestore.
///
/// Colección: `usuarios` con documentos cuyo id es el `uid` de Firebase
/// Authentication. Cada documento guarda los datos personales y el rol.
class UsuarioRepository {
  UsuarioRepository({FirebaseFirestore? db, FirebaseAuth? auth})
    : _db = db ?? FirebaseFirestore.instance,
      _auth = auth ?? FirebaseAuth.instance;

  final FirebaseFirestore _db;
  final FirebaseAuth _auth;

  /// FirebaseAuth subyacente (para escuchar cambios de sesión).
  FirebaseAuth get auth => _auth;

  /// Colección `usuarios`.
  CollectionReference<Map<String, dynamic>> get _usuarios =>
      _db.collection('usuarios');

  DocumentReference<Map<String, dynamic>> _doc(String uid) =>
      _usuarios.doc(uid);

  /// Crea (o sobrescribe) el perfil del usuario al registrarse.
  ///
  /// **El rol que se asigna es siempre el de operación.** Antes existía una
  /// excepción: si el correo era `admin@sigvach.com`, el perfil nacía como
  /// administrador. Se retiró porque cualquiera que consiguiera registrarse con
  /// ese correo obtenía las atribuciones de administración sin que nadie se las
  /// concediera, lo que contradice el principio de menor privilegio. El rol de
  /// administrador se concede **después**, desde el panel o desde el servicio,
  /// y queda registrado quién lo hizo.
  Future<void> crearPerfilInicial({
    required String uid,
    required String email,
    required String nombre,
    String telefono = '',
    String cargo = '',
  }) async {
    final perfil = UsuarioPerfil(
      uid: uid,
      email: email,
      nombre: nombre,
      telefono: telefono,
      cargo: cargo,
      rol: Roles.porDefecto,
      activo: true,
      creadoEn: DateTime.now(),
    );
    await _doc(uid).set(perfil.toMap());
  }

  /// Lee el perfil de un usuario por su uid. Devuelve null si no existe.
  Future<UsuarioPerfil?> obtenerPorUid(String uid) async {
    final snap = await _doc(uid).get();
    if (!snap.exists) return null;
    return UsuarioPerfil.fromMap(snap.data()!, uid: snap.id);
  }

  /// Perfil del usuario actualmente autenticado (null si no hay sesión).
  Future<UsuarioPerfil?> obtenerUsuarioActual() async {
    final user = _auth.currentUser;
    if (user == null) return null;
    return obtenerPorUid(user.uid);
  }

  /// Actualiza datos personales de un usuario.
  Future<void> actualizarDatos({
    required String uid,
    String? nombre,
    String? telefono,
    String? cargo,
  }) async {
    final data = <String, dynamic>{};
    if (nombre != null) data['nombre'] = nombre.trim();
    if (telefono != null) data['telefono'] = telefono.trim();
    if (cargo != null) data['cargo'] = cargo.trim();
    if (data.isNotEmpty) {
      await _doc(uid).update(data);
    }
  }
}
