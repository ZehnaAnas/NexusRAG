/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#FAF8FF",
        surface: "#FFFFFF",
        ink: "#241B3A",
        "ink-soft": "#6B6280",
        border: "#ECE7FB",
        primary: {
          DEFAULT: "#7C5CFC",
          dark: "#6845E8",
          light: "#EFE9FF",
        },
        peach: {
          DEFAULT: "#FF8FA3",
          dark: "#F4667F",
          light: "#FFE7EB",
        },
        mint: {
          DEFAULT: "#2DD4BF",
          light: "#DAFBF5",
        },
        amber: {
          DEFAULT: "#F5A524",
          light: "#FEF3DA",
        },
        rose: {
          DEFAULT: "#FB5B7B",
          light: "#FFE4E9",
        },
      },
      fontFamily: {
        display: ["Fredoka", "sans-serif"],
        body: ["Plus Jakarta Sans", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      borderRadius: {
        blob: "42% 58% 63% 37% / 41% 44% 56% 59%",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0) rotate(0deg)" },
          "50%": { transform: "translateY(-6px) rotate(3deg)" },
        },
        pulseSoft: {
          "0%, 100%": { transform: "scale(1)" },
          "50%": { transform: "scale(1.06)" },
        },
        riseIn: {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        dotBounce: {
          "0%, 80%, 100%": { transform: "translateY(0)" },
          "40%": { transform: "translateY(-4px)" },
        },
      },
      animation: {
        float: "float 5s ease-in-out infinite",
        pulseSoft: "pulseSoft 1.6s ease-in-out infinite",
        riseIn: "riseIn 0.35s ease-out",
        dotBounce: "dotBounce 1.2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
