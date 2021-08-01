import discord

client = discord.Client()

def command_from_message(content):
    try:
        pos = content.find('>')
        return content if pos == -1 else content[pos+2:]
    except:
        return None

def lower(msg):
    return msg.lower().strip('#!., \n\r')

class Game:
    def __init__(self):
        self.state = 'initialized'
        self.rounds = []
        self.players = []
        self.round = 0

    def instate(self, state):
        return self.state == state

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

    direct = str(message.channel.type) == 'private' or client.user.mentioned_in(message)
    command = command_from_message(message.content)
    icommand = lower(command)
    print('command (direct? {}): {}'.format(direct, icommand))

    if direct and icommand == 'giddy up':
        await message.channel.send("Alright, who's in cowfolks? Can I get an 'In!'?")
        game.state = 'gathering'
    elif game.instate('gathering') and icommand == 'in':
        game.add_player(message.author)
        await message.add_reaction('🐴')
    elif direct and game.instate('gathering') and icommand == 'ready':
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
