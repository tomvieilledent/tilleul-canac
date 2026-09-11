import { useEffect, useState } from "react";
import { API_URL } from "../lib/site.js";

async function fetchJson(url) {
  const res = await fetch(url, { cache: "no-cache" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

/**
 * Disponibilités : lit l'API (backend/) si VITE_API_URL est définie, avec repli
 * sur le JSON statique généré par sync-availability.yml si l'API est indisponible
 * ou non configurée. Même forme dans les deux cas : { updated, booked: [{start,end}] }.
 */
export function useAvailability(refreshKey = 0) {
  const [state, setState] = useState({ data: null, error: null, loading: true });

  useEffect(() => {
    let alive = true;
    const staticUrl = `${import.meta.env.BASE_URL}data/availability.json`;

    (async () => {
      if (API_URL) {
        try {
          const data = await fetchJson(`${API_URL}/api/availability`);
          if (alive) setState({ data, error: null, loading: false });
          return;
        } catch (err) {
          console.error("useAvailability: API indisponible, repli sur le JSON statique", err);
        }
      }
      try {
        const data = await fetchJson(staticUrl);
        if (alive) setState({ data, error: null, loading: false });
      } catch (err) {
        if (alive) setState({ data: null, error: err, loading: false });
      }
    })();

    return () => {
      alive = false;
    };
  }, [refreshKey]);

  return state;
}
