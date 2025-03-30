import asyncio

from telegram.ext import ContextTypes

from app.handlers import BaseInvoiceHandler


class LinguaInvoiceHandler(BaseInvoiceHandler):
    """Handles the Lingua invoice process."""

    async def trigger_flow(self, context: ContextTypes.DEFAULT_TYPE, username: str) -> None:
        """Background task for Lingua - simulates data analysis with progress updates."""


        try:
            self.logger.info(f"Starting Lingua flow for user {username}")
            chat_id = context.user_data.get("chat_id")

            await asyncio.sleep(1)
            msg = 'Some flow will be processing for Lingua...'
            await context.bot.send_message(chat_id=chat_id,text=msg)


            await asyncio.sleep(1)
            msg = 'All done...'
            await context.bot.send_message(chat_id=chat_id,text=msg)

            self.logger.info(f"Completed Lingua task A for user {username}")


        except Exception as e:
            self.logger.error(f"Error in Lingua task: {e}", exc_info=True)
            try:
                chat_id = context.user_data.get("chat_id")
                if chat_id:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text="Sorry, an error occurred during processing the flow."
                    )
            except Exception as notify_error:
                self.logger.error(f"Failed to notify user about error: {notify_error}")
