#!/usr/bin/env python3
"""
BEEDATA – Bilingual Site Compiler
Generates physical, search-engine-optimized English (/) and Polish (/pl/) pages
from the master template (src/template.html) with full hreflang and canonical support.
Zero external dependencies (pure Python 3 standard library).
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "src" / "template.html"
OUT_EN_PATH = BASE_DIR / "index.html"
OUT_PL_PATH = BASE_DIR / "pl" / "index.html"

def compile_pages():
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found at {TEMPLATE_PATH}")

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        src = f.read()

    en_content = generate_en(src)
    pl_content = generate_pl(src)

    with open(OUT_EN_PATH, "w", encoding="utf-8") as f:
        f.write(en_content)

    OUT_PL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PL_PATH, "w", encoding="utf-8") as f:
        f.write(pl_content)

    print(f"✓ Generated English page: {OUT_EN_PATH} ({len(en_content):,} bytes)")
    print(f"✓ Generated Polish page:  {OUT_PL_PATH} ({len(pl_content):,} bytes)")

def clean_css(html: str) -> str:
    # Remove old display: none CSS for lang classes
    old_css = re.compile(
        r'/\*\s*Przełączanie wersji językowej[^*]*\*/\s*'
        r'body\.lang-en \.lang-pl\s*\{\s*display:\s*none\s*!important;\s*\}\s*'
        r'body\.lang-pl \.lang-en\s*\{\s*display:\s*none\s*!important;\s*\}',
        re.DOTALL
    )
    html = old_css.sub('', html)

    # Clean body class
    html = html.replace('class="lang-en bg-', 'class="bg-')
    html = html.replace('class="lang-pl bg-', 'class="bg-')
    return html

def generate_en(template: str) -> str:
    c = template

    # 1. HTML lang attribute
    c = re.sub(r'<html lang="[^"]*"', '<html lang="en"', c, count=1)

    # 2. Canonical & Hreflang
    canonical_hreflang = """  <link rel="canonical" href="https://www.marcinrzezniczuk.pl/" />
  <link rel="alternate" hreflang="en" href="https://www.marcinrzezniczuk.pl/" />
  <link rel="alternate" hreflang="pl" href="https://www.marcinrzezniczuk.pl/pl/" />
  <link rel="alternate" hreflang="x-default" href="https://www.marcinrzezniczuk.pl/" />"""
    c = re.sub(r'  <link rel="canonical" href="[^"]*" />', canonical_hreflang, c, count=1)

    # 3. Meta description
    en_desc = "Official portfolio of Marcin Rzeźniczuk. 10+ years in IT, bridging data architecture and AI systems with agile product delivery (TPM / AI Product Lead). Experience in Pharma, Logistics, and Enterprise."
    c = re.sub(r'<meta name="description" content="[^"]*" />', f'<meta name="description" content="{en_desc}" />', c, count=1)

    # 4. OpenGraph & Twitter tags
    c = re.sub(r'<meta property="og:url" content="[^"]*" />', '<meta property="og:url" content="https://www.marcinrzezniczuk.pl/" />', c, count=1)
    c = re.sub(r'<meta property="og:locale" content="[^"]*" />', '<meta property="og:locale" content="en_US" />', c, count=1)
    c = re.sub(r'<meta property="og:locale:alternate" content="[^"]*" />', '<meta property="og:locale:alternate" content="pl_PL" />', c, count=1)
    c = re.sub(r'<meta name="twitter:url" content="[^"]*" />', '<meta name="twitter:url" content="https://www.marcinrzezniczuk.pl/" />', c, count=1)

    # 5. Language switcher buttons
    en_switcher = """        <!-- Przełącznik języka EN / PL -->
        <div class="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 shadow-2xs" role="group" aria-label="Language selector">
          <span id="btn-en" class="px-3 py-1 text-xs font-bold rounded-lg bg-blue-600 text-white shadow-xs" aria-current="page" aria-label="English language active">
            EN
          </span>
          <a id="btn-pl" href="/pl/" class="px-3 py-1 text-xs font-bold rounded-lg transition-all text-slate-600 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2" aria-label="Przełącz na język polski">
            PL
          </a>
        </div>"""
    switcher_pattern = re.compile(
        r'<!-- Przełącznik języka EN / PL -->\s*<div[^>]*role="group"[^>]*>.*?</div>',
        re.DOTALL
    )
    c = switcher_pattern.sub(en_switcher, c, count=1)

    # 6. Copy button element
    c = c.replace(
        '<span id="copy-text-en" class="lang-en">Copy Email</span>\n                <span id="copy-text-pl" class="lang-pl">Kopiuj Email</span>',
        '<span id="copy-text">Copy Email</span>'
    )

    # 7. Remove Polish blocks
    c = re.sub(r'\s*<(span|div|p|h[1-6])[^>]*class="[^"]*lang-pl[^"]*"[^>]*>.*?</\1>', '', c, flags=re.DOTALL)

    # 8. Unwrap English spans
    c = re.sub(r'<span class="lang-en">(.*?)</span>', r'\1', c, flags=re.DOTALL)

    # 9. Clean CSS
    c = clean_css(c)

    # 10. Dedicated clean script for English page
    en_script = """  <!-- Skrypt obsługujący kopiowanie do schowka -->
  <script>
    function copyEmailToClipboard() {
      const email = 'marcin.rzezniczuk@gmail.com';
      const textSpan = document.getElementById('copy-text');
      const origText = textSpan ? textSpan.textContent : 'Copy Email';

      function showFeedback() {
        if (textSpan) textSpan.textContent = 'Copied!';
        setTimeout(() => {
          if (textSpan) textSpan.textContent = origText;
        }, 2000);
      }

      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(email).then(showFeedback).catch(() => {
          fallbackCopy(email, showFeedback);
        });
      } else {
        fallbackCopy(email, showFeedback);
      }
    }

    function fallbackCopy(text, callback) {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-9999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        document.execCommand('copy');
        callback();
      } catch (err) {
        console.error('Fallback copy failed', err);
      }
      document.body.removeChild(textArea);
    }
  </script>"""

    script_pattern = re.compile(
        r'<!-- Skrypt obsługujący przełącznik wersji językowej i schowek -->\s*<script>.*?</script>',
        re.DOTALL
    )
    c = script_pattern.sub(en_script, c, count=1)

    return c

def generate_pl(template: str) -> str:
    c = template

    # 1. HTML lang attribute
    c = re.sub(r'<html lang="[^"]*"', '<html lang="pl"', c, count=1)

    # 2. Canonical & Hreflang
    canonical_hreflang = """  <link rel="canonical" href="https://www.marcinrzezniczuk.pl/pl/" />
  <link rel="alternate" hreflang="pl" href="https://www.marcinrzezniczuk.pl/pl/" />
  <link rel="alternate" hreflang="en" href="https://www.marcinrzezniczuk.pl/" />
  <link rel="alternate" hreflang="x-default" href="https://www.marcinrzezniczuk.pl/" />"""
    c = re.sub(r'  <link rel="canonical" href="[^"]*" />', canonical_hreflang, c, count=1)

    # 3. Meta description
    pl_desc = "Oficjalne portfolio Marcina Rzeźniczuka. Ponad 10 lat w IT: zwinne zarządzanie projektami technologicznymi (Agile/TPM), wdrażanie produktów AI/LLM i nowoczesna architektura danych w sektorze Pharma i Enterprise."
    c = re.sub(r'<meta name="description" content="[^"]*" />', f'<meta name="description" content="{pl_desc}" />', c, count=1)

    # 4. OpenGraph & Twitter tags
    pl_og_desc = "Łączę głębokie zrozumienie architektury danych i systemów AI ze zwinnym dostarczaniem produktów technologicznych (Agile/TPM). Ponad dekada doświadczenia w transformacjach enterprise."
    c = re.sub(r'<meta property="og:description" content="[^"]*" />', f'<meta property="og:description" content="{pl_og_desc}" />', c, count=1)
    c = re.sub(r'<meta property="og:url" content="[^"]*" />', '<meta property="og:url" content="https://www.marcinrzezniczuk.pl/pl/" />', c, count=1)
    c = re.sub(r'<meta property="og:locale" content="[^"]*" />', '<meta property="og:locale" content="pl_PL" />', c, count=1)
    c = re.sub(r'<meta property="og:locale:alternate" content="[^"]*" />', '<meta property="og:locale:alternate" content="en_US" />', c, count=1)
    c = re.sub(r'<meta name="twitter:url" content="[^"]*" />', '<meta name="twitter:url" content="https://www.marcinrzezniczuk.pl/pl/" />', c, count=1)
    c = re.sub(r'<meta name="twitter:description" content="[^"]*" />', f'<meta name="twitter:description" content="{pl_og_desc}" />', c, count=1)

    # 5. Language switcher buttons
    pl_switcher = """        <!-- Przełącznik języka EN / PL -->
        <div class="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 shadow-2xs" role="group" aria-label="Wybór języka">
          <a id="btn-en" href="/" class="px-3 py-1 text-xs font-bold rounded-lg transition-all text-slate-600 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2" aria-label="Switch to English language">
            EN
          </a>
          <span id="btn-pl" class="px-3 py-1 text-xs font-bold rounded-lg bg-blue-600 text-white shadow-xs" aria-current="page" aria-label="Język polski aktywny">
            PL
          </span>
        </div>"""
    switcher_pattern = re.compile(
        r'<!-- Przełącznik języka EN / PL -->\s*<div[^>]*role="group"[^>]*>.*?</div>',
        re.DOTALL
    )
    c = switcher_pattern.sub(pl_switcher, c, count=1)

    # 6. JSON-LD URL & language
    c = c.replace('"url": "https://www.marcinrzezniczuk.pl/"', '"url": "https://www.marcinrzezniczuk.pl/pl/"')
    c = c.replace('"inLanguage": ["en", "pl"]', '"inLanguage": "pl"')
    pl_jsonld_desc = "Technical Project Manager & AI Product Lead z ponad 10-letnim doświadczeniem w dostarczaniu systemów AI/LLM, nowoczesnych architektur danych oraz zwinnych strumieni wartości."
    c = re.sub(
        r'"description": "Technical Project Manager & AI Product Lead with over a decade of experience delivering enterprise AI/LLM products, modern cloud data architectures, and agile value streams\."',
        f'"description": "{pl_jsonld_desc}"',
        c
    )

    # 7. Copy button element
    c = c.replace(
        '<span id="copy-text-en" class="lang-en">Copy Email</span>\n                <span id="copy-text-pl" class="lang-pl">Kopiuj Email</span>',
        '<span id="copy-text">Kopiuj Email</span>'
    )

    # 8. Remove English blocks
    c = re.sub(r'\s*<(span|div|p|h[1-6])[^>]*class="[^"]*lang-en[^"]*"[^>]*>.*?</\1>', '', c, flags=re.DOTALL)

    # 9. Unwrap Polish spans
    c = re.sub(r'<span class="lang-pl">(.*?)</span>', r'\1', c, flags=re.DOTALL)

    # 10. Clean CSS
    c = clean_css(c)

    # 11. Dedicated clean script for Polish page
    pl_script = """  <!-- Skrypt obsługujący kopiowanie do schowka -->
  <script>
    function copyEmailToClipboard() {
      const email = 'marcin.rzezniczuk@gmail.com';
      const textSpan = document.getElementById('copy-text');
      const origText = textSpan ? textSpan.textContent : 'Kopiuj Email';

      function showFeedback() {
        if (textSpan) textSpan.textContent = 'Skopiowano!';
        setTimeout(() => {
          if (textSpan) textSpan.textContent = origText;
        }, 2000);
      }

      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(email).then(showFeedback).catch(() => {
          fallbackCopy(email, showFeedback);
        });
      } else {
        fallbackCopy(email, showFeedback);
      }
    }

    function fallbackCopy(text, callback) {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-9999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        document.execCommand('copy');
        callback();
      } catch (err) {
        console.error('Fallback copy failed', err);
      }
      document.body.removeChild(textArea);
    }
  </script>"""

    script_pattern = re.compile(
        r'<!-- Skrypt obsługujący przełącznik wersji językowej i schowek -->\s*<script>.*?</script>',
        re.DOTALL
    )
    c = script_pattern.sub(pl_script, c, count=1)

    return c

if __name__ == "__main__":
    compile_pages()
