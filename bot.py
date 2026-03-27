from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

TOKEN = "8432285867:AAFmaVLrp3XKfMoX8G88tFMCeE5za0SkCqI"
CHANNEL = "@Quote0me"

# زر التحقق
def join_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 اشترك بالقناة", url=f"https://t.me/{CHANNEL[1:]}")],
        [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 أهلاً بك في بوت تحميل الفيديو\n\n📥 أرسل رابط أي فيديو وأنا أحمله لك فوراً 😎",
        reply_markup=join_buttons()
    )

async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if await check_subscription(user_id, context.bot):
        await query.answer("✅ تم التحقق! أرسل الرابط الآن")
        await query.edit_message_text("🎉 أنت مشترك! أرسل الرابط لتحميل الفيديو")
    else:
        await query.answer("❌ لم تشترك بعد")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not await check_subscription(user_id, context.bot):
        await update.message.reply_text(
            "⚠️ يجب الاشتراك أولاً",
            reply_markup=join_buttons()
        )
        return

    url = update.message.text
    await update.message.reply_text("⏳ جاري التحميل...")

    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': 'video.%(ext)s',
    }

   with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

        await update.message.reply_video(video=open("video.mp4", "rb"))

except:
        await update.message.reply_text("❌ الرابط غير صالح")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
