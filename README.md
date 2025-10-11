# RE/MAX Astra - Strona Nieruchomości

Automatyczna strona internetowa RE/MAX Astra, która codziennie scrapuje najnowsze oferty nieruchomości i deployuje je na GitHub Pages.

## Funkcjonalności

- 🔄 **Automatyczne scrapowanie**: Codziennie o północy scrapuje nowe oferty z RE/MAX Polska
- 🏠 **Wyświetlanie ofert**: Prezentuje najnowsze oferty nieruchomości z obrazami i szczegółami
- 📱 **Responsywność**: Strona jest w pełni responsywna i działa na wszystkich urządzeniach
- 🚀 **Automatyczny deployment**: Automatycznie deployuje na GitHub Pages po każdym scrapowaniu

## Konfiguracja GitHub Pages

Aby uruchomić stronę na GitHub Pages, wykonaj następujące kroki:

### 1. Włącz GitHub Pages w ustawieniach repozytorium

1. Przejdź do **Settings** w swoim repozytorium GitHub
2. W lewym menu wybierz **Pages**
3. W sekcji **Source** wybierz **GitHub Actions**
4. Zapisz zmiany

### 2. Sprawdź uprawnienia workflow

Upewnij się, że workflow ma odpowiednie uprawnienia:
- W **Settings** → **Actions** → **General**
- W sekcji **Workflow permissions** wybierz **Read and write permissions**
- Zaznacz **Allow GitHub Actions to create and approve pull requests**

### 3. Uruchom workflow

Workflow uruchomi się automatycznie:
- Codziennie o północy (UTC)
- Po każdym push do brancha `master`
- Możesz też uruchomić go ręcznie w zakładce **Actions**

## Struktura projektu

```
remaxastra.pl/
├── .github/workflows/
│   ├── scrape_and_deploy.yml    # Główny workflow do scrapowania
│   └── pages.yml                # Workflow do deploymentu na GitHub Pages
├── static/                      # Pliki statyczne (CSS, JS, obrazy)
├── templates/
│   └── index.html              # Szablon HTML
├── scrapingscript.py           # Skrypt do scrapowania danych
├── generate_static_site.py     # Generator statycznej strony
├── app.py                      # Aplikacja Flask (używana lokalnie)
├── listings.db                 # Baza danych SQLite z ofertami
└── requirements.txt            # Zależności Python
```

## Jak to działa

1. **Scrapowanie**: `scrapingscript.py` używa Selenium do scrapowania ofert z RE/MAX Polska
2. **Generowanie**: `generate_static_site.py` tworzy statyczną stronę HTML z danych z bazy
3. **Deployment**: GitHub Actions automatycznie deployuje stronę na GitHub Pages
4. **Aktualizacja**: Proces powtarza się codziennie automatycznie

## Lokalne uruchomienie

Aby uruchomić stronę lokalnie:

```bash
# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom scrapowanie
python scrapingscript.py

# Wygeneruj statyczną stronę
python generate_static_site.py

# Uruchom serwer Flask (opcjonalnie)
python app.py
```

## Wymagania

- Python 3.12+
- Chrome/Chromium browser
- ChromeDriver
- Wszystkie zależności z `requirements.txt`

## Kontakt

RE/MAX Astra Warszawa
- Telefon: +48 505 028 658
- Adres: Łopuszańska 24g, 02-220 Warszawa
- Strona: https://remaxastra.pl
