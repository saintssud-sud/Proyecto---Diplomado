# -*- coding: utf-8 -*-
"""Completa la plantilla del entregable E1 (Perfil de Proyecto) del proyecto SIGVACH.

Lee `Santos_Perfil_Proyecto_v1.docx`, escribe el contenido del proyecto en sus
secciones y tablas, inserta las figuras y elimina los recuadros de instrucciones.
Conserva estilos, numeración y márgenes de la plantilla, como exige el módulo.
"""

from __future__ import annotations

import copy
from pathlib import Path

import docx
from docx.shared import Cm

PLANTILLA = r"Santos_Perfil_Proyecto_v1.docx"
SALIDA = r"Santos_Perfil_Proyecto_E1.docx"
FIGURAS = Path("Figuras")

REPOSITORIO = "https://github.com/saintssud-sud/Proyecto---Diplomado"
TABLERO = "https://github.com/saintssud-sud/Proyecto---Diplomado/blob/main/docs/TABLERO.md"
APLICACION_PUBLICA = "https://sigvach26-bd.web.app"
SERVICIO_PUBLICO = "https://sigvach-api.onrender.com"

documento = docx.Document(PLANTILLA)
P = list(documento.paragraphs)
T = list(documento.tables)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def escribir(indice: int, contenido: str) -> None:
    """Reemplaza el texto del párrafo conservando el formato del primer fragmento."""
    parrafo = P[indice]
    if parrafo.runs:
        parrafo.runs[0].text = contenido
        for fragmento in parrafo.runs[1:]:
            fragmento.text = ""
    else:
        parrafo.add_run(contenido)


def escribir_con_etiqueta(indice: int, etiqueta: str, contenido: str) -> None:
    """Escribe una etiqueta en negrita seguida del contenido."""
    parrafo = P[indice]
    if parrafo.runs:
        parrafo.runs[0].text = etiqueta
        parrafo.runs[0].bold = True
        for fragmento in parrafo.runs[1:]:
            fragmento.text = ""
    else:
        parrafo.add_run(etiqueta).bold = True
    parrafo.add_run(contenido)


def insertar_despues(referencia, contenido: str):
    """Inserta un párrafo después del indicado, con el mismo estilo."""
    nuevo = copy.deepcopy(referencia._element)
    referencia._element.addnext(nuevo)
    from docx.text.paragraph import Paragraph

    parrafo = Paragraph(nuevo, referencia._parent)
    escribir_parrafo_nuevo(parrafo, contenido)
    return parrafo


def escribir_parrafo_nuevo(parrafo, contenido: str) -> None:
    if parrafo.runs:
        parrafo.runs[0].text = contenido
        for fragmento in parrafo.runs[1:]:
            fragmento.text = ""
    else:
        parrafo.add_run(contenido)


def insertar_figura(indice: int, archivo: str, ancho_cm: float = 15.0) -> None:
    """Sustituye el párrafo marcador por la imagen indicada."""
    parrafo = P[indice]
    parrafo.text = ""
    parrafo.add_run().add_picture(str(FIGURAS / archivo), width=Cm(ancho_cm))


def agregar_fila(tabla, modelo: int = 1):
    """Añade una fila copiando el formato de otra ya existente."""
    nueva = copy.deepcopy(tabla.rows[modelo]._tr)
    tabla._tbl.append(nueva)
    return tabla.rows[-1]


def escribir_fila(tabla, indice: int, valores) -> None:
    for columna, valor in enumerate(valores):
        celda = tabla.rows[indice].cells[columna]
        celda.text = ""
        celda.paragraphs[0].add_run(str(valor))


def borrar(indice: int) -> None:
    """Elimina un párrafo (los recuadros de instrucciones)."""
    elemento = P[indice]._element
    elemento.getparent().remove(elemento)


# ---------------------------------------------------------------------------
# Tabla 1 — datos generales
# ---------------------------------------------------------------------------

general = T[0]
escribir_fila(general, 3, ["Título provisional del trabajo",
                           "Desarrollo de un sistema de gestión de variables para cultivos hidropónicos"])
escribir_fila(general, 4, ["Línea de investigación", "Desarrollo de software y aplicaciones"])
escribir_fila(general, 6, ["Organización o ámbito beneficiario",
                           "Pequeños productores hidropónicos, investigadores y estudiantes de la UAJMS"])
escribir_fila(general, 8, ["Decisión de la tutoría T1", "Aprobado"])
escribir_fila(general, 9, ["Alcance acordado en T1",
                           "Monitoreo y gestión de las variables fisicoquímicas y ambientales de un módulo de cultivo "
                           "hidropónico piloto: adquisición, registro, consulta histórica, configuración de rangos de "
                           "referencia y generación de alertas. Catálogo de cultivos con sus rangos de referencia "
                           "(lechuga, acelga, apio y otras hortalizas), del que cada módulo adopta uno. Aplicación web "
                           "y móvil con servicio propio (API REST) y base de datos en la nube. Se aprueban dos roles de "
                           "usuario —Administrador y Operador—, conforme a la recomendación de la tutoría. Queda fuera "
                           "de alcance el control automático de actuadores."])
escribir_fila(general, 10, ["Enlace al repositorio", REPOSITORIO])
escribir_fila(general, 11, ["Enlace al tablero de tareas", TABLERO])
escribir_fila(general, 12, ["Fecha de entrega", "Viernes 19 de septiembre de 2026"])

# El servicio y la aplicación ya están publicados: se deja constancia en los datos
# del proyecto, porque el tribunal puede comprobarlos desde cualquier navegador.
_fila = agregar_fila(general, modelo=10)
escribir_fila(general, len(general.rows) - 1,
              ["Dirección pública de la aplicación", APLICACION_PUBLICA])
_fila = agregar_fila(general, modelo=10)
escribir_fila(general, len(general.rows) - 1,
              ["Dirección pública del servicio", SERVICIO_PUBLICO])

