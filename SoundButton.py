import os
import discord
from discord.ui import Button
from constants import AVAILABLE_SOUNDS, SOUNDS_FOLDER


class SoundButton(Button):
    def __init__(self, sound_name, **kwargs):
        super().__init__(label=sound_name, **kwargs)
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

            if vc.is_playing():
                vc.stop()

            vc.play(audio_source)
        else:
            await interaction.response.send_message('You are not in a voice channel!')
