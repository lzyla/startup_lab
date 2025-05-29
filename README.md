# Asystent AI – Django + Bootstrap

To jest MVP aplikacji webowej zbudowanej w Django z Bootstrapem, pozwalającej na wybór postaci AI i prowadzenie rozmowy z nimi.

## Funkcje
- Wybór jednej z wielu postaci AI
- Chat tekstowy z postacią
- Panel administratora do dodawania i edycji postaci
- Prosty interfejs oparty o Bootstrap

## Struktura projektu

- `ai_assistant_project/` – konfiguracja Django
- `backend/` – logika aplikacji (modele, widoki, formularze)
- `templates/` – widoki HTML
- `static/` – style CSS

## Jak uruchomić

1. Stwórz i aktywuj środowisko virtualne (opcjonalnie):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate  # Windows
   ```

2. Zainstaluj zależności:
   ```bash
   pip install django
   ```

3. Uruchom migracje i serwer:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

4. Wejdź na `http://127.0.0.1:8000/`

