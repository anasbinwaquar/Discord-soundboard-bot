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

    if not vc.is_playing():
        vc.play(audio_source, after=lambda e: print('Finished playing'))
        await message.channel.send(f'Playing {sound_name} 🔊')
    else:
        await message.channel.send('Already playing something! Wait or use /stop')

async def stop_sound(message):
    if message.guild.voice_client and message.guild.voice_client.is_playing():
        message.guild.voice_client.stop()
        await message.channel.send('Stopped the sound.')
    else:
        await message.channel.send('Nothing is playing.')

async def add_sound_to_board(message, name, url):
    if 'myinstants' in url:
        media_url, ext = fetch_data_url(url=url)
    else:
        await message.channel.send(f'Sorry we currently only support URLs from myinstants')

    if not media_url or not ext:
        await message.channel.send(f'Unable to find mp3 file')

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
