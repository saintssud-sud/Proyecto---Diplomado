# Capturas que faltan del Anexo A

Lista de las capturas que el manual anuncia con su número de figura. Todavía no están insertadas: este archivo es la guía para tomarlas.

## Reglas para todas las capturas

1. Dirección pública visible. La barra de direcciones del navegador debe mostrar `https://sigvach26-bd.web.app` sin recortarla. No se admite una captura tomada contra `localhost`, contra `127.0.0.1:8011` ni contra el emulador.
2. Fecha visible. La fecha del equipo o del sistema debe quedar a la vista, y las lecturas deben mostrar horas coherentes con esa fecha. En las pantallas que muestran fecha y hora de lectura, esa fecha también debe quedar legible.
3. Datos ficticios. Se usan las cuentas, los módulos, los cultivos y los valores de la tabla de datos ficticios de este archivo. No se usan cuentas reales, ni correos de personas reales, ni el correo de la cuenta de administración del proyecto.
4. Sin recortes que oculten lo anterior. Se puede recortar el marco del sistema operativo, pero nunca la barra de direcciones, la fecha ni los datos que la figura debe mostrar.
5. Capturas de producción. Las imágenes se toman sobre el sistema desplegado, con sesión iniciada. No se aceptan dibujos, prototipos ni pantallas armadas.
6. Una captura por figura. Si una figura necesita mostrar dos estados distintos, se toma una sola imagen con el estado que indica la descripción.

## Datos ficticios que deben aparecer

**Las cuentas tienen que ser las que se entregan como usuarios de prueba**, porque son las que el
docente va a usar para revisar y las que van declaradas en el campo de texto de la entrega. No hay que
crear cuentas nuevas para las capturas:

| Dato | Valor |
|---|---|
| Cuenta de Operador | la que se entrega como usuario de prueba del rol 1 (`operador@proyecto.test`) |
| Cuenta de Administrador | la que se entrega como usuario de prueba del rol 2 (`administrador@proyecto.test`) |

Los datos de cultivo que aparecen en las capturas:

| Dato | Valor |
|---|---|
| Módulo 1 | `Módulo 1` · tipo de cultivo `Lechuga` · cultivo `Lechuga` · ubicación `Invernadero Este` · Activo |
| Módulo 2 | `Módulo 2` · tipo de cultivo `Acelga` · cultivo `Acelga` · ubicación `Bancal Sur` · Activo |
| Cultivo Lechuga | pH 5,5 a 6,5 · TDS 560 a 840 ppm · EC 1,2 a 1,8 mS/cm · temperatura de la solución 18 a 22 °C · temperatura ambiental 18 a 26 °C · humedad relativa 60 a 80 % |
| Lecturas del Módulo 1 | pH 6,2 · TDS 850 ppm · EC 1,7 mS/cm · temperatura de la solución 21,5 °C · temperatura ambiental 24,5 °C · humedad relativa 65 % |
| Lectura fuera de rango para la alerta | pH 7,4, con rango del perfil 5,5 a 6,5 |
| Historial | Al menos doce mediciones de pH repartidas en tres meses, entre 5,9 y 6,4 |

> Si el módulo de la maqueta ya existe en el sistema, se puede usar ése en lugar de crear los dos
> ficticios: los datos de cultivo no son datos personales. Lo que no se admite es mostrar correos de
> personas reales ni la cuenta de administración del proyecto con su contraseña.

## Lista de figuras

