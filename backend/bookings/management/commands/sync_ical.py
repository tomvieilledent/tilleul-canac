import os

import requests
from django.core.management.base import BaseCommand
from psycopg.types.range import DateRange

from bookings.ical import parse_ics
from bookings.models import ExternalBlock

USER_AGENT = "tilleul-de-canac-site/1.0"


class Command(BaseCommand):
    help = "Importe l'agenda iCal Booking.com dans ExternalBlock."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            default=os.environ.get("BOOKING_ICAL_URL"),
            help="URL du flux iCal (défaut : variable d'env BOOKING_ICAL_URL).",
        )

    def handle(self, *args, **options):
        url = options["url"]
        if not url:
            self.stderr.write("BOOKING_ICAL_URL manquant — rien à faire.")
            return

        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        resp.raise_for_status()
        events = parse_ics(resp.text)

        seen, created, updated = set(), 0, 0
        for ev in events:
            if not ev["uid"] or ev["end"] <= ev["start"]:
                continue
            seen.add(ev["uid"])
            _, is_new = ExternalBlock.objects.update_or_create(
                source=ExternalBlock.Source.BOOKING,
                uid=ev["uid"],
                defaults={
                    "stay": DateRange(ev["start"], ev["end"], bounds="[)"),
                    "summary": ev["summary"][:255],
                },
            )
            created += int(is_new)
            updated += int(not is_new)

        stale = ExternalBlock.objects.filter(
            source=ExternalBlock.Source.BOOKING
        ).exclude(uid__in=seen)
        removed = stale.count()
        stale.delete()

        self.stdout.write(
            f"iCal Booking : +{created} créé(s), {updated} maj, -{removed} supprimé(s)."
        )
