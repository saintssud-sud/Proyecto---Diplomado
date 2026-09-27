# -*- coding: utf-8 -*-
"""Comprueba que lo publicado este sirviendo de verdad al sistema.

Existe por un fallo real. En la entrega del E2, la aplicacion publicada en
Firebase apuntaba a `http://127.0.0.1:8011`, porque se subio la carpeta
`build/web` de una compilacion hecha para probar en local.

La direccion del servicio no se elige al ejecutar la aplicacion, sino **al
compilarla** (`--dart-define=API_BASE_URL=...`). Por eso, compilar para local y
publicar esa misma carpeta deja a la aplicacion pidiendole los datos al equipo
de quien la mira: funciona en el equipo del autor —donde esa direccion existe— y
falla en todos los demas. El navegador no tiene culpa: hace lo que le dice la
pagina.

De ahi las cuatro comprobaciones de este script:

  1. El paquete publicado lleva la direccion publica del servicio.
  2. El paquete publicado es el mismo que hay en `build/web` (o se avisa de que
     no lo es).
  3. El servicio responde en su ruta de salud.
  4. El origen de la aplicacion esta autorizado, incluido el examen previo que
     hace el navegador antes de las peticiones con token.

Nota sobre el punto 1: la direccion local `127.0.0.1:8011` **siempre** aparece
una vez en el paquete, porque es el valor de reserva que el codigo usa cuando no
se define ninguna direccion. Lo que delata una compilacion mal publicada no es su
presencia, sino la **ausencia** de la direccion publica.

Uso:
    python scripts/verificar_despliegue.py
    python scripts/verificar_despliegue.py --aplicacion https://otra.web.app
"""

import hashlib
import sys
import urllib.error
import urllib.request
from pathlib import Path

APLICACION = "https://sigvach26-bd.web.app"
SERVICIO = "https://sigvach-api.onrender.com"
DIRECCION_PUBLICA = "sigvach-api.onrender.com"
DIRECCION_LOCAL = "127.0.0.1:8011"
PAQUETE = "main.dart.js"

COMPILACION_LOCAL = (
    Path(__file__).resolve().parent.parent / "build" / "web" / PAQUETE
)


