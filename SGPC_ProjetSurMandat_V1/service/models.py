from django.db import models
from compte.models import SGPC_Utilisateur
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, datetime
import datetime
from datetime import timedelta


# create your models here

def validate_date(date):
    weekend = [5, 6]
    listeJourFerié = [datetime.date(2020, 12, 25), datetime.date(2021, 8, 1), datetime.date(2020, 12, 31),datetime.date(2021, 1, 1)]
    tomorrow = timezone.now().date()
    sixmonths = timezone.now().date() + timezone.timedelta(days=365.25/2)
    if date in listeJourFerié:
        raise ValidationError("Impossible de réserver durant un jour férié")
    if date <= tomorrow:
        raise ValidationError("Impossible de réserver pour aujourd'hui ou une date antérieur. ")
    elif date.weekday() in weekend:
        raise ValidationError("Impossible de réserver durant le weekend. ")
    elif date >= sixmonths:
        raise ValidationError("Impossible de réserver pour une date de plus de 6 mois.")



statut_choice =     (
        ('Confirmé', 'Confirmé'),
        ('En attente de confirmation','En attente de confirmation'),
        ('Annulé','Annulé'),
    )

# class SGPC_SERVICE(models.Model):
#     SER_NOM = models.CharField(max_length=50, null=False, blank=False)
#     SER_PRIX_STANDARD = models.PositiveIntegerField()
#     SER_DESCRIPTION = models.CharField(max_length=100, blank=True)
# 
#     def __str__(self):
#         return self.SER_NOM

class SGPC_DEVIS(models.Model):
    DEV_UTI = models.ForeignKey(SGPC_Utilisateur, on_delete=models.CASCADE)
#    DEV_SER = models.ManyToManyField(SGPC_SERVICE, through="SGPC_ASSO_SER_DEV")
    DEV_DATE = models.DateField(auto_now_add=True)


# heureDebut_choice = (
#         ('08:00', '08:00'),
#         ('09:00', 09:00),
#         (10:00, 10:00),
#         (11:00, 11:00),
#         (14:00, 14:00),
#         (15:00, 15:00),
#         (16:00, 16:00),
#         (17:00, 17:00),
#         (18:00, 18:00),
#     )


class SGPC_RESERVATION(models.Model):
    RES_UTI_ID = models.ForeignKey(SGPC_Utilisateur, on_delete=models.CASCADE)
    RES_DATE = models.DateField(auto_now_add=False, validators=[validate_date])
    RES_STATUT = models.CharField(max_length=50, choices=statut_choice)
#    RES_SER_ID = models.ForeignKey(SGPC_SERVICE, on_delete=models.CASCADE)
    RES_DEV_ID = models.ForeignKey(SGPC_DEVIS, on_delete=models.CASCADE, null=True, blank=True)
    RES_COM_ID = models.ForeignKey('catalogue.SGPC_COMMANDE', on_delete=models.CASCADE,blank=True, null=True)


# class SGPC_ASSO_SER_DEV(models.Model):
#      ASD_SER_ID = models.ForeignKey(SGPC_SERVICE, on_delete=models.CASCADE)
#      ASD_DEV_ID = models.ForeignKey(SGPC_DEVIS, on_delete=models.CASCADE)
#      ASD_PRIX_EFFECTIF = models.IntegerField(null=True, blank=True)
#      ASD_COMMENTAIRE = models.CharField(max_length=50, null=True, blank=True)
