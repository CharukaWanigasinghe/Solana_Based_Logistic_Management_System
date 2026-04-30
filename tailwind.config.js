/** @type {import('tailwindcss').Config} */
const colors = require('tailwindcss/colors');

module.exports = {
  content: [
    "./app/templates/**/*.{html,js}",
    "./app/static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        // palette inspired by https://ui.shadcn.com/
        primary: colors.indigo,
        secondary: colors.emerald,
        accent: colors.sky,
        neutral: colors.slate,
        base: colors.white,
        info: colors.blue,
        success: colors.green,
        warning: colors.yellow,
        error: colors.red,
        'primary-light': colors.indigo[300],
        'primary-dark': colors.indigo[700],
        'secondary-light': colors.emerald[300],
        'secondary-dark': colors.emerald[700],
      },
    },
  },
  plugins: [],
}