"""Announcement regressions: python -m unittest discover -s scripts."""

import unittest

from announce_release import announce

BASE = {
    "_comment": "policy",
    "minimum_version": "0.0.0",
    "latest_version": "1.2.0",
    "update_url": None,
    "message_es": "m",
    "soft_update_message_es": "s",
}
URL = "https://appdistribution.firebase.google.com/testerapps/app/releases/abc"


class AnnounceTests(unittest.TestCase):
    def test_updates_version_and_link_only(self):
        out = announce(BASE, "1.5.0", URL)
        self.assertEqual(out["latest_version"], "1.5.0")
        self.assertEqual(out["update_url"], URL)
        untouched = {k: v for k, v in BASE.items() if k not in ("latest_version", "update_url")}
        self.assertEqual({k: out[k] for k in untouched}, untouched)
        self.assertEqual(list(out), list(BASE))  # key order kept for a clean diff

    def test_never_touches_minimum_version(self):
        self.assertEqual(announce(BASE, "2.0.0", URL)["minimum_version"], "0.0.0")

    def test_rejects_downgrade_and_reannouncement(self):
        for version in ("1.1.9", "1.2.0"):
            with self.assertRaises(ValueError):
                announce(BASE, version, URL)

    def test_compares_numerically_not_lexically(self):
        cfg = {**BASE, "latest_version": "1.9.0"}
        self.assertEqual(announce(cfg, "1.10.0", URL)["latest_version"], "1.10.0")

    def test_rejects_malformed_version(self):
        for version in ("1.5", "v1.5.0", "1.5.0-beta", ""):
            with self.assertRaises(ValueError):
                announce(BASE, version, URL)

    def test_requires_https_link(self):
        for url in ("", "http://example.com", "firebase://x"):
            with self.assertRaises(ValueError):
                announce(BASE, "1.5.0", url)

    def test_first_announcement_without_previous_version(self):
        cfg = {k: v for k, v in BASE.items() if k != "latest_version"}
        self.assertEqual(announce(cfg, "1.0.0", URL)["latest_version"], "1.0.0")

    def test_does_not_mutate_input(self):
        announce(BASE, "1.5.0", URL)
        self.assertEqual(BASE["latest_version"], "1.2.0")


if __name__ == "__main__":
    unittest.main()