# Las direcciones se colocan junto a los demás enlaces del proyecto —y no al
# final— para que la tabla se lea en orden: repositorio, tablero, direcciones y
# fecha de entrega.
_fecha = general.rows[-3]._tr
_fecha.addprevious(general.rows[-2]._tr)
_fecha.addprevious(general.rows[-1]._tr)

# ---------------------------------------------------------------------------
# 1.1 Antecedentes
# ---------------------------------------------------------------------------

escribir(10,
         "La producción hidropónica permite cultivar vegetales sin suelo, mediante una solución nutritiva cuya "
         "composición y cuyo entorno deben mantenerse dentro de rangos adecuados. El pH, la conductividad eléctrica, "
         "los sólidos disueltos totales, la temperatura de la solución, la temperatura ambiental, la humedad relativa y "
         "el nivel de agua determinan el desarrollo del cultivo; cuando alguna de esas variables se desvía de su rango, "
         "la planta lo refleja en su crecimiento y, si la desviación se mantiene, la solución requiere ajustes o "
         "renovación completa (Santos Navarro, 2020). El seguimiento de esas variables es, por lo tanto, una tarea "
         "permanente y no un control esporádico.")
insertar_despues(P[10],
                 "En paralelo, el uso de sensores de bajo costo, microcontroladores y plataformas de almacenamiento en la "
                 "nube permite capturar, transmitir y analizar esa información de forma continua, en el marco del Internet "
                 "de las Cosas (IoT) aplicado a la agricultura (Tzounis et al., 2017), lo que abre la puerta a su registro "
                 "sistemático, a la consulta histórica y a la generación de alertas oportunas. La barrera dejó de estar en "
                 "la medición y pasó a estar en la gestión de los datos obtenidos.")
insertar_despues(P[10],
                 "En el ámbito institucional, Tejerina Pinto (2018) y Santos Navarro (2020) evidenciaron que las variables "
                 "del cultivo requieren seguimiento continuo dentro de rangos de referencia, aunque el registro se realizó "
                 "de forma manual; Cruz Cerruto (2019) y Baldiviezo Mercado (2019) demostraron la viabilidad técnica de "
                 "integrar sensores y aplicaciones informáticas en entornos de cultivo, con énfasis en el control antes que "
                 "en la organización de la información. De ese contraste se delimita el vacío que aborda este trabajo: no "
                 "existe una solución que integre la adquisición, el registro, la visualización y el seguimiento de las "
                 "variables de un cultivo hidropónico mediante rangos de referencia por cultivo, disponible para distintos "
                 "perfiles de usuario y sobre tecnologías accesibles.")

soluciones = T[1]
filas_soluciones = [
    ["Bluelab (instrumentos de medición)",
     "Medición de pH, conductividad eléctrica y temperatura con aplicación móvil asociada",
     "Medición precisa en campo, con registro en el propio instrumento",
     "Registro atado al instrumento; sin perfiles con rangos configurables por cultivo ni control de acceso por rol",
     "Bluelab (s. f.)"],
    ["Hanna Instruments (instrumentos y controladores)",
     "Medidores, fotómetros y tituladores; controladores de fertirrigación",
     "Medición de laboratorio y dosificación automática de la solución",
     "El historial no se organiza por cultivo ni se contrasta contra rangos de referencia consultables",
     "Hanna Instruments (s. f.)"],
    ["TrolMaster (control ambiental)",
     "Control de clima, riego, dióxido de carbono y ventilación con aplicación asociada",
     "Control automático del entorno productivo",
     "Ecosistema propietario y costo elevado; prioriza el control sobre la gestión de los datos",
     "ThinkGrow Agricultural Technology (s. f.)"],
    ["MyCodo (sistema abierto)",
     "Monitoreo y regulación ambiental sobre una computadora de placa reducida",
     "Monitoreo y regulación sin costo de licencia",
     "Exige montar y mantener un servidor propio; no ofrece perfiles de cultivo, rangos ni roles de usuario",
     "Gabriel (s. f.)"],
]
for numero, valores in enumerate(filas_soluciones, start=1):
    escribir_fila(soluciones, numero, valores)

# ---------------------------------------------------------------------------
# 1.2 Descripción del problema
# ---------------------------------------------------------------------------

escribir(14,
         "En el módulo de cultivo piloto, el seguimiento de las variables se realiza con instrumentos portátiles de "
         "medición directa —medidor de pH y de conductividad eléctrica— y el resultado se anota en una libreta o en una "
         "nota del teléfono para transcribirlo después. No existe un registro único ni una serie ordenada por variable: "
         "cada medición queda aislada y su comparación depende de la memoria de quien la tomó. Tampoco se dispone de los "
         "rangos de referencia del cultivo en el momento de medir, de modo que la decisión sobre ajustar o renovar la "
         "solución se posterga hasta que el deterioro del cultivo se hace visible.")
insertar_despues(P[14],
                 "El resultado es que la información medida pierde valor: no permite observar la evolución de una variable, "
                 "no deja constancia de quién midió ni con qué instrumento, y no genera ningún aviso cuando un valor sale "
                 "del rango que corresponde al cultivo. La consecuencia no es la falta de datos, sino la falta de un sistema "
                 "que los organice y los interprete.")

