from discord.ext import commands
from db import characters, users

class SetActiveCharacter(commands.Cog):
    @commands.command(name="setactive")
    async def set_active_character(self, ctx, pb_id: str):
        user_id = str(ctx.author.id)

        # Check if the character exists and belongs to the user
        if not characters.find_one({"user_id": user_id, "pb_id": pb_id}):
            await ctx.send("❌ You don't have a character with that Pathbuilder ID.")
            return

        result = users.update_one(
            {"user_id": user_id},
            {"$set": {"current_character": pb_id}}
        )

        if result.matched_count == 0:
            await ctx.send("❌ You don't have a user profile. Import a character first.")
            return

        await ctx.send(f"✅ Set your active character to Pathbuilder ID `{pb_id}`!")

async def setup(bot):
    await bot.add_cog(SetActiveCharacter())
