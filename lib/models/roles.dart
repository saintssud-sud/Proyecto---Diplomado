/// Nombres de los roles del sistema.
///
/// **Estos valores deben coincidir con los que usa el servicio**, que los lee
/// de su configuración (`ROL_ADMINISTRADOR` y `ROL_OPERADOR` en
/// `backend/app/config.py`).
///
/// Se declaran en un solo lugar a propósito. El motivo es concreto: cuando el
/// servicio pasó a llamar a los roles «administrador» y «operador», en la
/// aplicación quedaron siete comparaciones escritas a mano con los nombres
/// anteriores. La comprobación del rol de administración empezó a dar falso, y
/// la pantalla de gestión de usuarios desapareció de Ajustes sin que ninguna
/// prueba lo advirtiera. Con una sola fuente, un cambio de vocabulario se hace
/// en un sitio y no hay lugares donde olvidarlo.
class Roles {
  const Roles._();

  /// Rol con atribuciones de administración: gestiona módulos, rangos y cuentas.
  static const String administrador = 'administrador';

  /// Rol de operación: registra lecturas y consulta la información del cultivo.
  static const String operador = 'operador';

  /// Rol de solo consulta.
  static const String invitado = 'invitado';

  /// Rol asignado por defecto, que es el de menor privilegio.
  ///
  /// Una cuenta sin rol reconocido no debe recibir atribuciones: si el valor
  /// llegara vacío o con un nombre inesperado, se asume el mínimo.
  static const String porDefecto = operador;

  /// Indica si un rol tiene atribuciones de administración.
  static bool esAdministrador(String? rol) => rol == administrador;

  /// Texto presentable de un rol, para la interfaz.
  static String etiqueta(String? rol) {
    switch (rol) {
      case administrador:
        return 'Administrador';
      case operador:
        return 'Operador';
      case invitado:
        return 'Invitado';
      default:
        return (rol == null || rol.isEmpty) ? 'Sin rol' : rol;
    }
  }

  /// Normaliza el valor de rol recibido a uno de los tres conocidos.
  ///
  /// Admite también los nombres anteriores —`admin` y `usuario`— para que un
  /// documento que no se haya migrado siga resolviendo al rol correcto en lugar
  /// de caer al valor por defecto.
  static String normalizar(dynamic valor) {
    final texto = (valor ?? '').toString().trim().toLowerCase();
    switch (texto) {
      case administrador:
      case 'admin':
        return administrador;
      case operador:
      case 'usuario':
        return operador;
      case invitado:
        return invitado;
      default:
        return porDefecto;
    }
  }

  /// Devuelve el otro rol de operación, para alternar desde el panel.
  ///
  /// El panel permite alternar entre administración y operación; el rol de
  /// invitado no se asigna desde ahí.
  static String alternar(String? rol) =>
      esAdministrador(rol) ? operador : administrador;
}
