/// Modelos de los recursos que expone la API del backend.
///
/// Se mantienen juntos porque cambian juntos: todos corresponden al contrato
/// del apartado 2.4.4 de la monografía y sus nombres de campo son los que el
/// servidor envía, en notación de serpiente (`tipo_cultivo`, `perfil_id`,
/// `estado_rango`). No se reutilizan los modelos de la persistencia local
/// porque su forma es distinta y forzar la conversión perdería información.
library;

import '../../services/api_errores.dart';

// Los errores de la capa de API viven en `services/api_errores.dart`, junto con
// el resto de los errores de esa capa. Se reexporta [ErrorDeContrato] porque es
// el error que produce la lectura de estos modelos.
export '../../services/api_errores.dart' show ErrorDeContrato;

// ---------------------------------------------------------------------------
// Catálogo de variables
// ---------------------------------------------------------------------------

/// Variable gestionada por el sistema.
class VariableCatalogo {
  const VariableCatalogo({
    required this.codigo,
    required this.nombre,
    required this.unidad,
  });

  /// Código con el que el backend identifica la variable (`ph`, `temp_solucion`…).
  final String codigo;

  /// Nombre presentable en la interfaz.
  final String nombre;

  final String unidad;
}

/// Catálogo de variables que la aplicación presenta en la interfaz.
///
/// Los códigos son los mismos del catálogo del backend. La aplicación mantiene
/// esta copia solo para mostrar nombres y unidades; la validación de los valores
/// y la evaluación contra los rangos las realiza siempre el servidor.
const List<VariableCatalogo> catalogoVariables = <VariableCatalogo>[
  VariableCatalogo(codigo: 'ph', nombre: 'pH', unidad: ''),
  VariableCatalogo(
    codigo: 'tds',
    nombre: 'Sólidos disueltos totales',
    unidad: 'ppm',
  ),
  VariableCatalogo(
    codigo: 'ec',
    nombre: 'Conductividad eléctrica',
    unidad: 'mS/cm',
  ),
  VariableCatalogo(
    codigo: 'temp_solucion',
    nombre: 'Temperatura de la solución nutritiva',
    unidad: '°C',
  ),
  VariableCatalogo(
    codigo: 'temp_ambiental',
    nombre: 'Temperatura ambiental',
    unidad: '°C',
  ),
  VariableCatalogo(codigo: 'humedad', nombre: 'Humedad relativa', unidad: '%'),
  VariableCatalogo(codigo: 'nivel_agua', nombre: 'Nivel de agua', unidad: 'cm'),
];

/// Nombre presentable de una variable; si el código es desconocido, lo devuelve tal cual.
String nombreDeVariable(String codigo) {
  for (final VariableCatalogo variable in catalogoVariables) {
    if (variable.codigo == codigo) {
      return variable.nombre;
    }
  }
  return codigo;
}

/// Unidad de una variable según el catálogo, vacía si el código es desconocido.
String unidadDeVariable(String codigo) {
  for (final VariableCatalogo variable in catalogoVariables) {
    if (variable.codigo == codigo) {
      return variable.unidad;
    }
  }
  return '';
}

// ---------------------------------------------------------------------------
// Utilidades internas de lectura
// ---------------------------------------------------------------------------

String _texto(
  Map<String, dynamic> json,
  String campo, {
  String porDefecto = '',
}) {
  final Object? valor = json[campo];
  return valor == null ? porDefecto : valor.toString();
}

double _numero(Map<String, dynamic> json, String campo) {
  final Object? valor = json[campo];
  if (valor is num) {
    return valor.toDouble();
  }
  if (valor is String) {
    final double? convertido = double.tryParse(valor);
    if (convertido != null) {
      return convertido;
    }
  }
  throw ErrorDeContrato(
    'El campo "$campo" debía ser numérico y llegó como "$valor".',
  );
}

DateTime _fecha(Map<String, dynamic> json, String campo) {
  final Object? valor = json[campo];
  final DateTime? fecha = valor == null
      ? null
      : DateTime.tryParse(valor.toString());
  if (fecha == null) {
    throw ErrorDeContrato('El campo "$campo" no contiene una fecha válida.');
  }
  return fecha;
}

// ---------------------------------------------------------------------------
// Recursos
// ---------------------------------------------------------------------------

/// Módulo o zona de cultivo.
class ModuloCultivo {
  const ModuloCultivo({
    required this.id,
    required this.nombre,
    required this.tipoCultivo,
    required this.perfilId,
    this.perfilNombre = '',
    this.ubicacion,
    this.activo = true,
  });

