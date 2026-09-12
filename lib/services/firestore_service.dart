import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_core/firebase_core.dart';

import '../firebase_options.dart';

/// Servicio de conexión con Cloud Firestore.
///
/// Este proyecto usa Firebase (Authentication + Firestore) como backend.
/// El servicio expone la inicialización de Firebase y algunos ejemplos de
/// CRUD listos para usar.
///
/// Para usarlo dentro de la app:
/// ```dart
/// final firestore = context.read<FirestoreService>();
/// await firestore.demo.addDemo();
/// ```
class FirestoreService {
  FirestoreService();

  /// Inicializa Firebase con la configuración de [DefaultFirebaseOptions].
  /// Se llama una sola vez al arrancar la app (en main.dart).
  Future<void> initialize() async {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
  }

  /// Instancia de Firestore ya inicializada.
  FirebaseFirestore get db => FirebaseFirestore.instance;

  /// Acceso a una colección de prueba/ejemplo.
  CollectionReference<Map<String, dynamic>> get demos =>
      db.collection('firestore_demo');

  // ---------------------------------------------------------------------
  // Ejemplos básicos de CRUD sobre la colección `firestore_demo`.
  // Sirven para verificar que la conexión funciona. Puedes copiar este
  // patrón para tus propias colecciones (cultivos, mediciones, etc.).
  // ---------------------------------------------------------------------

  /// Crea un documento nuevo en `firestore_demo`.
  /// [data] puede contener cualquier par clave/valor.
  Future<DocumentReference<Map<String, dynamic>>> addDemo(
    Map<String, dynamic> data,
  ) {
    return demos.add({...data, 'created_at': FieldValue.serverTimestamp()});
  }

  /// Escucha en tiempo real los documentos de `firestore_demo`
  /// ordenados por fecha de creación (del más nuevo al más antiguo).
  Stream<List<Map<String, dynamic>>> watchDemos() {
    return demos
        .orderBy('created_at', descending: true)
        .snapshots()
        .map(
          (snapshot) => snapshot.docs.map((doc) {
            final data = doc.data();
            data['id'] = doc.id;
            return data;
          }).toList(),
        );
  }

  /// Lee una sola vez todos los documentos de `firestore_demo`.
  Future<List<Map<String, dynamic>>> fetchDemos() async {
    final snapshot = await demos.orderBy('created_at', descending: true).get();
    return snapshot.docs.map((doc) {
      final data = doc.data();
      data['id'] = doc.id;
      return data;
    }).toList();
  }

  /// Actualiza campos de un documento existente.
  Future<void> updateDemo(String id, Map<String, dynamic> data) async {
    await demos.doc(id).update(data);
  }

  /// Elimina un documento por su id.
  Future<void> deleteDemo(String id) async {
    await demos.doc(id).delete();
  }
}
