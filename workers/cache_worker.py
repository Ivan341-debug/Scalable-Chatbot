import pika
import json
import asyncio
import threading
from services.redis_service import *
from utils.timer_async import main

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    loop.close()

# Callback para processar cada mensagem da fila
def callback(ch, method, properties, body):
    data = json.loads(body)
    usuario = data.get('usuario')
    nome = data.get('nome')
    mensagem = data.get('mensagem')
    timeStamp = data.get('timeStamp')
    message_id = data.get('message_id')

    data = {
        'usuario': usuario,
        'nome': nome,
        'mensagem': mensagem,
        'timeStamp': timeStamp,
        'message_id': message_id,
    }

    print(f"[Worker] Recebido: {usuario}")

    dados = GetRedis(usuario)

    if not dados:
        send = InsertRedis(usuario, data)
        thread = threading.Thread(
            target=run_async,
            args=(main(usuario, data),)
        )
        thread.start()
        print("Info Criada")

    elif dados:
        new_data = {
            'usuario': usuario,
            'nome': nome,
            'mensagem': dados + " " + mensagem,
            'timeStamp': timeStamp,
            'message_id': message_id,
        }

        send = InsertRedis(usuario, new_data)
        thread = threading.Thread(
            target=run_async,
            args=(main(usuario, new_data),)
        )
        thread.start()
        print("Info Atualizada")

    else:
        print('erro')
        insere_log('Erro-Cache', str(data), numero)

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
channel.basic_consume(queue='Input Text', on_message_callback=callback)

print("[Worker] Aguardando mensagens...")
channel.start_consuming()
