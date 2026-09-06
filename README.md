# Marcin Rzeźniczuk – Wizytówka B2B (GitHub Pages)

Nowoczesna, responsywna strona wizytówka B2B dla roli **Technical Project Manager & Senior Data Engineer**, zoptymalizowana pod kątem szybkości ładowania, urządzeń mobilnych oraz bezobsługowego wdrożenia na **GitHub Pages** z obsługą domeny niestandardowej.

---

## 🚀 Wymagane kroki po stronie użytkownika (Konfiguracja)

Przed pierwszym wdrożeniem lub tuż po nim wykonaj dwa poniższe kroki:

### 1. Podmiana adresu domeny w pliku `CNAME`
Otwórz plik [`CNAME`](./CNAME) znajdujący się w katalogu głównym repozytorium i zastąp tymczasową wartość `twojadomena.pl` swoją docelową domeną (np. `marcinrzezniczuk.pl`).
> **Wskazówka:** W pliku [`index.html`](./index.html) możesz również podmienić docelowy adres w linku e-mail (`mailto:kontakt@twojadomena.pl`) na swój rzeczywisty adres kontaktowy.

### 2. Włączenie opcji "GitHub Actions" w ustawieniach repozytorium
1. Przejdź do repozytorium na GitHubie.
2. Wejdź w zakładkę **Settings** &rarr; **Pages** (w menu po lewej stronie).
3. W sekcji **Build and deployment** zmień pole **Source** z *Deploy from a branch* na **GitHub Actions**.
4. Po wypchnięciu zmian na gałąź `main` (lub `master`), akcja wdrożeniowa uruchomi się automatycznie i opublikuje witrynę pod podpiętą domeną z certyfikatem SSL.

---

## 🛠️ Architektura i technologie

- **HTML5 & Semantic Web:** Lekki, semantyczny kod zoptymalizowany pod SEO i urządzenia mobilne.
- **Tailwind CSS (CDN):** Minimalistyczny, biznesowy styl bazujący na odcieniach bieli, szarości (`slate`) oraz akcentach niebieskich (`blue`).
- **GitHub Actions (`.github/workflows/deploy.yml`):** Automatyczny pipeline CI/CD wdrażający stronę przy każdym pushu do gałęzi `main`/`master` z użyciem oficjalnych akcji GitHub Pages (`checkout@v4`, `upload-pages-artifact@v3`, `deploy-pages@v4`).
- **CNAME:** Konfiguracja routingu niestandardowej domeny DNS.

---

## 📁 Struktura repozytorium

```text
.
├── .github/
│   └── workflows/
│       └── deploy.yml    # Pipeline automatycznego wdrożenia na GitHub Pages
├── CNAME                 # Plik konfiguracji własnej domeny
├── index.html            # Główny plik strony wizytówki B2B (HTML5 + Tailwind CSS)
└── README.md             # Dokumentacja projektu i instrukcja wdrożenia
```

---

## 💻 Podgląd lokalny

Strona nie wymaga żadnych narzędzi budujących (zero-build setup). Aby podejrzeć ją lokalnie, wystarczy otworzyć plik `index.html` bezpośrednio w przeglądarce lub uruchomić prosty serwer HTTP:

```bash
python3 -m http.server 8000
```
Następnie przejdź w przeglądarce pod adres [http://localhost:8000](http://localhost:8000).