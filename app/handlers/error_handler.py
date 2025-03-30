import asyncio
from functools import wraps

from telegram.error import NetworkError, TelegramError, TimedOut
from telegram.ext import ConversationHandler

from app.priontech_logging import load_logger


def error_handler(func):
    """Decorator to handle errors in the bot commands."""
    logger = load_logger()
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except (NetworkError, TimedOut) as e:
            logger.error(f"Network error occurred, retry in 1s. ERROR DETAIL:: {e}")
            await asyncio.sleep(1)
            try:
                return await func(update, context, *args, **kwargs)
            except Exception as retry_error:
                logger.error(f"Retry also failed: {retry_error}")
                await update.message.reply_text("Network issue detected. Please try again later.")
        except TelegramError as e:
            logger.error(f"Telegram API error: {e}")
            await update.message.reply_text("Sorry, a Telegram API error occurred. Please try again later.")
        except Exception as e:
            logger.error(f"Unhandled error: {e}", exc_info=True)
            await update.message.reply_text("An unexpected error occurred. Our team has been notified.")
        return ConversationHandler.END

    return wrapper
