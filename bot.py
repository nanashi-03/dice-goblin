import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

required_env_vars = ["DISCORD_TOKEN", "MONGODB_URI"]
missing = [var for var in required_env_vars if not os.getenv(var)]
if missing:
    raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Load commands
@bot.event
async def setup_hook():
    # Reduced list of commands
    extensions = [
        "import_character",
        "view_character",
        "roll",
        "repeat_roll",
        "attack",
        "help"
    ]
    for ext in extensions:
        await bot.load_extension(f"commands.{ext}")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

bot.run(os.getenv("DISCORD_TOKEN"))