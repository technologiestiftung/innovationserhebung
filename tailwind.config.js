/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["app/templates/**/*.html", "app/styles/*.css"],
  jit: true,
  theme: {
    fontFamily: {
      clan: ["ClanPro", "sans-serif"],
      source: ["Source Serif", "serif"],
    },
    extend: {
      boxShadow: {
        top: "0px -8px 24px 0px rgba(0, 0, 0, 0.32)",
        bottom: "0px 0px 16px 0px rgba(0, 0, 0, 0.32)",
        toggleButton: "0px 0px 4px 0px rgba(0, 0, 0, 0.16)",
      },
      colors: {
        "corporate-blue": "#1E3791",
        "corporate-blue-light": "#495DA5",
        "corporate-gray-20": "#DADADA",
        "corporate-gray-90": "#3B3B3A",
        "light-gray": "#EBECF0",
        "page-background": "#F6F6F6",
      },
      fontSize: {
        h1: "2rem",
        h2: "1.125rem",
      },
      lineHeight: {
        h1: "2.5rem",
        h2: "1.5rem",
      },
      margin: {
        "3/5": "60vh",
        hero: "var(--width-hero)",
        mobile: "1.5rem",
      },
      maxWidth: {
        hero: "var(--width-hero)",
        80: "20rem",
      },
      minHeight: {
        4: "1rem",
      },
      padding: {
        mobile: "1.5rem",
        desktop: "4.75rem",
      },
      screens: {
        desktop: "1280px",
        tablet: "768px",
      },
      translate: {
        "x-full": "100%",
        "2x-full": "200%",
      },
      width: {
        "2x-hero": "calc(2 * var(--width-hero))",
        hero: "var(--width-hero)",
      },
    },
    purge: "app/static/**/*.js",
  },
  plugins: [],
}
