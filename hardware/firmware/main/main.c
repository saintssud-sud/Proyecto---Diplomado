/* ============================================================================
 *  SI.G.VA.C.H. — Firmware del módulo de adquisición  (ESP-IDF)
 *  Placa: ESP32 (38 pines) sobre placa de expansión
 *  ---------------------------------------------------------------------------
 *  Versión ESP-IDF del firmware del módulo. Sustituye a la versión de Arduino.
 *
 *  Qué hace este programa:
 *    1. Inicializa el conversor analógico con su CALIBRACIÓN DE FÁBRICA: en
 *       lugar de estimar los voltios con una regla de tres, le pide al chip la
 *       tensión real en milivoltios.
 *    2. Se conecta a la red WiFi y sincroniza la hora por Internet (SNTP).
 *    3. Lee los sensores del módulo.
 *    4. Publica cada variable en el servicio SI.G.VA.C.H. por HTTPS, con la
 *       clave del dispositivo en la cabecera X-Device-Key.
 *    5. Si el servicio no responde, guarda las lecturas en memoria NO VOLÁTIL
 *       (NVS) y las reintenta: sobreviven incluso a un corte de luz.
 *
 *  ETAPA ACTUAL: cimientos. Se validan el entorno, el ADC calibrado y la red.
 *  Los sensores digitales (DS18B20 y DHT22) y la publicación se agregan después.
 *
 *  NOTA SOBRE LA CALIBRACIÓN DEL ADC
 *  El ESP32 clásico admite UN SOLO esquema de calibración: el de AJUSTE DE
 *  RECTA (line fitting), que se apoya en los valores grabados en el eFuse de
 *  fábrica. El esquema de AJUSTE DE CURVA (curve fitting) existe únicamente en
 *  los ESP32-S2, S3 y C3: pedirlo en este chip no compila.
 * ==========================================================================*/

#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"

#include "esp_log.h"
#include "esp_err.h"
#include "esp_event.h"
#include "esp_rom_sys.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "esp_sntp.h"
#include "nvs_flash.h"

#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"

#include "configuracion.h"
#include "sensores.h"
#include "publicacion.h"
#include "cola_nvs.h"

static const char *ETIQUETA = "SIGVACH";

/* ---------------------------------------------------------------------------
 *  1. CONEXIONADO  (pines de la placa de expansión)
 * -------------------------------------------------------------------------*/
/* En el ESP32 clásico, ADC1 se reparte así:
 *    GPIO36 = canal 0   GPIO37 = canal 1   GPIO38 = canal 2   GPIO39 = canal 3
 *    GPIO32 = canal 4   GPIO33 = canal 5   GPIO34 = canal 6   GPIO35 = canal 7
 * Se usan SOLO canales del ADC1: el ADC2 no funciona con el WiFi encendido. */
#define CANAL_PH   ADC_CHANNEL_0   /* SVP · GPIO 36 · salida Po del PH-4502C */
#define CANAL_TDS  ADC_CHANNEL_3   /* SVN · GPIO 39 · salida AOUT del TDS V1.0 */

/* Pines del ADC1 que la placa de expansión expone como entradas analógicas.
 *
 * Sirven para el diagnóstico de conexionado: el programa mide la dispersión de
 * las muestras en cada uno y dice cuál tiene un sensor de verdad y cuál está al
 * aire. Se excluyen a propósito P32 (GPIO 32) y P33 (GPIO 33), ocupados por el
 * DS18B20 y el AM2302: leerlos como analógicos falsearía su señal digital.
 *
 * En el ESP32 clásico, ADC1 se reparte así:
 *    GPIO36 = canal 0 · GPIO39 = canal 3 · GPIO34 = canal 6 · GPIO35 = canal 7
 * Los cuatro son pines de entrada, que es justo lo que el ADC necesita. */
typedef struct {
    adc_channel_t canal;
    const char *etiqueta;
    const char *previsto;
} CanalAnalogico;

