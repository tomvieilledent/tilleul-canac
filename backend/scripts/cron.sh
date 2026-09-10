#!/usr/bin/env bash
# Tâches périodiques de l'API (à câbler dans la crontab du VPS).
#
# Exemple de crontab :
#   17 */3 * * *  /opt/vlldnt/projects/tilleul-canac/backend/scripts/cron.sh sync_ical
#   */10 * * * *  /opt/vlldnt/projects/tilleul-canac/backend/scripts/cron.sh expire_holds
set -euo pipefail

CMD="${1:?usage: cron.sh <sync_ical|expire_holds>}"
COMPOSE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$COMPOSE_DIR"
docker compose -f compose.yml exec -T web python manage.py "$CMD"
