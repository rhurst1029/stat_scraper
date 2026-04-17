/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'ucla-blue': '#2774AE',
        gold: '#FFD100',
        'dark-bg': '#0f172a',
        'card-bg': '#1e293b',
        border: '#334155',
        muted: '#94a3b8',
      },
    },
  },
  plugins: [],
}

