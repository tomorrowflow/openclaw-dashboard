"""Data schema validation tests — AC9-AC14.

Validates data.json matches the expected schema produced by refresh.sh.
Static tests — no server needed, just reads data.json.
"""

import json
import os
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(REPO, "data.json")


def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)


@unittest.skipUnless(os.path.exists(DATA_FILE), "data.json not found")
class TestDataSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data()

    def test_ac9_required_top_level_keys(self):
        """AC9: All required top-level keys present."""
        required = [
            "gateway", "totalTokensToday", "totalTokensAllTime", "avgDailyTokens",
            "crons", "sessions", "tokenUsage", "subagentRuns", "dailyChart",
            "skills", "gitLog", "agentConfig",
        ]
        for key in required:
            self.assertIn(key, self.data, f"Missing top-level key: {key}")

    def test_ac10_crons_schema(self):
        """AC10: crons is a list; each item has required fields."""
        crons = self.data["crons"]
        self.assertIsInstance(crons, list)
        for c in crons:
            for field in ("name", "schedule", "lastRun", "nextRun"):
                self.assertIn(field, c, f"Cron missing '{field}': {c.get('name', '?')}")
            # 'status' may be stored as 'lastStatus' or 'enabled'
            self.assertTrue(
                "lastStatus" in c or "status" in c or "enabled" in c,
                f"Cron missing status field: {c.get('name', '?')}"
            )

    def test_ac11_sessions_schema(self):
        """AC11: sessions is a list; each item has key, model, type."""
        sessions = self.data["sessions"]
        self.assertIsInstance(sessions, list)
        for s in sessions:
            self.assertIn("key", s)
            self.assertIn("model", s)
            self.assertIn("type", s)

    def test_ac12_total_tokens_today_is_nonneg_int(self):
        """AC12: totalTokensToday is an int >= 0."""
        tokens = self.data["totalTokensToday"]
        self.assertIsInstance(tokens, int)
        self.assertGreaterEqual(tokens, 0)

    def test_ac13_daily_chart_schema(self):
        """AC13: dailyChart is a list of dicts with date and tokens."""
        chart = self.data["dailyChart"]
        self.assertIsInstance(chart, list)
        self.assertGreater(len(chart), 0, "dailyChart should not be empty")
        for entry in chart:
            self.assertIsInstance(entry, dict)
            self.assertIn("date", entry)
            self.assertIn("tokens", entry)
            self.assertIsInstance(entry["tokens"], int)

    def test_ac14_gateway_status_enum(self):
        """AC14: gateway status is one of: online, offline, unknown."""
        gw = self.data["gateway"]
        if isinstance(gw, dict):
            status = gw.get("status", "unknown")
        else:
            status = gw
        self.assertIn(status, ("online", "offline", "unknown"))


if __name__ == "__main__":
    unittest.main()
