import unittest
from policy_view import render_rule


class RuleViewTests(unittest.TestCase):
    def test_distinct_observed_value(self):
        self.assertEqual(render_rule("trap", "drop"), {
            "configured_action": "trap", "observed_action": "drop", "reason": None})

    def test_unknown_is_not_configured(self):
        self.assertEqual(render_rule("trap", None, "read failed"), {
            "configured_action": "trap", "observed_action": "unknown", "reason": "read failed"})

    def test_missing_observation_is_unknown(self):
        self.assertEqual(render_rule("drop", None), {
            "configured_action": "drop", "observed_action": "unknown", "reason": None})


if __name__ == "__main__":
    unittest.main()
