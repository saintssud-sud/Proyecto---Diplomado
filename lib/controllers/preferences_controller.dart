import 'package:flutter/material.dart';

import '../models/alerta.dart';
import '../models/cultivo.dart';
import '../models/medicion.dart';
import '../models/variable_rango.dart';
import '../services/preferences_service.dart';

class PreferencesController extends ChangeNotifier {
  PreferencesController(this.service) {
    _darkMode = service.getDarkMode();
    _name = service.getName();
    _temperature = service.getTemperature();
    _humidity = service.getHumidity();
    _ph = service.getPh();
    _tds = service.getTds();
    _waterLevel = service.getWaterLevel();
    _lastUpdate = service.getLastUpdate();
    _cultivos = service.getCultivos();
    _rangos = service.getRangos();
    _alertas = service.getAlertas();
    _mediciones = service.getMediciones();
    _perfilNombre = service.getPerfilNombre();
    _perfilCargo = service.getPerfilCargo();
  }

  final PreferencesService service;

  bool _darkMode = false;
  String _name = '';
  double _temperature = 24.5;
  double _humidity = 65.0;
  double _ph = 6.2;
  double _tds = 850.0;
  double _waterLevel = 78.0;
  String _lastUpdate = '';
  List<Cultivo> _cultivos = <Cultivo>[];
  List<VariableRango> _rangos = <VariableRango>[];
  List<Alerta> _alertas = <Alerta>[];
  List<Medicion> _mediciones = <Medicion>[];
  String _perfilNombre = '';
  String _perfilCargo = '';

  bool get darkMode => _darkMode;
  String get name => _name;
  double get temperature => _temperature;
  double get humidity => _humidity;
  double get ph => _ph;
  double get tds => _tds;
  double get waterLevel => _waterLevel;
  String get lastUpdate => _lastUpdate;
  List<Cultivo> get cultivos => _cultivos;
  List<VariableRango> get rangos => _rangos;
  List<Alerta> get alertas => _alertas;
  List<Medicion> get mediciones => _mediciones;
  String get perfilNombre => _perfilNombre;
  String get perfilCargo => _perfilCargo;

  ThemeMode get themeMode => _darkMode ? ThemeMode.dark : ThemeMode.light;

  Future<void> setDarkMode(bool value) async {
    _darkMode = value;
    notifyListeners();
    await service.setDarkMode(value);
  }

  Future<void> setName(String value) async {
    _name = value.trim();
    notifyListeners();
    await service.setName(_name);
  }

  // --- Valores del dashboard (persistentes) ---
  Future<void> setTemperature(double value) async {
    _temperature = value;
    notifyListeners();
    await service.setTemperature(value);
  }

  Future<void> setHumidity(double value) async {
    _humidity = value;
    notifyListeners();
    await service.setHumidity(value);
  }

  Future<void> setPh(double value) async {
    _ph = value;
    notifyListeners();
    await service.setPh(value);
  }

  Future<void> setTds(double value) async {
    _tds = value;
    notifyListeners();
    await service.setTds(value);
  }

  Future<void> setWaterLevel(double value) async {
    _waterLevel = value;
    notifyListeners();
    await service.setWaterLevel(value);
  }

  Future<void> setLastUpdate(String value) async {
    _lastUpdate = value;
    notifyListeners();
    await service.setLastUpdate(value);
  }

  // --- Cultivos ---
  Future<void> setCultivos(List<Cultivo> value) async {
    _cultivos = value;
    notifyListeners();
    await service.setCultivos(value);
  }

  Future<void> addCultivo(Cultivo cultivo) {
    return setCultivos(<Cultivo>[..._cultivos, cultivo]);
  }

  Future<void> removeCultivo(String id) {
    return setCultivos(_cultivos.where((c) => c.id != id).toList());
  }

  // --- Rangos de variables ---
  Future<void> setRangos(List<VariableRango> value) async {
    _rangos = value;
    notifyListeners();
    await service.setRangos(value);
  }

  Future<void> updateRango(VariableRango rango) {
    final index = _rangos.indexWhere((r) => r.variable == rango.variable);
    if (index < 0) return setRangos(<VariableRango>[..._rangos, rango]);
    final nuevos = List<VariableRango>.of(_rangos);
    nuevos[index] = rango;
    return setRangos(nuevos);
  }

  // --- Alertas ---
  Future<void> setAlertas(List<Alerta> value) async {
    _alertas = value;
    notifyListeners();
    await service.setAlertas(value);
  }

  Future<void> marcarAlertaResuelta(String id) {
    final nuevos = _alertas.map((a) {
      if (a.id == id) {
        return Alerta(
          id: a.id,
          titulo: a.titulo,
          nivelActual: a.nivelActual,
          rangoPermitido: a.rangoPermitido,
          fecha: a.fecha,
          estado: 'Resuelta',
          critica: a.critica,
        );
      }
      return a;
    }).toList();
    return setAlertas(nuevos);
  }

