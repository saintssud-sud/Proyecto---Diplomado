# Tablero de tareas — SIGVACH (Kanban)

**Herramienta:** tablero versionado en el repositorio (`docs/TABLERO.md`)
**Límite de trabajo en curso (WIP):** 2 tarjetas
**Marco de trabajo:** Scrum reducido con sprints de una semana, según el apartado 2.2

---

## 📋 Backlog

| ID | Tarea | Requisito | Prioridad |
|---|---|---|---|
| T-14 | Consulta y filtrado de lecturas por módulo, variable y periodo | RF-07 | Must |
| T-15 | Historial y tendencia de una variable con su resumen | RF-12 | Should |
| T-16 | Exportación del historial en CSV | RF-13 | Could |
| T-17 | Gestión de usuarios y asignación de roles (panel de administración) | RF-02 | Should |
| T-18 | Rol de solo consulta (Invitado): autorización de lectura | RF-02 · RNF-03 | Should |
| T-19 | Verificación de adaptabilidad en tres anchos (320, 768 y 1920 px) | RNF-04 · RNF-06 | Should |
| T-20 | Publicar las reglas de seguridad de Cloud Firestore | RNF-03 | Must |
| T-21 | Primer despliegue público del servicio y de la aplicación web | Requisito mínimo 1 | Must |

---

## 🔄 En curso (límite: 2)

| ID | Tarea | Requisito | Responsable | Inicio |
|---|---|---|---|---|
| T-11 | **E1 · Perfil de proyecto:** capítulo 1, metodología y requisitos | Entregable E1 | Autor | 14/09 |
| T-12 | Migración de las pantallas del dominio al servicio (5 de 7 cerradas) | RF-03 · RF-08 · RF-10 · RF-11 | Autor | 14/09 |

---

## ✅ Hecho

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
| T-09 | Juego de pruebas del servicio (69 casos) y verificador estructural de Dart | RNF-01 · 2.8 | 14/09 |
| T-10 | Índices compuestos de Firestore declarados y desplegados | RNF-01 | 15/09 |
| T-13 | Recurso del perfil de usuario en el servicio (`/api/v1/usuarios/perfil`) | RF-02 · Requisito mínimo 3 | 15/09 |

---

**Estado al cierre de la Semana 1 (15 de septiembre de 2026):** 11 tareas terminadas · 2 en curso · 8 en el backlog.
