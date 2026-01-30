import os
import json
import random
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ====== الإعدادات ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = [5638954248, 7853380905]
CHANNEL_LINK = "https://t.me/yourchannel"
DATA_FILE = "users.json"
# ======================


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def random_gift():
    gifts = (
        ["🚗 سيارة + سرعة + Boost نهائي"] * 10 +
        ["💰 فلوس 100 مليون"] * 10 +
        ["🪙 ذهب 100 مليون"] * 10 +
        ["🗺️ فتح خرائط مجانًا"] * 10 +
        ["❌ حظ أوفر"] * 60
    )
    return random.choice(gifts)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    now = datetime.now()

    data = load_data()

    # أول مرة
    if user_id not in data:
        data[user_id] = {
            "used": False,
            "time": None
        }
        save_data(data)

        await update.message.reply_text(
            f"👋 أهلاً {user.first_name}\n\n"
            f"📢 اشترك في القناة أولاً:\n"
            f"{CHANNEL_LINK}\n\n"
            f"ثم اضغط /start مرة ثانية لاستلام هديتك 🎁"
        )
        return

    user_data = data[user_id]

    # إذا أخذ الهدية
    if user_data["used"]:
        last_time = datetime.fromisoformat(user_data["time"])
        if now - last_time < timedelta(hours=24):
            remaining = timedelta(hours=24) - (now - last_time)
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60

            await update.message.reply_text(
                f"⏳ لقد استلمت هديتك بالفعل\n"
                f"🔁 حاول بعد {hours} ساعة و {minutes} دقيقة"
            )
            return

    # إعطاء الهدية
    gift = random_gift()
    user_data["used"] = True
    user_data["time"] = now.isoformat()
    save_data(data)

    await update.message.reply_text(
        f"🎉 مبروك!\n\n"
        f"🎁 هديتك:\n{gift}"
    )

    # إشعار الأدمن
    for admin_id in ADMINS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=(
                    "📥 طلب هدية جديد\n\n"
                    f"👤 الاسم: {user.first_name}\n"
                    f"🔗 المعرف: @{user.username}\n"
                    f"🆔 ID: {user.id}\n"
                    f"🎁 الهدية: {gift}\n"
                    f"🕒 الوقت: {now.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            )
        except Exception as e:
            print(f"Admin send error: {e}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":

    main()

