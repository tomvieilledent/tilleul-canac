// Données non traduites (coordonnées, liens). Les textes sont dans src/i18n/strings.js.

export const BOOKING_URL =
  "https://www.booking.com/hotel/fr/chambre-d-39-hote-rodez.fr.html";
export const BOOKING_REVIEWS_URL = BOOKING_URL + "#tab-reviews";

// API de réservation (backend/). Vide -> pas de formulaire, calendrier en repli JSON statique.
// Définie via .env / .env.production (VITE_API_URL=https://tilleul-canac-api.vlldnt.fr).
export const API_URL = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

export const CONTACT = {
  address1: "270 chemin de Canac",
  address2: "12850 Onet-le-Château",
  phone: "06 63 71 39 62",
  phoneHref: "+33663713962",
  email: "lbcmarie.12@gmail.com",
};

// 270 chemin de Canac, 12850 Onet-le-Château (coordonnées de la fiche OSM du gîte)
export const MAP = { lat: 44.36362, lon: 2.58369, zoom: 16 };

// Photos dans public/photos/ : pour chaque nom, tcN.jpg (repli 1024) + tcN-400/800/1024.webp.
// Régénérer avec : npm run images
export const PHOTO_WIDTHS = [400, 800, 1024];
export const GALLERY_PHOTOS = ["tc1", "tc2", "tc3", "tc4", "tc5", "tc6"];
export const HERO_PHOTO = "tc7";

export const asset = (path) => `${import.meta.env.BASE_URL}${String(path).replace(/^\//, "")}`;
export const photoJpg = (name) => asset(`photos/${name}.jpg`);
export const photoWebpSrcSet = (name) =>
  PHOTO_WIDTHS.map((w) => `${asset(`photos/${name}-${w}.webp`)} ${w}w`).join(", ");