static const CanalAnalogico CANALES_ANALOGICOS[] = {
    { ADC_CHANNEL_0, "SVP GPIO 36", "pH"          },
    { ADC_CHANNEL_3, "SVN GPIO 39", "TDS"         },
    { ADC_CHANNEL_6, "P34 GPIO 34", "alternativa" },
    { ADC_CHANNEL_7, "P35 GPIO 35", "alternativa" },
};
#define CUANTOS_CANALES (sizeof(CANALES_ANALOGICOS) / sizeof(CANALES_ANALOGICOS[0]))

/* ---------------------------------------------------------------------------
 *  2. MUESTREO
 * -------------------------------------------------------------------------*/
#define MUESTRAS_ANALOGICAS  30    /* se toma la mediana: descarta el ruido */

/* Espera de asentamiento del conversor después de inicializarlo.
 * Medido: a 1 s las lecturas todavía son falsas (~142 mV en todos los canales);
 * a 5 s ya son reales. Se toma un margen cómodo. */
#define ASENTAMIENTO_ADC_MS  4000

#if PUBLICAR_EN_SERVICIO
#define SEGUNDOS_ENTRE_LECTURAS  300   /* 5 minutos: 10 % de la cuota diaria */
#else
#define SEGUNDOS_ENTRE_LECTURAS  5     /* en prueba: para ver que todo responde */
#endif

/* Tensión de referencia por defecto, en milivoltios. Solo se usa si el eFuse
 * no trae valores de calibración (el firmware avisa por el Monitor Serie). */
#define TENSION_REFERENCIA_MV  1100

/* ---------------------------------------------------------------------------
 *  3. Objetos del conversor analógico
 * -------------------------------------------------------------------------*/
static adc_oneshot_unit_handle_t adc1;
static adc_cali_handle_t cali_adc1 = NULL;

#if PUBLICAR_EN_SERVICIO
/* Grupo de eventos para saber si hay red. */
static EventGroupHandle_t grupoRed;
#define RED_CONECTADA  BIT0
#endif

/* ---------------------------------------------------------------------------
 *  4. Utilidades
 * -------------------------------------------------------------------------*/

/** Ordena de menor a mayor (inserción: son 30 valores). */
static void ordenar(int *valores, int cuantos)
{
    for (int i = 1; i < cuantos; i++) {
        int actual = valores[i];
        int j = i - 1;
        while (j >= 0 && valores[j] > actual) {
            valores[j + 1] = valores[j];
            j--;
        }
        valores[j + 1] = actual;
    }
}

/** Formatea un flotante con dos decimales SIN usar %f.
 *  El formateo "nano" de newlib puede no soportar %f, y en ese caso el Monitor
 *  Serie mostraría basura. Esta función arma el texto con enteros. */
static void formatear2(char *destino, size_t tamano, float valor)
{
    bool negativo = valor < 0.0f;
    if (negativo) valor = -valor;

    int entero = (int)valor;
    int decimales = (int)((valor - (float)entero) * 100.0f + 0.5f);
    if (decimales >= 100) {          /* redondeo que desborda: 2,997 -> 3,00 */
        entero++;
        decimales -= 100;
    }
    snprintf(destino, tamano, "%s%d.%02d", negativo ? "-" : "", entero, decimales);
}

/** Convierte milivoltios a texto con dos decimales, en voltios. */
static void milivoltiosAVoltios(char *destino, size_t tamano, int milivoltios)
{
    char temporal[16];
    formatear2(temporal, sizeof(temporal), (float)milivoltios / 1000.0f);
    snprintf(destino, tamano, "%s V", temporal);
}

/* ---------------------------------------------------------------------------
 *  5. Conversor analógico con calibración de fábrica
 * -------------------------------------------------------------------------*/

