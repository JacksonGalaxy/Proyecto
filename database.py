from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob

# Configuración de la conexión a la base de datos
DATABASE_URL = "mysql+pymysql://root:rootpassword@db:3306/video_games"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Función para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_tables():
    """Obtiene una lista de todas las tablas en la base de datos"""
    inspector = inspect(engine)
    return inspector.get_table_names()

def get_table_data(table_name, limit=100):
    """Obtiene datos de una tabla específica"""
    query = text(f"SELECT * FROM {table_name} LIMIT {limit}")
    with engine.connect() as conn:
        result = conn.execute(query)
        data = [dict(row._mapping) for row in result]
    return data

def execute_query(query_text, params=None):
    """Ejecuta una consulta SQL personalizada"""
    query = text(query_text)
    with engine.connect() as conn:
        result = conn.execute(query, params or {})
        data = [dict(row._mapping) for row in result]
    return data

def get_table_to_dataframe(table_name, limit=1000):
    """Convierte una tabla a DataFrame de pandas"""
    query = text(f"SELECT * FROM {table_name} LIMIT {limit}")
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def export_table_to_csv(table_name, file_path):
    """Exporta una tabla a un archivo CSV"""
    df = get_table_to_dataframe(table_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False)
    return file_path

def create_bar_chart(data, x_column, y_column, title, file_path):
    """Crea un gráfico de barras y lo guarda"""
    plt.figure(figsize=(12, 6))
    if isinstance(data, list):
        # Convertir lista de diccionarios a DataFrame
        data = pd.DataFrame(data)
    
    sns.barplot(x=x_column, y=y_column, data=data)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    plt.savefig(file_path)
    plt.close()
    return file_path

def create_line_chart(data, x_column, y_column, title, file_path):
    """Crea un gráfico de líneas y lo guarda"""
    plt.figure(figsize=(12, 6))
    if isinstance(data, list):
        # Convertir lista de diccionarios a DataFrame
        data = pd.DataFrame(data)
    
    plt.plot(data[x_column], data[y_column], marker='o')
    plt.title(title)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    plt.savefig(file_path)
    plt.close()
    return file_path

def get_database_schema():
    """Obtiene el esquema de la base de datos"""
    inspector = inspect(engine)
    schema = {}
    
    for table_name in inspector.get_table_names():
        columns = []
        for column in inspector.get_columns(table_name):
            columns.append({
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"]
            })
        
        foreign_keys = []
        for fk in inspector.get_foreign_keys(table_name):
            foreign_keys.append({
                "referred_table": fk["referred_table"],
                "referred_columns": fk["referred_columns"],
                "constrained_columns": fk["constrained_columns"]
            })
        
        schema[table_name] = {
            "columns": columns,
            "foreign_keys": foreign_keys
        }
    
    return schema

def get_all_databases(db):
    """Obtiene una lista de todas las bases de datos en el servidor MySQL"""
    query = text("SHOW DATABASES")
    result = db.execute(query)
    databases = [row[0] for row in result]
    return databases

def execute_sql_file(db, file_path):
    """Ejecuta un archivo SQL"""
    with open(file_path, 'r') as file:
        sql_content = file.read()
    
    # Dividir por ; para ejecutar múltiples comandos
    statements = sql_content.split(';')
    
    for statement in statements:
        if statement.strip():
            db.execute(text(statement))
    
    db.commit()
    return True

# Nueva función para realizar consultas para gráficos de seaborn
def execute_dataframe_query(query_text, params=None):
    """Ejecuta una consulta SQL y devuelve un DataFrame de pandas"""
    query = text(query_text)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params or {})
    return df