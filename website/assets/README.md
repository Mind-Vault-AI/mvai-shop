# Assets Folder Structure

Deze folder bevat alle statische assets voor de MindVault-AI website.

## Structuur

```
assets/
├── images/          # Product afbeeldingen, screenshots, foto's
│   ├── products/    # Product mockups en previews
│   ├── hero/        # Hero section afbeeldingen
│   └── testimonials/# Avatar foto's voor testimonials
├── icons/           # SVG icons en favicon
│   └── favicon.svg  # Website favicon
└── fonts/           # Custom fonts (indien nodig)
```

## Afbeelding Specs

### Product Images
- Formaat: PNG of WebP
- Afmetingen: 800x600px minimum
- Aspect ratio: 4:3 of 16:9

### Hero Images
- Formaat: WebP (met PNG fallback)
- Afmetingen: 1920x1080px
- Geoptimaliseerd voor web (<500KB)

### Icons
- Formaat: SVG (vector)
- Optimaliseer met SVGO

## Optimalisatie Tips

1. Gebruik WebP waar mogelijk
2. Lazy load afbeeldingen below the fold
3. Gebruik srcset voor responsive images
4. Comprimeer met tools zoals TinyPNG of Squoosh

## Placeholder Images

Voor development kun je placeholder services gebruiken:
- https://placeholder.com/
- https://picsum.photos/
- https://via.placeholder.com/
