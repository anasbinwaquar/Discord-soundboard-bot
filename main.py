import os
import discord
import requests
from dotenv import load_dotenv

from constants import AVAILABLE_SOUNDS, SOUNDS_FOLDER
from fetch_data_url import fetch_data_url
from utils import send_sound_list_message, play_sound, stop_sound, add_sound_to_board

# Initialize intents and client
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
load_dotenv()

client = discord.Client(intents=intents)

def load_sounds():
    for file in os.listdir(SOUNDS_FOLDER):
        name, ext = os.path.splitext(file)
        if ext in ['.mp3', '.wav']:
            AVAILABLE_SOUNDS[name] = file

# Load sounds at startup
load_sounds()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$info'):
        await send_info(message)

    elif message.content.startswith('$list'):
        if AVAILABLE_SOUNDS:
            await send_sound_list_message(message)
        else:
            await message.channel.send('No sounds available.')

    elif message.content.startswith('$play'):
        await handle_play_command(message)

    # Stop the currently playing sound
    elif message.content.startswith('$stop'):
        await stop_sound(message)

    elif message.content.startswith('$leave'):
        await handle_leave_command(message)

    elif message.content.startswith('$addsound'):
        await handle_addsound_command(message)

async def send_info(message):
    info_message = """
            **Available Commands:**

            `$list`: List all available sounds with clickable buttons.
            `$play <sound_name>`: Play a specific sound. Example: `$play airhorn`
            `$stop`: Stop the current playing sound.
            `$leave`: Disconnect the bot from the voice channel.
            `$addsound <name> <url>`: Add a new sound to the soundboard from a URL.
            `$info`: Display this message with available commands.

            **Note**: Sounds can be played in a voice channel where you are currently connected.
            """
    await message.channel.send(info_message)

async def handle_play_command(message):
    if message.author.voice:
        channel = message.author.voice.channel
        if message.guild.voice_client is None:
            vc = await channel.connect()
        else:
            vc = message.guild.voice_client
            await vc.move_to(channel)

        parts = message.content.split()
        if len(parts) < 2:
            await message.channel.send('Please specify a sound! Example: `/play airhorn`')
            return

        sound_name = parts[1]
        if sound_name not in AVAILABLE_SOUNDS:
            await message.channel.send(f'Invalid sound! Available: {", ".join(AVAILABLE_SOUNDS.keys())}')
            return

        sound_path = os.path.join(SOUNDS_FOLDER, AVAILABLE_SOUNDS[sound_name])
        await play_sound(message, sound_name, sound_path)

    else:
        await message.channel.send('You are not in a voice channel!')

async def handle_leave_command(message):
    if message.guild.voice_client:
        await message.guild.voice_client.disconnect()
        await message.channel.send('Disconnected from the voice channel.')
    else:
        await message.channel.send('Not connected to any voice channel.')

async def handle_addsound_command(message):
    parts = message.content.split()
    if len(parts) < 3:
        await message.channel.send('Usage: /addsound <name> <url_to_mp3_or_wav>')
        return

    name = parts[1]
    url = parts[2]
    await add_sound_to_board(message, name, url)

client.run(os.getenv('TOKEN'))
