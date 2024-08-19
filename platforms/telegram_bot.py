from telegram import Update, Chat
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ChatAction
from telegram.error import BadRequest
from agent import Agent
from python.helpers.print_style import PrintStyle
import asyncio
import random


def start_telegram_bot(token: str, agent: Agent):
    # Initialize the Application with the bot token
    application = Application.builder().token(token).build()

    # Start command
    async def start(update: Update, context: CallbackContext):
        if update.message:
            await update.message.reply_text("Hello! I'm your Agent. Type a message to start a conversation.")

    # Message handler with improved streaming
    async def handle_message(update: Update, context: CallbackContext):
        if update.message:
            user_message = update.message.text or ""

            # Simulate typing action
            await update.message.chat.send_action(action=ChatAction.TYPING)

            # Create a function to handle streaming responses
            async def stream_response(response_generator):
                full_response = ""
                message = None
                last_edit_length = 0
                for chunk in response_generator:
                    full_response += chunk
                    if len(full_response) >= last_edit_length + random.randint(30, 50):  # Send update every 20 new characters
                        if message:
                            try:
                                await message.edit_text(full_response)
                                last_edit_length = len(full_response)
                            except BadRequest as e:
                                if "Message is not modified" not in str(e):
                                    raise  # Re-raise if it's not the "not modified" error
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
                PrintStyle(font_color="white", background_color="#1D8348", bold=True, padding=True).print(f"{agent.agent_name}: response:")
                PrintStyle(font_color="white").print(full_response)

            # Assuming agent.message_loop now returns a generator
            response_generator = agent.message_loop(user_message)
            await stream_response(response_generator)

    # Command to stop the bot (Optional)
    async def stop(update: Update, context: CallbackContext):
        await application.stop()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CommandHandler("stop", stop))

    # Start the bot
    application.run_polling()