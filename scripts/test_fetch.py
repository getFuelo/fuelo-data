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


FIXED_NOW = fetch.datetime(2026, 10, 10, 7, 15, 0, tzinfo=fetch.timezone.utc)


def _response(payload):
    response = Mock()
    response.json.return_value = payload
    return response


class SourceDateTests(unittest.TestCase):
    """Every station carries when the official source published the snapshot
    (`sourceUpdatedAt`, ISO UTC): Spain's licence requires showing it, and the
    app's freshness label must reflect the data, not the download."""

    def _es(self, payload_extra):
        payload = {"ListaEESSPrecio": [{
            "IDEESS": "1", "Latitud": "40,1", "Longitud (WGS84)": "-3,4", "Precio Gasoleo A": "1,5",
        }], **payload_extra}
        with patch.object(fetch.SESSION, "get", return_value=_response(payload)), \
             patch.object(fetch, "now_utc", return_value=FIXED_NOW):
            return fetch.fetch_es()

    def test_spain_uses_the_ministry_fecha_in_madrid_time(self):
        self.assertEqual(self._es({"Fecha": "10/10/2026 9:13:41"})[0]["sourceUpdatedAt"], "2026-10-10T07:13:41Z")
        self.assertEqual(self._es({"Fecha": "10/01/2026 9:13:41"})[0]["sourceUpdatedAt"], "2026-01-10T08:13:41Z")

    def test_spain_without_a_usable_fecha_falls_back_to_the_fetch_time(self):
        for extra in ({}, {"Fecha": ""}, {"Fecha": "ayer"}):
            with self.subTest(extra=extra):
                self.assertEqual(self._es(extra)[0]["sourceUpdatedAt"], "2026-10-10T07:15:00Z")

    def _fr(self, meta):
        record = {"id": 7, "geom": {"lat": 48.8, "lon": 2.3}, "ville": "Paris", "gazole_prix": 1.7}

        def get(url, **kwargs):
            if url == fetch.FR_URL:
                return _response([record])
            if meta is None:
                raise fetch.requests.ConnectionError("down")
            return _response(meta)

        with patch.object(fetch.SESSION, "get", side_effect=get), \
             patch.object(fetch, "now_utc", return_value=FIXED_NOW):
            return fetch.fetch_fr()

    def test_france_uses_the_dataset_processing_date(self):
        meta = {"metas": {"default": {"data_processed": "2026-10-10T07:04:41.510000+00:00"}}}
        self.assertEqual(self._fr(meta)[0]["sourceUpdatedAt"], "2026-10-10T07:04:41Z")

    def test_france_without_metadata_falls_back_to_the_fetch_time(self):
        for meta in (None, {}, {"metas": {"default": {"data_processed": "nope"}}}):
            with self.subTest(meta=meta):
                self.assertEqual(self._fr(meta)[0]["sourceUpdatedAt"], "2026-10-10T07:15:00Z")

    def test_andorra_and_portugal_use_the_fetch_time(self):
        ad = {"features": [{
            "properties": {"CESI": "C1", "PREU": 1.3, "Tipus_carburant": "GLP", "NOM": "X", "DataFi": 1},
            "geometry": {"type": "Polygon", "coordinates": [[[1.5, 42.5], [1.6, 42.5], [1.6, 42.6]]]},
        }]}
        pt_page = {"resultado": [{"Id": 9, "Combustivel": "GPL Auto", "Preco": "0,9 €", "Latitude": 38.7, "Longitude": -9.1}]}
        pt_pages = [pt_page, {"resultado": []}]
        with patch.object(fetch.SESSION, "get", return_value=_response(ad)), \
             patch.object(fetch, "now_utc", return_value=FIXED_NOW):
            self.assertEqual(fetch.fetch_ad()[0]["sourceUpdatedAt"], "2026-10-10T07:15:00Z")
        with patch.object(fetch.SESSION, "get", side_effect=[_response(p) for p in pt_pages]), \
             patch.object(fetch, "now_utc", return_value=FIXED_NOW):
            self.assertEqual(fetch.fetch_pt()[0]["sourceUpdatedAt"], "2026-10-10T07:15:00Z")


if __name__ == "__main__":
    unittest.main()
