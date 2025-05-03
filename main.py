import os

import discord
from dotenv import load_dotenv

from ConfirmView import ConfirmView
from constants import AVAILABLE_SOUNDS, SOUNDS_FOLDER
from utils import add_sound_to_board, handle_play_command_with_name, handle_removesound_command, play_sound, \
    send_sound_list_message, stop_sound

if not os.path.exists(SOUNDS_FOLDER):
    os.makedirs(SOUNDS_FOLDER)

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

    if message.content.startswith('/info'):
        await send_info(message)

    elif message.content.startswith('/list'):
        await send_sound_list_message(message)

    elif message.content.startswith('/plays'):
        await handle_play_command(message)

    elif message.content.startswith('/stops'):
        await stop_sound(message)

    elif message.content.startswith('/leave'):
        await handle_leave_command(message)

    elif message.content.startswith('/addandplay'):
        await handle_addandplay_command(message)

    elif message.content.startswith('/add'):
        await handle_addsound_command(message)

    elif message.content.startswith('/removeall'):
        await handle_removeall_command(message)

    elif message.content.startswith('/remove'):
        await handle_removesound_command(message)


async def send_info(message):
    info_message = """
            **Available Commands:**

            `/list`: List all available sounds with clickable buttons.
            `/play <sound_name>`: Play a specific sound. Example: `/play airhorn`
            `/stop`: Stop the current playing sound.
            `/leave`: Disconnect the bot from the voice channel.
            `/add <name> <url>`: Add a new sound to the soundboard from a URL.
            `/info`: Display this message with available commands.
            `/addandplay <name> <url>`: Downloads the sound and plays it.
            `/remove <sound_name>`: Remove a sound.
            `/removeall`: Remove all sounds.

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
        await message.channel.send('Usage: /add <name> <url_to_mp3_or_wav>')
        return

    name = parts[1]
    url = parts[2]
    await add_sound_to_board(message, name, url)

async def handle_addandplay_command(message):
    parts = message.content.split()
    if len(parts) < 3:
        await message.channel.send('Usage: /addandplay <name> <url_to_mp3_or_wav>')
        return

    name = parts[1]
    url = parts[2]

    success = await add_sound_to_board(message, name, url)
    if success:
        await handle_play_command_with_name(message, name)

async def handle_removeall_command(message):
    async def confirm_callback(interaction):
        # Remove all sound files
        for file in os.listdir(SOUNDS_FOLDER):
            os.remove(os.path.join(SOUNDS_FOLDER, file))
        AVAILABLE_SOUNDS.clear()
        await interaction.response.send_message('✅ All sounds removed!', ephemeral=False)

    view = ConfirmView(confirm_callback)
    await message.channel.send('⚠️ Are you sure you want to remove all sounds?', view=view)

client.run(os.getenv('TOKEN'))
