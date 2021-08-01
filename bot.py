import discord

client = discord.Client()

def commands_from_mention(content):
    try:
        return content[content.find('>')+2:].split()
    except:
        return None

def lower(lst):
    if isinstance(lst, str):
        lst = [lst]
    return [s.lower().strip('!.,') for s in lst]

class Game:
    def __init__(self):
        self.state = 'initialized'
        self.rounds = []
        self.players = []
        self.round = 0

    def add_player(self, author):
        player = author.name
        if player not in self.players:
            self.players.append(player)

    def start_game(self):
        self.state = 'playing'
        return self.next_round()

    def next_round(self):
        msgs = []
        print('Starting round!', self.players)
        if self.round == 0:
            msgs.append('Alright, starting a game with players: {}'.format(' '.join(self.players)))
        turn = self.round % len(self.players)
        msgs.append("You're up, {}. Slide a truth bomb into my DMs! Everyone else, a fib.".format(self.players[turn]))
        return msgs

    def end_round(self):
        self.round += 1


    def __str__(self):
        return '{}: {}'.format(self.state, self.players)

game = Game()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print('BEFORE:')
    print(game)

    if client.user.mentioned_in(message):
        print('Mention from {}!'.format(message.author))
        commands = commands_from_mention(message.content)
        if lower(commands) == ['giddy', 'up']:
            await message.channel.send("Alright, who's in cowfolks? Can I get an 'In!'?")
            game.state = 'gathering'
        elif game.state == 'gathering' and lower(commands) == ['in']:
            game.add_player(message.author)
            await message.add_reaction('🐴')
        elif game.state == 'gathering' and lower(commands) == ['ready']:
            for msg in game.start_game():
                await message.channel.send(msg)
        #TODO: handle DMs of submissions: truth or fibs depending on turn
        #TODO: when we have a submission from all players, shuffle and display
        #TODO: accept guesses as DMs or spoiler mentions
        #TODO: when we have a guess from players - 1, show the results!
        #TODO: 'again!' for another round

    print('AFTER:')
    print(game)

if __name__ == "__main__":
    import sys
    token = sys.argv[1]
    client.run(token)
