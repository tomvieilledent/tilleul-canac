import uuid

import django.contrib.postgres.fields.ranges
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators
from django.contrib.postgres.operations import BtreeGistExtension
from django.db import migrations, models

import bookings.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        BtreeGistExtension(),
        migrations.CreateModel(
            name="Booking",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("guest_name", models.CharField(max_length=120, verbose_name="nom")),
                ("email", models.EmailField(max_length=254)),
                (
                    "phone",
                    models.CharField(blank=True, max_length=40, verbose_name="téléphone"),
                ),
                (
                    "stay",
                    django.contrib.postgres.fields.ranges.DateRangeField(
                        help_text="Nuits réservées, borne de fin exclusive (jour du départ).",
                        verbose_name="séjour",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "En attente"),
                            ("confirmed", "Confirmée"),
                            ("cancelled", "Annulée"),
                        ],
                        default="pending",
                        max_length=10,
                        verbose_name="statut",
                    ),
                ),
                (
                    "hold_until",
                    models.DateTimeField(
                        default=bookings.models.default_hold_until,
                        verbose_name="bloqué jusqu'à",
                    ),
                ),
                (
                    "stripe_payment_intent_id",
                    models.CharField(blank=True, max_length=255),
                ),
                (
                    "amount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=8,
                        null=True,
                        verbose_name="montant",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="créée le"),
                ),
            ],
            options={
                "verbose_name": "réservation",
                "verbose_name_plural": "réservations",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="ExternalBlock",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        choices=[("booking.com", "Booking.com")],
                        default="booking.com",
                        max_length=32,
                    ),
                ),
                ("uid", models.CharField(max_length=255)),
                (
                    "stay",
                    django.contrib.postgres.fields.ranges.DateRangeField(
                        verbose_name="période"
                    ),
                ),
                (
                    "summary",
                    models.CharField(blank=True, max_length=255, verbose_name="libellé"),
                ),
                (
                    "synced_at",
                    models.DateTimeField(auto_now=True, verbose_name="synchronisé le"),
                ),
            ],
            options={
                "verbose_name": "blocage externe",
                "verbose_name_plural": "blocages externes",
                "ordering": ("-synced_at",),
            },
        ),
        migrations.AddConstraint(
            model_name="booking",
            constraint=ExclusionConstraint(
                condition=models.Q(("status__in", ("pending", "confirmed"))),
                expressions=[("stay", RangeOperators.OVERLAPS)],
                name="booking_no_overlap",
            ),
        ),
        migrations.AddConstraint(
            model_name="externalblock",
            constraint=models.UniqueConstraint(
                fields=("source", "uid"), name="externalblock_uid_unique"
            ),
        ),
        migrations.AddConstraint(
            model_name="externalblock",
            constraint=ExclusionConstraint(
                expressions=[("stay", RangeOperators.OVERLAPS)],
                name="externalblock_no_overlap",
            ),
        ),
    ]
