from flask import Flask, request, jsonify
import asyncio
import re
import time
from telethon import TelegramClient, events
from telethon.tl.types import User
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize Flask app
app = Flask(__name__)

# Define your API ID and hash from my.telegram.org
api_id = 16553273
api_hash = '92595a750f923a15cf1fb26dd69058c2'
bot_token = '7424863149:AAGg9f1IovYe_ACMHhw8pXwXm4-PbNmvTyw'

# Path to the ChromeDriver executable
chromedriver_path = '/usr/local/bin/chromedriver'

# Group chat ID (replace with the integer ID of your group)
GROUP_CHAT_ID = -1002170864046

# Initialize the Telegram client
client = TelegramClient('userbot', api_id, api_hash).start(bot_token=bot_token)

# Function to run Selenium script
def run_selenium_script(url):
    chrome_options = Options()
    chrome_options.add_argument("headless")
    chrome_options.add_argument("no-sandbox")
    chrome_options.add_argument("disable-dev-shm-usage")
    chrome_options.add_argument("remote-debugging-port=9222")
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("disable-software-rasterizer")

    service = Service(chromedriver_path)
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(url)
        time.sleep(20)

        menu_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'tp98'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", menu_btn)
        driver.execute_script("arguments[0].click();", menu_btn)
        time.sleep(40)
        menu_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'btn6'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", menu_btn)
        driver.execute_script("arguments[0].click();", menu_btn)
        time.sleep(40)

        menu_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'btn6'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", menu_btn)
        driver.execute_script("arguments[0].click();", menu_btn)
        time.sleep(25)

        menu_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'gtelinkbtn'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", menu_btn)
        driver.execute_script("arguments[0].click();", menu_btn)
        time.sleep(25)

        last_url = driver.current_url
        driver.quit()
        return last_url
    except Exception as e:
        driver.quit()
        raise e

# Function to send a message to the group
async def send_to_group(message):
    try:
        await client.send_message(GROUP_CHAT_ID, message)
        print(f'Sent to group: {message}')
    except Exception as e:
        print(f'Failed to send message to group: {e}')

# Function to send a reply to the sender
async def send_reply(sender_id, message):
    try:
        await client.send_message(sender_id, message)
        print(f'Replied to sender {sender_id}: {message}')
    except Exception as e:
        print(f'Failed to send reply to sender: {e}')

# Function to get the profile link of the sender
async def get_profile_link(sender_id):
    try:
        user = await client.get_entity(sender_id)
        if isinstance(user, User):
            if user.username:
                profile_link = f"https://t.me/{user.username}"
            else:
                profile_link = f"https://t.me/{sender_id}"
        else:
            profile_link = f"https://t.me/{sender_id}"
        return profile_link
    except Exception as e:
        print(f"Failed to get profile link for user {sender_id}: {e}")
        return "Profile link not available"

# Function to process the URL
async def process_url(url, sender_id):
    profile_link = await get_profile_link(sender_id)
    await send_reply(sender_id, 'Processing URL. This may take up to 3-4 minutes.')
    await send_to_group(f'Processing URL: {url}\nSender Profile Link: {profile_link}')
    try:
        last_url = run_selenium_script(url)
        await send_to_group(f'Script completed successfully. Last URL: {last_url}')
        await send_reply(sender_id, f'Script completed successfully. Last URL: {last_url}')
    except Exception as e:
        await send_to_group(f'An error occurred: {e}')
        await send_reply(sender_id, f'An error occurred: {e}')

# Define an event handler for new messages
@client.on(events.NewMessage)
async def handler(event):
    if event.message.out:
        return  # Ignore messages sent by the bot itself

    if not event.message.message.startswith('/'):
        message = event.message.message
        url_match = re.search(r'(https?://inshorturl\.com/\S+)', message)
        if url_match:
            url = url_match.group(1)
            sender_id = event.message.sender_id
            await event.reply('requesting...')
            asyncio.create_task(process_url(url, sender_id))

# Define the /start command handler
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    start_message = (
        "This bot is made for bypassing the ads from https://inshorturl.com/... | Master - @love_the_way_she_laugh | "
        "just directly send the link no need of any command"
    )
    await event.reply(start_message)

# Start the client
async def main():
    await client.start(bot_token=bot_token)
    print('Bot is running...')
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())

@app.route('/')
def index():
    return "Telegram Bot Web App Running"

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    url = data.get('url')
    sender_id = data.get('sender_id')
    asyncio.run(process_url(url, sender_id))
    return jsonify({'status': 'Processing initiated'})

if __name__ == '__main__':
    app.run(debug=True)
