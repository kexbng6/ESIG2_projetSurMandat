from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(SGPC_RESERVATION)
#admin.site.register(SGPC_SERVICE)
admin.site.register(SGPC_DEVIS)
#admin.site.register(SGPC_ASSO_SER_DEV)