/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        paper: '#EAF0EE',
        'paper-dark': '#DCE6E2',
        ink: '#16313D',
        'ink-light': '#2A4A59',
        saffron: '#E2A63B',
        'saffron-dark': '#C88A22',
        rupee: '#2F6F5E',
        'rupee-light': '#3E8C77',
        coral: '#D65F4C',
        'coral-light': '#F0E4E1',
      },
      fontFamily: {
        display: ['"Fraunces"', 'serif'],
        body: ['"Inter"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
      boxShadow: {
        stamp: '0 2px 0 0 rgba(22,49,61,0.15)',
        card: '0 1px 2px rgba(22,49,61,0.06), 0 4px 12px rgba(22,49,61,0.06)',
      },
    },
  },
  plugins: [],
}
