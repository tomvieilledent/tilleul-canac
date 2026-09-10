"""Génération et lecture de flux iCal (RFC 5545) pour la synchro Booking.com."""
from datetime import date, datetime, timedelta

from icalendar import Calendar, Event

PRODID = "-//Le Tilleul de Canac//Reservations//FR"
CALNAME = "Le Tilleul de Canac"


def _as_date(value):
    if isinstance(value, datetime):
        return value.date()
    return value


def build_ics(bookings):
    """VCALENDAR avec un VEVENT par réservation confirmée."""
    cal = Calendar()
    cal.add("prodid", PRODID)
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    cal.add("x-wr-calname", CALNAME)

    for b in bookings:
        ev = Event()
        ev.add("uid", f"{b.id}@tilleul-canac.vlldnt.fr")
        ev.add("dtstamp", b.created_at)
        ev.add("dtstart", b.stay.lower)
        ev.add("dtend", b.stay.upper)
        ev.add("summary", "Réservé (site)")
        ev.add("transp", "OPAQUE")
        cal.add_component(ev)

    return cal.to_ical()


def parse_ics(text):
    """Liste de dicts {uid, start: date, end: date, summary}. Fin exclusive."""
    cal = Calendar.from_ical(text)
    out = []
    for comp in cal.walk("vevent"):
        raw_start = comp.get("dtstart")
        if raw_start is None:
            continue
        start = _as_date(raw_start.dt)

        raw_end = comp.get("dtend")
        end = _as_date(raw_end.dt) if raw_end is not None else start + timedelta(days=1)

        out.append(
            {
                "uid": str(comp.get("uid") or ""),
                "start": start,
                "end": end,
                "summary": str(comp.get("summary") or ""),
            }
        )
    return out


def merge_ranges(ranges):
    """Fusionne des couples (start, end) triés/chevauchants/contigus."""
    ordered = sorted(ranges)
    merged = []
    for lo, hi in ordered:
        if merged and lo <= merged[-1][1]:
            if hi > merged[-1][1]:
                merged[-1][1] = hi
        else:
            merged.append([lo, hi])
    return [(lo, hi) for lo, hi in merged]
