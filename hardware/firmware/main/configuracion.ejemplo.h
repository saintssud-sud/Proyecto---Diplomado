/* ============================================================================
 *  Plantilla de configuración privada — SI.G.VA.C.H.  (versión ESP-IDF)
 *  ---------------------------------------------------------------------------
 *  CÓMO USARLA
 *    1. Copiar este archivo con el nombre:  configuracion.h
 *    2. Completar los datos entre comillas con los del proyecto real.
 *    3. NO subir `configuracion.h` al repositorio: contiene la clave del
 *       dispositivo. El archivo `.gitignore` de esta carpeta ya lo excluye.
 * ==========================================================================*/

#ifndef CONFIGURACION_H
#define CONFIGURACION_H

/* --- Red WiFi (el ESP32 clásico solo trabaja en 2,4 GHz) ------------------- */
#define NOMBRE_WIFI   "NOMBRE-DE-TU-RED"
#define CLAVE_WIFI    "CLAVE-DE-TU-RED"

/* --- Modo de trabajo ------------------------------------------------------ */
/* 0 = solo lee los sensores y los muestra por el Monitor Serie.
 *     Sirve para comprobar el conexionado sin WiFi ni servicio.
 * 1 = publica las lecturas en el servicio SI.G.VA.C.H. */
#define PUBLICAR_EN_SERVICIO  0

/* --- Servicio SI.G.VA.C.H. ------------------------------------------------ */
/* Servicio publicado (cifrado, con validación del certificado). */
#define USAR_HTTPS   1
#define HOST_API     "sigvach-api.onrender.com"
#define PUERTO_API   443

/* Servicio local para probar en casa (sin cifrado):
 * #define USAR_HTTPS   0
 * #define HOST_API     "192.168.1.100"   // IP de la computadora en la red local
 * #define PUERTO_API   8011
 */

#define RUTA_LECTURAS "/api/v1/lecturas"

/* --- Identidad del dispositivo (NO compartir) ----------------------------- */
/* La clave se copia del archivo .env del proyecto (DEVICE_API_KEY). */
#define CLAVE_DISPOSITIVO  "PEGAR-AQUI-LA-CLAVE-DEL-DISPOSITIVO"

/* --- Identificador del módulo de cultivo ---------------------------------- */
/* El de la maqueta: Maqueta NFT - Lechuga. */
#define MODULO_ID          "v6wrYSXxeHyttf3prDd7"

#endif
