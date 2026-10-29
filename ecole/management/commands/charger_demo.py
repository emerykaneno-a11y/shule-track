from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from ecole.models import Classe, EmpruntLivre, Eleve, EntreeSortie, Livre


class Command(BaseCommand):
    help = "Charge des données de démonstration (classes, élèves, livres)."

    def handle(self, *args, **opts):
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser("admin", "", "admin1234")
            self.stdout.write("Compte admin créé : admin / admin1234 (À CHANGER !)")
        if Eleve.objects.exists():
            self.stdout.write("Données déjà présentes : rien à faire.")
            return
        c = {n: Classe.objects.create(nom=n) for n in ["7ème A", "7ème B", "8ème A"]}
        data = [("Amina Niyonkuru", "7ème A", "+25779123401"), ("Eric Ndayishimiye", "7ème A", "+25779123402"),
                ("Grace Irakoze", "7ème B", "+25779123403"), ("Patrick Habonimana", "8ème A", "+25779123404"),
                ("Chantal Uwimana", "8ème A", "+25779123405")]
        eleves = [Eleve.objects.create(nom=n, classe=c[cl], parent_telephone=t) for n, cl, t in data]
        livres = [Livre.objects.create(titre=t, auteur=a, categorie=cat, couleur=col) for t, a, cat, col in [
            ("Les Enfants de la Terre rouge", "A. Ndikumana", "Roman", "#1E40AF"),
            ("Mathématiques 7ème année", "MINEDUC Burundi", "Manuel", "#0F766E"),
            ("Histoire du Burundi", "J. Bigirimana", "Histoire", "#B45309"),
            ("Sciences et Vie", "C. Nshimirimana", "Sciences", "#7C3AED")]]
        jour = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        for e, h, m, retard in [(eleves[2], 7, 5, False), (eleves[0], 7, 12, False), (eleves[1], 7, 41, True)]:
            EntreeSortie.objects.create(eleve=e, type="ENTREE", retard=retard, horodatage=jour.replace(hour=h, minute=m))
        for d in range(1, 8):  # historique des jours précédents
            j = jour - timedelta(days=d)
            if j.weekday() < 5:
                for i, e in enumerate(eleves):
                    if (i * 7 + d * 3) % 7 != 0:
                        EntreeSortie.objects.create(eleve=e, type="ENTREE", horodatage=j.replace(hour=7, minute=5 + (i * 5 + d * 4) % 35))
        EmpruntLivre.objects.create(livre=livres[1], eleve=eleves[0], date_retour_prevue=timezone.localdate() + timedelta(days=10))
        self.stdout.write(self.style.SUCCESS("Données de démonstration chargées."))
