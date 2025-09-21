""" hey future me if you're reading this, i hope ur drinking lucozade, smiling and remembering how hard it was to make this work. you did it you beautiful, stubborn, brilliant babe. now go spread love darling"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    CallbackQueryHandler,
)
from telegram.request import HTTPXRequest
from telegram.error import TimedOut, NetworkError
import asyncio
import random
import os
import json
import warnings

# shhh, no scary warnings we got this
warnings.filterwarnings("ignore", category=UserWarning, module="telegram.ext._conversationhandler")

# your bot's secret key keep it safe, like your favorite coffee mug
# BOT_TOKEN = 'key here'

# we read it from a file so we don't accidentally share it up to github hehe
try:
    with open('key.txt', 'r') as f:
        BOT_TOKEN = f.read().strip() 
    print("🔑 Bot token loaded from key.txt")
except FileNotFoundError:
    print("❌ ERROR: key.txt not found! Create it with your bot token.")
    exit(1)

# where we keep all our love notes (user data hehe)
USERS_FILE = 'users.json'

# load our little love circle if it exists
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}  # if file breaks, we start fresh no biggie

# save our love circle so no one gets forgotten
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# everyone we are sending love to loaded from file
users = load_users()

# what we're waiting for from each user
ASKING_NAME, ASKING_INTERVAL, UPDATING_INTERVAL = 1, 2, 3

# our love notes fill in the {name} with their actual name
message_templates = [
    "i love uuuuuuuuuu",
    "am soooooo proud of you ✨🥺",
    "am rlyyyy proud of you my {name}",
    "you're doing amazing, sweetie! 💋",
    "just a reminder: u r awesome 😊",
    "sending you a big hug today! 🤗",
    "you've got this! i believe in you 💪",
    "thinking of you and all the great things you do ❤️",
    "you are capable of anything you set your mind to ✨",
    "remember to be kind to yourself today 💋",
    "here's a hug to start your day off right 🤗",
    "you are so loved {name} ❤️",
    "you light up my life ✨",
    "have a wonderful day, sweetie! 💋",
    "💋",
    "sending all my love 🤗",
    "so glad you're in my life ❤️",
    "i love you moooooooorrreeeeeeee! 🥰",
    "am so lucky to have you in my life ❤️",
    "am with you, honey 🤗",
    "just a reminder that you are loved beyond words ✨",
    "thinking of you and sending all my love to u 💋",
    "your my special person {name} ❤️",
    "your my favorite person in the universe 🥰",
    "i c u, smile my pretty 👀",
    "you make my life so much better ❤️",
    "you got a heart of gold ✨",
    "your soooo awesome am jealous 🤤",
    "sending you a virtual hug now 🫂",
    "🫂",
    "{name} yes ur fabulous 🫂",
    "superstar 🚀",
]

# when u say love you i wil sooo hit u with extra love!
love_u_more = [
    "love u more 💖",
    "love u tooooo",
    "love u ♾️",
    "noooo, i love YOU more! 😘",
]

# send love, even if the internet is being moody
async def safe_send_message(bot, chat_id, text, reply_markup=None, parse_mode=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            return True
        except (TimedOut, NetworkError) as e:
            print(f"⚠️ internet being dramatic for {chat_id} (try {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # wait 1s, then 2s, then 4s
                print(f"⏳ giving it {wait_time} seconds to chill...")
                await asyncio.sleep(wait_time)
        except Exception as e:
            print(f"❌ oopsie for {chat_id}: {e}")
            break
    return False

# set up a love schedule for one person
def schedule_user_job(application, chat_id, hours):
    async def job_callback(context: ContextTypes.DEFAULT_TYPE):
        user_data = users.get(chat_id, {})
        if not user_data.get("subscribed", False) or not user_data.get("name"):
            return

        name = user_data["name"]
        message = random.choice(message_templates).format(name=name)
        
        # send it with retries because love never gives up
        success = await safe_send_message(context.bot, chat_id, message)
        if success:
            print(f"sent to {name} ({chat_id}): {message}")
        else:
            print(f"💀 gave up after 3 tries for {name} internet wins this round")

    # clear old schedule if exists
    job_name = f"love_{chat_id}"
    for job in application.job_queue.get_jobs_by_name(job_name):
        job.schedule_removal()

    # set up new schedule
    application.job_queue.run_repeating(
        job_callback,
        interval=hours * 3600, # convert hours to seconds
        first=60, # first love note in 60 seconds
        name=job_name
    )
    print(f"⏰ love scheduled for {chat_id} every {hours} hours")

# when someone says /start welcome them home
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user = users.get(chat_id, {})

    if user.get("name"):
        await safe_send_message(
            context.bot,
            chat_id,
            f"👋 welcome back, {user['name']}! you're still on my love list 💕"
        )
        return ConversationHandler.END
    else:
        await safe_send_message(
            context.bot,
            chat_id,
            "💖 hiiiii! i'm your personal love bot! what should i call you? (just type it!)"
        )
        return ASKING_NAME

# they told us their name save it like a precious memory
async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    name = update.message.text.strip()

    # save their name and subscribe them
    if chat_id not in users:
        users[chat_id] = {}
    users[chat_id]["name"] = name
    users[chat_id]["subscribed"] = True
    save_users(users)

    # show beautiful frequency buttons right away!
    keyboard = [
        [
            InlineKeyboardButton("💖 1h", callback_data="freq_1"),
            InlineKeyboardButton("🤗 4h", callback_data="freq_4"),
            InlineKeyboardButton("✨ 7h", callback_data="freq_7"),
        ],
        [
            InlineKeyboardButton("🌙 12h", callback_data="freq_12"),
            InlineKeyboardButton("☀️ 24h", callback_data="freq_24"),
            InlineKeyboardButton("🛌 48h", callback_data="freq_48"),
        ],
        [
            InlineKeyboardButton("🎉 168h", callback_data="freq_168"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_send_message(
        context.bot,
        chat_id,
        f"💌 thank you, {name}! how often should i remind you you're awesome?\n"
        "tap your perfect rhythm below:",
        reply_markup=reply_markup
    )
    return ConversationHandler.END  

# when they want to leave our love circle broooo ouch
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if chat_id in users:
        users[chat_id]["subscribed"] = False
        save_users(users)
        name = users[chat_id].get("name", "friend")
        await safe_send_message(
            context.bot,
            chat_id,
            f"💔 goodbye, {name}. i'll miss you! 😢"
        )
    else:
        await safe_send_message(
            context.bot,
            chat_id,
            "you're not in my love circle yet. 😊"
        )

# show them their settings with pretty buttons!
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    user_data = users.get(chat_id, {})

    if not user_data.get("name"):
        await safe_send_message(
            context.bot,
            chat_id,
            "you're not in my love circle yet. say /start first! 💖"
        )
        return ConversationHandler.END

    name = user_data.get("name", "friend")
    interval = user_data.get("interval_hours", 24)

    # make some cute buttons
    keyboard = [
        [
            InlineKeyboardButton("✏️ change name", callback_data="change_name"),
            InlineKeyboardButton("⏰ change frequency", callback_data="change_frequency"),
        ],
        [
            InlineKeyboardButton("💌 send love now", callback_data="send_now"),
            InlineKeyboardButton("❓ /help", callback_data="help_help"),
        ],
        [
            InlineKeyboardButton("❌ cancel", callback_data="cancel"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await safe_send_message(
        context.bot,
        chat_id,
        f"⚙️ *your love settings*\n\n"
        f"✨ *name:* {name}\n\n"
        f"⏰ *frequency:* every {interval} hour(s)\n\n"
        f"tap a button below to update:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# someone wants to change their name let them!
async def update_name_globally(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    
    # only if we are waiting for a name
    if context.user_data.get("awaiting_name"):
        new_name = update.message.text.strip()
        print(f"🔍 new name: '{new_name}'")

        # save it like a treasured memory
        if chat_id not in users:
            users[chat_id] = {}
        users[chat_id]["name"] = new_name
        save_users(users)
        print(f"🔍 updated: {users[chat_id]}")

        # tell them it worked
        await safe_send_message(
            context.bot,
            chat_id,
            f"your name is now: {new_name} 💖"
        )

        # we're done waiting
        context.user_data["awaiting_name"] = False
    else:
        return 

# if they say "love you" — we drown them in extra love!
async def love_u_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()  # make it case-insensitive
    words = text.split()  # split into words for "u" check

    # check for "love" or "luv"
    has_love_word = "love" in text or "luv" in text

    # check for "you" OR standalone "u"
    has_you_word = "you" in text or "u" in words  # ← "u" must be whole word

    if has_love_word and has_you_word:
        await asyncio.sleep(1)  # tiny pause for realism
        response = random.choice(love_u_more)
        await safe_send_message(
            context.bot,
            update.effective_chat.id,
            response
        )
        print(f"💌 Love response sent: {response}") # print to console
        print(f"🔍 DEBUG: Received text: '{text}'")
        print(f"🔍 DEBUG: has_love_word: {has_love_word}, has_you_word: {has_you_word}")

# show them how to talk to us
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # create beautiful buttons for each command
    keyboard = [
        [
            InlineKeyboardButton("💖 /start", callback_data="help_start"),
            InlineKeyboardButton("⚙️ /settings", callback_data="help_settings"),
        ],
        [
            InlineKeyboardButton("💔 /stop", callback_data="help_stop"),
            InlineKeyboardButton("❓ /help", callback_data="help_help"),
        ],
        [
            InlineKeyboardButton("💌 Back to Love", callback_data="help_back"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await safe_send_message(
        context.bot,
        chat_id,
        "💌 *how to talk to your love bot*\n"
        "tap any button below to learn what it does!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# handle all the button presses our love concierge
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = str(query.message.chat_id)
    data = query.data

    if data == "change_name":
        await query.edit_message_text("💌 what's your new name? (just type it!)")
        context.user_data["awaiting_name"] = True
        return ConversationHandler.END

    elif data == "change_frequency":
        keyboard = [
            [
                InlineKeyboardButton("1h", callback_data="freq_1"),
                InlineKeyboardButton("4h", callback_data="freq_4"),
                InlineKeyboardButton("7h", callback_data="freq_7"),
            ],
            [
                InlineKeyboardButton("12h", callback_data="freq_12"),
                InlineKeyboardButton("24h", callback_data="freq_24"),
                InlineKeyboardButton("48h", callback_data="freq_48"),
            ],
            [
                InlineKeyboardButton("168h", callback_data="freq_168"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("💌 how often should i send love?", reply_markup=reply_markup)
        return UPDATING_INTERVAL

    elif data == "cancel":
        await query.edit_message_text("settings unchanged. love you! 💖")
        return ConversationHandler.END

    elif data.startswith("freq_"):
        hours = int(data.split("_")[1])
        users[chat_id]["interval_hours"] = hours
        save_users(users)
        schedule_user_job(context.application, chat_id, hours)
        await query.edit_message_text(f"love frequency updated! you'll get messages every {hours} hour(s). 💖")
        return ConversationHandler.END

    elif data == "send_now":
        user_data = users.get(chat_id, {})
        if user_data.get("subscribed") and user_data.get("name"):
            name = user_data["name"]
            message = random.choice(message_templates).format(name=name)
            await safe_send_message(context.bot, chat_id, message)
            await query.edit_message_text("💌 sent! check your messages! 💖")
        else:
            await query.edit_message_text("❌ you're not in my love circle yet. say /start first! 💖")
        return ConversationHandler.END

    elif data == "help_start":
        await query.edit_message_text(
            "💖 */start* join our love circle!\n"
            "I'll ask for your name and how often you want love messages.\n"
            "You only need to do this once! 💕",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💌 Back to Help", callback_data="help_back_to_menu")
            ]])
        )

    elif data == "help_settings":
        await query.edit_message_text(
            "⚙️ */settings* - customize your love!\n"
            "Change your name, how often you get messages, or send yourself love right now!\n"
            "Tap buttons to make changes — no typing needed! ✨",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💌 Back to Help", callback_data="help_back_to_menu")
            ]])
        )

    elif data == "help_stop":
        await query.edit_message_text(
            "💔 */stop* - leave our love circle\n"
            "I'll stop sending you messages (but I'll miss you! 😢)\n"
            "You can always come back with /start!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💌 Back to Help", callback_data="help_back_to_menu")
            ]])
        )

    elif data == "help_help":
        await query.edit_message_text(
            "❓ */help* - show this menu!\n"
            "Tap buttons to learn about each command.\n"
            "I'm here to help you feel loved! 🤗",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💌 Back to Help", callback_data="help_back_to_menu")
            ]])
        )

    elif data == "help_back" or data == "help_back_to_menu":
        keyboard = [
            [
                InlineKeyboardButton("💖 /start", callback_data="help_start"),
                InlineKeyboardButton("⚙️ /settings", callback_data="help_settings"),
            ],
            [
                InlineKeyboardButton("💔 /stop", callback_data="help_stop"),
                InlineKeyboardButton("❓ /help", callback_data="help_help"),
            ],
            [
                InlineKeyboardButton("💌 Close", callback_data="help_close"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "💌 *how to talk to your love bot*\n"
            "tap any button below to learn what it does!",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif data == "help_close":
        await query.edit_message_text("💌 Help menu closed. I'm always here when you need me! 💖")


# the heart of our love machine
async def main():
    print("🔍 starting our love engine...")
    
    # make our internet requests patient and kind
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=30,
        read_timeout=30,
        write_timeout=30,
        pool_timeout=30
    )
    print("🔍 internet settings ready")

    # build our love bot
    application = Application.builder().token(BOT_TOKEN).request(request).build()
    print("🔍 love bot assembled")

    try:
        print("🔍 waking up our love bot...")
        await application.initialize()
        print("🔍 love bot is awake!")
        
        print("🔍 starting love engine...")
        await application.start()
        print("🔍 love engine running")
        
        print("🔍 listening for love...")
        await application.updater.start_polling()
        print("🔍 ears open for /start, /settings, and love notes")
        
        print("🤖 our love bot is alive and ready!")
        print("💌 tell your friends to say /start let's grow our love circle")
    except Exception as e:
        print(f"❌ our love bot stumbled: {e}")
        return

    # set up love schedules for everyone already in our circle
    for chat_id, data in users.items():
        if data.get("subscribed") and data.get("interval_hours"):
            schedule_user_job(application, chat_id, data["interval_hours"])
    print(f"⏰ love scheduled for {len(users)} beautiful humans.")

    # conversation flow how we talk to our love circle
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASKING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
        },
        fallbacks=[
            CommandHandler("start", start),
            CallbackQueryHandler(button_handler),
            MessageHandler(filters.TEXT & ~filters.COMMAND, update_name_globally),
        ],
    )

    # connect all the pieces
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, update_name_globally))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, love_u_back))

    # keep our love bot running for 24 hours using pythonanywhere for first time
    try:
        await asyncio.sleep(86400)  # 24 hours of love
    except KeyboardInterrupt:
        pass
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        print("💤 love bot taking a nap... but don't worry, it'll be back tomorrow!")

if __name__ == '__main__':
    asyncio.run(main())