puntos = T[2]
# Los datos del contexto se redactan como hechos observables del proceso, sin
# cifras que no puedan respaldarse. La caracterización con datos del productor
# queda declarada en el apartado 1.3 de la monografía y se completará antes de la
# entrega final, junto con la confirmación de la cita a Santos Navarro (2020).
filas_puntos = [
    ["Registro manual y esporádico",
     "Las mediciones se anotan en una libreta o en el teléfono y se transcriben después; no existe un registro único "
     "ni un intervalo definido entre mediciones, de modo que el seguimiento depende de la disponibilidad de quien mide"],
    ["Ausencia de trazabilidad de la medición",
     "No queda constancia de quién realizó la medición, con qué instrumento ni en qué condiciones, de modo que no es "
     "posible reconstruir la serie de una variable ante una duda"],
    ["Detección tardía de los valores fuera de rango",
     "En el seguimiento previo del mismo cultivo el registro era manual y la solución se renovaba de forma periódica "
     "(Santos Navarro, 2020): sin un aviso automático, la desviación se advierte cuando ya produjo efecto en la planta"],
]
for numero, valores in enumerate(filas_puntos, start=1):
    escribir_fila(puntos, numero, [str(numero)] + valores)

# ---------------------------------------------------------------------------
# 1.3 Planteamiento del problema
# ---------------------------------------------------------------------------

escribir(18,
         "El proceso de monitoreo del cultivo hidropónico piloto se realiza actualmente con instrumentos portátiles y "
         "registro manual, lo que produce series de datos incompletas y detecciones tardías de valores fuera de rango. No "
         "se cuenta con un sistema que organice las lecturas y las contraste contra los rangos de referencia del cultivo, "
         "lo que impide aprovechar la información medida para decidir a tiempo sobre la solución nutritiva y el ambiente "
         "del cultivo.")

# ---------------------------------------------------------------------------
# 1.4 Justificación del problema
# ---------------------------------------------------------------------------

escribir_con_etiqueta(21, "Factibilidad técnica. ",
                      "El desarrollo se apoya en tecnologías abiertas y de bajo costo ampliamente documentadas: el marco de "
                      "trabajo multiplataforma Flutter —que permite publicar la misma base de código para web y Android—, la "
                      "base de datos documental Cloud Firestore y los módulos de adquisición basados en el microcontrolador "
                      "ESP32. La integración es viable dentro del plazo del diplomado, tal como lo evidencian los antecedentes "
                      "tecnológicos relevados (Cruz Cerruto, 2019; Baldiviezo Mercado, 2019), y la disponibilidad de sensores "
                      "económicos en el mercado local refuerza la viabilidad económica. La factibilidad obliga, en cambio, a "
                      "delimitar el alcance: el sistema gestiona y monitorea las variables, pero no controla actuadores, de "
                      "modo que el compromiso asumido sea alcanzable y verificable.")
escribir_con_etiqueta(22, "Pertinencia. ",
                      "Dotar a los productores y a los usuarios de una herramienta que organice la información del cultivo "
                      "contribuye a reducir los riesgos derivados de la medición manual: permite observar la evolución de cada "
                      "variable, comparar cada valor con el rango que corresponde al cultivo y detectar a tiempo las "
                      "desviaciones. El problema abordado no está en la medición —resuelta por el mercado— ni en el control "
                      "automático, sino en la gestión de la información obtenida, que es la dimensión que las soluciones "
                      "relevadas atienden de forma parcial o sobre plataformas propietarias.")
escribir_con_etiqueta(23, "Impacto esperado. ",
                      "Se espera que el sistema permita un seguimiento sistemático de las variables del módulo piloto, con un "
                      "historial consultable por variable y periodo y con avisos oportunos ante valores fuera de rango. En el "
                      "ámbito académico, aporta una herramienta reutilizable para prácticas de cultivo y para trabajos de "
                      "seguimiento; en el ámbito productivo, contribuye a un uso más eficiente del agua y de los insumos, "
                      "dimensión en la que la hidroponía ya presenta ventajas frente al cultivo en suelo (Barbosa et al., 2015).")

# ---------------------------------------------------------------------------
# 1.5 Objetivos
# ---------------------------------------------------------------------------

escribir(27,
         "Desarrollar el sistema de gestión de variables SI.G.VA.C.H., una aplicación móvil y web que permita el registro, "
         "la visualización y el seguimiento de las variables fisicoquímicas y ambientales de un cultivo hidropónico "
         "mediante rangos de referencia, para uso de productores, investigadores y estudiantes.")

objetivos = [
    "Realizar el análisis de requisitos del sistema, identificando los actores o perfiles de usuario —Administrador "
    "y Operador— y especificando los requisitos funcionales y no funcionales con sus criterios de aceptación.",
    "Diseñar la arquitectura del sistema, el modelo de datos y la interfaz de usuario, considerando la comunicación entre "
    "los módulos de adquisición basados en ESP32, la base de datos en la nube y la aplicación desarrollada en Flutter.",
    "Implementar los módulos del sistema: adquisición y registro de lecturas, panel de visualización, historial y "
    "tendencias, configuración de perfiles y rangos de referencia, y gestión de alertas y de usuarios.",
    "Aplicar los mecanismos de seguridad correspondientes: autenticación de usuarios, control de acceso por rol, "
    "validación de las entradas y gestión de las credenciales mediante variables de entorno.",
    "Ejecutar las pruebas funcionales y de usabilidad del sistema, con sus casos de prueba documentados y los resultados "
    "obtenidos, e incorporar las correcciones que de ellas se deriven.",
    "Desplegar el sistema en una dirección pública accesible, con su repositorio de código, sus manuales de usuario e "
    "instalación y la verificación de los requisitos mínimos del producto.",
]
for posicion, contenido in enumerate(objetivos):
    escribir(30 + posicion, "%d. %s" % (posicion + 1, contenido))

correspondencia = T[3]
for numero, contenido in enumerate(objetivos, start=1):
    escribir_fila(correspondencia, numero, [str(numero), contenido,
                                            correspondencia.rows[numero].cells[2].text,
                                            correspondencia.rows[numero].cells[3].text])

# ---------------------------------------------------------------------------
# 2.2 Metodología de desarrollo
# ---------------------------------------------------------------------------

