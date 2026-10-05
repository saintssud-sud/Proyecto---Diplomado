# Anexo A. Manual de usuario

SIGVACH. Sistema de Gestión de Variables para Cultivos Hidropónicos.

Autor: Freddy Santos N. Diplomado en Desarrollo Web y Aplicaciones Móviles, Universidad Autónoma Juan Misael Saracho, Tarija, Bolivia.

---

## 1. Qué es SIGVACH

SIGVACH es una aplicación para registrar, consultar y dar seguimiento a las variables fisicoquímicas y ambientales de un cultivo hidropónico. Gestiona seis variables: pH, sólidos disueltos totales (TDS), conductividad eléctrica (EC), temperatura de la solución nutritiva, temperatura ambiental y humedad relativa.

El sistema no mide por sí mismo. Recibe las lecturas de un módulo de adquisición con sensores, o las que una persona registra a mano cuando mide con instrumentos portátiles. Su aporte está en organizar esa información: guardarla, compararla con los rangos de referencia del cultivo, generar una alerta cuando un valor sale del rango y permitir su consulta histórica.

La evaluación de cada valor contra su rango la realiza el servidor, no la aplicación. Por ese motivo los estados que usted ve en pantalla, las alertas y los resúmenes del historial son los mismos en cualquier dispositivo con el que consulte la misma cuenta.

## 2. Antes de empezar

### 2.1 Requisitos

| Aspecto | Requisito |
|---|---|
| Aplicación web | Navegador actualizado, en la dirección pública del sistema |
| Aplicación móvil | Android 8.0 o superior |
| Conexión | Necesaria para consultar y registrar. Sin conexión la aplicación informa el problema y ofrece reintentar |
| Cuenta | Un correo electrónico y una contraseña. La cuenta se crea desde la propia pantalla de acceso |
| Rol | Toda cuenta nueva queda con el rol de Operador. El rol de Administrador lo concede después una cuenta que ya lo tenga |

### 2.2 Conceptos que conviene fijar

| Concepto | Qué es |
|---|---|
| Módulo de cultivo | La instalación física donde están los sensores. Tiene nombre, tipo de cultivo, cultivo asociado, ubicación y un estado: Activo o Inactivo |
| Cultivo | La especie que se siembra en el módulo (lechuga, acelga, apio). Define los rangos de referencia de las seis variables |
| Rango de referencia | El mínimo y el máximo admisibles de una variable para un cultivo. Es el patrón con el que el servidor evalúa cada lectura |
| Lectura o medición | El valor de una variable en un momento determinado. Su origen es Automática, cuando la envía el módulo de adquisición, o Manual, cuando la registra una persona |
| Alerta | El aviso que genera el servidor cuando una lectura sale del rango de su cultivo. Está Activa mientras no se atienda y pasa al historial cuando se atiende |
| Rol | El conjunto de operaciones habilitadas para una cuenta: Administrador u Operador |

### 2.3 Cómo moverse por la aplicación

La barra inferior tiene seis secciones: Inicio, Variables, Módulo, Cultivos, Historial y Ajustes. Se cambia de sección pulsando la que corresponda.

| Elemento | Dónde está | Para qué sirve |
|---|---|---|
| Icono de actualizar | Barra superior, a la izquierda de la campana | Vuelve a consultar los datos de la sección en la que está |
| Campana | Barra superior, a la derecha | Abre la pantalla de Alertas. Cuando el módulo vigente tiene alertas activas, muestra sobre el icono cuántas son |
| Menú lateral | Icono de tres líneas, arriba a la izquierda | Muestra el saludo con el nombre de la cuenta y su rol, y ofrece Cerrar sesión |
| Barra inferior | Parte inferior de la pantalla | Cambia de sección |

La sección Inicio es el panel de estado del cultivo. La sección Módulo administra las instalaciones físicas. La sección Cultivos administra las especies y sus rangos. Las alertas no ocupan un lugar en la barra inferior: se consultan desde la campana. Los rangos de referencia y la administración de cuentas se alcanzan desde Ajustes.

### 2.4 Los cuatro estados de las vistas

Toda pantalla que muestra datos del servidor pasa por cuatro estados. Reconocerlos evita confundir un problema de conexión con un problema del sistema.

| Estado | Qué se ve | Qué debe hacer usted |
|---|---|---|
| Cargando | Un indicador de progreso con el texto Cargando información… | Espere. La primera consulta del día puede demorar porque el servicio se suspende por inactividad |
| Con datos | La información solicitada | Úsela con normalidad |
| Vacío | Un aviso que explica que todavía no hay información y qué hacer para generarla | Registre la primera medición del módulo o amplíe el periodo de la consulta |
| Con error | El título No se pudo conectar con el servidor, o el título La operación no pudo completarse, con el botón Reintentar | Si el problema es de conexión, revise la red y pulse Reintentar. Si el servidor rechazó la operación, reintentar no la resuelve: corrija el dato señalado o consulte con la administración |

## 3. Tareas del Operador

El Operador registra las mediciones, consulta el estado del cultivo, revisa el historial y atiende las alertas.

### 3.1 Entrar al sistema

1. Abra la aplicación. Mientras comprueba si hay una sesión iniciada aparece la pantalla de presentación con el logotipo y el texto Cargando...
2. En la pantalla de acceso, escriba su correo electrónico en el campo Usuario.
3. Escriba su contraseña en el campo Contraseña. Puede pulsar el icono del ojo para verla mientras la escribe.
4. Pulse el botón Iniciar Sesión. Mientras se comprueba, el botón muestra Procesando... y queda bloqueado.
5. Si las credenciales son correctas, se abre el panel de inicio. Si no lo son, aparece el mensaje Correo o contraseña incorrectos.

La pantalla de acceso se muestra en la Figura A.1 y el panel de inicio en la Figura A.2.

### 3.2 Crear una cuenta

