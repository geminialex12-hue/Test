import telebot
import requests
import json
import time
import logging

# ---------- НАСТРОЙКИ ----------
TELEGRAM_TOKEN = '8657842027:AAGm1qncYBO-z8b-yF8KePr6bzy0meKvSE0'
GROQ_API_KEY = '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'

# Модель Groq (можно заменить на другую: mixtral-8x7b-32768, llama3-70b-8192)
MODEL = 'llama3-70b-8192'
TEMPERATURE = 0.7
MAX_TOKENS = 2048

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ---------- ФУНКЦИЯ ЗАПРОСА К GROQ ----------
def get_ai_response(user_text):
    """Отправляет запрос к Groq API и возвращает ответ"""
    url = 'https://api.groq.com/openai/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GROQ_API_KEY}'
    }
    # Системный промпт с обращением "сер"
    system_prompt = (
        "Ты — Джарвис, созданный NODE / хелок. "
        "Всегда обращайся к пользователю на «Вы» и добавляй в конце каждого ответа слово «сер». "
        "Отвечай развёрнуто, структурированно, по возможности используй маркдаун. "
        "Ты эксперт в программировании и технологиях."
    )
    data = {
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_text}
        ],
        'temperature': TEMPERATURE,
        'max_tokens': MAX_TOKENS
    }
    try:
        logger.info(f'Запрос к Groq: {user_text[:50]}...')
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            logger.info('Ответ получен успешно')
            return answer
        else:
            error_msg = f'Ошибка API: {response.status_code} - {response.text}'
            logger.error(error_msg)
            return f'⚠️ {error_msg}'
    except requests.exceptions.Timeout:
        logger.error('Таймаут запроса к Groq')
        return '⏳ Превышено время ожидания ответа от сервера.'
    except Exception as e:
        logger.error(f'Исключение: {str(e)}')
        return f'❌ Ошибка: {str(e)}'

# ---------- ОБРАБОТЧИКИ КОМАНД ----------
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Приветственное сообщение"""
    welcome_text = (
        "👋 Привет! Я **Джарвис**, ваш персональный помощник, сер.\n\n"
        "Задайте мне любой вопрос – я помогу с программированием, анализом, идеями, сер.\n"
        "Просто напишите своё сообщение, и я отвечу."
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Обработка всех текстовых сообщений"""
    # Отправляем статус "печатает"
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Получаем ответ от ИИ
    answer = get_ai_response(message.text)
    
    # Если в ответе нет "сер", добавляем в конце
    if 'сер' not in answer.lower():
        answer += ', сер.'
    
    # Отправляем ответ (если длинный, разбиваем на части)
    if len(answer) > 4096:
        for x in range(0, len(answer), 4096):
            bot.reply_to(message, answer[x:x+4096])
    else:
        bot.reply_to(message, answer)

# ---------- ЗАПУСК ----------
if __name__ == '__main__':
    logger.info('🤖 Бот Джарвис запущен...')
    try:
        bot.infinity_polling()
    except Exception as e:
        logger.error(f'Ошибка при запуске бота: {e}')
