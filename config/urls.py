from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib.auth import get_user_model

def create_admin_temp(request):
    User = get_user_model()
    username = "admin"
    password = "ShuleTrack2026"
    email = "admin@shule.bi"
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        return HttpResponse(f"✅ Admin {username} créé ! Mot de passe: {password} <br> <a href='/admin/'>Aller au login admin</a>")
    else:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return HttpResponse(f"✅ Admin {username} mot de passe réinitialisé à: {password} <br> <a href='/admin/'>Aller au login admin</a>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ecole.urls')),
    path('creation-admin-2026/', create_admin_temp),
]
