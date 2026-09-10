from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import Booking


class Command(BaseCommand):
    help = "Annule les réservations 'pending' dont le blocage a expiré."

    def handle(self, *args, **options):
        stale = Booking.objects.filter(
            status=Booking.Status.PENDING, hold_until__lt=timezone.now()
        )
        count = stale.update(status=Booking.Status.CANCELLED)
        self.stdout.write(f"Réservations expirées annulées : {count}.")
