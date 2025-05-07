# Video Games Database API

Este proyecto implementa una API REST en FastAPI para el análisis y consulta de una base de datos de videojuegos. El sistema está containerizado con Docker y utiliza MySQL como base de datos, proporcionando endpoints para consultas básicas y análisis con visualizaciones.

## Estructura del Proyecto

El proyecto sigue una arquitectura modular orientada a servicios con los siguientes componentes:

- **API RESTful con FastAPI**: Implementa endpoints para consultar datos de videojuegos, plataformas, editores y ventas.
- **Base de Datos MySQL**: Almacena información sobre juegos, plataformas, editores, géneros y ventas por región.
- **Visualización de Datos**: Genera gráficos con Matplotlib y Seaborn para análisis visual.
- **Docker**: Conteneriza la aplicación para facilitar el despliegue.

## Tecnologías Utilizadas

- **Backend**: FastAPI, Python 3.11
- **Base de Datos**: MySQL 8.0
- **ORM**: SQLAlchemy
- **Análisis de Datos**: Pandas, Matplotlib, Seaborn
- **Contenedores**: Docker, Docker Compose
- **Administración de BD**: PHPMyAdmin

## Instalación y Configuración

### Prerrequisitos

- Docker y Docker Compose
- Git

### Pasos para la Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/video-games-api.git
   cd video-games-api
   ```

2. Iniciar los contenedores con Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. La API estará disponible en:
   ```
   http://localhost:8085
   ```

4. PHPMyAdmin para administrar la base de datos:
   ```
   http://localhost:8086
   ```
   Usuario: root
   Contraseña: rootpassword

## Estructura de la Base de Datos

El sistema utiliza una base de datos relacional con las siguientes tablas principales:

- **game**: Información básica de cada videojuego
- **platform**: Plataformas de juegos (PS4, Xbox, etc.)
- **publisher**: Compañías editoras de los juegos
- **genre**: Géneros de videojuegos
- **region**: Regiones geográficas para ventas
- **game_publisher**: Relación entre juegos y editores
- **game_platform**: Relación entre juegos y plataformas
- **region_sales**: Ventas de juegos por plataforma y región

## API Endpoints

### Endpoints Básicos

- `GET /`: Verificación de estado de la API
- `GET /tables`: Lista todas las tablas de la base de datos
- `GET /tables/{table_name}`: Obtiene datos de una tabla específica

### Endpoints de Juegos

- `GET /games`: Lista todos los juegos
- `GET /games/{game_id}`: Obtiene un juego por ID
- `GET /games/{game_id}/complete`: Obtiene información completa de un juego con sus relaciones
- `GET /games/by-year/{year}`: Filtra juegos por año de lanzamiento

### Endpoints de Estadísticas

- `GET /stats/best-sellings-games/{numero}`: Top N juegos más vendidos
- `GET /stats/sales-by-genre`: Ventas agrupadas por género
- `GET /stats/sales-by-platform`: Ventas agrupadas por plataforma
- `GET /stats/sales-by-publisher`: Ventas agrupadas por editor
- `GET /stats/sales-by-year-platform`: Ventas por año y plataforma

### Endpoints con Pandas (HTML)

- `GET /pandas/top-generos/{top}`: Top géneros con más juegos
- `GET /pandas/juegos-menos-ventas/{top}`: Juegos con menos ventas
- `GET /pandas/top-publishers/{top}`: Publishers con más juegos

### Endpoints con Seaborn (Gráficos)

- `GET /seaborn/top-juegos-ventas/{top}`: Gráfico de juegos con más ventas
- `GET /seaborn/top-generos-ventas/{top}`: Gráfico de géneros con más ventas
- `GET /seaborn/ventas-plataforma-region/{top}`: Gráfico de ventas por plataforma y región

## Ejemplos de Uso

### Obtener los 10 juegos más vendidos

```bash
curl -X GET "http://localhost:8085/stats/best-sellings-games/10"
```

### Visualizar géneros con más juegos

Navegar a:
```
http://localhost:8085/pandas/top-generos/5
```

### Obtener gráfico de ventas por plataforma y región

Navegar a:
```
http://localhost:8085/seaborn/ventas-plataforma-region/10
```

## Módulos Principales

- **main.py**: Punto de entrada de la aplicación FastAPI y definición de endpoints
- **database.py**: Funciones para la conexión y consulta a la base de datos
- **formato.py**: Formateo de respuestas HTML para visualización en navegador
- **pandas_consultas.py**: Consultas y análisis utilizando Pandas
- **seaborn_graficas.py**: Generación de gráficos con Seaborn

## Configuración del Entorno

La configuración del entorno se realiza mediante variables de entorno en el archivo docker-compose.yml:

- **DATABASE_URL**: URL de conexión a la base de datos
- **MYSQL_ROOT_PASSWORD**: Contraseña de root para MySQL
- **MYSQL_DATABASE**: Nombre de la base de datos
- **MYSQL_USER**: Usuario para la base de datos
- **MYSQL_PASSWORD**: Contraseña para el usuario

## Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Haz commit de tus cambios (`git commit -m 'Add some amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.

## Contacto

[Tu Nombre] - [tu@email.com]

Link del proyecto: [https://github.com/tu-usuario/video-games-api](https://github.com/tu-usuario/video-games-api)
