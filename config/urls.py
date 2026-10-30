from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib.auth import get_user_model

def create_admin_temp(request):
    User = get_user_model()
    username = "admin"
    password = "Shule track2026"
    email = "admin@shule.bi"
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        return HttpResponse(f"✅ Admin {username} créé ! Mot de passe: {password} <br> <a href='/'>Aller au login</a>")
    else:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        return HttpResponse(f"✅ Admin {username} existe déjà, mot de passe réinitialisé à: {password} <br> <a href='/'>Aller au login</a>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ecole.urls')),
    path('creation-admin-2026/', create_admin_temp),
]
