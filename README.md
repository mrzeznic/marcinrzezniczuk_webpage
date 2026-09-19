# Marcin Rzeźniczuk – Personal Expert Website

Oficjalna, dwujęzyczna (EN/PL) strona internetowa **Marcina Rzeźniczuka** – Technical Project Manager & AI Product Lead. Serwis prezentuje ponad 10 lat doświadczenia w realizacji złożonych inicjatyw technologicznych, zwinnego dostarczania produktów opartych o LLM/AI (Agile/TPM) oraz solidnych fundamentach architektonicznych platform danych (Modern Data Stack, Lakehouses) dla sektora farmaceutycznego, logistycznego i korporacyjnego.

Strona jest wdrożona na **GitHub Pages** i dostępna pod domeną [www.marcinrzezniczuk.pl](https://www.marcinrzezniczuk.pl).

---

## 🧭 Kluczowe moduły strony

### 1. Doświadczenie Zawodowe (Career Track Record)
- **C&F (2025 – obecnie):** Technical Project Manager – zarządzanie produktami i inicjatywami chmurowymi dla globalnych koncernów farmaceutycznych, optymalizacja strumienia wartości (Value Stream), orkiestracja wdrożeń AI/LLM i facylitacja delivery.
- **C&F (2023 – 2025):** Senior Data Engineer / Team Coordinator – architektura ETL/ELT (Snowflake, dbt), koordynacja zwinnych zespołów inżynierskich i standardy Data Governance.
- **C&F (2020 – 2023):** Data Engineer – projektowanie potoków danych, modelowanie struktur hurtowni w chmurze i integracja procesów ETL/ELT (Snowflake, SQL, Python).
- **JLL (2020):** Associate, Data & Analytics – modelowanie hurtowni danych i rozwój backendu analitycznego (Snowflake, MS SQL Server, Python).
- **DB Schenker (2017 – 2019):** Data Engineer & Service Consultant – PoC Apache Airflow, konteneryzacja Docker, wdrożenie Scrum i pipeline'y dla Data Science.
- **T-Mobile Polska & Danone (2015 – 2017):** Analityka biznesowa, wsparcie systemów SAP ERP i automatyzacja raportowania.

### 2. Akredytacje i Certyfikaty
- **AI & Automation:** AI_devs 4 Builders (2026), AI_devs 3 Agents (2025), AI Devs 2 (2024), Google AI in Business Development, AI_managers 2.
- **Agile Leadership & Management:** Professional Scrum Master™ I (Scrum.org PSM I), Kanban Management Professional (Kanban University KMP, KSI, KSD), First Time Manager (EY Academy of Business), ITIL Foundation.
- **Data Platforms:** Snowflake Hands On Essentials (Data Engineering, DWH, Data Applications, Sharing), Python, DataCamp, DataWorkshop ML Challenges.

### 3. Portfolio Kompetencji (9 obszarów)
- **Data & AI Solutions:** AI Product Management & Advisory, Data-Driven Business Consulting, Data Architecture & Engineering, Business Intelligence & Reporting.
- **Delivery & Agile Leadership:** Scrum, Agile Leadership, Data Team Leadership, Data Projects Management (TPM), Kanban Coaching & Implementation.

---

## 🛠️ Architektura i technologie

- **Frontend:** Czysty HTML5 zoptymalizowany pod kątem Core Web Vitals i urządzeń mobilnych.
- **Styling:** Tailwind CSS (CDN) z dynamicznymi geometrycznymi motywami w odcieniach błękitu i kobaltu.
- **Wielojęzyczność & SEO (i18n):** 
  - Fizyczne, dedykowane adresy URL pod kątem wyszukiwarek (Googlebot):
    - **`https://www.marcinrzezniczuk.pl/`** – wersja angielska (`lang="en"`, 100% czysty angielski kod HTML).
    - **`https://www.marcinrzezniczuk.pl/pl/`** – wersja polska (`lang="pl"`, 100% czysty polski kod HTML).
  - Wzajemne powiązanie tagami `<link rel="alternate" hreflang="..." />` (en, pl, x-default) oraz deklaracja w `sitemap.xml` (`xhtml:link`).
  - Pojedyncze źródło prawdy: `src/template.html` – kompilowane skryptem `build_i18n.py`.
- **Hosting & CI/CD:** GitHub Pages napędzane procesem GitHub Actions (`.github/workflows/deploy.yml`).

---

## 💻 Podgląd lokalny i kompilacja (Live Reload)

Repozytorium zawiera gotowy skrypt deweloperski [`serve.py`](./serve.py), który automatycznie kompiluje wersje językowe (`build_i18n.py`) i odświeża stronę w przeglądarce przy każdej zmianie w `src/template.html`:

```bash
python3 serve.py
# lub bezpośrednio kompilacja stron:
python3 build_i18n.py
```

Skrypt automatycznie otworzy adres [http://localhost:8000](http://localhost:8000) w domyślnej przeglądarce. Korzysta wyłącznie ze standardowej biblioteki Pythona 3.

---

## 🚀 Wdrażanie zmian (Deployment)

Repozytorium posiada w pełni automatyczny pipeline CI/CD. Każdy push na gałąź `main` natychmiast publikuje nową wersję strony:

```bash
git add .
git commit -m "feat: wzbogacenie strony o doświadczenie enterprise i certyfikaty z LinkedIn"
git push origin main
```