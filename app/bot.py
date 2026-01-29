import logging
import random
import string
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, REDIS_HOST, REDIS_PORT, REDIS_DB, CODE_EXPIRE_TIME, VERIFICATION_QUEUE
import redis

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Redis connection
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True
    )
    redis_client.ping()
    logger.info("Redis ulanishi muvaffaqiyatli!")
except Exception as e:
    logger.error(f"Redis ulanish xatosi: {e}")
    redis_client = None

def generate_code():
    """Generate 4-digit verification code"""
    return ''.join(random.choices(string.digits, k=4))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    user_id = str(user.id)
    
    # Generate 4-digit code
    code = generate_code()
    
    # Create metadata
    metadata = {
        'user_id': user_id,
        'code': code,
        'username': user.username or '',
        'first_name': user.first_name or '',
        'last_name': user.last_name or ''
    }
    
    try:
        # Push metadata to Redis queue (lpush)
        redis_client.lpush(VERIFICATION_QUEUE, json.dumps(metadata))
        
        # Set expiration for the metadata key
        # Also store in a separate key for tracking
        key = f"verification:{user_id}"
        redis_client.setex(key, CODE_EXPIRE_TIME, code)
        
        logger.info(f"User {user_id} kod oldi: {code}")
        
        await update.message.reply_text(
            f"🔐 *Tasdiqlash kodi*\n\n"
            f"Sizning kodingiz: `{code}`\n\n"
            f"⏱ Kod {CODE_EXPIRE_TIME} soniya amal qiladi.\n"
            f"📱 Telegram ID: `{user_id}`\n\n"
            f"✅ Iltimos, saytda faqat kodni kiriting.\n"
            f"Telegram ID avtomatik aniqlandi!",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Redis xatosi: {e}")
        await update.message.reply_text(
            "❌ Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.\n"
            "Agar muammo davom etsa, administratorga murojaat qiling."
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
        "3. Saytda faqat kodni kiriting (ID kerak emas!)\n"
        f"4. Kod {CODE_EXPIRE_TIME} soniya amal qiladi"
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
    if not redis_client:
        logger.error("Redis ulanmagan! Botni ishga tushirish mumkin emas.")
        return
    
    logger.info("Bot ishga tushmoqda...")
    
    # Create application
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verify", verify))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    logger.info("Bot ishga tushdi! Redis orqali ishlayapti.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()