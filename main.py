import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from services.ai_service import AIService

# --- Setup Flask ---
app = Flask(__name__)

# --- Bot Logic Class ---
class InteriorDesignBot:
    def __init__(self, token, hf_token):
        # Build the app (Synchronous part)
        self.app = ApplicationBuilder().token(token).build()
        self.ai_service = AIService(hf_token)
        self._add_handlers()
        self.is_ready = False # Track if async setup is done

    def _add_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_text))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))

    async def ensure_ready(self):
        """Lazy initialization for production server"""
        if not self.is_ready:
            await self.app.initialize()
            await self.app.start()
            self.is_ready = True

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Send me a description or a photo! 🏠")

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        prompt = update.message.text
        await update.message.reply_text(f"Designing based on: {prompt}...")
        # Add your AI logic here:
        # img = self.ai_service.generate(prompt)
        # await update.message.reply_photo(img)

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Processing your photo... 🖼️")
        # Add your AI logic here

# --- Configuration ---
# NOTE: load_dotenv is not strictly needed on Render (we use Environment settings in UI),
# but good to keep for local testing.
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 

# Create global instance
bot_instance = InteriorDesignBot(TELEGRAM_TOKEN, HF_TOKEN)

# --- Routes ---

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Endpoint for Telegram Updates"""
    if request.method == "POST":
        # 1. Ensure bot is initialized (Crucial for Render)
        await bot_instance.ensure_ready()

        # 2. Process Update
        update_json = request.get_json(force=True)
        update = Update.de_json(update_json, bot_instance.app.bot)
        
        # 3. Feed to bot
        await bot_instance.app.process_update(update)
        
        return "OK", 200
    return "Invalid", 400

@app.route('/')
def index():
    return "Interior Design Bot is Live on Render! 🚀"

@app.route('/set_webhook')
async def set_webhook():
    """Run this URL once to tell Telegram where your Render app is"""
    await bot_instance.ensure_ready()
    
    # Construct the full URL. Render provides the base URL.
    # If WEBHOOK_URL is set in env, use it, otherwise try to guess (risky)
    webhook_endpoint = f"{WEBHOOK_URL}/webhook"
    
    success = await bot_instance.app.bot.set_webhook(webhook_endpoint)
    if success:
        return f"Webhook successfully set to {webhook_endpoint}", 200
    return "Failed to set webhook", 500
