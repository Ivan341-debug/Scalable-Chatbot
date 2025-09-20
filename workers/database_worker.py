import time
import pika
import json
import os
from dotenv import load_dotenv
from utils.logger import insere_log
from services.db_service import InsertHistories

load_dotenv()

# Callback para processar cada mensagem da fila
def callback(ch, method, properties, body):
    data = json.loads(body)
    usuario = data.get('usuario')
    role = data.get('role')
    content = data.get('content')

    insert = InsertHistories(usuario, role, content)
    if insert == True:
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        print(insert)

    print(f"Role: {role}, Mensagem: {content}, Usuario: {usuario}")

# Conecta no RabbitMQ
connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.environ.get('RABBIT_HOST'),
                port=os.environ.get('RABBIT_PORT'),
                credentials=pika.PlainCredentials(
                    os.environ.get('RABBIT_USER'),
                    os.environ.get('RABBIT_PASS')
                )
            )
        )
channel = connection.channel()

# Consome a fila
channel.basic_qos(prefetch_count=1)  # processa uma mensagem por vez
channel.basic_consume(queue='Database', on_message_callback=callback)

print("[Worker] Aguardando mensagens...")
channel.start_consuming()
