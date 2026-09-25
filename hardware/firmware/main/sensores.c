/* ============================================================================
 *  SI.G.VA.C.H. — Sensores del módulo  (ESP-IDF)
 *  ---------------------------------------------------------------------------
 *  Sensor de ambiente: AM2302 (DHT22) o DHT11.
 *
 *  SOBRE EL PULL-UP  (importante)
 *  El driver `dht` de esp-idf-lib NO configura ningún pull-up: usa la línea
 *  como salida de DRENADOR ABIERTO y como entrada, y su propia documentación
 *  pide "una resistencia de pull-up adecuada". Por eso hay que activar el
 *  pull-up interno del ESP32 a mano (lo que hace el ejemplo del componente):
 *
 *      gpio_set_pull_mode(pin, GPIO_PULLUP_ONLY);
 *
 *  El pull-up interno ronda los 45 kΩ. Es más débil que la resistencia externa
 *  de 10 kΩ que indica el manual, pero alcanza con el cable propio del AM2302.
 *
 *  SOBRE LA BÚSQUEDA DEL PIN
 *  Si el sensor no responde en el pin previsto, el programa prueba los demás
 *  pines que expone la placa de expansión e informa en cuál responde. Así se
 *  resuelve en un arranque una duda de conexionado que, a mano, lleva media
 *  hora de prueba y error.
 *
 *  CÓMO SE RECONOCE QUE EL SENSOR RESPONDE
 *  El driver baja la línea 20 ms y la suelta; el sensor debe bajarla a 0 dentro
 *  de 40 µs como acuse de recibo (la "fase B"). Si eso no ocurre, el error es
 *  "problem in phase 'B'" y significa que la línea se quedó en alto: el pull-up
 *  la sostiene y nadie del otro lado la baja, o sea que el sensor no está
 *  conectado a ESE pin, o no está alimentado.
 * ==========================================================================*/

#include <math.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "driver/gpio.h"
#include "esp_log.h"

#include "dht.h"
#include "onewire_bus.h"
#include "ds18b20.h"
#include "sensores.h"

static const char *ETIQUETA = "SENSORES";

/* Pin en uso y modelo detectado. Se completan en sensores_iniciar(). */
static gpio_num_t pinAmbiente = PIN_AMBIENTE;
static dht_sensor_type_t tipoAmbiente = DHT_TYPE_AM2301;

/* Pines que expone la placa de expansión y que SIRVEN para este sensor.
 *
 * Se excluyen a propósito:
 *   - GPIO 34 y 35: son de SOLO ENTRADA, y el driver necesita bajar la línea.
 *   - GPIO 6 a 11 (CMD, SD2, SD3 y las demás de la memoria flash): tocarlos
 *     cuelga el arranque del chip.
 *   - GPIO 0, 2, 12 y 15: son pines de arranque (strapping); bajarlos puede
 *     impedir que el chip arranque.
 * Queda un conjunto seguro: el pin previsto primero y después los demás. */
static const gpio_num_t PINES_CANDIDATOS[] = {
    PIN_AMBIENTE,   /* 33 - P33, el pin del manual: se prueba primero  */
    32,             /* P32 - previsto para el DS18B20                  */
    25,             /* P25 - previsto para el disparo del ultrasónico  */
    26,             /* P26 - previsto para el eco del ultrasónico      */
    27,             /* P27                                             */
    14,             /* P14                                             */
    13,             /* P13                                             */
};
#define CUANTOS_CANDIDATOS (sizeof(PINES_CANDIDATOS) / sizeof(PINES_CANDIDATOS[0]))

/* ---------------------------------------------------------------------------
 *  Detección
 * -------------------------------------------------------------------------*/

