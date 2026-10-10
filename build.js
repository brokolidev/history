import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import frontMatter from 'front-matter';
import { marked } from 'marked';
import Prism from 'prismjs';
globalThis.Prism = Prism;
import loadLanguages from 'prismjs/components/index.js';

try {
  loadLanguages([
    'markup',
    'css',
    'javascript',
    'bash',
    'php',
    'nginx',
    'sql',
    'python',
    'yaml',
    'json',
    'ini',
    'docker',
    'java',
    'c',
    'cpp'
  ]);
} catch (e) {
  console.warn('Prism loadLanguages warning:', e);
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Custom marked renderer for syntax-highlighted code blocks
const renderer = new marked.Renderer();
renderer.code = function ({ text, lang }) {
  const rawLang = (lang || '').toLowerCase().trim();
  const langAliases = {
    js: 'javascript',
    ts: 'typescript',
    py: 'python',
    sh: 'bash',
    shell: 'bash',
    zsh: 'bash',
    conf: 'nginx',
    html: 'markup',
    xml: 'markup',
    yml: 'yaml',
  };
  const cleanLang = langAliases[rawLang] || rawLang || 'text';
  const displayLang = (rawLang || cleanLang || 'CODE').toUpperCase();

  let highlighted = text;
  if (cleanLang && Prism.languages[cleanLang]) {
    try {
      highlighted = Prism.highlight(text, Prism.languages[cleanLang], cleanLang);
    } catch (e) {
      highlighted = text;
    }
  }

  return `
<div class="code-block-wrapper">
  <div class="code-block-header">
    <div class="code-block-header-left">
      <span class="mac-dot mac-dot-red"></span>
      <span class="mac-dot mac-dot-yellow"></span>
      <span class="mac-dot mac-dot-green"></span>
      <span class="code-lang-badge">${displayLang}</span>
    </div>
    <button type="button" class="code-copy-btn" onclick="copyCodeBlock(this)" aria-label="Copy code">
      <i class="far fa-copy"></i>
      <span>Copy</span>
    </button>
  </div>
  <pre class="language-${cleanLang}"><code class="language-${cleanLang}">${highlighted}</code></pre>
</div>`;
};
marked.setOptions({ renderer });

const POSTS_DIR = path.join(__dirname, 'content', 'history');
const DIST_DIR = path.join(__dirname, 'dist');
const DIST_POSTS_DIR = path.join(DIST_DIR, 'posts');
const PUBLIC_DIR = path.join(__dirname, 'public');

// Unified GA4 Tag (Identical across brokolidev.com, blog, and history)
const GA_TAG_HTML = `
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-0KR5V5X1NT"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-0KR5V5X1NT');
  </script>`;

function getFaviconHtml(rootPrefix = '') {
  return `
  <link rel="icon" type="image/x-icon" href="${rootPrefix}favicon.ico">
  <link rel="shortcut icon" href="${rootPrefix}img/favicon.ico">
  <link rel="icon" type="image/png" sizes="32x32" href="${rootPrefix}img/favicon_io/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="${rootPrefix}img/favicon_io/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="${rootPrefix}img/favicon_io/apple-touch-icon.png">
  <link rel="manifest" href="${rootPrefix}img/favicon_io/site.webmanifest">`;
}

function copyDirRecursive(src, dest) {
  if (!fs.existsSync(src)) return;
  fs.mkdirSync(dest, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDirRecursive(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function parseDateParts(dateStr) {
  const match = String(dateStr).match(/^(\d{4})-(\d{2})-(\d{2})/);
  let year = 2026, month = '01', day = '01';
  let d;
  if (match) {
    year = Number(match[1]);
    month = match[2];
    day = match[3];
    d = new Date(year, Number(month) - 1, Number(day));
  } else {
    d = new Date(dateStr);
    year = d.getFullYear() || 2026;
    month = String(d.getMonth() + 1).padStart(2, '0');
    day = String(d.getDate()).padStart(2, '0');
  }

  const weekdays = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
  const weekday = weekdays[d.getDay()] || 'DAY';
  return {
    year: String(year),
    monthDay: `${month}.${day}`,
    weekday,
    full: `${year}.${month}.${day}`,
  };
}

function getHeaderHtml(rootPrefix = '') {
  return `
  <!-- Ambient Background Light Effects (Identical to brokolidev.com) -->
  <div class="ambient-glow" aria-hidden="true">
    <div class="ambient-blob-1"></div>
    <div class="ambient-blob-2"></div>
  </div>

  <header class="site-header">
    <div class="header-outer">
      <div class="header-inner">
        <!-- Brand / Logo -->
        <a href="https://brokolidev.com" class="header-brand">
          <span>brokoli<span class="text-accent">.dev</span></span>
        </a>

        <!-- Seamless Navigation Links & Theme Toggle -->
        <nav class="header-nav">
          <a href="https://brokolidev.com" class="nav-tab-inactive">
            <span>Profile</span>
          </a>
          <a href="https://blog.brokolidev.com" class="nav-tab-inactive">
            <span>Blog</span>
          </a>
          <a href="${rootPrefix ? rootPrefix + 'index.html' : '/'}" class="nav-tab-active">
            <span>History</span>
          </a>

          <!-- Theme Toggle -->
          <button type="button" id="theme-toggle" aria-label="Toggle theme" class="theme-btn">
            <i class="fas fa-sun theme-icon-sun"></i>
            <i class="fas fa-moon theme-icon-moon"></i>
          </button>
        </nav>
      </div>
    </div>
  </header>`;
}

function getFooterHtml() {
  return `
  <footer class="site-footer">
    <div class="footer-inner">
      <p>© 2026 <strong>brokolidev.com</strong> · History & Memories Archive</p>
    </div>
  </footer>`;
}

function getHeadInitScript() {
  return `
  <script>
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  </script>`;
}

async function build() {
  console.log('⚡️ Compiling history.brokolidev.com archive...');

  if (fs.existsSync(DIST_POSTS_DIR)) {
    fs.rmSync(DIST_POSTS_DIR, { recursive: true, force: true });
  }
  fs.mkdirSync(DIST_POSTS_DIR, { recursive: true });
  fs.mkdirSync(path.join(DIST_DIR, 'css'), { recursive: true });
  fs.mkdirSync(path.join(DIST_DIR, 'js'), { recursive: true });

  if (!fs.existsSync(POSTS_DIR)) {
    fs.mkdirSync(POSTS_DIR, { recursive: true });
  }

  const postFiles = fs.readdirSync(POSTS_DIR).filter((f) => f.endsWith('.md'));
  const posts = [];
  const sourcesSet = new Set();
  const categoriesSet = new Set();

  for (const file of postFiles) {
    const raw = fs.readFileSync(path.join(POSTS_DIR, file), 'utf-8');
    const parsed = frontMatter(raw);
    const attrs = parsed.attributes || {};

    const slug = attrs.slug || file.replace(/\.md$/, '');
    const dateStr = attrs.date || '2020-01-01';
    const dateMeta = parseDateParts(dateStr);
    const source = (attrs.source || 'naver').toLowerCase();
    const category = attrs.category || '일상';

    sourcesSet.add(source);
    categoriesSet.add(category);

    posts.push({
      slug,
      title: attrs.title || slug,
      date: dateStr,
      dateMeta,
      source,
      sourceLabel: attrs.source_label || (source === 'naver' ? 'Naver Blog' : source === 'facebook' ? 'Facebook' : source.toUpperCase()),
      category,
      tags: attrs.tags || [],
      excerpt: attrs.excerpt || '',
      media: attrs.media || [],
      body: parsed.body,
      html: marked(parsed.body),
    });
  }

  // Sort by date descending
  posts.sort((a, b) => new Date(b.date) - new Date(a.date));

  // Group by Year
  const yearGroups = {};
  for (const p of posts) {
    const yr = p.dateMeta.year;
    if (!yearGroups[yr]) yearGroups[yr] = [];
    yearGroups[yr].push(p);
  }
  const sortedYears = Object.keys(yearGroups).sort((a, b) => Number(b) - Number(a));

  const sourcesList = Array.from(sourcesSet);
  const categoriesList = Array.from(categoriesSet);

  // 1. Generate Individual Standalone Post Pages
  for (const post of posts) {
    const postHtml = `<!DOCTYPE html>
<html lang="ko" class="h-full antialiased dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#09090b">

  <title>${post.title} - History - brokolidev</title>
  <meta name="title" content="${post.title} - History - brokolidev">
  <meta name="description" content="${(post.excerpt || '').replace(/"/g, '&quot;')}">
  <link rel="canonical" href="https://history.brokolidev.com/posts/${post.slug}.html">

  ${getFaviconHtml('../')}

  <!-- Fonts & Styles -->
  <link rel="preconnect" href="https://rsms.me/">
  <link rel="stylesheet" href="https://rsms.me/inter/inter.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/style.css?v=20261010a">
  ${getHeadInitScript()}
  ${GA_TAG_HTML}
</head>
<body>
  ${getHeaderHtml('../')}

  <main class="main-wrapper">
    <div class="main-outer">
      <div class="main-inner">
        <div style="margin-bottom: 2rem;">
          <a href="../index.html" class="nav-tab-active" style="display: inline-flex; gap: 0.4rem;">
            <i class="fas fa-arrow-left" style="font-size: 0.75rem;"></i>
            <span>Timeline</span>
          </a>
        </div>

        <article class="history-item is-open" style="border: none; background: transparent; box-shadow: none;">
          <div class="history-meta-strip" style="border-top: 1px solid var(--border-subtle); padding-top: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
              <span class="badge-source badge-${post.source}">${post.sourceLabel}</span>
              <span>${post.date}</span>
              <span>•</span>
              <span>${post.category}</span>
            </div>
          </div>

          <h1 style="font-size: 1.85rem; font-weight: 800; letter-spacing: -0.03em; margin: 1rem 0 1.5rem; color: var(--text-main);">
            ${post.title}
          </h1>

          <div class="prose-content">
            ${post.html}
          </div>

          ${
            post.media && post.media.length > 0
              ? `<div class="history-media-grid">
                  ${post.media
                    .map(
                      (m) => `
                    <div class="history-media-item">
                      <img src="${m.src}" alt="${m.caption || ''}" loading="lazy">
                    </div>`
                    )
                    .join('')}
                </div>`
              : ''
          }
        </article>
      </div>
    </div>
  </main>

  ${getFooterHtml()}
  <script src="../js/main.js?v=20261010a"></script>
</body>
</html>`;

    fs.writeFileSync(path.join(DIST_POSTS_DIR, `${post.slug}.html`), postHtml, 'utf-8');
  }

  // 2. Generate History Timeline Index Page
  const timelineHtml = `<!DOCTYPE html>
<html lang="ko" class="h-full antialiased dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#09090b">

  <title>History & Memories - brokolidev</title>
  <meta name="title" content="History & Memories - brokolidev">
  <meta name="description" content="Personal history archive, past memories, essays, and photos from Naver Blog, Facebook, and more by Ted Choi.">
  <link rel="canonical" href="https://history.brokolidev.com/">

  ${getFaviconHtml('')}

  <!-- Fonts & Styles -->
  <link rel="preconnect" href="https://rsms.me/">
  <link rel="stylesheet" href="https://rsms.me/inter/inter.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/style.css?v=20261010a">
  ${getHeadInitScript()}
  ${GA_TAG_HTML}
</head>
<body>
  ${getHeaderHtml('')}

  <main class="main-wrapper">
    <div class="main-outer">
      <div class="main-inner">
        <!-- Hero Header -->
        <section class="history-hero">
          <h1 class="history-title">History & Memories</h1>

          <!-- Realtime Search Bar -->
          <div class="search-container">
            <i class="fas fa-search search-icon"></i>
            <input type="text" id="search-input" class="search-input" placeholder="키워드, 제목, 본문 검색 (예: 제주, 생각, 일상)...">
          </div>

          <!-- Dual Filter Bar (Platform & Category) -->
          <div class="filter-group">
            <div class="filter-row">
              <span class="filter-label">Platform</span>
              <div class="filter-chips">
                <button type="button" class="chip-btn active" data-filter-source="all">전체 (${posts.length})</button>
                ${sourcesList
                  .map(
                    (s) => `<button type="button" class="chip-btn" data-filter-source="${s}">
                    ${s === 'naver' ? '네이버' : s === 'facebook' ? '페이스북' : s.toUpperCase()}
                  </button>`
                  )
                  .join('')}
              </div>
            </div>

            <div class="filter-row">
              <span class="filter-label">Category</span>
              <div class="filter-chips">
                <button type="button" class="chip-btn active" data-filter-category="all">전체</button>
                ${categoriesList
                  .map((c) => `<button type="button" class="chip-btn" data-filter-category="${c}">${c}</button>`)
                  .join('')}
              </div>
            </div>
          </div>
        </section>

        <!-- Timeline Grouped by Year -->
        <section class="history-timeline">
          ${sortedYears
            .map(
              (year, yearIdx) => `
          <div class="year-block" id="year-${year}">
            <div class="year-heading">
              <span class="year-title">${year}</span>
              <span class="year-count-badge">${yearGroups[year].length}</span>
              <div class="year-divider"></div>
            </div>

            <div class="entries-list">
              ${yearGroups[year]
                .map(
                  (post, postIdx) => `
              <div class="history-item${yearIdx === 0 && postIdx === 0 ? ' is-open' : ''}" data-slug="${post.slug}" data-source="${post.source}" data-category="${post.category}">
                <div class="history-summary">
                  <div class="history-summary-left">
                    <span class="history-date">${post.dateMeta.monthDay}</span>
                    <span class="badge-source badge-${post.source}">${post.sourceLabel}</span>
                    <span class="history-title-text">${post.title}</span>
                  </div>
                  <div class="history-summary-right">
                    <i class="fas fa-chevron-down history-chevron"></i>
                  </div>
                </div>

                <div class="history-content">
                  <div class="history-meta-strip">
                    <div>
                      <span>Date: <strong>${post.date}</strong></span>
                      <span style="margin: 0 0.5rem; opacity: 0.5;">•</span>
                      <span>Category: <strong>${post.category}</strong></span>
                      ${
                        post.tags && post.tags.length > 0
                          ? `<span style="margin: 0 0.5rem; opacity: 0.5;">•</span><span>Tags: ${post.tags.map((t) => `#${t}`).join(' ')}</span>`
                          : ''
                      }
                    </div>
                  </div>

                  <div class="prose-content">
                    ${post.html}
                  </div>

                  ${
                    post.media && post.media.length > 0
                      ? `<div class="history-media-grid">
                          ${post.media
                            .map(
                              (m) => `
                            <div class="history-media-item">
                              <img src="${m.src}" alt="${m.caption || ''}" loading="lazy">
                            </div>`
                            )
                            .join('')}
                        </div>`
                      : ''
                  }
                </div>
              </div>`
                )
                .join('')}
            </div>
          </div>`
            )
            .join('')}
        </section>
      </div>
    </div>
  </main>

  ${getFooterHtml()}
  <script src="js/main.js?v=20261010a"></script>
</body>
</html>`;

  fs.writeFileSync(path.join(DIST_DIR, 'index.html'), timelineHtml, 'utf-8');
  fs.copyFileSync(path.join(__dirname, 'src', 'css', 'style.css'), path.join(DIST_DIR, 'css', 'style.css'));
  fs.copyFileSync(path.join(__dirname, 'src', 'js', 'main.js'), path.join(DIST_DIR, 'js', 'main.js'));
  fs.writeFileSync(path.join(__dirname, 'index.html'), timelineHtml, 'utf-8');

  copyDirRecursive(PUBLIC_DIR, DIST_DIR);
  copyDirRecursive(PUBLIC_DIR, __dirname);

  console.log(`✅ History archive build complete! Processed ${posts.length} entries across ${sortedYears.length} years.`);
}

build().catch((err) => {
  console.error('❌ Build failed:', err);
  process.exit(1);
});
