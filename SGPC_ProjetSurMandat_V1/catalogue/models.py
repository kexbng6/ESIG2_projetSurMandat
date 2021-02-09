from django.db import models
from compte.models import SGPC_Utilisateur
from service.models import SGPC_RESERVATION
# from activatable_model.models import BaseActivatableModel
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here

class SGPC_MARQUE(models.Model):
    MAR_NOM = models.CharField(max_length=40, unique=True)
    MAR_is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.MAR_NOM


class SGPC_CATEGORIE(models.Model):
    CAT_NOM = models.CharField(max_length=40, unique=True)
    CAT_is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.CAT_NOM


class SGPC_PRODUIT(models.Model):
    PRO_NOM = models.CharField(max_length=40)
    PRO_MARQUE = models.ForeignKey(SGPC_MARQUE, on_delete=models.CASCADE)
    PRO_DESCRIPTION = models.TextField(max_length=200)
    PRO_PRIX_CATALOGUE = models.DecimalField(max_digits=12,decimal_places=2,  validators=[MinValueValidator(0.01)])
    PRO_CATEGORIE = models.ForeignKey(SGPC_CATEGORIE, models.CASCADE)
    PRO_QUANTITESTOCK = models.PositiveIntegerField()
    PRO_IMAGE = models.ImageField(default="", blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.PRO_NOM + ' ' + str(self.PRO_MARQUE) + ' ' + str(self.PRO_PRIX_CATALOGUE) + ' ' + str(self.PRO_QUANTITESTOCK)

class SGPC_COMMANDE(models.Model):
    COM_UTI_ID = models.ForeignKey(SGPC_Utilisateur, on_delete=models.CASCADE)
    COM_DATE = models.DateField(auto_now_add=False)
    COM_STATUT = models.CharField(max_length=50)
    COM_NUMEROSUIVI = models.CharField(max_length=50, blank=True)
    COM_FACTURE_DATE = models.DateField(blank=True, null=True)
    COM_FACTURE_STATUT = models.CharField(max_length=50, blank=True, null=True)
    COM_FRAIS_LIVRAISON = models.DecimalField(max_digits=12,decimal_places=2,  validators=[MinValueValidator(0.01)], blank=True, null=True)
    COM_RES_ID = models.ManyToManyField('service.SGPC_RESERVATION', related_name="est_associe_a",blank=True)
    COM_PRO_ID = models.ManyToManyField(SGPC_PRODUIT, through='SGPC_ASSO_COM_PRO')

    def __str__(self):
        return self.COM_STATUT + ' ' + str(self.COM_DATE)


class SGPC_ASSO_COM_PRO(models.Model):
    ACP_QUANTITE = models.PositiveIntegerField()
    ACP_PRIX_VENTE = models.FloatField()
    ACP_TAUX_TVA = models.FloatField()
    ACP_COMMANDE = models.ForeignKey(SGPC_COMMANDE, on_delete=models.CASCADE)
    ACP_PRODUIT = models.ForeignKey(SGPC_PRODUIT, on_delete=models.CASCADE)

class SGPC_PARAMETRES(models.Model):
    PAR_TAUX_TVA = models.FloatField()
    PAR_DELAI_PAIEMENT = models.PositiveIntegerField()
    PAR_DELAI_PREMIER_RAPPEL = models.PositiveIntegerField()
    PAR_DELAI_DEUXIEME_RAPPEL = models.PositiveIntegerField()
    PAR_NBMAX_RDV_JOUR = models.PositiveIntegerField()
    PAR_LIMITE_STOCK = models.PositiveIntegerField()
    PAR_FRAIS_LIVRAISON_PETIT = models.IntegerField()
    PAR_FRAIS_LIVRAISON_MOYEN = models.IntegerField()
    PAR_FRAIS_LIVRAISON_GRANDE = models.IntegerField()