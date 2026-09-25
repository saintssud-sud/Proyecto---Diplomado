# ============================================================================
#  Componente principal — SI.G.VA.C.H.
#  ---------------------------------------------------------------------------
#  OJO: no agregar REQUIRES ni PRIV_REQUIRES.
#  El componente `main` recibe automáticamente TODOS los demás componentes, y
#  basta con eso. Si se declara REQUIRES, ESP-IDF deja de agregar los
#  requisitos comunes y el programa deja de encontrar cabeceras básicas
#  (falla con "esp_event.h: No such file or directory").
#  Los componentes externos (dht) se declaran en `main/idf_component.yml`.
# ============================================================================

idf_component_register(
    SRCS        "main.c"
                "sensores.c"
                "publicacion.c"
                "cola_nvs.c"
    INCLUDE_DIRS "."
)
