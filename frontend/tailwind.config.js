/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Eco-friendly theme palette
        forest: {
          DEFAULT: "#1B4332", // primary brand green
          light: "#2D6A4F",
          dark: "#0F2E20",
        },
        gold: {
          DEFAULT: "#E9C46A", // soft gold/yellow accent
          light: "#F4E1A1",
          dark: "#D4A93C",
        },
        cream: "#FAFAF7", // off-white background
      },
    },
  },
  plugins: [],
};
