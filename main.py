import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from services.ai_service import AIService

class InteriorDesignBot:
    def __init__(self, token, hf_token):
        self.app = ApplicationBuilder().token(token).build()
        self.ai_service = AIService(hf_token)
        self._add_handlers()

    def _add_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_text))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Send me a description of a room, or upload a photo to redecorate it!")

    # Handler for text prompts (Imagined Spaces)
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        prompt = update.message.text
        await update.message.reply_text("Designing your space... 🎨")

        image_path = generate_from_text(prompt)
        await update.message.reply_photo(photo=open(image_path, 'rb'), caption=f"Design for: {prompt}")

    # Handler for photos (Redecorating/Virtual Staging)
    async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Get the highest resolution version of the photo
        photo_file = await update.message.photo[-1].get_file()
        input_path = f"user_{update.effective_user.id}.jpg"
        await photo_file.download_to_drive(input_path)

        await update.message.reply_text("Analyzing your room... 🛋️")

        # Redesign using the caption as the prompt
        prompt = update.message.caption or "Modern interior design"
        output_path = redesign_from_image(input_path, prompt)

        await update.message.reply_photo(photo=open(output_path, 'rb'), caption="Here is your redecorated space!")

    def run(self):
        self.app.run_polling()

if __name__ == '__main__':
    load_dotenv()
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    hf_token = os.getenv("HF_TOKEN")
    bot = InteriorDesignBot(telegram_token, hf_token)
    bot.run()
