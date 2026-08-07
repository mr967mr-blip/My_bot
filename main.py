لقد راجعت الكود وتأكدت من سلامته برمجياً. إليك الأسباب الشائعة لعدم عمل البوت وكيفية حلها:

1.  **تحديث المكتبة**: الكود يستخدم الإصدار الجديد من مكتبة `python-telegram-bot`. تأكد من تحديثها في جهازك عبر هذا الأمر:
    ```bash
    pip install python-telegram-bot --upgrade
    ```
2.  **ملف البيانات القديم**: إذا كان لديك ملف `clients_data.json` قديم، قد يحدث تعارض بسبب تغيير هيكل قسم "الكورسات" من نص إلى قائمة. يفضل حذف ملف `clients_data.json` القديم أو تعديله ليتوافق مع الهيكل الجديد (الكود سيقوم بإنشاء ملف جديد تلقائياً إذا لم يجد القديم).
3.  **التوكن (TOKEN)**: تأكد من أن التوكن الموجود في الكود صحيح ولم يتغير.
4.  **بيئة التشغيل**: تأكد من أنك قمت بنسخ الكود كاملاً دون نقصان.

سأقوم الآن بإعادة إرسال الكود في قالب واحد نظيف ومرتب لتتأكد من نسخه بشكل صحيح:

```python
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# --- الإعدادات ---
TOKEN = '8230814965:AAGdR9KvXi3QtMY4G_bALzVbvcBQqwZcvgk' 
MY_ID = 5848768601 
DATA_FILE = 'clients_data.json'
BOT_BRAND_NAME = "بوت المندوب" 

# الهيكل الأساسي للمواد
DEFAULT_DATA = {
    "c_sharp": {"name": "💻 C# - سي شارب", "lectures": [], "courses": [], "docs": [], "costs": []},
    "os": {"name": "⚙️ Operating System - نظم التشغيل", "lectures": [], "courses": [], "docs": [], "costs": []},
    "tech_writing": {"name": "📝 Technical Writing 1 - الكتابة التقنية 1", "lectures": [], "courses": [], "docs": [], "costs": []},
    "dbms": {"name": "🗄️ Database Management Systems - نظم إدارة قواعد البيانات", "lectures": [], "courses": [], "docs": [], "costs": []},
    "computer_math": {"name": "📐 Computer Math - رياضيات الحاسوب", "lectures": [], "courses": [], "docs": [], "costs": []},
    "internet_intro": {"name": "🌐 Introduction to Internet - مقدمة في الإنترنت", "lectures": [], "courses": [], "docs": [], "costs": []},
    "conflict": {"name": "🇵🇸 Arabic Israeli Conflict - الصراع العربي الإسرائيلي", "lectures": [], "courses": [], "docs": [], "costs": []},
    "hardware": {"name": "🔧 PC Hardware and Maintenance - صيانة عتاد الحاسوب", "lectures": [], "courses": [], "docs": [], "costs": []}
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
                for key in DEFAULT_DATA:
                    if key in current_data:
                        current_data[key]["name"] = DEFAULT_DATA[key]["name"]
                        if "costs" not in current_data[key]: current_data[key]["costs"] = []
                        if not isinstance(current_data[key].get("courses"), list): current_data[key]["courses"] = []
                return current_data
        except: return DEFAULT_DATA
    return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

DATA = load_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton(item["name"], callback_data=f"mat_{key}")] for key, item in DATA.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"✨ مرحباً بك في **{BOT_BRAND_NAME}**.\nالرجاء اختيار المادة الدراسية:", reply_markup=reply_markup, parse_mode="Markdown")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global DATA
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("mat_"):
        subject_key = data.replace("mat_", "")
        keyboard = [
            [InlineKeyboardButton("📚 المحاضرات", callback_data=f"lec_{subject_key}"), InlineKeyboardButton("📄 الملازم", callback_data=f"doc_{subject_key}")],
            [InlineKeyboardButton("🖼️ صور التكاليف", callback_data=f"cst_{subject_key}"), InlineKeyboardButton("💻 الكورسات", callback_data=f"crs_{subject_key}")],
            [InlineKeyboardButton("🔙 العودة للقائمة", callback_data="back_to_main")]
        ]
        await query.edit_message_text(text=f"📂 مادة: {DATA[subject_key]['name']}", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("lec_") or data.startswith("doc_"):
        cat = "lectures" if data.startswith("lec_") else "docs"
        sub = data.replace("lec_", "").replace("doc_", "")
        items = DATA[sub][cat]
        if not items: await query.message.reply_text("📭 القسم فارغ حالياً.")
        else:
            for item in items: await context.bot.send_document(chat_id=query.message.chat_id, document=item["file_id"], caption=item.get("caption", item["title"]))
        await show_back_button(query, sub)

    elif data.startswith("cst_"):
        sub = data.replace("cst_", "")
        costs = DATA[sub].get("costs", [])
        if not costs: await query.message.reply_text("📭 لا توجد صور تكاليف.")
        else:
            for cost in costs: await context.bot.send_photo(chat_id=query.message.chat_id, photo=cost["file_id"], caption=cost.get("caption", "صورة"))
        await show_back_button(query, sub)

    elif data.startswith("crs_"):
        sub = data.replace("crs_", "")
        courses = DATA[sub].get("courses", [])
        if not courses: await query.message.reply_text("📭 لا توجد كورسات.")
        else:
            links = ""
            for idx, crs in enumerate(courses, 1):
                if "file_id" in crs: await context.bot.send_document(chat_id=query.message.chat_id, document=crs["file_id"], caption=crs["caption"])
                else: links += f"{idx}- {crs['caption']}\n"
            if links: await query.message.reply_text(links)
        await show_back_button(query, sub)

    elif data == "back_to_main":
        keyboard = [[InlineKeyboardButton(item["name"], callback_data=f"mat_{key}")] for key, item in DATA.items()]
        await query.edit_message_text("✨ القائمة الرئيسية:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("adm_set_sub_"):
        context.user_data["upload_sub"] = data.replace("adm_set_sub_", "")
        keyboard = [[InlineKeyboardButton("📚 محاضرات", callback_data="adm_set_cat_lectures"), InlineKeyboardButton("📄 ملازم", callback_data="adm_set_cat_docs")],
                    [InlineKeyboardButton("🖼️ تكاليف", callback_data="adm_set_cat_costs"), InlineKeyboardButton("💻 كورسات", callback_data="adm_set_cat_courses")]]
        await query.edit_message_text("⚙️ اختر القسم:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("adm_set_cat_"):
        context.user_data["upload_cat"] = data.replace("adm_set_cat_", "")
        await query.edit_message_text("✍️ أرسل الوصف (Caption) أو الرابط (للملفات أرسل . للاكتفاء بالاسم):")

async def show_back_button(query, subject_key):
    keyboard = [[InlineKeyboardButton("🔙 عودة", callback_data=f"mat_{subject_key}")]]
    await query.message.reply_text("👇 للعودة:", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_receive_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == MY_ID:
        if update.message.document:
            context.user_data.update({"upload_file_id": update.message.document.file_id, "upload_file_name": update.message.document.file_name or "ملف"})
        elif update.message.photo:
            context.user_data.update({"upload_file_id": update.message.photo[-1].file_id, "upload_file_name": "صورة"})
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
            DATA[sub][cat].append({"title": context.user_data["upload_file_name"], "file_id": f_id, "caption": cap})
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

إذا استمرت المشكلة، يرجى إخباري بأي رسالة خطأ تظهر لك في شاشة التشغيل (Terminal).
