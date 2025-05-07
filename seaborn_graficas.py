from fastapi import Response
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from sqlalchemy import create_engine, text

# Configuración de la conexión a la base de datos
DATABASE_URL = "mysql+pymysql://root:rootpassword@db:3306/video_games"
engine = create_engine(DATABASE_URL)

def get_top_editoras_por_cantidad_de_juegos(TOP):
    # Gráfica de barras – Las editoras con más juegos publicados
    query = f"""
    SELECT pu.publisher_name AS publisher, 
           COUNT(*) AS total_games
    FROM publisher pu
    JOIN game_publisher gp ON pu.id = gp.publisher_id
    GROUP BY pu.publisher_name
    ORDER BY total_games DESC
    LIMIT {TOP}
    """
    
    df = pd.read_sql(query, engine)
    
    plt.figure(figsize=(max(10, len(df)*0.8), 6))
    grafica = sns.barplot(x='publisher', y='total_games', data=df, palette='coolwarm')
    
    plt.title(f"TOP {TOP} editoras con más juegos publicados")
    plt.ylabel("Cantidad de juegos")
    plt.xlabel("Editora")
    grafica.set_xticklabels(grafica.get_xticklabels(), rotation=10, ha='right')
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()
    return Response(content=buffer.read(), media_type="image/png")


def get_distribucion_ventas_por_region():
    # Gráfica de pastel – Distribución global de ventas por región
    query = """
    SELECT r.region_name, 
           SUM(rs.num_sales) AS total_sales
    FROM region_sales rs
    JOIN region r ON rs.region_id = r.id
    GROUP BY r.region_name
    ORDER BY total_sales DESC
    """
    
    df = pd.read_sql(query, engine)
    
    plt.figure(figsize=(14, 10))
    plt.pie(df['total_sales'], labels=df['region_name'], autopct='%1.1f%%', colors=plt.cm.Set3.colors)
    plt.axis('equal')
    plt.title("Distribución global de ventas por región")
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()
    return Response(content=buffer.read(), media_type="image/png")


def get_juegos_mas_lanzados_por_anio(TOP):
    # Gráfica de líneas – Años con más lanzamientos de videojuegos
    query = f"""
    SELECT gpl.release_year AS release_year, 
           COUNT(*) AS num_games
    FROM game_platform gpl
    WHERE gpl.release_year IS NOT NULL
    GROUP BY gpl.release_year
    ORDER BY num_games DESC
    LIMIT {TOP}
    """
    
    df = pd.read_sql(query, engine).sort_values('release_year')
    
    plt.figure(figsize=(12, 6))
    sns.lineplot(x='release_year', y='num_games', data=df, marker='o', color='orange')
    plt.title(f"TOP {TOP} años con más lanzamientos de videojuegos")
    plt.xlabel("Año")
    plt.ylabel("Cantidad de juegos lanzados")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()
    return Response(content=buffer.read(), media_type="image/png")

def get_top_juegos_ventas(TOP):
    # Gráfica de barras – Juegos con más ventas totales
    query = f"""
    SELECT g.game_name AS game,
           SUM(rs.num_sales) AS total_sales
    FROM game g
    JOIN game_publisher gp ON g.id = gp.game_id
    JOIN game_platform gpl ON gp.id = gpl.game_publisher_id
    JOIN region_sales rs ON gpl.id = rs.game_platform_id
    GROUP BY g.game_name
    ORDER BY total_sales DESC
    LIMIT {TOP}
    """
    
    df = pd.read_sql(query, engine)
    
    plt.figure(figsize=(max(12, len(df)*0.8), 6))
    grafica = sns.barplot(x='game', y='total_sales', data=df, palette='viridis')
    
    plt.title(f"TOP {TOP} juegos con más ventas totales")
    plt.ylabel("Ventas totales (millones)")
    plt.xlabel("Juego")
    grafica.set_xticklabels(grafica.get_xticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()
    return Response(content=buffer.read(), media_type="image/png")

def get_top_generos_ventas(TOP):
    # Gráfica de barras – Géneros con más ventas totales
    query = f"""
    SELECT COALESCE(g.genre_name, 'Desconocido') AS genre,
           SUM(rs.num_sales) AS total_sales
    FROM region_sales rs
    JOIN game_platform gpl ON rs.game_platform_id = gpl.id
    JOIN game_publisher gp ON gpl.game_publisher_id = gp.id
    JOIN game ga ON gp.game_id = ga.id
    LEFT JOIN genre g ON ga.genre_id = g.id
    GROUP BY g.genre_name
    ORDER BY total_sales DESC
    LIMIT {TOP}
    """
    
    df = pd.read_sql(query, engine)
    
    plt.figure(figsize=(max(10, len(df)*0.8), 6))
    grafica = sns.barplot(x='genre', y='total_sales', data=df, palette='plasma')
    
    plt.title(f"TOP {TOP} géneros con más ventas totales")
    plt.ylabel("Ventas totales (millones)")
    plt.xlabel("Género")
    grafica.set_xticklabels(grafica.get_xticklabels(), rotation=15, ha='right')
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()
    return Response(content=buffer.read(), media_type="image/png")

def get_ventas_plataforma_region(TOP):
    # Gráfica de barras agrupadas – Ventas por plataforma y región
    # Primero obtenemos las TOP plataformas por ventas totales
    platform_query = f"""
    SELECT p.platform_name AS platform,
           SUM(rs.num_sales) AS total_sales
    FROM region_sales rs
    JOIN game_platform gpl ON rs.game_platform_id = gpl.id
    JOIN platform p ON gpl.platform_id = p.id
    GROUP BY p.platform_name
    ORDER BY total_sales DESC
    LIMIT {TOP}
    """
    
    top_platforms_df = pd.read_sql(platform_query, engine)
    top_platform_list = top_platforms_df['platform'].tolist()
    
    # Ahora obtenemos las ventas por región para estas plataformas
    if top_platform_list:
        placeholders = ', '.join([':p' + str(i) for i in range(len(top_platform_list))])
        params = {f'p{i}': platform for i, platform in enumerate(top_platform_list)}
        
        query = f"""
        SELECT p.platform_name AS platform,
               r.region_name AS region,
               SUM(rs.num_sales) AS total_sales
        FROM region_sales rs
        JOIN region r ON rs.region_id = r.id
        JOIN game_platform gpl ON rs.game_platform_id = gpl.id
        JOIN platform p ON gpl.platform_id = p.id
        WHERE p.platform_name IN ({placeholders})
        GROUP BY p.platform_name, r.region_name
        ORDER BY p.platform_name, SUM(rs.num_sales) DESC
        """
        
        df = pd.read_sql(text(query), engine, params=params)
    else:
        # En caso de que no haya plataformas (poco probable)
        df = pd.DataFrame(columns=['platform', 'region', 'total_sales'])
    
    # Usamos un gráfico de barras estándar en lugar de catplot para mejor control
    plt.figure(figsize=(max(12, len(top_platform_list)*1.5), 8))
    sns.barplot(x="platform", y="total_sales", hue="region", data=df, palette="Set2")
    
    plt.title(f"Ventas por región en las TOP {TOP} plataformas")
    plt.ylabel("Ventas totales (millones)")
    plt.xlabel("Plataforma")
    plt.xticks(rotation=45)
    plt.legend(title="Región")
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()
    return Response(content=buffer.read(), media_type="image/png")
