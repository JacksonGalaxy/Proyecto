# Video Games Database API

Este proyecto implementa una API REST completa para gestionar y analizar una base de datos de videojuegos, utilizando FastAPI, SQLAlchemy, MySQL y herramientas de visualización de datos como Pandas, Matplotlib y Seaborn.

## 📋 Descripción

Esta aplicación proporciona una interfaz completa para acceder a datos de videojuegos, incluyendo información sobre:

- Juegos
- Plataformas
- Géneros
- Editoras (Publishers)
- Regiones
- Ventas por región

La API está diseñada para facilitar tanto consultas básicas como análisis avanzados y visualizaciones de datos.

## 🛠️ Tecnologías Utilizadas

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **Base de Datos**: MySQL
- **ORM**: SQLAlchemy
- **Análisis de Datos**: Pandas
- **Visualización**: Matplotlib, Seaborn
- **Contenedorización**: Docker, Docker Compose
- **Administración de BD**: phpMyAdmin

## 🚀 Instalación y Despliegue

### Requisitos Previos

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Pasos para el Despliegue

1. **Clonar el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd video-games-database
   ```

2. **Iniciar los servicios con Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Acceder a la API**:
   - La API estará disponible en: `http://localhost:8085`
   - La documentación de la API (Swagger UI): `http://localhost:8085/docs`
   - phpMyAdmin para administrar la base de datos: `http://localhost:8086`
     - Usuario: `root`
     - Contraseña: `rootpassword`

## 📊 Estructura de la Base de Datos

La base de datos `video_games` está formada por las siguientes tablas principales:

- **game**: Información básica de los juegos.
- **platform**: Plataformas de videojuegos.
- **publisher**: Compañías editoras.
- **genre**: Géneros de videojuegos.
- **region**: Regiones geográficas.
- **game_publisher**: Relación entre juegos y editoras.
- **game_platform**: Relación entre juegos publicados y plataformas, incluye año de lanzamiento.
- **region_sales**: Ventas de juegos por región.

## 📌 Endpoints de la API

### Endpoints Básicos

- `GET /`: Punto de entrada principal
- `GET /tables`: Lista todas las tablas de la base de datos
- `GET /tables/{table_name}`: Obtiene datos de una tabla específica

### Consultas Específicas

#### Datos Generales
- `GET /games`: Lista todos los juegos
- `GET /games/{game_id}`: Obtiene información de un juego específico por ID
- `GET /games/{game_id}/complete`: Obtiene información completa de un juego (con relaciones)
- `GET /platforms`: Lista todas las plataformas
- `GET /publishers`: Lista todas las editoras
- `GET /genres`: Lista todos los géneros
- `GET /regions`: Lista todas las regiones
- `GET /sales`: Lista datos de ventas
- `GET /game-platforms`: Lista relaciones juego-plataforma
- `GET /game-publishers`: Lista relaciones juego-editora

#### Estadísticas y Análisis
- `GET /stats/best-sellings-games/{numero}`: Top juegos más vendidos
- `GET /stats/sales-by-genre`: Ventas por género
- `GET /stats/sales-by-platform`: Ventas por plataforma
- `GET /stats/sales-by-publisher`: Ventas por editora
- `GET /stats/sales-by-year-platform`: Ventas por año y plataforma
- `GET /games/by-year/{year}`: Juegos filtrados por año de lanzamiento

### Visualizaciones con Pandas (HTML)

Los siguientes endpoints devuelven tablas HTML formateadas:

- `GET /pandas/top-plataformas/{top}`: Top plataformas con más juegos
- `GET /pandas/juegos-region/{region}/{top}`: Top juegos más vendidos por región
- `GET /pandas/lanzamientos-anio`: Lanzamientos por año
- `GET /pandas/top-generos/{top}`: Top géneros con más juegos
- `GET /pandas/juegos-menos-ventas/{top}`: Top juegos con menos ventas
- `GET /pandas/top-publishers/{top}`: Top publishers con más juegos

### Visualizaciones con Seaborn (Imágenes)

Los siguientes endpoints devuelven imágenes de gráficos:

- `GET /seaborn/top-editoras/{top}`: Gráfico de editoras con más juegos
- `GET /seaborn/distribucion-ventas`: Distribución de ventas por región
- `GET /seaborn/lanzamientos-anio/{top}`: Años con más lanzamientos
- `GET /seaborn/top-juegos-ventas/{top}`: Juegos con más ventas totales
- `GET /seaborn/top-generos-ventas/{top}`: Géneros con más ventas totales
- `GET /seaborn/ventas-plataforma-region/{top}`: Ventas por plataforma y región

## 📊 Ejemplos de Uso

### Consultar los 5 juegos más vendidos

```bash
curl -X GET "http://localhost:8085/stats/best-sellings-games/5"
```

Respuesta:
```json
{
  "message": "Top 5 juegos más vendidos",
  "count": 5,
  "data": [
    {
      "id": 1,
      "game_name": "Wii Sports",
      "genre": "Sports",
      "total_sales": 82.74
    },
    ...
  ]
}
```

### Obtener un gráfico de los top 10 géneros con más ventas

Acceder a:
```
http://localhost:8085/seaborn/top-generos-ventas/10
```
(Devuelve una imagen PNG del gráfico)

### Obtener tabla HTML de lanzamientos por año

Acceder a:
```
http://localhost:8085/pandas/lanzamientos-anio
```
(Devuelve una tabla HTML formateada)

## 🔍 Análisis Avanzados

El sistema permite realizar análisis avanzados mediante la combinación de datos de múltiples tablas:

- Tendencias de ventas a lo largo del tiempo
- Comparación de rendimiento entre plataformas
- Análisis de géneros más populares por región
- Evolución de las ventas por editora

## 🗂️ Estructura de Archivos

- `database.py`: Configuración y funciones para interactuar con la base de datos
- `main.py`: Aplicación principal FastAPI con todos los endpoints
- `pandas_consultas.py`: Consultas específicas utilizando Pandas
- `seaborn_graficas.py`: Generación de gráficos utilizando Seaborn
- `formato.py`: Utilidades para formatear tablas HTML
- `docker-compose.yml`: Configuración de los servicios Docker
- `requirements.txt`: Dependencias del proyecto

## 🔧 Personalización

### Modificar la Conexión a la Base de Datos

La conexión a la base de datos está configurada en los archivos `database.py`, `pandas_consultas.py` y `seaborn_graficas.py`. Si necesitas modificar los parámetros de conexión, actualiza la variable `DATABASE_URL`.

### Añadir Nuevas Consultas

Para añadir nuevas consultas:

1. Define las funciones de consulta en `pandas_consultas.py` o `seaborn_graficas.py`
2. Agrega nuevos endpoints en `main.py` que utilicen estas funciones

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Haz un fork del repositorio
2. Crea una rama para tu característica (`git checkout -b feature/amazing-feature`)
3. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está licenciado bajo [incluir tu licencia preferida].

## 📧 Contacto

[Tu Nombre/Equipo] - [tu@email.com]

---

Desarrollado con ❤️ utilizando FastAPI, MySQL y herramientas de análisis de datos.
