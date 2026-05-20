from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path

from packet_garden.tools.log_maintenance import compact_log_file, prune_log_dir


class LogMaintenanceTests(unittest.TestCase):
    def test_compact_log_file_keeps_tail_and_adds_banner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "daemon.log"
            path.write_text("header\n" + ("x" * 4096) + "\nTAIL\n", encoding="utf-8")

            result = compact_log_file(path, max_bytes=1024, keep_bytes=256)

            text = path.read_text(encoding="utf-8")
            self.assertEqual(result["compacted"], 1)
            self.assertLess(result["after_bytes"], result["before_bytes"])
            self.assertIn("log compacted at", text)
            self.assertIn("TAIL", text)

    def test_prune_log_dir_removes_only_stale_old_logs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            now = time.time()
            paths = []
            for idx in range(5):
                path = log_dir / f"log-{idx}.log"
                path.write_text(f"log-{idx}\n" + ("a" * 512), encoding="utf-8")
                age = 7200 - (idx * 60)
                os.utime(path, (now - age, now - age))
                paths.append(path)

            fresh = log_dir / "fresh.log"
            fresh.write_text("fresh\n" + ("b" * 512), encoding="utf-8")
            os.utime(fresh, (now - 60, now - 60))

            result = prune_log_dir(
                log_dir,
                keep_recent=2,
                max_total_bytes=1400,
                min_age_seconds=1800,
            )

            remaining = {p.name for p in log_dir.glob("*.log")}
            self.assertGreaterEqual(result["removed"], 1)
            self.assertIn("fresh.log", remaining)
            self.assertLessEqual(len(remaining), 3)


if __name__ == "__main__":
    unittest.main()
