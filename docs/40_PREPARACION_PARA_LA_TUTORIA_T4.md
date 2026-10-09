# Preparación para la tutoría T4 y la predefensa

**Hoy, viernes 9 de octubre de 2026, 17:00.** Esta tutoría es la última antes de la defensa
final (T5, martes 13) y tiene dos partes: el docente verifica en vivo lo que pidió corregir
del E3, y se ensaya la defensa.

---

## 1. Lo que el docente va a verificar en vivo

De las recomendaciones del E3 (`Recomendaciones_E3_T4.txt`, punto 1): *«En la T4: repetir la
medición de `cuentas-de-prueba-2026-09-29.txt` en vivo (401, 403 y 200) y una lectura del
dispositivo con `X-Device-Key` inválida (401)»*.

**Está resuelto en un solo comando.** El programa `scripts/verificar_autorizacion.py` hace las
cinco comprobaciones y guarda la evidencia fechada:

```powershell
cd "D:\SIGVACH-Monograf\Proyecto SIGVACH"
python scripts\verificar_autorizacion.py
```

Resultado de la corrida de hoy (13:23), guardado en `evidencia/autorizacion-2026-10-09.txt`:

| # | Comprobación | Resultado |
|---|---|---|
| 1 | `GET /api/v1/usuarios` **sin token** | **401** — «Falta el token de identidad…» |
| 2 | La misma ruta con la cuenta de **operador** | **403** — «La operación requiere el rol de administrador», con `rol_actual: operador` |
| 3 | La misma ruta con la cuenta de **administrador** | **200** — 8 cuentas |
| 4 | Lectura del dispositivo con **`X-Device-Key` inválida** | **401** — «La clave del módulo de adquisición no es válida» (no se registra nada) |
| 5 | Monitor del despliegue `GET /api/v1/salud` | **200** — `base_de_datos: conectada` |

**Aviso importante para las 17:00:** la primera petición al servicio publicado tarda ~35 s
porque la capa gratuita lo suspende por inactividad. **Despertalo cinco minutos antes** con
una llamada cualquiera (abrí la aplicación web), así cuando el docente mire responde al
instante.

---

## 2. Estado de las correcciones del E3

| Punto que pidió el docente | Estado |
|---|---|
| 2.7 en cinco apartados (2.7.1 a 2.7.5) | **Hecho** — el contenido es el mismo, reorganizado |
| 2.3.1: nombrar el rol de solo consulta | **Hecho** — se declara como rol técnico sin pantalla propia |
| **CP-24 (RNF-01 «No cumple»)** | **Hecho y medido**: p95 de **1042 → 427 ms** con 200 registros y de **984 → 406 ms** con 50; 20 de 20 consultas dentro de los 800 ms. Evidencia en `evidencia/rendimiento-2026-10-09-*.txt` |
| Cerrar CP-06, CP-11 y CP-19 | **CP-06, CP-11 y CP-19 cerrados** (verificados en vivo). CP-04, CP-12 y CP-18 siguen en «Parcial» |
| CP-22 (usabilidad con tres usuarios) | **Pendiente**: la sesión con usuarios. Guion en `docs/38_GUION_CP22_USABILIDAD.md` y planilla en `evidencia/usabilidad-planilla-para-llenar.txt` |
| Open-Meteo fuera del stack | **Hecho** — 0 menciones en el E4 |
| Extensión del cuerpo (límite 30-40 páginas) | **Hecho** — el cuerpo mide **38 páginas** |
| `DELETE /api/v1/lecturas/{id}` → anulación con motivo (A-01, RNF-08) | **Hecho**: la ruta de borrado ya no existe (405) y en su lugar está `POST /api/v1/lecturas/{id}/anulacion`, con motivo obligatorio. Verificado en vivo |

---

## 3. Los números que conviene tener a mano

| Dato | Valor |
|---|---|
| Pruebas automatizadas | **248** — 152 del servicio y 96 de la aplicación, todas sin fallos |
| Casos de prueba | **24**: 20 aprobados · 3 parciales · 1 pendiente (usabilidad) |
| Rendimiento (RNF-01, parte de API) | p95 **427 ms** con 200 registros · objetivo 800 ms · **cumple** |
| Variables publicadas | **6** (pH, conductividad, sólidos disueltos, temperatura de solución y ambiente, humedad) |
| Sensores del módulo | **4** sobre ESP32, con publicación cifrada y clave de dispositivo |
| Calibración del pH | patrones 4,01 y 6,86 → **1520 mV** y **1280 mV** (−84,2 mV por unidad de pH) |
| Calibración del TDS | patrón Hanna HI7031 de 1413 µS/cm (707 ppm) → factor **0,9373**, verificado en **707,08 ppm** de media |
| Operaciones del contrato | **32** |
| Aplicación publicada | `https://sigvach26-bd.web.app` |
| Servicio publicado | `https://sigvach-api.onrender.com` |
| Repositorio | `https://github.com/saintssud-sud/Proyecto---Diplomado` |
| Entrega | E4 en `.docx` y `.pdf`, monografía de **154 páginas** con el cuerpo en 38 |

