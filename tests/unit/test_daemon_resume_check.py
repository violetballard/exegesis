from __future__ import annotations

import unittest


class DaemonResumeCheckTests(unittest.TestCase):
    def test_resume_state_waiting_without_new_epoch(self) -> None:
        from packet_garden.tools import daemon_resume_check as resume_check

        previous = {
            "current_resume_epoch": "epoch-1",
            "last_cycle_at": "2026-04-16T22:10:17Z",
            "live_cycle_count": 3,
        }
        current = {
            "current_resume_epoch": "epoch-1",
            "last_cycle_at": "2026-04-16T22:10:17Z",
            "live_cycle_count": 0,
        }

        self.assertEqual(resume_check._resume_state(previous, current), "waiting")

    def test_resume_state_started_with_new_epoch_before_cycle_end(self) -> None:
        from packet_garden.tools import daemon_resume_check as resume_check

        previous = {
            "current_resume_epoch": "epoch-1",
            "last_cycle_at": "2026-04-16T22:10:17Z",
            "live_cycle_count": 4,
        }
        current = {
            "current_resume_epoch": "epoch-2",
            "resume_epoch_started_at": "2026-04-16T22:20:00Z",
            "last_cycle_at": "2026-04-16T22:20:00Z",
            "live_cycle_count": 0,
        }

        self.assertEqual(resume_check._resume_state(previous, current), "started")

    def test_resume_state_completed_with_new_epoch_and_cycle_count(self) -> None:
        from packet_garden.tools import daemon_resume_check as resume_check

        previous = {
            "current_resume_epoch": "epoch-1",
            "last_cycle_at": "2026-04-16T22:10:17Z",
            "live_cycle_count": 4,
        }
        current = {
            "current_resume_epoch": "epoch-2",
            "resume_epoch_started_at": "2026-04-16T22:20:00Z",
            "last_cycle_at": "2026-04-16T22:20:18Z",
            "live_cycle_count": 1,
        }

        self.assertEqual(resume_check._resume_state(previous, current), "completed")


if __name__ == "__main__":
    unittest.main()
