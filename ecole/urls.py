from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("scan/", views.scan, name="scan"),
    path("scan/api/", views.scan_api, name="scan_api"),
    path("bibliotheque/", views.bibliotheque, name="bibliotheque"),
    path("livres/<int:pk>/lire/", views.lire_livre, name="lire_livre"),
    path("livres/<int:pk>/reserver/", views.reserver, name="reserver"),
    path("mes-emprunts/", views.mes_emprunts, name="mes_emprunts"),
    path("parent/", views.espace_parent, name="parent"),
    path("cartes/", views.liste_cartes, name="cartes"),
    path("eleve/<int:pk>/carte/", views.carte, name="carte"),
]
