from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List
import os
import matplotlib
matplotlib.use('Agg')  # Usar backend no interactivo

# Importar desde database.py correctamente
from database import get_db, get_tables, get_table_data, execute_query, get_table_to_dataframe, create_bar_chart

# Importar los módulos nuevos
from formato import tabla_formato
from pandas_consultas import get_top_generos_juegos, get_top_juegos_menos_ventas, get_top_publishers_juegos
from seaborn_graficas import get_top_juegos_ventas, get_top_generos_ventas, get_ventas_plataforma_region

# Crear la app FastAPI
app = FastAPI(title="Game Database API")

# Agregar middleware CORS para permitir solicitudes desde el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las orígenes en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar la base de datos al iniciar la aplicación
@app.on_event("startup")
def startup():
    try:
        # Simplemente verificamos la conexión a la base de datos
        db = next(get_db())
        print("✅ Conexión a la base de datos exitosa")
        db.close()
    except Exception as e:
        print(f"❌ Error durante la inicialización: {str(e)}")

# Endpoint raíz
@app.get("/")
def read_root():
    return {"message": "Game Database API is running"}

# Endpoint para listar tablas
@app.get("/tables")
def list_tables():
    try:
        tables = get_tables()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tablas: {str(e)}")

# Endpoint para obtener datos de una tabla
@app.get("/tables/{table_name}")
def get_table(table_name: str, limit: int = 100):
    try:
        data = get_table_data(table_name, limit)
        return {"table": table_name, "data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos de la tabla: {str(e)}")

# Endpoints básicos para cada tabla
@app.get("/games")
def get_games(limit: int = 100):
    try:
        data = get_table_data("game", limit)
        return {"data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener juegos: {str(e)}")

@app.get("/games/{game_id}")
def get_game_by_id(game_id: int):
    try:
        # Usamos parámetros para evitar inyección SQL
        query = "SELECT * FROM game WHERE id = :game_id"
        data = execute_query(query, {"game_id": game_id})
        if not data:
            raise HTTPException(status_code=404, detail=f"Juego con ID {game_id} no encontrado")
        return {"data": data[0]}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener juego: {str(e)}")

@app.get("/platforms")
def get_platforms(limit: int = 100):
    try:
        data = get_table_data("platform", limit)
        return {"data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener plataformas: {str(e)}")

@app.get("/publishers")
def get_publishers(limit: int = 100):
    try:
        data = get_table_data("publisher", limit)
        return {"data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener publishers: {str(e)}")

@app.get("/genres")
def get_genres(limit: int = 100):
    try:
        data = get_table_data("genre", limit)
        return {"data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener géneros: {str(e)}")

@app.get("/regions")
def get_regions(limit: int = 100):
    try:
        data = get_table_data("region", limit)
        return {"data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener regiones: {str(e)}")

@app.get("/sales")
def get_sales(limit: int = 100):
    try:
        data = get_table_data("region_sales", limit)
        return {"data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas: {str(e)}")

@app.get("/game-platforms")
def get_game_platforms(limit: int = 100):
    try:
        data = get_table_data("game_platform", limit)
        return {"data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener relaciones juego-plataforma: {str(e)}")

@app.get("/game-publishers")
def get_game_publishers(limit: int = 100):
    try:
        data = get_table_data("game_publisher", limit)
        return {"data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener relaciones juego-publisher: {str(e)}")