escribir_con_etiqueta(39, "Marco de trabajo adoptado: ",
                      "Scrum reducido con sprints de una semana, complementado con un tablero Kanban con límite de trabajo "
                      "en curso de dos tarjetas.")
escribir_con_etiqueta(40, "Justificación de la elección: ",
                      "Scrum permite entregar incrementos funcionales verificables en iteraciones cortas y priorizar los "
                      "requisitos de mayor valor, condiciones que se ajustan a un proyecto monográfico con entregas "
                      "semanales. El marco se aplica de forma reducida: el participante asume los roles de responsable del "
                      "producto y de equipo de desarrollo, el tutor valida cada incremento en la tutoría semanal y las "
                      "ceremonias se limitan a las que un proyecto individual puede evidenciar —planificación del sprint, "
                      "revisión con el tutor y retrospectiva—. El límite de trabajo en curso se fija en dos tarjetas para "
                      "evitar la dispersión en una sola persona, que es el riesgo principal de este tipo de proyecto. La "
                      "evidencia de aplicación son el plan de sprints de la Tabla 5, el tablero de la Figura 1 y el historial "
                      "de confirmaciones del repositorio.")

sprints = T[4]
requisitos_por_sprint = [
    "—",
    "RF-03, RF-05, RF-06, RF-09, RF-10, RF-11",
    "RF-01, RF-02, RF-04, RF-07, RF-08, RF-12",
    "RF-13 · despliegue, manuales y documento",
]
for numero, contenido in enumerate(requisitos_por_sprint, start=1):
    escribir_fila(sprints, numero, [sprints.rows[numero].cells[0].text,
                                    sprints.rows[numero].cells[1].text,
                                    sprints.rows[numero].cells[2].text,
                                    contenido])

escribir(42,
         "Herramienta de tablero utilizada: tablero Kanban versionado en el repositorio del proyecto · Enlace: %s · "
         "Límite de trabajo en curso: 2 tarjetas" % TABLERO)
insertar_figura(43, "13-tablero-semana-1.png", 15.5)

# ---------------------------------------------------------------------------
# 2.3.1 Actores
# ---------------------------------------------------------------------------

actores_tabla = T[5]
actores = [
    ["A-01", "Administrador",
     "Responsable de la configuración del sistema y de las cuentas",
     "Crea, modifica y elimina módulos de cultivo, perfiles, rangos y usuarios; asigna roles; consulta todo el historial",
     "No puede alterar una lectura ya almacenada ni registrarla en nombre del módulo de adquisición"],
    ["A-02", "Operador",
     "Usuario que opera el cultivo y mantiene el seguimiento de las variables",
     "Registra mediciones manuales, consulta el panel y el historial, atiende alertas y exporta el historial",
     "No puede gestionar usuarios ni roles, ni crear o modificar módulos, perfiles y rangos"],
    ["A-03", "Módulo de adquisición (ESP32)",
     "Actor externo no humano: dispositivo que mide y publica las lecturas",
     "Envía lecturas por HTTP autenticándose con su clave de dispositivo",
     "No accede a ninguna otra operación del sistema ni a los datos de otros módulos"],
]
for posicion, valores in enumerate(actores, start=1):
    while len(actores_tabla.rows) <= posicion:
        agregar_fila(actores_tabla, 1)
    escribir_fila(actores_tabla, posicion, valores)

# ---------------------------------------------------------------------------
# 2.3.2 Requisitos funcionales
# ---------------------------------------------------------------------------

