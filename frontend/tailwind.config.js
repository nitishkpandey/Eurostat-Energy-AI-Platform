/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#667eea",
          dark: "#764ba2",
        },
        surface: "#1a1f2e",
        card: "#242938",
        border: "rgba(255,255,255,0.08)",
      },
    },
  },
  plugins: [],
}

