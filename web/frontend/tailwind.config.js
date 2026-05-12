/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: { 50: '#f3f0ff', 100: '#e9e5ff', 200: '#d5cfff', 300: '#b5a9fe', 400: '#9275fb', 500: '#6C5CE7', 600: '#5f47d4', 700: '#5236b8', 800: '#442e96', 900: '#3a2b77' },
      }
    }
  },
  plugins: []
}