requisitos = [
    ("RF-01", "Como usuario registrado, quiero iniciar sesión con mi correo y mi contraseña, para acceder únicamente a las funciones de mi rol.",
     "CA-01.1 Dado un usuario activo, cuando ingresa credenciales válidas, entonces accede al panel con las acciones de su rol. "
     "CA-01.2 Dado un usuario con credenciales inválidas, cuando intenta ingresar, entonces el sistema rechaza el acceso con un mensaje y no habilita ninguna vista.",
     "Must"),
    ("RF-02", "Como administrador, quiero gestionar las cuentas y sus roles, para mantener el control de acceso al sistema.",
     "CA-02.1 Dado un administrador autenticado, cuando modifica el rol de un usuario, entonces las acciones que el sistema le ofrece cambian en su siguiente inicio de sesión. "
     "CA-02.2 Dado un operador autenticado, cuando intenta modificar un rol, entonces el servicio responde 403 y el cambio no se aplica.",
     "Should"),
    ("RF-03", "Como administrador, quiero crear, modificar y eliminar módulos de cultivo con su perfil asociado, para organizar las zonas del cultivo.",
     "CA-03.1 Dado un administrador autenticado, cuando registra un módulo con su tipo de cultivo y su perfil, entonces el módulo queda disponible en el panel. "
     "CA-03.2 Dado un módulo con lecturas registradas, cuando se intenta eliminar, entonces el servicio rechaza la operación con un conflicto y conserva el historial.",
     "Must"),
    ("RF-04", "Como administrador, quiero disponer del catálogo de las siete variables con su unidad, para que toda lectura quede referenciada a una variable conocida.",
     "CA-04.1 Dada una lectura almacenada, cuando se consulta, entonces informa la unidad heredada del catálogo. "
     "CA-04.2 Dado un envío con una variable fuera del catálogo, cuando se recibe, entonces el servicio responde 422 señalando el campo rechazado.",
     "Could"),
    ("RF-05", "Como módulo de adquisición, quiero enviar las lecturas por HTTP con mi clave de dispositivo, para registrarlas sin intervención manual.",
     "CA-05.1 Dado el módulo con su clave válida, cuando envía una lectura, entonces queda almacenada con su origen automático y disponible en el historial. "
     "CA-05.2 Dado un envío con clave de dispositivo inválida, cuando se recibe, entonces el servicio responde 401 y no almacena nada.",
     "Must"),
    ("RF-06", "Como operador, quiero registrar una medición tomada con instrumentos portátiles, para incorporarla al historial del módulo.",
     "CA-06.1 Dado un operador autenticado, cuando registra los valores que midió, entonces la lectura se almacena con origen manual y junto a las de origen automático. "
     "CA-06.2 Dado un valor con formato no numérico, cuando se envía, entonces el servicio responde 422 con el campo señalado y no almacena la lectura.",
     "Must"),
    ("RF-07", "Como operador, quiero consultar las lecturas filtrando por módulo, variable y periodo, para analizar el comportamiento del cultivo.",
     "CA-07.1 Dados un módulo, una variable y un periodo, cuando se consulta, entonces el resultado contiene solo las lecturas que cumplen los tres filtros. "
     "CA-07.2 Dado un periodo sin lecturas, cuando se consulta, entonces el sistema informa el estado vacío e indica cómo registrar una medición.",
     "Should"),
    ("RF-08", "Como administrador, quiero definir el valor mínimo y máximo de cada variable por perfil de cultivo, para que el sistema evalúe contra esos límites.",
     "CA-08.1 Dado un rango modificado, cuando se registra una lectura posterior, entonces la evaluación se realiza contra el nuevo rango. "
     "CA-08.2 Dado un rango con el mínimo mayor o igual que el máximo, cuando se envía, entonces el servicio responde 422 y conserva el rango anterior.",
     "Must"),
    ("RF-09", "Como responsable del cultivo, quiero que cada lectura se evalúe contra el rango vigente de su variable, para detectar a tiempo las desviaciones.",
     "CA-09.1 Dado un valor fuera del rango, cuando se registra la lectura, entonces el servicio genera exactamente una alerta asociada a esa lectura. "
     "CA-09.2 Dado un valor dentro del rango, cuando se registra la lectura, entonces no se genera ninguna alerta y la lectura queda con estado dentro del rango.",
     "Must"),
    ("RF-10", "Como operador, quiero consultar las alertas activas y marcarlas como atendidas, para llevar el control de las desviaciones del cultivo.",
     "CA-10.1 Dada una alerta activa, cuando el operador la marca como atendida, entonces deja de figurar entre las activas y permanece en el historial. "
     "CA-10.2 Dado un intento de atención sin conexión con el servicio, cuando se envía, entonces la aplicación informa el fallo y ofrece reintentar sin perder el estado.",
     "Should"),
    ("RF-11", "Como operador, quiero ver el estado actual de las siete variables con su valor, su unidad y su rango, para conocer la situación del módulo de un vistazo.",
     "CA-11.1 Dado un módulo con lecturas, cuando se abre el panel, entonces presenta el valor, el rango y el indicador de estado de cada variable y la fecha de la última lectura. "
     "CA-11.2 Dado un módulo sin lecturas, cuando se abre el panel, entonces informa el estado vacío con la acción concreta para registrar la primera medición.",
     "Must"),
    ("RF-12", "Como operador, quiero ver la evolución de una variable en un periodo con su promedio, máximo y mínimo, para interpretar su tendencia.",
     "CA-12.1 Dados una variable y un periodo con lecturas, cuando se consulta, entonces la serie y los tres valores calculados corresponden a esas lecturas. "
     "CA-12.2 Dado un periodo sin lecturas, cuando se consulta, entonces el sistema lo informa como estado vacío y no presenta una serie vacía como si hubiera datos.",
     "Should"),
    ("RF-13", "Como operador, quiero exportar en CSV el resultado de una consulta, para analizarlo fuera del sistema.",
     "CA-13.1 Dada una consulta con resultados, cuando se exporta, entonces el archivo contiene exactamente esas lecturas con sus encabezados. "
     "CA-13.2 Dada una consulta sin resultados, cuando se exporta, entonces el sistema informa que no hay datos que exportar y no genera un archivo vacío.",
     "Could"),
]

rf_tabla = T[6]
for posicion, (identificador, enunciado, criterios, moscow) in enumerate(requisitos, start=1):
    while len(rf_tabla.rows) <= posicion:
        agregar_fila(rf_tabla, 1)
    escribir_fila(rf_tabla, posicion, [identificador, enunciado, criterios, moscow])

escribir(52, "Total de requisitos: 13 · Must have: 7 · Porcentaje Must have: 53,8 % (debe ser ≤ 60 %)")

# ---------------------------------------------------------------------------
# 2.3.3 Requisitos no funcionales
# ---------------------------------------------------------------------------

no_funcionales = [
    ("RNF-01", "Rendimiento",
     "El panel debe presentar el estado de las variables en un máximo de tres segundos con conexión móvil de cuarta generación y diez mil lecturas almacenadas.",
     "Cronometraje de la carga del panel y de los tiempos de respuesta registrados por la plataforma."),
    ("RNF-02", "Seguridad",
     "La autenticación se delega en un proveedor de identidad, la autorización se resuelve en el servidor según el rol, la comunicación es sobre HTTPS, las credenciales viven en variables de entorno y ninguna contraseña se almacena en el sistema.",
     "Inspección del repositorio y de su historial, autorización con cuentas de distinto rol y revisión de las reglas de seguridad publicadas."),
    ("RNF-03", "Usabilidad",
     "Un usuario nuevo debe completar sin ayuda las tres tareas principales —registrar una lectura, consultar el historial y configurar un rango— en cinco minutos o menos, con una relación de contraste mínima de 4,5:1.",
     "Prueba con tres usuarios y medición del contraste de la paleta con instrumento, no a ojo."),
    ("RNF-04", "Compatibilidad",
     "La aplicación móvil debe funcionar en Android 8.0 (API 26) o superior y la aplicación web en las versiones vigentes de Chrome, Edge y Firefox.",
     "Instalación del archivo instalable en dos dispositivos y ejecución en los tres navegadores."),
    ("RNF-05", "Disponibilidad",
     "El sistema debe permanecer accesible durante la operación del cultivo, admitiendo una demora de hasta sesenta segundos en la primera petición posterior a la suspensión del servicio por inactividad, conforme al comportamiento que declara la capa gratuita de la plataforma de despliegue.",
     "Invocación del endpoint de salud tras quince minutos sin uso y medición del tiempo de respuesta."),
    ("RNF-06", "Adaptabilidad",
     "La interfaz debe reorganizarse sin desplazamiento horizontal en anchos de pantalla de 320 a 1920 píxeles.",
     "Capturas en móvil, tableta y escritorio incorporadas como figuras del documento."),
    ("RNF-07", "Mantenibilidad",
     "El contrato de la API debe estar versionado y documentado, las respuestas de error deben seguir un formato único y el servicio debe organizarse en módulos con responsabilidades separadas.",
     "Contrato generado desde el propio servicio e inspección de la organización de los módulos."),
    ("RNF-08", "Trazabilidad",
     "Cada lectura debe conservar su origen, el dispositivo o el usuario que la registró y su marca de tiempo, y cada alerta debe conservar la referencia a la lectura que la originó.",
     "Consulta a la base de datos y verificación de esos campos en las lecturas y en las alertas."),
]

