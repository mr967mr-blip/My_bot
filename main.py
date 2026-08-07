import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# تفعيل تسجيل الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- الإعدادات المحمية ---
TOKEN = '8230814965:AAGdR9KvXi3QtMY4G_bALzVbvcBQqwZcvgk' 
MY_ID = 5848768601 
DATA_FILE = 'clients_data.json'
BOT_BRAND_NAME = "بوت المندوب" 

# الهيكل الأساسي للمواد الدراسية
DEFAULT_DATA = {
    "c_sharp": {"name": "💻 C# - سي شارب", "lectures": [], "courses": "🔗 كورس السي شارب الشامل لاحقاً", "docs": [], "assignments": []},
    "os": {"name": "⚙️ Operating System - نظم التشغيل", "lectures": [], "courses": "🔗 شرح مادة نظم التشغيل لاحقاً", "docs": [], "assignments": []},
    "tech_writing": {"name": "📝 Technical Writing 1 - الكتابة التقنية 1", "lectures": [], "courses": "🔗 كورس الكتابة التقنية لاحقاً", "docs": [], "assignments": []},
    "dbms": {"name": "🗄️ Database Management Systems - نظم إدارة قواعد البيانات", "lectures": [], "courses": "🔗 كورس قواعد البيانات لاحقاً", "docs": [], "assignments": []},
    "computer_math": {"name": "📐 Computer Math - رياضيات الحاسوب", "lectures": [], "courses": "🔗 فيديوهات رياضيات الحاسوب", "docs": [], "assignments": []},
    "internet_intro": {"name": "🌐 Introduction to Internet - مقدمة في الإنترنت", "lectures": [], "courses": "🔗 كورس شبكة الإنترنت", "docs": [], "assignments": []},
    "conflict": {"name": "🇵🇸 Arabic Israeli Conflict - الصراع العربي الإسرائيلي", "lectures": [], "courses": "🔗 وثائقيات القضية", "docs": [], "assignments": []},
    "hardware": {"name": "🔧 PC Hardware and Maintenance - صيانة عتاد الحاسوب", "lectures": [], "courses": "🔗 كورس صيانة الكمبيوتر", "docs": [], "assignments": []}
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
                for key in DEFAULT_DATA:
                    if key in current_data:
                        current_data[key]["name"] = DEFAULT_DATA[key]["name"]
                        if "assignments" not in current_data[key]:
                            current_data[key]["assignments"] = []
                return current_data
        except Exception:
            return DEFAULT_DATA
    return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

DATA = load_data()

# استقبال الطلاب عند كتابة أمر البدء /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton(item["name"], callback_data=f"mat_{key}")] for key, item in DATA.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    first_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"✨ مرحباً بك يا {first_name} في **{BOT_BRAND_NAME}** التعليمي.\n\n"
        f"الرجاء اختيار المادة الدراسية لتصفح محتواها السابق 👇:", 
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# معالج ضغط الأزرار بالكامل للطلاب ولوحة تحكم المندوب
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global DATA
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("mat_"):
        subject_key = data.replace("mat_", "")
        keyboard = [
            [InlineKeyboardButton("📚 المحاضرات المرفوعة", callback_data=f"lec_{subject_key}")],
            [InlineKeyboardButton("📄 المستندات والملازم", callback_data=f"doc_{subject_key}")],
            [InlineKeyboardButton("📝 التكاليف والواجبات", callback_data=f"asg_{subject_key}")],
            [InlineKeyboardButton("💻 الكورسات والروابط", callback_data=f"crs_{subject_key}")],
            [InlineKeyboardButton("🔙 العودة لقائمة المواد", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"📂 مادة: ({DATA[subject_key]['name']})\n\nالرجاء اختيار القسم المطلوب:", reply_markup=reply_markup)

    elif data.startswith("lec_"):
        subject_key = data.replace("lec_", "")
        await send_section_content(query, context, subject_key, "lectures", "محاضرات", user_id)

    elif data.startswith("doc_"):
        subject_key = data.replace("doc_", "")
        await send_section_content(query, context, subject_key, "docs", "ملازم ومستندات", user_id)

    elif data.startswith("asg_"):
        subject_key = data.replace("asg_", "")
        await send_section_content(query, context, subject_key, "assignments", "تكاليف وواجبات", user_id)

    elif data.startswith("crs_"):
        subject_key = data.replace("crs_", "")
        keyboard = [[InlineKeyboardButton("🔙 عودة للمادة", callback_data=f"mat_{subject_key}")]]
        await query.edit_message_text(text=DATA[subject_key]["courses"], reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "back_to_main":
        keyboard = [[InlineKeyboardButton(item["name"], callback_data=f"mat_{key}")] for key, item in DATA.items()]
        await query.edit_message_text("✨ القائمة الرئيسية:\nالرجاء اختيار المادة الدراسية:", reply_markup=InlineKeyboardMarkup(keyboard))

    # --- لوحة التحكم الخاصة بالمندوب فقط ---
    elif data.startswith("adm_set_sub_"):
        context.user_data["upload_sub"] = data.replace("adm_set_sub_", "")
        keyboard = [
            [InlineKeyboardButton("📚 قسم المحاضرات", callback_data="adm_set_cat_lectures")],
            [InlineKeyboardButton("📄 قسم المستندات والملازم", callback_data="adm_set_cat_docs")],
            [InlineKeyboardButton("📝 قسم التكاليف والواجبات", callback_data="adm_set_cat_assignments")]
        ]
        await query.edit_message_text("⚙️ ممتاز، الآن اختر القسم الذي تود تصنيف هذا المحتوى داخله:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("adm_set_cat_"):
        cat = data.replace("adm_set_cat_", "")
        sub = context.user_data.get("upload_sub")
        item_type = context.user_data.get("upload_type")
        content = context.user_data.get("upload_content")
        caption = context.user_data.get("upload_caption", "")

        if sub and content:
            DATA[sub][cat].append({"type": item_type, "content": content, "caption": caption})
            save_data(DATA)
            await query.edit_message_text(f"✅ تم بنجاح إضافة وتثبيت التحديث الدراسي!\n📂 في مادة: {DATA[sub]['name']}\n🗂️ القسم: {cat}")
            context.user_data.clear()

    # --- ميزة حذف أي عنصر بالخطأ (للمندوب فقط) ---
    elif data.startswith("del_"):
        if user_id == MY_ID:
            parts = data.split("_")
            if len(parts) >= 4:
                index = int(parts[-1])
                category = parts[-2]
                subject_key = "_".join(parts[1:-2])
                
                if subject_key in DATA and category in DATA[subject_key]:
                    try:
                        DATA[subject_key][category].pop(index)
                        save_data(DATA)
                        await query.message.reply_text(f"🗑️ تم حذف العنصر بنجاح من قسم {category} لمادة ({DATA[subject_key]['name']}).")
                        await query.message.delete()
                    except IndexError:
                        await query.message.reply_text("❌ عذراً، لم يتم العثور على العنصر المراد حذفه.")
        else:
            await query.answer("❌ عذراً، لا تمتلك صلاحية مسح الملفات.", show_alert=True)

# دالة عرض المحتوى للطلاب مع زر الحذف الذكي للمندوب (تم تعديل السطر 144 هنا ليصبح صحيحاً)
async def send_section_content(query, context, subject_key, category, category_title, user_id):
    items = DATA[subject_key][category]
    if not items:
        await query.message.reply_text(f"📭 لا توجد عناصر مرفوعة حالياً في قسم {category_title} لمادة ({DATA[subject_key]['name']}).")
    else:
        await query.message.reply_text(f"⏳ جاري جلب محتويات قسم {category_title}...")
        for index, item in enumerate(items):
            t = item.get("type", "doc")
            
            reply_markup = None
            if user_id == MY_ID:
                keyboard = [[InlineKeyboardButton("🗑️ حذف هذا العنصر", callback_data=f"del_{subject_key}_{category}_{index}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)

            if t == "text":
                await context.bot.send_message(chat_id=query.message.chat_id, text=item["content"], reply_markup=reply_markup)
            elif t == "photo":
                await context.bot.send_photo(chat_id=query.message.chat_id, photo=item["content"], caption=item.get("caption", ""), reply_markup=reply_markup)
            else:
                await context.bot.send_document(chat_id=query.message.chat_id, document=item["content"], caption=item.get("caption", ""), reply_markup=reply_markup)
    
    keyboard = [[InlineKeyboardButton("🔙 عودة للمادة", callback_data=f"mat_{subject_key}")]]
    await query.message.reply_text("👇 للعودة إلى خيارات المادة السابقة:", reply_markup=InlineKeyboardMarkup(keyboard))

# دالة استقبال محتويات المندوب وتصنيفها آلياً
async def admin_receive_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != MY_ID:
        return 

    if update.message.text:
        context.user_data["upload_type"] = "text"
        context.user_data["upload_content"] = update.message.text
        context.user_data["upload_caption"] = ""
        prompt_text = f"📥 تم استلام النص بنجاح:\n`{update.message.text[:50]}...`"

    elif update.message.photo:
        context.user_data["upload_type"] = "photo"
        context.user_data["upload_content"] = update.message.photo[-1].file_id
        context.user_data["upload_caption"] = update.message.caption if update.message.caption else ""
