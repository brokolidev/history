# ⏳ History & Memories Archive (`history.brokolidev.com`)

[![Live Demo](https://img.shields.io/badge/Live-history.brokolidev.com-0d9488?style=flat-square&logo=cloudflare)](https://history.brokolidev.com)
[![Built with Bun](https://img.shields.io/badge/Built%20with-Bun-fbf0df?style=flat-square&logo=bun)](https://bun.sh)
[![Deploy Cloudflare Pages](https://img.shields.io/badge/Deploy-Cloudflare%20Pages-f38020?style=flat-square&logo=cloudflarepages)](https://pages.cloudflare.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

A personal digital history timeline and memory archive chronicling 11+ years (2005–2020) of software engineering notes, reflections, technical learnings, and milestones migrated from Naver Blog and social channels.

🔗 **Live Website**: [https://history.brokolidev.com](https://history.brokolidev.com)

---

## 🌟 Key Features

- **⚡️ SSG Built with Bun**: Ultra-fast static site compilation (compiles 294+ detailed markdown articles across 11 years in seconds).
- **📅 Chronological Year-Grouped Timeline**: Clean, interactive year sections with collapsible accordion cards and deep-linking anchors (`#slug`).
- **🔍 Real-Time Search & Dual Filtering**: Instant multi-keyword search across titles and article content, paired with platform (`Naver Blog`, etc.) and category filter chips.
- **🎨 Tailwind Catalyst Dark Theme (Zinc 950)**: Minimalist, modern dark mode design adhering to Tailwind Catalyst UI specifications with ambient glow background and high-contrast typography (> 7:1).
- **💻 macOS Window Code Blocks**:
  - macOS terminal window controls (🔴 🟡 🟢)
  - Automatic language badge detection (`NGINX`, `BASH`, `PHP`, `SQL`, `PYTHON`, `JAVASCRIPT`, `HTML`, etc.)
  - 1-Tap clipboard copy with animated visual confirmation (`Copied!`)
  - Prism.js syntax highlighting with inlined critical styles to prevent flash of unstyled content (FOUC).
- **🚀 Automated CI/CD**: Automatic zero-downtime static deployment to Cloudflare Pages on push via GitHub Actions.

---

## 🛠️ Tech Stack

- **Runtime & Build Engine**: [Bun](https://bun.sh)
- **Markdown & Syntax Highlighting**: [Marked](https://marked.js.org), [Prism.js](https://prismjs.com), [front-matter](https://github.com/jxson/front-matter)
- **Styling**: Vanilla CSS modeled on [Tailwind UI Catalyst](https://catalyst.tailwindui.com), Inter & JetBrains Mono typography, Font Awesome 6
- **Hosting & Edge Delivery**: [Cloudflare Pages](https://pages.cloudflare.com)
- **CI/CD**: GitHub Actions

---

## 📂 Project Structure

```text
history/
├── content/
│   └── history/             # Markdown post archives (Frontmatter + Markdown body)
├── src/
│   ├── css/
│   │   └── style.css        # Core stylesheet (Catalyst theme, timeline, cards)
│   └── js/
│       └── main.js          # Client-side interactions (search, filter, copy, theme)
├── public/                  # Static assets (favicons, images, manifests)
├── dist/                    # Compiled production static output
├── .github/
│   └── workflows/
│       └── deploy.yml       # Cloudflare Pages CI/CD workflow
├── build.js                 # Bun static site generator script
└── package.json
```

---

## 🚀 Getting Started

### Prerequisites

- [Bun](https://bun.sh) (v1.0.0 or higher)

### Installation

```bash
# Clone the repository
git clone git@github.com:brokolidev/history.git
cd history

# Install dependencies
bun install
```

### Build & Run

```bash
# Compile static HTML to dist/
bun run build

# Start local preview server
bun run dev
```

---

## 👤 Author

**Ted Choi**
- Website: [https://brokolidev.com](https://brokolidev.com)
- GitHub: [@brokolidev](https://github.com/brokolidev)
- Email: bocalist@gmail.com

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
