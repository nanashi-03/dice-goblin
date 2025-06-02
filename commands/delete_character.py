from discord.ext import commands
from db import characters, users
import asyncio

class DeleteCharacter(commands.Cog):
    @commands.command(name="deletechar")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def delete_character(self, ctx, pb_id: str):
        user_id = str(ctx.author.id)
        char = characters.find_one({"user_id": user_id, "pb_id": pb_id})

        if not char:
            await ctx.send("❌ No character found with that Pathbuilder ID.")
            return

        confirm = await ctx.send(
            f"⚠️ Are you sure you want to delete **{char['name']}** (`{pb_id}`)? React with ✅ to confirm."
        )
        await confirm.add_reaction("✅")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.id == confirm.id

        try:
            await ctx.bot.wait_for("reaction_add", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("⌛ Timed out. Deletion cancelled.")
            return

        characters.delete_one({"_id": char["_id"]})

        # Unset current_character if needed
        user_doc = users.find_one({"user_id": user_id})
        if user_doc and user_doc.get("current_character") == pb_id:
            users.update_one(
                {"user_id": user_id},
                {"$unset": {"current_character": ""}}
            )

        await ctx.send(f"🗑️ Deleted character **{char['name']}**.")

async def setup(bot):
    await bot.add_cog(DeleteCharacter())
