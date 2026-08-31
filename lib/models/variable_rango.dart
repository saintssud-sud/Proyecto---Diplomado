/// Rango óptimo de una variable (mínimo, máximo y unidad).
///
/// Se usa en la pantalla 2.2 (Rangos óptimos) y para decidir el estado de una
/// variable (Normal / Fuera de rango). Se persiste en SharedPreferences.
class VariableRango {
  const VariableRango({
    required this.variable,
    required this.minimo,
    required this.maximo,
    required this.unidad,
  });

  final String variable;
  final double minimo;
  final double maximo;
  final String unidad;

  /// Rangos por defecto (semilla) según el diagrama de pantallas.
  static List<VariableRango> seed() {
    return const <VariableRango>[
      VariableRango(
        variable: 'Temperatura',
        minimo: 18.0,
        maximo: 26.0,
        unidad: '°C',
      ),
      VariableRango(
        variable: 'Humedad',
        minimo: 40.0,
        maximo: 80.0,
        unidad: '%',
      ),
      VariableRango(variable: 'pH', minimo: 5.5, maximo: 6.5, unidad: ''),
      VariableRango(
        variable: 'TDS',
        minimo: 800.0,
        maximo: 1100.0,
        unidad: 'ppm',
      ),
      VariableRango(
        variable: 'Nivel de agua',
        minimo: 50.0,
        maximo: 100.0,
        unidad: '%',
      ),
    ];
  }

  Map<String, dynamic> toJson() {
    return <String, dynamic>{
      'variable': variable,
      'minimo': minimo,
      'maximo': maximo,
      'unidad': unidad,
    };
  }

  factory VariableRango.fromJson(Map<String, dynamic> json) {
    return VariableRango(
      variable: json['variable'] as String,
      minimo: (json['minimo'] as num).toDouble(),
      maximo: (json['maximo'] as num).toDouble(),
      unidad: json['unidad'] as String? ?? '',
    );
  }
}
