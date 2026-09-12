/// Perfil de usuario del sistema SIGVACH.
///
/// Se guarda en Firestore, colección `usuarios`, con el documento cuyo id
/// es el `uid` de Firebase Authentication. Además de las credenciales de
/// acceso (que viven en Firebase Auth), aquí se almacenan los datos
/// personales y el rol (admin / usuario).
class UsuarioPerfil {
  const UsuarioPerfil({
    this.uid,
    this.email = '',
    this.nombre = '',
    this.telefono = '',
    this.cargo = '',
    this.rol = 'usuario',
    this.activo = true,
    this.creadoEn,
  });

  final String? uid;
  final String email;
  final String nombre;
  final String telefono;
  final String cargo;
  final String rol; // 'admin' | 'usuario'
  final bool activo;
  final DateTime? creadoEn;

  bool get esAdmin => rol == 'admin';

  Map<String, dynamic> toMap() {
    return <String, dynamic>{
      'email': email.trim(),
      'nombre': nombre.trim(),
      'telefono': telefono.trim(),
      'cargo': cargo.trim(),
      'rol': rol,
      'activo': activo,
      'creado_en': creadoEn?.toIso8601String() ?? '',
    };
  }

  factory UsuarioPerfil.fromMap(Map<String, dynamic> map, {String? uid}) {
    return UsuarioPerfil(
      uid: uid ?? map['uid']?.toString(),
      email: map['email']?.toString() ?? '',
      nombre: map['nombre']?.toString() ?? '',
      telefono: map['telefono']?.toString() ?? '',
      cargo: map['cargo']?.toString() ?? '',
      rol: map['rol']?.toString() == 'admin' ? 'admin' : 'usuario',
      activo: map['activo'] as bool? ?? true,
      creadoEn: DateTime.tryParse(map['creado_en']?.toString() ?? ''),
    );
  }

  UsuarioPerfil copyWith({
    String? uid,
    String? email,
    String? nombre,
    String? telefono,
    String? cargo,
    String? rol,
    bool? activo,
    DateTime? creadoEn,
  }) {
    return UsuarioPerfil(
      uid: uid ?? this.uid,
      email: email ?? this.email,
      nombre: nombre ?? this.nombre,
      telefono: telefono ?? this.telefono,
      cargo: cargo ?? this.cargo,
      rol: rol ?? this.rol,
      activo: activo ?? this.activo,
      creadoEn: creadoEn ?? this.creadoEn,
    );
  }
}
