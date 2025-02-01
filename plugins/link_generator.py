from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(
                text="Send the First Post Link from DB Channel:",
                chat_id=message.from_user.id,
                filters=filters.text,
                timeout=60
            )
        except:
            return

        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply(
                "❌ Error\n\nThis link is not from my DB Channel or is invalid.",
                quote=True
            )
            continue

    while True:
        try:
            second_message = await client.ask(
                text="Send the Last Post Link from DB Channel:",
                chat_id=message.from_user.id,
                filters=filters.text,
                timeout=60
            )
        except:
            return

        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply(
                "❌ Error\n\nThis link is not from my DB Channel or is invalid.",
                quote=True
            )
            continue

    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
    )

    await second_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)