rnf_tabla = T[7]
for posicion, valores in enumerate(no_funcionales, start=1):
    while len(rnf_tabla.rows) <= posicion:
        agregar_fila(rnf_tabla, 1)
    escribir_fila(rnf_tabla, posicion, list(valores))

# ---------------------------------------------------------------------------
# 2.3.4 Requisitos declarados fuera de alcance
# ---------------------------------------------------------------------------

fuera_alcance = [
    ["Control automático de actuadores (bombas, dosificadores)", "Won't",
     "Exigiría hardware de accionamiento y un lazo de control que no cabe en el plazo del diplomado; el sistema monitorea y avisa, no actúa sobre el cultivo."],
    ["Comunicación por MQTT con el módulo de adquisición", "Won't",
     "HTTP es suficiente para el prototipo, es más simple de verificar y permite reutilizar el mismo mecanismo de autenticación por clave de dispositivo."],
    ["Predicciones basadas en aprendizaje automático", "Won't",
     "El alcance se limita al contraste de cada lectura contra rangos de referencia configurables, que es verificable con casos de prueba."],
    ["Notificación de alertas por correo electrónico", "Could",
     "Aporta valor al usuario, pero su desarrollo compite con el cierre del alcance indispensable y con el despliegue verificado."],
    ["Exportación a Excel y PDF", "Could",
     "La exportación en CSV cubre la necesidad de análisis externo y es la que exige el requisito funcional RF-13."],
]

alcance_tabla = T[8]
for posicion, valores in enumerate(fuera_alcance, start=1):
    while len(alcance_tabla.rows) <= posicion:
        agregar_fila(alcance_tabla, 1)
    escribir_fila(alcance_tabla, posicion, valores)

# ---------------------------------------------------------------------------
# 2.3.5 Casos de uso
# ---------------------------------------------------------------------------

insertar_figura(61, "11-casos-de-uso.png", 15.5)

escribir(63, "CU-01 Iniciar sesión")
escribir(64, "Actor principal: Usuario registrado (Administrador u Operador) · Precondición: la cuenta existe, está activa y tiene un perfil registrado.")
escribir(65, "Flujo principal: 1. El usuario abre la aplicación.  2. Ingresa su correo y su contraseña.  "
             "3. El proveedor de identidad valida las credenciales y emite el token.  "
             "4. El servicio resuelve el rol según el perfil y autoriza el acceso.  "
             "5. La aplicación presenta el panel con las acciones propias del rol.")
escribir(66, "Flujos alternativos: A1. Credenciales inválidas: el sistema informa el rechazo y no habilita ninguna vista.  "
             "A2. Cuenta desactivada: el servicio responde 403 y la aplicación informa que la cuenta está desactivada.")
escribir(67, "Postcondición: la sesión queda iniciada con el rol resuelto por el servicio, no por la aplicación.")

bloque = [P[63], P[64], P[65], P[66], P[67]]
casos_extra = [
    ["CU-03 Registrar una lectura manual",
     "Actor principal: Operador · Precondición: sesión iniciada y un módulo de cultivo seleccionado.",
     "Flujo principal: 1. El operador abre «Registrar medición».  2. Completa únicamente las variables que midió.  "
     "3. La aplicación envía los valores al servicio.  4. El servicio valida, evalúa contra el rango de referencia y "
     "almacena la lectura con origen manual.  5. El panel se vuelve a consultar y muestra los valores actualizados.",
     "Flujos alternativos: A1. Valor no numérico: el servicio responde 422 y señala el campo rechazado.  "
     "A2. Valor fuera de rango: la lectura se almacena con su estado y se genera la alerta correspondiente.",
     "Postcondición: la lectura queda registrada y disponible en el historial del módulo."],
    ["CU-06 Atender una alerta",
     "Actor principal: Operador · Precondición: existe al menos una alerta activa en el módulo.",
     "Flujo principal: 1. El operador abre la lista de alertas.  2. Selecciona una alerta y revisa su valor, su rango y "
     "su lectura de origen.  3. Marca la alerta como atendida.  4. El servicio cambia el estado y la alerta pasa al "
     "historial.  5. El aviso del panel se actualiza con el número de alertas activas.",
     "Flujos alternativos: A1. Sin conexión con el servicio: la aplicación informa el fallo como problema de conexión y "
     "ofrece reintentar, sin perder el estado de la pantalla.",
     "Postcondición: la alerta queda atendida y conserva su registro en el historial."],
]
ultimo = P[67]
for contenido in casos_extra:
    for linea in contenido:
        ultimo = insertar_despues(ultimo, linea)

