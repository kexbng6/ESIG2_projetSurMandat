from django.conf.urls import url
from django.urls import path, include
from catalogue import views


urlpatterns = [
    url(r'notre_catalogue/', views.catalogue, name="catalogue"),
    url(r'^(?P<produit_id>[0-9]+)/$', views.detail, name="detail"),

    #url du panier
    path('cart/add/<int:id>/', views.ajouterPanier, name='ajouterPanier'),# inspiré de https://pypi.org/project/django-shopping-cart/
    path('cart/item_clear/<int:id>/', views.supprimerProduitPanier, name='supprimerProduitPanier'),# inspiré de https://pypi.org/project/django-shopping-cart/
    path('mon_panier/', views.detailPanier, name='detailPanier'),# inspiré de https://pypi.org/project/django-shopping-cart/
    path('cart/item_increment/<int:id>/', views.augmenterNbProduit, name='augmenterNbProduit'),# inspiré de https://pypi.org/project/django-shopping-cart/
    path('cart/item_decrement/<int:id>/', views.diminuerNbProduit, name='diminuerNbProduit'),# inspiré de https://pypi.org/project/django-shopping-cart/
    path('cart/cart_clear/', views.viderPanier, name='viderPanier'),# inspiré de https://pypi.org/project/django-shopping-cart/

    path(r'votre_commande/', views.resumerCommande, name="resumerCommande"),
    path('commander/', views.creerCommandeProduit, name="creerCommande"),
    path(r'commandeAnnulee/', views.commandeAnnulee, name="commandeAnnulee"),
    path(r'commandeErreur/', views.commandeErreur, name="commandeErreur"),
    path(r'checkout/', views.checkout, name="checkout"),

    path('pdf_view/<int:id>/', views.ViewPDF.as_view(), name="pdf_view"),#inspiré de https://www.youtube.com/watch?v=5umK8mwmpWM

    path('search/', views.search, name="search"),

    # path('numeroSuivi/<str:id>/', views.numeroSuivi, name="numeroSuivi"),

]
