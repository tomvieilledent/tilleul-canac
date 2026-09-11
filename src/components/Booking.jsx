import { useState } from "react";
import { useApp } from "../app/store.jsx";
import { useAvailability } from "../hooks/useAvailability.js";
import { BOOKING_URL } from "../lib/site.js";
import BookingForm from "./BookingForm.jsx";
import {
  toDate, startOfToday, sameDay, isBooked, monthGrid,
  weekdayNames, monthLabel, longDate, dateTime,
} from "../lib/calendar.js";

const MONTHS_TO_SHOW = 2;

function toWeeks(cells) {
  const weeks = [];
  for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7));
  return weeks;
}

function Month({ year, month, ranges, today, locale, t, weekdays }) {
  const label = monthLabel(locale, year, month);
  return (
    <table className="cal-table">
      <caption>{label}</caption>
      <thead>
        <tr>
          {weekdays.map((d) => (
            <th key={d} scope="col">{d}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {toWeeks(monthGrid(year, month)).map((week, wi) => (
          <tr key={wi}>
            {week.map((day, di) => {
              if (!day) return <td key={di} className="cal-day is-empty" aria-hidden="true" />;
              const past = day < today;
              const booked = !past && isBooked(day, ranges);
              const state = past ? "" : booked ? t("booking.dayBooked") : t("booking.dayFree");
              const cls =
                "cal-day" +
                (past ? " is-past" : booked ? " is-booked" : " is-free") +
                (sameDay(day, today) ? " is-today" : "");
              return (
                <td
                  key={di}
                  className={cls}
                  aria-label={state ? `${longDate(locale, day)} — ${state}` : longDate(locale, day)}
                  aria-current={sameDay(day, today) ? "date" : undefined}
                >
                  <span aria-hidden="true">{day.getDate()}</span>
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function Booking() {
  const { t, locale } = useApp();
  const [refreshKey, setRefreshKey] = useState(0);
  const { data, error } = useAvailability(refreshKey);

  const today = startOfToday();
  const ranges = (data?.booked || []).map((r) => ({ start: toDate(r.start), end: toDate(r.end) }));
  const bookingUrl = data?.bookingUrl || BOOKING_URL;
  const weekdays = weekdayNames(locale);

  const months = [];
  const cursor = new Date(today.getFullYear(), today.getMonth(), 1);
  for (let i = 0; i < MONTHS_TO_SHOW; i++) {
    months.push({ year: cursor.getFullYear(), month: cursor.getMonth() });
    cursor.setMonth(cursor.getMonth() + 1);
  }

  const updated =
    data?.updated && !Number.isNaN(new Date(data.updated).valueOf())
      ? dateTime(locale, new Date(data.updated))
      : null;

  return (
    <section id="reservation" className="section section-alt" aria-labelledby="reservation-title">
      <div className="container">
        <p className="eyebrow">{t("booking.eyebrow")}</p>
        <h2 id="reservation-title">{t("booking.title")}</h2>
        <p className="section-intro">{t("booking.intro")}</p>

        <div className="booking-block">
          <div className="calendar">
            {error ? (
              <p className="calendar-error" role="status">
                {t("booking.error")}{" "}
                <a href={bookingUrl} target="_blank" rel="noopener noreferrer">Booking.com</a>
              </p>
            ) : !data ? (
              <p className="calendar-loading" role="status">{t("booking.loading")}</p>
            ) : (
              <div className="calendar-months">
                {months.map((m) => (
                  <Month
                    key={`${m.year}-${m.month}`}
                    {...m}
                    ranges={ranges}
                    today={today}
                    locale={locale}
                    t={t}
                    weekdays={weekdays}
                  />
                ))}
              </div>
            )}
          </div>

          <aside className="booking-cta" aria-label={t("booking.reserveTitle")}>
            <h3>{t("booking.reserveTitle")}</h3>
            <p>{t("booking.reserveText")}</p>
            <a className="btn btn-block" href={bookingUrl} target="_blank" rel="noopener noreferrer">
              {t("booking.reserveBtn")}
            </a>
            <p className="booking-legend">
              <span className="swatch swatch-free" aria-hidden="true" /> {t("booking.legendFree")}
              <span className="swatch swatch-booked" aria-hidden="true" /> {t("booking.legendBooked")}
            </p>
            {updated && <p className="booking-updated">{t("booking.updated")} {updated}</p>}

            <BookingForm onBooked={() => setRefreshKey((k) => k + 1)} />
          </aside>
        </div>
      </div>
    </section>
  );
}
