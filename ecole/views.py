import json
import random
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import services
from .models import Classe, EmpruntLivre, Eleve, EntreeSortie, Livre


def dashboard(request):
    classes = Classe.objects.all()
    classe = classes.filter(pk=request.GET.get("classe")).first() if request.GET.get("classe", "").isdigit() else None
    return render(request, "ecole/dashboard.html", {
        "classes": classes, "classe": classe, "s": services.stats_du_jour(classe),
        "aujourdhui": timezone.localdate(), "limite": settings.HEURE_LIMITE_RETARD,
    })


def scan(request):
    passages = EntreeSortie.objects.filter(horodatage__date=timezone.localdate()).select_related("eleve", "eleve__classe")[:40]
    return render(request, "ecole/scan.html", {"passages": passages})


@require_POST
def scan_api(request):
    try:
        data = json.loads(request.body or "{}")
    except ValueError:
        data = {}
    code = (data.get("code") or "").strip()
    if data.get("aleatoire"):
        eleves = list(Eleve.objects.filter(actif=True))
        eleve = random.choice(eleves) if eleves else None
    else:
        eleve = Eleve.objects.filter(actif=True, qr_code_id=code).first() or \
                Eleve.objects.filter(actif=True, matricule__iexact=code).first()
    if not eleve:
        return JsonResponse({"ok": False, "message": "Carte inconnue ou élève inactif."}, status=404)
    passage, message = services.enregistrer_passage(eleve)
    base = {"nom": eleve.nom, "classe": eleve.classe.nom, "matricule": eleve.matricule,
            "initiales": eleve.initiales, "photo": eleve.photo.url if eleve.photo else None}
    if passage is None:
        return JsonResponse({"ok": True, "doublon": True, "message": message, **base})
    heure = timezone.localtime(passage.horodatage)
    return JsonResponse({
        "ok": True, "doublon": False, "type": passage.type, "retard": passage.retard,
        "heure": f"{heure:%H:%M}",
        "message": f"Notification envoyée au parent {eleve.parent_telephone} : {message}", **base})


def bibliotheque(request):
    q = request.GET.get("q", "").strip()
    livres = Livre.objects.all()
    if q:
        livres = livres.filter(titre__icontains=q) | livres.filter(auteur__icontains=q) | livres.filter(categorie__icontains=q)
    return render(request, "ecole/bibliotheque.html", {"livres": livres.distinct(), "q": q})


def lire_livre(request, pk):
    livre = get_object_or_404(Livre, pk=pk)
    if livre.fichier_pdf:
        return redirect(livre.fichier_pdf.url)
    return render(request, "ecole/lire_livre.html", {"livre": livre})


@require_POST
def reserver(request, pk):
    livre = get_object_or_404(Livre, pk=pk)
    eleve = Eleve.objects.filter(matricule__iexact=request.POST.get("matricule", "").strip()).first()
    if not eleve:
        messages.error(request, "Matricule introuvable. Exemple : SHULE-2026-001")
    elif not livre.disponible:
        messages.error(request, f"« {livre.titre} » est déjà emprunté.")
    else:
        retour = timezone.localdate() + timedelta(days=settings.DUREE_EMPRUNT_JOURS)
        EmpruntLivre.objects.create(livre=livre, eleve=eleve, date_retour_prevue=retour)
        messages.success(request, f"« {livre.titre} » réservé pour {eleve.nom}. Retour avant le {retour:%d/%m/%Y}.")
    return redirect("bibliotheque")


def mes_emprunts(request):
    mat = request.GET.get("matricule", "").strip()
    eleve = Eleve.objects.filter(matricule__iexact=mat).first() if mat else None
    emprunts = eleve.emprunts.select_related("livre") if eleve else []
    return render(request, "ecole/mes_emprunts.html", {"mat": mat, "eleve": eleve, "emprunts": emprunts})


def espace_parent(request):
    mat = request.GET.get("matricule", "").strip()
    eleve = Eleve.objects.select_related("classe").filter(matricule__iexact=mat).first() if mat else None
    ctx = {"mat": mat, "eleve": eleve}
    if eleve:
        ctx.update(statut=services.statut_eleve(eleve), historique=services.historique_7_jours(eleve),
                   emprunts=eleve.emprunts.select_related("livre").filter(rendu=False))
    return render(request, "ecole/parent.html", ctx)


def liste_cartes(request):
    return render(request, "ecole/liste_cartes.html", {"eleves": Eleve.objects.filter(actif=True).select_related("classe")})


def carte(request, pk):
    return render(request, "ecole/carte.html", {"e": get_object_or_404(Eleve, pk=pk)})
