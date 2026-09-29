# 25 · Guía para soldar la resistencia del AM2302

La resistencia de *pull-up* del AM2302 (4,7 kΩ) va **entre el cable rojo (3,3 V) y el
cable amarillo (datos)**, con los dos cables **enteros**: la resistencia se cuelga en
paralelo, no se corta ningún cable para ponerla en serie.

Sirve para que la línea de datos tenga un nivel alto firme cuando el sensor no habla.
Sin ella, o mal soldada, el firmware avisa:

```
dht: Initialization error, problem in phase 'B'
```

Ese mensaje significa que la línea se quedó en alto: el sensor no está en ese pin, no
está alimentado, o el pull-up no está haciendo contacto.

Figura de apoyo: `Figuras/22-soldadura-del-pullup.png` (copia en
`Modulo ESP32/Cableado/22-soldadura-del-pullup.png`).

---

## 1. Lo que hay que evitar

| Error | Qué pasa |
| --- | --- |
| Soldar sobre el aislante | El estaño se pega al plástico, el plástico se derrite y queda una banda blanquecina. Puede marcar continuidad en la mesa y fallar en cuanto se mueve el cable. |
| No pasar el termorretráctil antes | El tubo ya no entra por la unión. Con los extremos libres todavía se puede pasar desde una punta; con los cables ya conectados a la placa, no. |
| Cortar el cable para empalmar | Queda el sensor en serie: no funciona. La resistencia es un puente entre los dos cables. |
| Calentar más de 2 o 3 segundos | El aislante se derrite y el cobre se oxida: el estaño no agarra nunca. |
| Unión fría (gris opaca y grumosa) | No conduce bien. Se corrige recalentando y añadiendo un poco de estaño. Una unión buena queda **brillante y lisa**. |

## 2. Materiales

- Soldador y estaño.
- La resistencia de 4,7 kΩ (amarillo, violeta, rojo: 4-7-×100 = 4 700 Ω).
- Termorretráctil de 2 a 4 mm, dos trozos de 15 mm. Si no hay, sirve **cinta aislante**
  de PVC (ver el apartado 3.1).
- Multímetro.
- Pinza o "tercera mano" para sujetar el cable.

## 3. Paso a paso

1. **Pasa primero el termorretráctil** por cada cable, antes de soldar nada.
2. **Pela una ventana**: a unos 10 cm del sensor, quita 3 mm de aislante del cable rojo
   y otros 3 mm del amarillo **sin cortar el cobre**. Truco: apoya la punta del soldador
   1 segundo sobre el aislante y retíralo con la uña; así no se muerde el cobre.
   Deja las dos ventanas a distinta altura (una 5 mm más arriba que la otra), para que
   las uniones no queden enfrentadas y no se toquen.
3. **Estaña las ventanas** y también las patas de la resistencia, por separado.
4. **Enrolla la pata** media vuelta sobre la ventana ya estañada. Que sujete sola: eso
   es lo que hace que aguante los tirones.
5. **Suelda**: calienta la unión 1 o 2 segundos, añade estaño, retira el estaño y después
   el soldador. **No muevas la unión mientras enfría**.
6. **Corta la pata sobrante** a unos 5 mm y déblala contra el cable para que no pique ni
   pueda tocar el otro cable.
7. **Encoge el termorretráctil** corriéndolo sobre cada unión y acercándole el soldador
   de costado, sin tocarlo.

### 3.1 Si no tienes termorretráctil

Se puede hacer con **cinta aislante de PVC** (no sirve la cinta transparente ni la de
papel: se despegan con el calor del módulo). Reglas:

1. **Una tira por unión, nunca una sola tira abarcando las dos.** Si se envuelven juntas,
   la cinta aprieta las dos patas una contra otra y el riesgo de cortocircuito entre 3,3 V
   y datos queda dentro del envoltorio, donde no se ve.
2. Limpia la unión antes de encintar (los restos de flux impiden que pegue).
3. Corta unos 2 cm, **estira la cinta al colocarla**: el PVC pega contra sí mismo cuando
   está estirado, y así no se despega con el calor. Dos o tres capas, montando la mitad
   del ancho en cada vuelta, y aprieta al final.
4. Dobla la pata sobrante contra el cable antes de encintar, para que ninguna punta
   aguda atraviese la cinta con el tiempo.
5. Deja 5 mm entre las dos uniones, para que las cintas no se toquen.

Mejor todavía, si aparece cualquiera de estas dos cosas en casa:

- **Una funda**: 2 cm del forro exterior de un cable más grueso (una extensión, un cable
  de lámpara). Se corre sobre la unión, entra justo y sujeta sola; se remata con cinta en
  las puntas.
- **Silicona caliente** (pistola de pegar): una gota sobre la unión. Aísla muy bien y se
  retira con la uña si hay que rehacerla.

Lo ideal sigue siendo el termorretráctil: se consigue por monedas en cualquier tienda de
eléctricos. Si por ahora va con cinta, **revisa las uniones antes de la demostración** y
vuelve a medir, porque la cinta cede con el calor y con la humedad del ambiente del
montaje.

## 4. Comprobación antes de conectar a la placa

Con el multímetro, con el módulo **desconectado**:

| Medición | Debe dar | Si no da eso |
| --- | --- | --- |
| Punta libre del **amarillo** contra punta libre del **rojo** | 4 600 a 4 800 Ω (≈ 4,7 kΩ) | `1` o `OL`: alguna unión no conduce, hay que rehacerla. |
| Punta libre del **rojo** contra punta libre del **negro** | **No** debe dar 0 Ω | 0 Ω es un cortocircuito: no conectes, revisa la soldadura. |
| Tirón suave de cada pata con la pinza | La unión resiste | Si la pata se corre, la unión es solo mecánica: rehacer. |

**Repite las dos primeras mediciones después de encintar.** Al envolver se pueden juntar
las patas sin que se note por fuera, y esa es la única forma de detectarlo.

## 5. Conexión a la placa

| Cable del AM2302 | Pin de la placa ESP32 |
| --- | --- |
| Rojo | `3,3V` (verifica que el puente de la placa esté en 3,3 V, no en 5 V) |
| Amarillo | `P33` · GPIO 33 |
| Negro | `GND` |

Con la caja negra de protección puesta. Después se enciende y en el monitor serie debe
aparecer una lectura de `Ambiente` **sin** el error de la fase 'B'.

## 6. Registro

| Fecha | Qué se hizo | Medición rojo-amarillo | Resultado |
| --- | --- | --- | --- |
|  |  |  |  |
