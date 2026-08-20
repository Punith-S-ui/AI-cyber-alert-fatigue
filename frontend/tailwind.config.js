/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: {
          950: '#0A0E13',
          900: '#0F151C',
          800: '#141C26',
          700: '#1B2531',
          600: '#28374A',
        },
        signal: {
          cyan: '#2DD4BF',
          amber: '#F5A623',
          red: '#EF4444',
          green: '#34D399',
          blue: '#3B82F6',
        },
        ink: {
          100: '#E6EDF3',
          300: '#9FB0C0',
          500: '#6B7C8D',
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
