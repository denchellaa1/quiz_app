from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Список вопросов для викторины
# Каждый вопрос - это словарь с вопросом, вариантами ответов и правильным ответом.
questions = [
    {
        "question": "Какой самый большой океан на Земле?",
        "options": ["Атлантический", "Индийский", "Тихий", "Северный Ледовитый"],
        "answer": "Тихий"
    },
    {
        "question": "Как называется самая высокая гора в мире?",
        "options": ["К2", "Эльбрус", "Джомолунгма (Эверест)", "Килиманджаро"],
        "answer": "Джомолунгма (Эверест)"
    },
    {
        "question": "Какая планета Земля по счету от Солнца?",
        "options": ["Первая", "Вторая", "Третья", "Четвертая"],
        "answer": "Третья"
    },
    {
        "question": "Кто написал 'Гамлета'?",
        "options": ["Чарльз Диккенс", "Уильям Шекспир", "Лев Толстой", "Федор Достоевский"],
        "answer": "Уильям Шекспир"
    },
    {
        "question": "Какой химический элемент обозначается символом 'Fe'?",
        "options": ["Фтор", "Фермий", "Железо", "Фосфор"],
        "answer": "Железо"
    }
]

@app.route('/')
def index():
    """Отображает главную страницу викторины."""
    return render_template('index.html')

@app.route('/get_questions')
def get_questions():
    """Возвращает список вопросов в формате JSON."""
    # Мы можем вернуть только вопросы и варианты ответов, без правильных ответов,
    # чтобы избежать "читерства" на клиенте. Правильные ответы будут проверяться на сервере.
    questions_for_client = [
        {"question": q["question"], "options": q["options"]} for q in questions
    ]
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
        if i < len(questions):  # Проверяем, что индекс не выходит за пределы списка вопросов
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
    app.run(debug=True, port=8000)