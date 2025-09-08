import time
import pika
import json
from services.db_service import InsertHistories
from utils.logger import insere_log

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
                host="localhost",
                port=5673,
                credentials=pika.PlainCredentials(
                    "guest",
                   "guest"
                )
            )
        )
channel = connection.channel()

# Consome a fila
channel.basic_qos(prefetch_count=1)  # processa uma mensagem por vez
channel.basic_consume(queue='Database', on_message_callback=callback)

print("[Worker] Aguardando mensagens...")
channel.start_consuming()
