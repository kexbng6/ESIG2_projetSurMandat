from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(SGPC_COMMANDE)
admin.site.register(SGPC_PRODUIT)
admin.site.register(SGPC_PARAMETRES)
admin.site.register(SGPC_ASSO_COM_PRO)
admin.site.register(SGPC_MARQUE)
admin.site.register(SGPC_CATEGORIE)