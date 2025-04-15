import asyncio
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor

# Конфигурация
KAFKA_SERVER = "http://kafka-server/events"
API_SERVER = "http://rest-api-server"
TRAINING_CONTRACT = "http://contract-server/execute_training"
NFT_SERVER = "http://nft-server/check_access"
MODEL_STORAGE = "http://model-storage-api"

# Асинхронная функция для подписки на события
async def subscribe_to_events():
    while True:
        response = await asyncio.to_thread(requests.get, KAFKA_SERVER)
        if response.status_code == 200:
            event_data = response.json()
            if event_data['type'] == 'new_training_task':
                await handle
