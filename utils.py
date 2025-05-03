from discord.ui import View
from constants import AVAILABLE_SOUNDS
from sound_button_factory import SoundButtonFactory
import discord
import requests
from fetch_data_url import fetch_data_url
from constants import AVAILABLE_SOUNDS, SOUNDS_FOLDER
import os

def create_sound_list_view():
    view = View(timeout=60*60*24)
    for sound_name in AVAILABLE_SOUNDS:
        view.add_item(SoundButtonFactory.create(sound_name))
    return view

async def send_sound_list_message(message):
    view = create_sound_list_view()
    await message.channel.send("Click a sound to play:", view=view)

async def send_sound_list_interaction(interaction):
    view = create_sound_list_view()
    await interaction.followup.send("Click a sound to play:", view=view)

async def play_sound(message, sound_name, sound_path):
    vc = message.guild.voice_client
    audio_source = discord.FFmpegPCMAudio(sound_path)

    if vc.is_playing():
        vc.stop()

    vc.play(audio_source, after=lambda e: print('Finished playing'))
    await message.channel.send(f'Playing {sound_name} 🔊')


async def stop_sound(message):
    if message.guild.voice_client and message.guild.voice_client.is_playing():
        message.guild.voice_client.stop()
        await message.channel.send('Stopped the sound.')
    else:
        await message.channel.send('Nothing is playing.')

async def add_sound_to_board(message, name, url):
    try:
        if 'myinstants' in url:
            media_url, ext = fetch_data_url(url=url)
        else:
            await message.channel.send('Unsupported URL. Currently supports only https://www.myinstants.com/.')
            return False

        sound_path = os.path.join(SOUNDS_FOLDER, f'{name}.{ext}')
        response = requests.get(media_url)
        response.raise_for_status()
        with open(sound_path, 'wb') as f:
            f.write(response.content)

        AVAILABLE_SOUNDS[name] = f'{name}.{ext}'
        await message.channel.send(f'Added new sound: {name}')
        return True
    except Exception as e:
        await message.channel.send(f'Failed to download sound: {e}')
        return False

async def handle_play_command_with_name(message, sound_name):
    if message.author.voice:
        channel = message.author.voice.channel
        if message.guild.voice_client is None:
            vc = await channel.connect()
        else:
            vc = message.guild.voice_client
            await vc.move_to(channel)

        if sound_name not in AVAILABLE_SOUNDS:
            await message.channel.send(f'Invalid sound! Available: {", ".join(AVAILABLE_SOUNDS.keys())}')
            return

        sound_path = os.path.join(SOUNDS_FOLDER, AVAILABLE_SOUNDS[sound_name])
        await play_sound(message, sound_name, sound_path)

    else:
        await message.channel.send('You are not in a voice channel!')

async def handle_removesound_command(message):
    parts = message.content.split()
    if len(parts) < 2:
        await message.channel.send('Usage: $removesound <sound_name>')
        return

    sound_name = parts[1]

    if sound_name not in AVAILABLE_SOUNDS:
        await message.channel.send(f'Sound "{sound_name}" does not exist.')
        return

    sound_path = os.path.join(SOUNDS_FOLDER, AVAILABLE_SOUNDS[sound_name])

    try:
        if os.path.exists(sound_path):
            os.remove(sound_path)
        del AVAILABLE_SOUNDS[sound_name]
        await message.channel.send(f'Removed sound: {sound_name}')
    except Exception as e:
        await message.channel.send(f'Failed to remove sound: {e}')
