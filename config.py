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
BATCH_TIMEOUT = 60  # seconds
BROADCAST_INTERVAL = 60  # seconds
BROADCAST_MESSAGE = "Hello, this is a broadcast message!"
AUTO_DELETE_TIME = 5  # minutes
GET_FILE_AGAIN_BUTTON_TEXT = "Get File Again"
GET_FILE_AGAIN_BUTTON_URL = "https://example.com/get_file_again"
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
    return file["file"]

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
    return response.json()["short_url"]

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
            file = await client.download_media(message)
            # Store the file in the database
            file_id = os.path.basename(file)
            store_file(file_id, file)
            # Generate a link for the file
            link = f"https://example.com/{file_id}"
            # Shorten the link
            shortened_link = shorten_url(link)
            await message.reply(f"File uploaded successfully! You can access it here: {shortened_link}")
        elif message.text == "/batch":
            # Initialize a list to store the files
            files = []
            # Wait for the user to upload all the files
            await message.reply("Please upload all the files. You can upload up to {} files.".format(BATCH_SIZE))
            # Get all the files from the user
            for i in range(BATCH_SIZE):
                file = await client.download_media(message)
                files.append(file)
                # Check if the user has uploaded all the files
                if len(files) == BATCH_SIZE:
                    break
            # Store all the files in the database
            batch_id = os.path.basename(files[0])
            for file in files:
                file_id = os.path.basename(file)
                store_file(file_id, file)
                # Generate a link for the file
                link = f"https://example.com/{batch_id}/{file_id}"
                # Shorten the link
                shortened_link = shorten_url(link)
                # Add the link to the list of links
                links.append(shortened_link)
            # Send all the links to the user
            await message.reply("All files uploaded successfully! You can access them here: {}".format("\n".join(links)))
        elif message.text == "/delete":
            # Get the file ID from the user
            file_id = message.text.split(" ")[1]
            # Delete the file from the database
            delete_file(file_id
