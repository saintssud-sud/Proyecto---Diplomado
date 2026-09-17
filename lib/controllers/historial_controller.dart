import 'package:flutter/foundation.dart';

import '../models/api/modelos_api.dart';
import '../repositories/api/lecturas_api_repository.dart';
import '../widgets/vista_con_estados.dart';
import 'estado_de_vista.dart';

/// Filtros de una consulta del historial.
///
/// La variable se identifica con su **código** del catálogo (`ph`, `tds`, …),
/// que es el mismo que entiende el servicio; el nombre presentable se resuelve
/// con `nombreDeVariable` en el momento de mostrarlo.
class FiltroHistorial {
  const FiltroHistorial({
    required this.variable,
    this.moduloId,
    this.desde,
    this.hasta,
  });

  final String variable;

  /// Módulo del que se consulta el historial.
  ///
  /// La aplicación trabaja sobre el **módulo vigente**: sin este filtro, el
  /// historial mezclaba las lecturas de módulos con cultivos y rangos distintos,
  /// y el resumen del periodo no correspondía a ningún módulo en particular.
  final String? moduloId;
  final DateTime? desde;
  final DateTime? hasta;
}

/// Controlador de la consulta del historial.
///
/// El historial no se arma con los datos que la aplicación tenga en memoria: se
/// consulta al servicio con la variable y el periodo elegidos, y el resumen
/// —promedio, máximo y mínimo— lo calcula el propio servicio, de modo que el
/// mismo dato no se interprete de forma distinta según dónde se mire.
class HistorialController extends ChangeNotifier {
  HistorialController({required LecturasApiRepository lecturas})
      : _lecturas = lecturas;

  final LecturasApiRepository _lecturas;

  /// Número máximo de lecturas que se traen para la serie de la gráfica.
  static const int _limiteSerie = 500;

  EstadoVista _estado = EstadoVista.cargando;
  String? _mensajeError;
  bool _errorDeConexion = false;
  bool _seConsulto = false;
  FiltroHistorial _filtro = const FiltroHistorial(variable: 'ph');
  List<Lectura> _consultadas = const <Lectura>[];
  ResumenVariable? _resumen;

  EstadoVista get estado => _estado;
  String? get mensajeError => _mensajeError;
  bool get errorDeConexion => _errorDeConexion;
  FiltroHistorial get filtro => _filtro;

  /// Indica si el historial ya se consultó al menos una vez.
  ///
  /// La pantalla lo usa para no presentar el estado vacío antes de que el
  /// usuario haya pedido una consulta: «todavía no hay resultados» y «todavía no
  /// se ha consultado» son dos situaciones distintas y llevan a acciones
  /// distintas.
  bool get seConsulto => _seConsulto;

  /// Lecturas devueltas por el servicio para el filtro vigente.
  List<Lectura> get lecturas => _consultadas;

  /// Resumen del periodo calculado por el servicio; nulo si no hay lecturas.
  ResumenVariable? get resumen => _resumen;

  /// Serie ordenada de la más antigua a la más reciente, como la espera la
  /// gráfica.
  ///
  /// Se ordena aquí en vez de confiar en el orden recibido: la serie de una
  /// gráfica no debe depender de cómo el servicio decida ordenar la lista.
  List<Lectura> get serieCronologica {
    final List<Lectura> copia = List<Lectura>.of(_consultadas);
    copia.sort((Lectura a, Lectura b) => a.timestamp.compareTo(b.timestamp));
    return List<Lectura>.unmodifiable(copia);
  }

  /// Consulta el historial con el filtro indicado.
  ///
  /// El resumen y las lecturas se piden en la misma operación lógica: si el
  /// servicio no responde, la vista lo informa como un fallo en lugar de
  /// presentar una serie sin su resumen, que se leería como si el periodo no
  /// tuviera datos.
  Future<void> cargar({FiltroHistorial? filtro}) async {
    if (filtro != null) {
      _filtro = filtro;
    }
    _estado = EstadoVista.cargando;
    _mensajeError = null;
    _errorDeConexion = false;
    _seConsulto = true;
    notifyListeners();

    try {
      final List<ResumenVariable> resumenes = await _lecturas.resumen(
        variable: _filtro.variable,
        moduloId: _filtro.moduloId,
        desde: _filtro.desde,
        hasta: _filtro.hasta,
      );
      final List<Lectura> lecturas = await _lecturas.listar(
        variable: _filtro.variable,
        moduloId: _filtro.moduloId,
        desde: _filtro.desde,
        hasta: _filtro.hasta,
        limite: _limiteSerie,
      );

      _consultadas = lecturas;
      _resumen = _resumenDe(resumenes);
      _estado = lecturas.isEmpty ? EstadoVista.vacio : EstadoVista.conDatos;
    } catch (error) {
      final FalloDeVista fallo = FalloDeVista.desde(error);
      _consultadas = const <Lectura>[];
      _resumen = null;
      _mensajeError = fallo.mensaje;
      _errorDeConexion = fallo.deConexion;
      _estado = EstadoVista.error;
    } finally {
      notifyListeners();
    }
  }

  /// Vuelve a consultar con el filtro vigente.
  Future<void> reintentar() => cargar();

  /// Cambia el periodo consultado conservando la variable.
  ///
  /// Lo usan los períodos rápidos de la gráfica: son un atajo del mismo filtro,
  /// no un filtro propio de esa pantalla.
  Future<void> seleccionarPeriodo({DateTime? desde, DateTime? hasta}) => cargar(
        filtro: FiltroHistorial(
          variable: _filtro.variable,
          moduloId: _filtro.moduloId,
          desde: desde,
          hasta: hasta,
        ),
      );

  /// Selecciona el resumen de la variable consultada.
  ResumenVariable? _resumenDe(List<ResumenVariable> resumenes) {
    for (final ResumenVariable resumen in resumenes) {
      if (resumen.variable == _filtro.variable) {
        return resumen;
      }
    }
    return resumenes.isEmpty ? null : resumenes.first;
  }
}
