/// Alerta del sistema (variable fuera de rango o evento).
///
/// Se muestra en la pantalla 4 (Alertas) con pestañas Activas / Historial.
class Alerta {
  const Alerta({
    required this.id,
    required this.titulo,
    required this.nivelActual,
    required this.rangoPermitido,
    required this.fecha,
    required this.estado,
    this.critica = false,
  });

  final String id;
  final String titulo;
  final String nivelActual;
  final String rangoPermitido;
  final String fecha;
  final String estado; // 'Activa' o 'Resuelta'
  final bool critica;

  /// Alertas de ejemplo (semilla) según el diagrama.
  static List<Alerta> seed() {
    return const <Alerta>[
      Alerta(
        id: 'a1',
        titulo: 'pH fuera de rango',
        nivelActual: 'Nivel actual: 7.2',
        rangoPermitido: 'Rango permitido: 5.5 - 6.5',
        fecha: '21/03/2026 11:59 a. m.',
        estado: 'Activa',
        critica: true,
      ),
      Alerta(
        id: 'a2',
        titulo: 'TDS alto',
        nivelActual: 'Nivel actual: 1200 ppm',
        rangoPermitido: 'Rango permitido: 800 - 1100',
        fecha: '21/03/2026 11:45 a. m.',
        estado: 'Activa',
        critica: true,
      ),
      Alerta(
        id: 'a3',
        titulo: 'Nivel de agua bajo',
        nivelActual: 'Nivel actual: 25 %',
        rangoPermitido: 'Rango permitido: 50 - 100',
        fecha: '21/03/2026 11:30 a. m.',
        estado: 'Activa',
        critica: true,
      ),
      Alerta(
        id: 'a4',
        titulo: 'Temperatura normal',
        nivelActual: 'Nivel actual: 24.5 °C',
        rangoPermitido: 'Rango permitido: 18 - 26 °C',
        fecha: '20/03/2026 08:00 a. m.',
        estado: 'Resuelta',
        critica: false,
      ),
    ];
  }

  Map<String, dynamic> toJson() {
    return <String, dynamic>{
      'id': id,
      'titulo': titulo,
      'nivelActual': nivelActual,
      'rangoPermitido': rangoPermitido,
      'fecha': fecha,
      'estado': estado,
      'critica': critica,
    };
  }

  factory Alerta.fromJson(Map<String, dynamic> json) {
    return Alerta(
      id: json['id'] as String,
      titulo: json['titulo'] as String,
      nivelActual: json['nivelActual'] as String,
      rangoPermitido: json['rangoPermitido'] as String,
      fecha: json['fecha'] as String,
      estado: json['estado'] as String,
      critica: json['critica'] as bool? ?? false,
    );
  }
}
