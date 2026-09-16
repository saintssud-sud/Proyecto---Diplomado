import 'package:flutter/foundation.dart';

import '../models/api/modelos_api.dart';
import '../repositories/api/modulos_api_repository.dart';
import '../repositories/api/perfiles_api_repository.dart';
import '../widgets/vista_con_estados.dart';
import 'estado_de_vista.dart';

/// Controlador de los módulos o zonas de cultivo.
///
/// Un módulo es la unidad física del sistema: tiene un tipo de cultivo, un
/// perfil de referencia (de donde salen los rangos con los que se evalúan sus
/// lecturas) y un estado de activación. Es el equivalente en el servicio de lo
/// que la aplicación llamaba «cultivo».
class ModulosController extends ChangeNotifier {
  ModulosController({
    required ModulosApiRepository modulos,
    required PerfilesApiRepository perfiles,
  })  : _modulos = modulos,
        _perfiles = perfiles;

  final ModulosApiRepository _modulos;
  final PerfilesApiRepository _perfiles;

  EstadoVista _estado = EstadoVista.cargando;
  String? _mensajeError;
  bool _errorDeConexion = false;
  List<ModuloCultivo> _modulosCargados = const <ModuloCultivo>[];
  List<PerfilCultivo> _perfilesDisponibles = const <PerfilCultivo>[];

  EstadoVista get estado => _estado;
  String? get mensajeError => _mensajeError;
  bool get errorDeConexion => _errorDeConexion;
  List<ModuloCultivo> get modulos => _modulosCargados;

  /// Perfiles de cultivo que pueden asociarse a un módulo nuevo.
  List<PerfilCultivo> get perfiles => _perfilesDisponibles;

  /// Nombre presentable del perfil; si no se pudo resolver, devuelve el id.
  String nombrePerfil(String perfilId) {
    for (final PerfilCultivo perfil in _perfilesDisponibles) {
      if (perfil.id == perfilId) {
        return perfil.nombre;
      }
    }
    return perfilId;
  }

  /// Consulta los módulos y los perfiles de cultivo.
  Future<void> cargar() async {
    _estado = EstadoVista.cargando;
    _mensajeError = null;
    _errorDeConexion = false;
    notifyListeners();

    try {
      final List<ModuloCultivo> modulos = await _modulos.listar();
      _perfilesDisponibles = await _perfiles.listar();
      _modulosCargados = List<ModuloCultivo>.unmodifiable(modulos);
      _estado = _modulosCargados.isEmpty ? EstadoVista.vacio : EstadoVista.conDatos;
    } catch (error) {
      final FalloDeVista fallo = FalloDeVista.desde(error);
      _modulosCargados = const <ModuloCultivo>[];
      _mensajeError = fallo.mensaje;
      _errorDeConexion = fallo.deConexion;
      _estado = EstadoVista.error;
    } finally {
      notifyListeners();
    }
  }

  /// Registra un módulo en el servicio y refresca la lista.
  Future<void> crear({
    required String nombre,
    required String tipoCultivo,
    required String perfilId,
    String? ubicacion,
  }) async {
    await _modulos.crear(
      nombre: nombre,
      tipoCultivo: tipoCultivo,
      perfilId: perfilId,
      ubicacion: ubicacion,
    );
    await cargar();
  }

  /// Activa o desactiva un módulo y refresca la lista.
  Future<void> cambiarActivacion(ModuloCultivo modulo) async {
    await _modulos.actualizar(modulo.id, activo: !modulo.activo);
    await cargar();
  }

  /// Modifica los datos de un módulo y refresca la lista.
  Future<void> editar(
    ModuloCultivo modulo, {
    String? nombre,
    String? tipoCultivo,
    String? perfilId,
    String? ubicacion,
  }) async {
    await _modulos.actualizar(
      modulo.id,
      nombre: nombre,
      tipoCultivo: tipoCultivo,
      perfilId: perfilId,
      ubicacion: ubicacion,
    );
    await cargar();
  }

  /// Elimina un módulo.
  ///
  /// El servidor rechaza la operación si el módulo tiene lecturas registradas:
  /// esa comprobación no se duplica aquí, se deja al servicio, que es quien
  /// conoce el estado de los datos.
  Future<void> eliminar(ModuloCultivo modulo) async {
    await _modulos.eliminar(modulo.id);
    await cargar();
  }
}
