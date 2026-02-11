from flask import Flask, render_template, request, jsonify
import requests
import os # Для получения ключа API из переменных окружения

app = Flask(__name__)

# Получите ваш Unsplash Access Key. Настоятельно рекомендуется хранить его в переменных окружения.
# Для тестирования можете временно поставить сюда прямую строку, но для продакшена используйте os.environ.get().
# Пример: export UNSPLASH_ACCESS_KEY="ВАШ_КЛЮЧ"
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "JR50JbkgpTdS5Vmbg8F2M5cCNrA-iBIPJ0t3hETJqdM") # Замените на ваш ключ для демонстрации

# Список вопросов для викторины
questions = [
    {
        "question": "Какой самый большой океан на Земле?",
        "options": ["Атлантический", "Индийский", "Тихий", "Северный Ледовитый"],
        "answer": "Тихий",
        "search_term": "ocean" # Ключевое слово для поиска изображения на Unsplash
    },
    {
        "question": "Как называется самая высокая гора в мире?",
        "options": ["К2", "Эльбрус", "Джомолунгма (Эверест)", "Килиманджаро"],
        "answer": "Джомолунгма (Эверест)",
        "search_term": "mountain everest"
    },
    {
        "question": "Какая планета Земля по счету от Солнца?",
        "options": ["Первая", "Вторая", "Третья", "Четвертая"],
        "answer": "Третья",
        "search_term": "earth planet"
    },
    {
        "question": "Кто написал 'Гамлета'?",
        "options": ["Чарльз Диккенс", "Уильям Шекспир", "Лев Толстой", "Федор Достоевский"],
        "answer": "Уильям Шекспир",
        "search_term": "william shakespeare"
    },
    {
        "question": "Какой химический элемент обозначается символом 'Fe'?",
        "options": ["Фтор", "Фермий", "Железо", "Фосфор"],
        "answer": "Железо",
        "search_term": "iron metal"
    }
]

def get_unsplash_image(query):
    """
    Получает URL изображения с Unsplash по заданному запросу.
    Использует search/photos, выбирая случайное изображение из результатов.
    """
    if not UNSPLASH_ACCESS_KEY or UNSPLASH_ACCESS_KEY == "ВАШ_ACCESS_KEY_UNSPLASH":
        print("UNSPLASH_ACCESS_KEY не настроен. Изображения не будут загружены.")
        return None

    url = f"https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "client_id": UNSPLASH_ACCESS_KEY,
        "orientation": "landscape", # Предпочтительная ориентация
        "per_page": 1 # Мы хотим одно изображение, но API может вернуть несколько, выберем первое
    }
    try:
        response = requests.get(url, params=params, timeout=5) # Добавим таймаут
        response.raise_for_status() # Вызовет исключение для HTTP ошибок (4xx или 5xx)
        data = response.json()
        if data and data['results']:
            # Возвращаем URL небольшого или обычного размера
            return data['results'][0]['urls']['regular']
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к Unsplash API для '{query}': {e}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка при обработке ответа UnsplashAPI для '{query}': {e}")
        return None

@app.route('/')
def index():
    """Отображает главную страницу викторины."""
    return render_template('index.html')

@app.route('/get_questions')
def get_questions():
    """Возвращает список вопросов с URL изображений в формате JSON."""
    questions_for_client = []
    for q in questions:
        image_url = get_unsplash_image(q["search_term"])
        questions_for_client.append({
            "question": q["question"],
            "options": q["options"],
            "image_url": image_url # Добавляем URL изображения
        })
    return jsonify(questions_for_client)

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    """
    Принимает ответы от пользователя, проверяет их и возвращает результат.
    """
    user_answers = request.json.get('answers')
    score = 0
    results = []

    for i, user_answer_text in enumerate(user_answers):
        if i < len(questions):
            correct_answer = questions[i]["answer"]
            is_correct = (user_answer_text == correct_answer)
            if is_correct:
                score += 1

            results.append({
                "question": questions[i]["question"],
                "user_answer": user_answer_text,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            })

    total_questions = len(questions)
    return jsonify({
        "score": score,
        "total_questions": total_questions,
        "results": results
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000)) # Используем порт из переменной окружения Render, по умолчанию 8000
    app.run(debug=False, host='0.0.0.0', port=port) # debug=False для продакшена, host='0.0.0.0' для доступности извне