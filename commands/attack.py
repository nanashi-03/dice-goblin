import discord
from discord.ext import commands
import d20
from difflib import get_close_matches
import re
from utils.fetch import get_active_character  # You should have a utility for this

def parse_traits(args):
    """Parse weapon traits from command arguments.
    
    Args:
        args (list): List of command arguments
        
    Returns:
        dict: Parsed weapon traits
    """
    traits = {}
    for arg in args:
        if arg.startswith("fatal-"):
            traits["fatal"] = arg.split("-")[1]
        elif arg.startswith("deadly-"):
            traits["deadly"] = arg.split("-")[1]
        elif arg.startswith("2h-"):
            traits["2h"] = arg.split("-")[1]
        elif arg in {"agile", "flurry"}:
            traits[arg] = True
    return traits

def striking_multiplier(striking: str):
    return {
        "": 1,
        "striking": 2,
        "greaterStriking": 3,
        "majorStriking": 4
    }.get(striking, 1)

class Attack(commands.Cog):
    """Commands for handling weapon attacks and damage rolls."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="attack", aliases=["atk", "a"], help="Make an attack with a weapon.\nUsage:\n```!attack <weapon_name> [-n attack_number] [-d <extra_damage>] [-b <extra_bonus>] [-ac <target_ac>] [crit] [modifiers...]```\nAvailable modifiers: agile, flurry, fatal-<die>, deadly-<die>, 2h-<die>")
    async def attack(self, ctx, weapon_name: str, *args):
        character = get_active_character(ctx.author.id) 
     
        if not character:
            return await ctx.send("No character found. Please import your character first using `!import <pathbuilder_id>`.")

        # Optional modifiers
        extra_dmg = 0
        extra_bonus = 0
        target_ac = None
        crit_flag = False
        attack_number = 1
        traits = parse_traits(args)

        for i, arg in enumerate(args):
            try:
                if arg == "-d" and i + 1 < len(args):
                    extra_dmg = int(args[i + 1])
                if arg == "-b" and i + 1 < len(args):
                    extra_bonus = int(args[i + 1])
                if arg == "-ac" and i + 1 < len(args):
                    target_ac = int(args[i + 1])
                if arg == "-n" and i + 1 < len(args):
                    attack_number = int(args[i + 1])
                if arg.lower() == "crit":
                    crit_flag = True
            except ValueError:
                await ctx.send(f"❌ Invalid argument: {arg}. Please provide valid integers for modifiers.")
                return

        weapons = character.get("weapons", [])
        weapon_names = [w["name"] for w in weapons]
        close = get_close_matches(weapon_name, weapon_names, n=1)
        if not close:
            await ctx.send("❌ Weapon not found.")
            return
        
        weapon = next(w for w in weapons if w["name"] == close[0])

        # Determine MAP
        if traits.get("agile") and traits.get("flurry"):
            map_penalty = {1: 0, 2: -1, 3: -2}.get(attack_number, 0)
        elif traits.get("flurry"):
            map_penalty = {1: 0, 2: -2, 3: -4}.get(attack_number, 0)
        elif traits.get("agile"):
            map_penalty = {1: 0, 2: -4, 3: -8}.get(attack_number, 0)
        else:
            map_penalty = {1: 0, 2: -5, 3: -10}.get(attack_number, 0)
        
        if map_penalty is None:
            map_penalty = 0

        # Calculate attack bonus
        attack_bonus = weapon["attack_bonus"] + weapon.get("potency", 0) + extra_bonus + map_penalty

        # Roll attack
        attack_roll = d20.roll(f"1d20 + {attack_bonus}")
        attack_result = attack_roll.total

        # Determine hit/miss if AC is given
        hit_type = "N/A"
        if crit_flag:
            hit_type = "Critical Hit"
        elif target_ac is not None:
            if attack_result >= target_ac + 10:
                hit_type = "Critical Hit"
            elif attack_result >= target_ac:
                hit_type = "Hit"
            elif attack_result <= target_ac - 10:
                hit_type = "Critical Miss"
            else:
                hit_type = "Miss"

        # Determine damage die size
        damage_die = traits.get("2h", weapon["damage_die"])
        striking = weapon.get("striking", "")
        num_dice = striking_multiplier(striking)

        damage_expr = f"{num_dice}{damage_die} + {weapon.get('damage_bonus', 0) + extra_dmg}"
        if hit_type == "Critical Hit":
            if "fatal" in traits:
                damage_expr = f"{num_dice}{traits['fatal']} * 2 + {weapon.get('damage_bonus', 0) + extra_dmg}"
            else:
                damage_expr = f"({damage_expr}) * 2"
            if "deadly" in traits:
                damage_expr += f" + 1{traits['deadly']}"

        if hit_type in ["Hit", "Critical Hit", "N/A"]:
            damage_roll = d20.roll(damage_expr)
            damage = damage_roll.total
        else:
            damage = None

        # Build response embed
        embed = discord.Embed(title=f"🎯 Attack Roll: {weapon['display']}", color=discord.Color.green())
        embed.add_field(name="🎲 Roll", value=f"{attack_roll}", inline=False)
        if target_ac:
            embed.add_field(name="🎯 Target AC", value=target_ac, inline=True)
            embed.add_field(name="✅ Result", value=hit_type, inline=True)
        if damage is not None:
            embed.add_field(name="💥 Damage", value=f"{damage_roll}", inline=False)
        else:
            embed.add_field(name="💥 Damage", value="Missed!", inline=False)

        await ctx.send(embed=embed)

    @attack.error
    async def attack_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required arguments. Usage: `!attack <weapon_name> [-n attack_number] [-d <extra_damage>] [-b <extra_bonus>] [-ac <target_ac>] [crit] [traits...]`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument type. Please check your inputs.")
        else:
            await ctx.send(f"❌ An unexpected error occurred: {error}")

async def setup(bot):
    await bot.add_cog(Attack(bot))
