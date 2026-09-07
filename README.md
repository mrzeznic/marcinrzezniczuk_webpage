# Marcin Rzeźniczuk – Personal Expert Website

Oficjalna, dwujęzyczna (EN/PL) strona internetowa **Marcina Rzeźniczuka** – Technical Project Manager & Senior Data Engineer. Serwis prezentuje ponad 10 lat komercyjnego doświadczenia w inżynierii nowoczesnych platform danych (Modern Data Stack) oraz zwinnym przywództwie i zarządzaniu projektami technologicznymi (Agile Delivery, Scrum, Kanban) dla sektora farmaceutycznego, logistycznego i korporacyjnego.

Strona jest wdrożona na **GitHub Pages** i dostępna pod domeną [www.marcinrzezniczuk.pl](https://www.marcinrzezniczuk.pl).

---

## 🧭 Kluczowe moduły strony

### 1. Doświadczenie Zawodowe (Career Track Record)
- **C&F (Sep 2025 – Present):** Technical Project Manager – projekty chmurowe dla globalnych koncernów farmaceutycznych, automatyzacja potoków (Snowflake, dbt, Airflow), facylitacja Kanban i wdrażanie agentów AI.
- **C&F / BeeData (Apr 2023 – Sep 2025):** Senior Data Engineer / Team Coordinator – architektura ETL/ELT, mentoring techniczny i koordynacja zwinna zespołów inżynierskich.
- **JLL (2020):** Associate, Data & Analytics – modelowanie hurtowni danych i rozwój backendu (Snowflake, MS SQL Server, Python).
- **DB Schenker (2017 – 2019):** Data Engineer & Service Consultant – PoC Apache Airflow, konteneryzacja Docker, wdrożenie Scrum i pipeline'y dla Data Science.
- **T-Mobile Polska & Danone (2015 – 2017):** Analityka biznesowa, wsparcie systemów SAP ERP i automatyzacja raportowania.

### 2. Akredytacje i Certyfikaty
- **AI & Automation:** AI_devs 4 Builders (2026), AI_devs 3 Agents (2025), AI Devs 2 (2024), Google AI in Business Development, AI_managers 2.
- **Agile Leadership & Management:** Professional Scrum Master™ I (Scrum.org PSM I), Kanban Management Professional (Kanban University KMP, KSI, KSD), First Time Manager (EY Academy of Business), ITIL Foundation.
- **Data Platforms:** Snowflake Hands On Essentials (Data Engineering, DWH, Data Applications, Sharing), Python, DataCamp, DataWorkshop ML Challenges.

### 3. Portfolio Kompetencji (9 obszarów)
- **Data & AI Solutions:** Data Engineering, Data and AI Consulting, Data-Driven Business Consulting, Business Intelligence & Reporting.
- **Delivery & Agile Leadership:** Scrum, Agile Leadership, Data Team Leadership, Data Projects Management (TPM), Kanban Coaching & Implementation.

---

## 🛠️ Architektura i technologie

- **Frontend:** Czysty HTML5 zoptymalizowany pod kątem Core Web Vitals i urządzeń mobilnych.
- **Styling:** Tailwind CSS (CDN) z dynamicznymi geometrycznymi motywami w odcieniach błękitu i kobaltu.
- **Wielojęzyczność (i18n):** Domyślny język angielski (EN) z możliwością natychmiastowego przełączenia na język polski (PL) za pomocą przycisku w nagłówku i pamięcią wyboru (`localStorage`).
- **Hosting & CI/CD:** GitHub Pages napędzane procesem GitHub Actions (`.github/workflows/deploy.yml`).

---

## 💻 Podgląd lokalny z automatycznym odświeżaniem (Live Reload)

Repozytorium zawiera gotowy skrypt deweloperski [`serve.py`](./serve.py), który uruchamia lokalny serwer i **automatycznie odświeża otwartą stronę w przeglądarce za każdym razem, gdy zapiszesz zmiany w plikach**:

```bash
python3 serve.py
# lub bezpośrednio:
./serve.py
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