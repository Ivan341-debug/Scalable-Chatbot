import redis
import json
from datetime import datetime
from services.rabbit_mq_service import SendInput
from redis.commands.json.path import Path
from utils.logger import insere_log

r = redis.Redis(host='localhost', port=6575)

def InsertRedis(usuario, data):
    try:
        user = 'users:' + str(usuario)
        r.json().set(user, Path.root_path(), json.dumps(data))

    except Exception as e:
        insere_log('Erro_Redis1', str(e), usuario)
        return {"Error": str(e)}

    return {'status': 'ok'}

def GetRedis(usuario):
    try:
        user = 'users:' + str(usuario)
        key = r.json().get(user, Path.root_path())

        if type(key) == str:
            json_data = json.loads(key)
            mensagem = json_data.get('mensagem')

            return mensagem

        else:
            return None

    except Exception as e:
        insere_log('Erro_Redis', str(e), usuario)
        return {"Error": str(e)}

def GetHistories(usuario, include_fields=['role', 'content']):
    json_data = r.get(f"histories:{usuario}")

    if not json_data:
        return None
    try:
        histories = json.loads(json_data.decode('utf8'))

        return histories['messages']

    except json.JSONDecodeError as e:
        insere_log('Erro_Redis', str(e), usuario)
        print(f"Erro ao decodificar JSON para o usuário {usuario}")
        return None

def SaveHistories(usuario, message, ttl=86400):
    messages = GetHistories(usuario)
    key = 'histories:' + usuario
    data = r.get(key)

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

def UpdateHistories(usuario, role, content):
    if role and content:
        message = {'role': role, 'content': content}
        SaveHistories(usuario, message)

        data = {'usuario': usuario, 'role': role, 'content': content}
        SendInput('Database', data)

    else:
        SaveHistories(usuario, None)

def DeleteData(usuario):
    key = (f"users:{usuario}")
    r.delete(key)
    print('Json Deletado!')