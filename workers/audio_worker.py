import os
import pika
import json
import asyncio
import threading
import base64
import tempfile
import requests
from pika import data
from dotenv import load_dotenv
from services.rabbit_mq_service import SendInput

load_dotenv()

api_key = os.environ.get('OPENAI')

# Callback para processar cada mensagem da fila
def callback(ch, method, properties, body):
    data = json.loads(body)
    usuario = data.get('usuario')
    nome = data.get('nome')
    mensagem = data.get('audio')
    timeStamp = data.get('timeStamp')
    message_id = data.get('message_id')

    print(data)
    file = base64.b64decode(mensagem)
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            f.write(file)
            temp_file_path = f.name

        with open(temp_file_path, 'rb') as f:
            headers = {
                'Authorization': f'Bearer {api_key}',
            }
            files = {
                'file': (os.path.basename(temp_file_path), f, 'audio/mp3'),
            }
            data = {
                'model': 'whisper-1',
                'response_format': 'json'  # Corrigido
            }
            response = requests.post(
                'https://api.openai.com/v1/audio/transcriptions',
                headers=headers,
                files=files,
                data=data,
            )

            if response.status_code == 200:
                transcription = response.json()

                new_data = {
                    'usuario': usuario,
                    'nome': nome,
                    'mensagem': transcription['text'],
                    'timeStamp': timeStamp,
                    'message_id': message_id,
                }

                SendInput('Input AI', new_data)
                print("Transcrição:", transcription['text'])
            else:
                print(f"Erro na requisição: {response.status_code}")
                print(response.text)

    finally:
        # Garante que o arquivo temporário seja excluído mesmo se ocorrer erro
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

    print(f"[Worker] Recebido: {usuario}")

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
channel.basic_consume(queue='Input Audio', on_message_callback=callback)

print("[Worker] Aguardando mensagens...")
channel.start_consuming()
