module.exports = {
  purge: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      colors: {
        gray: {
          lightest: '#3b3c64',
          lighter: '#333457',
          light: '#2b2c4a',
          dark: '#23243c',
          darker: '#1c1c2f',
          darkest: '#141421'
        }
      },
      height: {
        '112': '28rem',
        '128': '32rem',
        '144': '36rem',
        '160': '40rem',
        '176': '44rem',
        '192': '48rem'
      },
      width: {
        '112': '28rem',
        '128': '32rem',
        '144': '36rem',
        '160': '40rem',
        '176': '44rem',
        '192': '48rem'
      }
    },
  },
  variants: {
    extend: {
      display: ['group-hover'],
    },
  },
  plugins: [],
}
