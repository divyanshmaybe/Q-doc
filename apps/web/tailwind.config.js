/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        midnight: {
          DEFAULT: "#0a0a0a",
          50: "#1a1a1a",
          100: "#141414",
          200: "#111111",
          300: "#0d0d0d",
          400: "#0a0a0a",
          900: "#000000",
        },
        electric: {
          DEFAULT: "#4361ee",
          light: "#5c7aff",
          dark: "#3a50d9",
          glow: "rgba(67, 97, 238, 0.32)",
        },
        accent: {
          DEFAULT: "#f72585",
          hover: "#d4186e",
          glow: "rgba(247, 37, 133, 0.32)",
        },
        neon: {
          DEFAULT: "#f72585",
          light: "#ff4d9e",
          dark: "#d4186e",
          glow: "rgba(247, 37, 133, 0.32)",
        },
        cyber: {
          emerald: "#00E599",
          amber: "#FFB020",
          red: "#FF3355",
        }
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        head: ["Poppins", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"],
      },
      boxShadow: {
        "electric-glow": "0 0 25px -3px rgba(67, 97, 238, 0.45)",
        "accent-glow": "0 2px 14px rgba(247, 37, 133, 0.35)",
        "neon-glow": "0 0 25px -3px rgba(247, 37, 133, 0.45)",
        "hud-card": "0 8px 32px 0 rgba(0, 0, 0, 0.7)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "radar-sweep": "sweep 4s linear infinite",
        "reticle-spin": "spin 12s linear infinite",
      },
      keyframes: {
        sweep: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        }
      }
    },
  },
  plugins: [],
}

