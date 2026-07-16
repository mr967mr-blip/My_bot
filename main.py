from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# ضع هنا التوكين الجديد الذي حصلت عليه من BotFather
TOKEN = '8230814965:AAGdR9KvXi3QtMY4G_bALzVbvcBQqwZcvgk' 
MY_ID = 5848768601 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 تصميم الباركودات", callback_data='barcode')],
        [InlineKeyboardButton("💻 تصميم الواجهات (UI/UX)", callback_data='ui_design')],
        [InlineKeyboardButton("🗄 بناء قواعد البيانات", callback_data='database')],
        [InlineKeyboardButton("🚀 بناء مشاريع برمجية", callback_data='projects')],
        [InlineKeyboardButton("📝 حل التكاليف والمهام", callback_data='tasks')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "✨ **مرحباً بك في Al Hattami لخدمات البرمجة والتصميم** ✨\n\n"
        "يسعدنا خدمتك! نحن متخصصون في تقديم حلول برمجية وتقنية متكاملة.\n"
        "يرجى اختيار الخدمة المطلوبة من القائمة أدناه للبدء:"
    )
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    services = {
        'barcode': "تصميم الباركودات الذكية",
        'ui_design': "تصميم واجهات احترافية وجذابة",
        'database': "بناء وإدارة قواعد البيانات",
        'projects': "بناء وتطوير المشاريع البرمجية",
        'tasks': "حل التكاليف البرمجية والتقنية"
    }
    
    selected_service = services.get(query.data)
    
    await query.edit_message_text(
        f"✅ لقد اخترت: *{selected_service}*\n\n"
        "من فضلك، اكتب تفاصيل طلبك هنا (أو أرفق صوراً/ملفات إذا لزم الأمر)، "
        "وسأقوم بإيصال طلبك للمهندس فوراً."
    )
    
    await context.bot.send_message(
        chat_id=MY_ID,
        text=f"🔔 **طلب خدمة جديد**\n\n👤 العميل: {query.from_user.full_name}\n📂 الخدمة: {selected_service}\n\n*يرجى الرد على هذا الإشعار للبدء مع العميل.*"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id == MY_ID and update.message.reply_to_message:
        try:
            # محاولة الحصول على الـ ID من الرسالة المحولة (Forward)
            # لاحظ: إذا قام الزبون بإخفاء هويته، لن يعمل الرد التلقائي
            target_id = update.message.reply_to_message.forward_from.id if update.message.reply_to_message.forward_from else None
            if target_id:
                await context.bot.send_message(target_id, f"💬 **رد من إدارة Al Hattami:**\n\n{update.message.text}")
            else:
                await update.message.reply_text("⚠️ لا يمكن الرد: العميل يخفي معلومات حسابه أو الرسالة ليست محولة بشكل صحيح.")
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ في إرسال الرد: {e}")
    
    elif update.message.chat_id != MY_ID:
        await update.message.reply_text("👋 أهلاً بك! يرجى استخدام القائمة لاختيار الخدمة المطلوبة ليتم تسجيل طلبك بدقة.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("البوت الاحترافي يعمل الآن...")
    app.run_polling()

