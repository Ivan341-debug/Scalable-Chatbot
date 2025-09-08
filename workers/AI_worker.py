import os
import pika
import json
import openai
from dotenv import load_dotenv
from openai import OpenAI
from services.redis_service import GetHistories, UpdateHistories
from services.rabbit_mq_service import SendInput

load_dotenv()

prompt = 'Você é um assistente útil e responde sempre em português.'
client = OpenAI(api_key=os.environ.get('OPENAI'))

def callback(ch, method, properties, body):
    data = json.loads(body)
    usuario = data.get('usuario')
    nome = data.get('nome')
    mensagem = data.get('mensagem')

    print(f"[Worker] Recebido: {usuario}")

    update = UpdateHistories(usuario, 'user', mensagem)
    messages =[{'role':'system', 'content': prompt}] + GetHistories(usuario)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    resposta = response.choices[0].message.content
    UpdateHistories(usuario, 'assistant', resposta)

    response = {'usuario': usuario, 'mensagem': resposta}
    SendInput('Response AI', response)

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
channel.basic_consume(queue='Input AI', on_message_callback=callback)

print("[Worker] Aguardando mensagens...")
channel.start_consuming()