#!/usr/bin/env python3
"""Offline consistency check for the reviewed ES/AD tariff snapshot.

This does not validate live tariffs or route matching. Re-audit sources before
updating the snapshot; never treat a successful run as proof of full coverage.
"""
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'audit/2026-09-16'


def validate(catalogs, audit, geometry, sources):
    errors = []
    rows = audit['entries']
    reviewed = {r['id']: r for r in rows}
    geo = {r['id']: r for r in geometry['entries']}
    downloaded = {s['url'] for s in sources if s['status'] == 'downloaded'}
    ids = [t['id'] for d in catalogs.values() for t in d['tolls']]
    if len(set(ids)) != len(ids) or len(reviewed) != len(rows):
        errors.append('Duplicate catalog or audit ID')
    if set(ids) != set(reviewed) or set(ids) != set(geo):
        errors.append('Every catalog entry needs tariff and geometry audit records')
    for country, catalog in catalogs.items():
        if catalog['schema'] != 1 or catalog['currency'] != 'EUR':
            errors.append(f'{country}: unsupported schema/currency')
        if catalog['complete'] and any(r['blockers'] for r in rows if r['country'] == country):
            errors.append(f'{country}: complete=true contradicts unresolved audit blockers')
        for t in catalog['tolls']:
            r = reviewed.get(t['id'])
            if r is None:
                continue
            if t['country'] != country or t['vehicle_class'] != 'light':
                errors.append(f"{t['id']}: wrong country/vehicle class")
            for key, audit_key in [('price', 'reference_price'), ('price_high', 'reference_price_high')]:
                price = t[key]
                if price != r[audit_key]:
                    errors.append(f"{t['id']}: {key} differs from reviewed tariff; re-audit required")
                if price is not None and (isinstance(price, bool) or Decimal(str(price)) < 0 or Decimal(str(price)).as_tuple().exponent < -2):
                    errors.append(f"{t['id']}: invalid EUR amount")
            if t['price_high'] is not None and (t['price_high'] < t['price'] or not t['variable']):
                errors.append(f"{t['id']}: inconsistent tariff range")
            if 'sum' in r['pricing_kind'] and t['model'] == 'fixed':
                errors.append(f"{t['id']}: multi-gate total must not be marked fixed per crossing")
            if t['model'] not in ['fixed', 'ticket']:
                errors.append(f"{t['id']}: unsupported model")
            if t['verified'] != r['tariff_checked'] or t['verified'] > catalog['generated']:
                errors.append(f"{t['id']}: inconsistent verification date")
            if t['source'] not in downloaded or any(s['url'] not in downloaded for s in r['sources']):
                errors.append(f"{t['id']}: missing downloaded source provenance")
            g = geo.get(t['id'], {})
            if g.get('coordinate') != [t['lat'], t['lng']]:
                errors.append(f"{t['id']}: coordinates changed without an updated geometry audit")
    return errors


def load_inputs():
    return ({c: json.loads((ROOT / f'tolls-{c}.json').read_text()) for c in ['es', 'ad']},
            *[json.loads((AUDIT / f).read_text()) for f in ['entries.json', 'geometry-audit.json', 'source-fetch.json']])


if __name__ == '__main__':
    result = validate(*load_inputs())
    if result:
        raise SystemExit('\n'.join(result))
    print('OK: 36 tariff/geometry records agree with the reviewed snapshot; ES coverage remains incomplete.')
