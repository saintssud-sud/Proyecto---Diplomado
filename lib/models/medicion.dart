/// Una medición histórica del laboratorio.
///
/// Se usa en la pantalla 5 (Historial): consulta por rango de fechas, gráfica
/// histórica (5.1) y lista de mediciones (5.2).
class Medicion {
  const Medicion({
    required this.fechaHora,
    required this.temperatura,
    required this.humedad,
    required this.ph,
    required this.tds,
  });

  final String fechaHora;
  final double temperatura;
  final double humedad;
  final double ph;
  final double tds;

  /// Mediciones de ejemplo (semilla) en orden cronológico.
  static List<Medicion> seed() {
    return const <Medicion>[
      Medicion(
        fechaHora: '21/03/2026 11:59 a. m.',
        temperatura: 24.5,
        humedad: 65,
        ph: 6.2,
        tds: 850,
      ),
      Medicion(
        fechaHora: '21/03/2026 11:38 a. m.',
        temperatura: 24.1,
        humedad: 64,
        ph: 6.1,
        tds: 840,
      ),
      Medicion(
        fechaHora: '21/03/2026 11:28 a. m.',
        temperatura: 23.9,
        humedad: 63,
        ph: 6.0,
        tds: 830,
      ),
      Medicion(
        fechaHora: '20/03/2026 11:59 a. m.',
        temperatura: 24.2,
        humedad: 66,
        ph: 6.2,
        tds: 845,
      ),
      Medicion(
        fechaHora: '19/03/2026 11:59 a. m.',
        temperatura: 24.8,
        humedad: 67,
        ph: 6.3,
        tds: 860,
      ),
      Medicion(
        fechaHora: '18/03/2026 11:59 a. m.',
        temperatura: 25.1,
        humedad: 68,
        ph: 6.4,
        tds: 870,
      ),
    ];
  }

  Map<String, dynamic> toJson() {
    return <String, dynamic>{
      'fechaHora': fechaHora,
      'temperatura': temperatura,
      'humedad': humedad,
      'ph': ph,
      'tds': tds,
    };
  }

  factory Medicion.fromJson(Map<String, dynamic> json) {
    return Medicion(
      fechaHora: json['fechaHora'] as String,
      temperatura: (json['temperatura'] as num).toDouble(),
      humedad: (json['humedad'] as num).toDouble(),
      ph: (json['ph'] as num).toDouble(),
      tds: (json['tds'] as num).toDouble(),
    );
  }
}
