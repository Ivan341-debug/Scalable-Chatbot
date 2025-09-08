import psycopg2
from psycopg2 import pool
import logging
from utils.logger import insere_log

# Configuração do pool de conexões
connection_pool = None


def get_connection_pool():
    """Obtém ou cria o pool de conexões"""
    global connection_pool
    if connection_pool is None:
        try:
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host='localhost',
                database='database',
                user='postgres',
                password='Sakura2013@',
                port=8083
            )
            logging.info("Pool de conexões criado com sucesso")
        except Exception as e:
            logging.error(f"Erro ao criar pool de conexões: {e}")
            raise
    return connection_pool


def get_db_connection():
    """Obtém uma conexão do pool"""
    try:
        pool = get_connection_pool()
        conn = pool.getconn()
        return conn
    except Exception as e:
        logging.error(f"Erro ao obter conexão do pool: {e}")
        raise


def release_db_connection(conn):
    """Devolve a conexão para o pool"""
    try:
        pool = get_connection_pool()
        pool.putconn(conn)
    except Exception as e:
        logging.error(f"Erro ao devolver conexão para o pool: {e}")


def InsertHistories(usuario, role, content):
    """Versão com pool de conexões"""
    conn = None
    cursor = None
    try:
        # Obtém conexão do pool
        conn = get_db_connection()
        cursor = conn.cursor()

        # Executa a inserção
        cursor.execute('INSERT INTO historico (usuario, role, content) VALUES (%s, %s, %s) RETURNING id',
                       (usuario, role, content))
        row = cursor.fetchone()[0]
        conn.commit()

        if row:
            return True
        else:
            return False

    except(Exception, psycopg2.Error) as e:
        # Faz rollback em caso de erro
        if conn:
            conn.rollback()
        insere_log('Error_database_queue', str(e), usuario)
        return {'erro': str(e)}

    finally:
        # Fecha o cursor
        if cursor:
            cursor.close()

        # Devolve a conexão para o pool
        if conn:
            release_db_connection(conn)

def search_user(numero):
    query_1 = 'SELECT cliente_id FROM usuarios WHERE numero = %s'
    query_2 = 'SELECT status FROM clientes WHERE id = %s'
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(query_1, (numero,))
        row = cursor.fetchone()

        if row is None:
            return False  # usuário não encontrado
        id = row[0]

        cursor.execute(query_2, (id,))
        users = cursor.fetchone()

        if users:
            return True
        else:
            return False

    except(Exception, psycopg2.Error) as e:
        insere_log('Error-search_user', str(e), numero)
        return {'erro': str(e)}

    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)