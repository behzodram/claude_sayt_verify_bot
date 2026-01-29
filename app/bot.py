import logging
import random
import string
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
import json
import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Simple in-memory storage (Redis alternative)
verification_codes = {}

def generate_code():
    """Generate 4-digit verification code"""
    return ''.join(random.choices(string.digits, k=4))

def save_verification(user_id, code):
    """Save verification code with expiration"""
    expire_time = datetime.now() + timedelta(minutes=1)
    verification_codes[user_id] = {
        'code': code,
        'expires_at': expire_time.isoformat()
    }
    # Save to file for persistence across restarts
    save_verification_data()

def load_verifications():
    """Load verification codes from file"""
    if os.path.exists('verification_data.json'):
        try:
            with open('verification_data.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def get_verification(user_id):
    """Get verification code if not expired"""
    if user_id in verification_codes:
        data = verification_codes[user_id]
        expire_time = datetime.fromisoformat(data['expires_at'])
        if datetime.now() < expire_time:
            return data['code']
        else:
            # Code expired, remove it
            del verification_codes[user_id]
            save_verification_data()
    return None

def verify_code(user_id, code):
    """Verify the code and return user_id if valid"""
    stored_code = get_verification(user_id)
    if stored_code and stored_code == code:
        # Remove used code
        del verification_codes[user_id]
        save_verification_data()
        return user_id
    return None

def save_verification_data():
    """Save current verification data to file"""
    # Clean expired codes first
    current_time = datetime.now()
    valid_codes = {
        k: v for k, v in verification_codes.items()
        if datetime.fromisoformat(v['expires_at']) > current_time
    }
    verification_codes.clear()
    verification_codes.update(valid_codes)
    
    with open('verification_data.json', 'w') as f:
        json.dump(verification_codes, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    code = generate_code()
    save_verification(str(user.id), code)
    
    logger.info(f"User {user.id} requested verification code: {code}")
    
    await update.message.reply_text(
        f"🔐 *Tasdiqlash kodi*\n\n"
        f"Sizning kodingiz: `{code}`\n\n"
        f"⏱ Kod 1 daqiqada amal qiladi.\n"
        f"📱 Telegram ID: `{user.id}`\n\n"
        f"Iltimos, saytda ushbu kodni kiriting.",
        parse_mode='Markdown'
    )

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /verify command to get new code"""
    await start(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "🤖 *Bot buyruqlari:*\n\n"
        "/start - Yangi tasdiqlash kodi olish\n"
        "/verify - Tasdiqlash kodi olish\n"
        "/help - Yordam\n\n"
        "📝 *Qanday ishlatish:*\n"
        "1. /start buyrug'ini yuboring\n"
        "2. Sizga 4 raqamli kod yuboriladi\n"
        "3. Kodni saytga kiriting\n"
        "4. Kod 1 daqiqa amal qiladi"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    await update.message.reply_text(
        "Yangi tasdiqlash kodi olish uchun /start yoki /verify buyrug'ini yuboring.\n\n"
        "Yordam uchun /help buyrug'ini yuboring."
    )

def main():
    """Start the bot"""
    # Load existing verifications
    global verification_codes
    verification_codes = load_verifications()
    
    logger.info("Starting bot...")
    
    # Create application
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verify", verify))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    logger.info("Bot ishga tushdi!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()