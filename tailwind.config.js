/** @type {import('tailwindcss').Config} */
// Design tokens from CLONE_SPEC.md §0.2–0.5. Colour/button-font values live once in src/index.css :root
// (verbatim from the original); these entries map Tailwind names onto those CSS variables.
const fallback = [
  '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu',
  'Cantarell', 'Open Sans', 'Helvetica Neue', 'sans-serif',
]

export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    // Full replacement (not extend): the project palette is only these tokens.
    colors: {
        transparent: 'transparent',
        current: 'currentColor',
        inherit: 'inherit',
        black: 'var(--black)',
        accent: 'var(--accent)',
        white: 'var(--white)',
        red: 'var(--red)',
        'nav-glass': 'var(--nav-glass)',
        'ticker-band': 'var(--ticker-band)',
        backdrop: 'var(--backdrop)',
        'scroll-thumb': 'var(--scroll-thumb)',
        'popup-close': 'var(--popup-close)',
    },
    extend: {
      fontFamily: {
        aeonik: ['Aeonik', ...fallback],
        recife: ['Recife', ...fallback],
        neuehaas: ['NeueHaas', ...fallback],
        button: ['var(--font-button)'], // UA default button font measured in Chromium (spec §0.1)
      },
      borderRadius: {
        nav: '12px',
        rounded: '20px',
        card: '0 20px 20px',
        'card-m': '0 10px 10px',
        popup: '12px',
        menu: '10px',
        toast: '5px',
      },
      boxShadow: {
        revealer: '0 -16px 44px #b1dd4029',
      },
      transitionTimingFunction: {
        expo: 'cubic-bezier(.16,1,.3,1)',
      },
      screens: {
        // single desktop/mobile switch (spec §0.1)
        desk: '1060px',
      },
    },
  },
  // The original's `.container` (vw padding, no max-width) must not be overridden by Tailwind's breakpoint container.
  corePlugins: { container: false },
  plugins: [],
}
