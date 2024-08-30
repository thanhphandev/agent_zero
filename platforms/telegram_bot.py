from telegram import Update, Chat
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ChatAction
from telegram.error import BadRequest
from agent import Agent
from python.helpers.print_style import PrintStyle
import asyncio
import random


class TelegramBot:
    def __init__(self, token: str, agent: Agent):
        self.token = token
        self.agent = agent
        self.application = Application.builder().token(self.token).build()

    async def start(self, update: Update, context: CallbackContext):
        if update.message:
            await update.message.reply_text("Hello! I'm your Agent. Type a message to start a conversation.")

    async def handle_message(self, update: Update, context: CallbackContext):
        if update.message:
            user_message = update.message.text or ""

            # Simulate typing action
            await update.message.chat.send_action(action=ChatAction.TYPING)

            # Handle streaming response
            await self.stream_response(update, user_message)

    async def stream_response(self, update: Update, user_message: str):
        async def stream(response_generator):
            full_response = ""
            message = None
            last_edit_length = 0

            for chunk in response_generator:
                full_response += chunk
                if len(full_response) >= last_edit_length + random.randint(30, 50):  # Send update every 30-50 new characters
                    if message:
                        try:
                            await message.edit_text(full_response)
                            last_edit_length = len(full_response)
                        except BadRequest as e:
                            if "Message is not modified" not in str(e):
                                raise  # Re-raise if it's not the "not modified" error
                        except Exception as e:
                            print(f"Unexpected error while editing message: {e}")
                    else:
                        message = await update.message.reply_text(full_response)
                        last_edit_length = len(full_response)
                    await asyncio.sleep(0.1)  # Small delay to avoid rate limiting

            # Send final message if there's any remaining text
            if full_response and len(full_response) > last_edit_length:
                if message:
                    await message.edit_text(full_response)
                else:
                    await update.message.reply_text(full_response)

            # Print to terminal
            PrintStyle(font_color="white", background_color="#1D8348", bold=True, padding=True).print(f"{self.agent.agent_name}: response:")
            PrintStyle(font_color="white").print(full_response)

        # Assuming agent.message_loop now returns a generator
        response_generator = self.agent.message_loop(user_message)
        await stream(response_generator)

    async def stop(self, update: Update, context: CallbackContext):
        await self.application.stop()

    def run(self):
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(CommandHandler("stop", self.stop))

        # Start the bot
        PrintStyle(font_color="blue").print("Telegram bot running. Press Ctrl+C to stop.")
        self.application.run_polling()


    