---

## 4. Las tres observaciones de mayor impacto, y cómo quedaron

El docente las marcó como lo más importante del E3:

1. **«RNF-01 no se cumple con páginas grandes (CP-24).»** → Resuelto: se desplegó la memoria
   intermedia de las consultas y se midió **antes y después contra el servicio publicado**.
   Ahora cumple con 200 y con 50 registros, y el caso pasó de «No cumple» a «Aprobado».
2. **«Seis casos "Parcial" y la usabilidad sin ejecutar.»** → Se cerraron tres (CP-06, CP-11,
   CP-19) con verificación en vivo; quedan tres parciales y la sesión de usabilidad, que es lo
   único que no depende del sistema sino de conseguir usuarios.
3. **«2.7 sin la estructura de cinco apartados.»** → Hecho: 2.7.1 a 2.7.5 con los mismos textos.

---

## 5. Preguntas previsibles del tribunal, con la respuesta corta

- **«¿Por qué las lecturas se anulan en lugar de borrarse?»** Por trazabilidad: el dato medido
  no se pierde (RNF-08). La lectura queda marcada, con el motivo, quién la anuló y cuándo; deja
  de contarse en el panel y en la exportación, pero se sigue consultando por su identificador.
  El borrado físico no existe en el contrato.
- **«¿Cómo saben que el rendimiento mejoró y no es casualidad?»** Porque se midió con el mismo
  programa, el mismo número de consultas y contra el mismo servicio, antes y después de
  desplegar la mejora: 1042 → 427 ms de percentil 95 con 200 registros. Los informes están
  fechados y versionados en `evidencia/`.
- **«¿La calibración del TDS con qué patrón se hizo?»** Con el Hanna HI7031 de 1413 µS/cm, que
  equivale a 707 ppm. La sonda leía 6,7 % alto; se aplicó el factor 0,9373 en el firmware y la
  verificación posterior dio 707,08 ppm de media, con un error de +0,01 %.
- **«¿Por qué el documento es una monografía y no un perfil de proyecto?»** Porque el formato
  institucional establece que el trabajo final de diplomado adopta la forma de monografía, y los
  lineamientos técnicos del área precisan el contenido de cada capítulo. Los entregables
  anteriores usaron el formato de perfil; este ya está en el de monografía, con sus preliminares
  completos (contratapa, aprobación, advertencia e índice) y el resumen de 291 palabras.
- **«¿Qué falta?»** La sesión de usabilidad con usuarios (CP-22) y la mitad del RNF-01 que se
  mide en el navegador: que el panel muestre el estado en tres segundos o menos con conexión
  móvil. Esa medición se hace con la pestaña de red abierta y se guarda como captura fechada.

*(Hay más preguntas y respuestas en `docs/21_PREGUNTAS_PARA_LA_TUTORIA.md`.)*

---

## 6. Para el ensayo de la defensa

- **El guion de la demostración está en `docs/17_GUION_DE_LA_DEMOSTRACION.md`** (7 minutos de
  demostración y 5 de preguntas). El mapa del repositorio, para ubicar cualquier archivo delante
  del tribunal, está en `docs/28_MAPA_DEL_REPOSITORIO_PARA_LA_DEFENSA.md`.
- **Para explicar el código**, `docs/35_GUIA_PARA_ENTENDER_EL_CODIGO.md` recorre el servicio y la
  aplicación archivo por archivo.
- **Lo que conviene tener abierto antes de empezar:** la aplicación web en una pestaña, el
  servicio despierto, el repositorio en otra pestaña, el PDF del E4 a mano y esta guía impresa.

---

## 7. Lista de comprobación para las 17:00

- [ ] Subir el **E4** (`.docx` y `.pdf`) a la plataforma y al SharePoint.
- [ ] Abrir `https://sigvach26-bd.web.app` para **despertar el servicio** unos minutos antes
      (la primera petición tarda ~35 s).
- [ ] Ejecutar `python scripts\verificar_autorizacion.py` y tener a mano el resultado (5 de 5).
- [ ] Tener el informe de rendimiento `evidencia/rendimiento-2026-10-09-limite-200-despues-publicado.txt`.
- [ ] Tener la evidencia de la anulación `evidencia/anulacion-2026-10-09.txt`.
- [ ] Tener abierto el repositorio y el tablero (`docs/TABLERO.md`).
- [ ] Si se puede, hacer la **medición del panel en el navegador** (la mitad del RNF-01 que
      falta): pestaña de red abierta, móvil o emulación móvil, y captura fechada.
