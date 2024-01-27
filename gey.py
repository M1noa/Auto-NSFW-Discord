import requests
import json
import random
import discord
from discord.ext import tasks

base_urls = [
    'https://api.rule34.xxx//index.php?page=dapi&s=post&q=index&json=1&tags=femboy%20cum&limit=1000&pid={}',
    'https://api.rule34.xxx//index.php?page=dapi&s=post&q=index&json=1&tags=femboy%20bdsm&limit=1000&pid={}',
    'https://api.rule34.xxx//index.php?page=dapi&s=post&q=index&json=1&tags=femboy%20forced&limit=1000&pid={}',
    'https://api.rule34.xxx//index.php?page=dapi&s=post&q=index&json=1&tags=femboy&limit=1000&pid={}',
]

token = 'token'
channel_id = channel

excluded_urls = [
    ''
]

current_base_index = 0

intents = discord.Intents.default()
intents.all()

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    send_images.start() 

@tasks.loop(seconds=1.5)
async def send_images():
    global current_base_index

    try:
        base_url = get_current_base_url()
        current_base_index = (current_base_index + 1) % len(base_urls)  # Move to the next base URL

        response = requests.get(base_url.format(random.randint(1, 35)))
        if 'application/json' not in response.headers.get('content-type'):
            print(f'Skipping non-JSON content from {base_url}')
            return  # Try the next base URL

        data = json.loads(response.text)
        if not data:
            print(f'Empty JSON response from {base_url}. Trying the next URL...')
            return

        random_entry = random.choice(data)
        file_url = random_entry.get('file_url')

        # Check if the found file_url is excluded
        if file_url and file_url in excluded_urls:
            print(f'Excluded file_url found. Skipping...')
            return  # Try the next base URL

        if file_url:
            channel = bot.get_channel(channel_id)
            await channel.send(file_url)
            print(f'Sent api image to channel!')
        else:
            print(f'Could not find file_url from {base_url}. Trying the next URL...')
    except Exception as e:
        print(f'An error occurred: {str(e)}')
        print('Continuing...')

def get_current_base_url():
    global current_base_index
    return base_urls[current_base_index]

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

bot.run(token)
