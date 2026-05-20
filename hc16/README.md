# HC-16 Vulnerability Profile Pages

Complete set of 16 individual type profile pages plus an index page for the Non Dubito HC-16 Vulnerability Profile system.

## Overview

This directory contains 17 static HTML files:
- **16 Type Profile Pages** (DTAB.html through CTER.html)
- **1 Index Page** (index.html)

All files are self-contained, fully responsive, and feature complete bilingual support (Chinese/English).

## Files

### Type Profile Pages

Each type page follows the pattern `[TYPE_CODE].html`:

| File | Type | Chinese Name | English Dimensions |
|------|------|-------------|-------------------|
| DTAB.html | DTAB | 驱容专栖 | Drive · Tolerant · Anchor · Base |
| CTAB.html | CTAB | 泰容专栖 | Composed · Tolerant · Anchor · Base |
| DFAB.html | DFAB | 驱烈专栖 | Drive · Fierce · Anchor · Base |
| CFAB.html | CFAB | 泰烈专栖 | Composed · Fierce · Anchor · Base |
| DFER.html | DFER | 驱烈拓游 | Drive · Fierce · Explore · Roam |
| DTEB.html | DTEB | 驱容拓栖 | Drive · Tolerant · Explore · Base |
| CFAR.html | CFAR | 泰烈专游 | Composed · Fierce · Anchor · Roam |
| DTAR.html | DTAR | 驱容专游 | Drive · Tolerant · Anchor · Roam |
| DFEB.html | DFEB | 驱烈拓栖 | Drive · Fierce · Explore · Base |
| DFAR.html | DFAR | 驱烈专游 | Drive · Fierce · Anchor · Roam |
| DTER.html | DTER | 驱容拓游 | Drive · Tolerant · Explore · Roam |
| CTEB.html | CTEB | 泰容拓栖 | Composed · Tolerant · Explore · Base |
| CFER.html | CFER | 泰烈拓游 | Composed · Fierce · Explore · Roam |
| CFEB.html | CFEB | 泰烈拓栖 | Composed · Fierce · Explore · Base |
| CTAR.html | CTAR | 泰容专游 | Composed · Tolerant · Anchor · Roam |
| CTER.html | CTER | 泰容拓游 | Composed · Tolerant · Explore · Roam |

### Index Page

**index.html** - Overview page with a 4×4 responsive grid of all 16 types. Each type card shows:
- Type code
- Chinese name
- English dimension names
- Bilingual tagline
- Navigation link to type page

## Page Structure

Each type profile page contains:

1. **Hero Section**
   - Large type code (5-7rem, gold)
   - Chinese name (3rem)
   - English dimensions
   - Bilingual tagline (italic)

2. **Dimensions Display**
   - 2×2 responsive grid
   - Each dimension shows: character, HIGH/LOW indicator, bilingual description

3. **Content Sections**
   - 结构模式 / Pattern - Core behavioral pattern
   - 危险地形 / Blind Spots - Vulnerability and pitfalls
   - 常见误读 / Misread As - Common misconceptions
   - 修复逻辑 / What Helps - Actionable guidance (what doesn't work vs. what does)

4. **Call-to-Action Footer**
   - Links to take the test
   - Links to browse all types

## Design Features

### Visual Theme
- **Background**: #0f0f0e (deep black)
- **Primary Text**: #f5f0e8 (warm cream)
- **Accent Color**: #c49d61 (refined gold)
- **Secondary Text**: #999, #ccc (various grays)

### Typography
- **Serif**: EB Garamond (headers, taglines, emphasis)
- **Sans**: Inter (body text, UI, navigation)
- **CJK**: Noto Serif SC (Chinese characters)

All fonts loaded from Google Fonts.

### Responsive Design
- **Desktop (1200px+)**: Full layouts, 2-4 column grids
- **Tablet (768px-1024px)**: Adjusted spacing, 2-3 column grids
- **Mobile (480px-768px)**: 1-2 column layouts
- **Small Mobile (<480px)**: Single column, optimized for touch

### Bilingual Support
- Default language: Chinese (中文)
- Toggle button: EN|中文 in header
- Persistence: Language preference saved to localStorage
- No page reloads required

## Technical Details

### HTML5
- Valid HTML5 structure
- Semantic elements (header, main, section, footer)
- Proper heading hierarchy
- UTF-8 encoding

### CSS
- Embedded styles (no external stylesheets)
- CSS Grid and Flexbox layouts
- Media queries for responsiveness
- Smooth transitions and hover effects
- CSS variables for consistency

### JavaScript
- Minimal, dependency-free
- Language toggle functionality
- localStorage for preference persistence
- Auto-restore saved language on page load

### SEO & Accessibility
- Unique meta descriptions per page
- Open Graph tags for social sharing
- Canonical URLs
- High contrast text
- Semantic HTML structure
- Keyboard navigable
- Touch-friendly

## Deployment

### Ready for
- Direct hosting on nondubito.net/hc16/
- Static site hosting (Netlify, Vercel, GitHub Pages)
- CDN distribution
- S3 or other cloud storage

### No Requirements
- No build process needed
- No package dependencies
- No database required
- No backend server needed
- Works with simple HTTP serving

## File Size Statistics

- **Total Size**: 344 KB
- **Average File Size**: 20.2 KB
- **Smallest File**: 18 KB
- **Largest File**: 21 KB

All files are optimized and self-contained.

## Customization

To customize:

1. **Content**: Edit type data in the generator script
2. **Colors**: Update CSS color values in page templates
3. **Fonts**: Modify Google Fonts import URL
4. **Layout**: Adjust CSS Grid/Flexbox values in media queries
5. **Analytics**: Add tracking code to page templates

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Android)

## Notes

- All content is fully bilingual (Chinese/English)
- Pages are optimized for sharing on social media
- Images can be added to enhance visual appeal
- Pages are mobile-first and accessibility-aware
- No external JavaScript libraries used

---

Generated: March 8, 2026
Generator: Python 3 script (generate_hc16_pages.py)
Status: Production Ready
