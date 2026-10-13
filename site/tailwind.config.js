/** Compiled Tailwind for ppreader (offline-first, Fix 3).
 *  Replaces the Play CDN + inline tailwind.config. Build with:
 *  npx -y tailwindcss@3.4.17 -i ppreader/input.css -o ppreader/ppreader.css
 *  darkMode:'class' matches the reader's own theme switch (builder P12).
 */
module.exports = {
  darkMode: 'class',
  content: ['./ppreader/**/*.html', './ppreader/**/*.py'],
  safelist: [
    'story-text-sm', 'story-text-md', 'story-text-lg', 'story-text-xl',
  ],
  theme: {
    extend: {
      colors: {
        templeRed: '#7A0016',
        templeGold: '#D4AF37',
        saffron: '#E65100',
        parchment: '#FDFBF7',
        parchmentDark: '#F4EFE6',
        charcoal: '#2A221B',
        sepiaBg: '#F5EBE1',
        sepiaText: '#433422',
        darkBg: '#181512',
        darkText: '#E6DFD5',
        sandalwood: '#C8A276',
        vermilion: '#C62828'
      },
      fontFamily: {
        heading: ['Cinzel', 'serif'],
        body: ['Inter', 'sans-serif'],
        serif: ['Lora', 'serif'],
        tamil: ['"Noto Serif Tamil"', 'serif']
      }
    }
  },
  plugins: [],
}
