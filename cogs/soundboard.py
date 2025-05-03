import os
import discord
from discord.ext import commands
from discord import app_commands
from constants import AVAILABLE_SOUNDS, SOUNDS_FOLDER
from utils import handle_addandplay_command, handle_addsound_command, handle_leave_command, \
    handle_play_command_with_name, \
    handle_removeall_command, \
    handle_removesound_command, \
    send_sound_list_message, stop_sound


class Soundboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_sounds()

    def load_sounds(self):
        if not os.path.exists(SOUNDS_FOLDER):
            os.makedirs(SOUNDS_FOLDER)
        for file in os.listdir(SOUNDS_FOLDER):
            name, ext = os.path.splitext(file)
            if ext in ['.mp3', '.wav']:
                AVAILABLE_SOUNDS[name] = file

    @app_commands.command(name="info", description="Display available commands and bot information")
    async def info(self, interaction: discord.Interaction):
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
        await interaction.response.send_message(info_message)

    @app_commands.command(name="play", description="Play a sound")
    @app_commands.describe(sound_name="Name to save the sound as")
    async def play(self, interaction: discord.Interaction, sound_name: str):
        await handle_play_command_with_name(interaction, sound_name)

    @app_commands.command(name="add", description="Add a new sound")
    @app_commands.describe(sound_name="Name to save the sound as", url="URL of the sound (e.g., myinstants link)")
    async def add(self, interaction: discord.Interaction, sound_name: str, url: str):
        await handle_addsound_command(interaction, sound_name, url)

    @app_commands.command(name="remove", description="Remove a sound")
    @app_commands.describe(sound_name="Name of sound to remove")
    async def remove(self, interaction: discord.Interaction, sound_name: str):
        await handle_removesound_command(interaction, sound_name)

    @app_commands.command(name="removeall", description="Remove all sounds")
    async def removeall(self, interaction: discord.Interaction):
        await handle_removeall_command(interaction)

    @app_commands.command(name="addandplay", description="Add and immediately play a sound")
    @app_commands.describe(sound_name="Name to save the sound as", url="URL of the sound (e.g., myinstants link)")
    async def addandplay(self, interaction: discord.Interaction, sound_name: str, url: str):
        await handle_addandplay_command(interaction, sound_name, url)

    @app_commands.command(name="list", description="List all available sounds")
    async def list(self, interaction: discord.Interaction):
        await send_sound_list_message(interaction)

    @app_commands.command(name="stop", description="Stop the current sound")
    async def stop(self, interaction: discord.Interaction):
        await stop_sound(interaction)

    @app_commands.command(name="leave", description="Make the bot leave the voice channel")
    async def leave(self, interaction: discord.Interaction):
        await handle_leave_command(interaction)

async def setup(bot):
    await bot.add_cog(Soundboard(bot))