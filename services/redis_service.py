import os
import json
import redis
from datetime import datetime
from dotenv import load_dotenv
from utils.logger import insere_log
from redis.commands.json.path import Path
from services.db_service import GetHistories, InsertHistories
from services.rabbit_mq_service import SendInput

r = redis.Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'))

def InsertRedis(usuario, data):
    try:
        insere_log('Cache_worker', 'preparando arquivo', usuario)
        user = 'users:' + str(usuario)
        r.json().set(user, Path.root_path(), json.dumps(data))
        insere_log('Cache_worker', 'Ok', usuario)

    except Exception as e:
        insere_log('Erro_InsertRedis', str(e), usuario)
        return {"Error": str(e)}

    return {'status': 'ok'}

def GetRedis(usuario):
    try:
        insere_log('Cache_worker', 'Verificando usuario', usuario)
        user = 'users:' + str(usuario)
        key = r.json().get(user, Path.root_path())

        if type(key) == str:
            json_data = json.loads(key)
            mensagem = json_data.get('mensagem')
            insere_log('Cache_worker', mensagem, usuario)

            return mensagem

        else:
            return None

    except Exception as e:
        insere_log('Erro_GetRedis', str(e), usuario)
        return {"Error": str(e)}

def GetHistories(usuario, include_fields=['role', 'content']):
    json_data = r.get(f"histories:{usuario}")

    if not json_data:
        histories = GetHistories(usuario)
        if histories:
            InsertRedis(usuario, histories)
            return histories
        else:
            return None
    try:
        histories = json.loads(json_data.decode('utf8'))

        return histories['messages']

    except json.JSONDecodeError as e:
        insere_log('Erro_GetHistories', str(e), usuario)
        print(f"Erro ao decodificar JSON para o usuário {usuario}")
        return None

def SaveHistories(usuario, message, ttl=86400):
    messages = GetHistories(usuario)
    key = 'histories:' + usuario
    data = r.get(key)

    try:
        if data:
            try:
                histories = json.loads(data)
                histories['updated_at'] = datetime.now().isoformat()
            except json.JSONDecodeError:
                histories = {
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'messages':[]
                }
        else:
            histories = {
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'messages': []
            }

        if message:
            histories['messages'].append(message)

        json_data = json.dumps(histories)
        r.setex(key, ttl, json_data.encode('utf-8'))

        return histories
    except Exception as e:
        insere_log('Erro_SaveHistories', str(e), usuario)

def UpdateHistories(usuario, role, content):
    try:
        if role and content:
            message = {'role': role, 'content': content}
            SaveHistories(usuario, message)

            data = {'usuario': usuario, 'role': role, 'content': content}
            SendInput('Database', data)

        else:
            SaveHistories(usuario, None)
    except Exception as e:
        insere_log('Erro_UpdateHistories', str(e), usuario)

def DeleteData(usuario):
    key = (f"users:{usuario}")
    r.delete(key)
    print('Json Deletado!')