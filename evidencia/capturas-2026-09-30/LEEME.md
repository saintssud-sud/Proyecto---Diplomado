# Capturas del flujo completo en producción · 30 de septiembre de 2026

Evidencia del **nivel funcional** que pide la plenaria P4: el flujo Must recorrido desde la
interfaz, **en la URL publicada**, con capturas fechadas.

| Dato | Valor |
|---|---|
| Aplicación | https://sigvach26-bd.web.app |
| Fecha de las capturas | miércoles 30 de septiembre de 2026, entre las 10:16 y las 10:51 |
| Cuenta usada | `operador@proyecto.test` (cuenta ficticia de prueba) |
| Módulo mostrado | «Maqueta NFT - Lechuga» (el módulo piloto) y «Módulo 1» |
| Resolución | 1920 × 1080 |

## Por qué estas capturas valen como evidencia

La plenaria dice qué hace válida una captura: que se vea **la URL pública**, la **fecha** y datos
ficticios, y que no sea un recorte de `localhost`. En estas se ve:

- **la barra de direcciones** del navegador con `sigvach26-bd.web.app`, en todas;
- **el reloj del sistema** con la fecha `30/9/2026` en la barra de tareas, en todas;
- los datos del módulo, que son los del montaje real (no hay datos personales de terceros).

Se verificaron dos de ellas a tamaño completo (la de inicio de sesión y la del panel con alerta) y
el resto con una hoja de contactos: las diecisiete cumplen las tres condiciones.

## Qué muestra cada archivo

| Archivo | Qué muestra |
|---|---|
| `01-inicio-de-sesion.jpg` | La pantalla de inicio de sesión, antes de entrar |
| `02-inicio-de-sesion-vista-2.jpg` | La misma pantalla, segunda vista |
| `03-panel-maqueta.jpg` | El panel del módulo piloto |
| `04-panel-con-alerta.jpg` | El panel con el aviso «Sistema con alertas» y las seis variables: TDS y conductividad por debajo del rango, pH «Sin lecturas» |
| `05-panel-vista-3.jpg` | El panel, tercera vista |
| `06-historial.jpg` | El historial de lecturas |
| `07-historial-grafico-1.jpg` | El historial con el gráfico de una variable |
| `08-historial-grafico-2.jpg` | El gráfico de otra variable |
| `09` a `13-historial-lista-*.jpg` | El historial en lista, con las marcas de tiempo |
| `14-panel-modulo-1.jpg` | El panel del «Módulo 1», con el botón «Registrar medición» y su última actualización |
| `15-dialogo-1.jpg` y `16-dialogo-2.jpg` | Dos diálogos de la aplicación |
| `17-panel-modulo-1-vista-2.jpg` | El panel del «Módulo 1», segunda vista |

> Los nombres son **provisionales** en los archivos que no se pudieron identificar con certeza
> (`05`, `15`, `16` y `17`). Se confirman con el autor antes de citarlos en el documento.

En `_descartadas/` quedaron dos capturas que sólo muestran la pantalla de carga («Cargando…»): no
sirven como evidencia del flujo.

## Lo que falta capturar

| Falta | Por qué importa |
|---|---|
| **El 403 en vivo**: con la sesión del operador, intentar una operación de administración y que se vea el rechazo del servicio | Es el paso 3 del protocolo de la defensa y el criterio «seguridad demostrada» de la rúbrica (15 puntos) |
| La pantalla de **usuarios** con la cuenta `administrador@proyecto.test`, mostrando las dos cuentas de prueba y sus roles | Demuestra la administración de cuentas y el rol de cada una |
| El **registro manual** de una lectura, con su confirmación | Es un requisito Must |

El rechazo del servicio ya está demostrado con llamadas directas en
`../cuentas-de-prueba-2026-09-29.txt`; la captura desde la interfaz es la que falta para el nivel
funcional.
