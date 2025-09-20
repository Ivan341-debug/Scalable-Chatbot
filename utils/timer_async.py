import asyncio
from services.redis_service import InsertRedis, DeleteData
from services.rabbit_mq_service import SendInput

# Dicionário para armazenar timers ativos por usuario
timers = {}

async def Input(usuario, data):
    if usuario in timers:
        timers[usuario].cancel()
        del timers[usuario]

    timer = asyncio.create_task(Cache(usuario, 1, action, data))
    timers[usuario] = timer

async def Cache(user_id, delay, func, data):
        try:
            await asyncio.sleep(delay)
            await func(user_id, data)
        except asyncio.CancelledError:
            pass
        finally:
            if user_id in timers and timers[user_id] == asyncio.current_task():
                del timers[user_id]

async def action(user_id, data):
    SendInput('Input AI', data)
    print('RabbitMq Ok')
    DeleteData(user_id)

async def main(user, data):
    await Input(user, data)

    while timers:
        await asyncio.sleep(0.1)