1. En la pantalla de acceso, pulse el enlace Crear una cuenta. El encabezado cambia a Crea tu cuenta para continuar.
2. Escriba sus nombres en el campo Nombres. Es obligatorio.
3. Complete, si corresponde, los campos Apellidos, Teléfono y Cargo (opcional).
4. Escriba el correo electrónico en el campo Usuario. Debe contener el símbolo arroba.
5. Escriba una contraseña de seis caracteres como mínimo.
6. Pulse el botón Registrarme.
7. Si el registro prospera, aparece el mensaje Cuenta creada y sesion iniciada, y se abre el panel de inicio.

La cuenta queda con el rol de Operador. Para tareas de administración, una cuenta con rol de Administrador debe concederle ese rol desde Ajustes, como se describe en la tarea 4.5.

Puede volver al formulario de acceso con el enlace Ya tengo cuenta. El formulario de registro se muestra en la Figura A.3.

### 3.3 Cerrar sesión

1. Pulse el icono de tres líneas, arriba a la izquierda, para abrir el menú lateral.
2. Pulse Cerrar sesión. La sesión se cierra y la aplicación vuelve a la pantalla de acceso.

También puede cerrar sesión desde Ajustes, con la opción Cerrar sesión del final de la lista, o desde Perfil, con la opción del mismo nombre. El menú lateral abierto se muestra en la Figura A.4.

### 3.4 Consultar el estado del cultivo

1. Pulse Inicio en la barra inferior. Si acaba de iniciar sesión, ya se encuentra en esta sección.
2. Lea el recuadro superior. Indica el estado general del módulo: Sistema normal con el texto Todo dentro del rango óptimo, o Sistema con alertas con el texto Algunos parámetros están fuera de rango.
3. Revise la tarjeta del módulo: nombre, tipo de cultivo, el cultivo de referencia y la ubicación, además de si está Activo o Inactivo.
4. Lea las tarjetas de las variables. Cada una muestra el último valor con su unidad, el nombre de la variable, su rango de referencia y una etiqueta de estado.
5. Compruebe el renglón Última actualización, al pie. Si indica Sin lecturas, el módulo todavía no tiene ninguna medición registrada.
6. Si necesita el dato más reciente, pulse el icono de actualizar de la barra superior.

Un valor sin fecha no es información. Antes de sacar conclusiones, verifique la última actualización: si es de hace varias horas, los valores que ve pueden no corresponder al estado actual del cultivo.

El panel sin novedades se muestra en la Figura A.5 y el panel con parámetros fuera de rango en la Figura A.6.

### 3.5 Cambiar el módulo de cultivo que se consulta

1. En Inicio, si hay más de un módulo activo, aparece arriba el desplegable Módulo de cultivo.
2. Ábralo y elija el módulo que desea revisar.
3. El panel vuelve a consultar los datos del módulo elegido. El cambio alcanza también a las secciones Variables, Historial y a la pantalla de Alertas, que siempre trabajan sobre el módulo vigente.

Si el módulo elegido todavía no tiene lecturas, el panel muestra el aviso correspondiente y el botón para registrar la primera medición. El selector de módulo se muestra en la Figura A.7.

### 3.6 Revisar el estado de todas las variables

1. Pulse Variables en la barra inferior.
2. Revise el encabezado: indica que los datos vienen del servicio y que se evalúan contra los rangos del cultivo, y repite la tarjeta del módulo vigente.
3. Lea la lista de las seis variables. Cada renglón muestra el último valor con su unidad, el nombre de la variable, su rango de referencia, la fecha de la lectura y una etiqueta de estado.

| Etiqueta | Significado |
|---|---|
| Normal | El valor está dentro del rango de referencia del cultivo |
| Por encima del rango | El valor supera el máximo del rango |
| Por debajo del rango | El valor no alcanza el mínimo del rango |
| Sin rango configurado | El cultivo asociado no tiene definido un rango para esa variable |
| Sin lecturas | Esa variable todavía no tiene ninguna medición registrada; el valor se muestra con una raya |

La pantalla de variables se muestra en la Figura A.8.

### 3.7 Registrar una medición a mano

Esta vía es la prevista para cuando la medición se realiza con instrumentos portátiles.

1. En Inicio, pulse Registrar medición, al pie de las tarjetas de variables. Si el módulo todavía no tiene lecturas, el botón se llama Registrar la primera medición y aparece en el centro de la pantalla.
2. En el cuadro Registrar medición, complete únicamente los campos de las variables que haya medido. Los campos que deje vacíos no se envían: no se registra un valor cero, que sería un dato falso. Cada campo muestra como ayuda el rango de referencia vigente de esa variable o el texto Sin rango configurado.
3. Escriba los valores con punto o con coma decimal.
4. Pulse Guardar.
5. El sistema confirma con el aviso Lectura registrada y evaluada por el servidor cuando envió una sola variable, o con N lecturas registradas y evaluadas por el servidor cuando envió varias.
6. El panel se vuelve a consultar: los valores enviados aparecen en sus tarjetas con el estado que les asignó el servidor, y las alertas que correspondan quedan activas.

Para descartar la operación, pulse Cancelar. El cuadro de registro se muestra en la Figura A.9, el aviso de confirmación en la Figura A.10 y el estado vacío con el botón de la primera medición en la Figura A.11.

### 3.8 Ver la evolución de una variable

1. Pulse Historial en la barra inferior.
2. En el desplegable Variable, elija la variable que quiere estudiar.
3. Pulse el botón Inicio: se abre el calendario y elige la fecha desde la que quiere consultar. Mientras no elija una fecha, el botón indica Inicio: Sin seleccionar.
4. Pulse el botón Fin y elija la fecha de cierre. Si no elige ninguna fecha, la consulta abarca todo el historial registrado.
5. Pulse Consultar. El resumen del periodo aparece al pie de la misma pantalla, con la cantidad de mediciones y los valores Promedio, Máximo y Mínimo.
6. Pulse Ver gráfica para ver la evolución del periodo. La gráfica ofrece tres atajos de periodo: 3 meses, 6 meses y 1 año. Si la serie tiene una sola medición, no se traza una línea y el valor se muestra en el resumen.
7. Pulse Mediciones para ver la lista de lecturas del periodo consultado, con la más reciente primero. Cada renglón indica la fecha y la hora, el valor con su unidad, el origen de la lectura (Manual o Automática) y su estado respecto del rango.

