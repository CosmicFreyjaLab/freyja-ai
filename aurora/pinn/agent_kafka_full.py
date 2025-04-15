import requests
import time
import json
import tensorflow as tf  # или любой другой ML фреймворк, например, PyTorch

# Конфигурация
KAFKA_SERVER = "http://kafka-server/events"  # Сервера Kafka для подписки на события
API_SERVER = "http://rest-api-server"  # REST API сервер
TRAINING_CONTRACT = "http://contract-server/execute_training"  # Контракт для обучения модели
NFT_SERVER = "http://nft-server/check_access"  # Сервера для проверки доступа через NFT
MODEL_STORAGE = "http://model-storage-api"  # API для сохранения моделей

# Подписка на обновления
def subscribe_to_events():
    while True:
        # Подключаемся к Kafka-серверу, чтобы получать события
        response = requests.get(KAFKA_SERVER)
        if response.status_code == 200:
            event_data = response.json()
            if event_data['type'] == 'new_training_task':
                handle_training_task(event_data)
        time.sleep(5)  # Пауза между запросами

# Проверка доступа через NFT
def check_nft_access(user_id):
    response = requests.get(f"{NFT_SERVER}/{user_id}")
    return response.json().get('has_access', False)

# Получение данных для обучения
def fetch_training_data(task_id):
    data_url = f"{API_SERVER}/training_data/{task_id}"
    response = requests.get(data_url)
    return response.json()

# Обучение модели (используется TensorFlow или другой ML-фреймворк)
def train_model(training_data):
    # Здесь можно использовать любую модель машинного обучения
    # Пример для TensorFlow
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu', input_shape=(len(training_data['features']),)),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    # Обучаем модель
    model.fit(training_data['features'], training_data['labels'], epochs=10)

    return model

# Сохранение обученной модели
def save_model(model, model_id):
    model_url = f"{MODEL_STORAGE}/save/{model_id}"
    model_data = model.to_json()  # Преобразуем модель в формат JSON для хранения
    response = requests.post(model_url, json={"model": model_data})
    return response.status_code

# Основная логика агента
def handle_training_task(event_data):
    user_id = event_data['user_id']
    task_id = event_data['task_id']
    
    if check_nft_access(user_id):  # Проверяем доступ через NFT
        training_data = fetch_training_data(task_id)  # Получаем данные для обучения
        
        # Обучаем модель
        model = train_model(training_data)
        
        # Сохраняем результат обучения
        model_id = event_data['model_id']
        save_model(model, model_id)
        
        print(f"Training task {task_id} completed successfully for user {user_id}.")
    else:
        print(f"User {user_id} does not have access to training contract.")

# Запуск агента
if __name__ == "__main__":
    subscribe_to_events()
