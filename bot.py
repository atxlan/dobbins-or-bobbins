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
        self.channel = None

    def initialize(self, channel):
        game.state = 'gathering'
        game.channel = channel
        return ["Alright, who's in cowfolks? Can I get an 'In!'?"]

    def instate(self, state):
        return self.state == state

    def add_player(self, author):
        player = author
        if player not in self.players:
            self.players.append(player)
        return [':🐴']

    def start_game(self):
        return self.next_round()

    def next_round(self):
        msgs = []
        print('Starting round!', self.players)
        if self.round == 0:
            msgs.append('Alright, starting a game with players: {}'.format(' '.join(self.players)))
        turn = self.round % len(self.players)
        msgs.append("You're up, {}. Slide a truth bomb into my DMs! Everyone else, a fib.".format(self.players[turn]))
        self.state = 'awaiting_submissions'
        self.rounds.append({})
        return msgs

    def end_round(self):
        self.round += 1

    def submission(self, author, text):
        #print(repr(author), self.players, author in self.players)
        if author not in self.players:
            return [':🚫']
        round = self.rounds[-1]
        round[author] = text
        num_submissions = len(round.keys())
        msgs = [':✅']
        if num_submissions == len(self.players):
            msgs += self.show_submissions()
        return msgs

    def show_submissions(self):
        msgs = []
        self.state = 'awaiting_guesses'
        msgs.append('Here are the submissions!')
        return msgs

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
    player = message.author.name
    print('command (direct? {}): {}'.format(direct, icommand))

    async def handle_response(response):
        if response is not None:
            for msg in response:
                if len(msg) == 2 and msg[0] == ':':
                    await message.add_reaction(msg[1])
                else:
                    await game.channel.send(msg)

    if direct and icommand == 'giddy up':
        await handle_response(game.initialize(message.channel))
    elif game.instate('gathering') and icommand == 'in':
        await handle_response(game.add_player(player))
    elif direct and game.instate('gathering') and icommand == 'ready':
        await handle_response(game.start_game())
    elif direct and game.instate('awaiting_submissions'):
        await handle_response(game.submission(player, icommand))
    elif direct and game.instate('awaiting_guesses'):
        game.guess(player, icommand)

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
