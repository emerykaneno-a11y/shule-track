import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = "admin"
password = "Shule track2026"
email = "admin@shule.bi"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"✅ Admin {username} créé avec succès !")
else:
    print(f"Admin {username} existe déjà")
