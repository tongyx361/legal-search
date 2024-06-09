import type { Config } from "tailwindcss";


const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      backgroundImage: {
        "grid": "url('/bg.svg')",
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
export default config;
