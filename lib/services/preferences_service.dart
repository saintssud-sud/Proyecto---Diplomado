import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../models/alerta.dart';
import '../models/cultivo.dart';
import '../models/medicion.dart';
import '../models/variable_rango.dart';

class PreferencesService {
  PreferencesService(this.preferences);

  final SharedPreferences preferences;

  static const String darkModeKey = 'dark_mode';
  static const String nameKey = 'student_name';

  // Claves de los valores del dashboard (persistencia).
  static const String temperatureKey = 'dashboard_temperature';
  static const String humidityKey = 'dashboard_humidity';
  static const String phKey = 'dashboard_ph';
  static const String tdsKey = 'dashboard_tds';
  static const String waterLevelKey = 'dashboard_water_level';
  static const String lastUpdateKey = 'dashboard_last_update';

  // Claves de los cultivos (lista en JSON).
  static const String cultivosKey = 'cultivos_list';

  // Claves de rangos, alertas, mediciones y perfil.
  static const String rangosKey = 'rangos_variables';
  static const String alertasKey = 'alertas_list';
  static const String medicionesKey = 'mediciones_list';
  static const String perfilNombreKey = 'perfil_nombre';
  static const String perfilCargoKey = 'perfil_cargo';

  bool getDarkMode() => preferences.getBool(darkModeKey) ?? false;
  String getName() => preferences.getString(nameKey) ?? '';

  Future<void> setDarkMode(bool value) {
    return preferences.setBool(darkModeKey, value);
  }

  Future<void> setName(String value) {
    return preferences.setString(nameKey, value.trim());
  }

  // --- Valores del dashboard ---
  double getTemperature() => preferences.getDouble(temperatureKey) ?? 24.5;
  double getHumidity() => preferences.getDouble(humidityKey) ?? 65.0;
  double getPh() => preferences.getDouble(phKey) ?? 6.2;
  double getTds() => preferences.getDouble(tdsKey) ?? 850.0;
  double getWaterLevel() => preferences.getDouble(waterLevelKey) ?? 78.0;
  String getLastUpdate() =>
      preferences.getString(lastUpdateKey) ?? '31/05/2026 11:30 a. m.';

  Future<void> setTemperature(double value) =>
      preferences.setDouble(temperatureKey, value);
  Future<void> setHumidity(double value) =>
      preferences.setDouble(humidityKey, value);
  Future<void> setPh(double value) => preferences.setDouble(phKey, value);
  Future<void> setTds(double value) => preferences.setDouble(tdsKey, value);
  Future<void> setWaterLevel(double value) =>
      preferences.setDouble(waterLevelKey, value);
  Future<void> setLastUpdate(String value) =>
      preferences.setString(lastUpdateKey, value);

  // --- Cultivos ---
  List<Cultivo> getCultivos() {
    final raw = preferences.getString(cultivosKey);
    if (raw == null || raw.isEmpty) {
      return Cultivo.seed();
    }
    final list = jsonDecode(raw) as List<dynamic>;
    return list
        .map((item) => Cultivo.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<void> setCultivos(List<Cultivo> cultivos) {
    final raw = jsonEncode(cultivos.map((c) => c.toJson()).toList());
    return preferences.setString(cultivosKey, raw);
  }

  // --- Rangos de variables ---
  List<VariableRango> getRangos() {
    final raw = preferences.getString(rangosKey);
    if (raw == null || raw.isEmpty) {
      return VariableRango.seed();
    }
    final list = jsonDecode(raw) as List<dynamic>;
    return list
        .map((item) => VariableRango.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<void> setRangos(List<VariableRango> rangos) {
    final raw = jsonEncode(rangos.map((r) => r.toJson()).toList());
    return preferences.setString(rangosKey, raw);
  }

  // --- Alertas ---
  List<Alerta> getAlertas() {
    final raw = preferences.getString(alertasKey);
    if (raw == null || raw.isEmpty) {
      return Alerta.seed();
    }
    final list = jsonDecode(raw) as List<dynamic>;
    return list
        .map((item) => Alerta.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<void> setAlertas(List<Alerta> alertas) {
    final raw = jsonEncode(alertas.map((a) => a.toJson()).toList());
    return preferences.setString(alertasKey, raw);
  }

  // --- Mediciones históricas ---
  List<Medicion> getMediciones() {
    final raw = preferences.getString(medicionesKey);
    if (raw == null || raw.isEmpty) {
      return Medicion.seed();
    }
    final list = jsonDecode(raw) as List<dynamic>;
    return list
        .map((item) => Medicion.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<void> setMediciones(List<Medicion> mediciones) {
    final raw = jsonEncode(mediciones.map((m) => m.toJson()).toList());
    return preferences.setString(medicionesKey, raw);
  }

  // --- Perfil ---
  String getPerfilNombre() =>
      preferences.getString(perfilNombreKey) ?? 'Juan Pérez';
  String getPerfilCargo() =>
      preferences.getString(perfilCargoKey) ?? 'Jefe de operaciones';

  Future<void> setPerfilNombre(String value) {
    return preferences.setString(perfilNombreKey, value.trim());
  }

  Future<void> setPerfilCargo(String value) {
    return preferences.setString(perfilCargoKey, value.trim());
  }
}
