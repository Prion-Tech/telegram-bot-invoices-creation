from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, ConversationHandler)

from app.config import BOT_TOKEN
from app.handlers.error_handler import error_handler
from app.priontech_logging import setup_logging

logger = setup_logging()

logger.info('Starting bot...')

# States for the conversation handler
CHOOSING, PROCESSING_OPTION_A, PROCESSING_OPTION_B = range(3)


@error_handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends a wake-up message with options when the command /start is issued."""
    user = update.effective_user
    logger.info(f"User {user.username} started the bot")

    keyboard = [
        [
            InlineKeyboardButton("Granton", callback_data="granton"),
            InlineKeyboardButton("Lingua", callback_data="lingua"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Hello {user.first_name}!.\n\n"
        "Please choose one of the following options:",
        reply_markup=reply_markup,
    )

    return CHOOSING


@error_handler
async def granton_is_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the selection of Granton and starts the corresponding background task."""

    query = update.callback_query
    await query.answer()

    username = update.effective_user.username
    logger.info(f"User {username} selected Granton")

    await query.edit_message_text(
        text="You've selected Granton so it is hour based invoice."
    )

    # Store the chat_id in context for the background task to use
    context.user_data["chat_id"] = update.effective_chat.id

    # Create and schedule the background task
    from app.handlers import GrantonInvoiceHandler
    handler = GrantonInvoiceHandler()
    context.application.create_task(handler.trigger_flow(context, username))

    return PROCESSING_OPTION_A


async def lingua_is_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the selection of Lingua and starts the corresponding background task."""
    query = update.callback_query
    await query.answer()

    username = update.effective_user.username
    logger.info(f"User {username} selected Granton")

    await query.edit_message_text(
        text="You've selected Lingua so it is money based invoice."
    )

    # Store the chat_id in context for the background task to use
    context.user_data["chat_id"] = update.effective_chat.id

    # Create and schedule the background task
    from app.handlers import LinguaInvoiceHandler
    handler = LinguaInvoiceHandler()
    context.application.create_task(handler.trigger_flow(context, username))

    return PROCESSING_OPTION_B


@error_handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.effective_user
    logger.info(f"User {user.id} canceled the conversation")

    await update.message.reply_text("Operation canceled. Send /start to begin again.")

    return ConversationHandler.END


async def error_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler for the application."""
    logger.error(f"Update {update} caused error: {context.error}", exc_info=context.error)

    try:
        # Send a message to the user
        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, an unexpected error occurred. Please try again later."
            )
    except Exception as e:
        logger.error(f"Failed to send error message to user: {e}")


def main() -> None:
    """Set up and run the bot."""
    try:
        # Get the token from environment variable
        token = BOT_TOKEN

        # Create the Application
        application = Application.builder().token(token).build()

        # Set up conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                CHOOSING: [
                    CallbackQueryHandler(granton_is_selected, pattern="^granton"),
                    CallbackQueryHandler(lingua_is_selected, pattern="^lingua$"),
                ],
                PROCESSING_OPTION_A: [
                    CommandHandler("cancel", cancel),
                ],
                PROCESSING_OPTION_B: [
                    CommandHandler("cancel", cancel),
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
            allow_reentry=True,
        )

        application.add_handler(conv_handler)

        # Register error handler
        application.add_error_handler(error_callback)

        # Start the Bot
        logger.info("Starting bot...")
        application.run_polling()

    except Exception as e:
        logger.critical(f"Failed to start the bot: {e}", exc_info=True)


if __name__ == "__main__":
    main()
