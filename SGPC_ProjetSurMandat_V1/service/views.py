from django.shortcuts import render

from django.contrib.auth.decorators import login_required, user_passes_test

# from service.models import SGPC_SERVICE
# 
# 
# 
# # Create your views here.
# def Services(request):
#     services = SGPC_SERVICE.objects.all() #Récupération de tous les services.
#     context = {
#         'services': services,
#     }
#     return render(request, 'service/service.html', context)