La consulta se hace siempre sobre el módulo vigente en el panel de inicio. Si cambia de módulo, el historial se vuelve a consultar con ese módulo.

La pantalla del historial con sus filtros se muestra en la Figura A.12, el resumen de la consulta en la Figura A.13, la gráfica en la Figura A.14 y la lista de mediciones en la Figura A.15.

### 3.9 Atender una alerta

1. Pulse la campana de la barra superior. Sobre el icono figura el número de alertas activas.
2. En la pestaña Activas aparece la lista de alertas, cada una con el título, el valor registrado, el rango del perfil de cultivo y la fecha de la lectura. Los títulos tienen la forma pH por encima del rango, pH por debajo del rango o pH fuera del rango, según de qué lado del rango quedó el valor.
3. Pulse la alerta que va a atender, para abrir su detalle.
4. Revise en el detalle el estado, la variable, el valor registrado, el rango del perfil, la desviación, la fecha de la lectura y la lectura de origen. La lectura de origen es la referencia que conserva la trazabilidad de la alerta.
5. Corrija la causa en el cultivo: ajuste la solución nutritiva, reponga agua, ventile, según corresponda.
6. Pulse Marcar como atendida. El detalle se cierra y la alerta sale de la pestaña Activas para quedar en el historial.
7. Si marcó una alerta como atendida por error, ábrala desde la pestaña Historial y pulse Devolver a alertas activas.

No marque una alerta como atendida sin haber intervenido: el historial de alertas es la memoria del cultivo. Si no hay ninguna alerta registrada, la pantalla muestra el aviso Todavía no hay alertas. El servicio genera una alerta cada vez que una lectura sale del rango de su perfil de cultivo. Si hay alertas pero ninguna activa, la pestaña Activas indica No hay alertas activas; y si todavía no se atendió ninguna, la pestaña Historial indica No hay alertas atendidas todavía.

La pestaña Activas se muestra en la Figura A.16, el detalle de una alerta en la Figura A.17 y la pestaña Historial en la Figura A.18.

### 3.10 Mantener sus datos de perfil

1. Pulse Ajustes en la barra inferior.
2. Pulse Perfil.
3. Revise los datos que se muestran: nombre, cargo, rol, estado de la cuenta, correo, teléfono e identificador de la cuenta. El correo lo administra el proveedor de identidad del sistema.
4. Pulse Editar información.
5. Corrija el nombre, el teléfono y el cargo.
6. Pulse Guardar. El sistema confirma con el aviso Perfil actualizado en el servicio.

El rol y el estado de la cuenta no se modifican desde aquí: son atribuciones de la administración. La pantalla de perfil se muestra en la Figura A.19 y el cuadro de edición en la Figura A.20.

### 3.11 Cambiar el tema y el nombre que se muestra

1. Pulse Ajustes y luego Perfil.
2. Pulse Preferencias de app.
3. Para cambiar el nombre con el que se le saluda en el menú lateral, escríbalo en el campo Tu nombre y pulse Guardar. El sistema confirma con el aviso Nombre guardado localmente.
4. Para alternar el aspecto de la aplicación, use el interruptor Tema oscuro.

La pantalla de preferencias se muestra en la Figura A.21.

## 4. Tareas del Administrador

El Administrador, además de todas las tareas del Operador, configura el sistema: los cultivos con sus rangos de referencia, los módulos de cultivo y las cuentas con sus roles. Las tareas 3.1 a 3.11 de este manual también le corresponden.

### 4.1 Registrar un cultivo con sus rangos de referencia

1. Pulse Cultivos en la barra inferior.
2. Pulse Añadir cultivo.
3. Escriba el nombre del cultivo. Es obligatorio y debe tener dos letras como mínimo.
4. Escriba, si quiere, una descripción.
5. En la lista Rangos de referencia por variable, escriba el mínimo y el máximo de cada variable que conozca. Deje los dos campos vacíos en las variables que todavía no quiera limitar: los rangos vacíos no se envían.
6. Pulse Guardar. El sistema confirma con el aviso Cultivo "nombre" registrado en el servicio.

Las lecturas se evalúan contra los rangos del cultivo asociado al módulo. Mientras un cultivo no tenga rangos, sus lecturas quedan con la etiqueta Sin rango configurado, no se evalúan y no generan alertas. El cuadro de alta de un cultivo se muestra en la Figura A.22.

### 4.2 Completar o corregir los rangos de un cultivo

1. Pulse Cultivos en la barra inferior.
2. Localice el cultivo en la lista. Bajo su nombre figura la cantidad de rangos definidos y el resumen de ellos, o el texto Sin rangos definidos todavía.
3. Pulse el botón de rangos del cultivo, a la derecha de su tarjeta.
4. Corrija o complete lo que corresponda. Los campos muestran los límites vigentes; las variables sin rango quedan vacías para que usted las complete. El nombre y la descripción del cultivo no se modifican aquí.
5. Pulse Guardar. El sistema confirma con el aviso Rangos de "nombre" guardados en el servicio.

El cuadro de rangos de un cultivo se muestra en la Figura A.23.

### 4.3 Ajustar el rango de referencia de una variable

1. Pulse Ajustes en la barra inferior.
2. Pulse Rangos de variables.
3. En el desplegable Cultivo, elija el cultivo cuyos rangos quiere revisar. La opción Todos los cultivos muestra los rangos de todos juntos, indicando en cada renglón a qué cultivo pertenece.
4. Pulse el rango que va a modificar. Se abre el cuadro Rango de nombre de la variable, que indica el cultivo al que pertenece.
5. Escriba el mínimo y el máximo. Los dos deben ser números y el mínimo debe ser menor que el máximo.
6. Pulse Guardar. El sistema confirma con el aviso Rango actualizado en el servicio.

Un cambio de rango se aplica a las lecturas siguientes. Las lecturas ya almacenadas conservan el estado que se les asignó cuando se registraron, igual que las alertas conservan los límites con los que fueron evaluadas. Ajustar un rango es una decisión técnica: un rango mal definido produce alertas falsas o, peor, deja pasar desviaciones reales.

