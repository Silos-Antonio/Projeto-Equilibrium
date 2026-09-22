import logging
import os

import mysql.connector
from mysql.connector import Error


logger = logging.getLogger(__name__)


def get_db_connection():
    host = os.getenv('DB_HOST')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASS')
    database = os.getenv('DB_NAME')

    if not all([host, user, database]):
        logger.error('Configuração do banco de dados incompleta.')
        return None

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password or '',
            database=database,
        )

        if connection.is_connected():
            return connection

        return None

    except Error as error:
        logger.error(
            'Erro ao conectar ao MySQL: %s',
            error,
        )
        return None