import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
PATCHER = ROOT / "scripts" / "patch-dashboard-picker.py"


class DashboardPatchTest(unittest.TestCase):
    def test_progress_rows_keep_their_projected_aggregate_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            reader = Path(directory) / "reader.py"
            reader.write_text(
                "PICKER_CANONICAL_LINK_ID_SQL = 'legacy'\n"
                "def _fetch_latest_progress_rows():\n"
                "    sql = (\n"
                "        'SELECT aggregate_id, ' \n"
                "        f\"{PICKER_CANONICAL_LINK_ID_SQL} AS link_id, \"\n"
                "    )\n"
                "    return sql\n"
                "\n"
                "def list_recent_executions():\n"
                "    return None\n",
                encoding="utf-8",
            )

            subprocess.run([sys.executable, str(PATCHER), "--reader", str(reader)], check=True)
            subprocess.run(
                [sys.executable, str(PATCHER), "--reader", str(reader), "--check"], check=True
            )

            source = reader.read_text(encoding="utf-8")
            self.assertIn('"aggregate_id AS link_id, "', source)
            self.assertNotIn('f"{PICKER_CANONICAL_LINK_ID_SQL} AS link_id, "', source)


if __name__ == "__main__":
    unittest.main()
