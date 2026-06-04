/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          50: "#F8F8F2",
          100: "#E6DB74",
          200: "#A59F85",
          300: "#75715E",
          500: "#49483E",
          700: "#3E3D32",
          900: "#1E1F1C",
        },
        accent: {
          500: "#F92672",
          600: "#E22062",
        },
        good: "#A6E22E",
        warn: "#FD971F",
        bad: "#F92672",
        cyan: "#66D9EF",
        purple: "#AE81FF",
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "sans-serif",
        ],
      },
      boxShadow: {
        card: "0 1px 0 rgba(255,255,255,0.04) inset, 0 12px 40px -12px rgba(0,0,0,0.6)",
      },
    },
  },
  plugins: [],
};
