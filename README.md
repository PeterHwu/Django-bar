# Django Bar

This is the Bar Django project. Auto-generated API docs are in the `docs/` folder.

Quick start

1. Create a virtualenv and install dependencies (this project uses Pipenv):

```powershell
pipenv install --dev
pipenv shell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

2. API docs

- `docs/API.md` — API endpoints and examples
- `docs/models.md` — model field descriptions

Notes

- Ensure Django REST Framework is configured in `settings.py`.
- The app expects user groups named `Customer`, `Manager`, and `Delivery` for permission checks.
