# Backend de SIGVACH — API

Servicio que expone el contrato de la API del sistema **SI.G.VA.C.H.** Es el único
componente que accede a Cloud Firestore y el lugar donde residen la validación de los
datos, la autorización por rol y las reglas de negocio. La aplicación Flutter y el
módulo de adquisición (ESP32) consumen esta API; ninguno de los dos accede a la base
de datos.

El presente documento es la base del **manual de instalación y despliegue** que se
incorpora como Anexo B de la monografía.

---

## 1. Responsabilidad del servicio

| Decisión | Dónde se toma |
|---|---|
| ¿La petición está autenticada? | Aquí, verificando el token de identidad o la clave de dispositivo |
| ¿El rol del usuario permite esta operación? | Aquí, en la dependencia de autorización |
| ¿El dato recibido es válido? | Aquí, en los esquemas de entrada |
| ¿La lectura está fuera de rango? | Aquí, en el servicio de evaluación |
| ¿Se genera una alerta? | Aquí, y la alerta queda referenciada a su lectura |
| Cómo se presenta la información | Aplicación Flutter |

## 2. Estructura

```
backend/
├── app/
│   ├── main.py               # Aplicación FastAPI: rutas, CORS y manejadores de error
│   ├── config.py             # Configuración leída del entorno
│   ├── errores.py            # Formato único de error {"codigo", "mensaje", "detalle"}
│   ├── esquemas.py           # Esquemas de entrada y salida, con la validación
│   ├── seguridad.py          # Autenticación y autorización (usuario y dispositivo)
│   ├── dependencias.py       # Proveedores de repositorios
│   ├── servicios/
│   │   ├── evaluacion.py     # Evaluación de rangos, alertas, resumen y CSV
│   │   └── lecturas.py       # Registro de una lectura y generación de su alerta
│   ├── repositorios/
│   │   ├── base.py           # Interfaz de persistencia
│   │   ├── firestore.py      # Implementación sobre Cloud Firestore
│   │   └── memoria.py        # Implementación en memoria (desarrollo y pruebas)
│   └── rutas/                # salud · lecturas · módulos · perfiles · rangos · alertas · exportaciones
├── pruebas/                  # 54 pruebas automatizadas
├── requirements.txt          # Dependencias del servicio
└── requirements-dev.txt      # Dependencias de las pruebas
```

## 3. Requisitos

- Python 3.13 o superior.
- Las dependencias de `requirements.txt`.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

## 4. Ejecución local

### 4.1 Modo de demostración, sin Firebase

Permite probar la API completa sin credenciales: el repositorio guarda los datos en
memoria y el proceso arranca con la configuración por defecto.

```bash
# Windows (PowerShell)
$env:USAR_REPOSITORIO_EN_MEMORIA="true"
$env:DEVICE_API_KEY="clave-de-demostracion"
uvicorn app.main:app --reload --port 8000
```

```bash
# Linux / macOS
USAR_REPOSITORIO_EN_MEMORIA=true DEVICE_API_KEY=clave-de-demostracion \
  uvicorn app.main:app --reload --port 8000
```

Los datos se pierden al detener el proceso. Es el modo previsto para la demostración
en vivo cuando no haya conectividad o cuando los sensores no estén calibrados.

### 4.2 Modo real, con Cloud Firestore

1. Copiar `.env.example` (en la raíz del proyecto) como `.env` y completar los valores.
2. Descargar la clave de la cuenta de servicio del proyecto de Firebase y colocarla
   **fuera del repositorio**, indicando su ruta en `GOOGLE_APPLICATION_CREDENTIALS`,
   o pegar su contenido en `FIREBASE_SERVICE_ACCOUNT_JSON`.
3. Iniciar el servicio:

```bash
uvicorn app.main:app --reload --port 8000
```

### 4.3 Comprobación

```bash
curl http://localhost:8000/api/v1/salud
```

Respuesta esperada: `{"estado":"ok","version_api":"v1","entorno":"desarrollo","base_de_datos":"conectada"}`.

