بالتأكيد، إليك الكود الكامل والمحدث لتتمكن من نسخه مباشرة. يتضمن الكود ميزات: إضافة نص توضيحي للملفات، قسم صور التكاليف، وقسم الكورسات التفاعلي.

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

# دالة تحميل البيانات
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
                for key in DEFAULT_DATA:
                    if key in current_data:
                        current_data[key]["name"] = DEFAULT_DATA[key]["name"]
                        if "costs" not in current_data[key]:
                            current_data[key]["costs"] = []
                        if not isinstance(current_data[key].get("courses"), list):
                            current_data[key]["courses"] = []
                return current_data
        except Exception:
            return DEFAULT_DATA
    return DEFAULT_DATA

# دالة حفظ البيانات
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

DATA = load_data()

# أمر /start للطلاب
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

# معالج تفاعل الطلاب والمشرف مع الأزرار
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global DATA
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("mat_"):
        subject_key = data.replace("mat_", "")
        keyboard = [
            [InlineKeyboardButton("📚 المحاضرات المرفوعة", callback_data=f"lec_{subject_key}")],
            [InlineKeyboardButton("📄 المستندات والملازم", callback_data=f"doc_{subject_key}")],
            [InlineKeyboardButton("🖼️ صور التكاليف", callback_data=f"cst_{subject_key}")],
            [InlineKeyboardButton("💻 الكورسات والروابط", callback_data=f"crs_{subject_key}")],
            [InlineKeyboardButton("🔙 العودة لقائمة المواد", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"📂 أنت الآن داخل مادة:\n({DATA[subject_key]['name']})\n\nالرجاء اختيار القسم المطلوب:", reply_markup=reply_markup)

    elif data.startswith("lec_") or data.startswith("doc_"):
        cat_map = {"lec_": "lectures", "doc_": "docs"}
        prefix = "lec_" if data.startswith("lec_") else "doc_"
        subject_key = data.replace(prefix, "")
        category = cat_map[prefix]
        
        items = DATA[subject_key][category]
        if not items:
            await query.message.reply_text(f"📭 لا توجد ملفات حالياً لمادة ({DATA[subject_key]['name']}).")
        else:
            await query.message.reply_text(f"⏳ جاري إرسال الملفات...")
            for item in items:
                caption = item.get("caption") or item["title"]
                await context.bot.send_document(chat_id=query.message.chat_id, document=item["file_id"], caption=caption)
        await show_back_button(query, subject_key)

    elif data.startswith("cst_"):
        subject_key = data.replace("cst_", "")
        costs = DATA[subject_key].get("costs", [])
        if not costs:
            await query.message.reply_text(f"📭 لا توجد صور تكاليف حالياً لمادة ({DATA[subject_key]['name']}).")
        else:
            await query.message.reply_text(f"⏳ جاري إرسال صور التكاليف...")
            for cost in costs:
                caption = cost.get("caption") or "صورة تكليف"
                await context.bot.send_photo(chat_id=query.message.chat_id, photo=cost["file_id"], caption=caption)
        await show_back_button(query, subject_key)

    elif data.startswith("crs_"):
        subject_key = data.replace("crs_", "")
        courses = DATA[subject_key].get("courses", [])
        if not courses:
            await query.message.reply_text(f"📭 لا توجد كورسات أو روابط مضافة حالياً لمادة ({DATA[subject_key]['name']}).")
        else:
            await query.message.reply_text(f"⏳ جاري عرض الكورسات والروابط لمادة ({DATA[subject_key]['name']})...")
            text_links = ""
            for idx, crs in enumerate(courses, 1):
                if "file_id" in crs:
                    await context.bot.send_document(chat_id=query.message.chat_id, document=crs["file_id"], caption=crs["caption"])
                else:
                    text_links += f"{idx}- {crs['caption']}\n"
            if text_links:
                await query.message.reply_text(text_links)
        await show_back_button(query, subject_key)

    elif data == "back_to_main":
        keyboard = [[InlineKeyboardButton(item["name"], callback_data=f"mat_{key}")] for key, item in DATA.items()]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("✨ القائمة الرئيسية:\nالرجاء اختيار المادة الدراسية:", reply_markup=reply_markup)

    # --- لوحة تحكم المشرف ---
    elif data.startswith("adm_set_sub_"):
        sub = data.replace("adm_set_sub_", "")
        context.user_data["upload_sub"] = sub
        keyboard = [
            [InlineKeyboardButton("📚 قسم المحاضرات", callback_data="adm_set_cat_lectures")],
            [InlineKeyboardButton("📄 قسم المستندات والملازم", callback_data="adm_set_cat_docs")],
            [InlineKeyboardButton("🖼️ قسم صور التكاليف", callback_data="adm_set_cat_costs")],
            [InlineKeyboardButton("💻 قسم الكورسات والروابط", callback_data="adm_set_cat_courses")]
        ]
        await query.edit_message_text("⚙️ ممتاز، اختر القسم الذي تريد الإضافة إليه:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("adm_set_cat_"):
        cat = data.replace("adm_set_cat_", "")
        context.user_data["upload_cat"] = cat
        if cat == "courses" and "upload_file_id" not in context.user_data:
            await query.edit_message_text("✍️ أرسل الآن رابط الكورس أو النص الذي تريد إضافته:")
        else:
            await query.edit_message_text("✍️ أرسل الآن النص التوضيحي (Caption) الذي سيظهر للمستخدمين (أرسل . للاكتفاء باسم الملف):")

async def show_back_button(query, subject_key):
    keyboard = [[InlineKeyboardButton("🔙 عودة للمادة", callback_data=f"mat_{subject_key}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("👇 للعودة إلى خيارات المادة:", reply_markup=reply_markup)

async def admin_receive_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == MY_ID:
        if update.message.document:
            media = update.message.document
            context.user_data["upload_file_id"] = media.file_id
            context.user_data["upload_file_name"] = media.file_name or "ملف"
        elif update.message.photo:
            media = update.message.photo[-1]
            context.user_data["upload_file_id"] = media.file_id
            context.user_data["upload_file_name"] = "صورة"
        else: return
        keyboard = [[InlineKeyboardButton(f"📥 إضافة إلى: {item['name']}", callback_data=f"adm_set_sub_{key}")] for key, item in DATA.items()]
        await update.message.reply_text("📥 تم استلام الوسائط. اختر المادة:", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == MY_ID:
        sub = context.user_data.get("upload_sub")
        cat = context.user_data.get("upload_cat")
        if sub and cat == "courses" and "upload_file_id" not in context.user_data:
            text = update.message.text.strip()
            DATA[sub]["courses"].append({"caption": text})
            save_data(DATA)
            await update.message.reply_text(f"✅ تم الإضافة لقسم الكورسات بنجاح.")
            context.user_data.clear()
            return
        f_id = context.user_data.get("upload_file_id")
        if sub and cat and f_id:
            caption_text = update.message.text.strip()
            if caption_text == ".": caption_text = context.user_data.get("upload_file_name", "ملف")
            DATA[sub][cat].append({"title": context.user_data.get("upload_file_name"), "file_id": f_id, "caption": caption_text})
            save_data(DATA)
            await update.message.reply_text(f"✅ تم الحفظ بنجاح في قسم {cat}.")
            context.user_data.clear()

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, admin_receive_media))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_receive_text))
    print(f"[{BOT_BRAND_NAME}] Running...")
    app.run_polling()

if __name__ == '__main__':
    main()
```