Si el cultivo elegido no tiene ningún rango, la pantalla lo advierte con el texto El cultivo nombre todavía no tiene rangos de referencia e indica dónde definirlos. La lista de rangos se muestra en la Figura A.24 y el cuadro de edición de un rango en la Figura A.25.

### 4.4 Gestionar los módulos de cultivo

1. Pulse Módulo en la barra inferior.
2. Revise la lista. Cada tarjeta muestra el nombre del módulo, su tipo de cultivo, el cultivo asociado, la ubicación y el distintivo Activo o Inactivo.

Para agregar un módulo:

1. Pulse Agregar módulo de cultivo.
2. Escriba el nombre del módulo y su tipo de cultivo.
3. En el desplegable Cultivo, elija el cultivo cuyos rangos se aplicarán a las lecturas de este módulo.
4. Escriba, si quiere, la ubicación.
5. Pulse Guardar. El sistema confirma con el aviso Módulo registrado en el servicio.

Para modificar un módulo:

1. Pulse el icono de tres puntos verticales de su tarjeta, para abrir el menú de acciones del módulo.
2. Pulse Editar módulo, corrija los datos y pulse Guardar cambios. El sistema confirma con el aviso Módulo modificado en el servicio.

Para activar o desactivar un módulo:

1. Abra el menú de acciones de la tarjeta.
2. Pulse Desactivar módulo o Activar módulo, según el estado que tenga. La tarjeta cambia su distintivo en el acto.

Para eliminar un módulo:

1. Abra el menú de acciones de la tarjeta.
2. Pulse Eliminar módulo.
3. Lea el aviso de confirmación: El módulo se eliminará del servicio. Si tiene lecturas registradas, la operación será rechazada para no perder el historial.
4. Pulse Eliminar. El sistema confirma con el aviso Módulo eliminado del servicio.

Si el módulo tiene lecturas registradas, el servicio rechaza la eliminación. En ese caso, desactive el módulo en lugar de eliminarlo: así se conserva el historial del cultivo. Si todavía no existe ningún cultivo registrado, el alta de módulos avisa con el texto Primero debe existir un perfil de cultivo con sus rangos.

La pantalla de módulos se muestra en la Figura A.26, el cuadro de alta o edición en la Figura A.27 y el aviso de confirmación de eliminación en la Figura A.28.

### 4.5 Gestionar los usuarios y sus roles

Esta tarea solo está disponible para una cuenta con rol de Administrador.

1. Pulse Ajustes en la barra inferior.
2. Pulse Usuarios (admin). Esta opción no aparece en las cuentas de Operador.
3. Revise la lista de cuentas. Cada tarjeta muestra el nombre y el correo, el rol, el cargo y el teléfono, y el distintivo Inactiva cuando la cuenta está desactivada. La tarjeta de su propia cuenta lleva, además, el distintivo Su cuenta.

Para corregir los datos de una cuenta:

1. Pulse el icono de edición de la tarjeta.
2. Corrija el nombre, el teléfono y el cargo.
3. Pulse Guardar. El sistema confirma con el aviso Datos actualizados.

Para cambiar el rol de una cuenta:

1. Pulse el icono de cambio de rol de la tarjeta.
2. Confirme en el aviso, que indica el correo y el rol actual y el nuevo.
3. Pulse Confirmar. El sistema confirma con el aviso Rol actualizado a nombre del rol.

Para activar o desactivar una cuenta:

1. Pulse el icono del ojo de la tarjeta.
2. El sistema confirma con el aviso Cuenta desactivada o Cuenta activada, según corresponda.

Una cuenta desactivada no puede operar sobre el sistema, pero su registro se conserva. Es la vía recomendada cuando alguien deja de participar del cultivo, en lugar de eliminar su perfil.

Para eliminar el perfil de una cuenta:

1. Pulse el icono del cesto de basura de la tarjeta.
2. Lea el aviso de confirmación y pulse Eliminar. El sistema confirma con el aviso Perfil eliminado. La credencial de acceso permanece en el proveedor de identidad.

Sobre su propia cuenta, los botones de cambiar el rol, activar o desactivar y eliminar quedan deshabilitados: el servicio rechaza esas operaciones para que la administración no pueda quitarse a sí misma las atribuciones ni dejar el sistema sin quien lo administre. La pantalla de usuarios se muestra en la Figura A.29, el cuadro de edición de datos en la Figura A.30 y la confirmación de cambio de rol en la Figura A.31.

### 4.6 Eliminar un cultivo

1. Pulse Cultivos en la barra inferior.
2. Pulse el botón del cesto de basura de la tarjeta del cultivo que va a eliminar.
3. Lea el aviso: Se eliminará el cultivo y sus N rangos de referencia. Los módulos que lo tuvieran asociado quedarían sin rangos para evaluar sus lecturas.
4. Si está de acuerdo, pulse Eliminar. El sistema confirma con el aviso Cultivo eliminado del servicio.

La confirmación de eliminación de un cultivo se muestra en la Figura A.32.

## 5. Qué puede hacer cada rol

El sistema reconoce tres roles: Administrador, Operador e Invitado. El rol de Invitado existe en el catálogo del sistema como rol de solo consulta, pero no se asigna desde la pantalla de usuarios.

### 5.1 Tareas del Administrador

1. Iniciar sesión y cerrar sesión.
2. Crear su propia cuenta desde la pantalla de acceso.
3. Consultar el estado del cultivo en el panel de inicio.
4. Cambiar el módulo de cultivo que se consulta.
5. Revisar el estado de las seis variables y sus etiquetas.
6. Registrar mediciones a mano.
7. Consultar la evolución de una variable en el historial, con su resumen, su gráfica y su lista de mediciones.
8. Atender alertas y devolver al estado activo una alerta atendida por error.
9. Mantener sus propios datos de perfil.
10. Cambiar el tema y el nombre con el que se le saluda.
11. Registrar un cultivo con sus rangos de referencia.
12. Completar o corregir los rangos de un cultivo.
13. Ajustar el rango de referencia de una variable.
14. Registrar, modificar, activar, desactivar y eliminar módulos de cultivo.
15. Ver la lista de cuentas registradas con su rol y su estado.
16. Corregir los datos de contacto de cualquier cuenta.
17. Cambiar el rol de una cuenta entre Administrador y Operador.
18. Activar y desactivar cuentas.
19. Eliminar el perfil de una cuenta.
20. Eliminar un cultivo con sus rangos de referencia.

