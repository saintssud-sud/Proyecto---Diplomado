"""Repositorios de persistencia.

`base` define la interfaz que el backend necesita, `firestore` la implementa
sobre Cloud Firestore para el despliegue real y `memoria` la implementa en
memoria para el desarrollo local y las pruebas automatizadas. `cache` envuelve a
cualquiera de las dos con la memoria intermedia de las consultas de lecturas, que
es lo que sostiene el RNF-01 (rendimiento) sin cambiar el contrato de la API.
"""
