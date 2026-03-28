from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp
import os

TOKEN = "8432285867:AAFmaVLrp3XKfMoX8G88tFMCeE5za0SkCqI"
CHANNEL = "@Quote0me"

user_links = {}

def join_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 اشترك بالقناة", url=f"https://t.me/{CHANNEL[1:]}")],
        [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 أهلاً بك\n\nارسل رابط الفيديو",
        reply_markup=join_buttons()
    )

async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not await check_subscription(user_id, context.bot):
        await update.message.reply_text("اشترك أولاً", reply_markup=join_buttons())
        return

    url = update.message.text
    user_links[user_id] = url

    buttons = [
        [InlineKeyboardButton("📥 جودة عالية HD", callback_data="hd")],
        [InlineKeyboardButton("⚡ جودة عادية", callback_data="sd")]
    ]

    await update.message.reply_text("اختر الجودة:", reply_markup=InlineKeyboardMarkup(buttons))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    url = user_links.get(user_id)

    await query.answer("⏳ جاري التحميل...")

    if query.data == "hd":
        format_type = 'best'
    else:
        format_type = 'worst'

    try:
        ydl_opts = {
            'format': format_type,
            'outtmpl': '%(id)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await context.bot.send_video(chat_id=user_id, video=open(filename, 'rb'))

        os.remove(filename)

    except:
        await context.bot.send_message(chat_id=user_id, text="❌ فشل التحميل")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
