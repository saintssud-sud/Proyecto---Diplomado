# 29 · El WiFi del módulo: señal, distancias y recomendaciones

**Para qué sirve.** El módulo de adquisición es el único componente del sistema que depende de la
red inalámbrica, y en la práctica resultó ser su punto más flojo: en el lugar donde está montado
recibe entre −73 y −78 dBm, que es una señal al límite. Este documento reúne lo que hay que saber
para ubicarlo bien, entender los valores que informa y decidir cuándo hace falta un repetidor.

---

## 1. Lo primero: el ESP32 sólo usa 2,4 GHz

El ESP32 clásico (el de este proyecto) **no ve las redes de 5 GHz**. Si el router tiene las dos
bandas con el mismo nombre, se conecta a la de 2,4; si el nombre es distinto, hay que usar el de
2,4. Y si el punto de acceso del teléfono está en 5 GHz, el módulo directamente no lo encuentra:
es el error que nos costó una tarde.

**Cómo darse cuenta:** el módulo informa «Conectando a la red …» y después nada. No hay estado de
conexión, ni error de clave, ni IP. Sencillamente no la encuentra.

---

## 2. La escala de señal, en dBm

El módulo informa la potencia recibida en **dBm**, que siempre es un número negativo. **Cuanto más
cerca de cero, mejor.** Estos son los valores de referencia:

| Valor | Calidad | Qué se puede esperar |
|---|---|---|
| −30 dBm | Excepcional | Prácticamente pegado al router |
| −50 dBm | Excelente | Cualquier uso, sin sobresaltos |
| −60 dBm | Muy bueno | Enlace estable y rápido |
| −67 dBm | Bueno | Fiable para un equipo que publica datos |
| **−70 dBm** | **Aceptable** | **Mínimo recomendable para este proyecto** |
| −75 dBm | Débil | Funciona, pero se corta y vuelve |
| −80 dBm | Muy débil | Se desconecta seguido; publica con retraso |
| −85 dBm | Malísima | Casi no sostiene la conexión |
| −90 dBm | En el límite | En la práctica, inutilizable |

**Dos reglas que ayudan a calcular de cabeza:**

- Cada **6 dB** que se pierden equivalen a **la mitad de la distancia**. O sea: duplicar la
  distancia al router cuesta unos 6 dB.
- Cada **10 dB** son **diez veces menos potencia**.

En el montaje actual, el módulo está entre −73 y −78 dBm. Traducido: funciona, publica y no pierde
datos, pero la conexión se cae cada tanto. Con −65 o mejor dejaría de ser un problema.

---

## 3. Distancia y obstáculos

La distancia importa, pero **los obstáculos importan más**. Valores aproximados en interiores:

| Situación | Alcance típico |
|---|---|
| Misma habitación, a la vista | 30 a 40 m |
| Misma habitación, con muebles | 15 a 25 m |
| **Una pared interior de por medio** | **8 a 12 m** |
| Dos paredes | 4 a 6 m |
| Tres paredes, o un piso de diferencia | 2 a 4 m |

Nuestro caso encaja exactamente en la tercera fila: **8 o 10 metros y una pared**, que da −74 dBm.
No es que el equipo esté mal: es que esa combinación es la que la física permite.

**Lo que más atenúa la señal, de peor a mejor:**

1. **Metal**: estanterías, gabinetes, chapas, el propio chasis de la computadora. Refleja la señal.
2. **Paredes de ladrillo o concreto con hierro**: cada una cuesta entre 10 y 20 dB.
3. **Agua**: absorbe el 2,4 GHz. Un acuario, un tanque, o el balde de la maqueta cerca de la antena.
4. **Estar debajo de una mesa**: la madera tapa y el equipo alrededor también.
5. **Interferencia**: microondas, teléfonos inalámbricos, Bluetooth y las redes de los vecinos.

---

## 4. Dónde está la antena del módulo

El ESP32 tiene la antena **impresa en la placa**, en uno de sus extremos: el **opuesto al conector
USB**. Es una antena de PCB, así que necesita aire.

Tres reglas:

- **Dejá libre ese extremo.** Que no quede tapado por el protoboard, ni por cables, ni por la tapa
  de una caja.
- **No lo apoyes sobre metal.** Una superficie metálica debajo arruina la antena.
- **Orientá ese extremo hacia el router.** Es gratis y a veces son varios dB.

---

## 5. Qué hacer para mejorarla, en orden de esfuerzo

| # | Medida | Cuánto ayuda |
|---|---|---|
| 1 | **Sacar el módulo de abajo de la mesa** y subirlo a la superficie | Bastante: la madera y el equipo son el primer obstáculo |
| 2 | **Alejar los cables** del extremo de la antena (USB y dupont) | Poco, pero gratis |
| 3 | **Orientar la antena** hacia el router | Poco, pero gratis |
| 4 | **Fijar el canal del router en 1, 6 u 11** y ancho de 20 MHz | Medio: evita pisarse con los vecinos |
| 5 | **Poner un repetidor a mitad de camino** | Mucho: es la solución de fondo |
| 6 | **Usar el punto de acceso del teléfono** al lado del módulo | Muchísimo, y sirve para la defensa |

**Recomendación concreta:** para el trabajo diario, un repetidor. Para la defensa, el punto de
acceso del teléfono: en el aula no se sabe cómo llega la red hasta la mesa, y con el teléfono el
problema desaparece.

---

## 6. Una mejora que queda pendiente en el firmware

El firmware deja el ahorro de energía del WiFi activado, que es lo que viene por defecto:

```
I (5884) wifi:pm start, type: 1
```

Con una señal débil, ese ahorro hace que el módulo duerma la radio entre transmisiones, y entonces
**pierde más paquetes y se desconecta más seguido**. Para un equipo enchufado a la corriente no
tiene sentido ahorrar: conviene desactivarlo con una línea,

```c
esp_wifi_set_ps(WIFI_PS_NONE);
```

antes de conectar. Es un cambio de una línea y es lo primero que probaría cuando la señal está al
límite. Queda anotado como pendiente.

---

## 7. Cómo consultar la señal en cualquier momento

El dato aparece en el registro del módulo cada vez que se conecta:

```
I (7184) wifi:connected with <red>, channel 4, BW20, rssi = -74
```

Para verlo cuando se quiera, alcanza con apretar **EN/RST** en la placa y escuchar el arranque: en
la primera línea de conexión aparece el valor. Con eso se puede comparar antes y después de mover
el módulo, sin adivinar.

De paso, ese mismo arranque informa el **canal** (`channel 4`) y el ancho de banda (`BW20`): sirve
para saber si el router está en un canal poco conveniente.

---

## 8. Y una tranquilidad: la red floja ya no cuesta datos

Desde el 2 de octubre, el firmware hace dos cosas que cambian el panorama:

1. **Reintenta con espera de quince segundos**, en lugar de insistir cada dos o tres. Los routers
   bloquean al cliente que insiste así, y el módulo quedaba en un bucle sin salida.
2. **Guarda el ciclo en memoria** cuando no hay red, en vez de descartarlo. Se publica cuando
   vuelve la conexión, con la hora en que se midió.

Resultado: con la señal al límite, lo que se pierde es **la puntualidad**, no los datos. El registro
del 2 de octubre lo mostró en vivo: el módulo acumuló once lecturas esperando red y después las
publicó todas.
