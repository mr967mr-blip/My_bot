import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# --- الإعدادات ---
TOKEN = '8230814965:AAGdR9KvXi3QtMY4G_bALzVbvcBQqwZcvgk' 
MY_ID = 5848768601 
DATA_FILE = 'clients_data.json'
BOT_BRAND_NAME = "بوت المندوب" 

# الهيكل الأساسي للمواد بأسماء مدمجة (عربي + إنجليزي) لسهولة الفهم
DEFAULT_DATA = {
    "c_sharp": {"name": "💻 C# - سي شارب", "lectures": [], "courses": "🔗 كورس السي شارب الشامل لاحقاً", "docs": []},
    "os": {"name": "⚙️ Operating System - نظم التشغيل", "lectures": [], "courses": "🔗 شرح مادة نظم التشغيل لاحقاً", "docs": []},
    "tech_writing": {"name": "📝 Technical Writing 1 - الكتابة التقنية 1", "lectures": [], "courses": "🔗 كورس الكتابة التقنية لاحقاً", "docs": []},
    "dbms": {"name": "🗄️ Database Management Systems - نظم إدارة قواعد البيانات", "lectures": [], "courses": "🔗 كورس قواعد البيانات لاحقاً", "docs": []},
    "computer_math": {"name": "📐 Computer Math - رياضيات الحاسوب", "lectures": [], "courses": "🔗 فيديوهات رياضيات الحاسوب", "docs": []},
    "internet_intro": {"name": "🌐 Introduction to Internet - مقدمة في الإنترنت", "lectures": [], "courses": "🔗 كورس شبكة الإنترنت", "docs": []},
    "conflict": {"name": "🇵🇸 Arabic Israeli Conflict - الصراع العربي الإسرائيلي", "lectures": [], "courses": "🔗 وثائقيات القضية", "docs": []},
    "hardware": {"name": "🔧 PC Hardware and Maintenance - صيانة عتاد الحاسوب", "lectures": [], "courses": "🔗 كورس صيانة الكمبيوتر", "docs": []}
}

# دالة تحميل البيانات
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
                # تحديث الأسماء في الملف المخزن إذا كانت قديمة لتصبح ثنائية اللغة
                for key in DEFAULT_DATA:
                    if key in current_data:
                        current_data[key]["name"] = DEFAULT_DATA[key]["name"]
                return current_data
        except Exception:
            return DEFAULT_DATA
    return DEFAULT_DATA

# دالة حفظ البيانات
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# تحميل البيانات عند بدء تشغيل البوت
DATA = load_data()

