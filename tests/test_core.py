import unittest

import core


class TestCore(unittest.TestCase):
    def test_01_no_duplicate(self):
        state = core.new_game()
        self.assertTrue(core.add(state, 1, 10))
        self.assertFalse(core.add(state, 1, 20))

    def test_02_capacity(self):
        state = core.new_game()
        state["load"] = 2
        self.assertFalse(core.receive(state, 1))

    def test_03_fee_exact(self):
        state = core.new_game()
        self.assertEqual(core.fee(state, 1, 3), 4)

    def test_04_cancel_refunds(self):
        state = core.new_game()
        core.add(state, 1, 5)
        core.cancel(state, 1)
        self.assertEqual(state["stock"], 100)

    def test_05_no_produce_on_fault(self):
        state = core.new_game()
        state["fault"] = True
        self.assertFalse(core.produce(state, 5))

    def test_06_event_once(self):
        state = core.new_game()
        core.event(state)
        self.assertEqual(state["metric"], 90)

    def test_07_no_guard_without_resource(self):
        state = core.new_game()
        state["resource"] = 0
        self.assertFalse(core.guard(state, 1))

    def test_08_pause_stops_clock(self):
        state = core.new_game()
        state["paused"] = True
        core.tick(state)
        self.assertEqual(state["clock"], 0)

    def test_09_settle_blocks_operations(self):
        state = core.new_game()
        core.settle(state)
        self.assertFalse(core.add(state, 1, 10))

    def test_10_load_preserves_id(self):
        state = core.new_game()
        state["id"] = 4
        loaded = core.load_state(core.save_state(state))
        self.assertEqual(loaded["id"], 4)


if __name__ == "__main__":
    unittest.main()
