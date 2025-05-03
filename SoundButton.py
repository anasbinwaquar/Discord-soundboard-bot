import os
import discord
from discord.ui import Button
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

            def after_playing(e):
                from utils import send_sound_list_interaction
                interaction.client.loop.create_task(send_sound_list_interaction(interaction))

            # 🔥 REMOVE the is_playing check → directly interrupt with .play()
            vc.play(audio_source, after=after_playing)
            await interaction.response.send_message(f'Playing {self.sound_name} 🔊', ephemeral=True)

        else:
            await interaction.response.send_message('You are not in a voice channel!', ephemeral=True)

