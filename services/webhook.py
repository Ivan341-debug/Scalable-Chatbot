import re
import asyncio
from flask import request
from services.redis_service import InsertRedis, GetRedis
from services.rabbit_mq_service import SendInput
from services.db_service import search_user
from utils.logger import insere_log
from utils.timer_async import *

def webhook_handler():
    data = request.get_json()
    time_stamp = data.get('body', {}).get('date_time', {})
    message_id = data.get('body', {}).get('data', {}).get('key', {}).get('id', '')
    remote_Jid = data.get('body', {}).get('data', {}).get('key', {}).get('remoteJid', '')
    numero = re.sub(r'\D', '', remote_Jid)
    fromMe = data.get('body', {}).get('data', {}).get('fromMe', False)
    pushName = data.get('body', {}).get('data', {}).get('pushName', '')
    mensagem = data.get('body', {}).get('data', {}).get('message', {})
    texto = mensagem.get('conversation', '')
    audio_base64 = mensagem.get('base64', '')

    if fromMe:
        return{'origem': 'remetente'},400

    try:
        dados = search_user(numero)

        if dados == False:
            return {'message': 'Usuário não encontrado'}, 404

    except Exception as e:
        insere_log('erro webhook',str(e),numero)
        return {'Erro': str(e)},400

    try:
        if audio_base64:
            data = {
                'usuario': numero,
                'nome': pushName,
                'audio': audio_base64,
                'timeStamp': time_stamp,
                'message_id': message_id,
            }
            send = SendInput('Input Audio', data)

            if send:
                return {'status': 'ok'}, 200
            else:
                return {'status': 'erro webhook'}, 500

        else:
            data = {
                'usuario': numero,
                'nome': pushName,
                'mensagem': texto,
                'timeStamp': time_stamp,
                'message_id': message_id,
            }
            send = SendInput('Input Text', data)

            if send:
                return {'status': 'ok'}, 200
            else:
                return {'status': 'erro webhook'}, 500

    except Exception as e:
        insere_log('erro webhook', str(e), numero)
        return {'message': str(e)}, 500