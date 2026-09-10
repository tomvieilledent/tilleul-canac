from datetime import date, timedelta

import pytest
from django.utils import timezone
from psycopg.types.range import DateRange
from rest_framework.test import APIClient

from bookings.ical import parse_ics
from bookings.models import Booking, ExternalBlock

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


def _payload(**over):
    base = {
        "guest_name": "Jean Test",
        "email": "jean@example.com",
        "phone": "0600000000",
        "check_in": (date.today() + timedelta(days=10)).isoformat(),
        "check_out": (date.today() + timedelta(days=12)).isoformat(),
    }
    base.update(over)
    return base


def test_create_booking_ok(client):
    resp = client.post("/api/bookings", _payload(), format="json")
    assert resp.status_code == 201
    assert Booking.objects.count() == 1
    assert resp.data["status"] == "pending"


def test_overlapping_booking_rejected(client):
    assert client.post("/api/bookings", _payload(), format="json").status_code == 201
    resp = client.post(
        "/api/bookings",
        _payload(
            check_in=(date.today() + timedelta(days=11)).isoformat(),
            check_out=(date.today() + timedelta(days=13)).isoformat(),
        ),
        format="json",
    )
    assert resp.status_code == 409
    assert Booking.objects.count() == 1


def test_booking_clashing_with_external_block_rejected(client):
    ExternalBlock.objects.create(
        uid="abc@booking.com",
        stay=DateRange(
            date.today() + timedelta(days=10), date.today() + timedelta(days=12)
        ),
    )
    resp = client.post("/api/bookings", _payload(), format="json")
    assert resp.status_code == 409


def test_availability_merges_sources(client):
    Booking.objects.create(
        guest_name="A",
        email="a@example.com",
        stay=DateRange(
            date.today() + timedelta(days=5), date.today() + timedelta(days=7)
        ),
        status=Booking.Status.CONFIRMED,
    )
    ExternalBlock.objects.create(
        uid="x@booking.com",
        stay=DateRange(
            date.today() + timedelta(days=7), date.today() + timedelta(days=9)
        ),
    )
    resp = client.get("/api/availability")
    assert resp.status_code == 200
    assert resp.data["booked"] == [
        {
            "start": (date.today() + timedelta(days=5)).isoformat(),
            "end": (date.today() + timedelta(days=9)).isoformat(),
        }
    ]


def test_expired_pending_not_blocking(client):
    b = Booking.objects.create(
        guest_name="A",
        email="a@example.com",
        stay=DateRange(
            date.today() + timedelta(days=5), date.today() + timedelta(days=7)
        ),
    )
    Booking.objects.filter(pk=b.pk).update(
        hold_until=timezone.now() - timedelta(minutes=1)
    )
    resp = client.get("/api/availability")
    assert resp.data["booked"] == []


def test_calendar_ics_lists_confirmed_only(client):
    Booking.objects.create(
        guest_name="A",
        email="a@example.com",
        stay=DateRange(
            date.today() + timedelta(days=5), date.today() + timedelta(days=7)
        ),
        status=Booking.Status.CONFIRMED,
    )
    Booking.objects.create(
        guest_name="B",
        email="b@example.com",
        stay=DateRange(
            date.today() + timedelta(days=20), date.today() + timedelta(days=22)
        ),
        status=Booking.Status.PENDING,
    )
    body = client.get("/api/calendar.ics").content.decode()
    assert body.count("BEGIN:VEVENT") == 1


def test_parse_ics_single_night_defaults_to_next_day():
    ics = (
        "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nBEGIN:VEVENT\r\n"
        "UID:only@booking.com\r\nDTSTART;VALUE=DATE:20260601\r\n"
        "SUMMARY:CLOSED\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n"
    )
    events = parse_ics(ics)
    assert events[0]["start"] == date(2026, 6, 1)
    assert events[0]["end"] == date(2026, 6, 2)
