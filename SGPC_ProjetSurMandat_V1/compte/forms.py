
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import SGPC_Utilisateur
from catalogue.models import SGPC_PRODUIT,SGPC_MARQUE, SGPC_CATEGORIE, SGPC_COMMANDE, SGPC_PARAMETRES
from service.models import SGPC_RESERVATION, SGPC_DEVIS#, SGPC_ASSO_SER_DEV, SGPC_SERVICE
from django import forms
from django.contrib.auth.forms import AuthenticationForm
import datetime as dt

# choix multiples

YEARS = [x for x in range(1940, dt.datetime.now().year + 1)]


class DateInput(forms.DateInput):
      input_type = 'date'


class loginForm(AuthenticationForm):
    class Meta:
        model = SGPC_Utilisateur
        fields = ('username','passeword')

class UtilisateurForm(UserCreationForm):

    class Meta:
        model = SGPC_Utilisateur
        fields = ['UTI_PRENOM', 'UTI_NOM', 'UTI_EMAIL','UTI_DATENAISSANCE', 'UTI_NUMEROTEL', 'UTI_RUE', 'UTI_NUMERORUE', 'UTI_CODEPOSTALE', 'UTI_LOCALITE']
        labels = {"UTI_PRENOM": "Prénom", "UTI_NOM" : "Nom" , "UTI_EMAIL":"E-mail","UTI_DATENAISSANCE":"Date de naissance","UTI_NUMEROTEL":"Numéro de téléphone","UTI_RUE":"Rue","UTI_NUMERORUE":"Numéro de rue","UTI_CODEPOSTALE":"Code postale","UTI_LOCALITE":"Localité"}

        widgets = {'UTI_DATENAISSANCE': forms.SelectDateWidget(years=YEARS)}

    def __init__(self, *args, **kwargs):
        super(UtilisateurForm, self).__init__(*args, **kwargs)

        for fieldname in ['password1', 'password2']:
            self.fields[fieldname].help_text = None

class ClientForm(forms.ModelForm):
    class Meta:
        model = SGPC_Utilisateur
        fields = ['UTI_PRENOM', 'UTI_NOM', 'UTI_EMAIL','UTI_DATENAISSANCE', 'UTI_NUMEROTEL', 'UTI_RUE', 'UTI_NUMERORUE', 'UTI_CODEPOSTALE', 'UTI_LOCALITE']
        labels = {"UTI_PRENOM": "Prénom", "UTI_NOM": "Nom", "UTI_EMAIL": "E-mail",
                  "UTI_DATENAISSANCE": "Date de naissance", "UTI_NUMEROTEL": "Numéro de téléphone", "UTI_RUE": "Rue",
                  "UTI_NUMERORUE": "Numéro de rue", "UTI_CODEPOSTALE": "Code postale", "UTI_LOCALITE": "Localité"}
        widgets = {"UTI_DATENAISSANCE": DateInput()}

class creerProduit(forms.ModelForm):
    class Meta:
        model = SGPC_PRODUIT
        fields = ['PRO_NOM', 'PRO_IMAGE' , 'PRO_MARQUE', 'PRO_DESCRIPTION', 'PRO_PRIX_CATALOGUE', 'PRO_CATEGORIE', 'PRO_QUANTITESTOCK']
        labels = {"PRO_NOM": "Nom", "PRO_MARQUE":"Marque", "PRO_DESCRIPTION":"Description" ,"PRO_PRIX_CATALOGUE":"Prix", "PRO_CATEGORIE":"Categorie", "PRO_QUANTITESTOCK": "Quantite en stock", "PRO_IMAGE":"Image"}


class modifierProduit(forms.ModelForm):
    class Meta:
        model = SGPC_PRODUIT
        fields = ['PRO_NOM', 'PRO_MARQUE', 'PRO_DESCRIPTION', 'PRO_PRIX_CATALOGUE', 'PRO_CATEGORIE', 'PRO_QUANTITESTOCK','PRO_IMAGE']
        labels = {"PRO_NOM": "Nom", "PRO_MARQUE": "Marque", "PRO_DESCRIPTION": "Description", "PRO_PRIX_CATALOGUE": "Prix",
                  "PRO_CATEGORIE": "Catégorie", "PRO_QUANTITESTOCK": "Quantité en stock", "PRO_IMAGE": "Image"}

class supprimerProduit(forms.ModelForm):
    class Meta:
        model = SGPC_PRODUIT
        fields = ['is_active']
        exclude = {"is_active"}

class reactiverProduit(forms.ModelForm):
    class Meta:
        model = SGPC_PRODUIT
        fields = ['is_active']
        exclude = {"is_active"}


class modifierDonnes(UserChangeForm):
    class Meta:
        model = SGPC_Utilisateur
        fields = ['UTI_PRENOM', 'UTI_NOM', 'UTI_EMAIL','UTI_DATENAISSANCE', 'UTI_NUMEROTEL', 'UTI_RUE', 'UTI_NUMERORUE', 'UTI_CODEPOSTALE', 'UTI_LOCALITE', 'password']
        labels = {"UTI_PRENOM": "Prénom", "UTI_NOM": "Nom", "UTI_EMAIL": "E-mail", "UTI_DATENAISSANCE": "Date de naissance",
                  "UTI_NUMERORUE": "Numéro de rue", "UTI_NUMEROTEL": "Numéro de téléphone", "UTI_RUE": "Rue",
                  "UTI_CODEPOSTALE": "Code postal", "UTI_LOCALITE": "Localité"}
        exclude = ['password']


