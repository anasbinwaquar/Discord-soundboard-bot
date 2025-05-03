import os

import discord
from discord.ui import Button, View

from constants import AVAILABLE_SOUNDS, SOUNDS_FOLDER


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

    async def generate_sound_list(self, interaction):
        view = View()
        for sound_name in AVAILABLE_SOUNDS:
            button = SoundButton(label=sound_name, sound_name=sound_name)
            view.add_item(button)

    async def send_sound_list(self, interaction):
        sound_list = ', '.join(AVAILABLE_SOUNDS.keys())
        await interaction.followup.send(f'Finished playing {self.sound_name}. Available sounds: {sound_list}')