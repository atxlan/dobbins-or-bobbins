import discord
import random

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
        self.channel = None
        self.state = 'initialized'
        self.rounds = []
        self.players = []
        self.round = 0
        self.guesses = {}

    def initialize(self, channel):
        self.channel = channel
        self.state = 'herding'
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

    def get_truther(self):
        round = len(self.rounds) - 1
        return self.players[round]

    def next_round(self):
        msgs = []
        if self.round == 0:
            msgs.append('Alright, starting a game with players: {}'.format(' '.join(self.players)))
        msgs.append("You're up, {}. Slide a truth bomb into my DMs! Everyone else, a fib.".format(self.get_truther()))
        self.state = 'awaiting_submissions'
        self.rounds.append({})
        return msgs

    def end_round(self):
        self.round += 1

    def get_round(self):
        return self.rounds[-1]

    def submission(self, author, text):
        if author not in self.players: return [':🚫']

        round = self.get_round()
        round[author] = text
        num_submissions = len(round.keys())
        msgs = [':✅']
        if num_submissions == len(self.players):
            msgs += self.show_submissions()
        return msgs

    def show_submissions(self):
        msgs = []
        self.state = 'awaiting_guesses'
        msg = "Okay, let's get guessing! Is the real answer:\n\n"
        lplayers = self.players[:]
        random.shuffle(lplayers)
        round = self.get_round()
        for i, player in enumerate(lplayers):
            msg += '{}. {}\n'.format(i+1, round[player])
        msg += '\nHit me with a DM or mention with your guess number!'
        msgs.append(msg)
        return msgs

    def guess(self, player, guess):
        if player not in self.players: return [':🚫']

        self.guesses[player] = guess
        msgs = []
        if len(self.guesses) == len(self.players):
            self.state = 'awaiting_nextround'
            msgs += self.finish_round()
        return [':✅'] + msgs

    def finish_round(self):
        msg = "Round complete! Here's the scores:"
        return [msg]

    def __str__(self):
        return '{}: {}'.format(self.state, self.players)

client = discord.Client()
game = Game()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

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
    elif game.instate('herding') and icommand == 'in':
        await handle_response(game.add_player(player))
    elif direct and game.instate('gathering') and icommand == 'ready':
        await handle_response(game.start_game())
    elif direct and game.instate('awaiting_submissions'):
        await handle_response(game.submission(player, icommand))
    elif direct and game.instate('awaiting_guesses'):
        await handle_response(game.guess(player, icommand))

    #TODO: when we have a guess from players - 1, show the results!
    #TODO: 'again!' for another round

if __name__ == "__main__":
    import sys
    token = sys.argv[1]
    client.run(token)
