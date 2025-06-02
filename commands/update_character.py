import json
from discord.ext import commands
from db import characters, users
import aiohttp
from utils.parse_json import parse_pathbuilder_character

class UpdateCharacter(commands.Cog):
    @commands.command(name="update")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def update_current_character(self, ctx):
        user_id = str(ctx.author.id)

        user_doc = users.find_one({"user_id": user_id})
        if not user_doc or not user_doc.get("current_character"):
            await ctx.send("❌ You don't have a current character set. Use `!setactive` to set one.")
            return

        pb_id = user_doc["current_character"]
        existing = characters.find_one({"user_id": user_id, "pb_id": pb_id})
        if not existing:
            await ctx.send("❌ Your current character could not be found in the database. Try re-importing with `!import`.")
            return

        url = f"https://pathbuilder2e.com/json.php?id={pb_id}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        await ctx.send("❌ Failed to fetch character data from Pathbuilder.")
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
            updated_doc = parse_pathbuilder_character(user_id, data, pb_id)
        except Exception as e:
            await ctx.send(f"❌ Failed to parse character: {e}")
            print(e)
            return

        characters.replace_one({"_id": existing["_id"]}, updated_doc)
        await ctx.send(f"✅ Successfully updated your current character: **{updated_doc['name']}**!")

async def setup(bot):
    await bot.add_cog(UpdateCharacter())
