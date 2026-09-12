---
name: leer
description: 'Ejecutar la app Flutter del proyecto (SIGVACH, Firebase). Usar
  para: correr la app, probar cambios, verificar la sesión de aula. No requiere
  archivo de configuración: Firebase va incrustado en lib/firebase_options.dart.
  Respeta la regla: flutter pub get SÍ, flutter pub upgrade NO.'
user-invocable: true
---

# Ejecutar la app (proyecto SIGVACH)

## Cuándo usar
- El usuario pide correr/ejecutar/probar la app
- Verificar que un cambio compila y abre en la pantalla esperada
- Preparar la app para probar el login/registro con Firebase Authentication

## Reglas del aula (importantes)
1. `flutter pub get` → permitido.
2. `flutter pub upgrade` → PROHIBIDO (podría romper dependencias).
3. No tocar `lib/firebase_options.dart` ni `android/app/google-services.json`
   (contienen las claves de Firebase y están fuera de Git).

## Procedimiento
1. No hace falta crear `config/local.json`: la configuración de Firebase va
   incrustada en `lib/firebase_options.dart`.
2. Ejecutar la app en el dispositivo deseado:
   ```
   flutter run
   ```
3. Confirmar que aparece la pantalla de login/registro.
4. Si hay error de compilación, revisar `lib/` y `pubspec.yaml` sin actualizar dependencias.
