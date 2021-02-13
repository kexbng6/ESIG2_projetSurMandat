from django.shortcuts import render, redirect
from activatable_model.models import BaseActivatableModel
from cart.cart import Cart
from catalogue.models import SGPC_PRODUIT, SGPC_COMMANDE, SGPC_ASSO_COM_PRO, SGPC_PARAMETRES, SGPC_MARQUE, SGPC_CATEGORIE
from service.models import SGPC_RESERVATION#, SGPC_ASSO_SER_DEV
from django.contrib import messages
from django.utils import timezone
from .filters import ProduitFilter
from django.core.paginator import Paginator#, PageNotAnInteger, EmptyPage
from django.db.models import Q

from compte.models import SGPC_Utilisateur

from django.views.decorators.csrf import csrf_exempt#, requires_csrf_token

from django.contrib.auth.decorators import login_required#, user_passes_test
from django.http import HttpResponse
from django.views import View
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa




# Create your views here.
def index(request):
    return render(request, 'index.html')

def catalogue(request):
    context = {}
    #produit_list = SGPC_PRODUIT.objects.filter(is_active=1)
    produit_filtrer = ProduitFilter(request.GET, queryset=SGPC_PRODUIT.objects.filter(is_active=1)) # Récupération de tous les produits actif dans la base de données
    #produit_list = myFilter.qs

    context['produit_filtrer'] = produit_filtrer

    # paginator = Paginator(produit_list, 21)
    # page = request.GET.get('page',1)
    # try:
    #     produit = paginator.page(page)
    # except PageNotAnInteger:
    #     produit = paginator.page(1)
    # except EmptyPage:
    #     produit = paginator.page(paginator.num_pages)
    paginated_filtered_produit = Paginator(produit_filtrer.qs,12) # Définition du nombre de produit qui apparaîssent par page
    page_number = request.GET.get('page') # Récupération du numéro de la page
    produit_page_obj = paginated_filtered_produit.get_page(page_number) #Tous les produits avec ou sans le filtre de recherche.

    context['produit_page_obj'] = produit_page_obj


    return render(request, 'catalogue/catalogue.html', context)


def detail(request, produit_id):
    produit = SGPC_PRODUIT.objects.get(pk=produit_id) #Récupération du produit sur lequel on a cliqué dans la boutique grace à son ID.
    context = {
        'produit': produit,
    }
    return render(request, 'catalogue/detail.html', context)

# inspiré de https://pypi.org/project/django-shopping-cart/
@login_required(login_url="/login/")
def ajouterPanier(request, id):
    panier = Cart(request)
    produit = SGPC_PRODUIT.objects.get(id=id)
    panier.add(product=produit)
    messages.success(request, 'Le produit a été ajouté au panier')
    return redirect("detail", id)

# inspiré de https://pypi.org/project/django-shopping-cart/
@login_required(login_url="/login/")
def detailPanier(request):
    panier = Cart(request).cart.values()
    commande = []

    for prod in panier:
        listProdQuantite = prod.get("quantity")
        listProdPrix = prod.get("price")
        totalLig = int(listProdPrix) * int(listProdQuantite)
        commande.append(totalLig)

    panierTot = sum(commande)
    context = {
        'panierTot': panierTot,
    }
    return render(request, 'catalogue/detailPanier.html', context)

# inspiré de https://pypi.org/project/django-shopping-cart/
@login_required(login_url="/login/")
def augmenterNbProduit(request, id):
    panier = Cart(request)
    produit = SGPC_PRODUIT.objects.get(id=id)
    panier.add(product=produit)
    return redirect("detailPanier")

# inspiré de https://pypi.org/project/django-shopping-cart/
@login_required(login_url="/login/")
def diminuerNbProduit(request, id):
    panier = Cart(request)
    produit = SGPC_PRODUIT.objects.get(id=id)
    panier.decrement(product=produit)
    return redirect("detailPanier")