  final String id;
  final String nombre;
  final String tipoCultivo;
  final String perfilId;

  /// Nombre del perfil de referencia, resuelto por el servicio.
  ///
  /// Llega vacío si el perfil ya no existe: en ese caso se muestra el módulo sin
  /// nombrar el perfil, en lugar de dejar la pantalla sin información.
  final String perfilNombre;
  final String? ubicacion;
  final bool activo;

  /// Perfil que se muestra: el nombre que envía el servicio y, si no llegó, el
  /// identificador, para no dejar el dato en blanco.
  String get perfilVisible => perfilNombre.isNotEmpty ? perfilNombre : perfilId;

  factory ModuloCultivo.fromJson(Map<String, dynamic> json) {
    return ModuloCultivo(
      id: _texto(json, 'id'),
      nombre: _texto(json, 'nombre'),
      tipoCultivo: _texto(json, 'tipo_cultivo'),
      perfilId: _texto(json, 'perfil_id'),
      perfilNombre: _texto(json, 'perfil_nombre'),
      ubicacion: json['ubicacion']?.toString(),
      activo: json['activo'] as bool? ?? true,
    );
  }
}

/// Perfil de cultivo al que se asocian los rangos de referencia.
class PerfilCultivo {
  const PerfilCultivo({
    required this.id,
    required this.nombre,
    this.descripcion,
    this.predefinido = false,
  });

  final String id;
  final String nombre;
  final String? descripcion;
  final bool predefinido;

  factory PerfilCultivo.fromJson(Map<String, dynamic> json) {
    return PerfilCultivo(
      id: _texto(json, 'id'),
      nombre: _texto(json, 'nombre'),
      descripcion: json['descripcion']?.toString(),
      predefinido: json['predefinido'] as bool? ?? false,
    );
  }
}

/// Rango de referencia de una variable dentro de un perfil de cultivo.
class RangoReferencia {
  const RangoReferencia({
    required this.id,
    required this.perfilId,
    required this.variable,
    required this.minimo,
    required this.maximo,
    this.unidad = '',
  });

  final String id;
  final String perfilId;
  final String variable;
  final double minimo;
  final double maximo;
  final String unidad;

  /// Nombre presentable de la variable.
  String get nombreVariable => nombreDeVariable(variable);

  factory RangoReferencia.fromJson(Map<String, dynamic> json) {
    return RangoReferencia(
      id: _texto(json, 'id'),
      perfilId: _texto(json, 'perfil_id'),
      variable: _texto(json, 'variable'),
      minimo: _numero(json, 'minimo'),
      maximo: _numero(json, 'maximo'),
      unidad: _texto(
        json,
        'unidad',
        porDefecto: unidadDeVariable(_texto(json, 'variable')),
      ),
    );
  }
}

/// Estados posibles de una lectura respecto de su rango de referencia.
class EstadoRango {
  const EstadoRango._();

  static const String dentro = 'dentro';
  static const String bajo = 'bajo';
  static const String alto = 'alto';
  static const String sinRango = 'sin_rango';

  /// Texto presentable del estado.
  static String etiqueta(String estado) {
    switch (estado) {
      case dentro:
        return 'Normal';
      case bajo:
        return 'Por debajo del rango';
      case alto:
        return 'Por encima del rango';
      case sinRango:
        return 'Sin rango configurado';
      default:
        return estado;
    }
  }

  /// Indica si el valor salió del rango de referencia.
  static bool esFueraDeRango(String estado) => estado == bajo || estado == alto;
}

/// Lectura de una variable, con su origen y el estado que le asignó el servidor.
class Lectura {
  const Lectura({
    required this.id,
    required this.moduloId,
    required this.variable,
    required this.valor,
    required this.unidad,
    required this.origen,
    required this.timestamp,
    this.estadoRango,
    this.observacion,
  });

  final String id;
  final String moduloId;
  final String variable;
  final double valor;
  final String unidad;

  /// `automatico` si la envió el módulo de adquisición, `manual` si la registró
  /// una persona.
  final String origen;
  final DateTime timestamp;
  final String? estadoRango;

  /// Observación anotada al registrar la medición; nula si no se anotó.
  final String? observacion;

  bool get esManual => origen == 'manual';

  String get nombreVariable => nombreDeVariable(variable);

