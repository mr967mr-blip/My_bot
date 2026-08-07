بالتأكيد، إليك الكود الكامل والمحدث بالتوكن الجديد والميزات المطلوبة (النصوص التوضيحية، قسم التكاليف، الكورسات التفاعلية، وميزة الحذف) جاهز للنسخ المباشر:

```python
import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# تفعيل تسجيل الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- الإعدادات ---
# التوكن الجديد الخاص بك
TOKEN = '8230814965:AAGiWxAKGtajAMBZ6CD5gn-mUtRv22yIkdA' 
MY_ID = 5848768601 
DATA_FILE = 'clients_data.json'
BOT_BRAND_NAME = "بوت المندوب" 

# الهيكل الأساسي للمواد الدراسية
DEFAULT_DATA = {
    "c_sharp": {"name": "💻 C# - سي شارب", "lectures": [], "courses": [], "docs": [], "assignments": []},
    "os": {"name": "⚙️ Operating System - نظم التشغيل", "lectures": [], "courses": [], "docs": [], "assignments": []},
    "tech_writing": {"name": "📝 Technical Writing 1 - الكتابة التقنية 1", "lectures": [], "courses": [], "docs": [], "assignments": []},
    "dbms": {"name": "🗄️ Database Management Systems - نظم إدارة قواعد البيانات", "lectures": [], "courses": [], "docs": [], "assignments": []},
    "computer_math": {"name": "📐 Computer Math - رياضيات الحاسوب", "lectures": [], "courses": [], "docs": [], "assignments": []},
    "internet_intro": {"name": "🌐 Introduction to Internet - مقدمة في الإنترنت", "lectures": [], "courses": [], "docs": [], "assignments": []},
    "conflict": {"name": "🇵🇸 Arabic Israeli Conflict - الصراع العربي الإسرائيلي", "lectures": [], "courses": [], "docs": [], "assignments": []},
    "hardware": {"name": "🔧 PC Hardware and Maintenance - صيانة عتاد الحاسوب", "lectures": [], "courses": [], "docs": [], "assignments": []}
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
                for key in DEFAULT_DATA:
                    if key in current_data:
                        current_data[key]["name"] = DEFAULT_DATA[key]["name"]
                        for section in ["lectures", "docs", "assignments", "courses"]:
                            if section not in current_data[key]:
                                current_data[key][section] = []
                            if section == "courses" and not isinstance(current_data[key][section], list):
                                current_data[key][section] = []
                return current_data
        except Exception:
            return DEFAULT_DATA
    return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

DATA = load_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton(item["name"], callback_data=f"mat_{key}")] for key, item in DATA.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    first_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"✨ مرحباً بك يا {first_name} في **{BOT_BRAND_NAME}** التعليمي.\n\n"
        f"الرجاء اختيار المادة الدراسية لتصفح محتواها 👇:", 
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global DATA
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("mat_"):
        subject_key = data.replace("mat_", "")
        keyboard = [
            [InlineKeyboardButton("📚 المحاضرات", callback_data=f"sec_{subject_key}_lectures"), InlineKeyboardButton("📄 الملازم", callback_data=f"sec_{subject_key}_docs")],
            [InlineKeyboardButton("📝 التكاليف", callback_data=f"sec_{subject_key}_assignments"), InlineKeyboardButton("💻 الكورسات", callback_data=f"sec_{subject_key}_courses")],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="back_to_main")]
        ]
        await query.edit_message_text(text=f"📂 مادة: ({DATA[subject_key]['name']})", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("sec_"):
        parts = data.split("_")
        subject_key = parts[1]
        category = parts[2]
        titles = {"lectures": "المحاضرات", "docs": "الملازم", "assignments": "التكاليف", "courses": "الكورسات"}
        await send_section_content(query, context, subject_key, category, titles.get(category, "القسم"), user_id)

    elif data == "back_to_main":
        keyboard = [[InlineKeyboardButton(item["name"], callback_data=f"mat_{key}")] for key, item in DATA.items()]
        await query.edit_message_text("✨ القائمة الرئيسية:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("adm_set_sub_"):
        context.user_data["upload_sub"] = data.replace("adm_set_sub_", "")
        keyboard = [
            [InlineKeyboardButton("📚 محاضرات", callback_data="adm_set_cat_lectures"), InlineKeyboardButton("📄 ملازم", callback_data="adm_set_cat_docs")],
            [InlineKeyboardButton("📝 تكاليف", callback_data="adm_set_cat_assignments"), InlineKeyboardButton("💻 كورسات", callback_data="adm_set_cat_courses")]
        ]
        await query.edit_message_text("⚙️ اختر القسم:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("adm_set_cat_"):
        cat = data.replace("adm_set_cat_", "")
        context.user_data["upload_cat"] = cat
        if cat == "courses" and "upload_file_id" not in context.user_data:
            await query.edit_message_text("✍️ أرسل الآن رابط الكورس أو النص:")
        else:
            await query.edit_message_text("✍️ أرسل الوصف (Caption) أو أرسل . للاكتفاء بالاسم:")

    elif data.startswith("del_"):
        if user_id == MY_ID:
            parts = data.split("_")
            sub, cat, idx = parts[1], parts[2], int(parts[3])
            try:
                DATA[sub][cat].pop(idx)
                save_data(DATA)
                await query.answer("🗑️ تم الحذف")
                await query.message.delete()
            except: await query.answer("❌ خطأ")
        else: await query.answer("❌ لا تملك صلاحية", show_alert=True)

async def send_section_content(query, context, subject_key, category, title, user_id):
    items = DATA[subject_key][category]
    if not items:
        await query.message.reply_text(f"📭 قسم {title} فارغ حالياً.")
    else:
        for index, item in enumerate(items):
            reply_markup = None
            if user_id == MY_ID:
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🗑️ حذف", callback_data=f"del_{subject_key}_{category}_{index}")]])
            cap = item.get("caption", "")
            if "file_id" in item:
                if item.get("type") == "photo":
                    await context.bot.send_photo(chat_id=query.message.chat_id, photo=item["file_id"], caption=cap, reply_markup=reply_markup)
                else:
                    await context.bot.send_document(chat_id=query.message.chat_id, document=item["file_id"], caption=cap, reply_markup=reply_markup)
            else:
                await context.bot.send_message(chat_id=query.message.chat_id, text=cap, reply_markup=reply_markup)
    
    keyboard = [[InlineKeyboardButton("🔙 عودة للمادة", callback_data=f"mat_{subject_key}")]]
    await query.message.reply_text("👇 للعودة:", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_receive_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == MY_ID:
        if update.message.document:
            context.user_data.update({"upload_file_id": update.message.document.file_id, "upload_file_name": update.message.document.file_name or "ملف", "upload_type": "doc"})
        elif update.message.photo:
            context.user_data.update({"upload_file_id": update.message.photo[-1].file_id, "upload_file_name": "صورة", "upload_type": "photo"})
        else: return
        keyboard = [[InlineKeyboardButton(f"📥 {item['name']}", callback_data=f"adm_set_sub_{key}")] for key, item in DATA.items()]
        await update.message.reply_text("📥 اختر المادة:", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == MY_ID:
        sub, cat = context.user_data.get("upload_sub"), context.user_data.get("upload_cat")
        if not sub or not cat: return
        text = update.message.text.strip()
        f_id = context.user_data.get("upload_file_id")
        if cat == "courses" and not f_id:
            DATA[sub]["courses"].append({"caption": text})
        elif f_id:
            cap = context.user_data["upload_file_name"] if text == "." else text
            DATA[sub][cat].append({"file_id": f_id, "caption": cap, "type": context.user_data["upload_type"]})
        else: return
        save_data(DATA)
        await update.message.reply_text("✅ تم الحفظ.")
        context.user_data.clear()

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, admin_receive_media))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_receive_text))
    app.run_polling()

if __name__ == '__main__':
    main()
```
