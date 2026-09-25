import 'package:flutter_test/flutter_test.dart';
import 'package:sigvach/models/roles.dart';
import 'package:sigvach/models/usuario_perfil.dart';

/// Pruebas del vocabulario de roles.
///
/// Están aquí por un fallo concreto: cuando el servicio pasó a llamar a los
/// roles «administrador» y «operador», la aplicación seguía comparando con
/// «admin». La comprobación del rol de administración empezó a dar falso y la
/// pantalla de gestión de usuarios desapareció de Ajustes, sin que ninguna
/// prueba lo advirtiera. Las que siguen cubren justamente ese punto.
void main() {
  group('Roles', () {
    test('reconoce el rol de administración con el nombre del servicio', () {
      expect(Roles.esAdministrador(Roles.administrador), isTrue);
      expect(Roles.esAdministrador(Roles.operador), isFalse);
      expect(Roles.esAdministrador(Roles.invitado), isFalse);
    });

    test('trata un rol nulo o vacío como el de menor privilegio', () {
      // Una cuenta sin rol reconocido no debe recibir atribuciones.
      expect(Roles.esAdministrador(null), isFalse);
      expect(Roles.esAdministrador(''), isFalse);
      expect(Roles.normalizar(null), Roles.porDefecto);
      expect(Roles.normalizar(''), Roles.porDefecto);
      expect(Roles.normalizar('algo-desconocido'), Roles.porDefecto);
    });

    test('normaliza también los nombres anteriores del vocabulario', () {
      // Un documento que no se haya migrado debe resolver al rol correcto.
      expect(Roles.normalizar('admin'), Roles.administrador);
      expect(Roles.normalizar('usuario'), Roles.operador);
      expect(Roles.normalizar('administrador'), Roles.administrador);
      expect(Roles.normalizar('operador'), Roles.operador);
    });

    test('normaliza sin distinguir mayúsculas ni espacios', () {
      expect(Roles.normalizar('  ADMINISTRADOR '), Roles.administrador);
      expect(Roles.normalizar('Operador'), Roles.operador);
    });

    test('traduce los roles a texto presentable', () {
      expect(Roles.etiqueta(Roles.administrador), 'Administrador');
      expect(Roles.etiqueta(Roles.operador), 'Operador');
      expect(Roles.etiqueta(Roles.invitado), 'Invitado');
      expect(Roles.etiqueta(''), 'Sin rol');
    });

    test('alterna entre administración y operación', () {
      expect(Roles.alternar(Roles.administrador), Roles.operador);
      expect(Roles.alternar(Roles.operador), Roles.administrador);
      expect(Roles.alternar(null), Roles.administrador);
    });
  });

  group('UsuarioPerfil', () {
    test('reconoce al administrador del servicio', () {
      const perfil = UsuarioPerfil(rol: Roles.administrador);
      expect(perfil.esAdmin, isTrue);
      expect(perfil.etiquetaRol, 'Administrador');
    });

    test('no reconoce como administrador al operador', () {
      const perfil = UsuarioPerfil(rol: Roles.operador);
      expect(perfil.esAdmin, isFalse);
      expect(perfil.etiquetaRol, 'Operador');
    });

    test('normaliza el rol al construir desde un mapa', () {
      final admin = UsuarioPerfil.fromMap(<String, dynamic>{'rol': 'admin'});
      expect(admin.rol, Roles.administrador);
      expect(admin.esAdmin, isTrue);

      final operador = UsuarioPerfil.fromMap(<String, dynamic>{'rol': 'usuario'});
      expect(operador.rol, Roles.operador);
      expect(operador.esAdmin, isFalse);
    });

    test('un mapa sin rol resuelve al de menor privilegio', () {
      final perfil = UsuarioPerfil.fromMap(<String, dynamic>{'email': 'a@b.c'});
      expect(perfil.rol, Roles.porDefecto);
      expect(perfil.esAdmin, isFalse);
    });
  });
}