/** Crea el esquema de calibración por AJUSTE DE RECTA para el ADC1.
 *
 *  En el ESP32 clásico este es el único esquema disponible. El manejador vale
 *  para toda la unidad: la calibración depende de la ATENUACIÓN, no del canal,
 *  así que el mismo sirve para el pH (GPIO 36) y para el TDS (GPIO 39).
 *
 *  Devuelve NULL si el chip no tiene calibración grabada; en ese caso se sigue
 *  funcionando con la estimación lineal, como hacía la versión de Arduino. */
static adc_cali_handle_t crearCalibracion(void)
{
    adc_cali_line_fitting_efuse_val_t valorEfuse;

    if (adc_cali_scheme_line_fitting_check_efuse(&valorEfuse) != ESP_OK) {
        ESP_LOGW(ETIQUETA, "El chip no informa calibracion de fabrica");
        return NULL;
    }

    const char *origen =
        (valorEfuse == ADC_CALI_LINE_FITTING_EFUSE_VAL_EFUSE_TP)   ? "dos puntos grabados en el eFuse" :
        (valorEfuse == ADC_CALI_LINE_FITTING_EFUSE_VAL_EFUSE_VREF) ? "tension de referencia del eFuse" :
                                                                     "valor por defecto (sin eFuse)";
    ESP_LOGI(ETIQUETA, "Calibracion de fabrica: %s", origen);

    adc_cali_handle_t manejador = NULL;
    adc_cali_line_fitting_config_t configuracion = {
        .unit_id      = ADC_UNIT_1,
        .atten        = ADC_ATTEN_DB_12,
        .bitwidth     = ADC_BITWIDTH_DEFAULT,
        .default_vref = TENSION_REFERENCIA_MV,   /* campo exclusivo del ESP32 */
    };

    esp_err_t resultado = adc_cali_create_scheme_line_fitting(&configuracion, &manejador);
    if (resultado != ESP_OK) {
        ESP_LOGW(ETIQUETA, "No se pudo crear la calibracion (0x%x)", resultado);
        return NULL;
    }
    return manejador;
}

static void iniciarConversor(void)
{
    adc_oneshot_unit_init_cfg_t configuracionUnidad = {
        .unit_id = ADC_UNIT_1,
    };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&configuracionUnidad, &adc1));

    /* Atenuación de 12 dB: permite leer hasta unos 3,1 V, que es lo que llega
     * desde el divisor del pH (2,5 V) y desde el TDS (hasta 2,3 V). */
    adc_oneshot_chan_cfg_t configuracionCanal = {
        .bitwidth = ADC_BITWIDTH_DEFAULT,
        .atten    = ADC_ATTEN_DB_12,
    };
    for (size_t i = 0; i < CUANTOS_CANALES; i++) {
        ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1, CANALES_ANALOGICOS[i].canal,
                                                   &configuracionCanal));
    }

    cali_adc1 = crearCalibracion();

    ESP_LOGI(ETIQUETA, "Conversor listo. Calibracion de fabrica: %s",
             cali_adc1 ? "SI" : "NO (se usa estimacion lineal)");

    /* --- ASENTAMIENTO DEL CONVERSOR -------------------------------------
     * El ADC del ESP32 NO queda listo al inicializarlo: tarda varios segundos
     * en estabilizarse. Mientras tanto informa ~142 mV con dispersión cero en
     * TODOS los canales, que es un valor que parece una señal limpia y no lo es.
     *
     * Está comprobado midiendo: a los 951 ms y a los 1031 ms la lectura es
     * falsa; a los 5 s ya es real. Descartar muestras sueltas no alcanza,
     * porque el problema no está en la primera conversión sino en el chip.
     *
     * De aquí la importancia de esta espera: sin ella, la PRIMERA lectura que
     * el módulo publique después de encenderse sería falsa. */
    vTaskDelay(pdMS_TO_TICKS(ASENTAMIENTO_ADC_MS));
    for (size_t i = 0; i < CUANTOS_CANALES; i++) {
        int descarte = 0;
        adc_oneshot_read(adc1, CANALES_ANALOGICOS[i].canal, &descarte);
    }
    ESP_LOGI(ETIQUETA, "Conversor asentado (%d ms de espera)", ASENTAMIENTO_ADC_MS);
}