/** Prueba si el sensor responde en un pin dado con un modelo dado. */
static bool respondeComo(gpio_num_t pin, dht_sensor_type_t tipo)
{
    float temperatura = NAN;
    float humedad = NAN;

    gpio_set_pull_mode(pin, GPIO_PULLUP_ONLY);

    /* OJO con el orden de los argumentos: primero la humedad, después la
     * temperatura. Está así en la firma de dht_read_float_data(). */
    esp_err_t resultado = dht_read_float_data(tipo, pin, &humedad, &temperatura);
    if (resultado != ESP_OK) return false;

    bool temperaturaValida = !isnan(temperatura) && temperatura > -40.0f && temperatura < 80.0f;
    bool humedadValida     = !isnan(humedad)     && humedad >= 0.0f && humedad <= 100.0f;

    return temperaturaValida && humedadValida;
}

/** Busca el sensor en todos los pines candidatos, con un modelo dado. */
static bool buscarEnTodosLosPines(dht_sensor_type_t tipo, gpio_num_t *encontrado)
{
    for (size_t i = 0; i < CUANTOS_CANDIDATOS; i++) {
        gpio_num_t pin = PINES_CANDIDATOS[i];

        /* El AM2302 necesita unos dos segundos de reposo entre lecturas. */
        vTaskDelay(pdMS_TO_TICKS(2200));

        if (respondeComo(pin, tipo)) {
            *encontrado = pin;
            return true;
        }
        ESP_LOGW(ETIQUETA, "  GPIO %2d: sin respuesta", (int)pin);
    }
    return false;
}

esp_err_t sensores_iniciar(void)
{
    gpio_num_t encontrado = GPIO_NUM_NC;

    ESP_LOGI(ETIQUETA, "Buscando el sensor de ambiente (primero en P%d)...", (int)PIN_AMBIENTE);

    /* --- Primer intento: el pin del manual, con el modelo del proyecto ----- */
    vTaskDelay(pdMS_TO_TICKS(100));
    if (respondeComo(PIN_AMBIENTE, DHT_TYPE_AM2301)) {
        pinAmbiente = PIN_AMBIENTE;
        tipoAmbiente = DHT_TYPE_AM2301;
        ESP_LOGI(ETIQUETA, "Sensor de ambiente: AM2302 / DHT22 en GPIO %d  (+-0,5 C, +-2 %% HR)",
                 (int)pinAmbiente);
        return ESP_OK;
    }
    vTaskDelay(pdMS_TO_TICKS(2200));
    if (respondeComo(PIN_AMBIENTE, DHT_TYPE_DHT11)) {
        pinAmbiente = PIN_AMBIENTE;
        tipoAmbiente = DHT_TYPE_DHT11;
        ESP_LOGW(ETIQUETA, "Sensor de ambiente: DHT11 en GPIO %d  (menos preciso: +-2 C, +-5 %% HR)",
                 (int)pinAmbiente);
        return ESP_OK;
    }

    /* --- Segundo intento: barrido de los demás pines ---------------------- */
    ESP_LOGW(ETIQUETA, "Sin respuesta en P%d. Se prueban los demas pines de la placa:",
             (int)PIN_AMBIENTE);

    if (buscarEnTodosLosPines(DHT_TYPE_AM2301, &encontrado)) {
        pinAmbiente = encontrado;
        tipoAmbiente = DHT_TYPE_AM2301;
        ESP_LOGW(ETIQUETA, "ENCONTRADO: AM2302 / DHT22 en GPIO %d (NO en el P%d del manual)",
                 (int)pinAmbiente, (int)PIN_AMBIENTE);
        return ESP_OK;
    }

    ESP_LOGW(ETIQUETA, "Tampoco como DHT11 en el primer barrido; se repite con DHT11:");
    if (buscarEnTodosLosPines(DHT_TYPE_DHT11, &encontrado)) {
        pinAmbiente = encontrado;
        tipoAmbiente = DHT_TYPE_DHT11;
        ESP_LOGW(ETIQUETA, "ENCONTRADO: DHT11 en GPIO %d", (int)pinAmbiente);
        return ESP_OK;
    }

    /* --- Nada respondió: se informa qué revisar --------------------------- */
    pinAmbiente = PIN_AMBIENTE;
    tipoAmbiente = DHT_TYPE_AM2301;

    ESP_LOGE(ETIQUETA, "=====================================================");
    ESP_LOGE(ETIQUETA, " El sensor de ambiente NO responde en NINGUN pin.");
    ESP_LOGE(ETIQUETA, " Revise, en este orden:");
    ESP_LOGE(ETIQUETA, "  1. Que el sensor este ALIMENTADO: rojo a 3,3 V, negro a GND.");
    ESP_LOGE(ETIQUETA, "  2. Que el hilo AMARILLO de datos este firme en su pin.");
    ESP_LOGE(ETIQUETA, "  3. Que la masa sea COMUN con la placa de expansion.");
    ESP_LOGE(ETIQUETA, "  4. Si el cable es largo, resistencia de 10 kOhm entre datos y 3,3 V.");
    ESP_LOGE(ETIQUETA, "  5. Que el puente de la placa este en 3,3 V y no en 5 V.");
    ESP_LOGE(ETIQUETA, "=====================================================");
    return ESP_ERR_NOT_FOUND;
}

