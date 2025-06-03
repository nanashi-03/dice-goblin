import json
from discord.ext import commands
from db import characters, users
import aiohttp
from datetime import datetime, timezone
from utils.parse_json import parse_pathbuilder_character

class ImportCharacter(commands.Cog):
    @commands.command(name="import", help="Import a character from Pathbuilder 2e using its ID. Example: `!import 123456`. Clcik on 'Export to JSON' in Pathbuilder to get the ID.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def import_character(self, ctx, pb_id: str):
        url = f"https://pathbuilder2e.com/json.php?id={pb_id}"
        user_id = str(ctx.author.id)

        async with aiohttp.ClientSession() as session:
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

        # Create user record if it doesn't exist
        if not users.find_one({"user_id": user_id}):
            users.insert_one({
                "user_id": user_id,
                "username": str(ctx.author),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "current_character": pb_id
            })

        # Check for existing character
        if characters.find_one({"user_id": user_id, "pb_id": pb_id}):
            await ctx.send(f"❌ You already have a character with this Pathbuilder ID. Use `!update {pb_id}` to update it.")
            return

        try:
            parsed = parse_pathbuilder_character(user_id, data, pb_id)
        except Exception as e:
            await ctx.send(f"❌ Failed to parse character: {e}")
            return

        characters.insert_one(parsed)
        await ctx.send(f"✅ Successfully imported **{parsed['name']}**!")

    @import_character.error
    async def import_character_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Please wait {error.retry_after:.1f}s before using this command again.")

async def setup(bot):
    await bot.add_cog(ImportCharacter())