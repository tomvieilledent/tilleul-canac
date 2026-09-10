# API réservation — Le Tilleul de Canac

Django 5 + DRF + PostgreSQL. Système de réservation d'une chambre d'hôtes avec
synchronisation iCal bidirectionnelle avec Booking.com.

## Endpoints

| Méthode | Chemin | Rôle |
|---------|--------|------|
| `GET`  | `/api/availability?from=&to=` | plages occupées fusionnées (résas site + blocs Booking) |
| `POST` | `/api/bookings` | crée une réservation `pending` (bloquée 30 min) |
| `GET`  | `/api/calendar.ics` | flux iCal des résas confirmées → à importer dans l'extranet Booking |
| `GET`  | `/api/healthz` | sonde |
| —      | `/admin/` | validation manuelle des réservations |

## Anti-doublon

Contrainte d'exclusion PostgreSQL (`btree_gist`) sur `Booking` (statuts actifs) et
`ExternalBlock`. Toute création qui chevauche une période occupée renvoie `409`.

## Dév local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # DEBUG=true, DATABASE_URL vers un Postgres local
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
pytest                        # nécessite un PostgreSQL accessible
```

## Conteneurs

```bash
cp .env.example .env          # renseigner les secrets
docker compose up --build
```

`web` applique les migrations au démarrage puis lance gunicorn sur `:8000`
(exposé en loopback `127.0.0.1:${PORT}`).

## Tâches périodiques

`scripts/cron.sh sync_ical` (toutes les ~3 h) et `scripts/cron.sh expire_holds`
(toutes les ~10 min), à déclarer dans la crontab du VPS.
