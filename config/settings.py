

from pathlib import Path

from decouple import Csv, config
from django.core.exceptions import ImproperlyConfigured

# Chemins de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# 1. Profil de fonctionnement (développement / production)
# ---------------------------------------------------------------------------
DEBUG = config("DEBUG", default=True, cast=bool)
IS_PRODUCTION = not DEBUG

# ---------------------------------------------------------------------------
# 2. Secrets et hôtes autorisés
# ---------------------------------------------------------------------------
SECRET_KEY = config("SECRET_KEY", default="")
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "SECRET_KEY manquant : copiez .env.example vers .env et renseignez une valeur."
    )

if IS_PRODUCTION:
    ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())
    if not ALLOWED_HOSTS:
        raise ImproperlyConfigured(
            "ALLOWED_HOSTS doit être renseigné en production (variable du .env)."
        )
else:
    ALLOWED_HOSTS = config(
        "ALLOWED_HOSTS", default="localhost,127.0.0.1,[::1]", cast=Csv()
    )

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())

# ---------------------------------------------------------------------------
# 3. Applications et middleware
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Applications du projet (jamais de troisième application)
    "core",
    "devis",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.company",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# 4. Base de données — SQLite en développement, PostgreSQL en production
#    (jamais SQLite en production, aucune détection automatique)
# ---------------------------------------------------------------------------
if IS_PRODUCTION:
    _postgres = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default=""),
        "USER": config("POSTGRES_USER", default=""),
        "PASSWORD": config("POSTGRES_PASSWORD", default=""),
        "HOST": config("POSTGRES_HOST", default=""),
        "PORT": config("POSTGRES_PORT", default="5432"),
        "CONN_MAX_AGE": 60,
        "OPTIONS": {"connect_timeout": 10},
    }
    _required = {"NAME": "POSTGRES_DB", "USER": "POSTGRES_USER", "HOST": "POSTGRES_HOST"}
    _missing = [var for attr, var in _required.items() if not _postgres[attr]]
    if _missing:
        raise ImproperlyConfigured(
            "Configuration PostgreSQL de production incomplète — "
            f"variables manquantes : {', '.join(_missing)}."
        )
    DATABASES = {"default": _postgres}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            "OPTIONS": {"timeout": 20},
        }
    }

# ---------------------------------------------------------------------------
# 5. Authentification — modèle utilisateur personnalisé à clé UUID
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "core.User"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ---------------------------------------------------------------------------
# 6. Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Douala"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# 7. Fichiers statiques et médias
#    Développement : sources dans static/ servies par Django.
#    Production    : collecte dans staticfiles/ (manifest) + médias dans media/,
#                    servis par le reverse proxy.
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

if IS_PRODUCTION:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
        },
    }
else:
    STATICFILES_DIRS = [BASE_DIR / "static"]

# ---------------------------------------------------------------------------
# 8. Sessions et messages
# ---------------------------------------------------------------------------
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 60 * 60 * 12  # 12 heures
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

MESSAGE_STORAGE = "django.contrib.messages.storage.fallback.FallbackStorage"

# ---------------------------------------------------------------------------
# 9. Cache (progressif / hors ligne côté administration géré côté client)
# ---------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "kcdelice-cache",
    }
}



# ---------------------------------------------------------------------------
# 11. Journalisation (logs)
# ---------------------------------------------------------------------------
LOG_LEVEL = config("LOG_LEVEL", default="INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose" if IS_PRODUCTION else "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "core": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "devis": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}

# ---------------------------------------------------------------------------
# 12. Sécurité — durcissement actif uniquement en production
# ---------------------------------------------------------------------------
X_FRAME_OPTIONS = "SAMEORIGIN"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

if IS_PRODUCTION:
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = "DENY"
    # Reverse proxy (nginx, etc.) qui termine le TLS
    if config("USE_X_FORWARDED_PROTO", default=True, cast=bool):
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ---------------------------------------------------------------------------
# 13. Divers
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
