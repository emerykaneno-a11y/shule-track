import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Sur Vercel on crée les tables automatiquement
if os.environ.get('VERCEL'):
    try:
        application = get_wsgi_application()
        call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)
    except Exception:
        pass

application = get_wsgi_application()
app = application
