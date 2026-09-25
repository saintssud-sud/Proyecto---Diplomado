/* ============================================================================
 *  SI.G.VA.C.H. — Cola de lecturas pendientes en memoria NO VOLÁTIL  (ESP-IDF)
 * ==========================================================================*/

#include <stdio.h>
#include <string.h>

#include "esp_log.h"
#include "nvs.h"
#include "nvs_flash.h"

#include "cola_nvs.h"

static const char *ETIQUETA = "COLA";

/* Espacio de nombres dentro de la partición NVS. */
static const char *ESPACIO = "pendientes";

static nvs_handle_t manejador;
static bool abierta = false;

/* Anillo: `cabeza` es la posición donde se escribirá la próxima lectura y
 * `cuantas` cuántas hay guardadas. La más antigua está en
 * (cabeza - cuantas + COLA_MAXIMA) % COLA_MAXIMA. */
static int cabeza = 0;
static int cuantas = 0;

/* ---------------------------------------------------------------------------
 *  Utilidades
 * -------------------------------------------------------------------------*/

/** Arma la clave NVS de una posición del anillo.
 *  Las claves de NVS no pueden pasar de 15 caracteres: "e00" a "e59" entran
 *  de sobra. */
static void claveDe(int indice, char *destino, size_t tamano)
{
    snprintf(destino, tamano, "e%02d", indice);
}

esp_err_t cola_iniciar(void)
{
    esp_err_t resultado = nvs_open(ESPACIO, NVS_READWRITE, &manejador);
    if (resultado != ESP_OK) {
        ESP_LOGE(ETIQUETA, "No se pudo abrir la memoria de pendientes (0x%x)", resultado);
        abierta = false;
        return resultado;
    }
    abierta = true;

    int32_t valorCabecera = 0;
    int32_t valorCuantas = 0;
    if (nvs_get_i32(manejador, "cabeza", &valorCabecera) != ESP_OK) valorCabecera = 0;
    if (nvs_get_i32(manejador, "cuantas", &valorCuantas) != ESP_OK) valorCuantas = 0;

    /* Saneamiento. Si los índices guardados no son coherentes —por ejemplo, si
     * se cortó la luz en mitad de una escritura— se vuelve a empezar de cero en
     * lugar de leer posiciones inválidas. */
    if (valorCabecera < 0 || valorCabecera >= COLA_MAXIMA) valorCabecera = 0;
    if (valorCuantas < 0 || valorCuantas > COLA_MAXIMA) valorCuantas = 0;

    cabeza = (int)valorCabecera;
    cuantas = (int)valorCuantas;

    if (cuantas > 0) {
        ESP_LOGW(ETIQUETA, "Hay %d lectura(s) pendiente(s) de ciclos anteriores", cuantas);
    } else {
        ESP_LOGI(ETIQUETA, "Memoria de pendientes lista (vacia)");
    }
    return ESP_OK;
}

int cola_cuantas(void)
{
    return abierta ? cuantas : 0;
}

/* ---------------------------------------------------------------------------
 *  Guardar
 * -------------------------------------------------------------------------*/

esp_err_t cola_guardar(const char *variable, float valor, const char *unidad,
                       const char *momento)
{
    if (!abierta) return ESP_ERR_INVALID_STATE;
    if (!variable || !unidad) return ESP_ERR_INVALID_ARG;

    LecturaPendiente pendiente;
    memset(&pendiente, 0, sizeof(pendiente));
    strlcpy(pendiente.variable, variable, sizeof(pendiente.variable));
    strlcpy(pendiente.unidad, unidad, sizeof(pendiente.unidad));
    strlcpy(pendiente.momento, momento ? momento : "", sizeof(pendiente.momento));
    pendiente.valor = valor;

    char clave[8];
    claveDe(cabeza, clave, sizeof(clave));

    esp_err_t resultado = nvs_set_blob(manejador, clave, &pendiente, sizeof(pendiente));
    if (resultado != ESP_OK) {
        ESP_LOGE(ETIQUETA, "No se pudo guardar la lectura (0x%x)", resultado);
        return resultado;
    }

    cabeza = (cabeza + 1) % COLA_MAXIMA;
    if (cuantas < COLA_MAXIMA) {
        cuantas++;
    }
    /* Si ya estaba llena, el contador no cambia: la lectura nueva ocupó el
     * lugar de la más antigua, que queda descartada. */

    nvs_set_i32(manejador, "cabeza", (int32_t)cabeza);
    nvs_set_i32(manejador, "cuantas", (int32_t)cuantas);
    return nvs_commit(manejador);
}

/* ---------------------------------------------------------------------------
 *  Recuperar
 * -------------------------------------------------------------------------*/

bool cola_primera(LecturaPendiente *destino)
{
    if (!abierta || cuantas == 0 || !destino) return false;

    int indice = (cabeza - cuantas + COLA_MAXIMA) % COLA_MAXIMA;
    char clave[8];
    claveDe(indice, clave, sizeof(clave));

    size_t longitud = sizeof(LecturaPendiente);
    if (nvs_get_blob(manejador, clave, destino, &longitud) != ESP_OK) {
        /* La entrada no está aunque el contador diga que sí: se descarta para
         * no quedar trabados reintentando algo que no existe. */
        ESP_LOGW(ETIQUETA, "Falta la entrada %d del anillo: se descarta", indice);
        return false;
    }
    return true;
}

esp_err_t cola_descartar_primera(void)
{
    if (!abierta || cuantas == 0) return ESP_ERR_INVALID_STATE;

    int indice = (cabeza - cuantas + COLA_MAXIMA) % COLA_MAXIMA;
    char clave[8];
    claveDe(indice, clave, sizeof(clave));

    nvs_erase_key(manejador, clave);
    cuantas--;

    nvs_set_i32(manejador, "cuantas", (int32_t)cuantas);
    return nvs_commit(manejador);
}

esp_err_t cola_vaciar(void)
{
    if (!abierta) return ESP_ERR_INVALID_STATE;

    char clave[8];
    while (cuantas > 0) {
        int indice = (cabeza - cuantas + COLA_MAXIMA) % COLA_MAXIMA;
        claveDe(indice, clave, sizeof(clave));
        nvs_erase_key(manejador, clave);
        cuantas--;
    }

    cabeza = 0;
    nvs_set_i32(manejador, "cabeza", 0);
    nvs_set_i32(manejador, "cuantas", 0);
    return nvs_commit(manejador);
}
