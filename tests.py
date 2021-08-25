import random
import unittest

from bot import Game, GameState


class TestGame(unittest.TestCase):
    def test_initial_state(self):
        g = Game()
        self.assertTrue(g.instate(GameState.UNSTARTED))
        self.assertEqual(str(g), 'In state "GameState.UNSTARTED" with players []')

    def test_giddy_up(self):
        g = Game()
        msgs = g.initialize("#")
        self.assertTrue(g.instate(GameState.HERDING), g.state)
        self.assertEqual(len(msgs), 1)
        state_string = 'In state "GameState.HERDING" with players []'
        self.assertEqual(str(g), state_string)

    def test_add_players(self):
        g = Game()
        g.initialize("#")

        self.assertEqual(g.players, [])
        msgs = g.add_player("fakeandy")
        self.assertEqual(msgs, [":🐴"])
        self.assertEqual(g.players, ["fakeandy"])
        self.assertEqual(str(g), "In state \"GameState.HERDING\" with players ['fakeandy']")
        # Ensure we don't get a dupe
        g.add_player("fakeandy")
        self.assertEqual(g.players, ["fakeandy"])
        g.add_player("roonbaob")
        self.assertEqual(g.players, ["fakeandy", "roonbaob"])
        self.assertEqual(str(g), "In state \"GameState.HERDING\" with players ['fakeandy', 'roonbaob']")

    def test_ready_up(self):
        g = Game()
        g.initialize("#")
        g.add_player("fakeandy")
        g.next_round()

        self.assertTrue(g.instate(GameState.AWAITING_SUBMISSIONS))
        self.assertTrue(g.get_truther(), "fakeandy")
        state_string = """In state "GameState.AWAITING_SUBMISSIONS" with players [\'fakeandy\']
In Round #1. Submissions from [], guesses from []"""
        self.assertEqual(str(g), state_string)

    def test_submissions(self):
        g = Game()
        g.initialize("#")
        g.add_player("roonbaob")
        g.add_player("fakeandy")
        g.next_round()

        self.assertTrue(g.get_truther(), "roonbaob")
        msgs = g.submission("fakeandy", "gokarts")
        self.assertTrue(g.instate(GameState.AWAITING_SUBMISSIONS))
        self.assertEqual(msgs, [":✅"])

        msgs = g.submission("unaddedplayer", "fakeout")
        self.assertTrue(g.instate(GameState.AWAITING_SUBMISSIONS))
        self.assertEqual(msgs, [":🚫"])

        msgs = g.submission("roonbaob", "chocolate")
        self.assertTrue(g.instate(GameState.AWAITING_GUESSES))
        self.assertEqual(msgs[0], ":✅")
        self.assertEqual(len(msgs), 2)

        state_string = """In state "GameState.AWAITING_GUESSES" with players [\'roonbaob\', \'fakeandy\']
In Round #1. Submissions from [\'fakeandy\', \'roonbaob\'], guesses from []"""
        self.assertEqual(str(g), state_string)

    def test_guesses(self):
        random.seed(9007)
        g = Game()
        g.initialize("#")
        g.add_player("fakeandy")
        g.add_player("roonbaob")
        g.add_player("tater")
        msgs = g.next_round()
        self.assertIn("You're up, fakeandy", msgs[1])
        g.submission("fakeandy", "gokarts")
        g.submission("tater", "bofa deez nuts")
        msgs = g.submission("roonbaob", "Chocolate")
        # print(msgs[1])

        msgs = g.guess("nonplayer", "1")
        self.assertEqual(msgs, [":🚫"])
        self.assertTrue(g.instate(GameState.AWAITING_GUESSES))

        # Ensure a submitter can't guess.
        self.assertEqual(g.get_truther(), "fakeandy")
        msgs = g.guess("fakeandy", "1")
        self.assertEqual(msgs, [":🚫"])
        self.assertTrue(g.instate(GameState.AWAITING_GUESSES))

        # Ensure a non-int is handled gracefully.
        msgs = g.guess("roonbaob", "2x")
        self.assertEqual(msgs[0], ":😱")

        msgs = g.guess("tater", "3")
        self.assertEqual(msgs, [":✅"])

        state_string = """In state "GameState.AWAITING_GUESSES" with players ['fakeandy', 'roonbaob', 'tater']
In Round #1. Submissions from ['fakeandy', 'tater', 'roonbaob'], guesses from ['tater']"""
        self.assertEqual(str(g), state_string)

        msgs = g.guess("roonbaob", "1")
        self.assertEqual(msgs[0], ":✅")
        self.assertEqual(len(msgs), 2)
        # print(msgs[1])
        self.assertTrue(g.instate(GameState.AWAITING_NEXTROUND))

        self.assertEqual(len(g.guesses), 2)
        g.next_round()
        self.assertEqual(len(g.guesses), 0)


if __name__ == "__main__":
    unittest.main()
