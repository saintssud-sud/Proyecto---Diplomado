# -*- coding: utf-8 -*-
"""Prueba de restauración del respaldo, sin tocar los datos reales.

Para qué sirve
--------------
La cátedra pide «respaldo de la base: copia periódica y una **restauración
probada al menos una vez**». Un respaldo que nunca se restauró no es un respaldo:
es un archivo del que se supone que sirve. Este script hace la prueba de verdad,
contra el servicio publicado, y deja la evidencia por escrito.

Cómo lo hace sin ensuciar los datos del cultivo
-----------------------------------------------
Restaurar sobre el módulo real es impensable: duplicaría lecturas del cultivo en
producción. El script, entonces, **se crea su propio espacio** y lo deshace al
terminar:

1. crea un módulo de prueba llamado ``PRUEBA DE RESTAURACION``, asociado al
   **mismo perfil de cultivo** que el módulo de la maqueta, de modo que las
   lecturas que inserte se evalúen contra los rangos de referencia reales;
2. inserta en él tres lecturas tomadas del respaldo, una por variable, con la
   observación ``restauracion de prueba <fecha>`` para poder reconocerlas;
3. comprueba que quedaron guardadas y que el servidor las evaluó: el campo
   ``estado_rango`` de la respuesta trae el resultado de esa evaluación;
4. borra todo lo que creó —las alertas que hayan podido generarse, las lecturas y
   el módulo— y comprueba que la base quedó como estaba.

Nunca se toca un dato preexistente: el script no borra ni modifica ninguna
lectura, módulo, rango o alerta que no haya creado él mismo en esta ejecución. Si
al empezar ya existe un módulo con ese nombre, se detiene y lo dice, en lugar de
borrar algo que no es suyo.

Si algo falla a mitad de camino, la limpieza se ejecuta igual y la evidencia
registra el fallo tal como ocurrió.

Uso
---
    python scripts/restaurar_prueba_base.py
    python scripts/restaurar_prueba_base.py --respaldo respaldos/respaldo-sigvach-2026-10-05_131500.json
    python scripts/restaurar_prueba_base.py --lecturas 4

La evidencia se escribe en ``evidencia/restauracion-<fecha>.txt``.

Credenciales: hacen falta las de una cuenta **administradora**
-------------------------------------------------------------
Esta prueba escribe, y por lo tanto necesita una cuenta con rol de
administración: la del operador responde 403 al crear o borrar un módulo. Las
credenciales se leen, como las del respaldo, de un archivo que vive **fuera** del
repositorio, y se buscan en este orden:

1. la ruta indicada en la variable de entorno ``CREDENCIALES_ADMINISTRADOR``;
2. ``%USERPROFILE%\\credenciales-sigvach\\administrador.txt``;
3. ``%USERPROFILE%\\credenciales-sigvach\\operador.txt``.

El script comprueba el rol **antes** de escribir nada y, si la cuenta no es
administradora, se detiene y lo dice: es preferible no empezar que dejar un módulo
de prueba a medio borrar.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# El script se apoya en la sesión y en la lectura de credenciales que ya resuelve
# `respaldar_base.py`, que vive en esta misma carpeta: una sola implementación del
# acceso al servicio, para que los dos scripts se comporten igual.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from respaldar_base import (  # noqa: E402 - la ruta se ajusta en la línea anterior
    ARCHIVO_CREDENCIALES,
    BOLIVIA,
    CARPETA_RESPALDOS,
    MODULO_MAQUETA,
    SERVICIO,
    Respuesta,
    Sesion,
    leer_credenciales,
)

NOMBRE_DEL_MODULO_DE_PRUEBA = "PRUEBA DE RESTAURACION"
UBICACION_DEL_MODULO_DE_PRUEBA = "Modulo temporal de la prueba de restauracion"

# Credenciales: la prueba crea y borra un módulo, así que necesita una cuenta con
# rol de administración. Se busca, en este orden, un archivo **fuera del
# repositorio** —igual que el respaldo— y se admite el del operador como último
# recurso, para que el script avise con un mensaje claro en vez de fallar por una
# ruta que no existe:
#   1. la ruta de la variable de entorno CREDENCIALES_ADMINISTRADOR;
#   2. %USERPROFILE%\credenciales-sigvach\administrador.txt;
#   3. el archivo del operador (%USERPROFILE%\credenciales-sigvach\operador.txt).
CARPETA_CREDENCIALES = Path(
    Path(os.environ.get("USERPROFILE", str(Path.home()))) / "credenciales-sigvach"
)
ARCHIVO_CREDENCIALES_ADMINISTRADOR = Path(
    os.environ.get("CREDENCIALES_ADMINISTRADOR")
    or CARPETA_CREDENCIALES / "administrador.txt"
)
# Orden con el que se eligen las lecturas del respaldo. Es indiferente para la
# prueba, salvo por un detalle que sí importa: conviene que la muestra caiga a los
# dos lados del rango —una variable dentro y otra fuera—, porque eso es lo que
# demuestra que el servidor **evalúa** en lugar de devolver siempre lo mismo. Al
# ejecutar el script sobre los datos reales, el detalle queda escrito en la
# evidencia y suele generar una alerta, que también se borra al final.
VARIABLES_PREFERIDAS = ("ph", "humedad", "temp_solucion", "ec", "tds", "temp_ambiental")
RUTA_EVIDENCIA = Path(__file__).resolve().parent.parent / "evidencia"
MAXIMO_CARACTERES_RESPUESTA = 600


class Diario:
    """Acumula las líneas de la evidencia, que se escribe al final.

    Se acumula en memoria y se vuelca una sola vez, en un bloque ``finally``: así
    la evidencia existe aunque la prueba se interrumpa a mitad de camino, que es
    justamente cuando más falta hace leerla.
    """

    def __init__(self) -> None:
        self.lineas: list[str] = []

    def linea(self, texto: str = "") -> None:
        self.lineas.append(texto)

    def titulo(self, texto: str) -> None:
        self.linea("=" * 78)
        self.linea(texto)
        self.linea("=" * 78)

    def seccion(self, texto: str) -> None:
        self.linea("")
        self.linea("-" * 78)
        self.linea(texto)
        self.linea("-" * 78)

    def dato(self, etiqueta: str, valor: object) -> None:
        self.linea("  %-22s: %s" % (etiqueta, valor))

    def paso(self, numero: str, metodo: str, ruta: str, respuesta: Respuesta,
             peticion: dict | None = None, nota: str = "") -> None:
        """Registra una llamada al servicio con su código y un fragmento."""
        self.linea("  [%s] %s %s  ->  HTTP %s" % (numero, metodo, ruta, respuesta.codigo))
        if peticion is not None:
            self.linea("      peticion : %s" % _compacto(peticion))
        self.linea("      respuesta: %s" % respuesta.fragmento(MAXIMO_CARACTERES_RESPUESTA))
        if nota:
            self.linea("      nota     : %s" % nota)

    def texto(self) -> str:
        return "\n".join(self.lineas) + "\n"


def _compacto(dato: object) -> str:
    """Presenta un diccionario en una sola línea, para la evidencia."""
    return " ".join(json.dumps(dato, ensure_ascii=False, default=str).split())


def _fragmento_de(dato: object, limite: int = MAXIMO_CARACTERES_RESPUESTA) -> str:
    texto = _compacto(dato)
    return texto[:limite] + ("..." if len(texto) > limite else "")


def fecha_de_hoy() -> str:
    """Fecha local (Bolivia) en formato ISO corto."""
    return datetime.now(BOLIVIA).strftime("%Y-%m-%d")


def respaldo_mas_reciente(carpeta: Path) -> Path | None:
    """Devuelve el respaldo más nuevo de la carpeta, o None si no hay ninguno."""
    if not carpeta.is_dir():
        return None
    archivos = sorted(carpeta.glob("respaldo-sigvach-*.json"))
    return archivos[-1] if archivos else None


class PruebaDeRestauracion:
    """Ejecuta la prueba completa y deja constancia de cada paso."""

    def __init__(self, sesion: Sesion, respaldo: dict, archivo: Path, diario: Diario,
                 cantidad: int, marca: str) -> None:
        self.sesion = sesion
        self.respaldo = respaldo
        self.archivo = archivo
        self.diario = diario
        self.cantidad = cantidad
        self.marca = marca
        self.fallos: list[str] = []
        self.creados: dict[str, object] = {"modulo_id": "", "lecturas": [], "alertas": []}
        self.huella_inicial: dict[str, set] = {"lecturas": set(), "alertas": set()}
        self.huella_final: dict[str, set] = {"lecturas": set(), "alertas": set()}

    # --- Utilidades --------------------------------------------------------
    def fallo(self, texto: str) -> None:
        """Anota un fallo: no detiene la limpieza ni la evidencia."""
        self.fallos.append(texto)
        self.diario.linea("      FALLO    : %s" % texto)

    def pedir(self, ruta: str, metodo: str = "GET", cuerpo: dict | None = None) -> Respuesta:
        """Llama al servicio sin reintentar las escrituras (ver `Sesion.pedir`)."""
        return self.sesion.pedir(
            ruta, metodo=metodo, cuerpo=cuerpo, reintentar=(metodo == "GET")
        )

    def listar(self, ruta: str) -> list:
        """Pide una colección y devuelve la lista (vacía si la respuesta no lo es)."""
        respuesta = self.pedir(ruta)
        if respuesta.correcta and isinstance(respuesta.datos, list):
            return respuesta.datos
        return []

    # --- Pasos -------------------------------------------------------------
    def comprobar_administracion(self) -> bool:
        """El módulo de prueba exige rol de administración: se comprueba antes."""
        self.diario.seccion("1. COMPROBACIÓN DE PERMISOS")
        ruta = "/api/v1/usuarios/perfil"
        respuesta = self.pedir(ruta)
        self.diario.paso("1.1", "GET", ruta, respuesta,
                         nota="La prueba crea y borra un módulo: exige administración.")
        perfil = respuesta.datos if isinstance(respuesta.datos, dict) else {}
        rol = str(perfil.get("rol") or "")
        self.diario.dato("Cuenta", perfil.get("email") or "(sin correo)")
        self.diario.dato("Rol", rol or "(sin rol)")
        if respuesta.codigo != 200 or rol != "administrador":
            self.fallo(
                "La cuenta de las credenciales no es administradora (rol '%s', HTTP %s): "
                "no puede crear ni borrar módulos y la prueba no puede ejecutarse."
                % (rol or "desconocido", respuesta.codigo)
            )
            return False
        return True

    def comprobar_que_no_existe_el_modulo_de_prueba(self) -> bool:
        """Evita dos cosas: duplicar el módulo y borrar uno que no es de esta prueba."""
        self.diario.seccion("2. COMPROBACIÓN PREVIA DEL ESTADO DE LA BASE")
        ruta = "/api/v1/modulos"
        respuesta = self.pedir(ruta)
        self.diario.paso("2.1", "GET", ruta, respuesta)
        modulos = respuesta.datos if isinstance(respuesta.datos, list) else []

        existente = next(
            (m for m in modulos if str(m.get("nombre")) == NOMBRE_DEL_MODULO_DE_PRUEBA), None
        )
        self.diario.dato("Módulos en el sistema", len(modulos))
        for modulo in modulos:
            self.diario.linea(
                "      · %-26s %s" % (modulo.get("nombre", "?"), modulo.get("id", "?"))
            )
        if existente:
            self.fallo(
                "Ya existe un módulo llamado '%s' (%s). No se toca: podría ser de una "
                "ejecución anterior o de un usuario. Elimínelo a mano si es suyo y "
                "vuelva a ejecutar la prueba."
                % (NOMBRE_DEL_MODULO_DE_PRUEBA, existente.get("id"))
            )
            return False
        self.diario.linea("      -> No existe un módulo con ese nombre: se puede crear.")

        # Se guarda la huella de la maqueta para poder demostrar al final que no
        # desapareció ninguno de los datos reales.
        self.huella_inicial = self._huella_de_la_maqueta()
        self.diario.linea("")
        self.diario.dato(
            "Huella del módulo real",
            "%d lecturas y %d alertas visibles (identificadores guardados para "
            "comprobar al final que ninguno desaparece)"
            % (len(self.huella_inicial["lecturas"]), len(self.huella_inicial["alertas"])),
        )
        return True

    def _huella_de_la_maqueta(self) -> dict:
        """Identificadores de las lecturas y alertas del módulo de la maqueta.

        No alcanza con contar: la API devuelve como mucho 1000 lecturas y 500
        alertas por consulta, así que un recuento compararía dos números
        recortados. Lo que sí se puede afirmar es qué registros existían antes y
        siguen existiendo después: si ninguno de los identificadores previos
        desapareció, la prueba no borró ni modificó nada del cultivo real. Que
        aparezcan lecturas nuevas es normal —el módulo publica cada cinco
        minutos— y no es consecuencia de esta prueba.
        """
        lecturas = self.listar("/api/v1/lecturas?modulo_id=%s&limite=1000" % MODULO_MAQUETA)
        identificadores_lecturas = {str(l.get("id")) for l in lecturas if l.get("id")}

        identificadores_alertas: set[str] = set()
        for estado in ("activa", "atendida"):
            alertas = self.listar(
                "/api/v1/alertas?estado=%s&modulo_id=%s&limite=500" % (estado, MODULO_MAQUETA)
            )
            identificadores_alertas.update(
                str(a.get("id")) for a in alertas if a.get("id")
            )

        return {
            "lecturas": identificadores_lecturas,
            "alertas": identificadores_alertas,
        }

    def preparar_lecturas(self) -> bool:
        """Elige del respaldo una lectura por variable, con rango configurado."""
        self.diario.seccion("3. QUÉ SE EXPORTÓ Y QUÉ SE VA A RESTAURAR")

        conteo = self.respaldo.get("conteo", {})
        self.diario.dato("Archivo de respaldo", self.archivo)
        self.diario.dato("Generado en", self.respaldo.get("generado_en", "?"))
        self.diario.dato("Origen", self.respaldo.get("origen", "?"))
        self.diario.linea("  Contenido del respaldo:")
        for clave in ("perfiles", "modulos", "rangos", "lecturas", "alertas"):
            self.diario.linea("      · %-12s %5s" % (clave, conteo.get(clave, 0)))
        for aviso in self.respaldo.get("avisos", []):
            self.diario.linea("      aviso: %s" % aviso)

        # El perfil del módulo de la maqueta: es el que da los rangos de referencia.
        ruta = "/api/v1/modulos/%s" % MODULO_MAQUETA
        respuesta = self.pedir(ruta)
        self.diario.paso("3.1", "GET", ruta, respuesta)
        if respuesta.codigo != 200 or not isinstance(respuesta.datos, dict):
            self.fallo("No se pudo leer el módulo de la maqueta (HTTP %s)." % respuesta.codigo)
            return False
        self.perfil_id = str(respuesta.datos.get("perfil_id") or "")
        self.tipo_cultivo = str(respuesta.datos.get("tipo_cultivo") or "Lechuga")
        self.diario.dato("Módulo de la maqueta", "%s (%s)" % (
            respuesta.datos.get("nombre", "?"), MODULO_MAQUETA))
        self.diario.dato("Perfil de cultivo", self.perfil_id)

        ruta_rangos = "/api/v1/rangos?perfil_id=%s" % self.perfil_id
        respuesta_rangos = self.pedir(ruta_rangos)
        self.diario.paso("3.2", "GET", ruta_rangos, respuesta_rangos,
                         nota="Los rangos son la referencia con la que se evalúan las lecturas.")
        rangos = respuesta_rangos.datos if isinstance(respuesta_rangos.datos, list) else []
        if not rangos:
            self.fallo(
                "El perfil '%s' no tiene rangos de referencia: las lecturas no podrían "
                "evaluarse y la prueba no demostraría nada." % self.perfil_id
            )
            return False
        self.rangos = {str(r.get("variable")): r for r in rangos}

        # Una lectura por variable, la más reciente de cada una. Se prefieren las
        # variables que tienen rango, para que el servidor pueda evaluarlas.
        lecturas = self.respaldo.get("lecturas") or []
        elegidas: dict[str, dict] = {}
        for variable in VARIABLES_PREFERIDAS:
            if variable not in self.rangos:
                continue
            candidatas = [l for l in lecturas if str(l.get("variable")) == variable]
            if candidatas:
                elegidas[variable] = candidatas[0]
            if len(elegidas) >= self.cantidad:
                break

        if len(elegidas) < self.cantidad:
            for lectura in lecturas:
                variable = str(lectura.get("variable"))
                if variable in self.rangos and variable not in elegidas:
                    elegidas[variable] = lectura
                if len(elegidas) >= self.cantidad:
                    break

        if len(elegidas) < self.cantidad:
            self.fallo(
                "El respaldo solo tiene %d lectura(s) de variables con rango configurado y "
                "la prueba necesita %d. Vuelva a ejecutar el respaldo."
                % (len(elegidas), self.cantidad)
            )
            return False

        self.elegidas = list(elegidas.values())
        self.diario.linea("")
        self.diario.linea("  Lecturas elegidas del respaldo (la más reciente de cada variable):")
        for lectura in self.elegidas:
            rango = self.rangos[str(lectura.get("variable"))]
            self.diario.linea(
                "      · %-16s valor=%-8s rango=[%s, %s]  original=%s"
                % (
                    lectura.get("variable"),
                    lectura.get("valor"),
                    rango.get("minimo"),
                    rango.get("maximo"),
                    lectura.get("timestamp"),
                )
            )
        return True

    def crear_modulo_de_prueba(self) -> bool:
        """Crea el módulo de prueba. Si la respuesta se pierde, lo busca."""
        self.diario.seccion("4. RESTAURACIÓN: MÓDULO DE PRUEBA")
        cuerpo = {
            "nombre": NOMBRE_DEL_MODULO_DE_PRUEBA,
            "tipo_cultivo": self.tipo_cultivo,
            "perfil_id": self.perfil_id,
            "ubicacion": UBICACION_DEL_MODULO_DE_PRUEBA,
            "activo": True,
        }
        ruta = "/api/v1/modulos"
        respuesta = self.pedir(ruta, metodo="POST", cuerpo=cuerpo)
        self.diario.paso("4.1", "POST", ruta, respuesta, peticion=cuerpo)

        if respuesta.codigo == 201 and isinstance(respuesta.datos, dict):
            self.creados["modulo_id"] = str(respuesta.datos.get("id") or "")
            self.diario.dato("Módulo de prueba creado", self.creados["modulo_id"])
            return True

        # La respuesta se perdió o el servicio falló: puede que el módulo exista.
        # Se busca antes de darse por vencido, para no dejarlo sin borrar.
        self.fallo(
            "No se pudo crear el módulo de prueba (HTTP %s). Se comprueba si quedó creado."
            % respuesta.codigo
        )
        for modulo in self.listar("/api/v1/modulos"):
            if str(modulo.get("nombre")) == NOMBRE_DEL_MODULO_DE_PRUEBA:
                self.creados["modulo_id"] = str(modulo.get("id") or "")
                self.diario.linea(
                    "      -> El módulo sí quedó creado (%s); se adopta para borrarlo al final."
                    % self.creados["modulo_id"]
                )
                return False
        self.diario.linea("      -> El módulo no quedó creado. Nada que borrar.")
        return False

    def restaurar_lecturas(self) -> bool:
        """Inserta las lecturas del respaldo en el módulo de prueba."""
        self.diario.seccion("5. RESTAURACIÓN: LECTURAS")
        if not self.creados["modulo_id"]:
            self.fallo("No hay módulo de prueba: no se pueden restaurar lecturas.")
            return False

        todas_bien = True
        for indice, lectura in enumerate(self.elegidas, start=1):
            variable = str(lectura.get("variable"))
            cuerpo = {
                "modulo_id": self.creados["modulo_id"],
                "variable": variable,
                "valor": lectura.get("valor"),
                "timestamp": lectura.get("timestamp"),
                "observacion": "%s | original: %s" % (self.marca, lectura.get("timestamp")),
            }
            ruta = "/api/v1/lecturas/manual"
            respuesta = self.pedir(ruta, metodo="POST", cuerpo=cuerpo)
            self.diario.paso("5.%d" % indice, "POST", ruta, respuesta, peticion=cuerpo)

            if respuesta.codigo == 422 and "timestamp" in respuesta.texto:
                # La marca de tiempo original fue rechazada (reloj del módulo
                # adelantado). Se reintenta una vez sin ella: la lectura se
                # restaura con la hora del servidor.
                self.diario.linea(
                    "      -> La marca de tiempo original fue rechazada; se reintenta sin ella."
                )
                cuerpo.pop("timestamp")
                cuerpo["observacion"] = "%s | original: %s (no admitida)" % (
                    self.marca,
                    lectura.get("timestamp"),
                )
                respuesta = self.pedir(ruta, metodo="POST", cuerpo=cuerpo)
                self.diario.paso("5.%d.b" % indice, "POST", ruta, respuesta, peticion=cuerpo)

            if respuesta.codigo == 201 and isinstance(respuesta.datos, dict):
                guardada = respuesta.datos
                self.creados["lecturas"].append(str(guardada.get("id") or ""))
                estado = guardada.get("estado_rango")
                self.diario.linea(
                    "      estado_rango = %s   (evaluada por el servidor contra "
                    "[%s, %s])" % (estado, self.rangos[variable].get("minimo"),
                                   self.rangos[variable].get("maximo"))
                )
                if estado in (None, "", "sin_rango"):
                    self.fallo(
                        "La lectura de '%s' quedó sin evaluar contra el rango "
                        "(estado_rango=%r)." % (variable, estado)
                    )
                    todas_bien = False
            elif respuesta.codigo == 0:
                # La respuesta nunca llegó: la lectura puede estar guardada. Se
                # busca por la marca de la observación antes de continuar.
                self.fallo(
                    "No se recibió respuesta al guardar la lectura de '%s': %s"
                    % (variable, respuesta.texto)
                )
                self._adoptar_lecturas_huerfanas()
                todas_bien = False
            else:
                self.fallo(
                    "La lectura de '%s' no se guardó (HTTP %s)."
                    % (variable, respuesta.codigo)
                )
                todas_bien = False
        return todas_bien

    def _adoptar_lecturas_huerfanas(self) -> None:
        """Busca lecturas de esta prueba a las que no se les leyó la respuesta."""
        conocidas = set(self.creados["lecturas"])
        for lectura in self.listar(
            "/api/v1/lecturas?modulo_id=%s&limite=1000" % self.creados["modulo_id"]
        ):
            identificador = str(lectura.get("id") or "")
            if identificador and identificador not in conocidas:
                if str(lectura.get("observacion") or "").startswith(self.marca):
                    self.creados["lecturas"].append(identificador)
                    self.diario.linea(
                        "      -> Se adopta la lectura %s para borrarla al final."
                        % identificador
                    )

    def comprobar_lo_guardado(self) -> bool:
        """Vuelve a leer las lecturas del módulo de prueba: lo guardado, guardado está."""
        self.diario.seccion("6. COMPROBACIÓN DE LO RESTAURADO")
        ruta = "/api/v1/lecturas?modulo_id=%s&limite=1000" % self.creados["modulo_id"]
        respuesta = self.pedir(ruta)
        self.diario.paso("6.1", "GET", ruta, respuesta)
        guardadas = respuesta.datos if isinstance(respuesta.datos, list) else []

        for lectura in guardadas:
            self.diario.linea(
                "      · %-16s valor=%-8s estado_rango=%-9s origen=%-9s observación=%s"
                % (
                    lectura.get("variable"),
                    lectura.get("valor"),
                    lectura.get("estado_rango"),
                    lectura.get("origen"),
                    str(lectura.get("observacion"))[:60],
                )
            )

        correcto = len(guardadas) == len(self.elegidas)
        if not correcto:
            self.fallo(
                "Se esperaban %d lecturas guardadas y el servicio devuelve %d."
                % (len(self.elegidas), len(guardadas))
            )
        if not all(
            str(lectura.get("observacion") or "").startswith(self.marca)
            for lectura in guardadas
        ):
            self.fallo("Alguna lectura guardada no lleva la marca de la prueba.")

        # Las alertas del módulo de prueba son las que generaron estas lecturas:
        # se recogen aquí para poder borrarlas después.
        self.recoger_alertas()
        return correcto

    def recoger_alertas(self) -> None:
        """Recoge las alertas generadas por las lecturas de prueba."""
        self.diario.linea("")
        self.diario.linea("  Alertas generadas por las lecturas de prueba:")
        encontradas: list[str] = []
        for estado in ("activa", "atendida"):
            ruta = "/api/v1/alertas?estado=%s&modulo_id=%s&limite=500" % (
                estado,
                self.creados["modulo_id"],
            )
            respuesta = self.pedir(ruta)
            self.diario.paso("6.2.%s" % estado, "GET", ruta, respuesta)
            for alerta in respuesta.datos if isinstance(respuesta.datos, list) else []:
                encontradas.append(str(alerta.get("id") or ""))
                self.diario.linea(
                    "      · %-16s valor=%-8s desviación=%-6s estado=%s"
                    % (
                        alerta.get("variable"),
                        alerta.get("valor"),
                        alerta.get("desviacion"),
                        alerta.get("estado"),
                    )
                )
        if not encontradas:
            self.diario.linea("      (ninguna: las tres lecturas quedaron dentro del rango)")
        # Cualquier alerta de este módulo la generaron estas lecturas: el módulo se
        # acaba de crear y no existía antes.
        self.creados["alertas"] = encontradas

    def limpiar(self) -> bool:
        """Borra todo lo creado, en el orden que exige el servicio."""
        self.diario.seccion("7. LIMPIEZA: SE BORRA TODO LO CREADO")
        if not self.creados["modulo_id"] and not self.creados["lecturas"]:
            self.diario.linea("  No se creó nada: no hay nada que borrar.")
            return True

        correcto = True
        for indice, alerta_id in enumerate(self.creados["alertas"], start=1):
            ruta = "/api/v1/alertas/%s" % alerta_id
            respuesta = self.pedir(ruta, metodo="DELETE")
            self.diario.paso(
                "7.1.%d" % indice,
                "DELETE",
                ruta,
                respuesta,
                nota="204: borrada. 404: ya no estaba (cuenta como borrada).",
            )

        for indice, lectura_id in enumerate(self.creados["lecturas"], start=1):
            ruta = "/api/v1/lecturas/%s" % lectura_id
            respuesta = self.pedir(ruta, metodo="DELETE")
            self.diario.paso("7.2.%d" % indice, "DELETE", ruta, respuesta)
            if respuesta.codigo not in (204, 404):
                self.fallo("No se pudo borrar la lectura %s (HTTP %s)."
                           % (lectura_id, respuesta.codigo))
                correcto = False

        if self.creados["modulo_id"]:
            ruta = "/api/v1/modulos/%s" % self.creados["modulo_id"]
            # El servicio no deja borrar un módulo con lecturas: si alguna quedó,
            # el 409 lo delata y se vuelve a intentar tras borrarla.
            respuesta = self.pedir(ruta, metodo="DELETE")
            self.diario.paso("7.3", "DELETE", ruta, respuesta)
            if respuesta.codigo == 409:
                self.fallo(
                    "El servicio se niega a borrar el módulo porque todavía tiene "
                    "lecturas. Se reintenta la limpieza."
                )
                self._adoptar_lecturas_huerfanas()
                for lectura_id in self.creados["lecturas"]:
                    self.pedir("/api/v1/lecturas/%s" % lectura_id, metodo="DELETE")
                respuesta = self.pedir(ruta, metodo="DELETE")
                self.diario.paso("7.3.b", "DELETE", ruta, respuesta)
            if respuesta.codigo not in (204, 404):
                self.fallo("No se pudo borrar el módulo de prueba (HTTP %s)."
                           % respuesta.codigo)
                correcto = False
        return correcto

    def comprobar_el_estado_final(self) -> bool:
        """Comprueba que no quedó nada y que los datos reales siguen intactos."""
        self.diario.seccion("8. COMPROBACIÓN FINAL: LA BASE QUEDÓ COMO ESTABA")
        correcto = True
        modulo_de_prueba = str(self.creados["modulo_id"] or "")

        if not modulo_de_prueba:
            # Sin módulo de prueba no hay nada que comprobar sobre él, y consultar
            # por un identificador vacío devolvería las lecturas de TODO el
            # sistema: se comprobaría lo que no corresponde.
            self.diario.linea(
                "  No se llegó a crear el módulo de prueba: no hay nada que comprobar\n"
                "  sobre él. Se comprueba igual que los datos reales sigan intactos."
            )
        else:
            ruta = "/api/v1/modulos/%s" % modulo_de_prueba
            respuesta = self.pedir(ruta)
            self.diario.paso("8.1", "GET", ruta, respuesta, nota="Se espera 404.")
            if respuesta.codigo != 404:
                self.fallo("El módulo de prueba todavía existe (HTTP %s)." % respuesta.codigo)
                correcto = False

            ruta = "/api/v1/lecturas?modulo_id=%s&limite=1000" % modulo_de_prueba
            respuesta = self.pedir(ruta)
            self.diario.paso("8.2", "GET", ruta, respuesta, nota="Se espera una lista vacía.")
            restantes = respuesta.datos if isinstance(respuesta.datos, list) else []
            if restantes:
                self.fallo("Quedaron %d lecturas de prueba sin borrar." % len(restantes))
                correcto = False

        ruta = "/api/v1/modulos"
        respuesta = self.pedir(ruta)
        self.diario.paso("8.3", "GET", ruta, respuesta)
        nombres = [str(m.get("nombre")) for m in respuesta.datos] if isinstance(
            respuesta.datos, list
        ) else []
        if NOMBRE_DEL_MODULO_DE_PRUEBA in nombres:
            self.fallo("El módulo de prueba sigue en la lista de módulos.")
            correcto = False

        self.huella_final = self._huella_de_la_maqueta()
        self.diario.linea("")
        self.diario.dato("Módulo de la maqueta", MODULO_MAQUETA)
        for nombre, etiqueta in (("lecturas", "Lecturas"), ("alertas", "Alertas")):
            antes = self.huella_inicial.get(nombre, set())
            ahora = self.huella_final.get(nombre, set())
            desaparecidos = sorted(antes - ahora)
            self.diario.linea(
                "      · %-10s visibles antes=%-5d después=%-5d  desaparecidos=%d  %s"
                % (
                    etiqueta,
                    len(antes),
                    len(ahora),
                    len(desaparecidos),
                    "sin cambios en lo que existía"
                    if not desaparecidos
                    else "SE PERDIERON DATOS",
                )
            )
            if desaparecidos:
                self.fallo(
                    "Desaparecieron %d %s del módulo de la maqueta (por ejemplo %s)."
                    % (len(desaparecidos), etiqueta.lower(), desaparecidos[0])
                )
                correcto = False
        return correcto

    def concluir(self, resultado: bool) -> None:
        """Cierra la evidencia con la conclusión del procedimiento."""
        self.diario.seccion("9. CONCLUSIÓN")
        if resultado and not self.fallos:
            self.diario.linea(
                "  El procedimiento de restauración SIRVE y quedó probado contra el\n"
                "  servicio publicado: se exportó el dominio a un archivo JSON, se creó un\n"
                "  módulo de prueba asociado al perfil de cultivo real, se restauraron\n"
                "  lecturas del respaldo en él, el servidor las almacenó y las evaluó\n"
                "  contra su rango de referencia (el campo 'estado_rango' de la respuesta\n"
                "  trae esa evaluación), y después se borró todo lo creado, dejando los\n"
                "  datos del cultivo sin cambios."
            )
        else:
            self.diario.linea(
                "  El procedimiento de restauración NO quedó probado por completo.\n"
                "  Fallos registrados durante la ejecución:"
            )
            for fallo in self.fallos:
                self.diario.linea("    - %s" % fallo)
            if self.creados["modulo_id"] or self.creados["lecturas"]:
                self.diario.linea(
                    "  ATENCIÓN: puede haber quedado algo sin borrar. Revise el apartado 8."
                )


def leer_respaldo(archivo: Path) -> dict:
    """Lee el archivo de respaldo y comprueba que sea el que este script espera."""
    if not archivo.exists():
        raise SystemExit(
            "No se encontró el archivo de respaldo: %s\n"
            "Ejecute primero:  python scripts/respaldar_base.py" % archivo
        )
    try:
        datos = json.loads(archivo.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError) as error:
        raise SystemExit("El archivo %s no es un JSON válido: %s" % (archivo, error))
    if not isinstance(datos, dict) or "lecturas" not in datos:
        raise SystemExit(
            "El archivo %s no tiene la forma de un respaldo de SIGVACH "
            "(falta la lista 'lecturas')." % archivo
        )
    return datos


def archivo_de_credenciales_por_defecto() -> Path:
    """Devuelve el primer archivo de credenciales que exista, con la precedencia documentada."""
    if ARCHIVO_CREDENCIALES_ADMINISTRADOR.exists():
        return ARCHIVO_CREDENCIALES_ADMINISTRADOR
    return ARCHIVO_CREDENCIALES


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:  # pragma: no cover - solo en consolas antiguas
        pass

    hoy = fecha_de_hoy()
    analizador = argparse.ArgumentParser(
        description="Prueba de restauración del respaldo, sin tocar los datos reales"
    )
    analizador.add_argument(
        "--respaldo",
        default="",
        help="archivo de respaldo a restaurar (por omisión, el más reciente de respaldos/)",
    )
    analizador.add_argument(
        "--carpeta",
        default=str(CARPETA_RESPALDOS),
        help="carpeta donde buscar el respaldo más reciente",
    )
    analizador.add_argument(
        "--evidencia",
        default=str(RUTA_EVIDENCIA / ("restauracion-%s.txt" % hoy)),
        help="archivo donde se escribe la evidencia",
    )
    analizador.add_argument(
        "--modulo", default=MODULO_MAQUETA, help="módulo de referencia (el de la maqueta)"
    )
    analizador.add_argument(
        "--lecturas", type=int, default=3, help="cuántas lecturas del respaldo se restauran"
    )
    analizador.add_argument(
        "--marca",
        default="restauracion de prueba %s" % hoy,
        help="texto con el que se marca la observación de cada lectura restaurada",
    )
    analizador.add_argument(
        "--credenciales",
        default=str(archivo_de_credenciales_por_defecto()),
        help="archivo local con las credenciales de una cuenta administradora, "
        "fuera del repositorio",
    )
    analizador.add_argument(
        "--servicio", default=SERVICIO, help="dirección del servicio a usar"
    )
    argumentos = analizador.parse_args()

    archivo_respaldo = (
        Path(argumentos.respaldo)
        if argumentos.respaldo
        else respaldo_mas_reciente(Path(argumentos.carpeta))
    )
    if archivo_respaldo is None:
        raise SystemExit(
            "No hay ningún respaldo en %s.\n"
            "Ejecute primero:  python scripts/respaldar_base.py" % argumentos.carpeta
        )

    archivo_evidencia = Path(argumentos.evidencia)
    correo, clave = leer_credenciales(Path(argumentos.credenciales))
    respaldo = leer_respaldo(archivo_respaldo)

    diario = Diario()
    ahora = datetime.now(BOLIVIA)
    diario.titulo("PRUEBA DE RESTAURACIÓN DEL RESPALDO — SIGVACH")
    diario.dato("Fecha de la prueba", ahora.strftime("%Y-%m-%d %H:%M:%S %z (hora de Bolivia)"))
    diario.dato("Servicio", argumentos.servicio)
    diario.dato("Cuenta", correo)
    diario.dato("Archivo de respaldo", archivo_respaldo.resolve())
    diario.dato("Tamaño del respaldo", "%d bytes" % archivo_respaldo.stat().st_size)
    diario.dato("Marca de las lecturas", argumentos.marca)
    diario.dato("Lecturas a restaurar", argumentos.lecturas)
    diario.linea("")
    diario.linea("  El procedimiento crea su propio módulo de prueba, restaura lecturas")
    diario.linea("  del respaldo en él y borra todo lo creado. No modifica ningún dato")
    diario.linea("  preexistente del cultivo.")

    print("=== PRUEBA DE RESTAURACIÓN DEL RESPALDO ===")
    print("  respaldo : %s" % archivo_respaldo.resolve())
    print("  servicio : %s" % argumentos.servicio)
    print("")

    sesion = Sesion(correo, clave, argumentos.servicio)
    prueba: PruebaDeRestauracion | None = None
    resultado = False
    try:
        print("Iniciando sesión...")
        sesion.ingresar()
        print("  sesión iniciada.")
        prueba = PruebaDeRestauracion(
            sesion,
            respaldo,
            archivo_respaldo,
            diario,
            argumentos.lecturas,
            argumentos.marca,
        )
        if prueba.comprobar_administracion():
            if prueba.comprobar_que_no_existe_el_modulo_de_prueba():
                if prueba.preparar_lecturas():
                    creado = prueba.crear_modulo_de_prueba()
                    restaurado = prueba.restaurar_lecturas()
                    verificado = prueba.comprobar_lo_guardado()
                    resultado = creado and restaurado and verificado
    except SystemExit as error:
        diario.linea("")
        diario.linea("  EJECUCIÓN INTERRUMPIDA: %s" % error)
        prueba = prueba or None
        if prueba is not None:
            prueba.fallos.append("Ejecución interrumpida: %s" % error)
    except Exception as error:  # noqa: BLE001 - se registra y se limpia igual
        diario.linea("")
        diario.linea("  ERROR NO PREVISTO: %s: %s" % (type(error).__name__, error))
        if prueba is not None:
            prueba.fallos.append("Error no previsto: %s: %s" % (type(error).__name__, error))
    finally:
        # La limpieza y la evidencia se ejecutan siempre, también tras un fallo.
        if prueba is not None:
            try:
                prueba.limpiar()
                prueba.comprobar_el_estado_final()
            except Exception as error:  # noqa: BLE001
                prueba.fallos.append(
                    "Fallo al limpiar o al comprobar el estado final: %s: %s"
                    % (type(error).__name__, error)
                )
            prueba.concluir(resultado)
        else:
            diario.seccion("9. CONCLUSIÓN")
            diario.linea("  No se pudo empezar la prueba (véase el error anterior).")

        archivo_evidencia.parent.mkdir(parents=True, exist_ok=True)
        archivo_evidencia.write_text(diario.texto(), encoding="utf-8")

    print("")
    print("=== RESULTADO ===")
    if prueba is not None:
        for fallo in prueba.fallos:
            print("  FALLO: %s" % fallo)
    print("  Evidencia: %s" % archivo_evidencia.resolve())
    print("  Restauración probada: %s" % ("SÍ" if (resultado and prueba and not prueba.fallos) else "NO"))
    return 0 if (resultado and prueba and not prueba.fallos) else 1


if __name__ == "__main__":
    raise SystemExit(main())
