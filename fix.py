import pathlib
# --- Corrige settings.py pour désactiver le cache ---
settings_path = pathlib.Path("config/settings.py")
settings_content = '''from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "changez-moi-avant-la-mise-en-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ecole",
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
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        },
    },
]
WSGI_APPLICATION = "config.wsgi.application"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Bujumbura"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
HEURE_LIMITE_RETARD = "07:30"
DUREE_EMPRUNT_JOURS = 14
DELAI_ANTI_DOUBLON_SECONDES = 10
'''
settings_path.write_text(settings_content, encoding='utf-8')
print("settings.py OK")

# --- Corrige dashboard.html ---
p = pathlib.Path("ecole/templates/ecole/dashboard.html")
t = p.read_text(encoding='utf-8', errors='ignore')
t = t.replace('tel:{{ s.telephone_parent }}','https://wa.me/{{ s.telephone_parent }}')
t = t.replace('tel:{{s.telephone_parent}}','https://wa.me/{{ s.telephone_parent }}')
t = t.replace('Appeler parent','WhatsApp parent')
p.write_text(t, encoding='utf-8')
print("dashboard.html OK ->", 'WhatsApp' in t)