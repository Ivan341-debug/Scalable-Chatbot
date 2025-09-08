import pika
import json
import requests
import os
from dotenv import load_dotenv
from services.redis_service import *

load_dotenv()

# Callback para processar cada mensagem da fila
def callback(ch, method, properties, body):
    data = json.loads(body)
    usuario = data.get('usuario')
    mensagem = data.get('mensagem')

    url = f"{os.environ.get('BASE_URL_EVO')}/message/sendText/{os.environ.get('INSTANCE')}"
    headers = {
        "Content-Type": "application/json",
        "apikey": os.environ.get('API_EVO')
    }

    payload = {
        "number": usuario,
        "text": mensagem
    }

    response = requests.post(url, headers=headers, json=payload)
    print(response.status_code, response.json())

    ch.basic_ack(delivery_tag=method.delivery_tag)

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
channel.basic_consume(queue='Response AI', on_message_callback=callback)

print("[Worker] Aguardando mensagens...")
channel.start_consuming()
