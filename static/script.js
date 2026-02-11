document.addEventListener('DOMContentLoaded', () => {
    const quizContainer = document.getElementById('quiz-container');
    const submitButton = document.getElementById('submit-button');
    const resultsContainer = document.getElementById('results-container');
    const scoreDisplay = document.getElementById('score-display');
    const detailedResults = document.getElementById('detailed-results');
    const restartButton = document.getElementById('restart-button');

    let questionsData = []; // Для хранения загруженных вопросов

    // Функция для загрузки вопросов с сервера
    async function loadQuestions() {
        quizContainer.innerHTML = '<p>Загрузка вопросов...</p>';
        submitButton.style.display = 'none';
        resultsContainer.style.display = 'none';

        try {
            const response = await fetch('/get_questions');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            questionsData = await response.json();
            displayQuestions();
            submitButton.style.display = 'block';
        } catch (error) {
            quizContainer.innerHTML = `<p style="color: red;">Ошибка при загрузке вопросов: ${error.message}</p>
                                       <p style="color: red;">Возможно, проблема с Unsplash API ключом или лимитами запросов.</p>`;
            console.error('Ошибка при загрузке вопросов:', error);
        }
    }

    // Функция для отображения вопросов на странице
    function displayQuestions() {
        quizContainer.innerHTML = ''; // Очищаем контейнер перед добавлением новых вопросов
        questionsData.forEach((q, index) => {
            const questionBlock = document.createElement('div');
            questionBlock.classList.add('question-block');

            let imageHtml = '';
            if (q.image_url) {
                // Добавляем изображение к вопросу
                imageHtml = `<div class="question-image-container">
                                <img src="${q.image_url}" alt="Изображение по теме вопроса" class="question-image">
                            </div>`;
            }

            questionBlock.innerHTML = `
                ${imageHtml}
                <p>Вопрос ${index + 1}: ${q.question}</p>
                <ul class="options-list">
                    ${q.options.map(option => `
                        <li>
                            <label>
                                <input type="radio" name="question${index}" value="${option}">
                                ${option}
                            </label>
                        </li>
                    `).join('')}
                </ul>
            `;
            quizContainer.appendChild(questionBlock);
        });
    }

    // Функция для сбора ответов пользователя
    function getUserAnswers() {
        const answers = [];
        questionsData.forEach((_, index) => {
            const selectedOption = document.querySelector(`input[name="question${index}"]:checked`);
            answers.push(selectedOption ? selectedOption.value : null); // null, если ответ не выбран
        });
        return answers;
    }

    // Обработчик события клика по кнопке "Завершить викторину"
    submitButton.addEventListener('click', async () => {
        const userAnswers = getUserAnswers();

        // Простая проверка, что все вопросы отвечены
        if (userAnswers.some(answer => answer === null)) {
            alert('Пожалуйста, ответьте на все вопросы, прежде чем завершить викторину!');
            return;
        }

        try {
            const response = await fetch('/submit_answers', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ answers: userAnswers })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            showResults(result);
        } catch (error) {
            alert(`Ошибка при отправке ответов: ${error.message}`);
            console.error('Ошибка при отправке ответов:', error);
        }
    });

    // Функция для отображения результатов
    function showResults(result) {
        quizContainer.style.display = 'none';
        submitButton.style.display = 'none';
        resultsContainer.style.display = 'block';

        scoreDisplay.textContent = `Ваш счет: ${result.score} из ${result.total_questions}`;
        detailedResults.innerHTML = ''; // Очищаем предыдущие результаты

        result.results.forEach((item, index) => {
            const resultItem = document.createElement('div');
            resultItem.classList.add('result-item');
            resultItem.innerHTML = `
                <p class="question">Вопрос ${index + 1}: ${item.question}</p>
                <p>Ваш ответ: <span class="user-answer ${item.is_correct ? 'correct' : 'incorrect'}">
                    ${item.user_answer || "Нет ответа"}
                </span></p>
                ${!item.is_correct ? `<p class="correct-answer-text">Правильный ответ: ${item.correct_answer}</p>` : ''}
            `;
            detailedResults.appendChild(resultItem);
        });
    }

    // Обработчик кнопки "Начать заново"
    restartButton.addEventListener('click', () => {
        resultsContainer.style.display = 'none';
        quizContainer.style.display = 'block';
        loadQuestions(); // Перезагружаем вопросы
    });

    // Инициализация загрузки вопросов при первой загрузке страницы
    loadQuestions();
});