## 5. Documentación del contrato

El propio servicio publica su contrato, que es el documento citado en el apartado 2.4.4
de la monografía:

- Interfaz navegable: <http://localhost:8000/docs>
- Especificación OpenAPI: <http://localhost:8000/api/v1/openapi.json>

## 6. Pruebas

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Las pruebas no requieren credenciales ni conexión: sustituyen el repositorio de
Cloud Firestore por el de memoria y el verificador de identidad por uno simulado.
La última ejecución registró 54 casos aprobados y ninguno fallido.

| Archivo | Qué verifica |
|---|---|
| `pruebas/test_evaluacion.py` | Evaluación de rangos, generación de alertas, resumen de series y exportación en CSV |
| `pruebas/test_validacion.py` | Validación de los datos de entrada, en el esquema y a través de la API (código 422 y campo rechazado) |
| `pruebas/test_api_lecturas.py` | Contrato de lecturas: recepción desde el dispositivo, registro manual, filtros, resumen y exportación |
| `pruebas/test_api_autorizacion.py` | Autenticación, autorización por rol, cuenta desactivada y acceso público al diagnóstico |

## 7. Variables de entorno

La plantilla completa está en `.env.example`, en la raíz del proyecto. Las variables
que afectan a este servicio son:

| Variable | Para qué |
|---|---|
| `PORT` | Puerto de escucha |
| `ALLOWED_ORIGINS` | Orígenes autorizados para las peticiones del navegador, separados por comas |
| `DEVICE_API_KEY` | Clave que autentica al módulo de adquisición (cabecera `X-Device-Key`) |
| `FIREBASE_PROJECT_ID` | Identificador del proyecto de Firebase |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Credenciales de la cuenta de servicio, en una sola línea |
| `GOOGLE_APPLICATION_CREDENTIALS` | Ruta al archivo de credenciales (alternativa a la anterior) |
| `USAR_REPOSITORIO_EN_MEMORIA` | Fuerza el repositorio en memoria, para demostración |
| `ROL_ADMINISTRADOR` · `ROL_OPERADOR` | Nombres de los roles que habilitan la administración y la operación |
| `MINUTOS_TOLERANCIA_RELOJ` | Tolerancia admitida para la marca de tiempo que envía el dispositivo |

## 8. Despliegue

Plataforma prevista: **Render**, capa gratuita.

1. Crear un *Web Service* apuntando al repositorio del proyecto.
2. Directorio raíz: `backend`.
3. Comando de compilación: `pip install -r requirements.txt`.
4. Comando de inicio: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. Cargar las variables de entorno en el panel del servicio (nunca en el repositorio).
6. Comprobar el despliegue consultando `/api/v1/salud` y verificar que la respuesta
   indique `"base_de_datos":"conectada"`.

**Limitación declarada.** La capa gratuita suspende el servicio tras un periodo de
inactividad, por lo que la primera petición posterior puede demorar hasta treinta
segundos. Se documenta en el apartado 2.9 y se mitiga invocando el endpoint de salud
antes de la demostración.

## 9. Índices de Cloud Firestore

Las consultas de lecturas que combinan un filtro de igualdad con un rango de fechas, y
las que ordenan por marca de tiempo, requieren un índice compuesto. Firestore devuelve
en el error un enlace directo para crearlo; los índices previstos son:

| Colección | Campos |
|---|---|
| `lecturas` | `modulo_id` (asc) · `timestamp` (desc) |
| `lecturas` | `variable` (asc) · `timestamp` (desc) |
| `alertas` | `estado` (asc) · `timestamp` (desc) |

## 10. Pendientes conocidos

- `uvicorn` y `firebase-admin` están declarados en `requirements.txt` pero no se
  instalaron en este equipo, por lo que el arranque real del servidor y la conexión con
  Cloud Firestore deben verificarse en el entorno de despliegue.
- El borrado de la cuenta de autenticación de un usuario dado de baja requiere funciones
  del lado del servidor; hoy alcanza con eliminar su perfil, según lo declarado en 2.7.
