import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';

import '../models/registro.dart';
import 'registro_repository.dart';

/// Repositorio de registros basado en Cloud Firestore.
///
/// Reemplaza al antiguo [SupabaseRegistroRepository]. Cada registro se
/// guarda como un documento de la colección `registros`, con el `uid` del
/// usuario autenticado en Firebase para separar la información por usuario.
class FirestoreRegistroRepository implements RegistroRepository {
  FirestoreRegistroRepository({FirebaseFirestore? db, FirebaseAuth? auth})
    : _db = db ?? FirebaseFirestore.instance,
      _auth = auth ?? FirebaseAuth.instance;

  final FirebaseFirestore _db;
  final FirebaseAuth _auth;

  String get _userId {
    final user = _auth.currentUser;
    if (user == null) {
      throw StateError('No existe una sesion autenticada.');
    }
    return user.uid;
  }

  CollectionReference<Map<String, dynamic>> get _registros =>
      _db.collection('registros');

  @override
  Future<List<Registro>> fetchAll() async {
    final snapshot = await _registros
        .where('user_id', isEqualTo: _userId)
        .orderBy('created_at', descending: true)
        .get();

    return snapshot.docs.map((doc) {
      final data = doc.data();
      data['id'] = doc.id;
      return Registro.fromMap(data);
    }).toList();
  }

  @override
  Future<void> create(Registro registro) async {
    final data = registro.toInsertMap(_userId);
    data['created_at'] = DateTime.now().toUtc().toIso8601String();
    await _registros.add(data);
  }

  @override
  Future<void> update(Registro registro) async {
    final id = registro.id;
    if (id == null) {
      throw ArgumentError('El registro no tiene id.');
    }

    final data = registro.toUpdateMap();
    data['user_id'] = _userId;
    await _registros.doc(id).update(data);
  }

  @override
  Future<void> delete(String id) async {
    await _registros.doc(id).delete();
  }
}
