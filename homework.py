from telebot import Telebot

from telegram import TelegramError
import logging
from logging.handlers import RotatingFileHandler
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
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info("Сообщение отправлено.")
    except TelegramError:
        logging.error('Сообщение не было отправлено.')
        raise TelegramError()


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
    logging.debug("Проверка ответа сервера")
    if not response:
        logging.error("Отсутствует ответ сервера")
        raise TypeError()
    if not isinstance(response, dict):
        logging.error("Неверный формат ответа.")
        raise TypeError()
    if "homeworks" not in response:
        logging.error("Ключа homeworks нет в ответе")
        raise KeyError()
    if "current_date" not in response:
        logging.error("Ключа current_date нет в ответе")
        raise KeyError()
    if not isinstance(response.get("homeworks"), list):
        logging.error("Неверный формат содержимого ключа homeworks.")
        raise TypeError()
    homeworks = response["homeworks"]
    if homeworks:
        return homeworks[0]
    else:
        logging.debug('Новых статусов нет')
        return False


def parse_status(homework):
    """Извлекает статус конкретной домашней работы"""
    logging.debug("Статус конкретной домашней работы")
    if 'homework_name' in homework:
        homework_name = homework['homework_name']
    else:
        raise KeyError('Отсутcтвует ключ "homework_name"')
    try:
        homework_status = homework['status']
        verdict = HOMEWORK_VERDICTS[homework_status]
    except KeyError as error:
        logging.error(f"Отсутвует ключ: {error}")
    return f"Изменился статус проверки работы '{homework_name}'. {verdict}"


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
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s - %(name)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler(__file__ + ".log", maxBytes=50_000_000,
                                backupCount=5, encoding="UTF-8")
        ]
    )
    main()
