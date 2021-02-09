import django_filters

from .models import SGPC_PRODUIT, SGPC_MARQUE, SGPC_CATEGORIE, SGPC_COMMANDE


#Création du filtre pour le catalogue et la liste des produits de l'admin.
class ProduitFilter(django_filters.FilterSet):
    class Meta:
        model = SGPC_PRODUIT
        fields = [
            'PRO_MARQUE',
            'PRO_CATEGORIE',
                ]

    def __init__(self, *args, **kwargs): #Définition des label pour les filtres dans le catalogue.
        super(ProduitFilter, self).__init__(*args, **kwargs)
        self.filters['PRO_MARQUE'].label = 'Marque'
        self.filters['PRO_CATEGORIE'].label = 'Catégorie'