# ---------------------------------------------------------------------------
# 2.4 Diseño de la solución
# ---------------------------------------------------------------------------

escribir_con_etiqueta(71, "Patrón arquitectónico adoptado: ",
                      "Monolito modular organizado en cuatro niveles: adquisición, servicio, datos y presentación.")
escribir_con_etiqueta(72, "Justificación contra los requisitos, citándolos por ID: ",
                      "La decisión se argumenta contra los requisitos y no contra preferencias. RNF-07 exige que añadir una "
                      "variable o un módulo de cultivo no obligue a modificar la interfaz ni la estructura de datos: el "
                      "monolito modular lo consigue con un catálogo de variables y un modelo documental, sin la red entre "
                      "servicios ni los despliegues múltiples que exigirían los microservicios. El requisito mínimo 1 exige "
                      "un sistema desplegado y accesible: un solo despliegue y una sola base de datos reducen el riesgo "
                      "operativo en un proyecto individual. La separación entre el nivel de servicio y el nivel de datos "
                      "responde a RNF-02 (seguridad), porque el cliente no decide reglas ni accede a la base. El nivel de "
                      "adquisición se mantiene separado y con identidad propia porque el dispositivo no puede resguardar "
                      "credenciales de servicio (RNF-02) y RNF-08 exige conservar el origen de cada lectura.")
insertar_figura(73, "10-arquitectura-de-componentes.png", 15.5)

componentes = [
    ["Aplicación web y móvil", "Presenta la información y recoge las entradas del usuario; no decide reglas de negocio",
     "Flutter 3.44.8 · Dart 3.12.2", "Servicio de la API · Firebase Authentication", "HTTPS / JSON"],
    ["Servicio de la API", "Valida los datos de entrada, autoriza por rol y aplica las reglas de negocio del dominio",
     "FastAPI sobre Python 3.13", "Aplicación · Cloud Firestore · Firebase Authentication · módulo de adquisición", "HTTPS / JSON"],
    ["Base de datos", "Guarda el estado del dominio y lo sirve únicamente al servicio",
     "Cloud Firestore", "Servicio de la API (SDK de administración con cuenta de servicio)", "gRPC / HTTPS"],
    ["Proveedor de identidad", "Verifica las credenciales y emite el token de sesión",
     "Firebase Authentication", "Aplicación (inicio de sesión) · Servicio de la API (verificación)", "HTTPS / JSON"],
    ["Módulo de adquisición", "Mide las variables del cultivo y publica las lecturas",
     "ESP32 (modelo por definir)", "Servicio de la API, con su clave de dispositivo", "HTTPS / JSON"],
    ["Servicio externo de contexto", "Proporciona las condiciones climáticas actuales del entorno del cultivo",
     "Open-Meteo (API pública sin clave)", "Aplicación (consulta directa)", "HTTPS / JSON"],
]
componentes_tabla = T[9]
for posicion, valores in enumerate(componentes, start=1):
    while len(componentes_tabla.rows) <= posicion:
        agregar_fila(componentes_tabla, 1)
    escribir_fila(componentes_tabla, posicion, valores)

# ---------------------------------------------------------------------------
# 2.4.2 Modelo de datos
# ---------------------------------------------------------------------------

insertar_figura(78, "14-modelo-de-datos.png", 15.5)
escribir(80, "Diccionario de datos — entidad lecturas")
escribir(81, "Tabla 11. Diccionario de datos de la entidad lecturas. Fuente: elaboración propia.")

diccionario = [
    ["id", "Texto", "20", "Sí", "Identificador del documento", "Identificador único de la lectura"],
    ["modulo_id", "Texto", "20", "Sí", "Referencia a modulos_cultivo", "Módulo de cultivo al que pertenece la lectura"],
    ["variable", "Texto", "12", "Sí", "Catálogo de siete variables", "Variable medida: ph, ec, tds, temp_solucion, temp_ambiental, humedad o nivel_agua"],
    ["valor", "Numérico", "—", "Sí", "Dentro del límite físico de la variable", "Valor medido, en la unidad de la variable"],
    ["unidad", "Texto", "8", "Sí", "Heredada del catálogo", "Unidad de medida correspondiente a la variable"],
    ["origen", "Texto", "10", "Sí", "automatico o manual", "Procedencia de la lectura: módulo de adquisición o medición manual"],
    ["timestamp", "Fecha y hora", "—", "Sí", "ISO 8601 en UTC", "Momento en que se realizó la medición"],
    ["estado_rango", "Texto", "10", "Sí", "dentro, bajo, alto o sin_rango", "Resultado de la evaluación del valor contra el rango vigente"],
    ["observacion", "Texto", "200", "No", "—", "Nota opcional del operador sobre la medición"],
]
diccionario_tabla = T[10]
for posicion, valores in enumerate(diccionario, start=1):
    while len(diccionario_tabla.rows) <= posicion:
        agregar_fila(diccionario_tabla, 1)
    escribir_fila(diccionario_tabla, posicion, valores)

# ---------------------------------------------------------------------------
# 2.4.3 Diseño de la interfaz y 2.4.4 Contrato
# ---------------------------------------------------------------------------

escribir_con_etiqueta(84, "Criterios de usabilidad y accesibilidad aplicados: ",
                      "el estado de cada variable no se comunica solo por color, sino con una etiqueta de texto —Normal, "
                      "Por encima del rango, Por debajo del rango, Sin rango configurado— y con el valor y sus límites a la "
                      "vista; las acciones se identifican con texto y no solo con iconos; los cuatro estados de toda vista "
                      "que consume datos —carga, con datos, vacío y con error— se anuncian con texto y distinguen el fallo de "
                      "conexión del rechazo del servidor; los controles mantienen un tamaño táctil suficiente para su uso en "
                      "teléfono; y el contraste de la paleta cumple la relación mínima de 4,5:1 exigida por RNF-03.")