const char *sensores_modelo_ambiente(void)
{
    return (tipoAmbiente == DHT_TYPE_DHT11) ? "DHT11" : "AM2302 (DHT22)";
}

int sensores_pin_ambiente(void)
{
    return (int)pinAmbiente;
}

/* ---------------------------------------------------------------------------
 *  Lectura
 * -------------------------------------------------------------------------*/

esp_err_t sensores_leer_ambiente(float *temperatura, float *humedad)
{
    if (!temperatura || !humedad) return ESP_ERR_INVALID_ARG;

    float lecturaTemperatura = NAN;
    float lecturaHumedad = NAN;

    esp_err_t resultado = dht_read_float_data(tipoAmbiente, pinAmbiente,
                                              &lecturaHumedad, &lecturaTemperatura);
    if (resultado != ESP_OK) return resultado;

    if (isnan(lecturaTemperatura) || isnan(lecturaHumedad)) return ESP_ERR_INVALID_RESPONSE;
    if (lecturaTemperatura <= -40.0f || lecturaTemperatura >= 80.0f) return ESP_ERR_INVALID_RESPONSE;
    if (lecturaHumedad < 0.0f || lecturaHumedad > 100.0f) return ESP_ERR_INVALID_RESPONSE;

    *temperatura = lecturaTemperatura;
    *humedad = lecturaHumedad;
    return ESP_OK;
}

/* ===========================================================================
 *  TEMPERATURA DE LA SOLUCIÓN — DS18B20 sobre bus OneWire
 * ===========================================================================
 *
 *  SOBRE EL BUS ONEWIRE
 *  El DS18B20 no usa un protocolo de dos hilos como el AM2302: usa un solo
 *  hilo, con temporización muy estricta (pulsos de microsegundos). En ESP-IDF
 *  lo correcto es implementarlo con el periférico RMT, que genera y mide los
 *  pulsos por hardware. La alternativa —hacerlo por software— depende de que el
 *  procesador no se distraiga, y falla en cuanto entra una interrupción del
 *  WiFi. Es la misma razón por la que el driver del AM2302 necesita un bloqueo.
 *
 *  SOBRE EL PULL-UP
 *  El DS18B20 exige una resistencia de pull-up en el hilo de datos (el manual
 *  pide 4,7 kΩ). Aquí se activa ADEMÁS el pull-up interno del ESP32: no
 *  reemplaza a la resistencia externa —la documentación del componente avisa
 *  que el interno no da corriente suficiente para todos los dispositivos— pero
 *  sirve de red de seguridad y deja funcionar sin la resistencia externa en
 *  cables cortos.
 * =========================================================================*/

static onewire_bus_handle_t busSolucion = NULL;
static ds18b20_device_handle_t sensorSolucion = NULL;
static unsigned long long direccionSolucion = 0;

