import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# --- الإعدادات ---
TOKEN = '8230814965:AAGdR9KvXi3QtMY4G_bALzVbvcBQqwZcvgk' 
MY_ID = 5848768601 
DATA_FILE = 'clients_data.json'
BOT_BRAND_NAME = "Al Hattami" 

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

active_users = load_data() 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        f"✨ **Welcome to {BOT_BRAND_NAME}** ✨\n\n"
        "We are here to provide creative technical and programming solutions.\n"
        "Please select the service you need:"
    )
    
    keyboard = [
        [InlineKeyboardButton("💻 UI Design & Programming", callback_data='ui_design')],
        [InlineKeyboardButton("🗄 Database Systems", callback_data='database')],
        [InlineKeyboardButton("📱 Barcode & Apps", callback_data='barcode')],
        [InlineKeyboardButton("🎨 Branding & Logos", callback_data='branding')],
        [InlineKeyboardButton("📸 Social Media Designs", callback_data='social_media')],
        [InlineKeyboardButton("📇 Cards & Invitations", callback_data='cards_inv')],
        [InlineKeyboardButton("📝 Tasks & Homework", callback_data='tasks')]
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    service_names = {
        'ui_design': 'UI Design & Programming',
        'database': 'Database Systems',
        'barcode': 'Barcode & Apps',
        'branding': 'Branding & Logos',
        'social_media': 'Social Media Designs',
        'cards_inv': 'Cards & Invitations',
        'tasks': 'Tasks & Homework'
    }
    
    selected_service = service_names.get(query.data, query.data)
    await query.edit_message_text(
        f"✅ **Selected Service:** {selected_service}\n\n"
        "Your request has been received. You can now send any details or files, "
        "and I will be with you shortly. Thank you for choosing **Al Hattami**.",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id

    # الرد على الإدارة (Reply)
    if chat_id == MY_ID and update.message.reply_to_message:
        if update.message.reply_to_message.forward_from:
            target_id = update.message.reply_to_message.forward_from.id
            await context.bot.copy_message(chat_id=target_id, from_chat_id=MY_ID, message_id=update.message.message_id)
            await update.message.reply_text("✅ Reply sent to client.", parse_mode='Markdown')
        return

    # استقبال رسائل العملاء
    if chat_id != MY_ID:
        await context.bot.forward_message(chat_id=MY_ID, from_chat_id=chat_id, message_id=update.message.message_id)
        
        if str(chat_id) not in active_users:
            active_users[str(chat_id)] = True
            save_data(active_users)
            await update.message.reply_text(
                f"👋 **Welcome to {BOT_BRAND_NAME}!**\n\n"
                "Your message has been received. Our team will review it and reply as soon as possible.",
                parse_mode='Markdown'
            )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    print(f"🤖 {BOT_BRAND_NAME} bot is now running...")
    app.run_polling()



