import discord
from collections import defaultdict
import random
import os

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
        self.state = 'unstarted'

    def initialize(self, channel):
        self.channel = channel
        self.state = 'herding'
        self.rounds = []
        self.players = []
        self.order = []
        self.guesses = {}
        self.scores = defaultdict(int)
        return ["Alright, who's in cowfolks? Can I get an 'In!'?"]

    def instate(self, state):
        return self.state == state

    def add_player(self, author):
        player = author
        if player not in self.players:
            self.players.append(player)
        return [':🐴']

    def get_round(self):
        return self.rounds[-1]

    def get_truther(self):
        round = len(self.rounds) - 1
        return self.players[round]

    def next_round(self):
        self.guesses = {}
        msgs = []
        if len(self.rounds) == 0:
            msgs.append('Alright, starting a game with players: {}'.format(' '.join(self.players)))
        self.rounds.append({})
        msgs.append("You're up, {}. Slide a truth bomb into my DMs! Everyone else, a fib.".format(self.get_truther()))
        self.state = 'awaiting_submissions'
        return msgs

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
        self.order = list(range(len(self.players)))
        random.shuffle(self.order)
        round = self.get_round()
        for i, x in enumerate(self.order):
            msg += '{}. {}\n'.format(i+1, round[self.players[x]])
        msg += '\nHit me with a DM or mention with your guess number!'
        msgs.append(msg)
        return msgs

    def guess(self, player, guess):
        if player not in self.players or player == self.get_truther(): return [':🚫']

        try:
            guess = int(guess)
        except ValueError:
            return [':😱']

        self.guesses[player] = guess - 1
        msgs = []
        if len(self.guesses) == len(self.players) - 1:
            self.state = 'awaiting_nextround'
            msgs += self.finish_round()
        return [':✅'] + msgs

    def finish_round(self):
        truther = self.get_truther()
        real = self.get_round()[truther]
        #print('===', truther, real, self.players, self.order)
        msg = "The real answer was '{}'!".format(real)
        real_guess = False
        for player, guess in self.guesses.items():
            owner = self.players[self.order[guess]]
            #print('===', player, guess+1, owner)
            if owner == truther:
                msg += "\n* {} correctly guessed {} (+1 for {})".format(player, guess+1, player)
                self.scores[player] += 1
                real_guess = True
            else:
                msg += "\n* {} guessed {} (+1 to {})".format(player, guess+1, owner)
                self.scores[owner] += 1
        if not real_guess:
            msg += "\n* {} fooled everyone with {}, +1 for them!".format(truther, real)
            self.scores[truther] += 1

        msg += "\n\nCurrent totals:"
        for player, total in sorted(self.scores.items(), key=lambda x: -x[1]):
            msg += '\n* {}: {}'.format(player, total)

        msg += "\n"
        return [msg]

    def __str__(self):
        status = 'In state "{}" with players {}'.format(self.state, self.players)
        if self.state != 'unstarted':
            status += '\nIn Round #{}. Submissions from {}, guesses from {}'.format(len(self.rounds), list(self.get_round().keys()), list(self.guesses.keys()))
        return status

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

    if direct and icommand == 'pedigree please':
        await message.channel.send(os.getenv('GIT_COMMIT'))
    elif direct and icommand == 'what\'s your damage':
        await message.channel.send(str(game))
    elif direct and icommand == 'giddy up':
        await handle_response(game.initialize(message.channel))
    elif game.instate('herding') and icommand == 'in':
        await handle_response(game.add_player(player))
    elif direct and game.instate('herding') and icommand == 'ready':
        await handle_response(game.next_round())
    elif direct and game.instate('awaiting_submissions'):
        await handle_response(game.submission(player, command))
    elif direct and game.instate('awaiting_guesses'):
        await handle_response(game.guess(player, icommand))
    elif direct and game.instate('awaiting_nextround') and icommand == 'again':
        await handle_response(game.next_round())

if __name__ == "__main__":
    import os
    import sys
    if os.getenv('DISCORD_TOKEN'):
        token = os.getenv('DISCORD_TOKEN')
    else:
        token = sys.argv[1]
    client.run(token)
