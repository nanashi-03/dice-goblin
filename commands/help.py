import discord
from discord.ext import commands

class HelpCommand(commands.Cog):
    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="📖 Pathfinder 2e Bot Help",
            description="Here's a list of commands you can use:",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="🛠 Character Management",
            value=(
                "`!import <pb_id>` - Import a character from Pathbuilder\n"
                "`!update` - Update your currently active character\n"
                "`!delete <pb_id>` - Delete a character by Pathbuilder ID\n"
                "`!list` - View a list of all your imported characters\n"
                "`!setactive <name>` - Switch your active character (fuzzy match)\n"
                "`!sheet` - View your active character's summary"
            ),
            inline=False
        )

        embed.add_field(
            name="🎲 Rolling Commands",
            value=(
                "`!roll <skill>` - Roll a skill like Arcana, Athletics, etc.\n"
                "`!roll lore <name>` - Roll a custom lore skill like Warfare, Cooking, etc."
            ),
            inline=False
        )

        embed.add_field(
            name="ℹ️ Notes",
            value=(
                "- You can only have one active character at a time.\n"
                "- Use Pathbuilder's public share link ID for imports.\n"
                "- Skills and rolls are based on your active character's data."
            ),
            inline=False
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCommand())
