import os
import discord
import requests
from discord.ui import Button, View
from constants import AVAILABLE_SOUNDS, SOUNDS_FOLDER
from fetch_data_url import fetch_data_url
from ConfirmView import ConfirmView
from sound_button_factory import SoundButtonFactory

MAX_BUTTONS = 24

class PageButton(Button):
    def __init__(self, label, page, total_pages, callback_func):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.page = page
        self.total_pages = total_pages
        self.callback_func = callback_func

    async def callback(self, interaction):
        await self.callback_func(interaction, self.page)


def create_sound_list_view(page, total_pages, page_callback):
    from discord.ui import View, Button

    view = View(timeout=1200)

    sound_names = list(AVAILABLE_SOUNDS.keys())
    start = page * MAX_BUTTONS
    end = start + MAX_BUTTONS
    current_sounds = sound_names[start:end]

    for sound_name in current_sounds:
        button = Button(label=sound_name)

        async def button_callback(inter, name=sound_name):
            sound_path = os.path.join(SOUNDS_FOLDER, AVAILABLE_SOUNDS[name])
            await play_sound(inter, name, sound_path)

        button.callback = button_callback
        view.add_item(button)

    if page > 0:
        prev_button = Button(label="Previous")

        async def prev_callback(inter):
            await page_callback(inter, page - 1)

        prev_button.callback = prev_callback
        view.add_item(prev_button)

    if page < total_pages - 1:
        next_button = Button(label="Next")

        async def next_callback(inter):
            await page_callback(inter, page + 1)

        next_button.callback = next_callback
        view.add_item(next_button)

    return view


async def send_sound_list_message(interaction):
    total_pages = (len(AVAILABLE_SOUNDS) + MAX_BUTTONS - 1) // MAX_BUTTONS

    async def page_callback(inter, page):
        view = create_sound_list_view(page, total_pages, page_callback)
        await inter.response.edit_message(content="Click a sound to play:", view=view)

    view = create_sound_list_view(0, total_pages, page_callback)
    await interaction.response.send_message("Click a sound to play:", view=view)



async def play_sound(interaction, sound_name, sound_path):
    vc = interaction.guild.voice_client

    if interaction.user.voice is None or interaction.user.voice.channel is None:
        if not interaction.response.is_done():
            await interaction.response.send_message("❌ You must be in a voice channel to play sounds!", ephemeral=True)
        return

    if vc is None:
        vc = await interaction.user.voice.channel.connect()

    audio_source = discord.FFmpegPCMAudio(sound_path)

    if vc.is_playing():
        vc.stop()

    vc.play(audio_source, after=lambda e: print('Finished playing'))

    if not interaction.response.is_done():
        await interaction.response.defer()



async def stop_sound(interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message('⏹️ Stopped the sound.')
    else:
        await interaction.response.send_message('⚠️ Nothing is playing.')


async def add_sound_to_board(interaction, name, url):
    try:
        if 'myinstants' in url:
            media_url, ext = fetch_data_url(url=url)
        else:
            await interaction.response.send_message('⚠️ Unsupported URL. Only https://www.myinstants.com/ is supported.')
            return False

        sound_path = os.path.join(SOUNDS_FOLDER, f'{name}.{ext}')
        response = requests.get(media_url)
        response.raise_for_status()
        with open(sound_path, 'wb') as f:
            f.write(response.content)

        AVAILABLE_SOUNDS[name] = f'{name}.{ext}'
        await interaction.response.send_message(f'✅ Added new sound: `{name}`')
        return True
    except Exception as e:
        await interaction.response.send_message(f'❌ Failed to download sound: {e}')
        return False


async def handle_play_command_with_name(interaction, sound_name):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        if vc is None:
            vc = await channel.connect()
        else:
            await vc.move_to(channel)

        if sound_name not in AVAILABLE_SOUNDS:
            await interaction.response.send_message(f'❌ Invalid sound! Available: {", ".join(AVAILABLE_SOUNDS.keys())}')
            return

        sound_path = os.path.join(SOUNDS_FOLDER, AVAILABLE_SOUNDS[sound_name])
        await play_sound(interaction, sound_name, sound_path)
    else:
        await interaction.response.send_message('⚠️ You are not in a voice channel!')


async def handle_removesound_command(interaction, sound_name):
    if sound_name not in AVAILABLE_SOUNDS:
        await interaction.response.send_message(f'❌ Sound `{sound_name}` does not exist.')
        return

    sound_path = os.path.join(SOUNDS_FOLDER, AVAILABLE_SOUNDS[sound_name])

    try:
        if os.path.exists(sound_path):
            os.remove(sound_path)
        del AVAILABLE_SOUNDS[sound_name]
        await interaction.response.send_message(f'✅ Removed sound: `{sound_name}`')
    except Exception as e:
        await interaction.response.send_message(f'❌ Failed to remove sound: {e}')


async def handle_leave_command(interaction):
    vc = interaction.guild.voice_client
    if vc:
        await vc.disconnect()
        await interaction.response.send_message('👋 Disconnected from the voice channel.')
    else:
        await interaction.response.send_message('⚠️ Not connected to any voice channel.')


async def handle_addsound_command(interaction, sound_name, url):
    await add_sound_to_board(interaction, sound_name, url)


async def handle_addandplay_command(interaction, sound_name, url):
    success = await add_sound_to_board(interaction, sound_name, url)
    if success:
        await handle_play_command_with_name(interaction, sound_name)


async def handle_removeall_command(interaction):
    async def confirm_callback(confirm_interaction):
        for file in os.listdir(SOUNDS_FOLDER):
            os.remove(os.path.join(SOUNDS_FOLDER, file))
        AVAILABLE_SOUNDS.clear()
        await confirm_interaction.response.send_message('✅ All sounds removed!')

    view = ConfirmView(confirm_callback)
    await interaction.response.send_message('⚠️ Are you sure you want to remove all sounds?', view=view)
