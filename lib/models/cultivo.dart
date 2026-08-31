/// Representa un cultivo del sistema SIGVACH.
///
/// Cada cultivo vive en un área (ej. "Invernadero Norte"), tiene un estado
/// ("Activo"), una cantidad de plantas, un número de módulo y su fecha de
/// inicio. Se guarda de forma persistente en SharedPreferences (JSON).
class Cultivo {
  const Cultivo({
    required this.id,
    required this.nombre,
    required this.area,
    required this.estado,
    required this.cantidad,
    required this.modulo,
    required this.fechaInicio,
    required this.progreso,
  });

  final String id;
  final String nombre;
  final String area;
  final String estado;
  final int cantidad;
  final int modulo;
  final String fechaInicio;
  final int progreso;

  /// Cultivos de ejemplo que se usan la primera vez (semilla).
  static List<Cultivo> seed() {
    return const <Cultivo>[
      Cultivo(
        id: 'c1',
        nombre: 'Lechuga',
        area: 'Invernadero Norte',
        estado: 'Activo',
        cantidad: 48,
        modulo: 4,
        fechaInicio: '10/03/2026',
        progreso: 70,
      ),
      Cultivo(
        id: 'c2',
        nombre: 'Acelga',
        area: 'Invernadero Sur',
        estado: 'Activo',
        cantidad: 35,
        modulo: 3,
        fechaInicio: '05/03/2026',
        progreso: 55,
      ),
      Cultivo(
        id: 'c3',
        nombre: 'Espinaca',
        area: 'Invernadero Este',
        estado: 'Activo',
        cantidad: 12,
        modulo: 2,
        fechaInicio: '01/03/2026',
        progreso: 35,
      ),
    ];
  }

  Map<String, dynamic> toJson() {
    return <String, dynamic>{
      'id': id,
      'nombre': nombre,
      'area': area,
      'estado': estado,
      'cantidad': cantidad,
      'modulo': modulo,
      'fechaInicio': fechaInicio,
      'progreso': progreso,
    };
  }

  factory Cultivo.fromJson(Map<String, dynamic> json) {
    return Cultivo(
      id: json['id'] as String,
      nombre: json['nombre'] as String,
      area: json['area'] as String,
      estado: json['estado'] as String,
      cantidad: json['cantidad'] as int,
      modulo: json['modulo'] as int,
      fechaInicio: json['fechaInicio'] as String,
      progreso: json['progreso'] as int? ?? 0,
    );
  }
}
