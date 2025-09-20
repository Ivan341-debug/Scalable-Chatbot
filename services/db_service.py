import os
import json
import logging
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
from utils.logger import insere_log
from pgvector.psycopg2 import register_vector

load_dotenv()
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
                host=os.environ.get('DB_HOST'),
                database=os.environ.get('DB_NAME'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                port=os.environ.get('DB_PORT')
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

def GetHistories(usuario):
    conn = None
    cursor = None
    query = 'SELECT * FROM historico WHERE usuario = %s'

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(query, (usuario,))
        rows = cursor.fetchall()

        if rows is None:
            return None
        else:
            histories = []
            for row in rows:
                role = row[2]
                content = row[3]

                histories.append({
                    'role': role,
                    'content': content
                })

            return histories
    except(Exception, psycopg2.Error) as e:
        print(e)

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


def InsertRag(data):
    conn = None
    cursor = None
    try:
        # Extrair dados
        content = data['content']
        metadata = data['metadata']
        usuario = data['usuario']
        embeddings = data['embeddings']

        # Converter metadados para JSON apenas uma vez
        metadata_json = json.dumps(metadata)

        # Processar embeddings
        if isinstance(embeddings, str):  # Se for string JSON
            embeddings = json.loads(embeddings)

        if isinstance(embeddings, dict):  # Se for dicionário
            embeddings = embeddings.get("embedding", [])

        # Garantir que seja uma lista 1D
        if isinstance(embeddings, (list, tuple)):
            # Se for lista de listas, pegar o primeiro elemento
            if embeddings and isinstance(embeddings[0], (list, tuple)):
                embeddings = embeddings[0]

            # Converter para lista Python pura se for numpy array
            if hasattr(embeddings, 'tolist'):
                embeddings = embeddings.tolist()

            # Garantir que seja lista de floats
            embeddings = [float(x) for x in embeddings]
        else:
            raise ValueError("Embeddings deve ser uma lista 1D")

        # Conectar ao banco
        conn = get_db_connection()
        cursor = conn.cursor()

        # Inserir dados
        cursor.execute(
            'INSERT INTO document_embeddings (content, embedding, metadata, usuario) VALUES (%s, %s, %s, %s)',
            (content, embeddings, metadata_json, usuario)
        )

        conn.commit()
        return True

    except(Exception, psycopg2.Error) as e:
        if conn:
            conn.rollback()
        insere_log('Error_Rag_Insert', str(e), usuario)
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)

def SearchRAG(usuario, embedding):
    conn = None
    cursor = None
    query = """
    SELECT content, 1 - (embedding <=> %s::vector) AS similarity
    FROM document_embeddings
    WHERE usuario = %s
    ORDER BY embedding <=> %s::vector
    LIMIT 5;
    """
    try:
        conn = get_db_connection()
        register_vector(conn)
        cursor = conn.cursor()
        cursor.execute(query, (embedding, usuario, embedding))

        rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append({
                'content': rows[1],
            })

        print(rows)

    except(Exception, psycopg2.Error) as e:
        insere_log('Error_SearchRAG', str(e), usuario)

    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)