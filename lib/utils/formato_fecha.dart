/// Formato de fechas y horas de la interfaz.
///
/// Se centraliza aquí porque las pantallas mostraban el formato escrito a mano
/// en cada lugar, lo que producía etiquetas distintas para la misma fecha.
library;

/// Formatea una fecha como `dd/mm/aaaa hh:mm a. m.`, en hora local.
String formatearFechaHora(DateTime fecha) {
  final DateTime local = fecha.toLocal();
  final int hora = local.hour;
  final String periodo = hora >= 12 ? 'p. m.' : 'a. m.';
  final int hora12 = hora % 12 == 0 ? 12 : hora % 12;
  return '${_dos(local.day)}/${_dos(local.month)}/${local.year} '
      '${_dos(hora12)}:${_dos(local.minute)} $periodo';
}

/// Formatea una fecha como `dd/mm/aaaa`.
String formatearFecha(DateTime fecha) {
  final DateTime local = fecha.toLocal();
  return '${_dos(local.day)}/${_dos(local.month)}/${local.year}';
}

/// Formatea una hora como `hh:mm a. m.`.
String formatearHora(DateTime fecha) {
  final DateTime local = fecha.toLocal();
  final int hora = local.hour;
  final String periodo = hora >= 12 ? 'p. m.' : 'a. m.';
  final int hora12 = hora % 12 == 0 ? 12 : hora % 12;
  return '${_dos(hora12)}:${_dos(local.minute)} $periodo';
}

/// Formatea un valor numérico sin decimales innecesarios.
String formatearValor(double valor) {
  return valor == valor.roundToDouble()
      ? valor.toStringAsFixed(0)
      : valor.toStringAsFixed(1);
}

/// Etiqueta de fecha y hora del momento actual.
String ahoraLegible() => formatearFechaHora(DateTime.now());

String _dos(int valor) => valor.toString().padLeft(2, '0');
