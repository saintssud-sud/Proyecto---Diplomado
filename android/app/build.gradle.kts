plugins {
    id("com.android.application")
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
        // TODO: Specify your own unique Application ID (https://developer.android.com/studio/build/application-id.html).
        applicationId = "bo.edu.uajms.sigvach"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        minSdk = flutter.minSdkVersion
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    buildTypes {
        release {
            // TODO: Add your own signing config for the release build.
            // Signing with the debug keys for now, so `flutter run --release` works.
            signingConfig = signingConfigs.getByName("debug")
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
