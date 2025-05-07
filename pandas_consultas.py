import pandas as pd
from sqlalchemy import create_engine, text
import os

DATABASE_URL = "mysql+pymysql://root:rootpassword@db:3306/video_games"
engine = create_engine(DATABASE_URL)

def get_top_plataformas_mas_juegos(TOP):
    """
    Obtiene las TOP plataformas con más juegos lanzados
    """
    query = f"""
    SELECT pf.platform_name AS 'Plataforma',
           COUNT(DISTINCT gpl.game_publisher_id) AS 'Cantidad de Juegos'
    FROM platform pf
    JOIN game_platform gpl ON pf.id = gpl.platform_id
    GROUP BY pf.platform_name
    ORDER BY COUNT(DISTINCT gpl.game_publisher_id) DESC
    LIMIT {TOP}
    """
    
    df = pd.read_sql(query, engine)
    return df

def get_juegos_mas_vendidos_por_region(region_name, TOP):
    """
    Obtiene los TOP juegos más vendidos en una región específica
    """
    query = f"""
    SELECT ga.game_name AS 'Juego',
           SUM(rs.num_sales) AS 'Ventas en Región'
    FROM region_sales rs
    JOIN region r ON rs.region_id = r.id
    JOIN game_platform gpl ON rs.game_platform_id = gpl.id
    JOIN game_publisher gp ON gpl.game_publisher_id = gp.id
    JOIN game ga ON gp.game_id = ga.id
    WHERE r.region_name = :region_name
    GROUP BY ga.game_name
    ORDER BY SUM(rs.num_sales) DESC
    LIMIT {TOP}
    """
    
    df = pd.read_sql(text(query), engine, params={"region_name": region_name})
    return df

def get_lanzamientos_por_anio():
    """
    Muestra la cantidad de juegos lanzados por año
    """
    query = """
    SELECT gpl.release_year AS 'Año de Lanzamiento',
           COUNT(*) AS 'Cantidad de Juegos'
    FROM game_platform gpl
    WHERE gpl.release_year IS NOT NULL
    GROUP BY gpl.release_year
    ORDER BY gpl.release_year
    """
    
    df = pd.read_sql(query, engine)
    return df

def get_top_generos_juegos(TOP):
    """
    Obtiene los TOP géneros con más juegos
    """
    query = f"""
    SELECT COALESCE(g.genre_name, 'Desconocido') AS 'Género',
           COUNT(DISTINCT ga.id) AS 'Cantidad de Juegos'
    FROM game ga
    LEFT JOIN genre g ON ga.genre_id = g.id
    GROUP BY g.genre_name
    ORDER BY COUNT(DISTINCT ga.id) DESC
    LIMIT {TOP}
    """
    
    df = pd.read_sql(query, engine)
    return df

def get_top_juegos_menos_ventas(TOP):
    """
    Obtiene los TOP juegos con menos ventas totales
    """
    query = f"""
    SELECT ga.game_name AS 'Juego',
           SUM(rs.num_sales) AS 'Ventas Totales'
    FROM game ga
    JOIN game_publisher gp ON ga.id = gp.game_id
    JOIN game_platform gpl ON gp.id = gpl.game_publisher_id
    JOIN region_sales rs ON gpl.id = rs.game_platform_id
    GROUP BY ga.game_name
    HAVING SUM(rs.num_sales) > 0
    ORDER BY SUM(rs.num_sales) ASC
    LIMIT {TOP}
    """
    
    df = pd.read_sql(query, engine)
    return df

def get_top_publishers_juegos(TOP):
    """
    Obtiene los TOP publishers con más juegos publicados
    """
    query = f"""
    SELECT p.publisher_name AS 'Publisher',
           COUNT(DISTINCT gp.game_id) AS 'Cantidad de Juegos'
    FROM publisher p
    JOIN game_publisher gp ON p.id = gp.publisher_id
    GROUP BY p.publisher_name
    ORDER BY COUNT(DISTINCT gp.game_id) DESC
    LIMIT {TOP}
    """
    
    df = pd.read_sql(query, engine)
    return df

