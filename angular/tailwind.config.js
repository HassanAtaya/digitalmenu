/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      colors: {
        luxury: {
          gold: "#C9A24B",
          dark: "#0F0F0F",
          slate: "#1B1B1B"
        }
      },
      fontFamily: {
        display: ["'Playfair Display'", 'serif'],
        body: ["'Inter'", 'sans-serif']
      }
    },
  },
  plugins: [],
}

