import mysql.connector
from mysql.connector import Error
import os

def get_db_connection():
    # Depuração: Vamos ver o que está sendo lido das variáveis
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    pw = os.getenv("DB_PASS")
    db = os.getenv("DB_NAME")
    
    print(f"DEBUG: Tentando conectar com Host={host}, User={user}, Pass={'[OCULTO]' if pw else '[VAZIO]'}, DB={db}")

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=pw if pw else "", # Garante string vazia se for None
            database=db
        )

        if connection.is_connected():
            return connection
        else:
            return None
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None