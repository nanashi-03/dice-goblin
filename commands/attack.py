import discord
from discord.ext import commands
from db import characters, users
import d20
import re
from difflib import get_close_matches

STRIKING_DICE = {
    None: 1,
    "striking": 2,
    "greaterStriking": 3,
    "majorStriking": 4
}

DIE_SIZES = ["d4", "d6", "d8", "d10", "d12"]

class Attack(commands.Cog):
    @commands.command(name="attack", aliases=["atk"])
    async def attack(self, ctx, *, args):
        user_id = str(ctx.author.id)
        user = users.find_one({"user_id": user_id})
        if not user or "current_character" not in user:
            await ctx.send("❌ You have no active character. Use `!setactive`.")
            return

        character = characters.find_one({
            "user_id": user_id,
            "pb_id": user["current_character"]
        })
        if not character:
            await ctx.send("❌ Could not find your current character.")
            return

        # Parse input
        match = re.match(r"(?P<name>[^\d]+)\s*(?P<attack_num>[123])?", args)
        if not match:
            await ctx.send("❌ Invalid format. Example: `!attack rapier 1 -b 2 -ac 18 agile`")
            return

        weapon_name = match.group("name").strip()
        attack_number = int(match.group("attack_num") or "1")

        # Flags
        bonus_match = re.findall(r"-b\s*(-?\d+)", args)
        damage_bonus_match = re.findall(r"-d\s*(-?\d+)", args)
        ac_match = re.findall(r"-ac\s*(\d+)", args)
        traits = {
            "agile": "agile" in args,
            "flurry": "flurry" in args,
        }
        for trait in ["fatal", "deadly", "2h"]:
            match_trait = re.findall(rf"{trait}-({'|'.join(DIE_SIZES)})", args)
            traits[trait] = match_trait[0] if match_trait else None

        extra_attack_bonus = int(bonus_match[0]) if bonus_match else 0
        extra_damage_bonus = int(damage_bonus_match[0]) if damage_bonus_match else 0
        target_ac = int(ac_match[0]) if ac_match else None

        # Find the weapon fuzzily
        weapons = character.get("weapons", [])
        weapon_names = [w["name"] for w in weapons]
        close = get_close_matches(weapon_name, weapon_names, n=1)
        if not close:
            await ctx.send("❌ Weapon not found.")
            return

        weapon = next(w for w in weapons if w["name"] == close[0])
        die = traits["2h"] or weapon.get("die", "d6")
        pot = int(weapon.get("pot", 0))
        str_value = weapon.get("str", None)
        striking_dice = STRIKING_DICE.get(str_value, 1)

        # Determine MAP (Multiple Attack Penalty)
        map_penalties = {
            1: 0,
            2: -5,
            3: -10
        }
        penalty = map_penalties[attack_number]
        if traits["agile"]:
            penalty += 1
        if traits["flurry"]:
            penalty += 3
        penalty = min(0, penalty)  # Prevent increasing attack by accident

        # Final attack bonus
        attack_bonus = int(weapon.get("attack", 0)) + pot + extra_attack_bonus + penalty
        attack_roll = d20.roll(f"1d20 + {attack_bonus}")

        embed = discord.Embed(
            title=f"🎯 Attack with {weapon['name']}",
            description=f"**Attack Roll:** {attack_roll}",
            color=discord.Color.orange()
        )

        crit = False
        if target_ac:
            result = attack_roll.total
            if result >= target_ac + 10:
                embed.description += f"\n**Critical Hit!** (vs AC {target_ac})"
                crit = True
            elif result >= target_ac:
                embed.description += f"\n**Hit!** (vs AC {target_ac})"
            else:
                embed.description += f"\n**Miss!** (vs AC {target_ac})"
                await ctx.send(embed=embed)
                return

        # Calculate damage
        base_damage = f"{striking_dice}{die}"
        damage_roll_str = f"{base_damage} + {extra_damage_bonus}" if extra_damage_bonus else base_damage
        damage_roll = d20.roll(damage_roll_str)

        if crit:
            # Fatal overrides dice
            if traits["fatal"]:
                fatal_die = traits["fatal"]
                damage_roll = d20.roll(f"{striking_dice}{fatal_die}")
                damage_roll = d20.roll(f"({damage_roll}) * 2")
            else:
                # Normal crit
                damage_roll = d20.roll(f"({damage_roll}) * 2")
                if traits["deadly"]:
                    deadly_die = traits["deadly"]
                    deadly_roll = d20.roll(deadly_die)
                    damage_roll = d20.roll(f"({damage_roll}) + {deadly_roll}")

        embed.add_field(name="💥 Damage", value=f"`{damage_roll}`", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Attack())
