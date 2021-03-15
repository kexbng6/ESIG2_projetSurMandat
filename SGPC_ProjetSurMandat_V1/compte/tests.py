from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from compte.decorators import unauthenticated_user
from SGPC_ProjetSurMandat_V1 import settings
from SGPC_ProjetSurMandat_V1.settings import AUTH_USER_MODEL
from compte.views import loginPage
from compte.models import SGPC_Utilisateur
from compte.forms import loginForm
from django.test.client import RequestFactory


# Create your tests here.
class TestoCase(TestCase):
    def setUp(self):
        userTest = SGPC_Utilisateur.objects.create(UTI_EMAIL='test@moi.ch', password='mdp',
                                                   UTI_DATENAISSANCE='1990-09-09')
        self.user = SGPC_Utilisateur.objects.get(UTI_EMAIL='test@moi.ch')
        self.login_url = reverse('login')
        # self.loginForm = loginForm()

    def test_login(self):
        form = loginForm(data={'username': 'iuiui', 'passeword': 'mdp'})
        adminPage = self.client.get(reverse('admin'))
        response = self.client.get(reverse('index'))

        # print(form.errors)
        print(response.context['user'].is_authenticated)
        # self.assertRedirects(adminPage,'/compte/login/?next=/compte/admin/')
        self.assertTrue(form.is_valid())


class Test_login_page(TestCase):
    def setUp(self):
        # SGPC_Utilisateur.objects.create(UTI_EMAIL='test@moi.ch', password='mdp', UTI_DATENAISSANCE='1990-09-09')
        # self.user = SGPC_Utilisateur.objects.get(UTI_EMAIL='test@moi.ch')
        self.user = SGPC_Utilisateur.objects.create_user('test@moi.ch', '1990-01-01', 'mdp')
        self.login_url = reverse('login')
        self.index_url = reverse('index')
        self.factory = RequestFactory()

    def test_formIsValid(self):
        data_form = {
            'username': 'test@moi.ch',
            'password': 'mdp'
        }
        login_form = loginForm(data=data_form)
        self.assertTrue(login_form.is_valid())

    def test_formNotValid(self):
        data_form = {
            'username': 'test@moi.ch',
            'password': 'fauxMdp'
        }
        login_form = loginForm(data=data_form)
        self.assertFalse(login_form.is_valid())

    def test_request_not_post(self):
        self.client.login(username='test@moi.ch', password='mdp')
        # response = self.client.get(self.login_url)
        request = self.factory.get(self.login_url)
        request.user = self.user
        #        @unauthenticated_user()
        resp = self.client.get(self.login_url)  # loginPage(request)
        # loginPage(request)
        # request = self.factory.get(self.login_url)
        # resp = anonym_view(request)
        self.assertRedirects(resp, '/')

    def test_redirect_userLogged_loginPage(self):
        self.client.login(username='test@moi.ch', password='mdp')
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.index_url)

    def test_request_method_not_post(self):
        form = loginForm()
        request = self.factory.get(self.login_url)
        request.user = self.user
        loginPage(request)
        self.assertEqual(loginForm(), form)

    def test_request_method_post(self):
        data_form = {
            'username': 'test@moi.ch',
            'password': 'mdp123'
        }
        response = self.client.post(
            self.login_url, data=data_form
        )
        response.user = self.user
        login_page = loginPage(response)
        # self.assertEqual(response.status_coakde, 200)
        self.assertEqual(login_page, data_form)