# Módulo de adquisición — SIGVACH

**Componente:** módulo de adquisición del sistema SI.G.VA.C.H. · ESP32 sobre
placa de expansión, con sensores de temperatura, humedad y sólidos disueltos
**Estado:** ✅ **midiendo y publicando en producción**

Este apartado reúne el hardware del proyecto: el firmware del módulo, su
diagrama de conexionado, la documentación del prototipo y las evidencias de los
ensayos con que se verificaron los sensores.

---

## 1. Qué hace el módulo

Cada **cinco minutos**:

1. Lee los sensores instalados en el módulo de cultivo.
2. Publica cada variable en el servicio por HTTPS, autenticándose con la clave
   propia del dispositivo.
3. Si el servicio no responde —arranque en frío, corte de red o servicio
   caído—, guarda las lecturas en **memoria no volátil** y las reintenta, con la
   hora en que se midieron.

**Mide y publica; no acciona nada.** El control de actuadores quedó fuera del
alcance aprobado en la tutoría.

### Variables que mide

| Variable | Sensor | Estado |
|---|---|---|
| `temp_ambiental` | AM2302 (DHT22) | ✅ Verificado |
| `humedad` | AM2302 (DHT22) | ✅ Verificado |
| `temp_solucion` | DS18B20 (bus OneWire) | ✅ Verificado |
| `tds` | TDS Meter V1.0 | ✅ Verificado |
| `ec` | derivada del TDS (`ppm ÷ 500`) | ✅ |
| `ph` | PH-4502C | ⏳ electrodo en recuperación |
| `nivel_agua` | manual, con regla | Por diseño |

---

## 2. Contenido de esta carpeta

```
hardware/
├── LEEME.md                        este índice
├── diagrama-conexionado.png/.pdf   diagrama visual, con colores por función
├── generar_diagrama_conexionado.py regenera el diagrama si cambia una pieza
├── docs/
│   ├── plan-y-lista-de-materiales.md   decisión maqueta/cama, etapas y materiales
│   ├── inventario-de-dispositivos.md   qué es cada pieza
│   └── calibracion-del-modulo.md       procedimiento y tablas para anotar valores
├── evidencias/                     registros de los ensayos de verificación
└── firmware/                       proyecto ESP-IDF, con su propio LEEME
    ├── LEEME.md                    manual: conexionado, montaje, pruebas, problemas
    ├── CMakeLists.txt · sdkconfig.defaults · entorno_idf.ps1
    └── main/                       programa y módulos
```

---

## 3. Cómo compilar y cargar

El procedimiento completo —conexionado, orden de montaje, pruebas y problemas
frecuentes— está en **`firmware/LEEME.md`**. El resumen es:

```powershell
cd firmware
. .\entorno_idf.ps1        # activar el entorno (el punto es obligatorio)
idf.py build               # compilar
idf.py -p COM6 flash       # cargar en la placa
idf.py -p COM6 monitor     # Monitor Serie (salir con Ctrl + ])
```

**Requiere ESP-IDF v5.5.3.** El firmware se escribió sobre el marco de trabajo
nativo de Espressif, no sobre Arduino.

---

## 4. 🔒 Antes de compilar: el archivo de datos privados

El programa **no compila sin `firmware/main/configuracion.h`**. Ese archivo
contiene la red WiFi, la clave del dispositivo y el identificador del módulo, y
**no se versiona**.

Para reconstruirlo:

1. Copiar `firmware/main/configuracion.ejemplo.h` con el nombre `configuracion.h`.
2. Completar la red WiFi **(de 2,4 GHz)**, la clave del dispositivo del `.env`
   del servicio y el identificador del módulo.

> **La clave del dispositivo no se comparte ni se sube al repositorio.** Con
> ella, cualquiera podría publicar lecturas falsas en el sistema. El
> `.gitignore` —el de esta carpeta y el de la raíz del repositorio— la excluye,
> incluidas las variantes de respaldo (`configuracion.h.respaldo`, `.bueno`,
> `.old`), que también llevan el secreto adentro.

---

## 5. Los ensayos de verificación

Los cuatro sensores del montaje se verificaron con ensayos propios, cuyos
registros están en `evidencias/`:

| Archivo | Ensayo | Resultado |
|---|---|---|
| `prueba-sal-tds.txt` | Respuesta del sensor de TDS al alterar la concentración de la solución | **155 mV → 2 415 mV** (×173 en cuentas crudas) |
| `contraste-temperatura.txt` | Contraste del DS18B20 contra el AM2302 | Sonda mojada: **3,3 °C por debajo** del aire (enfriamiento por evaporación) |
| `contraste-reposo.csv` · `contraste-reposo-parte2.csv` | Convergencia de los dos termómetros en reposo | Coinciden dentro de **0,01 °C** |

**Sobre el contraste de temperatura.** La diferencia entre los dos sensores
**cambió de signo** entre un ensayo y otro (+0,65 °C con la sonda en la mano,
−2,90 °C mojada). Un desvío de calibración no puede invertirse, así que quedó
descartado: la sonda sigue fielmente su entorno térmico real y **no necesita
constante de corrección**.

---

## 6. Lo que falta

| Tarea | Depende de |
|---|---|
| Recuperar y calibrar el electrodo de pH, e instalar su divisor ÷2 | Solución de conservación (KCl) y patrones de pH 4,00 y 6,86 |
| Calibrar el sensor de TDS | Patrón de 707 ppm |
| Armar la maqueta hidropónica y medir el ciclo | Depósito con tapa, tubo, canastillas y solución nutritiva A/B/C |

El detalle está en `docs/calibracion-del-modulo.md` y en el tablero de tareas del
repositorio (`docs/TABLERO.md`).
