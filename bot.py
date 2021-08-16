from collections import defaultdict
import random
import os
import sys
from typing import List

from discord.ext import commands
from discord.ext.commands.errors import CheckFailure


class Game:
    def __init__(self):
        self.state = 'unstarted'
        self.players = []

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
        return ['🐴']

    def get_round(self):
        return self.rounds[-1]

    def get_truther(self):
        round = len(self.rounds) - 1
        return self.players[round]

    def next_round(self) -> List[str]:
        self.guesses = {}
        msgs = []
        if len(self.rounds) == 0:
            msgs.append('Alright, starting a game with players: {}'.format(' '.join(self.players)))
        self.rounds.append({})
        msgs.append("You're up, {}. Slide a truth bomb into my DMs! Everyone else, a fib.".format(self.get_truther()))
        self.state = 'awaiting_submissions'
        return msgs

    def submission(self, author, text) -> List[str]:
        if author not in self.players:
            return ['🚫']

        round = self.get_round()
        round[author] = text
        num_submissions = len(round.keys())
        msgs = ['✅']
        if num_submissions == len(self.players):
            msgs += self.show_submissions()
        return msgs

    def show_submissions(self) -> List[str]:
        msgs = []
        self.state = 'awaiting_guesses'
        msg = "Okay, let's get guessing! Is the real answer:\n\n"
        self.order = list(range(len(self.players)))
        random.shuffle(self.order)
        round = self.get_round()
        for i, x in enumerate(self.order):
            msg += '{}. {}\n'.format(i + 1, round[self.players[x]])
        msg += '\nHit me with a DM or mention with your guess number!'
        msgs.append(msg)
        return msgs

    def guess(self, player, guess):
        if player not in self.players or player == self.get_truther():
            return ['🚫']

        try:
            guess = int(guess)
        except ValueError:
            return ['😱']

        self.guesses[player] = guess - 1
        msgs = []
        if len(self.guesses) == len(self.players) - 1:
            self.state = 'awaiting_nextround'
            msgs += self.finish_round()
        return ['✅'] + msgs

    def finish_round(self):
        truther = self.get_truther()
        real = self.get_round()[truther]
        # print('===', truther, real, self.players, self.order)
        msg = "The real answer was '{}'!".format(real)
        real_guess = False
        for player, guess in self.guesses.items():
            owner = self.players[self.order[guess]]
            # print('===', player, guess+1, owner)
            if owner == truther:
                msg += "\n* {} correctly guessed {} (+1 for {})".format(player, guess + 1, player)
                self.scores[player] += 1
                real_guess = True
            else:
                msg += "\n* {} guessed {} (+1 to {})".format(player, guess + 1, owner)
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
            status += '\nIn Round #{}. Submissions from {}, guesses from {}'.format(
                len(self.rounds), list(self.get_round().keys()), list(self.guesses.keys())
            )
        return status


def in_state(state):
    def predicate(ctx: commands.Context):
        if not state == ctx.cog.game.state:
            return CheckFailure(f'Neigh! Game state {ctx.game.state} not in required state: {state}')
        return True

    return commands.check(predicate)


class GameCog(commands.Cog):
    def __init__(self, bot, game):  # pylint: disable=redefined-outer-name
        self.bot = bot
        self.game = game

    @commands.command(name='giddyup', aliases=['giddy'])
    async def new_game(self, ctx, *args):  # pylint: disable=unused-argument
        await ctx.send(self.game.initialize(ctx.channel)[0])

    @commands.command(name='pedigree')
    async def show_pedigree(self, ctx, *args):  # pylint: disable=unused-argument
        if os.getenv('GIT_COMMIT') is None:
            await ctx.send('Neigh! No git commit found.')
        else:
            await ctx.send(os.getenv('GIT_COMMIT'))

    @commands.command(name='damage', aliases=['whats'])
    async def damage(self, ctx, *args):  # pylint: disable=unused-argument
        await ctx.send(str(self.game))

    @commands.command(name='in', aliases=['in!'])
    @in_state('herding')
    async def add_player(self, ctx, *args):  # pylint: disable=unused-argument):
        if self.game.add_player(ctx.author.name):
            await ctx.message.add_reaction('🐴')

    @in_state('herding')
    @commands.command(name='ready')
    async def ready(self, ctx):
        await ctx.send('\n'.join(map(str, self.game.next_round())))

    @in_state('awaiting_nextround')
    @commands.command(name='again')
    async def next_round(self, ctx):
        await ctx.send('\n'.join(map(str, self.game.next_round())))

    @commands.Cog.listener("on_message")
    async def add_submission(self, message):
        check = self.game.state == 'awaiting_submissions'
        if message.guild is None and check:
            await message.add_reaction(self.game.submission(message.author.name, message.content)[0])

    @commands.Cog.listener("on_message")
    async def add_guess(self, message):
        if message.guild is None and self.game.state == 'awaiting_guesses':
            reply: List = self.game.guess(message.author.name, message.content)

            if len(reply) == 1:
                await message.add_reaction(reply[0])
            else:
                await message.channel.send('\n'.join(map(str, reply)))


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self))


bot = Bot(command_prefix='🐴')
game = Game()
bot.add_cog(GameCog(bot, game))

if __name__ == "__main__":
    if os.getenv('DISCORD_TOKEN'):
        token = os.getenv('DISCORD_TOKEN')
    else:
        token = sys.argv[1]
    bot.run(token)
