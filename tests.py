import unittest

from bot import Game

class TestGame(unittest.TestCase):

    def test_initial_state(self):
        g = Game()
        self.assertTrue(g.instate('initialized'))

    def test_giddy_up(self):
        g = Game()
        msgs = g.initialize('#')
        self.assertTrue(g.instate('herding'), g.state)
        self.assertEqual(len(msgs), 1)

    def test_add_players(self):
        g = Game()
        g.initialize('#')

        self.assertEqual(g.players, [])
        g.add_player('fakeandy')
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
        g.start_game()

        self.assertTrue(g.instate('awaiting_submissions'))

    def test_submission(self):
        g = Game()
        g.initialize('#')
        g.add_player('fakeandy')
        g.add_player('roonbaob')
        g.start_game()

        msgs = g.submission('fakeandy', 'gokart')
        self.assertTrue(g.instate('awaiting_submissions'))
        self.assertEqual(msgs, [':✅'])

        msgs = g.submission('unaddedplayer', 'fakeout')
        self.assertTrue(g.instate('awaiting_submissions'))
        self.assertEqual(msgs, [':🚫'])

        msgs = g.submission('roonbaob', 'pathofexile')
        self.assertTrue(g.instate('awaiting_guesses'))
        self.assertEqual(msgs[0], ':✅')
        self.assertEqual(len(msgs), 2)
        print(msgs[1])

if __name__ == '__main__':
    unittest.main()
