import discord
from discord.ext import commands
from db import characters

class Sheet(commands.Cog):
    @commands.command(name="sheet", help="View your character sheet.")
    async def character_sheet(self, ctx):
        user_id = str(ctx.author.id)

        def striking_multiplier(striking: str):
            return {
                "": 1,
                "striking": 2,
                "greaterStriking": 3,
                "majorStriking": 4
            }.get(striking, 1)

        character = characters.find_one({"user_id": user_id})
        if not character:
            await ctx.send("❌ Character not found. Try re-importing with `!import`.")
            return

        embed = discord.Embed(
            title=f"{character['name']} (Lvl {character['level']})",
            description=f"**{character['ancestry']}** (**{character['heritage']}**)\n"
                        f"**{character['background']}**\n"
                        f"**{character['class']}**",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="General Info",
            value=f"**Size**: {character.get('size', 'Medium')}\n"
                  f"**Languages**: {', '.join(character.get('languages', [])) or 'None'}\n"
                  f"**Key Ability**: {character.get('key_ability', 'None')}\n"
                  f"**HP**: {character.get('hp', '?')}\n"
                  f"**AC**: {character.get('ac', '?')}\n"
                  f"**Speed**: {character.get('speed', '?')} ft\n"
                  f"**Class DC**: {character.get('classDC', '?')}",
            inline=True
        )

        embed.add_field(
            name="Money",
            value=f"**Copper**: {character.get("money").get('cp', 0)}\n"
                  f"**Silver**: {character.get("money").get('sp', 0)}\n"
                  f"**Gold**: {character.get("money").get('gp', 0)}\n"
                  f"**Platinum**: {character.get("money").get('pp', 0)}",
            inline=True
        )

        abilities = character.get("abilities", {})
        embed.add_field(
            name="🧠 Abilities",
            value="\n".join([f"**{k.upper()}**: {v:+.0f}" for k, v in abilities.items()]),
            inline=True
        )

        saves = character.get("saves", {})
        embed.add_field(
            name="🛡️ Saves",
            value="\n".join([
                f"**Fortitude**: {saves.get('fortitude', 0)}",
                f"**Reflex**: {saves.get('reflex', 0)}",
                f"**Will**: {saves.get('will', 0)}",
                f"**Perception**: {character.get('perception', 0)}"
            ]),
            inline=True
        )

        skills = character.get("skills", {})
        lores = character.get("lores", {})
        trained_skills = []
        for skill_name, modifier in skills.items():
            trained_skills.append(f"{skill_name.capitalize()}: {modifier}")

        for lore_name, modifier in lores.items():
            trained_skills.append(f"Lore ({lore_name}): {modifier}")
        
        embed.add_field(
            name="📘 Trained Skills",
            value=", ".join(trained_skills) or "None",
            inline=False
        )

        feats = character.get("feats", [])[:10]
        embed.add_field(
            name="✨ Feats",
            value=", ".join(feats) if feats else "None",
            inline=False
        )

        weapons = character.get("weapons", [])
        embed.add_field(
            name="🗡️ Weapons",
            value="\n".join([f"{w['display']} (Damage: {striking_multiplier(w.get('striking', ''))}{w.get('damage_die', 'N/A')}, Damage Type: {w.get('damage_type', 'N/A')}, Attack Bonus: {w.get('attack_bonus', 0)})" for w in weapons]) if weapons else "None",
            inline=False
        )

        specials = character.get("specials", [])
        embed.add_field(
            name="⚡ Specials",
            value="\n".join(specials) if specials else "None",
            inline=False
        )

        embed.set_footer(text=f"Owned by {ctx.author.display_name}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Sheet())
