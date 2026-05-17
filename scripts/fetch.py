#!/usr/bin/env python3
"""
Aggregates fuel-station price data from the public APIs of Spain, France and
Andorra into a single canonical JSON shape, written to the repo root as
`stations-{es,fr,ad}.json`. Designed to run on a GitHub Actions cron every
6 hours; jsDelivr serves the resulting files to the Fuelo mobile app, so the
app makes one fast CDN request per country instead of hitting three different
government APIs from every device.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parent.parent
BRAND_TYPOS: dict[str, str] = {
    k: v
    for k, v in json.loads((ROOT / "brand-typos.json").read_text(encoding="utf-8")).items()
    if not k.startswith("_")
}

# Browser-like UA — some endpoints (notably Spain's Ministry) appear to drop
# connections from obvious bot agents. The +URL stays so server admins can
# trace the traffic.
UA = (
    "Mozilla/5.0 (compatible; fuelo-data/1.0; +https://github.com/getFuelo/fuelo-data)"
)
TIMEOUT = 120


def make_session() -> requests.Session:
    """Session with sensible retries: 4 attempts, exponential backoff, retries on
    connection errors and 5xx responses. The Spain endpoint occasionally resets
    the TCP connection — once usually works after a short wait."""
    s = requests.Session()
    retries = Retry(
        total=4,
        connect=4,
        read=4,
        status=4,
        backoff_factor=2.0,  # 2s, 4s, 8s, 16s
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=4, pool_maxsize=4)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    s.headers.update({"User-Agent": UA})
    return s


SESSION = make_session()


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_decimal_es(s: Any) -> float | None:
    """Spanish Ministry uses comma-decimal floats stored as strings."""
    if not s:
        return None
    try:
        v = float(str(s).replace(",", "."))
    except (TypeError, ValueError):
        return None
    return v if v == v and v != float("inf") and v != float("-inf") else None


def canonicalize_brand(raw: str) -> str:
    """Exact uppercase lookup against BRAND_TYPOS. Unknown brands pass through."""
    trimmed = (raw or "").strip()
    if not trimmed:
        return ""
    upper = trimmed.upper()
    return BRAND_TYPOS.get(upper, trimmed)


def prices_dict(items: dict[str, float | None]) -> dict[str, float]:
    """Drop None entries so the wire format stays compact."""
    return {k: v for k, v in items.items() if v is not None}


# ── Spain (Ministerio para la Transición Ecológica) ──────────────────────────

ES_URL = (
    "https://sedeaplicaciones.minetur.gob.es"
    "/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
)


def fetch_es() -> list[dict[str, Any]]:
    t = time.time()
    res = SESSION.get(ES_URL, timeout=TIMEOUT)
    res.raise_for_status()
    payload = res.json()
    raw = payload.get("ListaEESSPrecio", []) or []
    out: list[dict[str, Any]] = []
    for r in raw:
        lat = parse_decimal_es(r.get("Latitud"))
        lng = parse_decimal_es(r.get("Longitud (WGS84)"))
        if lat is None or lng is None:
            continue
        out.append(
            {
                "id": f"ES-{r.get('IDEESS') or f'{lat},{lng}'}",
                "country": "ES",
                "brand": canonicalize_brand(r.get("Rótulo") or "Sin marca"),
                "address": (r.get("Dirección") or "").strip(),
                "city": (r.get("Localidad") or "").strip(),
                "province": (r.get("Provincia") or "").strip(),
                "schedule": (r.get("Horario") or "").strip(),
                "lat": lat,
                "lng": lng,
                "prices": prices_dict(
                    {
                        "diesel": parse_decimal_es(r.get("Precio Gasoleo A")),
                        "dieselPremium": parse_decimal_es(r.get("Precio Gasoleo Premium")),
                        "gasoline95": parse_decimal_es(r.get("Precio Gasolina 95 E5")),
                        "gasoline98": parse_decimal_es(r.get("Precio Gasolina 98 E5")),
                        "lpg": parse_decimal_es(r.get("Precio Gases licuados del petróleo")),
                    }
                ),
            }
        )
    print(f"[es] {len(out):,} stations in {time.time() - t:.1f}s")
    return out


# ── France (data.economie.gouv.fr) ───────────────────────────────────────────

FR_URL = (
    "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "prix-des-carburants-en-france-flux-instantane-v2/exports/json"
)


def fetch_fr() -> list[dict[str, Any]]:
    t = time.time()
    res = SESSION.get(FR_URL, timeout=TIMEOUT, headers={"Accept": "application/json"})
    res.raise_for_status()
    arr = res.json()
    out: list[dict[str, Any]] = []
    for r in arr:
        geom = r.get("geom") or {}
        lat = geom.get("lat")
        lng = geom.get("lon")
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            continue
        city = (r.get("ville") or "").strip()
        brand = city or "Station"
        # SP95 phased out for E10 — surface E10 as gasoline95 when SP95 missing.
        sp95 = r.get("sp95_prix")
        e10 = r.get("e10_prix")
        gas95 = sp95 if sp95 is not None else (e10 if e10 is not None else None)
        out.append(
            {
                "id": f"FR-{r.get('id') or f'{lat},{lng}'}",
                "country": "FR",
                "brand": brand,
                "address": (r.get("adresse") or "").strip(),
                "city": city,
                "province": (r.get("cp") or "")[:2],
                "schedule": "",
                "lat": float(lat),
                "lng": float(lng),
                "prices": prices_dict(
                    {
                        "diesel": r.get("gazole_prix"),
                        "gasoline95": gas95,
                        "gasoline98": r.get("sp98_prix"),
                        "lpg": r.get("gplc_prix"),
                    }
                ),
            }
        )
    print(f"[fr] {len(out):,} stations in {time.time() - t:.1f}s")
    return out


# ── Andorra (sig.govern.ad ArcGIS FeatureServer) ─────────────────────────────

AD_URL = (
    "https://sig.govern.ad/server/rest/services/CARBURANTS/CARBURANTS/FeatureServer/1/query"
    "?where=1%3D1&outFields=*&f=geojson&returnGeometry=true&outSR=4326"
)

AD_FUEL_MAP = {
    "Gasoil de locomoció": "diesel",
    "Gasoil de locomoció millorat": "dieselPremium",
    "Gasolina sense plom 95 octans": "gasoline95",
    "Gasolina sense plom 98 octans": "gasoline98",
    "GLP": "lpg",
}


def _polygon_centroid(geom: dict[str, Any]) -> tuple[float, float] | None:
    typ = geom.get("type")
    coords = geom.get("coordinates")
    if not coords:
        return None
    if typ == "Polygon":
        ring = coords[0]
    elif typ == "MultiPolygon":
        ring = coords[0][0] if coords and coords[0] else []
    else:
        return None
    sx = sy = 0.0
    n = 0
    for pt in ring:
        if isinstance(pt, list) and len(pt) >= 2:
            sx += pt[0]
            sy += pt[1]
            n += 1
    if n == 0:
        return None
    return sy / n, sx / n  # (lat, lng)


def _title_case(s: str) -> str:
    words = [w for w in s.split() if w]
    out = []
    for w in words:
        out.append(w.upper() if len(w) <= 2 else w[0].upper() + w[1:].lower())
    return " ".join(out)


def fetch_ad() -> list[dict[str, Any]]:
    t = time.time()
    res = SESSION.get(AD_URL, timeout=TIMEOUT)
    res.raise_for_status()
    features = res.json().get("features", []) or []

    # Aggregate by CESI station id, taking the latest price per fuel (max DataFi).
    by_cesi: dict[str, dict[str, Any]] = {}
    for f in features:
        p = f.get("properties") or {}
        cesi = p.get("CESI")
        preu = p.get("PREU")
        if not cesi or preu is None:
            continue
        fuel = AD_FUEL_MAP.get(p.get("Tipus_carburant") or "")
        if not fuel:
            continue
        centroid = _polygon_centroid(f.get("geometry") or {})
        if not centroid:
            continue
        lat, lng = centroid
        acc = by_cesi.get(cesi)
        if not acc:
            acc = {
                "id": cesi,
                "name": (p.get("NOM") or "").strip(),
                "parish": (p.get("Parroquia") or "").strip(),
                "brand_raw": (p.get("Marca_importador") or "").strip() or (p.get("NOM") or "").strip(),
                "lat": lat,
                "lng": lng,
                "prices_by_fuel": {},  # fuel -> (price, dataFi)
            }
            by_cesi[cesi] = acc
        prev = acc["prices_by_fuel"].get(fuel)
        cur_dt = p.get("DataFi") or 0
        if not prev or cur_dt > prev[1]:
            acc["prices_by_fuel"][fuel] = (preu, cur_dt)

    out: list[dict[str, Any]] = []
    for acc in by_cesi.values():
        brand = canonicalize_brand(acc["brand_raw"]) or _title_case(acc["brand_raw"])
        prices = {fuel: price for fuel, (price, _) in acc["prices_by_fuel"].items()}
        out.append(
            {
                "id": f"AD-{acc['id']}",
                "country": "AD",
                "brand": brand,
                "address": "",
                "city": acc["name"],
                "province": acc["parish"],
                "schedule": "",
                "lat": acc["lat"],
                "lng": acc["lng"],
                "prices": prices,
            }
        )
    print(f"[ad] {len(out):,} stations in {time.time() - t:.1f}s")
    return out


# ── Output ───────────────────────────────────────────────────────────────────

def write(country: str, stations: list[dict[str, Any]]) -> None:
    path = ROOT / f"stations-{country}.json"
    # Compact JSON (no indentation) keeps the CDN payload small. The file is
    # read by the mobile app, never by a human.
    path.write_text(
        json.dumps(stations, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    size_kb = path.stat().st_size / 1024
    print(f"      -> {path.name} ({size_kb:,.0f} KB)")


FETCHERS = {"es": fetch_es, "fr": fetch_fr, "ad": fetch_ad}


def main() -> int:
    """CLI: `python scripts/fetch.py [country ...]`. With no args, runs all
    three (useful for local validation). With args, runs only the requested
    countries — used by the per-country GitHub Actions matrix jobs so each
    country has its own visibility, retry, and pass/fail status."""
    countries = [c.lower() for c in sys.argv[1:]] or list(FETCHERS.keys())
    failures: list[str] = []
    for country in countries:
        fetcher = FETCHERS.get(country)
        if not fetcher:
            print(f"[{country}] unknown country (expected one of {list(FETCHERS)})", file=sys.stderr)
            failures.append(country)
            continue
        try:
            write(country, fetcher())
        except Exception as e:  # noqa: BLE001
            print(f"[{country}] FAILED: {e}", file=sys.stderr)
            failures.append(country)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
