/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#ffffff', // white
        blue: {
          light: '#e6f0fa', // light blue
        },
        orange: {
          light: '#ffe5c2', // light orange
        },
        dark: {
          DEFAULT: '#23272f', // dark grey
        },
        faded: {
          blue: '#b3cbe6',
          orange: '#ffd8a8',
          grey: '#f5f6fa',
        },
      },
    },
  },
  plugins: [],
};