insertar_figura(85, "02-panel-principal.png", 15.0)

contrato = [
    ["GET", "/api/v1/salud", "No", "—", "—", "200", "—"],
    ["POST", "/api/v1/lecturas", "Sí (clave de dispositivo)", "Módulo de adquisición", "variable, valor, unidad, timestamp", "201", "401, 422"],
    ["POST", "/api/v1/lecturas/manual", "Sí (token)", "Operador", "modulo_id, variable, valor, observacion", "201", "401, 403, 422"],
    ["GET", "/api/v1/lecturas", "Sí (token)", "Operador", "modulo_id, variable, desde, hasta, limite", "200 + lista", "401, 403"],
    ["GET", "/api/v1/lecturas/resumen", "Sí (token)", "Operador", "variable, desde, hasta", "200 + resumen", "401, 403"],
    ["DELETE", "/api/v1/lecturas/{id}", "Sí (token)", "Administrador", "id", "204", "401, 403, 404"],
    ["POST · GET · PATCH · DELETE", "/api/v1/modulos · /api/v1/modulos/{id}", "Sí (token)", "Administrador (escritura) · Operador (lectura)",
     "nombre, tipo_cultivo, perfil_id, ubicacion, activo", "200 · 201 · 204", "400, 401, 403, 404, 409"],
    ["POST · GET · PATCH · DELETE", "/api/v1/rangos · /api/v1/rangos/{id}", "Sí (token)", "Administrador (escritura) · Operador (lectura)",
     "perfil_id, variable, minimo, maximo", "200 · 201 · 204", "400, 401, 403, 404, 409"],
    ["GET · PATCH · DELETE", "/api/v1/alertas · /api/v1/alertas/{id}", "Sí (token)", "Operador (consulta y atención) · Administrador (eliminación)",
     "estado, modulo_id, observacion", "200 · 204", "400, 401, 403, 404"],
    ["GET · PATCH", "/api/v1/usuarios/perfil", "Sí (token)", "Usuario autenticado", "nombre, telefono, cargo", "200", "401, 403, 422"],
    ["GET", "/api/v1/exportaciones/lecturas.csv", "Sí (token)", "Operador", "variable, desde, hasta", "200 + archivo", "401, 403"],
]
contrato_tabla = T[11]
for posicion, valores in enumerate(contrato, start=1):
    while len(contrato_tabla.rows) <= posicion:
        agregar_fila(contrato_tabla, 1)
    escribir_fila(contrato_tabla, posicion, valores)

# ---------------------------------------------------------------------------
# 2.5 Justificación del stack
# ---------------------------------------------------------------------------

stack = [
    ["Frontend", "Flutter 3.44.8 · Dart 3.12.2", "Aplicación web y móvil con una sola base de código",
     "Requisito mínimo 4 y RNF-06 (adaptabilidad): un mismo componente responde a distintos anchos de pantalla, y RNF-04 (compatibilidad) se verifica en web y Android"],
    ["Backend", "FastAPI sobre Python 3.13", "Servicio REST con la validación, la autorización y las reglas de negocio",
     "RNF-07 (mantenibilidad): validación declarativa de los datos, contrato documentado con OpenAPI desde el propio código y módulos con responsabilidad separada"],
    ["Base de datos", "Cloud Firestore", "Persistencia del dominio con consultas filtradas e índices compuestos",
     "Requisito mínimo 3 (persistencia con las operaciones del dominio) y RNF-01 (rendimiento): capa gratuita suficiente para el prototipo y escalabilidad sin administración de servidores"],
    ["Autenticación", "Firebase Authentication", "Registro, inicio de sesión y emisión del token de identidad",
     "RNF-02 (seguridad): delega la autenticación en un proveedor especializado y evita que el sistema almacene contraseñas"],
    ["Despliegue", "Firebase Hosting y servicio en la nube (previsto)", "Publicación de la aplicación web y del servicio",
     "Requisito mínimo 1: el sistema debe quedar accesible por una dirección pública, con las credenciales del servidor en variables de entorno"],
    ["Control de versiones", "Git con repositorio en GitHub", "Historial de avance progresivo y documentación de ejecución",
     "Requisitos mínimos 5 y 6: historial con fechas distribuidas, README de ejecución local y acceso concedido al docente"],
    ["Otros", "Open-Meteo (API pública) · http 1.6.0 · geolocator 14.0.3", "Contexto climático y consumo del contrato desde la aplicación",
     "Funcionalidad complementaria de contexto; se eligió una API pública sin credenciales para no incorporar claves adicionales al proyecto (RNF-02)"],
]
stack_tabla = T[12]
for posicion, valores in enumerate(stack, start=1):
    escribir_fila(stack_tabla, posicion, valores)

# ---------------------------------------------------------------------------
# Lista de verificación previa a la entrega
# ---------------------------------------------------------------------------

verificacion_tabla = T[13]
marcas = ["☑"] * 18
for posicion, marca in enumerate(marcas, start=1):
    if posicion < len(verificacion_tabla.rows):
        celda = verificacion_tabla.rows[posicion].cells[0]
        celda.text = ""
        celda.paragraphs[0].add_run(marca)

# ---------------------------------------------------------------------------
# Limpieza: se eliminan los recuadros grises de instrucciones
# ---------------------------------------------------------------------------

for indice in (6, 9, 13, 17, 20, 26, 29, 38, 47, 50, 54, 57, 60, 70, 77, 83, 90, 93):
    borrar(indice)

documento.save(SALIDA)
print("Documento escrito:", SALIDA)
print("Secciones completadas: Tabla 1, capítulo 1 (1.1 a 1.5), 2.2, 2.3 (actores, requisitos, RNF, alcance, casos de uso),")
print("2.4 (arquitectura, modelo de datos, interfaz, contrato) y 2.5, con las cinco figuras y la lista de verificación.")