# Endpoint para obtener juego por ID con información completa (relaciones)
@app.get("/games/{game_id}/complete")
def get_game_complete(game_id: int):
    try:
        # Primero verificamos si el juego existe
        game_exists_query = "SELECT id FROM game WHERE id = :game_id"
        game_exists = execute_query(game_exists_query, {"game_id": game_id})
        
        if not game_exists:
            raise HTTPException(status_code=404, detail=f"Juego con ID {game_id} no encontrado")
        
        # Obtener datos básicos del juego
        game_query = """
        SELECT g.*
        FROM game g
        WHERE g.id = :game_id
        """
        game_data = execute_query(game_query, {"game_id": game_id})
        
        # Verificar si existe un genre_id y obtener el nombre del género
        genre_name = None
        if game_data and 'genre_id' in game_data[0] and game_data[0]['genre_id'] is not None:
            genre_query = "SELECT genre_name FROM genre WHERE id = :genre_id"
            genre_result = execute_query(genre_query, {"genre_id": game_data[0]['genre_id']})
            if genre_result:
                genre_name = genre_result[0]['genre_name']
        
        # Añadir el nombre del género a los datos del juego
        if game_data and genre_name:
            game_data[0]['genre_name'] = genre_name
            
        # Obtener plataformas del juego
        platforms_query = """
        SELECT p.id, p.platform_name, gp.release_year
        FROM platform p
        JOIN game_platform gp ON p.id = gp.platform_id
        WHERE gp.game_publisher_id IN (
            SELECT id FROM game_publisher WHERE game_id = :game_id
        )
        """
        platforms = execute_query(platforms_query, {"game_id": game_id})
        
        # Obtener publishers del juego
        publishers_query = """
        SELECT pu.id, pu.publisher_name
        FROM publisher pu
        JOIN game_publisher gp ON pu.id = gp.publisher_id
        WHERE gp.game_id = :game_id
        """
        publishers = execute_query(publishers_query, {"game_id": game_id})
        
        # Obtener ventas por región
        sales_query = """
        SELECT r.region_name, rs.num_sales as sales
        FROM region_sales rs
        JOIN region r ON rs.region_id = r.id
        JOIN game_platform gp ON rs.game_platform_id = gp.id
        WHERE gp.game_publisher_id IN (
            SELECT id FROM game_publisher WHERE game_id = :game_id
        )
        """
        sales = execute_query(sales_query, {"game_id": game_id})
        
        # Crear respuesta completa
        response = {
            "game": game_data[0],
            "platforms": platforms,
            "publishers": publishers,
            "sales": sales
        }
        
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener información completa del juego: {str(e)}")