### 5.2 Tareas del Operador

1. Iniciar sesión y cerrar sesión.
2. Crear su propia cuenta desde la pantalla de acceso.
3. Consultar el estado del cultivo en el panel de inicio.
4. Cambiar el módulo de cultivo que se consulta.
5. Revisar el estado de las seis variables y sus etiquetas.
6. Registrar mediciones a mano.
7. Consultar la evolución de una variable en el historial, con su resumen, su gráfica y su lista de mediciones.
8. Atender alertas y devolver al estado activo una alerta atendida por error.
9. Mantener sus propios datos de perfil.
10. Cambiar el tema y el nombre con el que se le saluda.

### 5.3 Tareas que el Operador no puede realizar

1. Registrar, modificar, activar, desactivar o eliminar módulos de cultivo.
2. Registrar, modificar o eliminar cultivos y sus rangos de referencia.
3. Ajustar los rangos de referencia de una variable.
4. Ver la lista de cuentas del sistema.
5. Corregir datos de otras cuentas.
6. Cambiar el rol de una cuenta.
7. Activar, desactivar o eliminar cuentas.
8. Eliminar cultivos.

La opción Usuarios (admin) de Ajustes no se muestra en las cuentas de Operador. En las operaciones que el servicio reserva a la administración, el rechazo lo determina el servidor: aunque una pantalla ofreciera el botón, la operación no se autoriza.

## 6. Mensajes del sistema y qué hacer

Los mensajes que se listan a continuación son los que la aplicación muestra en pantalla. Se agrupan por el momento en que aparecen.

### 6.1 Mientras la información está en camino

| Mensaje | Qué significa | Qué debe hacer usted |
|---|---|---|
| Cargando información… | La aplicación pidió los datos al servidor y todavía no llegaron | Espere. La primera consulta después de un periodo sin uso puede demorar porque el servicio se suspende por inactividad |
| Cargando... | La pantalla de presentación está comprobando si hay una sesión iniciada | Espere unos segundos |
| Procesando... | El botón de acceso está ejecutando el inicio de sesión o el registro | No pulse el botón otra vez; espere el resultado |

### 6.2 Cuando la operación no llega a completarse

| Mensaje | Qué significa | Qué debe hacer usted |
|---|---|---|
| No se pudo conectar con el servidor | La petición no llegó al servidor. Es un fallo de conexión, no un rechazo | Revise la conexión e intente nuevamente con el botón Reintentar |
| La petición no llegó al servidor. | Detalle del caso anterior | Igual que el anterior |
| La operación no pudo completarse | El servidor recibió la petición y la rechazó | Corrija el dato señalado. Si el problema continúa, comuníquese con la administración. Reintentar no lo resuelve por sí solo |
| El servidor rechazó la operación. | Detalle del caso anterior | Igual que el anterior |
| La operación no pudo completarse (código NNN). | El servidor respondió con un error sin detalle. El número es el código de la respuesta | Anote el código y consulte con la administración |
| No se pudo comunicar con el servidor. Revise la conexión e intente nuevamente. (detalle: …) | Fallo de conexión con el detalle técnico del caso: tiempo agotado, conexión rechazada o sesión no disponible | Revise la red y pulse Reintentar. El detalle sirve para informar el problema si persiste |
| La respuesta del servidor no pudo interpretarse. Vuelva a intentarlo. (detalle: …) | La respuesta llegó con una forma distinta a la esperada | Pulse Reintentar. Si se repite, comuníquese con la administración |
| Ocurrió un error no previsto. Vuelva a intentarlo. (detalle: …) | La aplicación no pudo clasificar el fallo | Pulse Reintentar y, si se repite, comuníquese con la administración |
| Sin información / El servicio no devolvió datos para esta consulta. | La consulta se completó pero llegó vacía donde se esperaba un contenido | Pulse Reintentar y, si se repite, comuníquese con la administración |
| No hay una sesión iniciada. | Se intentó una operación sin sesión válida | Vuelva a iniciar sesión |

### 6.3 Al iniciar sesión y al crear la cuenta

| Mensaje | Qué significa | Qué debe hacer usted |
|---|---|---|
| Correo o contraseña incorrectos. | El correo no está registrado o la contraseña no coincide | Verifique lo que escribió. Si no recuerda la contraseña, consulte con la administración |
| Ya existe una cuenta con ese correo. | Se intentó registrar un correo que ya tiene cuenta | Inicie sesión con ese correo o use otro |
| La contraseña es demasiado débil. | La contraseña no alcanza la longitud mínima exigida por el proveedor de identidad | Use una contraseña más larga y menos previsible |
| La cuenta fue deshabilitada. | La cuenta existe, pero la administración la desactivó | Comuníquese con la administración |
| Demasiados intentos. Espera un momento y vuelve a intentar. | El proveedor de identidad bloqueó temporalmente los intentos por su cantidad | Espere unos minutos y vuelva a intentar |
| El registro con correo no está habilitado en Firebase. | El proveedor de identidad no admite el registro con correo y contraseña en esta instalación | Comuníquese con la administración: el alta de cuentas no está disponible |
| No se pudo completar la acción. Código: código | El proveedor de identidad devolvió un error no previsto | Anote el código y consulte con la administración |
| Cuenta creada y sesion iniciada. | El registro se completó y la sesión quedó abierta | Continúe con la tarea que necesitaba |
| Tu sesión venció. Volvé a iniciar sesión. | El servicio rechazó la sesión porque el token de identidad venció o fue revocado | Vuelva a iniciar sesión. No se pierde información: los datos están en el servidor |
| Ingresa tus nombres | Quedó vacío el campo obligatorio Nombres en el registro | Escriba sus nombres |
| Correo invalido | El campo Usuario no contiene el símbolo arroba | Escriba el correo completo |
| Minimo 6 caracteres | La contraseña escrita tiene menos de seis caracteres | Escriba una contraseña de seis caracteres como mínimo |