/** Lee un canal y devuelve la tensión en milivoltios, tomando la mediana.
 *
 *  Informa además:
 *    - `crudo`: la mediana de las muestras crudas.
 *    - `dispersion`: la diferencia entre la mayor y la menor de las 30 muestras.
 *
 *  La dispersión es el dato que distingue una señal real de un pin al aire:
 *  con un sensor conectado es chica y estable; con el pin flotando, el ADC
 *  capta ruido y la dispersión se dispara. Sirve para no confundir "hay señal"
 *  con "hay ruido". */
static int leerMilivoltios(adc_channel_t canal, int *crudo, int *dispersion)
{
    int valores[MUESTRAS_ANALOGICAS];

    /* DESCARTE OBLIGATORIO (tres conversiones, con pausa).
     *
     * Dos motivos:
     *  1. La primera conversión de un canal recién inicializado no es
     *     confiable: devuelve 0 y arrastra la mediana hacia abajo.
     *  2. Cambiar de canal deja el ADC sin asentar. El condensador de muestreo
     *     tiene que cargarse desde la fuente, y con una entrada de alta
     *     impedancia —un pin al aire, por ejemplo— eso tarda bastante más que
     *     una conversión. Descartando una sola, el barrido de canales informaba
     *     "señal estable" en pines que en realidad estaban flotando.
     *
     * Sin este descarte, la primera lectura de cada canal informa ~142 mV con
     * dispersión cero: parece una señal buena y no lo es. */
    for (int i = 0; i < 3; i++) {
        int descarte = 0;
        ESP_ERROR_CHECK(adc_oneshot_read(adc1, canal, &descarte));
        esp_rom_delay_us(1500);
    }

    for (int i = 0; i < MUESTRAS_ANALOGICAS; i++) {
        ESP_ERROR_CHECK(adc_oneshot_read(adc1, canal, &valores[i]));
    }
    ordenar(valores, MUESTRAS_ANALOGICAS);

    int mediana = valores[MUESTRAS_ANALOGICAS / 2];
    if (crudo) *crudo = mediana;
    if (dispersion) *dispersion = valores[MUESTRAS_ANALOGICAS - 1] - valores[0];

    if (cali_adc1) {
        int milivoltios = 0;
        if (adc_cali_raw_to_voltage(cali_adc1, mediana, &milivoltios) == ESP_OK) {
            return milivoltios;
        }
    }
    /* Sin calibración: estimación lineal (la conversión que usaba Arduino). */
    return (int)((float)mediana * 3300.0f / 4095.0f + 0.5f);
}

#if PUBLICAR_EN_SERVICIO
/* ---------------------------------------------------------------------------
 *  6. Red WiFi y hora   (solo cuando se publica en el servicio)
 * -------------------------------------------------------------------------*/

/** Hora actual en formato ISO 8601 UTC. Vacío si el reloj aún no sincronizó. */
static void marcaDeTiempoISO(char *destino, size_t tamano)
{
    destino[0] = '\0';
    time_t ahora = time(NULL);
    if (ahora < 1700000000) return;          /* el reloj todavía no es válido */
    struct tm partes;
    gmtime_r(&ahora, &partes);
    strftime(destino, tamano, "%Y-%m-%dT%H:%M:%SZ", &partes);
}

static void manejadorRed(void *argumento, esp_event_base_t base, int32_t id, void *datos)
{
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();

    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        xEventGroupClearBits(grupoRed, RED_CONECTADA);
        ESP_LOGW(ETIQUETA, "WiFi caido: se reintenta la conexion");
        esp_wifi_connect();

    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t *evento = (ip_event_got_ip_t *)datos;
        ESP_LOGI(ETIQUETA, "Conectado. Direccion IP: " IPSTR, IP2STR(&evento->ip_info.ip));
        xEventGroupSetBits(grupoRed, RED_CONECTADA);
    }
}

