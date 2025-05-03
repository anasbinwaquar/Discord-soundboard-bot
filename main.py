import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from constants import AVAILABLE_SOUNDS, SOUNDS_FOLDER

if not os.path.exists(SOUNDS_FOLDER):
    os.makedirs(SOUNDS_FOLDER)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    await bot.load_extension('cogs.soundboard')
    await bot.tree.sync()
    print(f'✅ Logged in as {bot.user} and synced commands.')

bot.run(os.getenv('TOKEN'))