esp_err_t sensores_iniciar_solucion(void)
{
    /* --- 1. Instalar el bus OneWire en P32 -------------------------------- */
    onewire_bus_config_t configuracionBus = {
        .bus_gpio_num = PIN_SOLUCION,
        .flags = {
            .en_pull_up = 1,     /* pull-up interno, además del externo */
        },
    };
    /* max_rx_bytes: 1 byte de comando + 8 de número de ROM + 1 de comando. */
    onewire_bus_rmt_config_t configuracionRmt = {
        .max_rx_bytes = 10,
    };

    esp_err_t resultado = onewire_new_bus_rmt(&configuracionBus, &configuracionRmt, &busSolucion);
    if (resultado != ESP_OK) {
        ESP_LOGE(ETIQUETA, "No se pudo instalar el bus OneWire en GPIO %d (0x%x)",
                 PIN_SOLUCION, resultado);
        return resultado;
    }
    ESP_LOGI(ETIQUETA, "Bus OneWire instalado en GPIO %d (periferico RMT)", PIN_SOLUCION);

    /* --- 2. Buscar los DS18B20 conectados --------------------------------- */
    onewire_device_iter_handle_t iterador = NULL;
    resultado = onewire_new_device_iter(busSolucion, &iterador);
    if (resultado != ESP_OK) {
        ESP_LOGE(ETIQUETA, "No se pudo crear el buscador de dispositivos (0x%x)", resultado);
        return resultado;
    }

    int encontrados = 0;

    /* Recorre el bus. La búsqueda termina con ESP_ERR_NOT_FOUND, o con un error
     * si el bus no responde (por ejemplo, si falta el pull-up). */
    for (;;) {
        onewire_device_t dispositivo;
        esp_err_t busqueda = onewire_device_iter_get_next(iterador, &dispositivo);

        if (busqueda == ESP_ERR_NOT_FOUND) break;      /* no hay más dispositivos */

        if (busqueda != ESP_OK) {
            ESP_LOGW(ETIQUETA, "La busqueda en el bus termino con 0x%x", busqueda);
            break;
        }

        /* Se encontró algo en el bus: se comprueba si es un DS18B20 (hay otros
         * dispositivos OneWire con otro código de familia). */
        ds18b20_config_t configuracionSensor = {};
        ds18b20_device_handle_t candidato = NULL;

        if (ds18b20_new_device_from_enumeration(&dispositivo, &configuracionSensor, &candidato) != ESP_OK) {
            ESP_LOGW(ETIQUETA, "Hay un dispositivo OneWire que no es DS18B20 (ROM %016llX)",
                     (unsigned long long)dispositivo.address);
            continue;
        }

        encontrados++;

        if (sensorSolucion == NULL) {
            /* El primero pasa a ser el sensor en uso. */
            sensorSolucion = candidato;
            ds18b20_get_device_address(candidato, &direccionSolucion);
            /* 12 bits: la mayor precisión del DS18B20 (0,0625 °C). La conversión
             * tarda unos 750 ms, tiempo de sobra dentro de un ciclo de 5 min. */
            ds18b20_set_resolution(candidato, DS18B20_RESOLUTION_12B);
            ESP_LOGI(ETIQUETA, "DS18B20 en uso: ROM %016llX (resolucion 12 bits)",
                     direccionSolucion);
        } else {
            /* Si hubiera más de uno, se liberan: el módulo solo necesita uno. */
            ESP_LOGW(ETIQUETA, "Hay otro DS18B20 en el bus: se ignora");
            ds18b20_del_device(candidato);
        }
    }

    onewire_del_device_iter(iterador);

    if (sensorSolucion == NULL) {
        ESP_LOGE(ETIQUETA, "=====================================================");
        ESP_LOGE(ETIQUETA, " NO se encontro ningun DS18B20 en P%d.", PIN_SOLUCION);
        ESP_LOGE(ETIQUETA, " Revise, en este orden:");
        ESP_LOGE(ETIQUETA, "  1. La resistencia de 4,7 kOhm entre el hilo de");
        ESP_LOGE(ETIQUETA, "     datos y 3,3 V. Sin ella el bus no responde.");
        ESP_LOGE(ETIQUETA, "  2. El orden de los hilos: rojo a 3,3 V, amarillo a");
        ESP_LOGE(ETIQUETA, "     P%d, negro a GND.", PIN_SOLUCION);
        ESP_LOGE(ETIQUETA, "  3. Que la masa sea COMUN con la placa.");
        ESP_LOGE(ETIQUETA, "=====================================================");
        return ESP_ERR_NOT_FOUND;
    }

    ESP_LOGI(ETIQUETA, "Sensores DS18B20 encontrados: %d", encontrados);
    return ESP_OK;
}

