#import django_filters

from catalogue.models import SGPC_PRODUIT, SGPC_MARQUE, SGPC_CATEGORIE, SGPC_COMMANDE

from service.models import SGPC_DEVIS, SGPC_RESERVATION

from django.forms.widgets import TextInput

#from django_filters import DateRangeFilter,DateFilter
from django import forms
#import datetime as dt


class DateInput(forms.DateInput):
    input_type = 'date'

# class ProduitFilter(django_filters.FilterSet):
#     class Meta:
#         model = SGPC_PRODUIT
#         fields = [
#             'PRO_MARQUE',
#             'PRO_CATEGORIE',]
#     def __init__(self, *args, **kwargs): #Définition des label pour les filtres dans le catalogue.
#         super(ProduitFilter, self).__init__(*args, **kwargs)
#         self.filters['PRO_MARQUE'].label = 'Marque'
#         self.filters['PRO_CATEGORIE'].label = 'Catégorie'


# class CommandeFiltrer(django_filters.FilterSet):
#     class Meta:
#         model = SGPC_COMMANDE
#         fields = ['COM_UTI_ID']
#
#     def __init__(self, *args, **kwargs): #Définition des label pour les filtres dans le catalogue.
#         super(CommandeFiltrer, self).__init__(*args, **kwargs)
#         self.filters['COM_UTI_ID'].label = 'Nom du client'

# class DevisFiltrer(django_filters.FilterSet):
#     class Meta:
#         model = SGPC_DEVIS
#         fields = ['DEV_UTI']
#
#     def __init__(self, *args, **kwargs): #Définition des label pour les filtres dans le catalogue.
#         super(DevisFiltrer, self).__init__(*args, **kwargs)
#         self.filters['DEV_UTI'].label = 'Nom du client'

# class rdvFilter(django_filters.FilterSet): # Inspiré de (https://stackoverflow.com/questions/30366564/daterange-on-a-django-filter)
#     start_date = DateFilter(field_name='RES_DATE', lookup_expr=('gt'), widget=TextInput(attrs={'placeholder': 'jj/mm/yyyy'} ))
#     end_date = DateFilter(field_name='RES_DATE', lookup_expr=('lt'), widget=TextInput(attrs={'placeholder': 'jj/mm/yyyy'}))
#     class Meta:
#         model = SGPC_RESERVATION
#         fields = [
#             'RES_UTI_ID',
#             'start_date',
#             'end_date',
#             #'RES_SER_ID',
#             'RES_STATUT']
#     def __init__(self, *args, **kwargs): #Définition des label pour les filtres dans le catalogue.
#         super(rdvFilter, self).__init__(*args, **kwargs)
#         self.filters['RES_UTI_ID'].label = 'Nom du client'
#         self.filters['start_date'].label = 'Date début'
#         self.filters['end_date'].label = 'Date fin'
#         #self.filters['RES_SER_ID'].label = 'Service'
#         self.filters['RES_STATUT'].label = 'Statut'

