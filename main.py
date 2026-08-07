import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# --- الإعدادات ---
TOKEN = '8230814965:AAGdR9KvXi3QtMY4G_bALzVbvcBQqwZcvgk' 
MY_ID = 5848768601 
DATA_FILE = 'clients_data.json'
BOT_BRAND_NAME = "Al Hattami" 

# --- قاعدة بيانات المواد الدراسية ---
DATA = {
    "c_sharp": {
        "name": "💻 C# (سي شارب)",
        "lectures": [{"title": "📚 المحاضرة 1: مقدمة في لغة C#", "file_id": "PUT_FILE_ID_HERE"}],
        "courses": "🔗 كورس السي شارب الشامل:\n(سيتم إضافة روابط الكورسات هنا لاحقاً)",
        "docs": [{"title": "📄 كتاب أساسيات C#", "file_id": "PUT_FILE_ID_HERE"}]
    },
    "os": {
        "name": "⚙️ Operating System (نظم التشغيل)",
        "lectures": [{"title": "📚 المحاضرة 1: أنواع نظم التشغيل", "file_id": "PUT_FILE_ID_HERE"}],
        "courses": "🔗 شرح مادة نظم التشغيل:\n(سيتم إضافة الروابط لاحقاً)",
        "docs": [{"title": "📄 ملخص مفاهيم OS", "file_id": "PUT_FILE_ID_HERE"}]
    },
    "tech_writing": {
        "name": "📝 Technical Writing 1 (الكتابة التقنية 1)",
        "lectures": [{"title": "📚 المحاضرة 1: مقدمة في التقارير الفنية", "file_id": "PUT_FILE_ID_HERE"}],
        "courses": "🔗 كورس الكتابة التقنية والأكاديمية:\n(سيتم إضافة الروابط لاحقاً)",
        "docs": [{"title": "📄 قالب كتابة التقارير الرسمية", "file_id": "PUT_FILE_ID_HERE"}]
    },
    "dbms": {
        "name": "🗄️ Database Management Systems (نظم إدارة قواعد البيانات)",
        "lectures": [{"title": "📚 المحاضرة 1: مقدمة في ERD و SQL", "file_id": "PUT_FILE_ID_HERE"}],
        "courses": "🔗 كورس قواعد البيانات العملي:\n(سيتم إضافة الروابط لاحقاً)",
        "docs": [{"title": "📄 كتاب مرجع قواعد البيانات", "file_id": "PUT_FILE_ID_HERE"}]
    },
    "computer_math": {
        "name": "📐 Computer Math (رياضيات الحاسوب)",
        "lectures": [{"title": "📚 المحاضرة 1: الأنظمة العددية", "file_id": "PUT_FILE_ID_HERE"}],
        "courses": "🔗 فيديوهات شرح رياضيات الحاسوب:\n(سيتم إضافة الروابط لاحقاً)",
        "docs": [{"title": "📄 ملخص القوانين الرياضية للحاسوب", "file_id": "PUT_FILE_ID_HERE"}]
    },
    "internet_intro": {
        "name": "🌐 Introduction to Internet (مقدمة في الإنترنت)",
        "lectures": [{"title": "📚 المحاضرة 1: بروتوكولات الشبكة والإنترنت", "file_id": "PUT_FILE_ID_HERE"}],
        "courses": "🔗 كورس مفاهيم شبكة الإنترنت:\n(سيتم إضافة الروابط لاحقاً)",
        "docs": [{"title": "📄 كتاب مقدمة الإنترنت والويب", "file_id": "PUT_FILE_ID_HERE"}]
    },
    "conflict": {
        "name": "🇵🇸 Arabic Israeli Conflict (الصراع العربي الإسرائيلي)",
        "lectures": [{"title": "📚 المحاضرة 1: جذور وتاريخ القضية", "file_id": "PUT_FILE_ID_HERE"}],
        "courses": "🔗 وثائقيات ومحاضرات إثرائية:\n(سيتم إضافة الروابط لاحقاً)",
        "docs": [{"title": "📄 كتاب المنهج المعتمد للصراع", "file_id": "PUT_FILE_ID_HERE"}]
    },
    "hardware": {
        "name": "🔧 PC Hardware and Maintenance (صيانة عتاد الحاسوب)",
        "lectures": [{"title": "📚 المحاضرة 1: المكونات الداخلية للحاسوب", "file_id": "PUT_FILE_ID_HERE"}],
        "courses": "🔗 كورس صيانة الكمبيوتر العملي:\n(سيتم إضافة الروابط لاحقاً)",
        "docs": [{"title": "📄 دليل صيانة واستكشاف أخطاء الحاسوب", "file_id": "PUT_FILE_ID_HERE"}]
    }
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# أمر بدء عرض المواد للطلاب
async def start_materials(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton(item["name"], callback_data=f"mat_{key}")] for key, item in DATA.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"✨ مرحباً بك في بوت {BOT_BRAND_NAME}.\nالرجاء اختيار المادة التي تود تصفح محتواها:", reply_markup=reply_markup)

