import yt_dlp
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8432285867:AAFmaVLrp3XKfMoX8G88tFMCeE5za0SkCqI"
CHANNEL = "@Quote0me"

user_links = {}

# 🔹 زر الاشتراك
def join_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 اشترك بالقناة", url=f"https://t.me/{CHANNEL[1:]}")],
        [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check")]
    ])

# 🔹 التحقق من الاشتراك
async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# 🔹 start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 أهلاً بك\nارسل رابط الفيديو",
        reply_markup=join_buttons()
    )

# 🔹 زر تحقق
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if await check_subscription(user_id, context.bot):
        await query.message.reply_text("✅ تم التحقق، أرسل الرابط الآن")
    else:
        await query.message.reply_text("❌ لم تشترك بعد")

# 🔹 استقبال الرابط
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not await check_subscription(user_id, context.bot):
        await update.message.reply_text(
            "⚠️ يجب الاشتراك أولاً",
            reply_markup=join_buttons()
        )
        return

    url = update.message.text
    user_links[user_id] = url

    buttons = [
        [InlineKeyboardButton("📥 جودة عالية HD", callback_data="hd")],
        [InlineKeyboardButton("⚡ جودة عادية", callback_data="sd")]
    ]

    await update.message.reply_text(
        "اختر الجودة:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# 🔹 التحميل
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in user_links:
        await query.message.reply_text("❌ أرسل الرابط أولاً")
        return

    url = user_links[user_id]

    await query.message.reply_text("⏳ جاري التحميل...")

    try:
        quality = query.data

        if quality == "hd":
            format_code = "bestvideo+bestaudio/best"
        else:
            format_code = "best"

        ydl_opts = {
            'format': format_code,
            'merge_output_format': 'mp4',
            'outtmpl': f'video_{user_id}.%(ext)s',
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        filename = f"video_{user_id}.mp4"

        await query.message.reply_video(video=open(filename, "rb"))

        # 🧹 حذف الفيديو بعد الإرسال
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        print(e)
        await query.message.reply_text("❌ فشل التحميل")

# 🔹 تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button, pattern="check"))
app.add_handler(CallbackQueryHandler(download_video, pattern="hd|sd"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
