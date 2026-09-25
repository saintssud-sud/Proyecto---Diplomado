/* ============================================================================
 *  SI.G.VA.C.H. — Cola de lecturas pendientes en memoria NO VOLÁTIL  (ESP-IDF)
 *  ---------------------------------------------------------------------------
 *  Cuando el servicio no responde —porque está arrancando en frío, porque se
 *  cortó la red o porque se cayó— la lectura no se pierde: queda guardada en la
 *  partición NVS y se reintenta en el ciclo siguiente.
 *
 *  POR QUÉ EN NVS Y NO EN MEMORIA RAM
 *  La versión de Arduino guardaba las pendientes en un arreglo en RAM. Eso
 *  significa que un corte de luz —o un reinicio del módulo— borraba todo lo que
 *  estaba esperando. En una vivienda con cortes frecuentes, eso son datos del
 *  cultivo perdidos sin que nadie se entere.
 *
 *  Con NVS las lecturas sobreviven al corte: el módulo se reinicia y sigue
 *  teniendo la lista, con su marca de tiempo original.
 *
 *  CÓMO ESTÁ ORGANIZADA
 *  Es un anillo: se escribe siempre en la misma posición rotativa, así que
 *  guardar una lectura nueva NO obliga a reescribir las anteriores. Eso importa
 *  porque la memoria flash tiene un número limitado de escrituras por celda.
 * ==========================================================================*/

#ifndef COLA_NVS_H
#define COLA_NVS_H

#include <stdbool.h>
#include "esp_err.h"

/* Máximo de lecturas guardadas. A un ciclo cada 5 minutos son 5 horas de
 * autonomía sin servicio; suficiente para un corte de luz o una caída de red,
 * y chico como para no llenar la partición NVS. */
#define COLA_MAXIMA  60

/* Una lectura que no se pudo publicar. Se guarda completa: variable, valor,
 * unidad y —esto es importante— la marca de tiempo ORIGINAL, la del momento en
 * que se midió, no la del momento en que se logre publicar. */
typedef struct {
    char  variable[16];
    char  unidad[8];
    char  momento[24];
    float valor;
} LecturaPendiente;

/** Abre la memoria de pendientes y recupera lo que hubiera de ciclos anteriores. */
esp_err_t cola_iniciar(void);

/** Cuántas lecturas están esperando. */
int cola_cuantas(void);

/** Guarda una lectura que no se pudo publicar. Si la cola está llena, descarta
 *  la más antigua para dejar sitio (es preferible perder la más vieja que la
 *  recién medida). */
esp_err_t cola_guardar(const char *variable, float valor, const char *unidad,
                       const char *momento);

/** Copia la lectura más antigua sin sacarla de la cola. false si no hay ninguna. */
bool cola_primera(LecturaPendiente *destino);

/** Saca de la cola la lectura más antigua (después de publicarla con éxito). */
esp_err_t cola_descartar_primera(void);

/** Borra todas las pendientes. */
esp_err_t cola_vaciar(void);

#endif /* COLA_NVS_H */
