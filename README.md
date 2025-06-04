# PF2e Discord Dice Bot

A Discord bot for Pathfinder 2e character management and dice rolling. Integrates with Pathbuilder 2e for easy character imports.

## Features

- Import characters directly from Pathbuilder 2e
- View detailed character sheets
- Roll dice with character modifiers
- Make weapon attacks with MAP and damage calculations
- Supports skill checks and lore rolls
- Multiple dice rolling formats

## Setup

1. Create a `.env` file with the following variables:
```
DISCORD_TOKEN=your_discord_bot_token
MONGODB_URI=your_mongodb_connection_string
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the bot:
```bash
python bot.py
```

## Commands

### Character Management
- `!import [id]` - Import/update character from Pathbuilder 2e
- `!sheet` - View your character sheet

### Dice Rolling
- `!roll <expression>` - Roll dice with optional modifiers
  - Examples: `!roll 1d20+5`, `!roll perception`, `!roll lore warfare`
- `!rr <times> <expression>` - Repeat a roll multiple times
  - Example: `!rr 3 1d20+5`

### Combat
- `!attack <weapon> [options]` - Make weapon attacks
  - Options:
    - `-n <number>` - Attack number (for MAP)
    - `-d <number>` - Extra damage
    - `-b <number>` - Extra bonus
    - `-ac <number>` - Target AC
    - `crit` - Force critical hit
    - Traits: `agile`, `flurry`, `fatal-<die>`, `deadly-<die>`, `2h-<die>`
  - Example: `!attack shortsword -ac 15 -d 2 agile`

### Help
- `!help` - List all commands
- `!help <command>` - Get detailed help for a specific command

## Requirements

- Python 3.8+
- MongoDB database
- Discord bot token
- Required Python packages (see requirements.txt)

## License

MIT License