### 6.4 En el panel de inicio y en las variables

| Mensaje | Qué significa | Qué debe hacer usted |
|---|---|---|
| Sistema normal. Todo dentro del rango óptimo | Todas las variables tienen su último valor dentro del rango de referencia | No requiere acción. Verifique la última actualización antes de decidir |
| Sistema con alertas. Algunos parámetros están fuera de rango | Al menos una variable salió de su rango y tiene una alerta activa | Abra la campana y atienda las alertas |
| Última actualización: Sin lecturas | El módulo vigente todavía no tiene ninguna medición registrada | Registre la primera medición o espere el envío del módulo de adquisición |
| Lectura registrada y evaluada por el servidor | Se registró una sola medición manual y el servidor ya la evaluó | Verifique el resultado en las tarjetas de variables |
| N lecturas registradas y evaluadas por el servidor | Se registraron varias mediciones manuales en una sola operación | Verifique los valores y las alertas que se hayan generado |
| No hay módulos de cultivo activos. Cree uno en la sección Cultivos para comenzar a registrar variables. | No existe ningún módulo activo, de modo que no hay nada que evaluar | Registre un módulo de cultivo y actívelo |
| El módulo nombre todavía no tiene lecturas registradas. Registre la primera medición o espere el envío del módulo de adquisición. | El módulo existe y está activo, pero no tiene mediciones | Pulse Registrar la primera medición |
| El módulo todavía no tiene lecturas registradas. Registre la primera medición desde el panel principal. | El mismo caso, en la sección Variables | Vaya a Inicio y registre la primera medición |
| Complete únicamente las variables que haya medido. El servidor evaluará cada valor contra su rango de referencia. | Indicación del cuadro de registro de medición | Complete solo los campos que midió; deje el resto vacío |
| mensaje del servidor, seguido de Revise: variable, variable. | El servidor rechazó el valor de una o más variables y señala cuáles | Corrija los campos indicados y vuelva a registrar |
| Sin rango configurado | El cultivo asociado al módulo no tiene rango definido para esa variable | Si corresponde, defina el rango desde Ajustes, como se describe en la tarea 4.3 |
| Normal | El valor está dentro del rango | No requiere acción |
| Por encima del rango | El valor supera el máximo del rango | Revise el cultivo y atienda la alerta correspondiente |
| Por debajo del rango | El valor no alcanza el mínimo del rango | Revise el cultivo y atienda la alerta correspondiente |
| Sin lecturas | La variable todavía no tiene ninguna medición | Registre una medición de esa variable |

### 6.5 En alertas

| Mensaje | Qué significa | Qué debe hacer usted |
|---|---|---|
| Todavía no hay alertas. El servicio genera una alerta cada vez que una lectura sale del rango de su perfil de cultivo. | No hay ninguna alerta registrada, ni activa ni atendida | Verifique que el cultivo asociado al módulo tenga rangos definidos |
| No hay alertas activas | Hay alertas registradas, pero todas están atendidas | Revise la pestaña Historial si necesita consultarlas |
| No hay alertas atendidas todavía | Ninguna alerta se marcó como atendida | Atienda las alertas de la pestaña Activas después de corregir la causa |
| variable por encima del rango | El valor superó el máximo del rango del cultivo | Corrija la causa y marque la alerta como atendida |
| variable por debajo del rango | El valor no alcanzó el mínimo del rango del cultivo | Corrija la causa y marque la alerta como atendida |
| variable fuera del rango | El servidor no clasificó la desviación | Revise el valor y el rango en el detalle de la alerta |
| Valor registrado: valor unidad. Rango del perfil: mínimo – máximo unidad | Los datos con los que se generó la alerta | Compárelos con el estado actual del cultivo |
| Desviación: Sin clasificar | El servidor no clasificó la desviación de esa alerta | Revise el valor y el rango en el detalle |
| No aparece ningún aviso al atender una alerta | La pantalla se cierra y las dos listas se vuelven a consultar al servicio | Compruebe que la alerta ya figura en la pestaña Historial. Si la operación falla, sí aparece el mensaje del servidor |

### 6.6 En módulos, cultivos y rangos

| Mensaje | Qué significa | Qué debe hacer usted |
|---|---|---|
| No hay módulos de cultivo registrados. Cree uno para comenzar a registrar variables. | La lista de módulos está vacía | Pulse Agregar módulo de cultivo |
| Primero debe existir un perfil de cultivo con sus rangos. | Se intentó registrar un módulo y no hay ningún cultivo al que asociarlo | Registre primero un cultivo con sus rangos, como se describe en la tarea 4.1 |
| Escriba el nombre del módulo. | Quedó vacío el nombre al guardar un módulo | Escriba el nombre |
| Escriba el tipo de cultivo. | Quedó vacío el tipo de cultivo al guardar un módulo | Escriba el tipo de cultivo |
| Módulo registrado en el servicio. | El alta del módulo se completó | Verifique que aparezca en la lista y en el selector del panel |
| Módulo modificado en el servicio. | La modificación del módulo se completó | Verifique los datos en la tarjeta |
| Módulo eliminado del servicio. | La eliminación del módulo se completó | No requiere acción |
| El módulo se eliminará del servicio. Si tiene lecturas registradas, la operación será rechazada para no perder el historial. | Aviso previo a eliminar un módulo | Pulse Eliminar solo si el módulo no tiene historial que conservar; si lo tiene, desactívelo |
| Todavía no hay cultivos registrados. Registre el primero con su nombre y sus rangos de referencia. | La lista de cultivos está vacía | Pulse Añadir cultivo |
| Escriba el nombre del cultivo (dos letras como mínimo). | El nombre del cultivo es demasiado corto | Escriba un nombre de dos letras como mínimo |
| Complete el mínimo y el máximo de variable, o deje los dos campos vacíos. | Se completó solo uno de los dos límites de una variable | Complete los dos límites o borre el que escribió |
| En variable el mínimo debe ser menor que el máximo. | Los límites escritos están invertidos o son iguales | Corrija los valores |
| El nombre del cultivo no se modifica aquí | El nombre del cultivo se muestra solo como referencia al corregir sus rangos | Corrija únicamente los límites |
| Cultivo "nombre" registrado en el servicio. | El alta del cultivo se completó | Defina o revise sus rangos |
| Rangos de "nombre" guardados en el servicio. | La corrección de rangos se completó | Verifique el resumen en la tarjeta del cultivo |
| Cultivo eliminado del servicio. | La eliminación del cultivo y de sus rangos se completó | Los módulos que lo tuvieran asociado quedan sin rangos para evaluar sus lecturas |
| Se eliminará el cultivo y sus N rangos de referencia. Los módulos que lo tuvieran asociado quedarían sin rangos para evaluar sus lecturas. | Aviso previo a eliminar un cultivo | Confirme solo si ningún módulo depende de ese cultivo |
| El cultivo todavía no tiene rangos de referencia definidos. | El servicio no devolvió ningún rango de referencia | Registre los rangos del cultivo |
| El cultivo nombre todavía no tiene rangos de referencia | El cultivo elegido no tiene ningún rango | Defínalos desde Ajustes, en Cultivos, con el botón de rangos de ese cultivo |
| Escriba los dos límites como números. | Uno de los límites escritos no es un número | Corrija los valores |
| El mínimo debe ser menor que el máximo. | Los límites escritos están invertidos o son iguales | Corrija los valores |
| Rango actualizado en el servicio. | El cambio de rango se completó | Recuerde que se aplica a las lecturas siguientes |

