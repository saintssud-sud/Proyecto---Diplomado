import 'package:flutter/foundation.dart';

import '../models/api/modelos_api.dart';
import '../repositories/api/alertas_api_repository.dart';
import '../repositories/api/lecturas_api_repository.dart';
import '../repositories/api/modulos_api_repository.dart';
import '../repositories/api/rangos_api_repository.dart';
import '../widgets/vista_con_estados.dart';
import 'estado_de_vista.dart';

/// Situación de una variable en el panel: último valor, rango y estado.
class EstadoDeVariable {
  const EstadoDeVariable({
    required this.codigo,
    required this.nombre,
    required this.unidad,
    this.valor,
    this.fecha,
    this.minimo,
    this.maximo,
    this.estado,
  });

  final String codigo;
  final String nombre;
  final String unidad;

  /// Último valor registrado; nulo si la variable aún no tiene lecturas.
  final double? valor;
  final DateTime? fecha;

  /// Límites del rango de referencia; nulos si el perfil no lo define.
  final double? minimo;
  final double? maximo;

  /// Estado asignado por el servidor: `dentro`, `bajo`, `alto` o `sin_rango`.
  final String? estado;

  bool get tieneValor => valor != null;

  bool get tieneRango => minimo != null && maximo != null;

  /// Indica si el valor salió del rango de referencia.
  bool get fueraDeRango => estado != null && EstadoRango.esFueraDeRango(estado!);

  /// Texto presentable del estado.
  String get etiquetaEstado =>
      estado == null ? 'Sin lecturas' : EstadoRango.etiqueta(estado!);
}

/// Controlador del panel principal.
///
/// Reúne la información que el panel presenta —el módulo, el estado de cada
/// variable, las alertas activas y la fecha de la última lectura— a partir de
/// los repositorios del servicio, y publica el estado de la vista para que la
/// pantalla no tenga que decidir qué mostrar mientras carga o cuando falla.
class PanelController extends ChangeNotifier {
  PanelController({
    required ModulosApiRepository modulos,
    required LecturasApiRepository lecturas,
    required RangosApiRepository rangos,
    required AlertasApiRepository alertas,
  })  : _modulos = modulos,
        _lecturas = lecturas,
        _rangos = rangos,
        _alertas = alertas;

  final ModulosApiRepository _modulos;
  final LecturasApiRepository _lecturas;
  final RangosApiRepository _rangos;
  final AlertasApiRepository _alertas;

  EstadoVista _estado = EstadoVista.cargando;
  String? _mensajeError;
  bool _errorDeConexion = false;
  bool _cargando = false;
  List<ModuloCultivo> _modulosDisponibles = const <ModuloCultivo>[];
  ModuloCultivo? _modulo;
  List<EstadoDeVariable> _variables = const <EstadoDeVariable>[];
  int _alertasActivas = 0;
  DateTime? _ultimaLectura;

  EstadoVista get estado => _estado;
  String? get mensajeError => _mensajeError;
  bool get errorDeConexion => _errorDeConexion;
  bool get cargando => _cargando;
  ModuloCultivo? get modulo => _modulo;
  List<ModuloCultivo> get modulosDisponibles => _modulosDisponibles;
  List<EstadoDeVariable> get variables => _variables;
  int get alertasActivas => _alertasActivas;
  DateTime? get ultimaLectura => _ultimaLectura;

  /// Indica si hay alguna variable fuera de su rango de referencia.
  bool get hayVariablesFueraDeRango =>
      _variables.any((EstadoDeVariable variable) => variable.fueraDeRango);

  /// Consulta el panel completo.
  ///
  /// El orden de las consultas es deliberado: primero los módulos, porque sin
  /// módulo no hay nada que consultar; luego las lecturas y los rangos del
  /// módulo seleccionado; y en paralelo, las alertas activas del sistema.
  Future<void> cargar({String? moduloId, bool limpiarModulo = false}) async {
    _cargando = true;
    _estado = EstadoVista.cargando;
    _mensajeError = null;
    _errorDeConexion = false;
    notifyListeners();

    try {
      _modulosDisponibles = await _modulos.listar(activo: true);

      if (_modulosDisponibles.isEmpty) {
        // Sin módulos no hay variables que presentar: es un estado vacío con
        // una instrucción concreta, no un error.
        _modulo = null;
        _variables = const <EstadoDeVariable>[];
        _alertasActivas = (await _alertas.listar(estado: 'activa')).length;
        _ultimaLectura = null;
        _estado = EstadoVista.vacio;
        return;
      }

      _modulo = _seleccionarModulo(moduloId, limpiarModulo: limpiarModulo);
      final ModuloCultivo modulo = _modulo!;

      final List<Lectura> lecturas =
          await _lecturas.listar(moduloId: modulo.id, limite: 200);
      final List<RangoReferencia> rangos =
          await _rangos.listar(perfilId: modulo.perfilId);
      final List<AlertaServidor> alertas =
          await _alertas.listar(estado: 'activa', moduloId: modulo.id);

      _variables = _componerVariables(lecturas, rangos);
      _alertasActivas = alertas.length;
      _ultimaLectura = lecturas.isEmpty ? null : lecturas.first.timestamp;
      _estado = lecturas.isEmpty ? EstadoVista.vacio : EstadoVista.conDatos;
    } catch (error) {
      final FalloDeVista fallo = FalloDeVista.desde(error);
      _variables = const <EstadoDeVariable>[];
      _mensajeError = fallo.mensaje;
      _errorDeConexion = fallo.deConexion;
      _estado = EstadoVista.error;
    } finally {
      _cargando = false;
      notifyListeners();
    }
  }

