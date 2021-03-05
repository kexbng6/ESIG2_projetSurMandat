import random

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import loginForm, UtilisateurForm, ClientForm, NumeroSuivi
from django.contrib.auth.forms import UserChangeForm
from . import forms
from activatable_model.models import BaseActivatableModel
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from catalogue.models import SGPC_PRODUIT, SGPC_MARQUE, SGPC_CATEGORIE, SGPC_COMMANDE, SGPC_PARAMETRES
from .models import SGPC_Utilisateur
from catalogue.models import *
from service.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .decorators import unauthenticated_user
from service.models import SGPC_RESERVATION, SGPC_DEVIS#, SGPC_ASSO_SER_DEV, SGPC_SERVICE
import _datetime
from django.forms import inlineformset_factory
from .filters import ProduitFilter, CommandeFiltrer, DevisFiltrer, rdvFilter
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.views import View
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import date, datetime
import time

from django.http import JsonResponse
from django.core.serializers import serialize

from django.core import serializers
# Create your views here.


def loginPage(request):
    if request.method == 'POST':
        form = loginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'L\'adresse mail ou le mot de passe est invalide')
    else:
        form = loginForm()
    return render(request, 'compte/login.html', {'form': form})


def logoutPage(request):
    if request.method == 'POST':
        logout(request)
        return redirect('index')

def checkMailValid(request):
    utilisateurs = SGPC_Utilisateur.objects.all()
    data = serialize('json', list(utilisateurs), fields=('UTI_EMAIL'))
    if request.is_ajax() and request.method == "GET":
        user_email = request.GET.get("id_UTI_EMAIL")
        #time.sleep(2)
        print(data)
        if user_email in data and user_email != "":
            suggest_num = random.randrange(1,900)
            # si l'email est déjà utilisé, envoyer valide = false ainsi qu'une suggestion de mail
            return JsonResponse({"valid": False, "suggestion": str(suggest_num)+user_email, "mail": user_email}, status=200)
        else:
            # sinon envoyer valide = true
            print(user_email + ' est une adresse mail en ordre')
            return JsonResponse({"valid": True}, status=200)
    return JsonResponse({'data': "Rien a voir ici"}, status=400)

## https://docs.djangoproject.com/en/dev/topics/serialization/#serialization-formats-json
## https://simpleisbetterthancomplex.com/tutorial/2016/08/29/how-to-work-with-ajax-request-with-django.html
## https://stackoverflow.com/questions/7650448/how-to-serialize-django-queryset-values-into-json

