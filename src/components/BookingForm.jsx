import { useState } from "react";
import { useApp } from "../app/store.jsx";
import { API_URL } from "../lib/site.js";

const EMPTY_FORM = { guest_name: "", email: "", phone: "", check_in: "", check_out: "" };

export default function BookingForm({ onBooked }) {
  const { t } = useApp();
  const [form, setForm] = useState(EMPTY_FORM);
  const [state, setState] = useState({ status: "idle", message: "" });

  // Pas d'API déployée -> pas de formulaire (le calendrier reste en lecture seule).
  if (!API_URL) return null;

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setState({ status: "sending", message: "" });
    try {
      const res = await fetch(`${API_URL}/api/bookings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (res.status === 201) {
        setState({ status: "done", message: t("booking.form.success") });
        setForm(EMPTY_FORM);
        onBooked?.();
        return;
      }
      if (res.status === 409) {
        setState({ status: "conflict", message: t("booking.form.conflict") });
        return;
      }
      const body = await res.json().catch(() => null);
      setState({
        status: "error",
        message: body?.detail || t("booking.form.error"),
      });
    } catch {
      setState({ status: "error", message: t("booking.form.error") });
    }
  };

  const sending = state.status === "sending";

  return (
    <form className="booking-form" onSubmit={onSubmit}>
      <p className="booking-form-divider" aria-hidden="true">
        {t("booking.form.orDivider")}
      </p>
      <h3>{t("booking.form.title")}</h3>
      <p className="booking-form-note">{t("booking.form.note")}</p>

      <div className="booking-form-row">
        <label>
          {t("booking.form.checkIn")}
          <input
            type="date"
            name="check_in"
            required
            value={form.check_in}
            onChange={onChange}
          />
        </label>
        <label>
          {t("booking.form.checkOut")}
          <input
            type="date"
            name="check_out"
            required
            value={form.check_out}
            onChange={onChange}
          />
        </label>
      </div>

      <label>
        {t("booking.form.name")}
        <input type="text" name="guest_name" required value={form.guest_name} onChange={onChange} />
      </label>
      <label>
        {t("booking.form.email")}
        <input type="email" name="email" required value={form.email} onChange={onChange} />
      </label>
      <label>
        {t("booking.form.phone")}
        <input type="tel" name="phone" value={form.phone} onChange={onChange} />
      </label>

      <button className="btn btn-block" type="submit" disabled={sending}>
        {sending ? t("booking.form.sending") : t("booking.form.submit")}
      </button>

      <p role="status" className={`booking-form-status is-${state.status}`}>
        {state.message}
      </p>
    </form>
  );
}
