/* ============================================================================
 *  SI.G.VA.C.H. — Sensores del módulo  (ESP-IDF)
 *  ---------------------------------------------------------------------------
 *  Pines de la placa de expansión:
 *     P33 · GPIO 33 · sensor de ambiente (AM2302 / DHT22, o DHT11)
 *     P32 · GPIO 32 · DS18B20 para la temperatura de la solución
 *     SVP · GPIO 36 · pH                                           (pendiente)
 *     SVN · GPIO 39 · TDS
 * ==========================================================================*/

#ifndef SENSORES_H
#define SENSORES_H

#include <stdbool.h>
#include "esp_err.h"

/* --- Pines ----------------------------------------------------------------- */
#define PIN_AMBIENTE   33   /* P33 */
#define PIN_SOLUCION   32   /* P32 */

/* ---------------------------------------------------------------------------
 *  SENSOR DE AMBIENTE (AM2302 / DHT22 / DHT11)
 * -------------------------------------------------------------------------*/

/*  Inicializa el sensor de ambiente y AVERIGUA EL MODELO.
 *
 *  El AM2302 (DHT22) y el DHT11 comparten el mismo protocolo pero distinta
 *  trama: si se le dice al driver el modelo equivocado, entrega valores
 *  inválidos. En vez de exigir que se averigüe a mano, el programa prueba
 *  primero el AM2302 —el más preciso, y el que corresponde al proyecto— y, si
 *  no responde, prueba el DHT11 informándolo por el Monitor Serie.
 *
 *  Devuelve ESP_OK si el sensor de ambiente respondió. */
esp_err_t sensores_iniciar(void);

/** Modelo de sensor de ambiente detectado, en texto ("AM2302 (DHT22)" o "DHT11"). */
const char *sensores_modelo_ambiente(void);

/** Pin en el que se encontró el sensor de ambiente (para informarlo). */
int sensores_pin_ambiente(void);

/** Lectura del ambiente. Devuelve ESP_OK y completa las dos salidas. */
esp_err_t sensores_leer_ambiente(float *temperatura, float *humedad);

/* ---------------------------------------------------------------------------
 *  TEMPERATURA DE LA SOLUCIÓN (DS18B20, bus OneWire)
 * -------------------------------------------------------------------------*/

/*  Instala el bus OneWire sobre P32 y busca los DS18B20 que haya conectados.
 *
 *  El bus se implementa con el periférico RMT, que es la forma recomendada en
 *  ESP-IDF: hace la temporización por hardware y no depende de que el
 *  procesador esté libre, como pasaría con una implementación por software.
 *
 *  Devuelve ESP_OK si encontró al menos un sensor. */
esp_err_t sensores_iniciar_solucion(void);

/** true si hay un DS18B20 detectado y en uso. */
bool sensores_hay_solucion(void);

/** Dirección ROM del DS18B20 en uso (0 si no hay ninguno). */
unsigned long long sensores_direccion_solucion(void);

/** Lectura de la temperatura de la solución. */
esp_err_t sensores_leer_solucion(float *temperatura);

/* ---------------------------------------------------------------------------
 *  CONVERSIÓN DEL TDS
 * -------------------------------------------------------------------------*/

/*  Convierte la tensión de la sonda de TDS a partes por millón.
 *
 *  `voltios` es la tensión TAL COMO LLEGA AL ADC (la sonda del TDS no lleva
 *  divisor, así que coincide con la salida AOUT del módulo).
 *
 *  `temperatura_c` es la temperatura de la solución, que aporta el DS18B20: la
 *  conductividad del agua cambia ~2 % por grado, así que sin este dato el
 *  resultado se aparta. Si no hay lectura de temperatura, se pasa 25,0 (el
 *  valor de referencia del polinomio) y el programa lo informa. */
float sensores_tds_a_ppm(float voltios, float temperatura_c);

/** Conductividad eléctrica derivada del TDS: ppm ÷ 500 = mS/cm. */
float sensores_ppm_a_conductividad(float ppm);

#endif /* SENSORES_H */