  // --- Mediciones históricas ---
  Future<void> setMediciones(List<Medicion> value) async {
    _mediciones = value;
    notifyListeners();
    await service.setMediciones(value);
  }

  // --- Perfil ---
  Future<void> setPerfilNombre(String value) async {
    _perfilNombre = value.trim();
    notifyListeners();
    await service.setPerfilNombre(_perfilNombre);
  }

  Future<void> setPerfilCargo(String value) async {
    _perfilCargo = value.trim();
    notifyListeners();
    await service.setPerfilCargo(_perfilCargo);
  }

  // --- Actualizar valores del dashboard (con persistencia y alertas) ---
  /// Etiqueta de fecha/hora actual con formato: dd/mm/aaaa hh:mm a. m.
  static String nowLabel() {
    final ahora = DateTime.now();
    final h = ahora.hour;
    final periodo = h >= 12 ? 'p. m.' : 'a. m.';
    final h12 = h % 12 == 0 ? 12 : h % 12;
    return '${ahora.day.toString().padLeft(2, '0')}/'
        '${ahora.month.toString().padLeft(2, '0')}/'
        '${ahora.year} '
        '${h12.toString().padLeft(2, '0')}:'
        '${ahora.minute.toString().padLeft(2, '0')} $periodo';
  }

  static String _fmtValor(double v) {
    return v == v.roundToDouble() ? v.toStringAsFixed(0) : v.toStringAsFixed(1);
  }

  /// Actualiza todos los valores del dashboard, guarda la fecha/hora de
  /// actualización y sincroniza las alertas automáticamente.
  Future<void> actualizarValores({
    required double temperatura,
    required double humedad,
    required double ph,
    required double tds,
    required double nivelAgua,
  }) async {
    _temperature = temperatura;
    _humidity = humedad;
    _ph = ph;
    _tds = tds;
    _waterLevel = nivelAgua;
    _lastUpdate = nowLabel();
    notifyListeners();
    await Future.wait(<Future<void>>[
      service.setTemperature(_temperature),
      service.setHumidity(_humidity),
      service.setPh(_ph),
      service.setTds(_tds),
      service.setWaterLevel(_waterLevel),
      service.setLastUpdate(_lastUpdate),
    ]);
    await _syncAlertas();
    await _registrarMedicion();
  }

  /// Agrega una nueva medición al historial con los valores actuales.
  Future<void> _registrarMedicion() async {
    final nuevas = <Medicion>[
      ..._mediciones,
      Medicion(
        fechaHora: nowLabel(),
        temperatura: _temperature,
        humedad: _humidity,
        ph: _ph,
        tds: _tds,
      ),
    ];
    _mediciones = nuevas;
    notifyListeners();
    await service.setMediciones(nuevas);
  }

  /// Si una variable quedó fuera de su rango óptimo y no existe una alerta
  /// activa para ella, la crea automáticamente (persistente).
  Future<void> _syncAlertas() async {
    final nuevos = List<Alerta>.of(_alertas);
    var cambios = false;

    void verificar(
      String nombre,
      double valor,
      String unidad, {
      required String titulo,
    }) {
      VariableRango? rango;
      for (final r in _rangos) {
        if (r.variable == nombre) {
          rango = r;
          break;
        }
      }
      if (rango == null) return;
      final fuera = valor < rango.minimo || valor > rango.maximo;
      final existe = nuevos.any(
        (a) => a.titulo == titulo && a.estado == 'Activa',
      );
      if (fuera && !existe) {
        nuevos.add(
          Alerta(
            id: DateTime.now().microsecondsSinceEpoch.toString(),
            titulo: titulo,
            nivelActual: 'Nivel actual: ${_fmtValor(valor)} $unidad'.trim(),
            rangoPermitido:
                'Rango permitido: ${_fmtValor(rango.minimo)} - '
                        '${_fmtValor(rango.maximo)} $unidad'
                    .trim(),
            fecha: nowLabel(),
            estado: 'Activa',
            critica: true,
          ),
        );
        cambios = true;
      }
    }

    verificar(
      'Temperatura',
      _temperature,
      '°C',
      titulo: 'Temperatura fuera de rango',
    );
    verificar('Humedad', _humidity, '%', titulo: 'Humedad fuera de rango');
    verificar('pH', _ph, '', titulo: 'pH fuera de rango');
    verificar('TDS', _tds, 'ppm', titulo: 'TDS alto');
    verificar('Nivel de agua', _waterLevel, '%', titulo: 'Nivel de agua bajo');

    if (cambios) {
      _alertas = nuevos;
      notifyListeners();
      await service.setAlertas(nuevos);
    }
  }
}