# معالج الضغط على الأزرار وقراءة البيانات
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("mat_"):
        subject_key = data.replace("mat_", "")
        keyboard = [
            [InlineKeyboardButton("📚 المحاضرات المرفوعة", callback_data=f"lec_{subject_key}")],
            [InlineKeyboardButton("💻 الكورسات والروابط", callback_data=f"crs_{subject_key}")],
            [InlineKeyboardButton("📄 المستندات والملفات", callback_data=f"doc_{subject_key}")],
            [InlineKeyboardButton("🔙 العودة لقائمة المواد", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"📂 أنت الآن داخل مادة:\n({DATA[subject_key]['name']})\n\nالرجاء اختيار القسم المطلوب:", reply_markup=reply_markup)

    elif data.startswith("lec_"):
        subject_key = data.replace("lec_", "")
        lectures = DATA[subject_key]["lectures"]
        await query.message.reply_text(f"⏳ جاري جلب وإرسال محاضرات مادة ({DATA[subject_key]['name']})...")
        
        for lec in lectures:
            if lec["file_id"] != "PUT_FILE_ID_HERE":
                await context.bot.send_document(chat_id=query.message.chat_id, document=lec["file_id"], caption=lec["title"])
            else:
                await query.message.reply_text(f"❌ {lec['title']}\n(لم يتم رفع ملف هذه المحاضرة بعد).")
        await show_back_button(query, subject_key)

    elif data.startswith("doc_"):
        subject_key = data.replace("doc_", "")
        docs = DATA[subject_key]["docs"]
        await query.message.reply_text(f"⏳ جاري جلب وإرسال مستندات مادة ({DATA[subject_key]['name']})...")
        
        for doc in docs:
            if doc["file_id"] != "PUT_FILE_ID_HERE":
                await context.bot.send_document(chat_id=query.message.chat_id, document=doc["file_id"], caption=doc["title"])
            else:
                await query.message.reply_text(f"❌ {doc['title']}\n(لم يتم رفع هذا المستند بعد).")
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

async def show_back_button(query, subject_key):
    keyboard = [[InlineKeyboardButton("🔙 عودة للمادة", callback_data=f"mat_{subject_key}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("👇 للعودة إلى خيارات المادة السابقة:", reply_markup=reply_markup)

# دالة لالتقاط واستخراج file_id لأي ملف ترقعه للبوت (خاصة بك كمشرف)
async def catch_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == MY_ID:
        if update.message.document:
            f_id = update.message.document.file_id
            await update.message.reply_text(f"📥 معرف الملف (file_id) الخاص بك جاهز:\n\n`{f_id}`", parse_mode="MarkdownV2")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # الربط والتحكم بالأوامر
    app.add_handler(CommandHandler("materials", start_materials))
    app.add_handler(CallbackQueryHandler(button_click))
    
    # معالج مخصص لك كمطور لمعرفة الـ file_id عند إرسال أي ملف PDF للبوت
    app.add_handler(MessageHandler(filters.Document.ALL, catch_file_id))

    print(f"[{BOT_BRAND_NAME}] Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()




