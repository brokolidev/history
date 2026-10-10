/* ==========================================================================
   brokoli.dev - History Timeline Client Scripts
   Interactive Theme, Platform & Category Filtering, Realtime Search, Accordion
   ========================================================================== */

(function () {
  'use strict';

  // --- 1. Theme Management ---
  function initTheme() {
    const themeBtn = document.getElementById('theme-toggle');
    const htmlEl = document.documentElement;

    function setTheme(dark) {
      if (dark) {
        htmlEl.classList.add('dark');
        localStorage.setItem('theme', 'dark');
      } else {
        htmlEl.classList.remove('dark');
        localStorage.setItem('theme', 'light');
      }
    }

    const saved = localStorage.getItem('theme');
    if (saved) {
      setTheme(saved === 'dark');
    } else {
      setTheme(window.matchMedia('(prefers-color-scheme: dark)').matches);
    }

    if (themeBtn) {
      themeBtn.addEventListener('click', () => {
        setTheme(!htmlEl.classList.contains('dark'));
      });
    }
  }

  // --- 2. Interactive Filtering & Search Engine ---
  function initFilters() {
    const searchInput = document.getElementById('search-input');
    const platformChips = document.querySelectorAll('[data-filter-source]');
    const categoryChips = document.querySelectorAll('[data-filter-category]');
    const items = document.querySelectorAll('.history-item');
    const yearBlocks = document.querySelectorAll('.year-block');

    let activeSource = 'all';
    let activeCategory = 'all';
    let searchQuery = '';

    function applyFilters() {
      items.forEach((item) => {
        const itemSource = (item.getAttribute('data-source') || '').toLowerCase();
        const itemCategory = (item.getAttribute('data-category') || '').toLowerCase();
        const itemText = (item.innerText || '').toLowerCase();

        const matchSource = activeSource === 'all' || itemSource === activeSource;
        const matchCategory = activeCategory === 'all' || itemCategory === activeCategory;
        const matchSearch = !searchQuery || itemText.includes(searchQuery);

        if (matchSource && matchCategory && matchSearch) {
          item.style.display = '';
        } else {
          item.style.display = 'none';
        }
      });

      // Update year block visibility
      yearBlocks.forEach((block) => {
        const visibleItems = block.querySelectorAll('.history-item:not([style*="display: none"])');
        block.style.display = visibleItems.length > 0 ? '' : 'none';
      });
    }

    // Platform chip click
    platformChips.forEach((chip) => {
      chip.addEventListener('click', () => {
        platformChips.forEach((c) => c.classList.remove('active'));
        chip.classList.add('active');
        activeSource = (chip.getAttribute('data-filter-source') || 'all').toLowerCase();
        applyFilters();
      });
    });

    // Category chip click
    categoryChips.forEach((chip) => {
      chip.addEventListener('click', () => {
        categoryChips.forEach((c) => c.classList.remove('active'));
        chip.classList.add('active');
        activeCategory = (chip.getAttribute('data-filter-category') || 'all').toLowerCase();
        applyFilters();
      });
    });

    // Search input
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        searchQuery = (e.target.value || '').trim().toLowerCase();
        applyFilters();
      });
    }
  }

  // --- 3. Accordion & Permalink Engine ---
  function initAccordion() {
    const items = document.querySelectorAll('.history-item');

    items.forEach((item) => {
      const summary = item.querySelector('.history-summary');
      if (!summary) return;

      summary.addEventListener('click', (e) => {
        if (e.target.closest('.permalink-btn')) return;
        item.classList.toggle('is-open');
      });
    });

    // Hash deep linking
    const hash = window.location.hash.replace(/^#/, '');
    if (hash) {
      const target = document.querySelector(`.history-item[data-slug="${hash}"]`);
      if (target) {
        target.classList.add('is-open');
        setTimeout(() => {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 150);
      }
    }
  }

  // --- 4. Code Block Copy Engine ---
  function initCodeCopy() {
    window.copyCodeBlock = function (btn) {
      const wrapper = btn.closest('.code-block-wrapper');
      if (!wrapper) return;
      const codeEl = wrapper.querySelector('pre code');
      if (!codeEl) return;

      const textToCopy = codeEl.innerText;
      navigator.clipboard.writeText(textToCopy).then(() => {
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check" style="color: #34d399;"></i> <span>Copied!</span>';
        btn.classList.add('copied');
        setTimeout(() => {
          btn.innerHTML = originalHtml;
          btn.classList.remove('copied');
        }, 2000);
      }).catch((err) => {
        console.error('Failed to copy code snippet:', err);
      });
    };
  }

  // Bootstrap
  function bootstrap() {
    initTheme();
    initFilters();
    initAccordion();
    initCodeCopy();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootstrap);
  } else {
    bootstrap();
  }
})();
