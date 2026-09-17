# -*- coding: utf-8 -*-
"""Comprueba contra el servicio real que las reglas cierran el acceso directo.

Se consulta la API REST de Cloud Firestore **sin credenciales**, es decir como lo
haría un cliente anónimo, y se espera que la respuesta sea 403 (permiso denegado).
Es la comprobación de que nadie lee la base de datos sin pasar por el servicio,
que es la regla de diseño del sistema.

Se prueba también con una credencial de servicio: debe funcionar, porque el
backend no está sujeto a las reglas de seguridad (las reglas rigen únicamente a
los clientes).
"""

import json
import urllib.error
import urllib.request
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2 import service_account

PROYECTO = "sigvach26-bd"
BASE = "https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents" % PROYECTO
CLAVE = Path(r"C:\Users\FREDDY\credenciales-sigvach\serviceAccountKey.json")

COLECCIONES = ["lecturas", "alertas", "modulos_cultivo", "perfiles_cultivo", "usuarios"]


def consultar(ruta: str, token: str | None = None) -> tuple[int, str]:
    cabeceras = {"Authorization": "Bearer %s" % token} if token else {}
    peticion = urllib.request.Request(ruta, headers=cabeceras)
    try:
        with urllib.request.urlopen(peticion, timeout=45) as respuesta:
            return respuesta.status, respuesta.read(200).decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read(200).decode("utf-8", "replace")
    except Exception as error:  # noqa: BLE001
        return 0, "%s: %s" % (type(error).__name__, error)


print("=== 1) ACCESO ANONIMO (como un cliente sin sesion) ===")
print("    Se espera 403 en todas las colecciones: las reglas deniegan por defecto.")
print("")
anonimos_ok = True
for coleccion in COLECCIONES:
    codigo, cuerpo = consultar("%s/%s?pageSize=1" % (BASE, coleccion))
    denegado = codigo == 403
    anonimos_ok = anonimos_ok and denegado
    print("  %-18s -> HTTP %-4s %s" % (
        coleccion, codigo, "DENEGADO ✓" if denegado else "REVISAR: %s" % cuerpo[:90]
    ))

print("")
print("=== 2) ACCESO CON LA CUENTA DE SERVICIO (el backend) ===")
print("    Se espera 200: el backend no esta sujeto a las reglas de seguridad.")
print("")
credencial = service_account.Credentials.from_service_account_file(
    str(CLAVE), scopes=["https://www.googleapis.com/auth/datastore"]
)
credencial.refresh(Request())
servicio_ok = True
for coleccion in COLECCIONES:
    codigo, cuerpo = consultar("%s/%s?pageSize=1" % (BASE, coleccion), credencial.token)
    permitido = codigo == 200
    servicio_ok = servicio_ok and permitido
    print("  %-18s -> HTTP %-4s %s" % (
        coleccion, codigo, "PERMITIDO ✓" if permitido else "REVISAR: %s" % cuerpo[:90]
    ))

print("")
print("=== CONCLUSION ===")
print("  Un cliente anonimo no puede leer ninguna coleccion: %s" % ("SI ✓" if anonimos_ok else "NO"))
print("  El backend si accede a todas las colecciones:       %s" % ("SI ✓" if servicio_ok else "NO"))
if anonimos_ok and servicio_ok:
    print("")
    print("  Las reglas aislaron la base de datos: los clientes solo pueden")
    print("  usar la API del servicio, que es quien valida y autoriza.")
