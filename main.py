import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = '8230814965:AAGdR9KvXi3QtMY4G_bALzVbvcBQqwZcvgk' 
MY_ID = 5848768601 
DATA_FILE = 'clients_data.json'

# تحميل وحفظ بيانات المحادثات
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

user_sessions = load_data()
user_states = {} # لتتبع الخدمة المختارة حالياً

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
        "يرجى اختيار الخدمة المطلوبة من القائمة:",
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
    user_states[query.from_user.id] = selected_service
    
    await query.edit_message_text(
        f"✅ لقد اخترت: *{selected_service}*\n\n"
        "من فضلك، أرسل الآن تفاصيل طلبك (نص، صور، أو ملفات) هنا مباشرة، وسأقوم بإيصالها للإدارة فوراً."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. الرد من الإدارة (أنت) على العميل
    if update.message.chat_id == MY_ID and update.message.reply_to_message:
        reply_id = str(update.message.reply_to_message.message_id)
        target_id = user_sessions.get(reply_id)
        
        if target_id:
            # إرسال النص أو أي وسائط يرد بها المهندس
            await context.bot.copy_message(chat_id=target_id, from_chat_id=MY_ID, message_id=update.message.message_id)
            await update.message.reply_text("✅ تم إرسال الرد للعميل.")
        else:
            await update.message.reply_text("⚠️ لا يوجد سجل لهذا الطلب.")
        return

    # 2. استقبال رسائل العملاء
    user_id = update.message.chat_id
    if user_id != MY_ID:
        service_name = user_states.get(user_id, "خدمة عامة")
        
        # إرسال إشعار للإدارة مع إعادة توجيه الرسالة/الملف
        msg = await context.bot.send_message(
            chat_id=MY_ID,
            text=f"🔔 **طلب جديد - {service_name}**\n👤 العميل: {update.message.from_user.full_name}\n\nالتفاصيل:"
        )
        await context.bot.copy_message(chat_id=MY_ID, from_chat_id=user_id, message_id=update.message.message_id)
        
        # حفظ الربط
        user_sessions[str(msg.message_id)] = user_id
        save_data(user_sessions)
        
        await update.message.reply_text("✅ تم استلام طلبك. سيقوم المهندس بالرد عليك قريباً.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.ALL, handle_message)) # يستقبل كل شيء (نصوص، صور، ملفات)
    print("البوت يعمل الآن ومحمّي...")
    app.run_polling()
