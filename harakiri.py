import requests
import time
import os

# === НАСТРОЙКИ ===
LM_STUDIO_PORT = 1234
MODEL_NAME = "mistral-7b-instruct-v0.2.Q4_K_M"  # Укажи точное название модели из LM Studio
TOPICS_FILE = "topics.txt"
OUTPUT_DIR = "articles"

# Создаём папку для статей
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Проверка подключения
try:
    response = requests.get(f"http://localhost:{LM_STUDIO_PORT}/v1/models", timeout=5)
    response.raise_for_status()
    print(f"✅ Подключено к LM Studio. Модель: {MODEL_NAME}")
except Exception as e:
    print(f"❌ Ошибка подключения: {str(e)}")
    print("1. Запусти LM Studio")
    print("2. Включи Local Server в Settings")
    print("3. Загрузи модель в интерфейсе")
    exit()

# Читаем темы
try:
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        topics = [line.strip() for line in f if line.strip()]
    print(f"📝 Найдено тем: {len(topics)}")
except FileNotFoundError:
    print(f"❌ Файл {TOPICS_FILE} не найден. Создай его с темами.")
    exit()

# Генерация
for i, topic in enumerate(topics, 1):
    print(f"\n🔥 Обработка: '{topic}'")
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            # ВСЁ! Только user-сообщение, system промт берётся из LM Studio
            {"role": "user", "content": f"Напиши SEO-статью на тему: {topic}"}
        ],
        "temperature": 0.7,
        "max_tokens": 3500,  # Для статей лучше 3000+
        "stream": False
    }

    try:
        start = time.time()
        response = requests.post(
            f"http://localhost:{LM_STUDIO_PORT}/v1/chat/completions",
            json=payload,
            timeout=120  # Увеличенный таймаут для длинных статей
        )
        response.raise_for_status()
        
        article = response.json()["choices"][0]["message"]["content"].strip()
        
        # Сохраняем
        filename = f"{OUTPUT_DIR}/article_{i:03d}_{topic[:50].replace(' ', '_')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {topic}\n\n{article}")
        
        print(f"✅ Сохранено: {filename} | {len(article)//1000} тыс. символов | {time.time()-start:.1f}с")

    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        # Продолжаем обработку следующих тем

print("\n🎉 Готово! Все статьи в папке:", OUTPUT_DIR)
