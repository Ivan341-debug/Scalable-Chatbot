import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST

def insere_log(log_type, message, user_id):
    conn_log = None
    cursor_log = None

    try:
        conn_log = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=8083
        )
        cursor_log = conn_log.cursor()
        cursor_log.execute(
            "INSERT INTO logs (log_type, message, usuario) VALUES (%s, %s, %s)",
            (log_type, message, user_id)
        )
        conn_log.commit()
        print("Sucesso - Log inserido com sucesso!")

    except (Exception, psycopg2.Error) as e:
        print("Erro - Erro ao inserir log:", e)

    finally:
        if cursor_log:
            cursor_log.close()
        if conn_log:
            conn_log.close()