# inspiré de https://pypi.org/project/django-shopping-cart/
@login_required(login_url="/login/")
def supprimerProduitPanier(request, id):
    panier = Cart(request)
    produit = SGPC_PRODUIT.objects.get(id=id)
    panier.remove(produit)
    return redirect("detailPanier")

# inspiré de https://pypi.org/project/django-shopping-cart/
@login_required(login_url="/login/")
def viderPanier(request):
    panier = Cart(request)
    panier.clear()
    return redirect("detailPanier")

@login_required(login_url="/login/")
def resumerCommande(request):
    parametre = SGPC_PARAMETRES.objects.get(id=1)
    panier = Cart(request).cart.values()
    commande = []
    nbProduit = 0

    for prod in panier:
        listProdQuantite = prod.get("quantity")
        listProdPrix = prod.get("price")
        totalLig = int(listProdPrix) * int(listProdQuantite)
        commande.append(totalLig)
        nbProduit+=listProdQuantite

    commandeTot = sum(commande)
    if nbProduit <= parametre.PAR_FRAIS_LIVRAISON_PETIT:
        commandeTot+=parametre.PAR_FRAIS_LIVRAISON_PETIT
        fraisLivraison = parametre.PAR_FRAIS_LIVRAISON_PETIT
    elif nbProduit <= parametre.PAR_FRAIS_LIVRAISON_MOYEN:
        fraisLivraison = parametre.PAR_FRAIS_LIVRAISON_MOYEN
        commandeTot += parametre.PAR_FRAIS_LIVRAISON_MOYEN
    else:
        commandeTot += parametre.PAR_FRAIS_LIVRAISON_GRANDE
        fraisLivraison = parametre.PAR_FRAIS_LIVRAISON_GRANDE

    commandeTotPay = commandeTot * 100
    context = {
        'panier': panier,
        'commandeTot': commandeTot,
        'commandeTotPay': commandeTotPay,
        'fraisLivraison':fraisLivraison,
    }
    return render(request, 'catalogue/commande.html', context)


# https://pypi.org/project/django-shopping-cart/

@csrf_exempt
#@requires_csrf_token
#@login_required(login_url="/login/")
def creerCommandeProduit(request):
    global com_pro
    user = request.user
    panier = Cart(request).cart.values()
    nbProduitCom = []
    parametre = SGPC_PARAMETRES.objects.get(id=1)
    nbProduit = 0

    for qua in panier:
        listProdQuantite = qua.get("quantity")
        totalLig = int(listProdQuantite)
        nbProduitCom.append(totalLig)
        nbProduit+=listProdQuantite

    nbProduit = sum(nbProduitCom)


    if nbProduit <= parametre.PAR_FRAIS_LIVRAISON_PETIT:
        fraisLivraison = parametre.PAR_FRAIS_LIVRAISON_PETIT
    elif nbProduit <= parametre.PAR_FRAIS_LIVRAISON_MOYEN:
        fraisLivraison = parametre.PAR_FRAIS_LIVRAISON_MOYEN
    else:
        fraisLivraison = parametre.PAR_FRAIS_LIVRAISON_GRANDE

    tva = SGPC_PARAMETRES.objects.get(id=1).PAR_TAUX_TVA
    for prod in panier:
        produit = SGPC_PRODUIT.objects.get(id=prod.get("product_id"))
        if prod.get("quantity") < produit.PRO_QUANTITESTOCK:
            commande = SGPC_COMMANDE.objects.create(COM_UTI_ID_id=user.id, COM_DATE=timezone.now(), COM_STATUT="En préparation", COM_FACTURE_DATE=timezone.now(), COM_FACTURE_STATUT="Payée", COM_FRAIS_LIVRAISON=fraisLivraison)
            for prod in panier:
                com_pro = SGPC_ASSO_COM_PRO.objects.create(ACP_COMMANDE_id=commande.id, ACP_PRODUIT_id=prod.get("product_id"), ACP_QUANTITE=prod.get("quantity"), ACP_PRIX_VENTE=prod.get("price"), ACP_TAUX_TVA=tva)
                quantiteStockProduit = SGPC_PRODUIT.objects.get(id=prod.get("product_id"))
                quantiteStockProduit.PRO_QUANTITESTOCK -= prod.get("quantity")
                quantiteStockProduit.save()

            Cart(request).clear()
            context = {
                "com_pro": com_pro,
            }
            return render(request, 'catalogue/commandeProduit.html', context)

        else:
            listeProduitPanier = []
            for prod in panier:
                listeProduitPanier.append(prod.get("nom"))
                messages.info(request, 'message')
            context = {
                "listeProduitPanier" : listeProduitPanier,
            }
            return render(request, 'catalogue/detailPanier.html', context)

    return render(request, 'catalogue/commandeProduit.html')

