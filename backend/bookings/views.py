from datetime import date

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from psycopg.types.range import DateRange
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .ical import build_ics, merge_ranges
from .models import Booking, ExternalBlock
from .serializers import BookingCreateSerializer, BookingSerializer


def _active_bookings():
    now = timezone.now()
    return Booking.objects.filter(
        Q(status=Booking.Status.CONFIRMED)
        | Q(status=Booking.Status.PENDING, hold_until__gt=now)
    )


def _busy_ranges(date_from=None, date_to=None):
    rows = []
    for qs in (_active_bookings(), ExternalBlock.objects.all()):
        for obj in qs.only("stay"):
            lo, hi = obj.stay.lower, obj.stay.upper
            if date_from and hi <= date_from:
                continue
            if date_to and lo >= date_to:
                continue
            rows.append((lo, hi))
    return [
        {"start": lo.isoformat(), "end": hi.isoformat()} for lo, hi in merge_ranges(rows)
    ]


@api_view(["GET"])
def availability(request):
    def parse(name):
        raw = request.GET.get(name)
        return date.fromisoformat(raw) if raw else None

    try:
        date_from, date_to = parse("from"), parse("to")
    except ValueError:
        return Response(
            {"detail": "Paramètres 'from'/'to' attendus au format AAAA-MM-JJ."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {"updated": timezone.now().isoformat(), "booked": _busy_ranges(date_from, date_to)}
    )


@api_view(["POST"])
def create_booking(request):
    if not settings.BOOKINGS_ENABLED:
        return Response(
            {"detail": "Réservations désactivées pour le moment."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    serializer = BookingCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    stay = DateRange(data["check_in"], data["check_out"], bounds="[)")

    unavailable = Response(
        {"detail": "Ces dates ne sont plus disponibles."},
        status=status.HTTP_409_CONFLICT,
    )

    # La contrainte d'exclusion ne couvre pas le croisement inter-tables :
    # on teste explicitement les blocages externes.
    if ExternalBlock.objects.filter(stay__overlap=stay).exists():
        return unavailable

    try:
        with transaction.atomic():
            booking = Booking.objects.create(
                guest_name=data["guest_name"],
                email=data["email"],
                phone=data.get("phone", ""),
                stay=stay,
            )
    except IntegrityError:
        return unavailable

    return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)


def calendar_ics(request):
    bookings = Booking.objects.filter(status=Booking.Status.CONFIRMED).order_by("stay")
    response = HttpResponse(
        build_ics(bookings), content_type="text/calendar; charset=utf-8"
    )
    response["Content-Disposition"] = 'inline; filename="tilleul-canac.ics"'
    response["Cache-Control"] = "public, max-age=900"
    return response


def healthz(request):
    return JsonResponse({"status": "ok"})
