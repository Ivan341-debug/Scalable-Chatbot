import os
import pika
import json
import openai
from openai import OpenAI
from dotenv import load_dotenv
from services.rabbit_mq_service import SendInput
from services.redis_service import GetHistories, UpdateHistories

load_dotenv()

prompt = """Você é a Alexa, assistente da Hashtag Treinamentos especializada no atendimento de clientes buscando informações.
Sempre que um usuário fizer alguma pergunta sobre a hashtag treinamentos, estruture seu output nesse formato JSON:
{
    "type": "consulta"
}
Caso o usuário faça um outro tipo de pergunta apenas o responda!
"""
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
        model="gpt-4o-mini-2024-07-18",
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    resposta = response.choices[0].message.content
    UpdateHistories(usuario, 'assistant', resposta)

    response = {'usuario': usuario, 'mensagem': resposta}
    if isinstance(resposta, str):
        print('string')
        #SendInput('Response AI', response)
    if isinstance(resposta, dict):
        print('dict')

    ch.basic_ack(delivery_tag=method.delivery_tag)

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
channel.basic_consume(queue='Input AI', on_message_callback=callback)

print("[Worker] Aguardando mensagens...")
channel.start_consuming()