@csrf_exempt
def commandeAnnulee(request):
    return render(request, 'catalogue/commandeProduitCancel.html')

@csrf_exempt
def commandeErreur(request):
    return render(request, 'catalogue/commandeProduitError.html')

@csrf_exempt
def checkout(request):
    return redirect("creerCommande")

def search(request): # Inspiré de la vidéo de ALL IN ONE CODE (https://www.youtube.com/watch?v=b2KecUrYmcM)
    if request.method == 'GET':
        search = request.GET.get('search')
        post = SGPC_PRODUIT.objects.all().filter(Q(PRO_NOM__icontains=search) | Q(PRO_MARQUE__MAR_NOM__icontains=search)) #Filtrage de tous les produits en fonction de ce qui a été inscrit dans la search bar, sois par le nom du produit ou alors la marque
        context ={
            'post':post
        }
        return render(request, 'catalogue/search_form.html', context)

#inspiré de https://www.youtube.com/watch?v=5umK8mwmpWM
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
#inspiré de https://www.youtube.com/watch?v=5umK8mwmpWM
class ViewPDF(View):
    def get(self, request, id, *args, **kwargs):
        commande = SGPC_COMMANDE.objects.get(id=id)
        assos = SGPC_ASSO_COM_PRO.objects.filter(ACP_COMMANDE_id=commande.id)
        tauxTVA = SGPC_ASSO_COM_PRO.objects.get(id=1).ACP_TAUX_TVA
        listProd = []

        for prod in assos:
            listProdQuantite = prod.ACP_QUANTITE
            listProdPrix = prod.ACP_PRIX_VENTE
            totalLig = int(listProdPrix) * int(listProdQuantite)
            listProd.append(totalLig)

        commandeTot = sum(listProd)

        reservation = SGPC_RESERVATION.objects.all().filter(RES_COM_ID_id=commande.id)

        for res in reservation:
            if res.RES_DEV_ID_id == None:
                commandeTot+= res.RES_SER_ID.SER_PRIX_STANDARD

                data = {
                    'commande': commande,
                    'assos': assos,
                    'reservation': reservation,
                    "commandeTot": commandeTot,
                    "tauxTVA": tauxTVA,
                }

            else :
                # assoDev = SGPC_ASSO_SER_DEV.objects.filter(Q(ASD_DEV_ID_id=res.RES_DEV_ID_id, ASD_SER_ID_id=res.RES_SER_ID_id))
                #
                # for dev in assoDev:
                #     commandeTot += dev.ASD_PRIX_EFFECTIF


                data = {
                    'commande': commande,
                    'assos': assos,
                    'reservation': reservation,
                    # 'assoDev': assoDev,
                    "commandeTot": commandeTot,
                    "tauxTVA": tauxTVA,
                }

        data = {
            "commande": commande,
            "assos": assos,
            "commandeTot": commandeTot,
            "tauxTVA" : tauxTVA,
        }
        pdf = render_to_pdf('catalogue/pdf_template.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
