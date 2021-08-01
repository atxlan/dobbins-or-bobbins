### Usage:

1. pip install -r requirements.txt
1. python3 bot.py DISCORD_BOT_TOKEN

### Gameplay:

All commands are case-insensitive, with trailing punctuation and spacing ignored. They must be DMs or mentions, unless otherwise noted.

1. Begin a new game: `@bot giddy up!`. The bot will prompt for users.
1. `@bot in!` or simply `in!` from each player who wants to play. The bot will acknowledge each one with a reaction.
1. `@bot ready!` will tell the bot to begin the first round with the players in so far.
1. The bot will announce which player is submitting a "truth." Each player can now DM their submissions to the bot as appropriate. If you send multiple messages, the last one will be used.
1. Once a submission from each player has been received, the bot will present the choices in a random order.
1. Now, DM or mention your guess number (`@bot 2!`)
1. Once all guesses are received, the bot displays the results and current scores.
1. Use `@bot again!` for another round or `@bot giddy up!` to start over.
