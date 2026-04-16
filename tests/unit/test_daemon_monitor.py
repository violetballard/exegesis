from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from codex_packet_handoff.tools import daemon_monitor


class DaemonMonitorTests(unittest.TestCase):
    def test_read_log_tail_lines_returns_only_recent_tail(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'big.log'
            lines = [f'line-{idx:04d}' for idx in range(400)]
            path.write_text('\n'.join(lines) + '\n')

            tail = daemon_monitor._read_log_tail_lines(path, max_lines=5, max_bytes=128)

            self.assertEqual(tail, lines[-5:])
            self.assertNotIn(lines[0], tail)

    def test_detailed_conversation_summary_uses_tail_slice(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'fixer.log'
            early = '\n'.join(f'ERROR: stale blocker {idx:06d}' for idx in range(12000))
            tail = '\n'.join(
                [
                    'thinking',
                    '**Applying final gate rerun**',
                    'exec',
                    "/bin/zsh -lc './quality-test.sh' succeeded in 0ms:",
                    '[test] passed',
                ]
            )
            path.write_text(early + '\n' + tail + '\n')

            summary = daemon_monitor._detailed_conversation_summary(path)

            self.assertEqual(summary['phase'], 'Applying final gate rerun')
            self.assertIn('OK', summary['recent'][-1])
            self.assertIn('quality-test.sh', summary['recent'][-1])
            self.assertNotIn('ERROR: stale blocker', summary['blockers'])

    def test_feature_runner_state_skips_log_scan_for_review_waiting_lane(self) -> None:
        with mock.patch.object(
            daemon_monitor,
            '_lane_counts_for',
            return_value={'pending': 0, 'review': 1, 'approved': 0},
        ), mock.patch.object(
            daemon_monitor,
            '_feature_thread_state',
            return_value={},
        ), mock.patch.object(
            daemon_monitor,
            '_latest_feature_runner_log',
            side_effect=AssertionError('should not scan feature logs'),
        ):
            state = daemon_monitor._feature_runner_state('feat-a2ui-contract', {})

        self.assertEqual(state['state'], 'review_wait')
        self.assertIn('reviewer note present', state['summary'])

    def test_feature_runner_state_labels_cloud_direct_exec_sessions(self) -> None:
        with mock.patch.object(
            daemon_monitor,
            '_lane_counts_for',
            return_value={'pending': 0, 'review': 0, 'approved': 0},
        ), mock.patch.object(
            daemon_monitor,
            '_feature_thread_state',
            return_value={
                'feat-a2ui-contract': {
                    'status': 'direct_exec_running',
                    'pid': 12345,
                    'mode': 'cloud_primary',
                    'profile': 'worker_cloud',
                    'log_path': '/tmp/feat-a2ui-contract.log',
                }
            },
        ), mock.patch.object(
            daemon_monitor,
            '_pid_alive',
            return_value=True,
        ):
            state = daemon_monitor._feature_runner_state('feat-a2ui-contract', {})

        self.assertEqual(state['state'], 'direct_exec_running')
        self.assertIn('cloud session', state['summary'])
        self.assertIn('worker_cloud', state['summary'])


if __name__ == '__main__':
    unittest.main()