def signUpView(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            form.save()
            utilisateurPrenom = form.cleaned_data.get('UTI_PRENOM')
            utilisateurNom = form.cleaned_data.get('UTI_NOM')
            emailUTI = form.cleaned_data.get('UTI_EMAIL')
            send_mail('Bienvenue chez SG PERFORMANCES CUSTOMS',
                      'Bonjour,\n \n'
                      'Bienvenue chez SG PERFORMANCES CUSTOMS, vous pouvez maintenant vous connecter sur notre site ! \n \n' +
                      'SG PERFORMANCES CUSTOMS',
                      settings.EMAIL_HOST_USER,
                      [emailUTI],
                      fail_silently=False)
            messages.success(request,
                             'Le profil \'' + utilisateurNom + ' ' + utilisateurPrenom + '\' a été créé avec succès !')
            return redirect('login')
    else:
        form = UtilisateurForm()
    return render(request, 'compte/signup.html', {'form': form})

@login_required(login_url="/login/") #inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def adminView(request):
    aujourdhui = _datetime.date.today() #Récupération de la date du jour
    utilisateurs = SGPC_Utilisateur.objects.all() # Récupération de tous les utilisateurs présents dans la base de données
    #services = SGPC_SERVICE.objects.all() # Récupération de tous les services présents dans la base de données
    parametres = SGPC_PARAMETRES.objects.all() # Récupération de tous les paramètres

    commandesEnPrep = SGPC_COMMANDE.objects.filter(COM_STATUT='En préparation').order_by('-COM_DATE')[:10] # Récupération de tous les commandes ayant comme status "En préparation"

    commandesExpediees = SGPC_COMMANDE.objects.filter(COM_STATUT='Expédiée').order_by('-COM_DATE')[:10] # Récupération de tous les commandes ayant comme status "Expédiée"
    reservations = SGPC_RESERVATION.objects.filter(RES_DATE__gte = aujourdhui).order_by('RES_DATE')[:10] # Récupération des 10 prochaines réservation à partir de la date du jour
    devis = SGPC_DEVIS.objects.all() # Récupration de tous les devis présents dans la base de données
    produits = SGPC_PRODUIT.objects.all() # Récupration de tous les produits présents dans la base de données
    produitsStockAlert = SGPC_PRODUIT.objects.filter(PRO_QUANTITESTOCK__lte=10)
    context = {
        'utilisateurs': utilisateurs,
        #'services': services,
        'commandesEnPrep': commandesEnPrep,
        'commandesExpediees':commandesExpediees,
        'reservations': reservations,
        'produits': produits,
        'parametres': parametres,
        'devis': devis,
        'produitsStockAlert': produitsStockAlert,
    }
    return render(request, 'compte/admin.html', context)

@login_required(login_url="/login/") #inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def numeroSuivi(request,id):
    commande = SGPC_COMMANDE.objects.get(id=id) # Récupération de la commande ayant comme id le paramètre "ID"
    if request.method == 'POST': # Vérification si le formulaire est valide
        form = NumeroSuivi(request.POST, instance=commande)
        if form.is_valid():
            form = form.save(commit=False)
            form.COM_STATUT = 'Expédiée'# Changement du statut de la commande
            form.save() # Enregistrement du numéro de suivi ainsi que des changements effectués dans la base de données
            send_mail('Numéro de suivi pour la commande '+commande.id,
                      'Bonjour, '
                      'Votre commande n°'+ str(commande.id) +'du '+ commande.COM_DATE +' a été expédié.'+
                      'Voici votre numéro de suivi '+ str(commande.COM_NUMEROSUIVI),
                      settings.EMAIL_HOST_USER,
                      [settings.EMAIL_HOST_USER],
                      fail_silently=False)
            return redirect('admin')
    else:
        form = NumeroSuivi(instance=commande) # Rechargement du formulaire si celui-ci n'est pas valide
    context = {
        'commande': commande,
        'form' : form,
    }
    return render(request, 'compte/numeroSuivi.html',context)

@login_required(login_url="/login/") #inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def espaceClient(request, pk):
    aujourdhui = _datetime.date.today()  # Récupération de la date du jour
    compte = SGPC_Utilisateur.objects.get(id=pk) # Récupération du compte client ayant le même id que le paramètre "pk"
    reservations = SGPC_RESERVATION.objects.filter(Q(RES_UTI_ID_id=pk, RES_DATE__gte=aujourdhui)).order_by('RES_DATE')[:10] # Récupération de toutes les réservations ayant le meme ID d'utilisateur que le paramètre "pk"
    commandes = SGPC_COMMANDE.objects.filter(COM_UTI_ID_id=pk).order_by('-COM_DATE')[:10] # Récupération de toutes les commandes ayant le meme ID d'utilisateur que le paramètre "pk"
    devis = SGPC_DEVIS.objects.filter(DEV_UTI_id=pk)
    context = {
        'compte': compte,
        'reservations': reservations,
        'commandes': commandes,
        'devis': devis,
    }
    return render(request, 'compte/client.html', context)


@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def modifierDonnees(request, pk):
    uti = SGPC_Utilisateur.objects.get(id=pk) # Récupération de l'utilisateur ayant le même id que le paramètre "pk"
    form = forms.modifierDonnes(instance=uti) # Récupération du formulaire de modification de données pré-rempli avec les informations de l'utlisateur
    if request.method == 'POST':
        form = forms.modifierDonnes(request.POST, instance=uti)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save() # Enregistrement des données dans la base de données.
            return redirect('client', pk) # Redirection à l'espace client.
    context = {
        'form': form,
        'uti': uti,
    }
    return render(request, 'compte/modifierDonnees.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def creerProduit(request):
    if request.method == 'POST':
        form = forms.creerProduit(request.POST) # Récupération du formulaire de création de produit.
        if form.is_valid():
            form.save() # Enregistrement du nouveau produit créer dans la base de données.
            return redirect('admin')
    else:
        form = forms.creerProduit()
    return render(request, 'compte/creerProduit.html', {'form': form})

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def modifierProduit(request, pk):
    produit = SGPC_PRODUIT.objects.get(id=pk) # Récupération du produit ayant le même id que que le paramètre "pk"
    form = forms.modifierProduit(instance=produit) # Récupération du formulaire de modification de produit pré-rempli avec les informations du produit
    if request.method == 'POST':
        form = forms.modifierProduit(request.POST, instance=produit)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save() # Enregistrement des changements dans la base de données
            return redirect('liste_produits')
    context = {
        'form': form,
        'produit': produit,
    }
    return render(request, 'compte/modifierProduit.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def supprimerProduit(request, pk):
    produit = SGPC_PRODUIT.objects.get(id=pk) # Récupération du produit ayant le même id que que le paramètre "pk"
    form = forms.supprimerProduit(instance=produit) # Récupération du formulaire de suppression de produit avec les informations du produit
    if request.method == 'POST':
        form = forms.supprimerProduit(request.POST, instance=produit)
        produit.is_active = False # Changement de l'attribut "is_active" de "True" à "False", il n'apparaît plus dans la boutique mais est présent dans la liste des produits pour l'administrateur.
        if form.is_valid():
            form.save() # Enregistrement des données dans la base de données.
            return redirect('liste_produits')
    context = {
        'form': form,
        'produit': produit,
    }
    return render(request, 'compte/supprimerProduit.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def detailRDV(request, pk):
    reservation = SGPC_RESERVATION.objects.get(id=pk) # Récupération de la réservation ayant le même id que le paramètre "pk"
    context = {
        'reservation': reservation,
    }
    if reservation.RES_DEV_ID_id: # Test pour savoir si la réservation à un numéro de devis
        devis = SGPC_DEVIS.objects.get(id=reservation.RES_DEV_ID_id) # Récupération des informations du devis ayant le meme id que l'ID du devis dans réservation
        #assos = SGPC_ASSO_SER_DEV.objects.filter(ASD_DEV_ID_id=devis.id) # Récupération des informations de la classe d'association entre devis et service avec l'id du devis.
        context = {'devis': devis,
                    #'assos': assos,
                   'reservation': reservation,}
    return render(request, 'compte/detailReservation.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def detailCommande(request, pk):
    parametre = SGPC_PARAMETRES.objects.get(id=1)
    commande = SGPC_COMMANDE.objects.get(id=pk) # Récupération de la commande ayant le même id que le paramètres "pk"
    #assos = SGPC_ASSO_COM_PRO.objects.all().filter(ACP_COMMANDE_id=pk) # Récupération des informations présente dans la table d'association entre commande et produit en utilisateur l'id de la commande.
    reservation = SGPC_RESERVATION.objects.all().filter(RES_COM_ID_id=commande.id) # Récupération des réservations ayant comme le même id de commande

    context = {
        'commande': commande,
        #'assos': assos,
        'reservation': reservation,
    }
    for res in reservation: # On parcourt tous les réservations pour savoir s'il y un numéro de devis, afin de pouvoir afficher le numéro de devis et les informations présente dans la classe d'assocition "ASSO_SER_DEV"
        #assoDev = SGPC_ASSO_SER_DEV.objects.filter(ASD_DEV_ID_id=res.RES_DEV_ID_id)
        context = {
            'commande': commande,
        #    'assos': assos,
            'reservation': reservation,
         #   'assoDev': assoDev,
        }
    if commande.COM_FACTURE_STATUT != None:
        if commande.COM_FACTURE_STATUT != "Payée":
            if (commande.COM_FACTURE_DATE + timezone.timedelta(parametre.PAR_DELAI_PAIEMENT)) <= timezone.now().date():
                commande.COM_FACTURE_STATUT = "Premier rappel"
            if (commande.COM_FACTURE_DATE + timezone.timedelta(parametre.PAR_DELAI_PAIEMENT)+timezone.timedelta(parametre.PAR_DELAI_PREMIER_RAPPEL)) <= timezone.now().date():
                commande.COM_FACTURE_STATUT = "Deuxième rappel"
            if (commande.COM_FACTURE_DATE + timezone.timedelta(parametre.PAR_DELAI_PAIEMENT) + timezone.timedelta(parametre.PAR_DELAI_PREMIER_RAPPEL)+timezone.timedelta(parametre.PAR_DELAI_DEUXIEME_RAPPEL)) <= timezone.now().date():
                commande.COM_FACTURE_STATUT = "Deuxième rappel non payé ! (Poursuites)"
    return render(request, 'compte/detailCommande.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def detailDevis(request, pk):
    devis = SGPC_DEVIS.objects.get(id=pk) # Récupération du devis ayant le même id que le paramètre "pk"
    #assos = SGPC_ASSO_SER_DEV.objects.all().filter(ASD_DEV_ID_id=pk) # Récupération des informations dans la table "ASSO_SER_DEV" qui ont le meme id que devis dans l'attribut "ASD_DEV_ID"
    reservation = SGPC_RESERVATION.objects.all().filter(Q(RES_DEV_ID_id=devis.id)) # Récupération de toutes les réservations qui ont le meme id que devis dans l'attribut "RES_DEV_ID"
    listRes = [] # Création d'une liste
    for res in reservation: #On parcourt toutes les réservations afin de stocker tous id des services présent dans les réservations.
        listRes.append(res.RES_SER_ID_id)
    context = {
        'devis': devis,
     #   'assos': assos,
        'reservation': reservation,
        'listRes':listRes,
    }
    return render(request, 'compte/detailDevis.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def creerReservation(request): # Inspiré de la vidéo CRUD de Dennis Ivy (https://www.youtube.com/watch?v=EX6Tt-ZW0so)
    parametre = SGPC_PARAMETRES.objects.get(id=1)
    if request.method == 'POST':
        form = forms.creerReservation(request.POST) # Récupération du formulaire de création de devis
        if form.is_valid():
            obj = form.save(commit=False)
            nbReservation = SGPC_RESERVATION.objects.filter(RES_DATE=obj.RES_DATE).count() # Filtre afin d'obtenir le nombre de réservation présente à la date choisi par l'utilisateur dans son formulaire
            if nbReservation < parametre.PAR_NBMAX_RDV_JOUR: # Vérification si le nombre de réservation pour la date choisi n'est pas plus grande que 4
                obj.RES_STATUT = 'Confirmé'
                emailUti = obj.RES_UTI_ID.UTI_EMAIL
                obj.save() # Enregistrement des données dans la base de données
                form.save_m2m() # Enregistement des données pour les tables lié à SGPC_RESERVATION.
                send_mail('Nouvelle réservation',
                         'Bonjour, vous avez une réservation pour le ' + str(
                             obj.RES_DATE) + ' concernant ' + obj.RES_SER_ID.SER_NOM + '\n \n Merci de bien vouloir aller consulter votre espace adminitrateur'
                                                                                       '\n \n SG PERFORMANCES CUSTOMS',
                         settings.EMAIL_HOST_USER,
                         [settings.EMAIL_HOST_USER],
                         fail_silently=False)
                return redirect('admin')
            else:
                messages.error(request, 'La date est deja pleine') # Message d'erreur si le nombre de réservation dépasse 4
                form = forms.creerReservation() # Affiche d'un nouveau formulaire vierge.
    else:
        form = forms.creerReservation()
    context = {
        'form': form,
    }
    return render(request, 'compte/creerReservation.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def creerClient(request):
    if request.method == 'POST':
        form = ClientForm(request.POST) # Récupération du formulaire de créatio de client
        if form.is_valid():
            obj = form.save(commit=False)
            obj.is_active = 0 # Désactiviation du compte car le client a été créé par l'admin
            obj.save() # Enregistrement des données dans la base de données
            return redirect('create_reservation')
    else:
        form = ClientForm()
    context = {
        'form': form,
    }
    return render(request, 'compte/creerClient.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def modifierReservation(request, pk): # Inspiré de la vidéo CRUD de Dennis Ivy (https://www.youtube.com/watch?v=EX6Tt-ZW0so)
    parametre = SGPC_PARAMETRES.objects.get(id=1)
    reservation = SGPC_RESERVATION.objects.get(id=pk) # Récupération de la réservation ayant le même id que le paramètre "pk"
    form = forms.modifierReservation(instance=reservation) # Récupération du formulaire de modification de réservaiton pré-rempli avec les informations de la réservation.
    if request.method == 'POST':
        form = forms.modifierReservation(request.POST, instance=reservation)
        if form.is_valid():
            instance = form.save(commit=False)
            if instance.RES_STATUT == 'Annulé':
                send_mail('Votre demande de réservation',
                          'Bonjour, \n \n'
                          'Votre réservation a malheureusement annulé, nous vous invitons à prendre un nouveau rendez-vous ou alors à nous contacter directement. \n \n SG PERFORMANCE CUSTOMS',
                          settings.EMAIL_HOST_USER,
                          [instance.RES_UTI_ID.UTI_EMAIL],
                          fail_silently=False)
                instance.save()  # Enregistrement des données dans la base de données
                form.save_m2m()  # Enregistement des données pour les tables lié à SGPC_RESERVATION.
                return redirect('admin')
            else:
                nbReservation = SGPC_RESERVATION.objects.filter(RES_DATE=instance.RES_DATE).count() # Filtre afin d'obtenir le nombre de réservation présente à la date choisi par l'utilisateur dans son formulaire
                if nbReservation < parametre.PAR_NBMAX_RDV_JOUR:
                    instance.RES_STATUT = 'Confirmé' # Vérification si le nombre de réservation pour la date choisi n'est pas plus grande que 4
                    instance.save() # Enregistrement des données dans la base de données
                    form.save_m2m() # Enregistement des données pour les tables lié à SGPC_RESERVATION.
                    send_mail('Modification de réservation',
                              'Bonjour,\n \n '
                              'Votre réservation a été modifier et confirmé, merci bien vouloir regarder votre espace client.\n \n SG PERFORMANCES CUSTOMS',
                              settings.EMAIL_HOST_USER,
                              [instance.RES_UTI_ID.UTI_EMAIL],
                              fail_silently=False)
                    return redirect('admin')
        else:
            messages.error(request, 'La date est deja pleine') # Message d'erreur si le nombre de réservation dépasse 4
            form = forms.modifierReservation(instance=reservation) # Affiche du formulaire de modification de réservation.
    context = {
        'reservation': reservation,
        'form': form
    }
    return render(request, 'compte/modifierReservation.html', context)



@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def creerReservationClient(request):
     if request.method == 'POST':
         parametre = SGPC_PARAMETRES.objects.get(id=1)
         form = forms.creerReservationClient(request.POST) # Récupération du formulaire de création de réservaiton pour un client.
         if form.is_valid():
             obj = form.save(commit=False)
             nbReservation = SGPC_RESERVATION.objects.filter(RES_DATE=obj.RES_DATE).count()
             if nbReservation < parametre.PAR_NBMAX_RDV_JOUR: # Filtre afin d'obtenir le nombre de réservation présente à la date choisi par l'utilisateur dans son formulaire
                 obj.RES_UTI_ID = request.user # Récupération de l'id de l'utilisateur connecté.
                 obj.save()
                 obj.RES_STATUT = "en attente de confirmation"
                 obj.save() # Enregistrement des données dans la base de données
                 emailUti = obj.RES_UTI_ID.UTI_EMAIL
                 form.save_m2m() # Enregistement des données pour les tables lié à SGPC_RESERVATION.
                 send_mail('Nouvelle réservation',
                           'Bonjour, vous avez une nouvelle réservation en attente de ' + obj.RES_UTI_ID.UTI_NOM + ' ' + obj.RES_UTI_ID.UTI_NOM + ' pour le ' + str(
                               obj.RES_DATE) + ' concernant ' + obj.RES_SER_ID.SER_NOM +
                           '\n \nMerci de bien vouloir aller consulter votre espace adminitrateur \n \n SG PERFORMANCES CUSTOMS',
                           settings.EMAIL_HOST_USER,
                           [settings.EMAIL_HOST_USER],
                           fail_silently=False)
                 send_mail('Nouvelle réservation',
                           'Bonjour\n \n, Nous avons bien pris en compte votre demande de réservation, nous vous confirmerons celle-ci dans nos plus brefs délais.\n \n SG PERFORMANCES CUSTOMS',
                           settings.EMAIL_HOST_USER,
                           [emailUti],
                           fail_silently=False)
                 return redirect('nosServices')
             messages.warning(request, 'Cette date est déjà pleine, veuillez séléctionner une autre date.') # Message d'erreur si le nombre de réservation dépasse 4
             return redirect('create_reservationClient')# Affiche du formulaire de création de réservation.
     else:
         form = forms.creerReservationClient()
     context = {
         'form': form,
     }
     return render(request, 'compte/creerReservationClient.html', context)


def listeProduits(request):
    context = {}
    produit_filtrer = ProduitFilter(request.GET, queryset=SGPC_PRODUIT.objects.filter()) # Récupération de tous les produits

    context['produit_filtrer'] = produit_filtrer
    paginated_filtered_produit = Paginator(produit_filtrer.qs, 12) # Définition du nombre de produit qui apparaîssent par page
    page_number = request.GET.get('page') # Récupération du numéro de la page
    produit_page_obj = paginated_filtered_produit.get_page(page_number) #Tous les produits avec ou sans le filtre de recherche.

    context['produit_page_obj'] = produit_page_obj

    return render(request, 'compte/listeProduits.html', context)

def supprimerProduitAdmin(request,id): #Suppression d'un produit
    return render(request,id, 'compte/supprimerProduitAdmin.html')

def detailProduitAdmin(request, produit_id):
    produit = SGPC_PRODUIT.objects.get(pk=produit_id) # Récupération du produit ayant le même id que le paramètre "produit_id"
    context = {
        'produit': produit,
    }
    return render(request, 'compte/detailProduitAdmin.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def reactiverProduitAdmin(request, pk):
    produit = SGPC_PRODUIT.objects.get(id=pk) # Récupération du produit ayant le même id que le paramètre "pk"
    form = forms.reactiverProduit(instance=produit) # Récupération du formulaire de réactivation de produit
    if request.method == 'POST':
        form = forms.reactiverProduit(request.POST, instance=produit)
        produit.is_active = True # On passe l'attribut "is_active" du produit de "False" à "True".
        if form.is_valid():
            form.save() # Enregistrement des données dans la base de données.
            return redirect('liste_produits')
    context = {
        'form' : form,
        'produit': produit,
    }
    return render(request, 'compte/admin.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def rechercheProduit(request):

    if request.method =='GET':

        search = request.GET.get('search')
        filterlist = SGPC_PRODUIT.objects.all().filter(PRO_NOM__icontains=search)
        context ={
        'filterlist' : filterlist
        }
    return render(request, 'catalogue/search_form.html', context)


@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def creerDevis(request):
    #DevisFormSet = inlineformset_factory(SGPC_DEVIS, SGPC_ASSO_SER_DEV, extra=5, can_delete = False,
    #                                     fields=('ASD_SER_ID', 'ASD_PRIX_EFFECTIF', 'ASD_COMMENTAIRE'),
    #                                     labels={'ASD_SER_ID':'Services','ASD_PRIX_EFFECTIF':'Prix effectif','ASD_COMMENTAIRE':'Commentaire'})
    # Création du formulaire afin de pouvoir enregistré les informations dans les tables d'association "SGPC_ASSO_SER_DEV"
    #Inspiré de la vidéo de Dennis Ivy youtube sur Inline Formset (https://www.youtube.com/watch?v=MRWFg30FmZQ)
   #  if request.method == 'POST':
   #      form = forms.creerDevis(request.POST) # Récupération du formulaire de création de devis.
   #  #    formset = DevisFormSet(request.POST) # Récupération du formulaire créer en première ligne
   #      if form.is_valid():
   #          obj=form.save()
   # #         formset = DevisFormSet(request.POST, instance=obj)
   #          emailUTI = obj.DEV_UTI.UTI_EMAIL
   #          if formset.is_valid():
   #              for f in formset: #Pour les formset dans formset
   #                  obj = f.save(commit=False)
   #                  ser = f.cleaned_data.get('ASD_SER_ID') # On récupère l'id du service entré dans le formulaire
   #                  if ser==None: #Test pour savoir si le champ a été rempli
   #                      break # S'il n'a pas été rempli, il sort de la boucle car il marque la fin du formulaire
    #                 ser = obj.ASD_SER_ID # On stock le numero du service
    #                 prix = obj.ASD_PRIX_EFFECTIF # On stock le prix entré par l'admin
    #                 if prix==None:# Test pour savoir si un prix pour le service à été renseigner.
    #                     service = SGPC_SERVICE.objects.get(SER_NOM=ser)
    #                     obj.ASD_PRIX_EFFECTIF = service.SER_PRIX_STANDARD # Si le prix n'a pas été renseigner, on prend le prix standard du service correspondant à la demande.
    #                 obj.save()
    #             send_mail('Votre demande de devis',
    #                       'Bonjour, \n \nVotre devis n°' + str(
    #                           numeroDevis) + ' vous attend dans votre espace client !\n \n SG PERFORMANCES CUSTOMS',
    #                       settings.EMAIL_HOST_USER,
    #                       [emailUTI],
    #                       fail_silently=False)
    #             return redirect('admin')
    # else:
    #     form = forms.creerDevis(request.POST)
    #     formset = DevisFormSet()
    # context = {
    #           'form': form,
    #           'formset': formset,
    #      }
    return render(request, 'compte/creerDevis.html')#, context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def listeMarque(request):
    marque = SGPC_MARQUE.objects.all() # Récupération de toutes les marques présentent dans la base de données
    context = {
        'marque':marque,
    }
    return render(request, 'compte/listeMarque.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def listeCategorie(request):
    categorie = SGPC_CATEGORIE.objects.all() # Récupération de toutes les catégories présentent dans la base de données
    context = {
        'categorie': categorie,
    }
    return render(request, 'compte/listeCategorie.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def creerMarque(request):
    if request.method == 'POST':
        form = forms.creerMarque(request.POST) # Récupération du formulaire de création d'une marque
        if form.is_valid():
            form.save() # Enregistrement de la marque la base de données
            return redirect('listeMarque')
    else:
        form = forms.creerMarque
    context = {
        'form':form,
    }
    return render(request, 'compte/creerMarque.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def modifierMarque(request,pk):
    marque = SGPC_MARQUE.objects.get(id=pk) # Récupération de la marque ayant le meme id que le paramètre "pk"
    form = forms.modifierMarque(instance=marque) # Récupération du formulaire de modification de marque pré-rempli avec les informations de la marque
    if request.method == 'POST':
        form = forms.modifierMarque(request.POST, instance=marque)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save() # Enregristrement des données dans la base de données
            return redirect('listeMarque')
    else:
        form = forms.modifierMarque(instance=marque)
    context = {
        'form': form,
        'marque':marque,
    }
    return render(request, 'compte/modifierMarque.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin)
def supprimerMarque(request, pk):
    marque = SGPC_MARQUE.objects.get(id=pk) # Récupération de la marque ayant le meme id que le paramètre "pk"
    form = forms.supprimerMarque(instance=marque) # Récupération du formulaire de suppression de marque
    if request.method == 'POST':
        form = forms.supprimerMarque(request.POST, instance=marque)
        marque.MAR_is_active = False # On passe l'attribut "is_active" de "True" à "False"
        if form.is_valid():
            form.save() # Enregistrement des données dans la base de données.
            return redirect('listeMarque')
    context = {
        'form': form,
        'marque': marque,
    }
    return render(request, 'compte/supprimerMarque.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def reactiverMarque(request, pk):
    marque = SGPC_MARQUE.objects.get(id=pk) # Récupération de la marque ayant le meme id que le paramètre "pk"
    form = forms.supprimerMarque(instance=marque)# Récupération du formulaire de réactivation de marque
    if request.method == 'POST':
        form = forms.supprimerMarque(request.POST, instance=marque)
        marque.MAR_is_active = True # On passe l'attribut "is_active" de "False" à "True"
        if form.is_valid():
            form.save() # Enregistrement des données dans la base de données.
            return redirect('listeMarque')
    context = {
        'form': form,
        'marque': marque,
    }
    return render(request, 'compte/supprimerMarque.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def creerCategorie(request):
    if request.method == 'POST':
        form = forms.creerCategorie(request.POST) # Récupération du formulaire de création d'une catégorie
        if form.is_valid():
            form.save() # Enregistrement des données dans la base de données
            return redirect('listeCategorie')
    else:
        form = forms.creerCategorie
    context = {
        'form':form,
    }
    return render(request, 'compte/creerCategorie.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def modifierCategorie(request, pk):
    categorie = SGPC_CATEGORIE.objects.get(id=pk) # Récupération de la catégorie ayant le meme id que le paramètre "pk"
    form = forms.modifierCategorie(instance=categorie) # Récupération du formulaire de modification de catégorie pré-rempli avec les informations de la marque
    if request.method == 'POST':
        form = forms.modifierCategorie(request.POST, instance=categorie)
        if form.is_valid():
            form.save() # Enregistrement des données dans la base de données
            return redirect('listeCategorie')
    else:
        form = forms.modifierCategorie(instance=categorie)
    context = {
        'form':form,
        'categorie': categorie,
    }
    return render(request, 'compte/modifierCategorie.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def supprimerCategorie(request, pk):
    categorie = SGPC_CATEGORIE.objects.get(id=pk) # Récupération de la catégorie ayant le meme id que le paramètre "pk"
    form = forms.supprimerCategorie(instance=categorie) # Récupération du formulaire de suppresion de catégorie concernant la catégorie récupérer ci-dessus
    if request.method == 'POST':
        form = forms.supprimerCategorie(request.POST, instance=categorie)
        categorie.CAT_is_active = False # On passe l'attribut "is_active" de "True" à "False"
        if form.is_valid():
            form.save() # Enregistrement des données dans la base de données
            return redirect('listeCategorie')
    context = {
        'form': form,
        'categorie': categorie,
    }
    return render(request, 'compte/supprimerCategorie.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def reactiverCategorie(request, pk):
    categorie = SGPC_CATEGORIE.objects.get(id=pk) # Récupération de la catégorie ayant le meme id que le paramètre "pk"
    form = forms.reactiverCategorie(instance=categorie) # Récupération du formulaire de réactivation de catégorie concernant la catégorie récupérer ci-dessus
    if request.method == 'POST':
        form = forms.reactiverCategorie(request.POST, instance=categorie)
        categorie.CAT_is_active = True # On passe l'attribut "is_active" de "False" à "True"
        if form.is_valid():
            form.save()
            return redirect('listeCategorie')
    context = {
        'form': form,
        'categorie': categorie,
    }
    return render(request, 'compte/supprimerCategorie.html', context)


@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def creerDevisReservation(request, pk, serID): #Création d'un réservation à partir d'un devis
    devis = SGPC_DEVIS.objects.get(id=pk) # Récupéation du devis ayant le même id que le paramètre "pk"
   # asso = SGPC_ASSO_SER_DEV.objects.get(ASD_DEV_ID_id=devis.id, ASD_SER_ID_id=serID) # Récupération des données dans la classe d'association "SGPC_SER_DEV_ID" dont l'id du devis correspont à l'id du devis récupérer ci-dessus ainsi que l'id du service correspondant au paramètre "serID"
    parametre = SGPC_PARAMETRES.objects.get(id=1)
    if request.method == 'POST':
        form = forms.creerReservationDevis(request.POST) # Récupération du formulaire de création de réservation à partir d'un devis
        if form.is_valid():
            obj = form.save(commit=False)
            nbReservation = SGPC_RESERVATION.objects.filter(RES_DATE=obj.RES_DATE).count() # Filtre afin d'obtenir le nombre de réservation présente à la date choisi par l'utilisateur dans son formulaire
            if nbReservation < parametre.PAR_NBMAX_RDV_JOUR:
                obj.RES_UTI_ID_id = devis.DEV_UTI_id # l'id du client pour la réservation est le même que celui du devis
       #         obj.RES_SER_ID_id = asso.ASD_SER_ID_id # L'id du service est passé dans la réservation
                obj.RES_DEV_ID_id = devis.id # L'id du devis est passé dans dans la réservation
                if obj.RES_UTI_ID.UTI_is_admin:
                    obj.RES_STATUT = "Confirmé"  # Statut de la réservation confirmé
                    send_mail(
                        'Nouvelle réservation pour le service ' + obj.RES_SER_ID.SER_NOM + 'selon le devis ' + str(
                            devis.id),
                        'Bonjour ,\n \n Suivant votre demande, nous avons programmé un rendez-vous pour le ' + str(
                            obj.RES_DATE) + ' pour le service ' + obj.RES_SER_ID.SER_NOM + '\n \n SG PERFORMANCES CUSTOMS',
                        settings.EMAIL_HOST_USER,
                        [obj.RES_UTI_ID.UTI_EMAIL],
                        fail_silently=False)
                else:
                    obj.RES_STATUT = "En attente de confirmation"
                    send_mail('Nouvelle réservation',
                              'Bonjour,\n \n Vous avez une nouvelle réservation en attente de ' + obj.RES_UTI_ID.UTI_NOM + ' ' + obj.RES_UTI_ID.UTI_PRENOM + ' pour le ' + str(
                                  obj.RES_DATE) + ' concernant ' + obj.RES_SER_ID.SER_NOM +
                              '\n \n Merci de bien vouloir aller consulter votre espace adminitrateur \n \n SG PERFORMANCES CUSTOMS',
                              settings.EMAIL_HOST_USER,
                              [settings.EMAIL_HOST_USER],
                              fail_silently=False)
                    send_mail('Nouvelle réservation',
                              'Bonjour,\n \n Nous avons bien pris en compte votre demande de réservation, nous vous confirmerons celle-ci dans nos plus brefs délais.\n \n SG PERFORMANCES CUSTOMS',
                              settings.EMAIL_HOST_USER,
                              [obj.RES_UTI_ID.UTI_EMAIL],
                              fail_silently=False)
                obj.save() # Enregistrement des données dans la base de données
                return redirect('detail_devis', pk)
            else:
                messages.error(request, 'La date est deja pleine') # Message d'erreur si le nombre de réservation dépasse 4
                form = forms.creerReservationDevis(request.POST) # Rechargement du formulaire vide
    else:
        form = forms.creerReservationDevis(request.POST)
    context = {
        'form': form,
        'devis': devis,
    #    'asso': asso,
    }
    return render(request, 'compte/creerDevisReservation.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def demandeDevis(request):
    if request.method == 'POST':
        form = forms.ContactForm(request.POST) # Récupération du formulaire de contact pour un devis
        if form.is_valid():
            choice = form.cleaned_data['choice']
            email = form.cleaned_data['email']
            demande = form.cleaned_data['demande']
            utilisateur = request.user
            if utilisateur.UTI_EMAIL == email:
                send_mail('Demande de devis',
                          'Bonjour, \n \nVous avez une nouvelle demande de devis pour les services suivant : ' + ' ' +
                          str(choice) + ' \n \n' + demande,
                          settings.EMAIL_HOST_USER,
                          [settings.EMAIL_HOST_USER],
                          fail_silently=False)
                send_mail('Votre demande de devis',
                          'Bonjour,\n \n Nous avons bien reçu votre demande de devis.\n \n'
                          'Nous vous répondrons dans nos plus brefs délais.',
                          settings.EMAIL_HOST_USER,
                          [email],
                          fail_silently=False)
                return redirect('nosServices')
            else:
                messages.error(request,'Merci de bien vouloir entrer l''adresse email correspondante à votre compte')  # Message d'erreur si le nombre de réservation dépasse 4
                form = forms.ContactForm(request.POST)
    else:
        form = forms.ContactForm
    context = {
        'form' : form,
    }
    return render(request, 'compte/demandeDevis.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def listeCommande(request): #Inspiré du cours OpenClassroom sur Django pour le paginator.
    context = {}
    com_filtrer = CommandeFiltrer(request.GET, queryset=SGPC_COMMANDE.objects.all().order_by('-id'))  # Récupération de tous les produits
    context['com_filtrer'] = com_filtrer
    paginated_filtered_commande = Paginator(com_filtrer.qs, 10)  # Définition du nombre de produit qui apparaîssent par page
    page_number = request.GET.get('page')  # Récupération du numéro de la page
    commande_page_obj = paginated_filtered_commande.get_page(page_number)  # Tous les produits avec ou sans le filtre de recherche.
    context['commande_page_obj'] = commande_page_obj
    return render(request,'compte/listeCommande.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def listeCommandeExp(request):
    commandesExpediees = SGPC_COMMANDE.objects.filter(COM_STATUT='Expédiée').order_by('-COM_DATE')[:10]# Récupération de tous les commandes expédiées trier par date
    context = {
        'commandesExpediees': commandesExpediees,
    }
    return render(request,'compte/listeCommandeExp.html',context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def listeCommandePrep(request):
    commandesEnPrepAll = SGPC_COMMANDE.objects.filter(COM_STATUT='En préparation').order_by('-COM_DATE') # Récupération de tous les commandes en préparation trier par date
    context ={
        'commandesEnPrepAll': commandesEnPrepAll,
    }
    return render(request,'compte/listeCommandePrep.html',context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def creerCommandeRDV(request, pk): # Création d'un commande pour une réservation
    reservation = SGPC_RESERVATION.objects.get(id=pk) # Récupération de la réservation ayant le meme id que le paramètre "pk"
    commande = SGPC_COMMANDE.objects.create(COM_UTI_ID_id=reservation.RES_UTI_ID_id, COM_DATE=timezone.now(), COM_STATUT="validée", COM_FACTURE_DATE=timezone.now(), COM_FACTURE_STATUT="Ouverte") # Création de la commande. L'id de l'utilisateur est le même que celui de la réservation.
    reservation.RES_COM_ID_id = commande.id # Ajout du numéro de commande à la réservation
    reservation.save() # Enregistrement des données dans la base de données.
    return redirect('detail_RDV', pk)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def listeCommandeClient(request, pk, resID):
    commande = SGPC_COMMANDE.objects.filter(Q(COM_UTI_ID_id=pk, COM_FACTURE_STATUT=None)) # Récupération des commandes faites le client
    nbCommande = commande.count() # On compte le nombre de commande.
    reservation = SGPC_RESERVATION.objects.get(id=resID) # Récupération de toutes les réservations ayant le meme id que le paramètres "resID"
    context = {
        'commande':commande,
        'reservation':reservation,
        'nbCommande':nbCommande,
    }
    return render(request, 'compte/listeCommandeClient.html', context)


def ajouterCommandeRDV(request, pk, comID): # Ajout d'une réservation à une commande déjà existante
    reservation = SGPC_RESERVATION.objects.get(id=pk) # Récupération de toutes les réservation ayant le même id que le paramètres "pk"
    commande = SGPC_COMMANDE.objects.get(id=comID) # Récupération de toutes les commandes ayant le même id que le paramètres "comID"
    reservation.RES_COM_ID_id = commande.id # Ajout du numéro de commande choisi à la réservation.
    reservation.save() # Enregistrement des données dans la base de données
    return redirect('detail_RDV', pk)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def ajouterCommandeProd(request,pk, comID):
    parametre = SGPC_PARAMETRES.objects.get(id=1)
    produit = SGPC_PRODUIT.objects.get(id=pk)
    commande = SGPC_COMMANDE.objects.get(id=comID)
    com_pro = SGPC_ASSO_COM_PRO.objects.create(ACP_COMMANDE_id=commande.id, ACP_PRODUIT_id=produit.id,
                                               ACP_QUANTITE=1, ACP_PRIX_VENTE=produit.PRO_PRIX_CATALOGUE,
                                               ACP_TAUX_TVA=parametre.PAR_TAUX_TVA)
    return redirect('detail', pk)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def listeCommandeOuverte(request,pk):
    commande = SGPC_COMMANDE.objects.filter(COM_FACTURE_STATUT='Ouverte') # Récupération des commandes faites le client
    produit = SGPC_PRODUIT.objects.get(id=pk)
    context = {
        'commande':commande,
        'produit':produit,
    }
    return render(request, 'compte/listeCommandeOuverte.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def facturePaye(request, pk):
    commande = SGPC_COMMANDE.objects.get(id=pk)
    commande.COM_FACTURE_STATUT = "Payée"
    commande.save()
    return redirect('detail_commande', pk)


@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def listParametre(request):
   parametres = SGPC_PARAMETRES.objects.all() # Récupération de tous les paramètres.
   context = {
       'parametres': parametres,
   }
   return render(request, "compte/listParametre.html", context)


@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def modifParametre(request, pk):
   parametre = SGPC_PARAMETRES.objects.get(id=pk) # Récupération du paramètre ayant le même id que le paramètre "pk"
   form = forms.ModifParametre(instance=parametre) # Récupération du formulaire de modification de paramètres.
   if request.method == 'POST':
       form = forms.ModifParametre(request.POST, instance=parametre)
       if form.is_valid():
           instance = form.save(commit=False)
           form.save() # Enregistrement des données dans la base de données.
           return redirect('listParametre')
   else:
       form = forms.ModifParametre(instance=parametre)

   context = {
       'form': form,
       'parametre': parametre,
   }
   return render(request, "compte/modifParametre.html", context)

#inspiré de https://www.youtube.com/watch?v=5umK8mwmpWM
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

# #inspiré de https://www.youtube.com/watch?v=5umK8mwmpWM
class devisPDF(View):
    def get(self, request, id, *args, **kwargs):
        devis = SGPC_DEVIS.objects.get(id=id)
      #  assos = SGPC_ASSO_SER_DEV.objects.all().filter(ASD_DEV_ID_id=id)
        reservation = SGPC_RESERVATION.objects.all().filter(RES_DEV_ID_id=devis.id)
        data = {
            "devis": devis,
      #      "assos": assos,
            "reservation":reservation,
        }
        pdf = render_to_pdf('compte/devis_pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
@user_passes_test(lambda u: u.UTI_is_admin) #inspirer de https://stackoverflow.com/questions/21649439/redirecting-user-passes-testlambda-u-u-is-superuser-if-not-a-superuser-to-an
def listeDevis(request):
    context = {}
    dev_filtrer = DevisFiltrer(request.GET, queryset=SGPC_DEVIS.objects.all().order_by('-id'))
    context['dev_filtrer'] = dev_filtrer
    paginated_filtered_devis = Paginator(dev_filtrer.qs, 10)  # Définition du nombre de produit qui apparaîssent par page
    page_number = request.GET.get('page')  # Récupération du numéro de la page
    devis_page_obj = paginated_filtered_devis.get_page(page_number)  # Tous les produits avec ou sans le filtre de recherche.
    context['devis_page_obj'] = devis_page_obj
    return render(request, "compte/listeDevis.html", context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def listeDevisClient(request, pk):
    devis = SGPC_DEVIS.objects.filter(DEV_UTI_id=pk).order_by('-id')
    context = {
        "devis":devis,
    }
    return render(request, "compte/listeDevisClient.html", context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def listeRDVClient(request, pk):
    reservation = SGPC_RESERVATION.objects.filter(RES_UTI_ID_id=pk).order_by('-RES_DATE')
    context = {
        "reservation": reservation,
    }
    return render(request, "compte/listeRDVClient.html", context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def listeCommandeEspaceClient(request, pk):
    commande = SGPC_COMMANDE.objects.filter(COM_UTI_ID_id=pk) # Récupération des commandes faites le client
    context = {
        'commande':commande,
    }
    return render(request, 'compte/listeCommandeEspaceClient.html', context)

@login_required(login_url="/login/")#inspirer de https://www.youtube.com/watch?v=eBsc65jTKvw
def listeRendezVous(request): # Paginator inspiré du cours OpenClassroom sur Django
    context = {}
    rdv_filtrer = rdvFilter(request.GET, queryset=SGPC_RESERVATION.objects.all().order_by('-id'))
    context['rdv_filtrer'] = rdv_filtrer
    paginated_filtered_rdv = Paginator(rdv_filtrer.qs,
                                         10)  # Définition du nombre de produit qui apparaîssent par page
    page_number = request.GET.get('page')  # Récupération du numéro de la page
    rdv_page_obj = paginated_filtered_rdv.get_page(
        page_number)  # Tous les produits avec ou sans le filtre de recherche.
    context['rdv_page_obj'] = rdv_page_obj
    return render(request, 'compte/listRendezVous.html', context)