static void iniciarRed(void)
{
    grupoRed = xEventGroupCreate();

    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t configuracion = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&configuracion));

    ESP_ERROR_CHECK(esp_event_handler_instance_register(
        WIFI_EVENT, ESP_EVENT_ANY_ID, &manejadorRed, NULL, NULL));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(
        IP_EVENT, IP_EVENT_STA_GOT_IP, &manejadorRed, NULL, NULL));

    wifi_config_t red = { 0 };
    strlcpy((char *)red.sta.ssid,     NOMBRE_WIFI, sizeof(red.sta.ssid));
    strlcpy((char *)red.sta.password, CLAVE_WIFI,  sizeof(red.sta.password));
    red.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &red));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(ETIQUETA, "Conectando a la red %s", NOMBRE_WIFI);
}

/** Espera la conexión hasta el límite indicado. Devuelve true si hay red. */
static bool esperarRed(int segundos)
{
    EventBits_t bits = xEventGroupWaitBits(grupoRed, RED_CONECTADA,
                                           pdFALSE, pdTRUE,
                                           pdMS_TO_TICKS(segundos * 1000));
    return (bits & RED_CONECTADA) != 0;
}

/** true si hay red en este momento, sin esperar. */
static bool hayRed(void)
{
    return (xEventGroupGetBits(grupoRed) & RED_CONECTADA) != 0;
}

/** Pone la hora por Internet (SNTP). */
static void iniciarHora(void)
{
    esp_sntp_setoperatingmode(ESP_SNTP_OPMODE_POLL);
    esp_sntp_setservername(0, "pool.ntp.org");
    esp_sntp_setservername(1, "time.nist.gov");
    esp_sntp_init();

    for (int i = 0; i < 20 && time(NULL) < 1700000000; i++) {
        vTaskDelay(pdMS_TO_TICKS(500));
    }
    char momento[24];
    marcaDeTiempoISO(momento, sizeof(momento));
    ESP_LOGI(ETIQUETA, "Hora del dispositivo: %s",
             momento[0] ? momento : "sin sincronizar (el servicio pondra la hora)");
}
#endif /* PUBLICAR_EN_SERVICIO */

/* ---------------------------------------------------------------------------
 *  7. Un ciclo de lectura
 * -------------------------------------------------------------------------*/

/** Describe el estado de una entrada analógica según la dispersión de sus muestras. */
static const char *estadoDeLaEntrada(int dispersion)
{
    if (dispersion < 40)  return "senal estable";
    if (dispersion < 150) return "algo ruidosa";
    return "nada conectado (pin flotando)";
}

/** Mide la dispersión de cada entrada analógica y dice cuál tiene un sensor
 *  conectado.
 *
 *  Es la herramienta para no confundir "hay señal" con "hay ruido": una entrada
 *  al aire puede entregar cualquier tensión, pero salta mucho entre muestras, y
 *  eso se ve en la dispersión. Una señal de sensor de verdad es estable. */
static void diagnosticarEntradasAnalogicas(void)
{
    /* El ADC necesita un momento para asentarse después de inicializar. */
    vTaskDelay(pdMS_TO_TICKS(500));

    ESP_LOGI(ETIQUETA, "--- Entradas analogicas (dispersion de %d muestras) ---",
             MUESTRAS_ANALOGICAS);
    ESP_LOGI(ETIQUETA, "%-13s %-12s %10s %10s  %s",
             "PIN", "PREVISTO", "MEDIANA", "DISPERSION", "ESTADO");

    for (size_t i = 0; i < CUANTOS_CANALES; i++) {
        int crudo = 0, dispersion = 0;
        int milivoltios = leerMilivoltios(CANALES_ANALOGICOS[i].canal, &crudo, &dispersion);
        ESP_LOGI(ETIQUETA, "%-13s %-12s %7d mV %10d  %s",
                 CANALES_ANALOGICOS[i].etiqueta,
                 CANALES_ANALOGICOS[i].previsto,
                 milivoltios, dispersion,
                 estadoDeLaEntrada(dispersion));
    }
    ESP_LOGI(ETIQUETA, "-------------------------------------------------------");
    ESP_LOGI(ETIQUETA, "Un sensor conectado da una dispersion de decenas;");
    ESP_LOGI(ETIQUETA, "una entrada al aire salta cientos o miles de cuentas.");
}

