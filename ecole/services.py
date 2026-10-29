"""Logique métier : passages, retards, notifications, statistiques."""
from datetime import time, timedelta

from django.conf import settings
from django.utils import timezone

from .models import Eleve, EntreeSortie, Notification


def heure_limite():
    h, m = (int(x) for x in settings.HEURE_LIMITE_RETARD.split(":"))
    return time(h, m)


def passages_du_jour(eleve, jour=None):
    jour = jour or timezone.localdate()
    return eleve.passages.filter(horodatage__date=jour).order_by("horodatage")


def notifier(eleve, message):
    """Simulation SMS : enregistre en base et affiche dans la console.
    Pour un vrai envoi, brancher ici une API (Africa's Talking, Twilio, WhatsApp...)."""
    Notification.objects.create(eleve=eleve, telephone=eleve.parent_telephone, message=message)
    print(f"[SMS SIMULÉ -> {eleve.parent_telephone}] {message}", flush=True)


def enregistrer_passage(eleve):
    """Retourne (passage, message) ou (None, raison) si doublon."""
    maintenant = timezone.localtime()
    du_jour = passages_du_jour(eleve)
    dernier = du_jour.last()
    if dernier and (maintenant - dernier.horodatage).total_seconds() < settings.DELAI_ANTI_DOUBLON_SECONDES:
        return None, "Scan déjà enregistré à l’instant."
    type_ = EntreeSortie.SORTIE if dernier and dernier.type == EntreeSortie.ENTREE else EntreeSortie.ENTREE
    premiere_entree = type_ == EntreeSortie.ENTREE and not du_jour.filter(type=EntreeSortie.ENTREE).exists()
    retard = premiere_entree and maintenant.time() > heure_limite()
    passage = EntreeSortie.objects.create(eleve=eleve, type=type_, horodatage=maintenant, retard=retard)
    verbe = "ENTRÉ" if type_ == EntreeSortie.ENTREE else "SORTI"
    message = f"Votre enfant {eleve.nom} est bien {verbe} à {maintenant:%H:%M}"
    notifier(eleve, message)
    return passage, message


def statut_eleve(eleve):
    l = list(passages_du_jour(eleve))
    entrees = [p for p in l if p.type == EntreeSortie.ENTREE]
    return {
        "entre": bool(entrees),
        "premiere_entree": timezone.localtime(entrees[0].horodatage) if entrees else None,
        "retard": any(p.retard for p in l),
        "dedans": bool(l) and l[-1].type == EntreeSortie.ENTREE,
        "derniere": timezone.localtime(l[-1].horodatage) if l else None,
    }


def stats_du_jour(classe=None):
    eleves = Eleve.objects.filter(actif=True).select_related("classe")
    if classe:
        eleves = eleves.filter(classe=classe)
    par_eleve = {}
    for p in EntreeSortie.objects.filter(eleve__in=eleves, horodatage__date=timezone.localdate()).order_by("horodatage"):
        par_eleve.setdefault(p.eleve_id, []).append(p)
    presents = retards = dedans = 0
    non_entres, lignes = [], []
    for e in eleves:
        l = par_eleve.get(e.id, [])
        entrees = [p for p in l if p.type == EntreeSortie.ENTREE]
        info = {"eleve": e, "entre": bool(entrees), "retard": any(p.retard for p in l),
                "dedans": bool(l) and l[-1].type == EntreeSortie.ENTREE,
                "heure": timezone.localtime(entrees[0].horodatage) if entrees else None}
        lignes.append(info)
        if entrees:
            presents += 1
            retards += info["retard"]
            dedans += info["dedans"]
        else:
            non_entres.append(e)
    return {"total": len(lignes), "presents": presents, "absents": len(non_entres), "retards": retards,
            "dedans": dedans, "non_entres": non_entres, "lignes": lignes}


def historique_7_jours(eleve):
    aujourdhui = timezone.localdate()
    rows = []
    for d in range(1, 8):
        jour = aujourdhui - timedelta(days=d)
        if jour.weekday() >= 5:      # week-end ignoré
            continue
        p = eleve.passages.filter(horodatage__date=jour, type=EntreeSortie.ENTREE).order_by("horodatage").first()
        rows.append({"jour": jour, "present": bool(p), "heure": timezone.localtime(p.horodatage) if p else None,
                     "retard": bool(p and p.retard)})
    return rows
