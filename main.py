import discord
import os
import requests
from dotenv import load_dotenv
from discord.ui import Button, View

from fetch_data_url import fetch_data_url

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
load_dotenv()
client = discord.Client(intents=intents)

SOUNDS_FOLDER = 'sounds'
AVAILABLE_SOUNDS = {}


# Initialize sound list
def load_sounds():
    global AVAILABLE_SOUNDS
    AVAILABLE_SOUNDS = {}
    for file in os.listdir(SOUNDS_FOLDER):
        name, ext = os.path.splitext(file)
        if ext in ['.mp3', '.wav']:
            AVAILABLE_SOUNDS[name] = file


load_sounds()

import asyncio


class SoundButton(Button):
    def __init__(self, label, sound_name):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.sound_name = sound_name

    async def callback(self, interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            if interaction.guild.voice_client is None:
                vc = await channel.connect()
            else:
                vc = interaction.guild.voice_client
                await vc.move_to(channel)

            sound_path = os.path.join(SOUNDS_FOLDER, AVAILABLE_SOUNDS[self.sound_name])
            audio_source = discord.FFmpegPCMAudio(sound_path)

            if not vc.is_playing():
                def after_playing(e):
                    interaction.client.loop.create_task(self.send_sound_list(interaction))

                vc.play(audio_source, after=after_playing)
                await interaction.response.send_message(f'Playing {self.sound_name} 🔊')
            else:
                await interaction.response.send_message('Already playing something! Wait or use /stop')

        else:
            await interaction.response.send_message('You are not in a voice channel!')

    async def send_sound_list(self, interaction):
        # After sound finishes, send the list of available sounds
        sound_list = ', '.join(AVAILABLE_SOUNDS.keys())
        await interaction.followup.send(f'Finished playing {self.sound_name}. Available sounds: {sound_list}')


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$info'):
        info_message = """
                **Available Commands:**

                `$list`: List all available sounds with clickable buttons.
                `$play <sound_name>`: Play a specific sound. Example: `$play airhorn`
                `$stop`: Stop the current playing sound.
                `$leave`: Disconnect the bot from the voice channel.
                `$addsound <name> <url>`: Add a new sound to the soundboard from a URL. Example: `$addsound airhorn https://www.myinstants.com/en/instant/dj-airhorn/ ( Please note the bot currently supports this website only )`
                `$info`: Display this message with available commands.

                **Note**: Sounds can be played in a voice channel where you are currently connected. You need to be in a voice channel for the bot to play sounds.
                """
        await message.channel.send(info_message)

    if message.content.startswith('$list'):
        if AVAILABLE_SOUNDS:
            view = View()
            for sound_name in AVAILABLE_SOUNDS:
                button = SoundButton(label=sound_name, sound_name=sound_name)
                view.add_item(button)
            await message.channel.send("Click a sound to play:", view=view)
        else:
            await message.channel.send('No sounds available.')

    if message.content.startswith('$play'):
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
            audio_source = discord.FFmpegPCMAudio(sound_path)

            if not vc.is_playing():
                vc.play(audio_source, after=lambda e: print('Finished playing'))
                await message.channel.send(f'Playing {sound_name} 🔊')
            else:
                await message.channel.send('Already playing something! Wait or use /stop')

        else:
            await message.channel.send('You are not in a voice channel!')

    if message.content.startswith('$stop'):
        if message.guild.voice_client and message.guild.voice_client.is_playing():
            message.guild.voice_client.stop()
            await message.channel.send('Stopped the sound.')
        else:
            await message.channel.send('Nothing is playing.')

    if message.content.startswith('$leave'):
        if message.guild.voice_client:
            await message.guild.voice_client.disconnect()
            await message.channel.send('Disconnected.')
        else:
            await message.channel.send('Not connected.')

    if message.content.startswith('$addsound'):
        parts = message.content.split()
        if len(parts) < 3:
            await message.channel.send('Usage: /addsound <name> <url_to_mp3_or_wav>')
            return

        name = parts[1]
        url = parts[2]
        print(url)

        if 'myinstants' in url:
            media_url, ext = fetch_data_url(url=url)

        sound_path = os.path.join(SOUNDS_FOLDER, f'{name}.{ext}')
        try:
            response = requests.get(media_url)
            response.raise_for_status()
            with open(sound_path, 'wb') as f:
                f.write(response.content)

            AVAILABLE_SOUNDS[name] = f'{name}.{ext}'
            await message.channel.send(f'Added new sound: {name}')
        except Exception as e:
            await message.channel.send(f'Failed to download sound: {e}')


client.run(os.getenv('TOKEN'))
