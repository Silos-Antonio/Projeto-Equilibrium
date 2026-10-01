import os
import logging
import base64
import tempfile
from pathlib import Path

import mysql.connector
from mysql.connector import Error

logger = logging.getLogger(__name__)


def get_ssl_ca_path():
    # Desenvolvimento local: usa o arquivo existente
    ssl_ca = os.getenv('DB_SSL_CA')

    if ssl_ca:
        return ssl_ca

    # Produção: recebe o certificado em Base64
    ssl_ca_b64 = os.getenv('DB_SSL_CA_B64')

    if not ssl_ca_b64:
        return None

    ca_path = Path(tempfile.gettempdir()) / 'aiven-ca.pem'

    if not ca_path.exists():
        ca_path.write_bytes(
            base64.b64decode(ssl_ca_b64)
        )

    return str(ca_path)


def get_db_connection():
    host = os.getenv('DB_HOST')
    port = int(os.getenv('DB_PORT', '3306'))
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASS')
    database = os.getenv('DB_NAME')
    ssl_ca = get_ssl_ca_path()
    db_time_zone = os.getenv('DB_TIME_ZONE', '-03:00')

    if not all([host, user, database]):
        logger.error('Database environment variables are incomplete.')
        return None

    config = {
        'host': host,
        'port': port,
        'user': user,
        'password': password or '',
        'database': database,
    }

    if ssl_ca:
        config.update({
            'ssl_ca': ssl_ca,
            'ssl_verify_cert': True,
            'ssl_verify_identity': True,
        })

    try:
        connection = mysql.connector.connect(**config)

    except Error:
        logger.exception('Unable to connect to the database.')
        return None

    try:
        cursor = connection.cursor()
        cursor.execute(
            'SET time_zone = %s',
            (db_time_zone,)
        )
        cursor.close()

    except Error:
        logger.exception('Unable to configure database timezone.')
        connection.close()
        return None

    return connection