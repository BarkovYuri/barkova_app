import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        // Body text: Inter (современный, читаемый)
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'system-ui',
          'sans-serif',
        ],
        // Headings: Montserrat (акцидентный, сильный)
        heading: [
          'Montserrat',
          '-apple-system',
          'BlinkMacSystemFont',
          'sans-serif',
        ],
      },
      fontSize: {
        // Headings
        'h1-mobile': ['32px', { lineHeight: '1.2', fontWeight: '700' }],
        'h1-desktop': ['48px', { lineHeight: '1.2', fontWeight: '700' }],
        'h2-mobile': ['28px', { lineHeight: '1.2', fontWeight: '700' }],
        'h2-desktop': ['36px', { lineHeight: '1.2', fontWeight: '700' }],
        'h3-mobile': ['20px', { lineHeight: '1.2', fontWeight: '600' }],
        'h3-desktop': ['24px', { lineHeight: '1.2', fontWeight: '600' }],
        // Body
        'base-large': ['18px', { lineHeight: '1.6', fontWeight: '400' }],
        'base-default': ['16px', { lineHeight: '1.6', fontWeight: '400' }],
        'base-small': ['14px', { lineHeight: '1.5', fontWeight: '400' }],
        'base-tiny': ['12px', { lineHeight: '1.4', fontWeight: '400' }],
        // UI/Labels
        'ui-label': ['14px', { lineHeight: '1.5', fontWeight: '500' }],
      },
      colors: {
        // Primary (Доверие, профессионализм - медицинский голубой)
        primary: {
          50: '#E3F2FD',
          100: '#BBDEFB',
          200: '#90CAF9',
          300: '#64B5F6',
          400: '#42A5F5',
          500: '#2196F3',
          600: '#0066CC', // Main
          700: '#0052A3',
          800: '#003D7A',
          900: '#002851',
        },
        // Secondary (Здоровье, уверенность - зелёный)
        secondary: {
          50: '#ECFDF5',
          100: '#D1F4E6',
          200: '#A2E9D2',
          300: '#6DDDB3',
          400: '#4ECFA5',
          500: '#10B981', // Main
          600: '#059669',
          700: '#047857',
          800: '#065F46',
          900: '#064E3B',
        },
        // Accent (Внимание, деятельность - янтарь)
        accent: {
          50: '#FFFBEB',
          100: '#FEF3C7',
          200: '#FDE68A',
          300: '#FCD34D',
          400: '#FBBF24',
          500: '#F59E0B', // Main
          600: '#D97706',
          700: '#B45309',
          800: '#92400E',
          900: '#78350F',
        },
        // Error/Success/Warning
        error: {
          50: '#FEE2E2',
          600: '#EF4444',
          700: '#DC2626',
        },
        success: {
          50: '#ECFDF5',
          600: '#10B981',
          700: '#059669',
        },
        warning: {
          50: '#FEF3C7',
          600: '#F59E0B',
          700: '#D97706',
        },
        // Neutral (Фоны, текст)
        neutral: {
          0: '#FFFFFF',
          50: '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          600: '#4B5563',
          700: '#374151',
          800: '#1F2937',
          900: '#111827',
        },
      },
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '16px',
        lg: '24px',
        xl: '32px',
        '2xl': '48px',
        '3xl': '64px',
      },
      borderRadius: {
        xs: '4px',
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '24px',
      },
      boxShadow: {
        xs: '0 1px 2px rgba(0, 0, 0, 0.05)',
        sm: '0 1px 3px rgba(0, 0, 0, 0.1)',
        md: '0 4px 6px rgba(0, 0, 0, 0.1)',
        lg: '0 10px 15px rgba(0, 0, 0, 0.1)',
        xl: '0 20px 25px rgba(0, 0, 0, 0.15)',
        '2xl': '0 25px 50px rgba(0, 0, 0, 0.2)',
        'card': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'card-hover': '0 20px 25px rgba(0, 0, 0, 0.15)',
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.6s ease-out',
        'fade-in': 'fadeIn 0.4s ease-out',
        'slide-in': 'slideIn 0.4s ease-out',
        'pulse-gentle': 'pulseGentle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeInUp: {
          '0%': {
            opacity: '0',
            transform: 'translateY(20px)',
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
        fadeIn: {
          '0%': {
            opacity: '0',
          },
          '100%': {
            opacity: '1',
          },
        },
        slideIn: {
          '0%': {
            transform: 'translateX(-20px)',
            opacity: '0',
          },
          '100%': {
            transform: 'translateX(0)',
            opacity: '1',
          },
        },
        pulseGentle: {
          '0%, 100%': {
            opacity: '1',
          },
          '50%': {
            opacity: '0.8',
          },
        },
      },
      transitionDuration: {
        '300': '300ms',
        '500': '500ms',
      },
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'ease-in-out-smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [],
};

export default config;
