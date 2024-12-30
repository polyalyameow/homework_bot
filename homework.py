import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import time

from dotenv import load_dotenv
import requests
import telebot
from telebot.apihelper import ApiException

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


RETRY_PERIOD = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}

HOMEWORK_VERDICTS = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания."
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(tokens)


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug("Сообщение отправлено.")
    except ApiException as error:
        logging.error(f"Ошибка при отправке сообщения: {error}")


def get_api_answer(timestamp):
    """Делает запрос к API."""
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        logging.debug(
            f"Запрос выполнен: URL={ENDPOINT}, "
            f"Хэдеры={HEADERS}, Параметры={params}")
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
    """Проверяет полученный ответ."""
    logging.debug("Проверка ответа сервера")
    if not isinstance(response, dict):
        raise TypeError("Неверный формат ответа.")
    if "homeworks" not in response or "current_date" not in response:
        raise KeyError(
            "Отсутствуют ключи homeworks или current_date в ответе API.")
    if not isinstance(response.get("homeworks"), list):
        raise TypeError("Неверный формат содержимого ключа homeworks.")
    return response["homeworks"]


def parse_status(homework):
    """Извлекает статус конкретной домашней работы."""
    logging.debug("Статус конкретной домашней работы")
    if 'homework_name' not in homework:
        raise KeyError('Отсутcтвует ключ "homework_name"')
    homework_name = homework['homework_name']
    homework_status = homework.get("status")
    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError(f"Неизвестный статус работы: {homework_status}")
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logging.info("Запускаем бот!")
    bot = telebot.TeleBot(token=TELEGRAM_TOKEN)
    if not check_tokens():
        send_message(bot, "Ошибка: отсутствуют необходимые токены.")
        logging.critical("Необходимые токены отсутствуют.")
        sys.exit(1)

    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                send_message(bot, message)
            timestamp = response.get("current_date", timestamp)
        except Exception as error:
            logging.error(f"Сбой в работе программы: {error}")
        time.sleep(RETRY_PERIOD)


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
