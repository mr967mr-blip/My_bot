from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# التوكن الخاص بك مدمج هنا
TOKEN = '8230814965:AAGdR9KvXi3QtMY4G_bALzVbvcBQqwZcvgk'
MY_ID = 5848768601 # معرف حسابك الشخصي

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = update.message.chat_id
    text = update.message.text

    # إذا كانت الرسالة من الزبون (أي شخص غيرك)
    if chat_id != MY_ID:
        # رد ترحيبي وأنيق
        reply_text = (
            "وعليكم السلام ورحمة الله وبركاته، أهلاً بك.\n"
            "أنا المساعد الذكي الخاص بـ Al Hattami.\n"
            "لقد استلمت رسالتك، سأقوم بنقلها للإدارة فوراً وسيتواصلون معك بأقرب وقت ممكن.\n"
            "شكراً لصبرك."
        )
        await update.message.reply_text(reply_text)
        
        # إعادة توجيه الرسالة لك مع الاحتفاظ ببيانات الزبون للرد عليه لاحقاً
        await context.bot.forward_message(
            chat_id=MY_ID,
            from_chat_id=chat_id,
            message_id=update.message.message_id
        )
    
    # إذا كانت الرسالة منك أنت (للرد على الزبون)
    elif chat_id == MY_ID and update.message.reply_to_message:
        # استخراج ID الزبون من الرسالة المحولة التي قمت بالرد عليها
        target_id = update.message.reply_to_message.forward_from.id
        await context.bot.send_message(
            chat_id=target_id, 
            text=f"رسالة من إدارة Al Hattami:\n\n{text}"
        )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    # معالجة النصوص فقط (بدون الأوامر مثل /start)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("البوت يعمل الآن يا Al Hattami...")
    app.run_polling()