| Figura | Tarea a la que pertenece | Qué tiene que mostrar la imagen |
|---|---|---|
| Figura A.1 | 3.1 Entrar al sistema | Pantalla de acceso con el logotipo, el título SI.G.VA.C.H., el texto Inicia sesión para continuar, los campos Usuario y Contraseña, el botón Iniciar Sesión y el enlace Crear una cuenta. Con la barra de direcciones pública y la fecha a la vista |
| Figura A.2 | 3.1 Entrar al sistema | Panel de inicio recién abierto, con la barra superior SIGVACH, el recuadro Sistema normal con Todo dentro del rango óptimo, la tarjeta del Módulo 1, las seis tarjetas de variables y el renglón Última actualización con fecha y hora legibles |
| Figura A.3 | 3.2 Crear una cuenta | Formulario de registro con el texto Crea tu cuenta para continuar y los campos Nombres, Apellidos, Teléfono, Cargo (opcional), Usuario y Contraseña completados con datos ficticios, y el botón Registrarme. El correo debe ser ficticio |
| Figura A.4 | 3.3 Cerrar sesión | Menú lateral abierto, con el saludo Hola, seguido del nombre de la cuenta ficticia, el distintivo del rol Operador, el nombre del sistema y la opción Cerrar sesión |
| Figura A.5 | 3.4 Consultar el estado del cultivo | Panel de inicio con el recuadro Sistema normal y el texto Todo dentro del rango óptimo, con las seis variables dentro de rango y la última actualización visible |
| Figura A.6 | 3.4 Consultar el estado del cultivo | Panel de inicio con el recuadro Sistema con alertas y el texto Algunos parámetros están fuera de rango, con la campana de la barra superior mostrando el contador de alertas activas |
| Figura A.7 | 3.5 Cambiar el módulo de cultivo que se consulta | Desplegable Módulo de cultivo abierto, con los dos módulos ficticios a la vista, y debajo la tarjeta del módulo vigente |
| Figura A.8 | 3.6 Revisar el estado de todas las variables | Pantalla Variables con el encabezado, la tarjeta del módulo y la lista de las seis variables. Al menos una tarjeta debe mostrar la etiqueta Normal y otra la etiqueta Por encima del rango o Por debajo del rango, con su rango y su fecha de lectura legibles |
| Figura A.9 | 3.7 Registrar una medición a mano | Cuadro Registrar medición abierto, con la indicación de completar solo las variables medidas, cuatro campos completados con valores ficticios y dos vacíos, y el rango de referencia a la vista como texto de ayuda |
| Figura A.10 | 3.7 Registrar una medición a mano | Aviso emergente al pie con el texto N lecturas registradas y evaluadas por el servidor, sobre el panel de inicio ya actualizado con los valores enviados |
| Figura A.11 | 3.7 Registrar una medición a mano | Panel de inicio de un módulo sin lecturas, con el aviso El módulo nombre todavía no tiene lecturas registradas y el botón Registrar la primera medición a la vista |
| Figura A.12 | 3.8 Ver la evolución de una variable | Pantalla Historial con la tarjeta del módulo, el desplegable Variable con pH elegido, los botones Inicio y Fin con fechas ya seleccionadas y el botón Consultar |
| Figura A.13 | 3.8 Ver la evolución de una variable | Bloque Resultado de la consulta con la línea del nombre de la variable y la cantidad de mediciones, y los renglones Promedio, Máximo y Mínimo con sus valores y unidades |
| Figura A.14 | 3.8 Ver la evolución de una variable | Pantalla Gráfica Histórica con el nombre de la variable, la descripción del periodo, los atajos 3 meses, 6 meses y 1 año, la línea trazada y el resumen del periodo con su cantidad de mediciones |
| Figura A.15 | 3.8 Ver la evolución de una variable | Pantalla Lista de mediciones con el conteo del encabezado y al menos seis renglones, cada uno con fecha y hora, valor con unidad, la etiqueta Manual o Automática y la etiqueta de estado |
| Figura A.16 | 3.9 Atender una alerta | Pantalla Alertas con la tarjeta del módulo, las pestañas Activas e Historial, y la pestaña Activas con al menos una alerta: título pH por encima del rango, valor registrado, rango del perfil y fecha |
| Figura A.17 | 3.9 Atender una alerta | Detalle de la alerta, con el encabezado de color según el estado y los renglones Estado, Variable, Valor registrado, Rango del perfil, Desviación, Fecha de la lectura y Lectura de origen, y el botón Marcar como atendida |
| Figura A.18 | 3.9 Atender una alerta | Pestaña Historial con al menos una alerta atendida, y el estado de la lista tal que se vea que la pestaña Activas quedó sin alertas o con otra |
| Figura A.19 | 3.10 Mantener sus datos de perfil | Pantalla Perfil con el nombre de la cuenta ficticia, su cargo, los distintivos del rol y del estado de la cuenta, y los renglones Correo, Teléfono, Cargo e Identificador de la cuenta |
| Figura A.20 | 3.10 Mantener sus datos de perfil | Cuadro Editar información con los campos Nombre, Teléfono y Cargo completados con datos ficticios y la indicación de que el rol y el estado de la cuenta no se modifican desde ahí |
| Figura A.21 | 3.11 Cambiar el tema y el nombre que se muestra | Pantalla Preferencias con el campo Tu nombre, el botón Guardar, el interruptor Tema oscuro y el renglón del modo de la aplicación |
| Figura A.22 | 4.1 Registrar un cultivo con sus rangos de referencia | Cuadro Añadir cultivo con el campo Nombre del cultivo, el campo Descripción y la lista Rangos de referencia por variable con los mínimos y máximos ficticios de las seis variables |
| Figura A.23 | 4.2 Completar o corregir los rangos de un cultivo | Cuadro Rangos de nombre del cultivo, con los límites vigentes ya cargados y el nombre del cultivo en modo de solo lectura |
| Figura A.24 | 4.3 Ajustar el rango de referencia de una variable | Pantalla Rangos de variables con el desplegable Cultivo, y la lista de rangos mostrando el nombre de la variable y su rango con unidad |
| Figura A.25 | 4.3 Ajustar el rango de referencia de una variable | Cuadro Rango de nombre de la variable, con el cultivo indicado arriba y los campos Mínimo y Máximo con sus unidades, ya corregidos |
| Figura A.26 | 4.4 Gestionar los módulos de cultivo | Pantalla Módulo de cultivo con el título, el texto explicativo, las tarjetas de los dos módulos ficticios con sus distintivos Activo, y el botón Agregar módulo de cultivo |
| Figura A.27 | 4.4 Gestionar los módulos de cultivo | Cuadro Agregar módulo de cultivo con los campos Nombre, Tipo de cultivo, el desplegable Cultivo y el campo Ubicación (opcional) completados con datos ficticios |
| Figura A.28 | 4.4 Gestionar los módulos de cultivo | Menú de acciones de la tarjeta de un módulo desplegado, con las opciones Editar módulo, Desactivar módulo o Activar módulo, y Eliminar módulo, y el cuadro de confirmación de eliminación con el aviso completo a la vista |
| Figura A.29 | 4.5 Gestionar los usuarios y sus roles | Pantalla Usuarios con al menos tres cuentas ficticias, sus roles en distintivos, los datos de contacto y los botones de editar, cambiar rol, activar o desactivar y eliminar. Una cuenta debe mostrar el distintivo Inactiva y la propia, el distintivo Su cuenta |
| Figura A.30 | 4.5 Gestionar los usuarios y sus roles | Cuadro Editar a correo ficticio con los campos Nombre, Teléfono y Cargo |
| Figura A.31 | 4.5 Gestionar los usuarios y sus roles | Cuadro de confirmación Cambiar rol, con el correo, el rol actual y el rol nuevo, y los botones Cancelar y Confirmar |
| Figura A.32 | 4.6 Eliminar un cultivo | Cuadro de confirmación de eliminación de un cultivo, con el título Eliminar seguido del nombre del cultivo y el aviso completo sobre los rangos y los módulos asociados |

Total: 32 figuras.
