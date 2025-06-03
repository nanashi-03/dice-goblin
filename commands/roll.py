import discord
from discord.ext import commands
import d20
from db import characters, users
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
    """Fetch nested key using dot notation"""
    keys = dotted_key.split(".")
    for k in keys:
        doc = doc.get(k, {})
    return doc if isinstance(doc, int) else 0

class RollCommand(commands.Cog):
    @commands.command(name="roll", aliases=["r"], help="Rolls a d20 with optional modifiers or lore skills. Use `lore <skill>` for lore checks. Modifiers can be used directly (e.g., `!roll perception`). For manual rolls, use `!roll 1d20+5`.")
    async def roll(self, ctx, *, expression: str):
        user_id = str(ctx.author.id)
        expression = expression.strip().lower()
        character = None

        # Lore handling
        if expression.startswith("lore "):
            lore_query = expression[5:].strip()
            user_data = users.find_one({"user_id": user_id})
            if not user_data or not user_data.get("current_character"):
                await ctx.send("❌ No active character. Use `!setactive` first.")
                return

            pb_id = user_data["current_character"]
            character = characters.find_one({"user_id": user_id, "pb_id": pb_id})
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
            stat_label = f"{lore_name.title()} Lore"

        elif expression in MODIFIER_FIELDS:
            user_data = users.find_one({"user_id": user_id})
            if not user_data or not user_data.get("current_character"):
                await ctx.send("❌ No active character set.")
                return

            pb_id = user_data["current_character"]
            character = characters.find_one({"user_id": user_id, "pb_id": pb_id})
            if not character:
                await ctx.send("❌ Active character not found.")
                return

            mod_field = MODIFIER_FIELDS[expression]
            modifier = get_nested(character, mod_field)
            stat_label = expression.title()
            expression = f"1d20+{modifier}"

        else:
            stat_label = None  # For manual rolls

        # Roll the expression
        try:
            result = d20.roll(expression)
        except d20.RollSyntaxError as e:
            await ctx.send(f"❌ Invalid roll: {e}")
            return

        embed = discord.Embed(
            title=f"🎲 Roll: `{expression}`",
            description=f"**Result:** `{result.total}`",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Details", value=f"`{result.result}`", inline=False)

        if character and stat_label:
            embed.set_footer(text=f"{character['name']}'s {stat_label}")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RollCommand())