/** Publica una variable si el modo lo permite, informando el resultado.
 *
 *  Un valor inválido NO se publica: es preferible dejar el hueco antes que
 *  ensuciar el historial del cultivo con un dato que en realidad no se midió.
 *
 *  Si el envío falla, la lectura se guarda en memoria no volátil para
 *  reintentarla — salvo que el fallo sea un rechazo del contrato, que no se
 *  arregla reintentando. */
static void publicar(const char *variable, float valor, const char *unidad)
{
#if PUBLICAR_EN_SERVICIO
    if (isnan(valor)) {
        ESP_LOGW(ETIQUETA, "  %-15s sin dato: no se publica", variable);
        return;
    }

    /* La marca de tiempo se toma AHORA, antes de intentar el envío. Si el envío
     * falla y la lectura va a la cola, tiene que quedar con la hora en que se
     * MIDIÓ, no con la hora del reintento. */
    char momento[24];
    publicacion_marca_de_tiempo(momento, sizeof(momento));

    int resultado = publicacion_enviar(variable, valor, unidad, momento);

    if (resultado == 200 || resultado == 201) {
        char texto[16];
        formatear2(texto, sizeof(texto), valor);
        ESP_LOGI(ETIQUETA, "  %-15s %10s %-6s  ->  %s", variable, texto, unidad,
                 publicacion_describir_resultado(resultado));
        return;
    }

    ESP_LOGW(ETIQUETA, "  %-15s NO se publico: %s (codigo %d)", variable,
             publicacion_describir_resultado(resultado), resultado);

    /* Un rechazo del contrato —clave inválida (401), módulo inexistente (404) o
     * valor/unidad fuera de contrato (422)— no se arregla con el tiempo. Guardar
     * esas lecturas solo llenaría la cola con datos que nunca se van a aceptar. */
    if (resultado == 401 || resultado == 404 || resultado == 422) {
        ESP_LOGE(ETIQUETA, "  Se descarta: reintentarla no la arreglaria");
        return;
    }

    /* Fallo de red o servicio caído: esto sí puede resolverse después. */
    if (cola_guardar(variable, valor, unidad, momento) == ESP_OK) {
        ESP_LOGW(ETIQUETA, "  %-15s guardada en memoria no volatil (quedan %d)",
                 variable, cola_cuantas());
    }
#else
    (void)variable; (void)valor; (void)unidad;
#endif
}

/** Reintenta las lecturas guardadas en ciclos anteriores.
 *
 *  Publica siempre la más antigua primero y, si esa falla, se detiene: no tiene
 *  sentido insistir con las siguientes mientras el servicio siga sin responder.
 *  Las que sí se publican se sacan de la cola, así el progreso no se pierde. */
static void publicarPendientes(void)
{
#if PUBLICAR_EN_SERVICIO
    if (cola_cuantas() == 0) return;
    if (!hayRed()) {
        ESP_LOGW(ETIQUETA, "Hay %d lectura(s) en la cola, pero no hay red",
                 cola_cuantas());
        return;
    }

    ESP_LOGI(ETIQUETA, "Quedan %d lectura(s) guardada(s): se reintentan", cola_cuantas());

    while (cola_cuantas() > 0) {
        LecturaPendiente pendiente;
        if (!cola_primera(&pendiente)) {
            cola_descartar_primera();   /* entrada ilegible: se saca y se sigue */
            continue;
        }

        int resultado = publicacion_enviar(pendiente.variable, pendiente.valor,
                                           pendiente.unidad, pendiente.momento);
        if (resultado != 200 && resultado != 201) {
            ESP_LOGW(ETIQUETA, "  %s sigue sin publicarse: se conserva",
                     pendiente.variable);
            break;
        }

        char texto[16];
        formatear2(texto, sizeof(texto), pendiente.valor);
        ESP_LOGI(ETIQUETA, "  recuperada: %-15s %10s %-6s  (medida el %s)",
                 pendiente.variable, texto, pendiente.unidad,
                 pendiente.momento[0] ? pendiente.momento : "sin hora registrada");
        cola_descartar_primera();
    }

    ESP_LOGI(ETIQUETA, "Quedan %d lectura(s) en la cola", cola_cuantas());
#endif
}

