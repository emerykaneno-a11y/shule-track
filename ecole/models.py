import io
import uuid

import qrcode
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone


class Classe(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Eleve(models.Model):
    matricule = models.CharField(max_length=20, unique=True, blank=True)
    nom = models.CharField(max_length=120)
    classe = models.ForeignKey(Classe, on_delete=models.PROTECT, related_name="eleves")
    photo = models.ImageField(upload_to="photos/", blank=True, null=True)
    parent_telephone = models.CharField(max_length=20, help_text="Ex : +25779123456")
    qr_code_id = models.CharField(max_length=40, unique=True, blank=True)
    qr_image = models.ImageField(upload_to="qr/", blank=True, null=True)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ["classe__nom", "nom"]

    def __str__(self):
        return f"{self.nom} ({self.matricule})"

    @property
    def initiales(self):
        return "".join(m[0] for m in self.nom.split()[:2]).upper()

    def save(self, *args, **kwargs):
        if not self.matricule:
            annee = timezone.now().year
            n = Eleve.objects.filter(matricule__startswith=f"SHULE-{annee}-").count() + 1
            self.matricule = f"SHULE-{annee}-{n:03d}"
        if not self.qr_code_id:
            self.qr_code_id = f"QR-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)
        if not self.qr_image:
            buf = io.BytesIO()
            qrcode.make(self.qr_code_id).save(buf, format="PNG")
            self.qr_image.save(f"{self.matricule}.png", ContentFile(buf.getvalue()), save=False)
            super().save(update_fields=["qr_image"])


class EntreeSortie(models.Model):
    ENTREE, SORTIE = "ENTREE", "SORTIE"
    TYPES = [(ENTREE, "Entrée"), (SORTIE, "Sortie")]

    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name="passages")
    type = models.CharField(max_length=6, choices=TYPES)
    horodatage = models.DateTimeField(default=timezone.now)
    retard = models.BooleanField(default=False)

    class Meta:
        ordering = ["-horodatage"]
        verbose_name = "entrée/sortie"
        verbose_name_plural = "entrées/sorties"

    def __str__(self):
        return f"{self.eleve.nom} - {self.type} - {timezone.localtime(self.horodatage):%d/%m %H:%M}"


class Notification(models.Model):
    CANAUX = [("SMS", "SMS"), ("WHATSAPP", "WhatsApp")]

    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name="notifications")
    telephone = models.CharField(max_length=20)
    message = models.TextField()
    canal = models.CharField(max_length=10, choices=CANAUX, default="SMS")
    envoye_le = models.DateTimeField(default=timezone.now)
    simule = models.BooleanField(default=True)

    class Meta:
        ordering = ["-envoye_le"]

    def __str__(self):
        return f"{self.canal} → {self.telephone}"


class Livre(models.Model):
    titre = models.CharField(max_length=200)
    auteur = models.CharField(max_length=120)
    categorie = models.CharField(max_length=60, blank=True)
    couleur = models.CharField(max_length=7, default="#1E40AF", help_text="Couleur de la couverture")
    fichier_pdf = models.FileField(upload_to="livres/", blank=True, null=True)

    class Meta:
        ordering = ["titre"]

    def __str__(self):
        return self.titre

    @property
    def disponible(self):
        return not self.emprunts.filter(rendu=False).exists()


class EmpruntLivre(models.Model):
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name="emprunts")
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name="emprunts")
    date_emprunt = models.DateField(default=timezone.localdate)
    date_retour_prevue = models.DateField()
    rendu = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date_emprunt"]

    def __str__(self):
        return f"{self.livre} → {self.eleve.nom}"