### 6.7 En el historial

| Mensaje | Qué significa | Qué debe hacer usted |
|---|---|---|
| Elija la variable y el rango de fechas, y pulse Consultar para ver el resumen del periodo. | Todavía no se hizo ninguna consulta en esta pantalla | Pulse Consultar |
| Sin rango se consulta todo el historial registrado. | No se eligió ninguna fecha | Elija las fechas si quiere acotar el periodo |
| Inicio: Sin seleccionar, Fin: Sin seleccionar | Todavía no se eligió esa fecha | Pulse el botón y elija la fecha en el calendario |
| La fecha de inicio es posterior a la de fin: corrija el rango antes de consultar. | El rango de fechas elegido está invertido | Corrija una de las dos fechas |
| Sin mediciones en el periodo. No hay mediciones de esta variable en el rango elegido. Amplíe el rango o registre una medición. | La consulta se completó y no hay lecturas de esa variable en el periodo | Amplíe el periodo o registre una medición |
| Sin mediciones en el periodo. No hay mediciones de variable en el rango elegido. | El mismo caso, en la lista de mediciones | Amplíe el periodo |
| Sin mediciones en el periodo. No hay mediciones de esta variable en el rango elegido. Pruebe con un periodo más amplio. | El mismo caso, en la gráfica | Pulse 3 meses, 6 meses o 1 año |
| Con una sola medición no se puede trazar una línea; se muestra su valor en el resumen. | El periodo tiene un único dato | Amplíe el periodo si necesita ver la tendencia |
| Se muestra 1 medición: hacen falta al menos dos para trazar la línea. | El mismo caso, con el conteo a la vista | Igual que el anterior |
| Serie de N mediciones, de la más antigua a la más reciente. | La gráfica se trazó con esa cantidad de puntos | No requiere acción |
| Todo el historial registrado | La gráfica abarca todas las lecturas, sin filtro de fechas | Elija un periodo si quiere acotarlo |
| Resumen del periodo (N mediciones) | Cantidad de lecturas con las que el servidor calculó el resumen | No requiere acción |
| El servicio no devolvió el resumen del periodo. | Llegaron las mediciones, pero no el resumen calculado | Pulse Reintentar |
| Manual | La lectura la registró una persona desde la aplicación | No requiere acción |
| Automática | La lectura la envió el módulo de adquisición | No requiere acción |

### 6.8 En perfil, preferencias y usuarios

| Mensaje | Qué significa | Qué debe hacer usted |
|---|---|---|
| Perfil actualizado en el servicio. | La corrección de sus datos se completó | No requiere acción |
| La cuenta todavía no tiene un perfil registrado. | El servicio no devolvió el perfil de la cuenta | Pulse Reintentar y, si se repite, consulte con la administración |
| El rol y el estado de la cuenta los administra el servicio: no se modifican desde aquí. | Indicación del cuadro de edición del perfil | Solicite el cambio a la administración |
| Nombre guardado localmente | El nombre de saludo se guardó en el dispositivo | No requiere acción |
| La cuenta con la que inició sesión no tiene atribuciones de administración. | El servicio rechazó la consulta de cuentas por falta de rol | Solicite el rol de Administrador |
| No se pudo obtener la lista de cuentas | La consulta de cuentas no se completó | Pulse Reintentar |
| Todavía no hay cuentas registradas. | La lista llegó vacía | No requiere acción |
| Datos actualizados. | La corrección de los datos de una cuenta se completó | No requiere acción |
| No se pudo actualizar: mensaje del servidor | La corrección de datos fue rechazada | Corrija lo que el mensaje señale |
| Rol actualizado a nombre del rol. | El cambio de rol se completó | La cuenta lo verá al volver a abrir el menú lateral |
| No se pudo cambiar el rol: mensaje del servidor | El cambio de rol fue rechazado | Verifique que no se trate de su propia cuenta |
| Cuenta desactivada. Cuenta activada. | El cambio de estado de la cuenta se completó | No requiere acción |
| No se pudo cambiar el estado: mensaje del servidor | El cambio de estado fue rechazado | Verifique que no se trate de su propia cuenta |
| Perfil eliminado. | El perfil de la cuenta se quitó del sistema | No requiere acción |
| No se pudo eliminar: mensaje del servidor | La eliminación del perfil fue rechazada | Verifique que no se trate de su propia cuenta |
| Cambiar rol: ¿Cambiar a correo de "rol actual" a "rol nuevo"? | Confirmación previa al cambio de rol | Pulse Confirmar para continuar o Cancelar para desistir |
| Eliminar cuenta: ¿Eliminar el perfil de correo? Esto lo quita del sistema. La credencial de Firebase Authentication permanece, porque eliminarla exige privilegios de administración del proveedor que no están en el alcance. | Confirmación previa a eliminar un perfil | Confirme solo si la persona deja de participar del cultivo; si es temporal, desactive la cuenta |
| Inactiva | La cuenta está desactivada y no puede operar | Actívela si debe volver a operar |
| Su cuenta | El renglón corresponde a la cuenta con la que inició sesión | Los botones de rol, estado y eliminación están deshabilitados en ese renglón |

