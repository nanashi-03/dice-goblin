import discord
from discord.ext import commands
from db import characters, users
from math import ceil

class ListCharacters(commands.Cog):
    @commands.command(name="listchars")
    async def list_characters(self, ctx, sort_by: str = "name"):
        user_id = str(ctx.author.id)
        all_chars = list(characters.find({"user_id": user_id}))
        if not all_chars:
            await ctx.send("❌ You don’t have any imported characters.")
            return

        user_data = users.find_one({"user_id": user_id})
        active_pb_id = user_data.get("current_character") if user_data else None

        # Sort
        if sort_by.lower() == "level":
            all_chars.sort(key=lambda c: c.get("level", 0), reverse=True)
        else:
            all_chars.sort(key=lambda c: c.get("name", "").lower())

        # Pagination config
        per_page = 5
        pages = ceil(len(all_chars) / per_page)

        def create_embed(page):
            embed = discord.Embed(
                title=f"{ctx.author.display_name}'s Characters (Page {page+1}/{pages})",
                color=discord.Color.green()
            )
            start = page * per_page
            for char in all_chars[start:start+per_page]:
                name = char.get("name", "Unnamed")
                pb_id = char.get("pb_id", "N/A")
                level = char.get("level", "?")
                is_active = (pb_id == active_pb_id)
                label = f"🟢 **(Active)**" if is_active else ""
                embed.add_field(
                    name=f"{name} (Lv {level})",
                    value=f"`{pb_id}` {label}",
                    inline=False
                )
            return embed

        page = 0
        message = await ctx.send(embed=create_embed(page))

        if pages <= 1:
            return

        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ["⬅️", "➡️"]

        while True:
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=60.0, check=check)
                await message.remove_reaction(reaction.emoji, user)
                if reaction.emoji == "➡️" and page < pages - 1:
                    page += 1
                elif reaction.emoji == "⬅️" and page > 0:
                    page -= 1
                await message.edit(embed=create_embed(page))
            except:
                break  # stop listening after timeout

async def setup(bot):
    await bot.add_cog(ListCharacters())
