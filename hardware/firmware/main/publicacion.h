/* ============================================================================
 *  SI.G.VA.C.H. — Publicación de lecturas en el servicio  (ESP-IDF)
 *  ---------------------------------------------------------------------------
 *  Envía cada lectura al servicio por HTTPS, con la clave del dispositivo.
 *
 *  SOBRE LA SEGURIDAD DEL TRANSPORTE
 *  La versión de Arduino usaba `setInsecure()`, que cifra el tráfico pero NO
 *  comprueba con quién está hablando: acepta cualquier certificado. Eso deja la
 *  puerta abierta a un intermediario que se haga pasar por el servicio y se
 *  quede con la clave del dispositivo.
 *
 *  Acá se usa el paquete de certificados raíz de ESP-IDF (`esp_crt_bundle`), que
 *  valida de verdad el certificado del servidor. Es una mejora concreta de
 *  seguridad y no cuesta memoria apreciable: el paquete se enlaza en modo solo
 *  lectura y se comparte.
 * ==========================================================================*/

#ifndef PUBLICACION_H
#define PUBLICACION_H

#include <stdbool.h>
#include "esp_err.h"

/* ---------------------------------------------------------------------------
 *  Envía una lectura al servicio.
 *
 *  `variable` es el código que espera el servicio ("tds", "ph", "humedad"…),
 *  `valor` el número y `unidad` su unidad ("°C", "ppm", "%"…). Las unidades
 *  deben coincidir EXACTAMENTE con el catálogo del servicio, que vive en
 *  `backend/app/esquemas.py`: si no coinciden, responde 422 y la lectura se
 *  pierde.
 *
 *  `momento` es la marca de tiempo ISO 8601 de CUÁNDO SE MIDIÓ. Se pasa NULL
 *  para que se use la hora actual —pero al reintentar una lectura guardada hay
 *  que pasar la hora original, no la del reintento: si no, el historial del
 *  cultivo queda con la fecha equivocada.
 *
 *  Devuelve el código HTTP de la respuesta (201 si se almacenó, 401 si la clave
 *  fue rechazada, 404 si el módulo no existe, 422 si el valor o la unidad están
 *  fuera de contrato), o un valor NEGATIVO si no hubo respuesta.
 * -------------------------------------------------------------------------*/
int publicacion_enviar(const char *variable, float valor, const char *unidad,
                       const char *momento);

/** Texto legible para un código devuelto por publicacion_enviar(). */
const char *publicacion_describir_resultado(int resultado);

/* ---------------------------------------------------------------------------
 *  Marca de tiempo ISO 8601 en UTC, para acompañar la lectura.
 *  Se apoya en la hora que sincroniza SNTP. Si el reloj todavía no sincronizó,
 *  deja la cadena vacía y el servicio pone la hora por su cuenta.
 * -------------------------------------------------------------------------*/
void publicacion_marca_de_tiempo(char *destino, unsigned tamano);

#endif /* PUBLICACION_H */
