# SKF Documentation Website

This directory contains the Astro + Starlight website for Skill Forge (SKF) documentation.

## Setup

Install dependencies:

```bash
cd website
npm install
```

## Development

Run the development server:

```bash
npm run dev
```

Visit <http://localhost:4321> to view the site.

## Build

Build the production site:

```bash
npm run build
```

Output is generated to `../build/site/` (configured in `astro.config.mjs`).

## Preview

Preview the production build locally:

```bash
npm run preview
```

## Structure

```
website/
├── astro.config.mjs      # Astro configuration
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript configuration
├── public/               # Static assets
│   ├── favicon.ico
│   └── robots.txt
├── src/
│   ├── components/       # Astro components
│   │   ├── Banner.astro
│   │   ├── Header.astro
│   │   └── MobileMenuFooter.astro
│   ├── content/          # Content collections
│   │   ├── config.ts
│   │   └── docs -> ../../../docs (symlink)
│   ├── lib/              # Utility libraries
│   │   └── site-url.js
│   ├── pages/            # Page templates
│   │   └── 404.astro
│   ├── styles/           # Custom CSS
│   │   └── custom.css
│   ├── rehype-markdown-links.js  # Rehype plugin for markdown links
│   └── rehype-base-paths.js      # Rehype plugin for base paths
```

## Configuration

The site URL is configured via environment variable or defaults:

```bash
# Set site URL for production
export SITE_URL=https://armelhbobdad.github.io/bmad-module-skill-forge

# Build with custom URL
SITE_URL=https://armelhbobdad.github.io/bmad-module-skill-forge npm run build
```

## Deployment

The site is built and deployed via the documentation build pipeline:

```bash
# From project root
npm run docs:build
```

This generates:

- `/build/artifacts/` - LLM files, download bundles
- `/build/site/` - Deployable website

## Starlight Features

- **Search**: Built-in full-text search
- **Navigation**: Sidebar from configuration
- **Dark Mode**: Automatic light/dark theme switching
- **Mobile-Friendly**: Responsive design
- **LLM Discovery**: Meta tags for AI agent consumption
- **Sitemap**: Automatic sitemap generation
- **Last Updated**: Git-based timestamps

## Customization

### Components

Custom components override Starlight defaults:

- `Banner.astro` - AI documentation banner
- `Header.astro` - Site header with banner
- `MobileMenuFooter.astro` - Mobile menu footer

### Styles

Custom CSS in `src/styles/custom.css` extends Starlight's default theme with an amber/orange forge palette.

### Sidebar

Sidebar configuration in `astro.config.mjs` controls navigation structure.

## Links

- Repository: <https://github.com/armelhbobdad/bmad-module-skill-forge>
- BMAD Method: <https://bmad-method.org>
