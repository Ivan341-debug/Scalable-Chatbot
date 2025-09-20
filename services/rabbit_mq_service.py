import os
import json
import pika
from dotenv import load_dotenv
from utils.logger import insere_log

load_dotenv()

def SendInput(fila, mensagem):
    try:
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

        channel.queue_declare(
            queue=fila,  # Nome da fila
            durable=True,  # Torna a fila persistente
            exclusive=False,  # Permite múltiplos consumidores
            auto_delete=False  # Não deleta a fila quando desconectar
        )

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
