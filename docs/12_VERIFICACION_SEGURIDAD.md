# Verificación de las reglas de seguridad de Cloud Firestore

**Proyecto:** SIGVACH — Sistema de Gestión de Variables para Cultivos Hidropónicos
**Proyecto de Firebase:** `sigvach26-bd`
**Fecha de la verificación:** jueves 17 de septiembre de 2026

---

## 1. Qué se quiso comprobar

El diseño del sistema declara una regla de arquitectura: **nadie accede a la base
de datos sin pasar por el servicio**. La aplicación web y móvil consumen la API, y
el módulo de adquisición (ESP32) publica contra esa misma API con su clave de
dispositivo. El único componente que habla con Cloud Firestore es el backend, con
su cuenta de servicio.

Las reglas de seguridad deben materializar esa regla: **ningún cliente puede leer
ni escribir las colecciones del dominio**, aunque tenga sesión iniciada. La única
excepción es la colección `usuarios`, porque el perfil se crea al registrarse y el
administrador lo administra desde el panel.

Esta verificación comprueba que las reglas publicadas cumplen lo anterior **contra
la base de datos real**, no contra una simulación.

## 2. Método

Se consultó la API REST de Cloud Firestore en dos condiciones:

| Condición | Qué representa | Resultado esperado |
|---|---|---|
| **Sin credenciales** | Un cliente anónimo, con la dirección del proyecto pero sin sesión | `403` (permiso denegado) |
| **Con la cuenta de servicio** | El backend, que no está sujeto a las reglas de seguridad | `200` (acceso permitido) |

Se probaron las cinco colecciones del dominio: `lecturas`, `alertas`,
`modulos_cultivo`, `perfiles_cultivo` y `usuarios`.

El procedimiento está implementado en `scripts/verificar_acceso_directo.py`, de
modo que la comprobación puede repetirse en cualquier momento —por ejemplo,
después de modificar las reglas— sin depender de una revisión manual.

## 3. Resultados

### Acceso anónimo (cliente sin sesión)

| Colección | Respuesta | Interpretación |
|---|---|---|
| `lecturas` | `403` | Denegado ✅ |
| `alertas` | `403` | Denegado ✅ |
| `modulos_cultivo` | `403` | Denegado ✅ |
| `perfiles_cultivo` | `403` | Denegado ✅ |
| `usuarios` | `403` | Denegado ✅ |

### Acceso con la cuenta de servicio (backend)

| Colección | Respuesta | Interpretación |
|---|---|---|
| `lecturas` | `200` | Permitido ✅ |
| `alertas` | `200` | Permitido ✅ |
| `modulos_cultivo` | `200` | Permitido ✅ |
| `perfiles_cultivo` | `200` | Permitido ✅ |
| `usuarios` | `200` | Permitido ✅ |

## 4. Conclusión

Las reglas publicadas **aislan la base de datos**: un cliente sin sesión no puede
leer ninguna colección, y el backend conserva el acceso que necesita para operar.
El resultado confirma que la única vía de acceso a los datos es la API del
servicio, que es donde se aplican las validaciones y la autorización por rol.

Conviene precisar el alcance de esta prueba: verifica la **denegación** del acceso
directo, que es la propiedad crítica. La **autorización por rol** —qué puede hacer
un operador y qué un administrador— se ejerce dentro del servicio y está cubierta
por las pruebas automáticas de la API.

## 5. Antes de publicar las reglas

La publicación se hizo después de comprobar que ningún componente del cliente
accede a las colecciones del dominio:

- La aplicación solo usa la colección `usuarios` (perfil propio y, para el
  administrador, el resto de los perfiles), que las reglas permiten.
- El correo del administrador declarado en las reglas (`admin@sigvach.com`)
  coincide con el que asigna la aplicación al crear el perfil.
- Las colecciones heredadas del proyecto del aula (`registros` y `firestore_demo`)
  corresponden a código sin uso, de modo que cerrarlas no afecta ninguna pantalla.

## 6. Cómo repetir la verificación

```powershell
cd "D:\SIGVACH-Monograf"
Proyecto SIGVACH\.venv\Scripts\python.exe Proyecto SIGVACH\scripts\verificar_acceso_directo.py
```

El programa informa el código de respuesta por colección y concluye si las reglas
siguen aislando la base de datos.
