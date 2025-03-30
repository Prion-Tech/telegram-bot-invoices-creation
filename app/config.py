import os

from app.exceptions import MissingBotTokenError

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOGGER_NAME = os.environ.get('LOGGER_NAME', 'telegram-bot-logger')

try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
except KeyError as e:
    raise MissingBotTokenError from e
