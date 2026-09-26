# Tablero de tareas — SIGVACH (Kanban)

**Herramienta:** tablero versionado en el repositorio (`docs/TABLERO.md`)
**Límite de trabajo en curso (WIP):** 2 tarjetas
**Marco de trabajo:** Scrum reducido con sprints de una semana, según el apartado 2.2

---

## 📋 Backlog

| ID | Tarea | Requisito | Prioridad |
|---|---|---|---|
| T-30 | Recuperar el electrodo de pH (24 a 48 h en KCl) e instalar su divisor ÷2 | RF-04 | Must |
| T-31 | Calibrar el sensor de pH con las soluciones patrón 4,00 y 6,86 | 2.8 · calibración | Must |
| T-32 | Calibrar el sensor de TDS con el patrón de 707 ppm | 2.8 · calibración | Must |
| T-19 | Verificación de adaptabilidad con capturas en tres anchos (320, 768 y 1920 px) | RNF-04 · RNF-06 | Should |

---

## 🔄 En curso (límite: 2)

| ID | Tarea | Requisito | Responsable | Inicio |
|---|---|---|---|---|
| T-28 | Montaje de la maqueta hidropónica y ensayos del módulo sobre el cultivo | RF-05 · Requisito mínimo 1 | Autor | 23/09 |
| T-29 | Entregable E2: vertical funcional desplegada, documento y evidencias | Entregable E2 | Autor | 22/09 |

---

## ✅ Hecho

### Semana 1 (30/08 al 15/09)

| ID | Tarea | Requisito | Fecha |
|---|---|---|---|
| T-01 | Repositorio inicializado con historial progresivo y README | Requisito mínimo 5 y 6 | 30/08 |
| T-02 | Configuración de credenciales por variables de entorno y plantilla `.env.example` | Requisito mínimo 7 | 31/08 |
| T-03 | Autenticación con Firebase y resolución del rol en el servidor | RF-01 · Requisito mínimo 2 | 11/09 |
| T-04 | Servicio REST propio (FastAPI) con el contrato `/api/v1` y validación de entradas | RF-05 · Requisito mínimo 8 | 12/09 |
| T-05 | Modelo de datos en Cloud Firestore y repositorio intercambiable en memoria | Requisito mínimo 3 | 12/09 |
| T-06 | Evaluación de lecturas contra el rango del perfil y generación de alertas | RF-09 · RF-10 | 13/09 |
| T-07 | Panel de visualización con los cuatro estados de vista | RF-11 · Requisito mínimo 4 | 13/09 |
| T-08 | Autenticación del módulo de adquisición por clave de dispositivo | RF-05 · RNF-03 | 13/09 |
| T-09 | Juego de pruebas del servicio y verificador estructural de Dart | RNF-01 · 2.8 | 14/09 |
| T-10 | Índices compuestos de Firestore declarados y desplegados | RNF-01 | 15/09 |
| T-13 | Recurso del perfil de usuario en el servicio (`/api/v1/usuarios/perfil`) | RF-02 · Requisito mínimo 3 | 15/09 |

### Semana 2 (16 al 22/09)

| ID | Tarea | Requisito | Fecha |
|---|---|---|---|
| T-12 | Migración de las siete pantallas del dominio al servicio | RF-03 · RF-08 · RF-10 · RF-11 | 17/09 |
| T-14 | Consulta y filtrado de lecturas por módulo, variable y periodo | RF-07 | 17/09 |
| T-15 | Historial y tendencia de una variable con su resumen | RF-12 | 17/09 |
| T-16 | Exportación del historial en CSV | RF-13 | 17/09 |
| T-18 | Rol de solo consulta (Invitado): autorización de lectura | RF-02 · RNF-03 | 17/09 |
| T-20 | Reglas de seguridad de Cloud Firestore publicadas y verificadas | RNF-03 | 17/09 |
| T-21 | Primer despliegue público: aplicación web, servicio en Render y archivo instalable de Android | Requisito mínimo 1 | 17/09 |
| T-11 | **E1 · Perfil de proyecto:** capítulo 1, metodología y requisitos | Entregable E1 | 19/09 |
| T-26 | Verificación de los antecedentes contra los documentos originales | 1.1 · 2.8 | 22/09 |
| T-25 | Trazabilidad de quién registró la lectura (`registrado_por`) | RF-06 · RNF-08 | 22/09 |
| T-17 | Gestión de cuentas desde el servicio (listar, consultar, modificar y eliminar) | RF-02 | 22/09 |
| T-24 | Simulador del módulo de adquisición para el E2 | RF-05 | 22/09 |

### Semana 3 (23 al 25/09)

| ID | Tarea | Requisito | Fecha |
|---|---|---|---|
| T-22 | **Módulo de adquisición real:** firmware sobre ESP-IDF, con calibración de fábrica del convertidor analógico, cola de lecturas en memoria no volátil y publicación por HTTPS validando el certificado del servidor | RF-05 · Requisito mínimo 1 | 23/09 |
| T-23 | Verificación de los cuatro sensores del módulo con ensayos propios: contraste del DS18B20 contra el AM2302, prueba de la sal del TDS y comprobación de la compensación por temperatura | 2.8 | 23/09 |
| T-27 | Alineación del vocabulario de roles con el alcance aprobado (administrador y operador) | RF-02 | 24/09 |
| T-33 | **Prototipo versionado:** firmware, diagrama, documentación y evidencias de los ensayos, con la clave del dispositivo fuera del repositorio | Requisito mínimo 5 | 25/09 |
| T-35 | **Panel de usuarios migrado al servicio** (cierra la observación B-1): deja de leer Firestore directamente y usa las operaciones de administración del contrato, con las reglas de seguridad alineadas al vocabulario de roles vigente | RF-02 | 25/09 |
| T-34 | **Guion de la demostración** del E2 y de la defensa, con el módulo real como protagonista, plan de contingencia y las preguntas previsibles del tribunal | Entregable E2 · Defensa | 25/09 |
| T-36 | **Identidad y rol en el menú lateral:** el encabezado presenta el nombre de la cuenta y el tipo de rol que el servicio le reconoce, consultado al abrir el menú, en lugar del saludo genérico | RF-01 · RF-02 | 25/09 |

---

## 📊 Estado del sistema al 25 de septiembre de 2026

| Elemento | Estado |
|---|---|
| **Contrato de la API** | 32 operaciones |
| **Pruebas automatizadas** | **199** — 106 del servicio y 93 de la aplicación |
| **Confirmaciones** | 123, repartidas en 13 días distintos |
| **Aplicación publicada** | `https://sigvach26-bd.web.app` |
| **Servicio publicado** | `https://sigvach-api.onrender.com` |
| **Módulo de adquisición** | Midiendo y publicando cinco variables en producción |

**Estado al cierre de la Semana 3:** 30 tareas terminadas · 2 en curso · 4 en el backlog.

> **Sobre la tarea T-29.** El entregable E2 permanece en la columna «En curso»: el
> documento está redactado, pero la entrega no se ha subido al aula virtual, que es
> parte de la tarea. Por eso no figura también entre las terminadas.

> **Sobre el módulo de adquisición.** El firmware está versionado en `hardware/`.
> El archivo `configuracion.h` —que contiene la clave del dispositivo y la red
> WiFi— queda fuera del repositorio, excluido tanto por el `.gitignore` de la
> carpeta del firmware como por el de la raíz. La plantilla
> `configuracion.ejemplo.h` sí se versiona.
