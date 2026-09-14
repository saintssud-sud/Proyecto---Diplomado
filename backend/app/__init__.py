"""Backend de la API de SIGVACH.

Monolito modular: un solo servicio, con separación interna por módulos
(configuración, esquemas, seguridad, servicios de dominio, repositorios y
rutas). Es el único componente que accede a Cloud Firestore.
"""

__all__ = ["__version__"]

__version__ = "1.0.0"