  factory Lectura.fromJson(Map<String, dynamic> json) {
    return Lectura(
      id: _texto(json, 'id'),
      moduloId: _texto(json, 'modulo_id'),
      variable: _texto(json, 'variable'),
      valor: _numero(json, 'valor'),
      unidad: _texto(json, 'unidad'),
      origen: _texto(json, 'origen', porDefecto: 'automatico'),
      timestamp: _fecha(json, 'timestamp'),
      estadoRango: json['estado_rango']?.toString(),
      observacion: json['observacion']?.toString(),
    );
  }
}

/// Promedio, máximo y mínimo de una variable en el periodo consultado.
class ResumenVariable {
  const ResumenVariable({
    required this.variable,
    required this.unidad,
    required this.cantidad,
    required this.promedio,
    required this.maximo,
    required this.minimo,
  });

  final String variable;
  final String unidad;
  final int cantidad;
  final double promedio;
  final double maximo;
  final double minimo;

  String get nombreVariable => nombreDeVariable(variable);

  factory ResumenVariable.fromJson(Map<String, dynamic> json) {
    final Object? cantidad = json['cantidad'];
    return ResumenVariable(
      variable: _texto(json, 'variable'),
      unidad: _texto(json, 'unidad'),
      cantidad: cantidad is num ? cantidad.toInt() : 0,
      promedio: _numero(json, 'promedio'),
      maximo: _numero(json, 'maximo'),
      minimo: _numero(json, 'minimo'),
    );
  }
}

/// Alerta generada por el servidor cuando una lectura salió de su rango.
class AlertaServidor {
  const AlertaServidor({
    required this.id,
    required this.lecturaId,
    required this.moduloId,
    required this.variable,
    required this.valor,
    required this.rangoMinimo,
    required this.rangoMaximo,
    required this.estado,
    required this.timestamp,
    this.unidad = '',
    this.desviacion,
    this.observacion,
  });

  final String id;

  /// Lectura que originó la alerta: es la trazabilidad que exige el sistema.
  final String lecturaId;
  final String moduloId;
  final String variable;
  final double valor;
  final double rangoMinimo;
  final double rangoMaximo;

  /// `activa` o `atendida`.
  final String estado;
  final DateTime timestamp;
  final String unidad;

  /// `bajo` o `alto`, según de qué lado del rango quedó el valor.
  final String? desviacion;
  final String? observacion;

  bool get estaActiva => estado == 'activa';

  String get nombreVariable => nombreDeVariable(variable);

  factory AlertaServidor.fromJson(Map<String, dynamic> json) {
    return AlertaServidor(
      id: _texto(json, 'id'),
      lecturaId: _texto(json, 'lectura_id'),
      moduloId: _texto(json, 'modulo_id'),
      variable: _texto(json, 'variable'),
      valor: _numero(json, 'valor'),
      rangoMinimo: _numero(json, 'rango_minimo'),
      rangoMaximo: _numero(json, 'rango_maximo'),
      estado: _texto(json, 'estado', porDefecto: 'activa'),
      timestamp: _fecha(json, 'timestamp'),
      unidad:
          json['unidad']?.toString() ??
          unidadDeVariable(_texto(json, 'variable')),
      desviacion: json['desviacion']?.toString(),
      observacion: json['observacion']?.toString(),
    );
  }
}

/// Perfil de la cuenta que tiene la sesión iniciada.
///
/// El identificador es el **uid** de Firebase Authentication; el rol lo resuelve
/// el servicio al autorizar cada petición, de modo que la aplicación lo presenta
/// pero nunca lo decide.
class PerfilUsuario {
  const PerfilUsuario({
    required this.id,
    this.email = '',
    this.nombre = '',
    this.rol = '',
    this.activo = true,
    this.telefono,
    this.cargo,
  });

  final String id;
  final String email;
  final String nombre;
  final String rol;
  final bool activo;
  final String? telefono;
  final String? cargo;

  bool get esAdministrador => rol == 'admin';

  /// Texto presentable del rol.
  String get etiquetaRol {
    switch (rol) {
      case 'admin':
        return 'Administrador';
      case 'usuario':
        return 'Operador';
      default:
        return rol.isEmpty ? 'Sin rol' : rol;
    }
  }

  factory PerfilUsuario.fromJson(Map<String, dynamic> json) {
    return PerfilUsuario(
      id: _texto(json, 'id'),
      email: json['email']?.toString() ?? '',
      nombre: json['nombre']?.toString() ?? '',
      rol: json['rol']?.toString() ?? '',
      // Un perfil sin el campo `activo` se considera habilitado: solo la
      // desactivación explícita bloquea el acceso, igual que en el servicio.
      activo: json['activo'] != false,
      telefono: json['telefono']?.toString(),
      cargo: json['cargo']?.toString(),
    );
  }
}
