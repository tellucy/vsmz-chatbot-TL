import json
from aiogram.types import Update
from create_bot import init_bot

# Инициализация бота и диспетчера
bot, dp = init_bot()

async def process_event(event, context):
    """Обработка входящего события от Telegram"""
    try:
        if 'messages' in event:
            for message in event['messages']:
                body = json.loads(message['details']['message']['body'])
                update = Update(**body)
        else:
            update = Update.model_validate_json(event['body'])
        
        await dp.feed_update(bot, update)
        
    except json.JSONDecodeError:
        return {'statusCode': 400, 'body': 'Invalid JSON'}
    except KeyError as e:
        print(f"Ошибка структуры события: {e}")
        return {'statusCode': 400, 'body': 'Invalid event structure'}
    except Exception as e:
        print(f"Ошибка обработки: {e}")
        return {'statusCode': 500, 'body': 'Internal Server Error'}
    
    return {'statusCode': 200, 'body': 'OK'}

async def handler(event, context):
    return await process_event(event, context)