## 7. Preguntas frecuentes

El valor que veo no es el actual. Revise Última actualización en la pantalla de Inicio. Si es antigua, el módulo de adquisición puede estar sin conexión o sin energía, o puede faltar registrar la medición del día.

Aparece una alerta que no corresponde. Verifique el rango configurado para esa variable en Ajustes, en Rangos de variables: puede estar más estrecho que el valor real de operación del cultivo. Ajustarlo con criterio agronómico.

Una variable muestra la etiqueta Sin rango configurado. El cultivo asociado al módulo no tiene definido el mínimo y el máximo de esa variable. Mientras no los tenga, sus lecturas no se evalúan y no generan alertas.

No puedo eliminar un módulo. Tiene lecturas registradas y el servicio rechaza la eliminación para no perder el historial. Desactívelo en lugar de eliminarlo.

No veo la opción Usuarios. Esa opción es exclusiva del rol de Administrador.

No veo la opción Usuarios y antes sí la veía. Verifique en el menú lateral el rol que muestra junto a su nombre. Si dice Operador, el rol de administración se retiró de su cuenta; solicítelo a quien administra el sistema.

No puedo cambiar mi propio rol ni desactivar mi cuenta. El servicio lo impide para que la administración no se quite a sí misma las atribuciones. Pida a otra cuenta con rol de Administrador que haga el cambio.

El sistema pide reintentar una y otra vez. Compruebe la conexión. Si otras aplicaciones funcionan, el servicio puede estar reiniciándose: espere unos segundos y vuelva a intentar. La primera consulta después de un periodo de inactividad demora más que las siguientes.

Cerré la sesión sin querer. Vuelva a iniciarla con su correo y contraseña. No se pierde información: los datos están en el servidor, no en el teléfono.

Consulté el historial y no aparece ninguna medición. Compruebe el módulo vigente en el panel de inicio: el historial consulta únicamente las lecturas de ese módulo. Después amplíe el rango de fechas o pulse el atajo de 3 meses, 6 meses o 1 año.

La gráfica no muestra una línea. Con una sola medición no se puede trazar una línea; el valor aparece en el resumen del periodo. Amplíe el periodo para obtener más puntos.

Cambié el rango de una variable y las lecturas anteriores siguen con su estado anterior. Es el comportamiento previsto: un cambio de rango se aplica a las lecturas siguientes. Las ya almacenadas conservan el estado que se les asignó cuando se registraron, para que el historial refleje lo que efectivamente ocurrió.

Marqué una alerta como atendida y no era así. Abra la pestaña Historial de la pantalla de Alertas, entre en la alerta y pulse Devolver a alertas activas.

¿Puedo usar el sistema sin conexión? No. La aplicación consulta y registra contra el servidor. Sin conexión informa el problema y ofrece reintentar.

Registré una medición y no se generó ninguna alerta. Puede ocurrir por dos motivos: el valor quedó dentro del rango, o el cultivo asociado al módulo no tiene rango definido para esa variable. Consulte la etiqueta de la variable.

¿Qué diferencia hay entre módulo y cultivo? El módulo es la instalación física donde están los sensores; el cultivo es la especie sembrada en él y define los rangos de referencia. Un módulo se asocia a un cultivo y sus lecturas se evalúan contra los rangos de ese cultivo.

## 8. Glosario de las variables gestionadas

| Variable | Unidad | Qué mide y por qué importa |
|---|---|---|
| pH | Sin unidad, de 0 a 14 | Acidez o alcalinidad de la solución nutritiva. Fuera de su rango, las raíces no pueden absorber algunos nutrientes aunque estén presentes |
| Sólidos disueltos totales (TDS) | ppm | Estimación de la concentración de sales a partir de la conductividad. Se usa para dosificar los nutrientes |
| Conductividad eléctrica (EC) | mS/cm | Concentración de sales disueltas: indica si la solución está demasiado diluida o demasiado concentrada |
| Temperatura de la solución nutritiva | °C | Afecta la absorción de agua y nutrientes y la disponibilidad de oxígeno en la raíz |
| Temperatura ambiental | °C | Condiciona el crecimiento y la transpiración de la planta |
| Humedad relativa | % | Influye en la transpiración y en el riesgo de enfermedades foliares |

## 9. Buenas prácticas de uso

1. Registrar con regularidad. Un historial con huecos explica poco. Lo importante no es la frecuencia exacta, sino que sea constante.
2. Revisar la última actualización antes de decidir. Un valor sin fecha no es información.
3. Atender las alertas con una intervención real. Marcar una alerta como atendida sin haber corregido la causa convierte el historial en un registro poco confiable.
4. Justificar los cambios de rango. Un cambio de rango modifica la evaluación de las lecturas siguientes; conviene dejar constancia de por qué se hizo.
5. No compartir cuentas. Cada persona debe usar la suya: los roles y la trazabilidad dependen de ello.
6. Comprobar el módulo vigente antes de registrar o consultar. Las mediciones se registran, y el historial se consulta, sobre el módulo que el panel de inicio tiene seleccionado.
7. Dejar los campos vacíos cuando no se midió esa variable. Un valor inventado o copiado de otro día contamina el historial y puede generar alertas falsas.
8. Desactivar en lugar de eliminar. Cuando un módulo deja de usarse o una persona deja de participar, la desactivación conserva la información; la eliminación no se puede deshacer.
9. Consultar el historial al cerrar un ciclo de cultivo. El resumen del periodo, con su promedio, su máximo y su mínimo, permite comparar un ciclo con el siguiente.

---

Fuente: elaboración propia.
