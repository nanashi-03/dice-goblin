import discord
from discord.ext import commands
import d20
from db import characters
import difflib

MODIFIER_FIELDS = {
    "perception": "perception",
    "fortitude": "saves.fortitude",
    "reflex": "saves.reflex",
    "will": "saves.will",
    "acrobatics": "skills.acrobatics",
    "arcana": "skills.arcana",
    "athletics": "skills.athletics",
    "crafting": "skills.crafting",
    "deception": "skills.deception",
    "diplomacy": "skills.diplomacy",
    "intimidation": "skills.intimidation",
    "medicine": "skills.medicine",
    "nature": "skills.nature",
    "occultism": "skills.occultism",
    "performance": "skills.performance",
    "religion": "skills.religion",
    "society": "skills.society",
    "stealth": "skills.stealth",
    "survival": "skills.survival",
    "thievery": "skills.thievery",
}

def get_nested(doc, dotted_key):
    """Fetch nested key using dot notation.
    
    Args:
        doc (dict): Document to search in
        dotted_key (str): Key in dot notation (e.g., "saves.fortitude")
        
    Returns:
        int: Value at the nested key or 0 if not found
    """
    keys = dotted_key.split(".")
    for k in keys:
        doc = doc.get(k, {})
    return doc if isinstance(doc, int) else 0

class RollCommand(commands.Cog):
    """Commands for handling dice rolls and skill checks."""
    @commands.command(name="roll", aliases=["r"], help="Rolls a d20 with optional modifiers or lore skills. Use `lore <skill>` for lore checks. Modifiers can be used directly (e.g., `!roll perception`). For manual rolls, use `!roll 1d20+5`.")
    async def roll(self, ctx, *, expression: str):
        user_id = str(ctx.author.id)
        parts = expression.strip().lower().split()
        bonus = 0
        
        # Extract bonus if specified with +N or -N
        if parts[-1].startswith(('+', '-')) and parts[-1][1:].isdigit():
            bonus = int(parts[-1])
            expression = ' '.join(parts[:-1])
        else:
            expression = ' '.join(parts)

        character = None

        # Lore handling
        if expression.startswith("lore "):
            lore_query = expression[5:].strip()
            character = characters.find_one({"user_id": user_id})
            if not character:
                await ctx.send("❌ Character not found.")
                return

            lores = character.get("lores", {})
            if not lores:
                await ctx.send("❌ No lore skills found.")
                return

            matches = difflib.get_close_matches(lore_query, lores.keys(), n=3, cutoff=0.3)
            if not matches:
                await ctx.send("❌ No matching lore skills found.")
                return

            if len(matches) > 1:
                options = "\n".join([f"{i+1}. {name} (+{lores[name]})" for i, name in enumerate(matches)])
                await ctx.send(f"🔎 Multiple lore matches found:\n{options}\nType a number to pick.")

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

                try:
                    msg = await ctx.bot.wait_for("message", check=check, timeout=20)
                    index = int(msg.content) - 1
                    if index < 0 or index >= len(matches):
                        raise ValueError
                except:
                    await ctx.send("❌ Invalid selection.")
                    return

                lore_name = matches[index]
            else:
                lore_name = matches[0]

            mod = lores[lore_name]
            expression = f"1d20+{mod}"
            if bonus:
                expression += f"{bonus:+d}"
            stat_label = f"{lore_name.title()} Lore"

        elif expression in MODIFIER_FIELDS:
            character = characters.find_one({"user_id": user_id})
            if not character:
                await ctx.send("❌ Active character not found.")
                return

            mod_field = MODIFIER_FIELDS[expression]
            modifier = get_nested(character, mod_field)
            stat_label = expression.title()
            expression = f"1d20+{modifier}"
            if bonus:
                expression += f"{bonus:+d}"

        else:
            stat_label = None  # For manual rolls

        # Roll the expression
        try:
            result = d20.roll(expression)
        except d20.RollSyntaxError as e:
            await ctx.send(f"❌ Invalid roll: {e}")
            return

        # Use embed for lore and skill rolls, simple format for manual rolls
        if character and stat_label:
            embed = discord.Embed(
                title=f"🎲 Roll: `{expression}`",
                description=f"**Result:** `{result.total}`",
                color=discord.Color.blurple()
            )
            embed.add_field(name="Details", value=f"{result.result}", inline=False)
            embed.set_footer(text=f"{character['name']}'s {stat_label}")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{expression}({result.result})")

    @roll.error
    async def roll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please provide a roll expression or lore skill.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid roll format. Use `!roll <expression>` or `!roll lore <skill>`.")
        else:
            await ctx.send("❌ An unexpected error occurred while processing the roll.")


async def setup(bot):
    await bot.add_cog(RollCommand())
