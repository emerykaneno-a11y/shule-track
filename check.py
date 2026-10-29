import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
django.setup()
from django.template.loader import get_template
t=get_template("ecole/dashboard.html")
print(t.origin.name)
