import java.util.Properties
import java.io.FileInputStream

// Firma de release. Las credenciales NO están en el repositorio (es público):
// viven en android/key.properties, que el .gitignore excluye, junto con el
// keystore .jks al que apunta. Si el archivo no existe, la configuración de
// firma queda vacía y la compilación de release falla de forma explícita.
val keystoreProperties = Properties()
val keystorePropertiesFile = rootProject.file("key.properties")
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(FileInputStream(keystorePropertiesFile))
}

plugins {
    id("com.android.application")
    // START: FlutterFire Configuration
    id("com.google.gms.google-services")
    // END: FlutterFire Configuration
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "bo.edu.uajms.sigvach"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    defaultConfig {
        applicationId = "bo.edu.uajms.sigvach"
        // La versión mínima se declara de forma explícita, y no con el valor
        // predeterminado del SDK de Flutter, porque el requisito no funcional
        // RNF-04 exige Android 8.0 (API 26) o superior y esa condición debe
        // quedar verificable en el propio archivo de construcción.
        minSdk = 26
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    signingConfigs {
        create("release") {
            keyAlias = keystoreProperties["keyAlias"] as String
            keyPassword = keystoreProperties["keyPassword"] as String
            storeFile = file(keystoreProperties["storeFile"] as String)
            storePassword = keystoreProperties["storePassword"] as String
        }
    }

    buildTypes {
        release {
            // Firma con el keystore propio del proyecto (android/key.properties),
            // no con las claves de depuración.
            signingConfig = signingConfigs.getByName("release")
        }
    }
}

// Crea una copia del APK de release con el nombre deseado: sigvach_1.0.0+1.apk
// (se ejecuta después de que el plugin de Flutter copie app-release.apk a flutter-apk/)
afterEvaluate {
    tasks.named("assembleRelease") {
        doLast {
            // En este proyecto layout.buildDirectory ya apunta a build/app
            val src = layout.buildDirectory
                .file("outputs/flutter-apk/app-release.apk").get().asFile
            val dst = layout.buildDirectory
                .file("outputs/flutter-apk/sigvach_1.0.0+1.apk").get().asFile
            if (src.exists()) {
                if (dst.exists()) dst.delete()
                src.copyTo(dst)
                println("APK generado: ${dst.absolutePath}")
            } else {
                println("No se encontró ${src.absolutePath}")
            }
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter {
    source = "../.."
}
