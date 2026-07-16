import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = '8230814965:AAGdR9KvXi3QtMY4G_bALzVbvcBQqwZcvgk' 
MY_ID = 5848768601 
DATA_FILE = 'clients_data.json'

# تحميل وحفظ سجلات العملاء
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
        "✨ **مرحباً بك في خدمات Al Hatami للبرمجة والتصميم** ✨\n\n"
        "يسعدنا خدمتك! نحن متخصصون في تقديم حلول برمجية وتقنية إبداعية.\n"
        "يرجى اختيار الخدمة المطلوبة للبدء:"
    )
    
    keyboard = [
        [InlineKeyboardButton("💻 تطوير الواجهات والبرمجة", callback_data='ui_design')],
        [InlineKeyboardButton("🗄 بناء قواعد البيانات", callback_data='database')],
        [InlineKeyboardButton("📱 تصميم الباركودات والتطبيقات", callback_data='barcode')],
        [InlineKeyboardButton("🎨 تصميم الهوية والشعارات", callback_data='branding')],
        [InlineKeyboardButton("📸 تصاميم السوشيال ميديا", callback_data='social_media')],
        [InlineKeyboardButton("📇 تصميم كروت ودعوات", callback_data='cards_inv')],
        [InlineKeyboardButton("📝 حل التكاليف والمهام", callback_data='tasks')]
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    
    active_users[str(user.id)] = True
    save_data(active_users)
    
    service_names = {
        'ui_design': 'تطوير الواجهات والبرمجة',
        'database': 'بناء قواعد البيانات',
        'barcode': 'تصميم الباركودات والتطبيقات',
        'branding': 'تصميم الهوية والشعارات',
        'social_media': 'تصاميم السوشيال ميديا',
        'cards_inv': 'تصميم كروت ودعوات',
        'tasks': 'حل التكاليف والمهام'
    }
    
    selected_service = service_names.get(query.data, query.data)

    # تنبيه الإدارة
    alert_message = (
        f"🔔 **طلب خدمة جديد** 🔔\n\n"
        f"👤 **العميل:** {user.full_name}\n"
        f"🆔 **المعرف:** `{user.id}`\n"
        f"🛠 **الخدمة المختارة:** {selected_service}"
    )
    await context.bot.send_message(chat_id=MY_ID, text=alert_message, parse_mode='Markdown')
    
    await query.edit_message_text(f"✅ تم اختيار: {selected_service}\n\n"
                                  "تم استلام طلبك. يمكنك الآن إرسال أي تفاصيل أو ملفات أو صور، "
                                  "وسأكون معك مباشرة.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id == MY_ID and update.message.reply_to_message:
        if update.message.reply_to_message.forward_from:
            target_id = update.message.reply_to_message.forward_from.id
            await context.bot.copy_message(chat_id=target_id, from_chat_id=MY_ID, message_id=update.message.message_id)
        else:
            await update.message.reply_text("⚠️ يرجى الرد على رسالة (Forward) قادمة من العميل.")
        return

    if update.message.chat_id != MY_ID:
        await context.bot.forward_message(chat_id=MY_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
        
        if str(update.message.chat_id) not in active_users:
            await update.message.reply_text("✅ تم استلام رسالتك، سيقوم المهندس بالرد عليك في أقرب وقت.")
            active_users[str(update.message.chat_id)] = True
            save_data(active_users)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    print("البوت يعمل الآن ومحمّي...")
    app.run_polling()


