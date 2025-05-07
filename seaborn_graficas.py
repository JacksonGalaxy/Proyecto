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
    SELECT ga.release_year, 
           COUNT(*) AS num_games
    FROM game ga
    GROUP BY ga.release_year
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