def descargar(url: str, cabeceras: dict | None = None,
              metodo: str = "GET", tiempo: int = 120) -> tuple[int, bytes, dict]:
    """Devuelve codigo, cuerpo y cabeceras de la respuesta."""
    peticion = urllib.request.Request(url, headers=cabeceras or {}, method=metodo)
    try:
        with urllib.request.urlopen(peticion, timeout=tiempo) as respuesta:
            return respuesta.status, respuesta.read(), dict(respuesta.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read(), dict(error.headers)
    except Exception as error:  # noqa: BLE001
        return 0, ("%s: %s" % (type(error).__name__, error)).encode("utf-8"), {}


def main() -> int:
    aplicacion = APLICACION
    if "--aplicacion" in sys.argv:
        aplicacion = sys.argv[sys.argv.index("--aplicacion") + 1]
    origen = aplicacion

    fallos = []
    print("=== COMPROBACION DEL DESPLIEGUE ===")
    print("  aplicacion: %s" % aplicacion)
    print("  servicio  : %s" % SERVICIO)
    print("")

    # --- 1) el paquete publicado lleva la direccion publica ------------------
    print("=== 1) DIRECCION QUE LLEVA LA APLICACION PUBLICADA ===")
    codigo, cuerpo, _ = descargar("%s/%s" % (aplicacion, PAQUETE), tiempo=300)
    if codigo != 200:
        fallos.append("no se pudo descargar el paquete publicado (HTTP %s)" % codigo)
        print("  REVISAR: no se pudo descargar %s/%s (HTTP %s)" % (aplicacion, PAQUETE, codigo))
    else:
        texto = cuerpo.decode("utf-8", "replace")
        hay_publica = DIRECCION_PUBLICA in texto
        hay_local = DIRECCION_LOCAL in texto
        print("  tamano del paquete      : %d bytes" % len(cuerpo))
        print("  huella SHA-256          : %s" % hashlib.sha256(cuerpo).hexdigest()[:32])
        print("  lleva la API publica    : %s" % ("SI" if hay_publica else "NO"))
        print("  lleva la reserva local  : %s (normal, es el valor de reserva)" % ("si" if hay_local else "no"))
        if hay_publica:
            print("  -> CORRECTO: la aplicacion publicada pide los datos al servicio publicado.")
        else:
            fallos.append("el paquete publicado NO lleva la direccion publica del servicio")
            print("  -> FALLA: esta publicado un paquete compilado sin la direccion publica.")
            print("     El navegador intentaria llamar a %s, que es el equipo de quien mira." % DIRECCION_LOCAL)
            print("     Hay que recompilar con:")
            print("       flutter build web --release --dart-define=API_BASE_URL=%s" % SERVICIO)
            print("     y volver a publicar con: firebase deploy --only hosting")

        # --- 2) coincide con la compilacion local? --------------------------
        print("")
        print("=== 2) COMPARACION CON LA COMPILACION LOCAL ===")
        if COMPILACION_LOCAL.exists():
            datos = COMPILACION_LOCAL.read_bytes()
            huella_local = hashlib.sha256(datos).hexdigest()
            iguales = huella_local == hashlib.sha256(cuerpo).hexdigest()
            print("  build/web/%s: %d bytes" % (PAQUETE, len(datos)))
            print("  coincide con lo publicado: %s" % ("SI" if iguales else "NO"))
            if not iguales:
                print("  -> Aviso: lo publicado no es lo que hay en build/web.")
                print("     Puede ser normal (se publico antes y luego se recompilo), pero conviene")
                print("     saberlo antes de dar por bueno un despliegue.")
        else:
            print("  No hay build/web/%s: solo se comparo lo publicado." % PAQUETE)

    # --- 3) el servicio responde --------------------------------------------
    print("")
    print("=== 3) EL SERVICIO RESPONDE EN SU RUTA DE SALUD ===")
    codigo, cuerpo, _ = descargar("%s/api/v1/salud" % SERVICIO, tiempo=180)
    respuesta = cuerpo.decode("utf-8", "replace")
    if codigo == 200 and '"estado":"ok"' in respuesta.replace(" ", ""):
        print("  HTTP %s  %s" % (codigo, respuesta[:110]))
        print("  -> CORRECTO. Si tardo, es el arranque en frio: la capa gratuita se duerme.")
    else:
        fallos.append("el servicio no respondio correctamente en /api/v1/salud (HTTP %s)" % codigo)
        print("  REVISAR: HTTP %s  %s" % (codigo, respuesta[:160]))

    # --- 4) el origen de la aplicacion esta autorizado ----------------------
    print("")
    print("=== 4) ORIGEN AUTORIZADO (CORS) ===")
    codigo, _, cabeceras = descargar(
        "%s/api/v1/salud" % SERVICIO,
        cabeceras={"Origin": origen, "Accept": "application/json"},
        tiempo=180,
    )
    permitido = cabeceras.get("access-control-allow-origin", "")
    print("  peticion simple  : HTTP %s   access-control-allow-origin: %s" % (
        codigo, permitido or "(no viene)"))
    if permitido in (origen, "*"):
        print("  -> CORRECTO: el navegador permite leer la respuesta desde la aplicacion.")
    else:
        fallos.append("el servicio no autoriza el origen %s" % origen)
        print("  -> FALLA: revisar ORIGENES_PERMITIDOS (ALLOWED_ORIGINS) en el servicio.")

    # El examen previo es el que hace el navegador antes de las peticiones con
    # token: si falla, la aplicacion no puede ni iniciar sesion.
    codigo, _, cabeceras = descargar(
        "%s/api/v1/alertas/comprobacion" % SERVICIO,
        cabeceras={
            "Origin": origen,
            "Access-Control-Request-Method": "PATCH",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
        metodo="OPTIONS",
        tiempo=180,
    )
    metodos = cabeceras.get("access-control-allow-methods", "")
    cabeceras_permitidas = cabeceras.get("access-control-allow-headers", "")
    print("  examen previo    : HTTP %s   metodos: %s" % (codigo, metodos or "(no vienen)"))
    if "PATCH" in metodos and "authorization" in cabeceras_permitidas.lower():
        print("  -> CORRECTO: el navegador podra hacer las peticiones con token.")
    else:
        fallos.append("el examen previo no autoriza PATCH con la cabecera Authorization")
        print("  -> FALLA: revisar allow_methods y allow_headers del servicio.")

    # --- conclusion ----------------------------------------------------------
    print("")
    print("=== CONCLUSION ===")
    if not fallos:
        print("  El despliegue esta correcto: la aplicacion publicada apunta al servicio")
        print("  publicado, el servicio responde y autoriza a la aplicacion.")
        print("")
        print("  Recuerda: si publicas algo nuevo, vuelve a ejecutar esta comprobacion.")
        return 0

    print("  Hay %d problema(s):" % len(fallos))
    for fallo in fallos:
        print("    - %s" % fallo)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
