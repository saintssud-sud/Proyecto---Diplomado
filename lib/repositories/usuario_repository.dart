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

  /// Correo que, al registrarse, recibe el rol `admin` automáticamente.
  static const String correoAdmin = 'admin@sigvach.com';

  /// Correo del usuario autenticado (público y de solo lectura).
  String? get currentEmail => _auth.currentUser?.email;

  /// Colección `usuarios`.
  CollectionReference<Map<String, dynamic>> get _usuarios =>
      _db.collection('usuarios');

  DocumentReference<Map<String, dynamic>> _doc(String uid) =>
      _usuarios.doc(uid);

  /// Crea (o sobrescribe) el perfil del usuario al registrarse.
  ///
  /// El rol se asigna automáticamente: `admin` si el correo es
  /// [correoAdmin], en cualquier otro caso `usuario`.
  Future<void> crearPerfilInicial({
    required String uid,
    required String email,
    required String nombre,
    String telefono = '',
    String cargo = '',
  }) async {
    final rol = _rolPara(email);
    final perfil = UsuarioPerfil(
      uid: uid,
      email: email,
      nombre: nombre,
      telefono: telefono,
      cargo: cargo,
      rol: rol,
      activo: true,
      creadoEn: DateTime.now(),
    );
    await _doc(uid).set(perfil.toMap());
  }

  /// Determina el rol según el correo (opción 2 de diseño).
  ///
  /// El rol de administración se asigna por correo; cualquier otra cuenta nace
  /// con el rol de menor privilegio, conforme al principio de menor privilegio.
  String _rolPara(String email) =>
      email.trim().toLowerCase() == correoAdmin.toLowerCase()
      ? Roles.administrador
      : Roles.porDefecto;

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

  /// Lista todos los usuarios registrados (para el panel del admin).
  Future<List<UsuarioPerfil>> listarTodos() async {
    final snap = await _usuarios.orderBy('creado_en', descending: true).get();
    return snap.docs
        .map((doc) => UsuarioPerfil.fromMap(doc.data(), uid: doc.id))
        .toList();
  }

  /// Escucha en tiempo real todos los usuarios (para el panel del admin).
  Stream<List<UsuarioPerfil>> verTodos() {
    return _usuarios
        .orderBy('creado_en', descending: true)
        .snapshots()
        .map(
          (snap) => snap.docs
              .map((doc) => UsuarioPerfil.fromMap(doc.data(), uid: doc.id))
              .toList(),
        );
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

  /// Cambia el rol de un usuario.
  Future<void> cambiarRol({required String uid, required String rol}) async {
    await _doc(uid).update(<String, dynamic>{'rol': Roles.normalizar(rol)});
  }

  /// Activa o desactiva un usuario.
  Future<void> cambiarActivo({
    required String uid,
    required bool activo,
  }) async {
    await _doc(uid).update(<String, dynamic>{'activo': activo});
  }

  /// Elimina el perfil de un usuario de Firestore.
  ///
  /// Nota: no elimina la cuenta de Firebase Auth (eso requiere Cloud
  /// Functions). Con esto el usuario deja de aparecer en el sistema.
  Future<void> eliminar(String uid) async {
    await _doc(uid).delete();
  }
}
