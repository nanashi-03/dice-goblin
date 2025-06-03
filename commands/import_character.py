import json
from discord.ext import commands
from db import characters
import aiohttp
from utils.parse_json import parse_pathbuilder_character

class ImportCharacter(commands.Cog):
    @commands.command(name="import", help="Import or update your character from Pathbuilder 2e using its ID. Example: `!import [123456]`. Click on 'Export to JSON' in Pathbuilder to get the ID. If no ID is provided, uses the ID from your last import.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def import_character(self, ctx, pb_id: str = None):
        user_id = str(ctx.author.id)
        
        # If no pb_id provided, try to get existing one
        if pb_id is None:
            existing_char = characters.find_one({"user_id": user_id})
            if existing_char and "pb_id" in existing_char:
                pb_id = existing_char["pb_id"]
            else:
                await ctx.send("❌ No character ID provided and no existing character found. Please provide a Pathbuilder ID.")
                return
        
        url = f"https://pathbuilder2e.com/json.php?id={pb_id}"

        if pb_id and not pb_id.isdigit():
            await ctx.send("❌ Invalid Pathbuilder ID format. IDs should be numbers only.")
            return

        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        await ctx.send("❌ Failed to fetch character from Pathbuilder.")
                        return
                    text = await response.text()

                    try:
                        data = json.loads(text.strip())
                    except json.JSONDecodeError:
                        await ctx.send("❌ Failed to decode character data as JSON.")
                        return
            except aiohttp.ClientError as e:
                await ctx.send(f"❌ Network error: {e}")
                return

        if not data.get("success") or "build" not in data:
            await ctx.send("❌ Invalid Pathbuilder character data.")
            return

        try:
            parsed = parse_pathbuilder_character(user_id, data, pb_id)
        except Exception as e:
            await ctx.send(f"❌ Failed to parse character: {e}")
            return

        # Replace or insert character
        characters.replace_one(
            {"user_id": user_id}, 
            parsed, 
            upsert=True
        )
        await ctx.send(f"✅ Successfully imported **{parsed['name']}**!")
    
    #handle the cooldown error
    @import_character.error
    async def import_character_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Please wait {error.retry_after:.2f} seconds before importing again.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid Pathbuilder ID format. Please provide a valid numeric ID.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please provide a Pathbuilder ID to import your character.")
        else:
            await ctx.send("❌ An unexpected error occurred while importing the character.")

async def setup(bot):
    await bot.add_cog(ImportCharacter())