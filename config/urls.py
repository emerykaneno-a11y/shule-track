from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib.auth import get_user_model, authenticate

def create_admin_temp(request):
    User = get_user_model()
    username = "admin"
    password = "ShuleTrack2026"
    email = "admin@shule.bi"
    
    # Crée ou met à jour
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
    else:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
    
    # Vérifie immédiatement si ça marche
    user_check = authenticate(username=username, password=password)
    if user_check:
        status = f"✅✅✅ IDENTIFIANTS VALIDES ! <br><br> Username: {username} <br> Password: {password} <br><br> Le login MARCHE, mais Vercel avec SQLite efface tout au prochain clic. Il faut passer à Postgres."
    else:
        status = "❌ Echec authentification"
    
    return HttpResponse(f"{status} <br><br> <a href='/admin/'>Essayer quand même d'aller à /admin/</a>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ecole.urls')),
    path('creation-admin-2026/', create_admin_temp),
]
