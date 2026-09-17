import 'package:flutter/foundation.dart';

import '../models/api/modelos_api.dart';
import '../repositories/api/perfiles_api_repository.dart';
import '../repositories/api/rangos_api_repository.dart';
import '../utils/formato_fecha.dart';
import '../widgets/vista_con_estados.dart';
import 'estado_de_vista.dart';

/// Un cultivo —la especie— con los rangos de referencia que tiene definidos.
///
/// Conviene no confundir dos conceptos del sistema: el **módulo** es la
/// instalación física donde están los sensores, y el **cultivo** es la especie
/// que se siembra en él —lechuga, acelga, apio— con los rangos de referencia
/// contra los que el servidor evalúa cada lectura.
class CultivoConRangos {
  const CultivoConRangos({required this.perfil, required this.rangos});

  final PerfilCultivo perfil;
  final List<RangoReferencia> rangos;

  String get id => perfil.id;
  String get nombre => perfil.nombre;
  String? get descripcion => perfil.descripcion;

  /// Los rangos del cultivo en una línea, para presentarlos en la lista.
  String get resumenRangos {
    if (rangos.isEmpty) {
      return 'Sin rangos definidos todavía';
    }
    final List<String> partes = rangos
        .map(
          (RangoReferencia rango) =>
              '${rango.nombreVariable} ${formatearValor(rango.minimo)}–'
              '${formatearValor(rango.maximo)} ${rango.unidad}'.trim(),
        )
        .toList(growable: false);
    return partes.join(' · ');
  }
}

/// Rango que se enviará al servicio al registrar un cultivo.
class RangoNuevo {
  const RangoNuevo({
    required this.variable,
    required this.minimo,
    required this.maximo,
  });

  final String variable;
  final double minimo;
  final double maximo;
}

/// Controlador del catálogo de cultivos.
///
/// Los cultivos —y sus rangos— viven en el servicio: son los valores contra los
/// que se evalúa cada lectura del módulo. Añadir un cultivo consiste, por tanto,
/// en registrarlo y definirle sus rangos, y no en guardar una preferencia local.
class CultivosController extends ChangeNotifier {
  CultivosController({
    required PerfilesApiRepository perfiles,
    required RangosApiRepository rangos,
  })  : _perfiles = perfiles,
        _rangos = rangos;

  final PerfilesApiRepository _perfiles;
  final RangosApiRepository _rangos;

  EstadoVista _estado = EstadoVista.cargando;
  String? _mensajeError;
  bool _errorDeConexion = false;
  List<CultivoConRangos> _cultivos = const <CultivoConRangos>[];

  EstadoVista get estado => _estado;
  String? get mensajeError => _mensajeError;
  bool get errorDeConexion => _errorDeConexion;
  List<CultivoConRangos> get cultivos => _cultivos;

  /// Consulta los cultivos registrados con sus rangos de referencia.
  ///
  /// Se piden los perfiles y los rangos en la misma operación lógica: presentar
  /// un cultivo sin sus rangos haría creer que no tiene límites definidos.
  Future<void> cargar() async {
    _estado = EstadoVista.cargando;
    _mensajeError = null;
    _errorDeConexion = false;
    notifyListeners();

    try {
      final List<PerfilCultivo> perfiles = await _perfiles.listar();
      final List<RangoReferencia> rangos = await _rangos.listar();

      _cultivos = List<CultivoConRangos>.unmodifiable(
        perfiles.map(
          (PerfilCultivo perfil) => CultivoConRangos(
            perfil: perfil,
            rangos: rangos
                .where((RangoReferencia rango) => rango.perfilId == perfil.id)
                .toList(growable: false),
          ),
        ),
      );
      _estado = _cultivos.isEmpty ? EstadoVista.vacio : EstadoVista.conDatos;
    } catch (error) {
      final FalloDeVista fallo = FalloDeVista.desde(error);
      _cultivos = const <CultivoConRangos>[];
      _mensajeError = fallo.mensaje;
      _errorDeConexion = fallo.deConexion;
      _estado = EstadoVista.error;
    } finally {
      notifyListeners();
    }
  }

  /// Registra un cultivo y, a continuación, los rangos indicados.
  ///
  /// El orden no es casual: el rango pertenece al cultivo, de modo que primero
  /// se registra el cultivo y después se le asocian sus límites.
  Future<void> crear({
    required String nombre,
    String? descripcion,
    List<RangoNuevo> rangos = const <RangoNuevo>[],
  }) async {
    final PerfilCultivo perfil = await _perfiles.crear(
      nombre: nombre,
      descripcion: descripcion,
    );
    for (final RangoNuevo rango in rangos) {
      await _rangos.crear(
        perfilId: perfil.id,
        variable: rango.variable,
        minimo: rango.minimo,
        maximo: rango.maximo,
      );
    }
    await cargar();
  }

  /// Define o corrige los rangos de un cultivo ya registrado.
  ///
  /// Un cultivo creado sin rangos no se podía completar después: la pantalla
  /// solo permitía registrarlo entero con sus rangos o eliminarlo, y la pantalla
  /// de rangos únicamente edita los que ya existen. Como las lecturas de un
  /// cultivo sin rangos no se evalúan ni generan alertas, la única salida era
  /// borrarlo y volverlo a crear. Aquí se actualiza el rango que ya existe y se
  /// crea el que falta, de modo que completar un cultivo no obligue a perderlo.
  Future<void> guardarRangos(
    CultivoConRangos cultivo,
    List<RangoNuevo> rangos,
  ) async {
    for (final RangoNuevo rango in rangos) {
      final RangoReferencia? existente = _rangoDe(cultivo, rango.variable);
      if (existente == null) {
        await _rangos.crear(
          perfilId: cultivo.id,
          variable: rango.variable,
          minimo: rango.minimo,
          maximo: rango.maximo,
        );
      } else {
        await _rangos.actualizar(
          existente.id,
          minimo: rango.minimo,
          maximo: rango.maximo,
        );
      }
    }
    await cargar();
  }

  /// Rango del cultivo para la variable indicada, si ya está definido.
  RangoReferencia? _rangoDe(CultivoConRangos cultivo, String variable) {
    for (final RangoReferencia rango in cultivo.rangos) {
      if (rango.variable == variable) {
        return rango;
      }
    }
    return null;
  }

  /// Elimina un cultivo junto con sus rangos.
  ///
  /// El servicio rechaza eliminar un cultivo que todavía tiene rangos definidos,
  /// de modo que la aplicación retira primero los rangos y después el cultivo:
  /// la regla del dominio se respeta en lugar de rodearse.
  Future<void> eliminar(CultivoConRangos cultivo) async {
    for (final RangoReferencia rango in cultivo.rangos) {
      await _rangos.eliminar(rango.id);
    }
    await _perfiles.eliminar(cultivo.id);
    await cargar();
  }
}
