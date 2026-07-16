import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = '8230814965:AAGdR9KvXi3QtMY4G_bALzVbvcBQqwZcvgk' 
MY_ID = 5848768601 
DATA_FILE = 'clients_data.json'

# تحميل بيانات العملاء المحفوظة
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# حفظ بيانات العملاء
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

user_sessions = load_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 تصميم الباركودات", callback_data='barcode')],
        [InlineKeyboardButton("💻 تصميم الواجهات (UI/UX)", callback_data='ui_design')],
        [InlineKeyboardButton("🗄 بناء قواعد البيانات", callback_data='database')],
        [InlineKeyboardButton("🚀 بناء مشاريع برمجية", callback_data='projects')],
        [InlineKeyboardButton("📝 حل التكاليف والمهام", callback_data='tasks')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✨ **مرحباً بك في خدمات البرمجة والتصميم** ✨\n\n"
        "يرجى اختيار الخدمة المطلوبة:",
        reply_markup=reply_markup
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    services = {
        'barcode': "تصميم الباركودات", 'ui_design': "تصميم الواجهات",
        'database': "قواعد البيانات", 'projects': "المشاريع البرمجية", 'tasks': "حل التكاليف"
    }
    
    selected_service = services.get(query.data)
    
    # إرسال إشعار لك
    msg = await context.bot.send_message(
        chat_id=MY_ID,
        text=f"🔔 **طلب جديد**\n👤 من: {query.from_user.full_name}\n📂 الخدمة: {selected_service}\n\n*رد على هذه الرسالة للتواصل مع العميل.*"
    )
    
    # حفظ الربط بين رسالتك و ID العميل
    user_sessions[str(msg.message_id)] = query.from_user.id
    save_data(user_sessions)
    
    await query.edit_message_text(f"✅ تم استلام طلبك ({selected_service}). سيتواصل معك الفريق قريباً.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # إذا كانت الرسالة منك ومردودة على رسالة إشعار
    if update.message.chat_id == MY_ID and update.message.reply_to_message:
        reply_id = str(update.message.reply_to_message.message_id)
        target_id = user_sessions.get(reply_id)
        
        if target_id:
            await context.bot.send_message(target_id, f"💬 **رد من الإدارة:**\n\n{update.message.text}")
            await update.message.reply_text("✅ تم إرسال الرد للعميل.")
        else:
            await update.message.reply_text("⚠️ لا يوجد سجل لهذا الطلب.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("البوت يعمل الآن ومحمّي...")
    app.run_polling()


