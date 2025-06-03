import discord
from discord.ext import commands

class Help(commands.Cog):
    """A custom help command that shows command usage and examples."""
    
    def __init__(self, bot):
        self.bot = bot
        # Remove default help
        bot.remove_command('help')

    @commands.command(name="help", aliases=["h"])
    async def help(self, ctx, command_name: str = None):
        """Show help for all commands or specific command details.
        
        Args:
            command_name (str, optional): Specific command to get help for.
        """
        if command_name:
            command = self.bot.get_command(command_name)
            if not command:
                await ctx.send(f"❌ Command '{command_name}' not found.")
                return
            
            embed = discord.Embed(
                title=f"Help: {command.name}",
                description=command.help or "No description available.",
                color=discord.Color.blue()
            )
            
            if command.aliases:
                embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
            
            # Command-specific examples
            examples = {
                "import": "!import 123456\n!import",
                "sheet": "!sheet",
                "roll": "!roll 1d20+5\n!roll perception\n!roll lore warfare",
                "repeatroll": "!rr 2 1d20+5",
                "attack": "!attack shortsword\n!attack greatsword -ac 15 -d 2\n!attack rapier -n 2 agile\n!attack dagger -b 2 "
            }
            
            if command.name in examples:
                embed.add_field(name="Examples", value=f"```{examples[command.name]}```", inline=False)
            
        else:
            embed = discord.Embed(
                title="PF2e Discord Bot Commands",
                description="Use `!help <command>` for detailed information about a command.",
                color=discord.Color.blue()
            )
            
            # Group commands by category
            categories = {
                "Character Management": ["import", "sheet"],
                "Dice & Combat": ["roll", "repeatroll", "attack"],
            }
            
            for category, cmds in categories.items():
                # Get all commands in this category
                value = []
                for cmd_name in cmds:
                    cmd = self.bot.get_command(cmd_name)
                    if cmd:
                        value.append(f"`!{cmd.name}` - {cmd.help.split('.')[0]}")
                
                if value:
                    embed.add_field(
                        name=category,
                        value="\n".join(value),
                        inline=False
                    )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
