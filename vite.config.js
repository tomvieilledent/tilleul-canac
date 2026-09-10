import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Servi à la racine de son sous-domaine (https://tilleul-canac.vlldnt.fr) par nginx.
export default defineConfig({
  base: "/",
  plugins: [react()],
  build: {
    // modulepreload est nativement supporté par les navigateurs ciblés :
    // pas de polyfill inline (compatibilité CSP script-src 'self').
    modulePreload: { polyfill: false },
    target: "es2020",
  },
});