static void cicloDeLectura(void)
{
    /* --- Sensor de ambiente: temperatura y humedad ------------------------ */
    float temperaturaAmbiente = NAN, humedadAmbiente = NAN;
    esp_err_t lecturaAmbiente = sensores_leer_ambiente(&temperaturaAmbiente, &humedadAmbiente);

    if (lecturaAmbiente == ESP_OK) {
        char textoTemperatura[16], textoHumedad[16];
        formatear2(textoTemperatura, sizeof(textoTemperatura), temperaturaAmbiente);
        formatear2(textoHumedad, sizeof(textoHumedad), humedadAmbiente);
        ESP_LOGI(ETIQUETA, "Ambiente -> %s C   %s %% HR", textoTemperatura, textoHumedad);
    } else {
        ESP_LOGW(ETIQUETA, "Ambiente -> sin respuesta (%s)", esp_err_to_name(lecturaAmbiente));
    }

    /* --- Temperatura de la solución (DS18B20) ----------------------------- */
    float temperaturaSolucion = NAN;
    esp_err_t lecturaSolucion = sensores_leer_solucion(&temperaturaSolucion);

    if (lecturaSolucion == ESP_OK) {
        char textoSolucion[16];
        formatear2(textoSolucion, sizeof(textoSolucion), temperaturaSolucion);
        ESP_LOGI(ETIQUETA, "Solucion -> %s C", textoSolucion);
    } else {
        ESP_LOGW(ETIQUETA, "Solucion -> sin respuesta (%s)", esp_err_to_name(lecturaSolucion));
    }

    /* --- Entradas analógicas --------------------------------------------- */
    int crudoPH = 0, crudoTDS = 0, dispPH = 0, dispTDS = 0;
    int mvPH  = leerMilivoltios(CANAL_PH,  &crudoPH,  &dispPH);
    int mvTDS = leerMilivoltios(CANAL_TDS, &crudoTDS, &dispTDS);

    char voltiosPH[16], voltiosTDS[16];
    milivoltiosAVoltios(voltiosPH,  sizeof(voltiosPH),  mvPH);
    milivoltiosAVoltios(voltiosTDS, sizeof(voltiosTDS), mvTDS);

    /* Mientras se arma el módulo, estos voltajes son la referencia para
     * calibrar: con los patrones de pH se anotan las dos tensiones.
     * La dispersión dice si la señal es de fiar o es solo ruido. */
    ESP_LOGI(ETIQUETA, "pH  -> %6d mV (%s) crudo %4d  dispersion %4d  %s",
             mvPH, voltiosPH, crudoPH, dispPH, estadoDeLaEntrada(dispPH));
    ESP_LOGI(ETIQUETA, "TDS -> %6d mV (%s) crudo %4d  dispersion %4d  %s",
             mvTDS, voltiosTDS, crudoTDS, dispTDS, estadoDeLaEntrada(dispTDS));

    /* Conversión a ppm. La compensación por temperatura usa la lectura del
     * DS18B20: es la razón de ser de ese sensor en este montaje. */
    float ppm = sensores_tds_a_ppm((float)mvTDS / 1000.0f, temperaturaSolucion);
    if (!isnan(ppm)) {
        char textoPpm[16], textoEc[16];
        formatear2(textoPpm, sizeof(textoPpm), ppm);
        formatear2(textoEc, sizeof(textoEc), sensores_ppm_a_conductividad(ppm));

        bool hayTemperatura = sensores_hay_solucion() && !isnan(temperaturaSolucion);
        ESP_LOGI(ETIQUETA, "  -> %s ppm   %s mS/cm   (compensado con %s)",
                 textoPpm, textoEc,
                 hayTemperatura ? "la temperatura de la solucion" : "25.0 C por defecto");
    }

    /* --- Publicación en el servicio --------------------------------------- */
#if PUBLICAR_EN_SERVICIO
    if (!hayRed()) {
        ESP_LOGW(ETIQUETA, "Sin red: este ciclo no se publica");
        return;
    }
#endif

    /* Las unidades deben coincidir EXACTAMENTE con el catálogo del servicio,
     * que vive en `backend/app/esquemas.py` (CATALOGO_VARIABLES). Si no
     * coinciden, el servicio rechaza la lectura con un 422.
     *
     * Ojo con las temperaturas: la unidad es "°C", con el símbolo de grado, no
     * "C". Con "C" el servicio responde 422 y la lectura se pierde. */
    publicar("temp_ambiental", temperaturaAmbiente, "°C");
    publicar("humedad",        humedadAmbiente,     "%");
    publicar("temp_solucion",  temperaturaSolucion, "°C");
    publicar("tds",            ppm,                 "ppm");
    publicar("ec",             sensores_ppm_a_conductividad(ppm), "mS/cm");
}