class creerReservation(forms.ModelForm):
    class Meta:
        model = SGPC_RESERVATION
        fields = ['RES_DATE', 'RES_STATUT', 'RES_UTI_ID']#,'RES_SER_ID']
        labels = {"RES_DATE": "Date", "RES_STATUT" : "Statut", "RES_UTI_ID" : "client"}#, 'RES_SER_ID': 'Service'}
        exclude = {"RES_STATUT"}
        widgets = {"RES_DATE": DateInput()}

class modifierReservation(forms.ModelForm):
    class Meta:
        model = SGPC_RESERVATION
        fields = ['RES_DATE', 'RES_STATUT']#,'RES_SER_ID']
        labels = {"RES_DATE": "Date", "RES_STATUT" : "Statut", "RES_UTI_ID" : "client",'RES_SER_ID': 'Service'}
        widgets = {"RES_DATE": DateInput()}

class creerReservationClient(forms.ModelForm):
    class Meta:
        model = SGPC_RESERVATION
        fields = ['RES_DATE', 'RES_STATUT', 'RES_UTI_ID']#,'RES_SER_ID']
        labels = {"RES_DATE": "Date"}#, 'RES_SER_ID': 'Service'}
        exclude = {"RES_STATUT", "RES_UTI_ID"}
        widgets = {"RES_DATE": DateInput()}


class creerDevis(forms.ModelForm):
    class Meta:
        model = SGPC_DEVIS
        fields = ['DEV_UTI']
        labels = {'DEV_UTI':'Client'}


# class creerDevisAssos(forms.ModelForm):
#     class Meta:
#         model = SGPC_ASSO_SER_DEV
#         fields = ['ASD_PRIX_EFFECTIF', 'ASD_COMMENTAIRE', 'ASD_SER_ID']
#         labels = {'ASD_PRIX_EFFECTIF': 'Prix','ASD_COMMENTAIRE':'Commentaire','ASD_SER_ID':'Service'}

class creerMarque(forms.ModelForm):
    class Meta:
        model = SGPC_MARQUE
        fields = ['MAR_NOM']
        labels = {'MAR_NOM':'Nom'}

class modifierMarque(forms.ModelForm):
    class Meta:
        model = SGPC_MARQUE
        fields = ['MAR_NOM']
        labels = {'MAR_NOM':'Nom'}

class supprimerMarque(forms.ModelForm):
    class Meta:
        model = SGPC_PRODUIT
        fields = ['MAR_is_active']
        exclude = {"MAR_is_active"}

class reactiverMarque(forms.ModelForm):
    class Meta:
        model = SGPC_PRODUIT
        fields = ['MAR_is_active']
        exclude = {"MAR_is_active"}


class creerCategorie(forms.ModelForm):
    class Meta:
        model = SGPC_CATEGORIE
        fields = ['CAT_NOM']
        labels = {'CAT_NOM':'Nom'}

class modifierCategorie(forms.ModelForm):
    class Meta:
        model = SGPC_CATEGORIE
        fields = ['CAT_NOM']
        labels = {'CAT_NOM':'Nom'}

class supprimerCategorie(forms.ModelForm):
    class Meta:
        model = SGPC_CATEGORIE
        fields = ['CAT_is_active']
        exclude = {"CAT_is_active"}

class reactiverCategorie(forms.ModelForm):
    class Meta:
        model = SGPC_CATEGORIE
        fields = ['CAT_is_active']
        exclude = {"CAT_is_active"}

class creerReservationDevis(forms.ModelForm):
    class Meta:
        model = SGPC_RESERVATION
        fields = ['RES_DATE', 'RES_STATUT', 'RES_SER_ID','RES_DEV_ID']
        exclude = {"RES_STATUT", "RES_UTI_ID", "RES_SER_ID"}
        widgets = {"RES_DATE": DateInput()}


class ContactForm(forms.Form):
    email = forms.EmailField(required=True)
    demande = forms.CharField(widget=forms.Textarea, required=True)
#    choice = forms.MultipleChoiceField(choices=[(choice.SER_NOM, choice) for choice in SGPC_SERVICE.objects.all()])
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['choice'].label = 'Services'



class NumeroSuivi(forms.ModelForm):
    class Meta:
        model = SGPC_COMMANDE
        fields = ['COM_NUMEROSUIVI', 'COM_STATUT']
        exclude = {'COM_STATUT'}
        labels = {'COM_NUMEROSUIVI':'Numéro de suivi'}

class ModifParametre(forms.ModelForm):
   class Meta:
       model = SGPC_PARAMETRES
       fields = ['PAR_TAUX_TVA', 'PAR_DELAI_PAIEMENT', 'PAR_DELAI_PREMIER_RAPPEL', 'PAR_DELAI_DEUXIEME_RAPPEL', 'PAR_NBMAX_RDV_JOUR', 'PAR_LIMITE_STOCK','PAR_FRAIS_LIVRAISON_PETIT','PAR_FRAIS_LIVRAISON_MOYEN','PAR_FRAIS_LIVRAISON_GRANDE']
       labels = {'PAR_TAUX_TVA':'Taux TVA', 'PAR_DELAI_PAIEMENT':'Délai de payement','PAR_DELAI_PREMIER_RAPPEL': 'Délai de premier rappel','PAR_DELAI_DEUXIEME_RAPPEL': 'Délai de deuxième rappel','PAR_NBMAX_RDV_JOUR':'Nombre maximum de rendez-vous par jour', 'PAR_LIMITE_STOCK':'Limite de stock','PAR_FRAIS_LIVRAISON_PETIT':'Frais de livraison pour une petite commande(-=5)','PAR_FRAIS_LIVRAISON_MOYEN':'Frais de livraison pour une moyenne commande(-=10)','PAR_FRAIS_LIVRAISON_GRANDE':'Frais de livraison pour une grande commande(-=15)'}