  /// Vuelve a consultar el panel con el módulo vigente.
  Future<void> reintentar() => cargar();

  /// Cambia el módulo cuyas variables se presentan.
  Future<void> seleccionarModulo(String moduloId) => cargar(moduloId: moduloId);

  /// Registra una medición tomada con instrumentos portátiles.
  ///
  /// Solo se envían las variables que el usuario completó. El servidor fija el
  /// origen de estas lecturas como manual, evalúa cada valor contra su rango y
  /// genera las alertas que correspondan; por eso, al terminar, el panel se
  /// vuelve a consultar en lugar de suponer el resultado.
  Future<int> registrarMedicion(
    Map<String, double> valores, {
    String? observacion,
  }) async {
    final ModuloCultivo? modulo = _modulo;
    if (modulo == null) {
      throw StateError('No hay un módulo de cultivo seleccionado.');
    }
    if (valores.isEmpty) {
      throw ArgumentError('No se indicó ningún valor para registrar.');
    }

    int registradas = 0;
    Object? fallo;
    for (final MapEntry<String, double> entrada in valores.entries) {
      try {
        await _lecturas.registrarManual(
          moduloId: modulo.id,
          variable: entrada.key,
          valor: entrada.value,
          observacion: observacion,
        );
        registradas++;
      } catch (error) {
        // Se conserva el primer fallo —con el detalle del campo rechazado— y se
        // continúa, para no perder las variables que sí eran válidas.
        fallo ??= error;
      }
    }

    await cargar(moduloId: modulo.id);

    if (fallo != null) {
      throw fallo;
    }
    return registradas;
  }

  ModuloCultivo _seleccionarModulo(String? moduloId, {required bool limpiarModulo}) {
    if (moduloId != null) {
      for (final ModuloCultivo modulo in _modulosDisponibles) {
        if (modulo.id == moduloId) {
          return modulo;
        }
      }
    }
    if (!limpiarModulo) {
      final ModuloCultivo? actual = _modulo;
      if (actual != null) {
        for (final ModuloCultivo modulo in _modulosDisponibles) {
          if (modulo.id == actual.id) {
            return modulo;
          }
        }
      }
    }
    return _modulosDisponibles.first;
  }

  /// Combina el último valor de cada variable con su rango de referencia.
  ///
  /// Las lecturas llegan ordenadas de la más reciente a la más antigua, de modo
  /// que la primera que aparece de cada variable es su último valor conocido.
  List<EstadoDeVariable> _componerVariables(
    List<Lectura> lecturas,
    List<RangoReferencia> rangos,
  ) {
    final Map<String, Lectura> ultimas = <String, Lectura>{};
    for (final Lectura lectura in lecturas) {
      ultimas.putIfAbsent(lectura.variable, () => lectura);
    }
    final Map<String, RangoReferencia> rangosPorVariable =
        <String, RangoReferencia>{
      for (final RangoReferencia rango in rangos) rango.variable: rango,
    };

    return catalogoVariables.map((VariableCatalogo variable) {
      final Lectura? lectura = ultimas[variable.codigo];
      final RangoReferencia? rango = rangosPorVariable[variable.codigo];
      return EstadoDeVariable(
        codigo: variable.codigo,
        nombre: variable.nombre,
        // La unidad del servidor tiene prioridad sobre la del catálogo local.
        unidad: (lectura?.unidad.isNotEmpty ?? false)
            ? lectura!.unidad
            : variable.unidad,
        valor: lectura?.valor,
        fecha: lectura?.timestamp,
        minimo: rango?.minimo,
        maximo: rango?.maximo,
        estado: lectura?.estadoRango,
      );
    }).toList(growable: false);
  }
}