bool sensores_hay_solucion(void)
{
    return sensorSolucion != NULL;
}

unsigned long long sensores_direccion_solucion(void)
{
    return direccionSolucion;
}

esp_err_t sensores_leer_solucion(float *temperatura)
{
    if (!temperatura) return ESP_ERR_INVALID_ARG;
    if (!sensorSolucion) return ESP_ERR_INVALID_STATE;

    /* Esta llamada bloquea el tiempo de conversión (unos 750 ms a 12 bits).
     * Es lo previsto: el ciclo de lectura es de minutos, no de milisegundos. */
    esp_err_t resultado = ds18b20_trigger_temperature_conversion_for_all(busSolucion);
    if (resultado != ESP_OK) return resultado;

    float lectura = 0.0f;
    resultado = ds18b20_get_temperature(sensorSolucion, &lectura);
    if (resultado != ESP_OK) return resultado;

    /* Rango de trabajo del DS18B20: -55 a +125 °C. Fuera de eso, la lectura es
     * un error de comunicación, no una temperatura. */
    if (lectura < -55.0f || lectura > 125.0f) return ESP_ERR_INVALID_RESPONSE;

    *temperatura = lectura;
    return ESP_OK;
}

/* ===========================================================================
 *  CONVERSIÓN DEL TDS A ppm
 * ===========================================================================
 *
 *  El módulo TDS Meter V1.0 entrega una tensión analógica, no un número de ppm.
 *  La conversión tiene dos pasos, tal como los documenta su fabricante:
 *
 *  1. COMPENSACIÓN POR TEMPERATURA. La conductividad del agua sube alrededor de
 *     2 % por cada grado. El polinomio está definido a 25 °C, así que primero se
 *     lleva la tensión medida a su equivalente a 25 °C:
 *
 *         V(25) = V(medida) / (1 + 0,02 · (T - 25))
 *
 *     Aquí es donde entra el DS18B20: sin la temperatura de la solución, este
 *     paso se hace a ciegas y el resultado se aparta varios por ciento.
 *
 *  2. POLINOMIO CÚBICO del fabricante, que relaciona esa tensión con los ppm.
 *     No es una recta: la respuesta del sensor se curva, y por eso se usa el
 *     polinomio y no una simple regla de tres.
 * =========================================================================*/

float sensores_tds_a_ppm(float voltios, float temperatura_c)
{
    if (isnan(voltios) || voltios < 0.0f) return NAN;

    /* Sin temperatura válida se usa 25 °C, que es la referencia del polinomio:
     * el factor de compensación queda en 1 y no se inventa una corrección. */
    if (isnan(temperatura_c)) temperatura_c = 25.0f;

    float compensada = voltios / (1.0f + 0.02f * (temperatura_c - 25.0f));

    float ppm = (133.42f * compensada * compensada * compensada
               - 255.86f * compensada * compensada
               + 857.39f * compensada) * 0.5f;

    if (ppm < 0.0f) ppm = 0.0f;
    return ppm;
}

float sensores_ppm_a_conductividad(float ppm)
{
    if (isnan(ppm)) return NAN;
    /* Relación habitual para soluciones nutritivas: TDS (ppm) ≈ EC (mS/cm) × 500 */
    return ppm / 500.0f;
}