# Endpoint para obtener los juegos más vendidos
@app.get("/stats/best-sellings-games/{numero}")
def get_best_selling_games(numero: int):
    try:
        # Validar que el número sea positivo
        if numero <= 0:
            raise HTTPException(status_code=400, detail="El número debe ser mayor que cero")
        
        # Consulta para sumar las ventas de cada juego a través de todas las regiones
        query = """
        SELECT 
            g.id,
            g.game_name,
            COALESCE(gen.genre_name, 'Desconocido') as genre,
            SUM(rs.num_sales) as total_sales
        FROM 
            game g
        LEFT JOIN 
            genre gen ON g.genre_id = gen.id
        JOIN 
            game_publisher gp ON g.id = gp.game_id
        JOIN 
            game_platform gpl ON gp.id = gpl.game_publisher_id
        JOIN 
            region_sales rs ON gpl.id = rs.game_platform_id
        GROUP BY 
            g.id, g.game_name, gen.genre_name
        ORDER BY 
            total_sales DESC
        LIMIT :limite
        """
        
        best_selling_games = execute_query(query, {"limite": numero})
        
        if not best_selling_games:
            return {"message": "No se encontraron datos de ventas", "data": []}
        
        # Formatear los resultados para mejor presentación
        for game in best_selling_games:
            if 'total_sales' in game:
                # Redondear a 2 decimales para mejor presentación
                game['total_sales'] = round(float(game['total_sales']), 2)
            
        return {
            "message": f"Top {numero} juegos más vendidos",
            "count": len(best_selling_games),
            "data": best_selling_games
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los juegos más vendidos: {str(e)}")

# Endpoint para obtener ventas por género
@app.get("/stats/sales-by-genre")
def get_sales_by_genre():
    try:
        query = """
        SELECT 
            COALESCE(g.genre_name, 'Desconocido') as genre,
            SUM(rs.num_sales) as total_sales
        FROM 
            region_sales rs
        JOIN 
            game_platform gp ON rs.game_platform_id = gp.id
        JOIN 
            game_publisher gpu ON gp.game_publisher_id = gpu.id
        JOIN 
            game ga ON gpu.game_id = ga.id
        LEFT JOIN 
            genre g ON ga.genre_id = g.id
        GROUP BY 
            g.genre_name
        ORDER BY 
            total_sales DESC
        """
        
        sales_by_genre = execute_query(query)
        
        if not sales_by_genre:
            return {"message": "No se encontraron datos de ventas por género", "data": []}
        
        # Formatear los resultados para mejor presentación
        for genre in sales_by_genre:
            if 'total_sales' in genre:
                genre['total_sales'] = round(float(genre['total_sales']), 2)
            
        return {
            "message": "Ventas totales por género",
            "count": len(sales_by_genre),
            "data": sales_by_genre
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas por género: {str(e)}")

# Endpoint para obtener ventas por plataforma
@app.get("/stats/sales-by-platform")
def get_sales_by_platform():
    try:
        query = """
        SELECT 
            p.platform_name,
            SUM(rs.num_sales) as total_sales
        FROM 
            region_sales rs
        JOIN 
            game_platform gp ON rs.game_platform_id = gp.id
        JOIN 
            platform p ON gp.platform_id = p.id
        GROUP BY 
            p.platform_name
        ORDER BY 
            total_sales DESC
        """
        
        sales_by_platform = execute_query(query)
        
        if not sales_by_platform:
            return {"message": "No se encontraron datos de ventas por plataforma", "data": []}
        
        # Formatear los resultados para mejor presentación
        for platform in sales_by_platform:
            if 'total_sales' in platform:
                platform['total_sales'] = round(float(platform['total_sales']), 2)
            
        return {
            "message": "Ventas totales por plataforma",
            "count": len(sales_by_platform),
            "data": sales_by_platform
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas por plataforma: {str(e)}")

# Endpoint para obtener ventas por publisher
@app.get("/stats/sales-by-publisher")
def get_sales_by_publisher():
    try:
        query = """
        SELECT 
            pu.publisher_name,
            SUM(rs.num_sales) as total_sales
        FROM 
            region_sales rs
        JOIN 
            game_platform gp ON rs.game_platform_id = gp.id
        JOIN 
            game_publisher gpu ON gp.game_publisher_id = gpu.id
        JOIN 
            publisher pu ON gpu.publisher_id = pu.id
        GROUP BY 
            pu.publisher_name
        ORDER BY 
            total_sales DESC
        """
        
        sales_by_publisher = execute_query(query)
        
        if not sales_by_publisher:
            return {"message": "No se encontraron datos de ventas por publisher", "data": []}
        
        # Formatear los resultados para mejor presentación
        for publisher in sales_by_publisher:
            if 'total_sales' in publisher:
                publisher['total_sales'] = round(float(publisher['total_sales']), 2)
            
        return {
            "message": "Ventas totales por publisher",
            "count": len(sales_by_publisher),
            "data": sales_by_publisher
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas por publisher: {str(e)}")

# Endpoint para obtener ventas por año y plataforma
@app.get("/stats/sales-by-year-platform")
def get_sales_by_year_platform():
    try:
        query = """
        SELECT 
            gp.release_year as year,
            p.platform_name,
            SUM(rs.num_sales) as total_sales
        FROM 
            region_sales rs
        JOIN 
            game_platform gp ON rs.game_platform_id = gp.id
        JOIN 
            platform p ON gp.platform_id = p.id
        WHERE
            gp.release_year IS NOT NULL
        GROUP BY 
            gp.release_year, p.platform_name
        ORDER BY 
            gp.release_year DESC, total_sales DESC
        """
        
        sales_by_year_platform = execute_query(query)
        
        if not sales_by_year_platform:
            return {"message": "No se encontraron datos de ventas por año y plataforma", "data": []}
        
        # Formatear los resultados para mejor presentación
        for entry in sales_by_year_platform:
            if 'total_sales' in entry:
                entry['total_sales'] = round(float(entry['total_sales']), 2)
            
        return {
            "message": "Ventas totales por año y plataforma",
            "count": len(sales_by_year_platform),
            "data": sales_by_year_platform
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas por año y plataforma: {str(e)}")

# Endpoint para filtrar juegos por año de lanzamiento
@app.get("/games/by-year/{year}")
def get_games_by_year(year: str):
    try:
        if year.lower() == "all":
            # Mostrar todos los juegos organizados por año
            query = """
            SELECT 
                g.id,
                g.game_name,
                COALESCE(gen.genre_name, 'Desconocido') as genre,
                gp.release_year as year,
                p.platform_name,
                pu.publisher_name
            FROM 
                game g
            LEFT JOIN 
                genre gen ON g.genre_id = gen.id
            JOIN 
                game_publisher gpu ON g.id = gpu.game_id
            JOIN 
                publisher pu ON gpu.publisher_id = pu.id
            JOIN 
                game_platform gp ON gpu.id = gp.game_publisher_id
            JOIN 
                platform p ON gp.platform_id = p.id
            WHERE
                gp.release_year IS NOT NULL
            ORDER BY 
                gp.release_year DESC, g.game_name
            """
            games = execute_query(query)
            message = "Todos los juegos organizados por año"
        else:
            # Intentar convertir el año a entero
            try:
                year_int = int(year)
            except ValueError:
                raise HTTPException(status_code=400, detail="El año debe ser un número o 'all'")
            
            # Filtrar juegos por el año específico
            query = """
            SELECT 
                g.id,
                g.game_name,
                COALESCE(gen.genre_name, 'Desconocido') as genre,
                gp.release_year as year,
                p.platform_name,
                pu.publisher_name
            FROM 
                game g
            LEFT JOIN 
                genre gen ON g.genre_id = gen.id
            JOIN 
                game_publisher gpu ON g.id = gpu.game_id
            JOIN 
                publisher pu ON gpu.publisher_id = pu.id
            JOIN 
                game_platform gp ON gpu.id = gp.game_publisher_id
            JOIN 
                platform p ON gp.platform_id = p.id
            WHERE
                gp.release_year = :year
            ORDER BY 
                g.game_name
            """
            games = execute_query(query, {"year": year_int})
            message = f"Juegos lanzados en el año {year}"
        
        if not games:
            return {"message": "No se encontraron juegos para el criterio especificado", "data": []}
            
        return {
            "message": message,
            "count": len(games),
            "data": games
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener juegos por año: {str(e)}")

# NUEVOS ENDPOINTS PARA CONSULTAS PANDAS

@app.get("/pandas/top-generos/{top}", response_class=HTMLResponse)
def get_top_generos(top: int = 10):
    """Endpoint para obtener los géneros con más juegos usando pandas"""
    try:
        df = get_top_generos_juegos(top)
        return tabla_formato(df, f"Top {top} Géneros con Más Juegos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener top géneros: {str(e)}")

@app.get("/pandas/juegos-menos-ventas/{top}", response_class=HTMLResponse)
def get_juegos_menos_ventas(top: int = 10):
    """Endpoint para obtener los juegos con menos ventas usando pandas"""
    try:
        df = get_top_juegos_menos_ventas(top)
        return tabla_formato(df, f"Top {top} Juegos con Menos Ventas")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener juegos con menos ventas: {str(e)}")

@app.get("/pandas/top-publishers/{top}", response_class=HTMLResponse)
def get_publishers_mas_juegos(top: int = 10):
    """Endpoint para obtener los publishers con más juegos usando pandas"""
    try:
        df = get_top_publishers_juegos(top)
        return tabla_formato(df, f"Top {top} Publishers con Más Juegos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener top publishers: {str(e)}")

# NUEVOS ENDPOINTS PARA GRÁFICAS SEABORN

@app.get("/seaborn/top-juegos-ventas/{top}")
def generate_top_juegos_ventas(top: int = 10):
    """Endpoint para generar gráfico de los juegos con más ventas"""
    try:
        return get_top_juegos_ventas(top)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar gráfico de ventas: {str(e)}")

@app.get("/seaborn/top-generos-ventas/{top}")
def generate_top_generos_ventas(top: int = 10):
    """Endpoint para generar gráfico de los géneros con más ventas"""
    try:
        return get_top_generos_ventas(top)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar gráfico de géneros: {str(e)}")

@app.get("/seaborn/ventas-plataforma-region/{top}")
def generate_ventas_plataforma_region(top: int = 10):
    """Endpoint para generar gráfico de ventas por plataforma y región"""
    try:
        return get_ventas_plataforma_region(top)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar gráfico de plataformas por región: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)