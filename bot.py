import requests
import time
import json
from bs4 import BeautifulSoup
import schedule
import discord
from discord.ext import tasks

base_urls = [
    'https://realbooru.com/index.php?page=post&s=random',
    'https://blacked.booru.org/index.php?page=post&s=random',
]

token = 'DISCORD BOT TOKEN' # Replace DISCORD BOT TOKEN with the token of the discord bot you want it to send through.
channel_id = 'CHANNEL ID' # Replace CHANNEL ID with the discord channel id you whant the nudes to be sent in.

excluded_urls = [
    'https://realbooru.com//images/5d/63/5d63212c8b520b9a4536c14b75a80b2b.jpg',
    'https://realbooru.com//images/9f/4c/9f4c15b0abc1d50f12387dd278b453af.jpg',
    'https://img.xbooru.com//images/64/fd0f076f02ab567434ac1f6a96b0f5ec790a2b13.jpg?72132',
    'https://img.xbooru.com//images/266/fe81eb73ae517875c12b7e45a4970b76.jpeg?282190',
    'https://img.xbooru.com//samples/188/sample_fee56ac80183da8320b28cc62bd240ca.jpg?349504',
    'https://img.xbooru.com//samples/119/sample_b026c09543f2b5b92728eec1b90da7dacc754de9.jpg?126626',
    'https://img.xbooru.com//samples/145/sample_cb6a40640735c31c0c7673f857854d2e.jpg?153912',
    'https://img.xbooru.com//samples/160/sample_b604c36cd6a1a89794747d945d23cead.jpg?170431',
    'https://img.xbooru.com//images/281/bd26211965f0f64f0d3539ee27705376.jpeg?299933',
    'https://img.booru.org/hgoon//images/5/b8c553a850f8a2b34ea8b5bd1924e968c58d4389.jpg',
    'https://img.xbooru.com//images/12/a465f214c358072c90117fc582eaa61f2de03cff.jpg?11198',
    'https://img.xbooru.com//images/68/04f597953cf8de09c100101b20f2385d4c0f1b7e.jpg?75652'
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

        response = requests.get(base_url)
        if 'text/html' not in response.headers.get('content-type'):
            print(f'Skipping non-image/video content from {base_url}')
            return  # Try the next base URL

        soup = BeautifulSoup(response.text, 'html.parser')
        image_link = None
        mp4_link = None

        # Check for image link
        img_element = soup.find('img', {'id': 'image'})
        if img_element:
            image_link = img_element.get('src')

        # Check for video links
        video_element = soup.find('video', {'id': 'gelcomVideoPlayer'})
        if video_element:
            sources = video_element.find_all('source')
            for source in sources:
                if source.get('type') == 'video/mp4':
                    mp4_link = source.get('src')
                    break

        # Check if the found image link is excluded
        if image_link and image_link in excluded_urls:
            print(f'Excluded image found. Skipping...')
            return  # Try the next base URL

        # Initialize payload before conditional checks
        payload = None

        # If an image link is not found, try using the video link
        if not image_link and mp4_link:
            payload = mp4_link
            print(f'Sent video to channel!')
        elif image_link:
            payload = image_link
            print(f'Sent image to channel!')
        else:
            print(f'Could not find image or video link from {base_url}. Trying the next URL...')

        if payload:
            channel = bot.get_channel(channel_id)
            await channel.send(payload)
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
