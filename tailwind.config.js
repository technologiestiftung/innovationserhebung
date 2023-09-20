/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["app/templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        "corporate-blue": "#1E3791",
      },
      margin: {
        "60vh": "60vh",
      },
      boxShadow: {
        top: "0px -8px 24px 0px rgba(0, 0, 0, 0.32)",
      },
    },
  },
  plugins: [],
};
