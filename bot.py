import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Load commands
@bot.event
async def setup_hook():
    # Reduced list of commands
    extensions = [
        "import_character",
        "view_character",
        "roll",
        "attack"
    ]
    for ext in extensions:
        await bot.load_extension(f"commands.{ext}")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

bot.run(os.getenv("DISCORD_TOKEN"))