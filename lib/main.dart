import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:provider/single_child_widget.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'app.dart';
import 'config/app_config.dart';
import 'controllers/alertas_controller.dart';
import 'controllers/context_controller.dart';
import 'controllers/cultivos_controller.dart';
import 'controllers/historial_controller.dart';
import 'controllers/modulos_controller.dart';
import 'controllers/panel_controller.dart';
import 'controllers/perfil_controller.dart';
import 'controllers/preferences_controller.dart';
import 'controllers/rangos_controller.dart';
import 'controllers/usuario_controller.dart';
import 'repositories/api/alertas_api_repository.dart';
import 'repositories/api/lecturas_api_repository.dart';
import 'repositories/api/modulos_api_repository.dart';
import 'repositories/api/perfiles_api_repository.dart';
import 'repositories/api/rangos_api_repository.dart';
import 'repositories/api/usuarios_api_repository.dart';
import 'repositories/usuario_repository.dart';
import 'services/api_cliente.dart';
import 'services/auth_service.dart';
import 'services/firestore_service.dart';
import 'services/location_service.dart';
import 'services/preferences_service.dart';
import 'services/weather_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Firebase/Firestore: la configuración va incrustada en
  // lib/firebase_options.dart. Si algo falla, la app arranca igualmente
  // en modo "no configurado" sin lanzar una excepción que la detenga.
  final firestoreService = FirestoreService();
  var firebaseReady = false;
  try {
    await firestoreService.initialize();
    firebaseReady = true;
  } catch (e) {
    debugPrint('Firebase no disponible: $e');
  }

  final config = AppConfig(firebaseReady: firebaseReady);
  final prefs = await SharedPreferences.getInstance();

  final preferencesController = PreferencesController(
    PreferencesService(prefs),
  );

  final providers = <SingleChildWidget>[
    Provider<AppConfig>.value(value: config),
    ChangeNotifierProvider<PreferencesController>.value(
      value: preferencesController,
    ),
  ];

  if (firebaseReady) {
    providers.add(Provider<FirestoreService>.value(value: firestoreService));
    providers.add(
      Provider<AuthService>(create: (providerContext) => AuthService()),
    );
    providers.add(
      Provider<UsuarioRepository>(
        create: (providerContext) => UsuarioRepository(),
      ),
    );
    providers.add(
      ChangeNotifierProvider<UsuarioController>(
        create: (providerContext) {
          final controller = UsuarioController(
            repository: providerContext.read<UsuarioRepository>(),
          );
          controller.iniciar();
          return controller;
        },
      ),
    );
  }

  // Acceso al servicio de la API. Se registra siempre: si el proveedor de
  // identidad no estuviera disponible, el cliente lo informa como un fallo de
  // conexión y la pantalla lo presenta con su acción de reintento.
  providers.add(Provider<ApiCliente>(create: (providerContext) => ApiCliente()));
  providers.add(
    ChangeNotifierProvider<PanelController>(
      create: (providerContext) {
        final ApiCliente cliente = providerContext.read<ApiCliente>();
        return PanelController(
          modulos: ModulosApiRepository(cliente),
          lecturas: LecturasApiRepository(cliente),
          rangos: RangosApiRepository(cliente),
          alertas: AlertasApiRepository(cliente),
        );
      },
    ),
  );
  providers.add(
    ChangeNotifierProvider<HistorialController>(
      create: (providerContext) => HistorialController(
        lecturas: LecturasApiRepository(providerContext.read<ApiCliente>()),
      ),
    ),
  );
  providers.add(
    ChangeNotifierProvider<AlertasController>(
      create: (providerContext) => AlertasController(
        alertas: AlertasApiRepository(providerContext.read<ApiCliente>()),
      ),
    ),
  );
  providers.add(
    ChangeNotifierProvider<RangosController>(
      create: (providerContext) {
        final ApiCliente cliente = providerContext.read<ApiCliente>();
        return RangosController(
          rangos: RangosApiRepository(cliente),
          perfiles: PerfilesApiRepository(cliente),
        );
      },
    ),
  );
  providers.add(
    ChangeNotifierProvider<ModulosController>(
      create: (providerContext) {
        final ApiCliente cliente = providerContext.read<ApiCliente>();
        return ModulosController(
          modulos: ModulosApiRepository(cliente),
          perfiles: PerfilesApiRepository(cliente),
        );
      },
    ),
  );
  providers.add(
    ChangeNotifierProvider<PerfilController>(
      create: (providerContext) => PerfilController(
        usuarios: UsuariosApiRepository(providerContext.read<ApiCliente>()),
      ),
    ),
  );
  providers.add(
    ChangeNotifierProvider<CultivosController>(
      create: (providerContext) {
        final ApiCliente cliente = providerContext.read<ApiCliente>();
        return CultivosController(
          perfiles: PerfilesApiRepository(cliente),
          rangos: RangosApiRepository(cliente),
        );
      },
    ),
  );

  providers.add(
    Provider<LocationService>(
      create: (providerContext) => const LocationService(),
    ),
  );
  providers.add(
    Provider<WeatherService>(
      create: (providerContext) => const WeatherService(),
    ),
  );
  providers.add(
    ChangeNotifierProvider<ContextController>(
      create: (providerContext) {
        return ContextController(
          locationService: providerContext.read<LocationService>(),
          weatherService: providerContext.read<WeatherService>(),
        );
      },
    ),
  );

  runApp(MultiProvider(providers: providers, child: const ProyectoFinalApp()));
}
