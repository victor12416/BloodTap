import random
import unittest

from simulator import (
    State,
    calendar_drop_failure_factor,
    calendar_omen_spawn_factor,
    calendar_switch_cost,
    next_omen_wait,
    switch_calendar,
    update_calendar,
)


class CalendarBoundaryTests(unittest.TestCase):
    def test_locked_invalid_and_unaffordable_switches_do_not_mutate(self):
        state=State(bank=10**20)
        before=(state.bank,state.calendar_state,state.calendar_switches)
        self.assertFalse(switch_calendar(state,0))
        self.assertEqual(before,(state.bank,state.calendar_state,state.calendar_switches))

        state.calendar_unlocked=True
        for invalid in (-1,5,True,1.5,"0"):
            self.assertFalse(switch_calendar(state,invalid))
        state.bank=calendar_switch_cost(state)-1
        self.assertFalse(switch_calendar(state,0))
        self.assertEqual(state.calendar_switches,0)

    def test_ascension_unlock_still_enables_calendar(self):
        state=State(bank=10**20,ascension_upgrades={"U181"})
        self.assertTrue(switch_calendar(state,4))
        self.assertEqual(state.calendar_until,86400)

    def test_communion_slot_scales_preserved_calendar_factors(self):
        state=State(calendar_state=0,oath_slots=[-1,4,-1])
        self.assertAlmostEqual(calendar_omen_spawn_factor(state),.9775)
        self.assertAlmostEqual(calendar_drop_failure_factor(state),.925)
        state.calendar_state=2
        self.assertAlmostEqual(calendar_omen_spawn_factor(state),.96625)
        self.assertEqual(calendar_drop_failure_factor(state),1.0)

    def test_calendar_factor_composes_with_omen_wait(self):
        plain=State(calendar_state=-1)
        active=State(calendar_state=0,oath_slots=[4,-1,-1])
        plain_wait=next_omen_wait(plain,random.Random(17))
        active_wait=next_omen_wait(active,random.Random(17))
        self.assertAlmostEqual(active_wait,plain_wait*.97)

    def test_expiry_and_eternal_mode(self):
        state=State(calendar_state=0,calendar_until=10,elapsed=10)
        update_calendar(state)
        self.assertEqual((state.calendar_state,state.calendar_until),(-1,0.0))

        eternal=State(calendar_state=0,calendar_until=1,elapsed=999,
                      eternal_calendar_enabled=True)
        update_calendar(eternal)
        self.assertEqual((eternal.calendar_state,eternal.calendar_until),(0,1))


if __name__=="__main__":
    unittest.main()