/* ---------------------------------------------------------------------------
 *  8. Arranque
 * -------------------------------------------------------------------------*/

void app_main(void)
{
    ESP_LOGI(ETIQUETA, "=================================================");
    ESP_LOGI(ETIQUETA, " SI.G.VA.CH. - modulo de adquisicion (ESP-IDF)");
    ESP_LOGI(ETIQUETA, "=================================================");

    /* La memoria no volátil es obligatoria para el WiFi y, más adelante, para
     * guardar las lecturas que no se pudieron publicar. */
    esp_err_t resultado = nvs_flash_init();
    if (resultado == ESP_ERR_NVS_NO_FREE_PAGES || resultado == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        resultado = nvs_flash_init();
    }
    ESP_ERROR_CHECK(resultado);
    ESP_LOGI(ETIQUETA, "Memoria no volatil (NVS) lista");

    /* Se abre la cola de pendientes: si el módulo se reinició con lecturas sin
     * publicar, quedan disponibles desde el arranque. */
    cola_iniciar();

    iniciarConversor();

    esp_err_t ambiente = sensores_iniciar();
    ESP_LOGI(ETIQUETA, "Ambiente en uso: %s en GPIO %d (%s)",
             sensores_modelo_ambiente(), sensores_pin_ambiente(),
             ambiente == ESP_OK ? "responde" : "SIN RESPUESTA");

    sensores_iniciar_solucion();

    diagnosticarEntradasAnalogicas();

#if PUBLICAR_EN_SERVICIO
    iniciarRed();
    if (esperarRed(30)) {
        iniciarHora();
        ESP_LOGI(ETIQUETA, "Modulo: %s | Servicio: %s", MODULO_ID, HOST_API);
    } else {
        ESP_LOGW(ETIQUETA, "Sin red por ahora: se reintenta en el proximo ciclo");
    }
#else
    ESP_LOGI(ETIQUETA, "Modo de prueba: no se usa WiFi ni el servicio.");
    ESP_LOGI(ETIQUETA, "Complete NOMBRE_WIFI y CLAVE_WIFI y ponga "
                       "PUBLICAR_EN_SERVICIO en 1 para publicar.");
#endif

    /* Bucle principal.
     * Primero se reintenta lo que quedó pendiente y después se mide: así, si el
     * servicio volvió, se descarga la cola antes de agregar lecturas nuevas. */
    while (true) {
        publicarPendientes();
        cicloDeLectura();
        vTaskDelay(pdMS_TO_TICKS(SEGUNDOS_ENTRE_LECTURAS * 1000));
    }
}
