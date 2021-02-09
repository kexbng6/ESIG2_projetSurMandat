from django.conf.urls import url
from django.urls import path
from django.contrib.auth import views as auth_views

from compte import views



urlpatterns = [
    url(r'login/',views.loginPage, name="login"),
    url(r'logout/',views.logoutPage, name="logout"),
    url(r'signup/',views.signUpView, name="signup"),
    url(r'admin/',views.adminView, name="admin"),
    url(r'liste_produits/',views.listeProduits, name="liste_produits"),
    url('creerProduit/', views.creerProduit, name="create_produit"),
    url('creerReservation/', views.creerReservation, name="create_reservation"),
    url('creerReservationClient/', views.creerReservationClient, name="create_reservationClient"),
    url('creerClient/', views.creerClient, name="creerClient"),
    url('creerDevis/', views.creerDevis, name="creerDevis"),
    url('creerMarque/', views.creerMarque, name="creerMarque"),
    url('creerCategorie/', views.creerCategorie, name="creerCategorie"),
    url('listeMarque/', views.listeMarque, name="listeMarque"),
    url('listeCategorie/', views.listeCategorie, name="listeCategorie"),
    path('client/<str:pk>',views.espaceClient, name="client"),
    path('modifierProduit/<str:pk>', views.modifierProduit, name="modif_produit"),
    path('supprimerProduit/<str:pk>', views.supprimerProduit, name="supprimer_produit"),
    url(r'^(?P<produit_id>[0-9]+)/$', views.detailProduitAdmin, name="detailProduitAdmin"),
    path('reactiverProduit/<str:pk>', views.reactiverProduitAdmin, name="reactiverProduit"),
    path('supprimerProduitadmin/<str:id>', views.supprimerProduitAdmin, name="supprimer_produitAdmin"),
    path('detailRDV/<str:pk>', views.detailRDV, name="detail_RDV"),
    path('detailCommande/<str:pk>', views.detailCommande, name="detail_commande"),
    path('detailDevis/<str:pk>', views.detailDevis, name="detail_devis"),
    path('modifierDonnees/<str:pk>', views.modifierDonnees, name="modif_donnees"),
    path('modifierReservation/<str:pk>', views.modifierReservation, name="modif_reservation"),
    path('rechercheProduit/', views.rechercheProduit, name="rechercheProduit"),
    path('listParametre/', views.listParametre, name='listParametre'),
    path('modifParametre/<str:pk>', views.modifParametre, name='modifParametre'),
    path('modifierMarque/<str:pk>', views.modifierMarque, name="modif_marque"),
    path('modifierCategorie/<str:pk>', views.modifierCategorie, name="modif_categorie"),
    path('supprimerMarque/<str:pk>', views.supprimerMarque, name="supprimer_marque"),
    path('reactiverMarque/<str:pk>', views.reactiverMarque, name="reactiver_marque"),
    path('supprimerCategorie/<str:pk>', views.supprimerCategorie, name="supprimer_categorie"),
    path('reactiverCategorie/<str:pk>', views.reactiverCategorie, name="reactiver_categorie"),
    path('creerDevisReservation/<str:pk>/<str:serID>', views.creerDevisReservation, name="creerDevisReservation"),
    path('listeCommandeClient/<str:pk>/<str:resID>',views.listeCommandeClient, name="listeCommandeClient"),
    url(r'listeCommandePrep/', views.listeCommandePrep, name="listeCommandePrep"),
    url(r'listeCommandeExp/', views.listeCommandeExp, name="listeCommandeExp"),
    url(r'listeCommande/', views.listeCommande, name="listeCommande"),
    path('creerCommandeRDV/<str:pk>', views.creerCommandeRDV, name="creerCommandeRDV"),
    path('ajouterCommandeRDV/<str:pk>/<str:comID>', views.ajouterCommandeRDV, name="ajouterCommandeRDV"),
    path('devisPDF/<int:id>/', views.devisPDF.as_view(), name="devisPDF"),#inspiré de https://www.youtube.com/watch?v=5umK8mwmpWM
    path('numeroSuivi/<str:id>/', views.numeroSuivi, name="numeroSuivi"),
    path('listeCommandeOuverte/<str:pk>/', views.listeCommandeOuverte, name="listeCommandeOuverte"),
    path('ajouterCommandeProd/<str:pk>/<str:comID>', views.ajouterCommandeProd, name="ajouterCommandeProd"),
    path('facturePaye/<str:pk>/', views.facturePaye, name="facturePaye"),
    url(r'listeDevis/', views.listeDevis, name="listeDevis"),
    path('listeDevisClient/<str:pk>/', views.listeDevisClient, name="listeDevisClient"),
    path('listeRDVClient/<str:pk>/', views.listeRDVClient, name="listeRDVClient"),
    path('listeCommandeEspaceClient/<str:pk>/', views.listeCommandeEspaceClient, name="listeCommandeEspaceClient"),
    path('listeRendezVous/', views.listeRendezVous, name='listeRendezVous'),

    url('demandeDevis/', views.demandeDevis, name="demandeDevis"),

    #réinitialisation de mot de passe // inspiré de https://www.youtube.com/watch?v=sFPcd6myZrY
    path('reset_password/',
        auth_views.PasswordResetView.as_view(template_name="compte/password_reset.html"),
        name="reset_password"),

    path('reset_password_sent/',
        auth_views.PasswordResetDoneView.as_view(template_name="compte/password_reset_sent.html"),
        name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name="compte/password_reset_form.html"),
        name="password_reset_confirm"),

    path('reset_password_complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name="compte/password_reset_done.html"),
        name="password_reset_complete"),


]
