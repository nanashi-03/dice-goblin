from discord.ext import commands
import d20

class RepeatRollCommand(commands.Cog):
    @commands.command(name="repeatroll", aliases=["rr"], help="Repeats a roll multiple times. Usage: `!rr <number> <roll>`")
    async def repeat_roll(self, ctx, times: int, *, expression):
        if times < 1:
            await ctx.send("❌ Please specify a number larger than 1.")
            return

        try:
            rolls = [d20.roll(expression) for _ in range(times)]
        except d20.RollSyntaxError as e:
            await ctx.send(f"❌ Invalid roll: {e}")
            return

        roll_texts = [f"{expression}({roll.result})" for roll in rolls]
        total = sum(roll.total for roll in rolls)
        
        await ctx.send("\n".join([*roll_texts, f"Total: `{total}`"]))

    @repeat_roll.error
    async def repeat_roll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please provide both the number of rolls and roll expression. Example: `!rr 2 1d20+5`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid number of rolls. Please provide a number above 1.")
        else:
            await ctx.send("❌ An unexpected error occurred while processing the roll.")

async def setup(bot):
    await bot.add_cog(RepeatRollCommand())