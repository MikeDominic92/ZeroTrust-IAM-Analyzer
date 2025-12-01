import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "var(--background)",
                foreground: "var(--foreground)",
                google: {
                    blue: "#4285F4",
                    red: "#EA4335",
                    yellow: "#FBBC05",
                    green: "#34A853",
                },
                risk: {
                    high: "#DC2626", // Vermillion
                    medium: "#F59E0B", // Orange
                    low: "#10B981", // Green
                },
                surface: {
                    DEFAULT: "#FFFFFF",
                    dark: "#1F2937", // Charcoal
                    muted: "#F8FAFC", // Off-white
                },
                secondary: {
                    DEFAULT: "#7C3AED", // Deep Purple
                    light: "#8B5CF6",
                },
                neutral: {
                    50: "#F8FAFC",
                    100: "#F1F5F9",
                    200: "#E2E8F0",
                    300: "#CBD5E1",
                    400: "#94A3B8",
                    500: "#64748B",
                    600: "#475569",
                    700: "#334155",
                    800: "#1E293B",
                    900: "#0F172A",
                }
            },
            fontFamily: {
                sans: ["var(--font-poppins)", "var(--font-inter)", "sans-serif"],
                mono: ["var(--font-roboto-mono)", "monospace"],
            },
            boxShadow: {
                'card': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
                'card-hover': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -1px rgb(0 0 0 / 0.1)',
                'elevation-1': '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)',
                'elevation-2': '0 1px 2px 0 rgba(60,64,67,0.3), 0 2px 6px 2px rgba(60,64,67,0.15)',
            },
        },
    },
    plugins: [],
};
export default config;
