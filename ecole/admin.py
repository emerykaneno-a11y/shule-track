from django.contrib import admin

from .models import Classe, EmpruntLivre, Eleve, EntreeSortie, Livre, Notification

admin.site.site_header = "SHULE TRACK – Administration"
admin.site.site_title = "SHULE TRACK"


@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = ("matricule", "nom", "classe", "parent_telephone", "actif")
    list_filter = ("classe", "actif")
    search_fields = ("nom", "matricule")
    readonly_fields = ("matricule", "qr_code_id", "qr_image")


@admin.register(EntreeSortie)
class EntreeSortieAdmin(admin.ModelAdmin):
    list_display = ("eleve", "type", "horodatage", "retard")
    list_filter = ("type", "retard")


@admin.register(EmpruntLivre)
class EmpruntAdmin(admin.ModelAdmin):
    list_display = ("livre", "eleve", "date_emprunt", "date_retour_prevue", "rendu")
    list_filter = ("rendu",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("eleve", "telephone", "canal", "envoye_le", "simule")


admin.site.register(Classe)
admin.site.register(Livre)
