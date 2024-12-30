from telebot import Telebot

import logging
import os
import sys
import time

import requests

from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


RETRY_PERIOD = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}
bot = Telebot(token=TELEGRAM_TOKEN)

HOMEWORK_VERDICTS = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания."
}


def check_tokens():
    """
    Проверяет доступность переменных окружения,
    которые необходимы для работы программы
    """
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if all(tokens):
        return True
    logging.error("Необходимые токены отсутствуют.")


@bot.message_handler(content_types=["text"])
def send_message(bot, message):
    """отправляет сообщение в Telegram-чат"""


def get_api_answer(timestamp):
    """Делает запрос к API."""
    params = {'form_date': timestamp}
    try:
        response = requests.get(url=ENDPOINT, headers=HEADERS, params=params)
        logging.debug(
            f"Запрос выполнен: URL={response.url}, "
            f"Хэдеры={response.request.headers}, Параметры={params}")
        if response.status_code != 200:
            logging.error(
                f"Ошибка при выполнении запроса к API: {response.status_code}")
            raise RuntimeError(
                f"HTTP {response.status_code}: {response.reason}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при выполнении запроса к API: {e}")
        raise RuntimeError(f"Ошибка запроса: {e}")
    return response.json()


def check_response(response):
    """Проверяет полученный ответ"""


def parse_status(homework):
    """Извлекает статус конкретной домашней работы"""

    return f"Изменился статус проверки работы "{homework_name}". {verdict}"


def main():
    """Основная логика работы бота."""

    ...

    # Создаем объект класса бота
    # bot = Telebot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    ...

    while True:
        try:
            homework = requests.get(ENDPOINT, headers=HEADERS, params=payload)

        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            logging.error(message)
        ...


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s - %(name)s",
        handlers=[
            logging.FileHandler(__file__ + ".log", encoding="UTF-8", mode="w"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    main()
