import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def insere_log(log_type, message, user_id):
    conn_log = None
    cursor_log = None

    try:
        conn_log = psycopg2.connect(
            dbname=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT')
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