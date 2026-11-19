module.exports = {
  content: [
    "./templates/**/*.html",
    "./core/**/*.{py,html}",
    "./devis/**/*.{py,html}",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        noir: "#0B0D0F",
        blanc: "#FFFFFF",
        vert: "#15A34A",
      },
      fontFamily: {
        display: ['"Suez One"', "ui-serif", "Georgia", "serif"],
      },
    },
  },
  plugins: [],
};
