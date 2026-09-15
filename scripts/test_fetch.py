"""Offline ingestion regressions: python -m unittest discover -s scripts."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import fetch


class SpainFetchTests(unittest.TestCase):
    def test_normalizes_ministry_response(self):
        response = Mock()
        response.json.return_value = {"ListaEESSPrecio": [{
            "IDEESS": "123", "Latitud": "40,12", "Longitud (WGS84)": "-3,45",
            "Rótulo": " REPSOL ", "Precio Gasoleo A": "1,499",
        }]}
        with patch.object(fetch.SESSION, "get", return_value=response):
            stations = fetch.fetch_es()
        response.raise_for_status.assert_called_once()
        self.assertEqual(len(stations), 1)
        self.assertEqual(stations[0]["id"], "ES-123")
        self.assertEqual(stations[0]["lat"], 40.12)
        self.assertEqual(stations[0]["lng"], -3.45)
        self.assertEqual(stations[0]["prices"], {"diesel": 1.499})

    def test_bad_responses_fail_without_overwriting_snapshot(self):
        payloads = [None, [], {}, {"ListaEESSPrecio": []},
                    {"ListaEESSPrecio": "invalid"}, {"ListaEESSPrecio": [{}]}]
        for payload in payloads:
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as tmp:
                snapshot = Path(tmp) / "stations-es.json"
                snapshot.write_text("previous snapshot")
                response = Mock()
                response.json.return_value = payload
                with patch.object(fetch.SESSION, "get", return_value=response), \
                     patch.object(fetch, "ROOT", Path(tmp)), \
                     patch.object(fetch.sys, "argv", ["fetch.py", "es"]):
                    self.assertEqual(fetch.main(), 1)
                self.assertEqual(snapshot.read_text(), "previous snapshot")

    def test_network_failure_preserves_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = Path(tmp) / "stations-es.json"
            snapshot.write_text("previous snapshot")
            with patch.object(fetch.SESSION, "get", side_effect=fetch.requests.ConnectionError("reset")), \
                 patch.object(fetch, "ROOT", Path(tmp)), \
                 patch.object(fetch.sys, "argv", ["fetch.py", "es"]):
                self.assertEqual(fetch.main(), 1)
            self.assertEqual(snapshot.read_text(), "previous snapshot")


if __name__ == "__main__":
    unittest.main()
