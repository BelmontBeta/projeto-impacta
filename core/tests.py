from django.test import TestCase
from django.urls import reverse


class PaginasPrincipaisTests(TestCase):
    def test_paginas_principais_respondem_200(self):
        paginas = {
            'home': 'core/home.html',
            'sobre': 'core/sobre.html',
            'desafios': 'core/desafios.html',
            'solucoes': 'core/solucoes.html',
        }

        for nome, template in paginas.items():
            with self.subTest(pagina=nome):
                response = self.client.get(reverse(nome))
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template)

    def test_home_esta_na_raiz_do_site(self):
        self.assertEqual(reverse('home'), '/')

    def test_pagina_inexistente_retorna_404(self):
        response = self.client.get('/pagina-que-nao-existe/')
        self.assertEqual(response.status_code, 404)

        