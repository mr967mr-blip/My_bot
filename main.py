import json
import os
from telegram import Update
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

# user_sessions يحفظ {user_id: True} بمجرد أن يبدأ العميل محادثة فعلية
active_users = load_data() 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # رسالة ترحيبية مهنية
    welcome_text = (
        "✨ **مرحباً بك في خدمات Al Hatami للبرمجة والتصميم** ✨\n\n"
        "يسعدنا خدمتك! نحن متخصصون في تقديم حلول برمجية وتقنية متكاملة.\n"
        "يرجى اختيار الخدمة المطلوبة للبدء:"
    )
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = [
        [InlineKeyboardButton("📱 تصميم الباركودات", callback_data='barcode')],
        [InlineKeyboardButton("💻 تصميم الواجهات", callback_data='ui_design')],
        [InlineKeyboardButton("🗄 بناء قواعد البيانات", callback_data='database')],
        [InlineKeyboardButton("🚀 بناء مشاريع برمجية", callback_data='projects')],
        [InlineKeyboardButton("📝 حل التكاليف والمهام", callback_data='tasks')]
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # تسجيل أن العميل أصبح في وضع "الدردشة المفتوحة"
    active_users[str(query.from_user.id)] = True
    save_data(active_users)
    
    await query.edit_message_text(f"✅ تم اختيار: {query.data}\n\n"
                                  "تم استلام طلبك. يمكنك الآن إرسال أي تفاصيل أو ملفات أو صور، "
                                  "وسأكون معك مباشرة.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    # 1. إذا كنت أنت المرسل (الإدارة ترد على العميل)
    if update.message.chat_id == MY_ID and update.message.reply_to_message:
        # هنا سنعتمد على أن الرسالة التي ترد عليها تحتوي على ID العميل في الـ Forward
        # إذا لم تكن Forward، البوت سيحاول إرسالها لآخر شخص تواصل معه
        if update.message.reply_to_message.forward_from:
            target_id = update.message.reply_to_message.forward_from.id
            await context.bot.copy_message(chat_id=target_id, from_chat_id=MY_ID, message_id=update.message.message_id)
        else:
            await update.message.reply_text("⚠️ يرجى الرد على رسالة (Forward) قادمة من العميل.")
        return

    # 2. إذا كان المرسل هو العميل
    if update.message.chat_id != MY_ID:
        # إعادة توجيه أي شيء يرسله العميل إليك (صورة، نص، ملف)
        await context.bot.forward_message(chat_id=MY_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
        
        # إرسال تأكيد "مرة واحدة فقط" إذا لم يكن مسجلاً في القائمة
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

