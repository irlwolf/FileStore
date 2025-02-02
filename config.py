import os
import schedule
import time
from pyrogram import Client, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
import requests

# Replace these with your own values
API_ID = 23580732
API_HASH = "81ca3df48f25d954b2ebef5aec715a73"
BOT_TOKEN = "8139084920:AAGhJnoy1EIdgg6Ex9BH4Xx_hNuPyHAuL-w"
BATCH_SIZE = 10
BROADCAST_MESSAGE = "Hello, this is a broadcast message!"
URL_SHORTENR_WEBSITE = "shortxlinks.com"
URL_SHORTNER_WEBSITE_API = "89e10e3c7ab7b79375729adab10b92bf5d863f8d"
OWNER_ID = 1302460619  # Replace with your owner ID
ADMIN_ID = [1302460619]  # Replace with your admin IDs

# Connect to the MongoDB database
client = MongoClient("mongodb+srv://irlwolf:9aEpUre0fkmBjHVz@cluster0.jkd3o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["telegram_bot"]
collection = db["files"]
users_collection = db["users"]

# Create a Pyrogram client
app = Client("telegram_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to store a file
def store_file(file_id, file):
    collection.insert_one({"file_id": file_id, "file": file})

# Function to get a file
def get_file(file_id):
    file = collection.find_one({"file_id": file_id})
    return file["file"] if file else None

# Function to delete a file
def delete_file(file_id):
    collection.delete_one({"file_id": file_id})

# Function to store a user ID
def store_user_id(user_id):
    users_collection.insert_one({"user_id": user_id})

# Function to get all user IDs
def get_all_user_ids():
    users = users_collection.find()
    return [user["user_id"] for user in users]

# Function to send a broadcast message
def send_broadcast_message():
    users = get_all_user_ids()
    for user in users:
        app.send_message(chat_id=user, text=BROADCAST_MESSAGE)

# Function to shorten a URL
def shorten_url(url):
    api_url = f"https://{URL_SHORTENR_WEBSITE}/api"
    headers = {"Authorization": f"Bearer {URL_SHORTNER_WEBSITE_API}"}
    data = {"url": url}
    response = requests.post(api_url, headers=headers, json=data)
    return response.json().get("short_url", "Error shortening URL")

# Start the bot
@app.on_message()
async def handle_message(client, message):
    # Check if the user is the owner or admin
    if message.from_user.id == OWNER_ID or message.from_user.id in ADMIN_ID:
        # Handle all commands
        if message.text == "/start":
            await message.reply("Welcome to the file store bot!")
            store_user_id(message.from_user.id)
        elif message.text == "/upload":
            # Get the file from the user
            if message.reply_to_message and message.reply_to_message.document:
                file = await client.download_media(message.reply_to_message)
                file_id = os.path.basename(file)
                store_file(file_id, file)
                link = f"https://example.com/{file_id}"
                shortened_link = shorten_url(link)
                await message.reply(f"File uploaded successfully! You can access it here: {shortened_link}")
            else:
                await message.reply("Please reply to a message containing a file to upload.")
        elif message.text == "/batch":
            await message.reply("Please upload all the files. You can upload up to {} files.".format(BATCH_SIZE))
            files = []
            links = []
            for _ in range(BATCH_SIZE):
                file_message = await client.listen(message.chat.id)  # Wait for the user to upload a file
                if file_message and file_message.document:
                    file = await client.download_media(file_message)
                    file_id = os.path.basename(file)
                    store_file(file_id, file)
                    link = f"https://example.com/{file_id}"
                    shortened_link = shorten_url(link)
                    links.append(shortened_link)
                    files.append(file_id)
                else:
                    break  # Stop if no more files are uploaded
            if links:
                await message.reply("All files uploaded successfully! You can access them here:\n" + "\n".join(links))
            else:
                await message.reply("No files were uploaded.")
        elif message.text.startswith("/delete"):
            try:
                file_id = message.text.split(" ")[1]
                delete_file(file_id)
                await message.reply(f"File with ID {file_id} deleted successfully.")
            except IndexError:
                await message.reply("Please provide a file ID to delete.")
            except Exception as e:
                await message.reply(f"An error occurred: {str(e)}")

# Run the bot
app.run()
