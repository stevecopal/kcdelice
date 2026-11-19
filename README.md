# KCDélices

Application web Django de l'entreprise événementielle : site public dynamique, administration privée et gestion complète des devis.

## Stack

| Composant | Version | Rôle |
| --- | --- | --- |
| Python | 3.14 (`.python-version` : 3.14) | Runtime |
| Django | 6.1.3 | Framework web |
| Tailwind CSS | 4.3.5 (`@tailwindcss/cli`) | Styles |
| Pillow | 13.0.0 | Traitement des images |
| psycopg | 3.3.9 (`[binary]`) | Pilote PostgreSQL |
| SQLite | 3.50.4 (module `sqlite3` de Python) | Base de développement |
| WeasyPrint | 70.0 | Génération PDF |
| Gunicorn | 27.0.1 | Serveur WSGI de production |
| pytest / pytest-django / pytest-cov | 9.2.0 / 4.14.0 / 7.1.0 | Tests |

Les versions réellement installées sont verrouillées dans `uv.lock`. Aucun `requirements.txt` n'est utilisé.

## Prérequis

- [uv](https://docs.astral.sh/uv/) (gère Python et l'environnement virtuel) ;
- Node.js 20+ et npm (uniquement pour compiler Tailwind CSS) ;
- PostgreSQL 16+ côté production (inutile en développement, SQLite suffit) ;
- bibliothèques système de WeasyPrint : `libpango-1.0-0`, `libcairo2`, `libgdk-pixbuf-2.0-0`.

## Installation

```bash
# Crée .venv avec la version de Python demandée et installe les dépendances verrouillées
uv sync

# Ajouter / retirer une dépendance (met à jour pyproject.toml et uv.lock)
uv add <paquet>
uv add --dev <paquet>
uv remove <paquet>

# Régénérer le verrou sans installer
uv lock

# Installer strictement ce que contient uv.lock (CI, production)
uv sync --locked
```

Compiler les styles :

```bash
npm install          # une seule fois
npm run build:css    # génère static/css/output.css
npm run watch:css    # reconstruction à la volée en développement
```

## Lancement

Développement (SQLite, `db.sqlite3`) :

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

Tests :

```bash
uv run pytest
uv run pytest --cov            # avec rapport de couverture
```

Contrôle de configuration :

```bash
uv run python manage.py check
```

Production (PostgreSQL, paramètres lus depuis l'environnement, jamais SQLite) :

```bash
uv sync --locked
npm ci && npm run build:css
uv run python manage.py collectstatic --noinput
uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## Structure

```
config/         réglages, URLs et points d'entrée WSGI/ASGI
core/           site public, administration, authentification, dashboard
devis/          gestion des devis, calculs et génération PDF
static/css/     input.css (source Tailwind) et output.css (compilé)
static/js/      JavaScript centralisé
templates/      gabarits Django
```
