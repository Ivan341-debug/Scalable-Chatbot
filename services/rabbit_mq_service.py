import pika
import os
import json
from utils.logger import insere_log
from config import RABBIT_USER, RABBIT_PASS, RABBIT_HOST

def SendInput(fila, mensagem):
    try:
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
        channel.queue_declare(queue=fila, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=fila,
            body=json.dumps(mensagem),
            properties=pika.BasicProperties(
                delivery_mode=2  # torna a mensagem persistente
            )
        )
        connection.close()
        return True
        print('sucesso')

    except Exception as e:
        insere_log('Erro RabbitMQ', str(e), mensagem.get('usuario', 'desconhecido'))
        return None
        print('erro RabbitMQ')
