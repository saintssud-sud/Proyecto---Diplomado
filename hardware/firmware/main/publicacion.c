/* ============================================================================
 *  SI.G.VA.C.H. — Publicación de lecturas en el servicio  (ESP-IDF)
 * ==========================================================================*/

#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>

#include "esp_log.h"
#include "esp_http_client.h"
#include "esp_crt_bundle.h"

#include "configuracion.h"
#include "publicacion.h"

static const char *ETIQUETA = "PUBLICACION";

/* Espera máxima de una petición, en segundos.
 * El servicio gratuito de Render se "duerme" y tarda hasta 60 s en despertar en
 * la primera petición. El valor cubre ese arranque en frío; con menos, la
 * primera lectura de cada jornada se perdería por impaciencia. */
#define SEGUNDOS_ESPERA_PUBLICACION  75

/* ---------------------------------------------------------------------------
 *  Utilidades
 * -------------------------------------------------------------------------*/

/** Arma el número para el JSON, con dos decimales, SIN usar %f.
 *  El formateo "nano" de newlib puede no soportar %f, y en ese caso el cuerpo
 *  JSON saldría con basura en lugar de un número. */
static void numeroAJson(char *destino, unsigned tamano, float valor)
{
    bool negativo = valor < 0.0f;
    if (negativo) valor = -valor;

    int entero = (int)valor;
    int decimales = (int)((valor - (float)entero) * 100.0f + 0.5f);
    if (decimales >= 100) {
        entero++;
        decimales -= 100;
    }
    snprintf(destino, tamano, "%s%d.%02d", negativo ? "-" : "", entero, decimales);
}

/** Arma la dirección completa del recurso.
 *  El puerto se omite cuando es el habitual del esquema (443 para HTTPS, 80
 *  para HTTP): así la dirección queda igual a la que funciona en el navegador. */
static void construirUrl(char *destino, unsigned tamano)
{
#if USAR_HTTPS
    const char *esquema = "https";
    bool puertoHabitual = (PUERTO_API == 443);
#else
    const char *esquema = "http";
    bool puertoHabitual = (PUERTO_API == 80);
#endif

    if (puertoHabitual) {
        snprintf(destino, tamano, "%s://%s%s", esquema, HOST_API, RUTA_LECTURAS);
    } else {
        snprintf(destino, tamano, "%s://%s:%d%s", esquema, HOST_API, PUERTO_API, RUTA_LECTURAS);
    }
}

void publicacion_marca_de_tiempo(char *destino, unsigned tamano)
{
    destino[0] = '\0';

    time_t ahora = time(NULL);
    if (ahora < 1700000000) return;      /* el reloj todavía no sincronizó */

    struct tm partes;
    gmtime_r(&ahora, &partes);
    strftime(destino, tamano, "%Y-%m-%dT%H:%M:%SZ", &partes);
}

/* ---------------------------------------------------------------------------
 *  Envío
 * -------------------------------------------------------------------------*/

int publicacion_enviar(const char *variable, float valor, const char *unidad,
                       const char *momentoIndicado)
{
    if (!variable || !unidad) return -1;

    char url[224];
    construirUrl(url, sizeof(url));

    char numero[16];
    numeroAJson(numero, sizeof(numero), valor);

    /* La marca de tiempo puede venir de afuera. Es lo que permite republicar una
     * lectura guardada con la hora en que SE MIDIÓ: si se usara la hora actual,
     * el historial del cultivo mostraría el dato en el momento equivocado. */
    char momentoGenerado[24];
    const char *momento = momentoIndicado;
    if (!momento || !momento[0]) {
        publicacion_marca_de_tiempo(momentoGenerado, sizeof(momentoGenerado));
        momento = momentoGenerado;
    }

    char cuerpo[288];
    if (momento[0]) {
        snprintf(cuerpo, sizeof(cuerpo),
                 "{\"modulo_id\":\"%s\",\"variable\":\"%s\",\"valor\":%s,"
                 "\"unidad\":\"%s\",\"timestamp\":\"%s\"}",
                 MODULO_ID, variable, numero, unidad, momento);
    } else {
        /* Sin hora sincronizada, el servicio pone la suya. */
        snprintf(cuerpo, sizeof(cuerpo),
                 "{\"modulo_id\":\"%s\",\"variable\":\"%s\",\"valor\":%s,\"unidad\":\"%s\"}",
                 MODULO_ID, variable, numero, unidad);
    }

    esp_http_client_config_t configuracion = {
        .url = url,
        .method = HTTP_METHOD_POST,
        .timeout_ms = SEGUNDOS_ESPERA_PUBLICACION * 1000,
#if USAR_HTTPS
        /* Valida el certificado del servidor de verdad. Sin esto habría que
         * usar setInsecure(), que cifra pero no comprueba con quién se habla. */
        .crt_bundle_attach = esp_crt_bundle_attach,
#endif
    };

    esp_http_client_handle_t cliente = esp_http_client_init(&configuracion);
    if (!cliente) {
        ESP_LOGE(ETIQUETA, "No se pudo crear la conexion");
        return -1;
    }

    esp_http_client_set_header(cliente, "Content-Type", "application/json");
    esp_http_client_set_header(cliente, "X-Device-Key", CLAVE_DISPOSITIVO);
    esp_http_client_set_post_field(cliente, cuerpo, (int)strlen(cuerpo));

    esp_err_t resultado = esp_http_client_perform(cliente);

    int codigo;
    if (resultado == ESP_OK) {
        codigo = esp_http_client_get_status_code(cliente);
    } else {
        /* Sin respuesta: se devuelve el error del transporte en negativo, para
         * que no se confunda con un código HTTP. */
        ESP_LOGW(ETIQUETA, "Sin respuesta de %s (%s)", url, esp_err_to_name(resultado));
        codigo = -(int)resultado;
    }

    esp_http_client_cleanup(cliente);
    return codigo;
}

const char *publicacion_describir_resultado(int resultado)
{
    switch (resultado) {
        case 200: return "aceptada";
        case 201: return "almacenada";
        case 400: return "peticion mal formada";
        case 401: return "CLAVE DEL DISPOSITIVO RECHAZADA";
        case 404: return "el modulo no existe en el servicio";
        case 408: return "el servicio tardo demasiado";
        case 422: return "valor fuera de rango o variable desconocida";
        case 429: return "demasiadas peticiones";
        case 500:
        case 502:
        case 503:
        case 504: return "el servicio no esta disponible";
        default:
            return (resultado < 0) ? "sin respuesta del servicio"
                                   : "respuesta inesperada";
    }
}
