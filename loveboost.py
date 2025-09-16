from telegram import Bot
import random
import asyncio

# ✅ REPLACE WITH YOUR BOT TOKEN
BOT_TOKEN = 'add_your_bot_token_here'
FRIEND_CHAT_ID = {
    'id': 'add_your_friend_chat_id_here',
}

messages = [
"I love Uuuuuuuuuu",
"am soooooo proud of you ✨🥺",
"am rlyyyy proud of you my  {name}",
"You're doing amazing, sweetie! 💋",
"Just a reminder: u r AWESOME 😊",
"Sending you a big hug today! 🤗",
"You've got this! I believe in you 💪",
"Thinking of you and all the great things you do ❤️",
"You are capable of anything you set your mind to ✨",
"Remember to be kind to yourself today 💋",
"Here's a hug to start your day off right 🤗",
"You are so loved {name} ❤️",
"You light up my life ✨",
"Have a wonderful day, sweetie! 💋",
"💋",
"Sending all my love 🤗",
"So glad you're in my life ❤️",
"I love you moooooooorrreeeeeeee! 🥰",
"am so lucky to have you in my life ❤️",
"am with you, honey 🤗",
"Just a reminder that you are loved beyond words ✨",
"Thinking of you and sending all my love to u 💋",
"Your my special person {name} ❤️",
"Your my favorite person in the universe 🥰",
"i c u, smile my pretty 👀",
"You make my life so much better ❤️",
"You got a heart of gold ✨",
"your soooo awesome am jealous 🤤",
"Sending you a virtual hug now 🫂",
"🫂",
"{name} yes ur fabulous 🫂",
"superstar 🚀",
]


# Initialize bot
bot = Bot(token=BOT_TOKEN)

async def send_love_message():
    message = random.choice(messages)
    await bot.send_message(chat_id=FRIEND_CHAT_ID, text=message)
    print(f"Sent: {message}")

async def main():
    print("💌 Love Bot is running...")
    print("Messages every 10 seconds. Press Ctrl+C to stop.")
    try:
        while True:
            await send_love_message()
            await asyncio.sleep(10)  # wait for 10 seconds
    except KeyboardInterrupt:
        print("\n Bot stopped!")

if __name__ == '__main__':
    asyncio.run(main())