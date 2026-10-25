#!/bin/sh
# Rebuild and check the Spanish toll catalog in one go. Graph-free: works from
# the committed candidates and per-area evidence, needs no national OSM extract.
#
#   scripts/tolls/update.sh /path/to/fuelo-app [--refresh-routes] [--export]
#
#   --refresh-routes  re-ask the router for every sweep journey (~2 min, our own
#                     server) instead of replaying the cached responses
#   --export          also copy the app fixtures (then open an app PR too)
#
# Prints PASS/FAIL per step and exits 1 if anything needs review.
set -u
cd "$(dirname "$0")/../.."
APP=${1:?usage: scripts/tolls/update.sh /path/to/fuelo-app [--refresh-routes] [--export]}
shift
REFRESH=0; EXPORT=0
for arg in "$@"; do
  case $arg in --refresh-routes) REFRESH=1 ;; --export) EXPORT=1 ;; *) echo "unknown option $arg"; exit 2 ;; esac
done
[ -d "$APP/node_modules/typescript" ] || { echo "Run npm ci in $APP first"; exit 2; }

FAILED=""
step() { # name, command...
  name=$1; shift
  printf '\n== %s\n' "$name"
  if "$@"; then echo "PASS $name"; else echo "FAIL $name"; FAILED="$FAILED\n  - $name"; fi
}

step "apply AP-6 Adanero terminal" python3 scripts/coverage/build_ap6_adanero_terminal.py
step "apply per-area evidence (coverage, plaza gates)" python3 scripts/coverage/build_area_coverage.py
step "assemble catalog (tolls-es-reviewed.json)" python3 scripts/coverage/build_spain_candidate.py
step "candidate integrity" python3 scripts/coverage/validate_candidates.py
step "tariff and geometry records" python3 scripts/validate_tolls.py
step "unit tests" python3 -m unittest discover -s scripts/coverage/tests
step "tariff validity (none expired or expiring within 60 days)" python3 scripts/tolls/check_validity.py
[ $EXPORT = 1 ] && step "export app fixtures" python3 scripts/coverage/export_app_fixtures.py "$APP"
step "national replay (retained journeys)" node scripts/coverage/audit_spain_integration.cjs "$APP"
step "avoidance replay" node scripts/coverage/audit_general_avoidance.cjs "$APP"
if [ $REFRESH = 1 ]; then
  rm -f pricing-candidates/terminal-sweep/responses/*.json
  step "sweep journeys (generate)" node scripts/coverage/sweep_terminals.cjs generate
  step "sweep journeys (ask the router)" node scripts/coverage/sweep_terminals.cjs fetch
fi
step "terminal sweep (gaps, plaza near misses, price changes)" node scripts/coverage/sweep_terminals.cjs check "$APP"

if [ -z "$FAILED" ]; then
  printf '\nALL PASS. Review the diff of tolls-es-reviewed.json, commit, open a PR; merging publishes it.\n'
else
  printf '\nNEEDS REVIEW:%b\n' "$FAILED"
  printf 'Sweep details: pricing-candidates/terminal-sweep/results.json (GAP lines carry coordinates).\n'
  exit 1
fi
