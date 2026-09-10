import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateRangeField, RangeOperators
from django.db import models
from django.utils import timezone


def default_hold_until():
    return timezone.now() + timedelta(minutes=settings.BOOKING_HOLD_MINUTES)


class Booking(models.Model):
    """Réservation prise depuis le site."""

    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        CONFIRMED = "confirmed", "Confirmée"
        CANCELLED = "cancelled", "Annulée"

    ACTIVE_STATUSES = (Status.PENDING, Status.CONFIRMED)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guest_name = models.CharField("nom", max_length=120)
    email = models.EmailField()
    phone = models.CharField("téléphone", max_length=40, blank=True)
    stay = DateRangeField(
        "séjour", help_text="Nuits réservées, borne de fin exclusive (jour du départ)."
    )
    status = models.CharField(
        "statut", max_length=10, choices=Status.choices, default=Status.PENDING
    )
    hold_until = models.DateTimeField("bloqué jusqu'à", default=default_hold_until)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(
        "montant", max_digits=8, decimal_places=2, null=True, blank=True
    )
    created_at = models.DateTimeField("créée le", auto_now_add=True)

    class Meta:
        verbose_name = "réservation"
        verbose_name_plural = "réservations"
        ordering = ("-created_at",)
        constraints = [
            ExclusionConstraint(
                name="booking_no_overlap",
                expressions=[("stay", RangeOperators.OVERLAPS)],
                condition=models.Q(status__in=("pending", "confirmed")),
            ),
        ]

    def __str__(self):
        return f"{self.guest_name} — {self.stay.lower}→{self.stay.upper} ({self.status})"


class ExternalBlock(models.Model):
    """Période importée depuis un calendrier externe (Booking.com…)."""

    class Source(models.TextChoices):
        BOOKING = "booking.com", "Booking.com"

    source = models.CharField(max_length=32, choices=Source.choices, default=Source.BOOKING)
    uid = models.CharField(max_length=255)
    stay = DateRangeField("période")
    summary = models.CharField("libellé", max_length=255, blank=True)
    synced_at = models.DateTimeField("synchronisé le", auto_now=True)

    class Meta:
        verbose_name = "blocage externe"
        verbose_name_plural = "blocages externes"
        ordering = ("-synced_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("source", "uid"), name="externalblock_uid_unique"
            ),
            ExclusionConstraint(
                name="externalblock_no_overlap",
                expressions=[("stay", RangeOperators.OVERLAPS)],
            ),
        ]

    def __str__(self):
        return f"{self.source} — {self.stay.lower}→{self.stay.upper}"
