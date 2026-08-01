/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: '#F8FAFC',
          dark: '#020617',
        },
        card: {
          DEFAULT: '#ffffff',
          dark: '#111827',
        },
        border: {
          DEFAULT: '#E5E7EB',
          dark: '#1F2937',
        },
        foreground: {
          DEFAULT: '#111827',
          dark: '#F8FAFC',
        },
        'muted-foreground': {
          DEFAULT: '#475569',
          dark: '#CBD5E1',
        },
        primary: {
          DEFAULT: '#06B6D4',
          dark: '#06B6D4',
        },
        accent: {
          DEFAULT: '#06B6D4',
          dark: '#22D3EE',
        },
      },
      boxShadow: {
        glow: '0 25px 80px rgba(56, 189, 248, 0.13)',
      },
    },
  },
  plugins: [],
}