# أمر /start للطلاب مع الرسالة الترحيبية الجديدة لـ "بوت المندوب"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton(item["name"], callback_data=f"mat_{key}")] for key, item in DATA.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    first_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"✨ مرحباً بك يا {first_name} في **{BOT_BRAND_NAME}** التعليمي.\n\n"
        f"الرجاء اختيار المادة الدراسية لتصفح محتواها السابق من محاضرات وملازم 👇:", 
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# معالج تفاعل الطلاب والمشرف مع الأزرار
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global DATA
    query = update.callback_query
    await query.answer()
    data = query.data

    # تصفح المواد للطلاب
    if data.startswith("mat_"):
        subject_key = data.replace("mat_", "")
        keyboard = [
            [InlineKeyboardButton("📚 المحاضرات المرفوعة", callback_data=f"lec_{subject_key}")],
            [InlineKeyboardButton("💻 الكورسات والروابط", callback_data=f"crs_{subject_key}")],
            [InlineKeyboardButton("📄 المستندات والملازم", callback_data=f"doc_{subject_key}")],
            [InlineKeyboardButton("🔙 العودة لقائمة المواد", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"📂 أنت الآن داخل مادة:\n({DATA[subject_key]['name']})\n\nالرجاء اختيار القسم المطلوب:", reply_markup=reply_markup)

    elif data.startswith("lec_"):
        subject_key = data.replace("lec_", "")
        lectures = DATA[subject_key]["lectures"]
        if not lectures:
            await query.message.reply_text(f"📭 لا توجد محاضرات مرفوعة حالياً لمادة ({DATA[subject_key]['name']}).")
        else:
            await query.message.reply_text(f"⏳ جاري إرسال محاضرات مادة ({DATA[subject_key]['name']})...")
            for lec in lectures:
                await context.bot.send_document(chat_id=query.message.chat_id, document=lec["file_id"], caption=lec["title"])
        await show_back_button(query, subject_key)

    elif data.startswith("doc_"):
        subject_key = data.replace("doc_", "")
        docs = DATA[subject_key]["docs"]
        if not docs:
            await query.message.reply_text(f"📭 لا توجد ملازم أو مستندات مرفوعة حالياً لمادة ({DATA[subject_key]['name']}).")
        else:
            await query.message.reply_text(f"⏳ جاري إرسال ملازم مادة ({DATA[subject_key]['name']})...")
            for doc in docs:
                await context.bot.send_document(chat_id=query.message.chat_id, document=doc["file_id"], caption=doc["title"])
        await show_back_button(query, subject_key)

    elif data.startswith("crs_"):
        subject_key = data.replace("crs_", "")
        keyboard = [[InlineKeyboardButton("🔙 عودة للمادة", callback_data=f"mat_{subject_key}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=DATA[subject_key]["courses"], reply_markup=reply_markup)

    elif data == "back_to_main":
        keyboard = [[InlineKeyboardButton(item["name"], callback_data=f"mat_{key}")] for key, item in DATA.items()]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("✨ القائمة الرئيسية:\nالرجاء اختيار المادة الدراسية:", reply_markup=reply_markup)

    # --- لوحة تحكم المشرف (إضافة الملفات تلقائياً) ---
    elif data.startswith("adm_set_sub_"):
        sub = data.replace("adm_set_sub_", "")
        context.user_data["upload_sub"] = sub
        
        keyboard = [
            [InlineKeyboardButton("📚 قسم المحاضرات", callback_data="adm_set_cat_lectures")],
            [InlineKeyboardButton("📄 قسم المستندات والملازم", callback_data="adm_set_cat_docs")]
        ]
        await query.edit_message_text("⚙️ ممتاز، الآن اختر القسم الذي تريد وضع الملف فيه:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("adm_set_cat_"):
        cat = data.replace("adm_set_cat_", "")
        sub = context.user_data.get("upload_sub")
        f_id = context.user_data.get("upload_file_id")
        f_name = context.user_data.get("upload_file_name")

        if sub and f_id:
            DATA[sub][cat].append({"title": f_name, "file_id": f_id})
            save_data(DATA)
            
            await query.edit_message_text(f"✅ تم بنجاح إضافة وتثبيت الملف:\n🏷️ اسم الملف: {f_name}\n📂 في مادة: {DATA[sub]['name']}\n🗂️ القسم: {cat}")
            context.user_data.clear()

async def show_back_button(query, subject_key):
    keyboard = [[InlineKeyboardButton("🔙 عودة للمادة", callback_data=f"mat_{subject_key}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("👇 للعودة إلى خيارات المادة السابقة:", reply_markup=reply_markup)

# استقبال الملفات من المندوب (المشرف) وتوجيهها للوحة التحكم تلقائياً
async def admin_receive_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == MY_ID and update.message.document:
        doc = update.message.document
        context.user_data["upload_file_id"] = doc.file_id
        context.user_data["upload_file_name"] = doc.file_name if doc.file_name else "ملف دراسي جديد"
        
        keyboard = [[InlineKeyboardButton(f"📥 إضافة إلى: {item['name']}", callback_data=f"adm_set_sub_{key}")] for key, item in DATA.items()]
        await update.message.reply_text(
            f"📥 تم استلام الملف: `{doc.file_name}` بنجاح.\n\nإلى أي مادة دراسية تود إضافة هذا الملف؟", 
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.Document.ALL, admin_receive_document))

    print(f"[{BOT_BRAND_NAME}] Dynamic Bot is running perfectly with bilingual names...")
    app.run_polling()

if __name__ == '__main__':
    main()






