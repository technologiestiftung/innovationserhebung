/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["app/templates/**/*.html"],
  theme: {
    extend: {
      boxShadow: {
        top: "0px -8px 24px 0px rgba(0, 0, 0, 0.32)",
      },
      colors: {
        "corporate-blue": "#1E3791",
      },
      margin: {
        "60vh": "60vh",
        hero: "var(--width-hero)",
      },
      maxWidth: {
        hero: "var(--width-hero)",
      },
      padding: {
        mobile: "1.5rem",
        desktop: "4.75rem",
      },
      screens: {
        desktop: "1280px",
        tablet: "768px",
      },
    },
  },
  plugins: [],
};
