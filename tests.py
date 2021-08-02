import random
import unittest

from bot import Game

class TestGame(unittest.TestCase):

    def test_initial_state(self):
        g = Game()
        self.assertTrue(g.instate('unstarted'))
        self.assertEqual(str(g), 'In state "unstarted" with players []')

    def test_giddy_up(self):
        g = Game()
        msgs = g.initialize('#')
        self.assertTrue(g.instate('herding'), g.state)
        self.assertEqual(len(msgs), 1)

    def test_add_players(self):
        g = Game()
        g.initialize('#')

        self.assertEqual(g.players, [])
        msgs = g.add_player('fakeandy')
        self.assertEqual(msgs, [':🐴'])
        self.assertEqual(g.players, ['fakeandy'])
        # Ensure we don't get a dupe
        g.add_player('fakeandy')
        self.assertEqual(g.players, ['fakeandy'])
        g.add_player('roonbaob')
        self.assertEqual(g.players, ['fakeandy', 'roonbaob'])

    def test_ready_up(self):
        g = Game()
        g.initialize('#')
        g.add_player('fakeandy')
        g.next_round()

        self.assertTrue(g.instate('awaiting_submissions'))
        self.assertTrue(g.get_truther(), 'fakeandy')

    def test_submissions(self):
        g = Game()
        g.initialize('#')
        g.add_player('roonbaob')
        g.add_player('fakeandy')
        g.next_round()

        self.assertTrue(g.get_truther(), 'roonbaob')
        msgs = g.submission('fakeandy', 'gokarts')
        self.assertTrue(g.instate('awaiting_submissions'))
        self.assertEqual(msgs, [':✅'])

        msgs = g.submission('unaddedplayer', 'fakeout')
        self.assertTrue(g.instate('awaiting_submissions'))
        self.assertEqual(msgs, [':🚫'])

        msgs = g.submission('roonbaob', 'chocolate')
        self.assertTrue(g.instate('awaiting_guesses'))
        self.assertEqual(msgs[0], ':✅')
        self.assertEqual(len(msgs), 2)

    def test_guesses(self):
        random.seed(9007)
        g = Game()
        g.initialize('#')
        g.add_player('fakeandy')
        g.add_player('roonbaob')
        g.add_player('tater')
        msgs = g.next_round()
        self.assertIn("You're up, fakeandy", msgs[1])
        g.submission('fakeandy', 'gokarts')
        g.submission('tater', 'bofa deez nuts')
        msgs = g.submission('roonbaob', 'Chocolate')
        #print(msgs[1])

        msgs = g.guess('nonplayer', '1')
        self.assertEqual(msgs, [':🚫'])
        self.assertTrue(g.instate('awaiting_guesses'))

        # Ensure a submitter can't guess.
        self.assertEqual(g.get_truther(), 'fakeandy')
        msgs = g.guess('fakeandy', '1')
        self.assertEqual(msgs, [':🚫'])
        self.assertTrue(g.instate('awaiting_guesses'))

        # Ensure a non-int is handled gracefully.
        msgs = g.guess('roonbaob', '2x')
        self.assertEqual(msgs[0], ':😱')

        msgs = g.guess('tater', '3')
        self.assertEqual(msgs, [':✅'])
        msgs = g.guess('roonbaob', '1')
        self.assertEqual(msgs[0], ':✅')
        self.assertEqual(len(msgs), 2)
        #print(msgs[1])
        self.assertTrue(g.instate('awaiting_nextround'))

        self.assertEqual(len(g.guesses), 2)
        g.next_round()
        self.assertEqual(len(g.guesses), 0)



if __name__ == '__main__':
    unittest.main()
