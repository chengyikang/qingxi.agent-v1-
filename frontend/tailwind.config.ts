import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'qx-bg': '#0f172a',
        'qx-bg-secondary': '#1e293b',
        'qx-bg-tertiary': '#334155',
        'qx-text': '#f1f5f9',
        'qx-text-secondary': '#94a3b8',
        'qx-text-muted': '#64748b',
        'qx-accent': '#f97316',
        'qx-accent-light': '#fb923c',
        'qx-accent-dark': '#ea580c',
        'stage-stranger': '#64748b',
        'stage-acquaintance': '#38bdf8',
        'stage-friend': '#fbbf24',
        'stage-confidant': '#f97316',
        'emotion-happy': '#4ade80',
        'emotion-calm': '#60a5fa',
        'emotion-sad': '#94a3b8',
        'emotion-anxious': '#f472b6',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      animation: {
        'typing': 'typing 1.4s infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'trust-change': 'trustChange 0.6s ease-out',
        'bounce-subtle': 'bounceSubtle 2s infinite',
      },
      keyframes: {
        typing: { '0%, 60%, 100%': { opacity: '0' }, '30%': { opacity: '1' } },
        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        slideUp: { '0%': { opacity: '0', transform: 'translateY(10px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
        trustChange: { '0%': { transform: 'scale(1)' }, '50%': { transform: 'scale(1.05)' }, '100%': { transform: 'scale(1)' } },
        bounceSubtle: { '0%, 100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-3px)' } },
      },
      transitionDuration: { '400': '400ms', '600': '600ms' },
    },
  },
  plugins: [],
}

export default config
