from django.test import TestCase
from django.urls import reverse

from .models import Feedback


class ContatoTests(TestCase):
    def setUp(self):
        self.url = reverse('contato')
        self.dados_validos = {
            'nome': 'Maria Silva',
            'email': 'maria@exemplo.com',
            'assunto': 'Elogio',
            'mensagem': 'Ótimo projeto!',
        }

    def test_pagina_do_formulario_abre(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contato/contato.html')

    def test_envio_valido_salva_feedback_no_banco(self):
        response = self.client.post(self.url, self.dados_validos)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['sucesso'])
        self.assertEqual(Feedback.objects.count(), 1)

        feedback = Feedback.objects.first()
        self.assertEqual(feedback.nome, 'Maria Silva')
        self.assertEqual(feedback.email, 'maria@exemplo.com')
        self.assertEqual(feedback.assunto, 'Elogio')

    def test_campos_obrigatorios_vazios_nao_salvam(self):
        response = self.client.post(self.url, {
            'nome': '',
            'email': '',
            'assunto': '',
            'mensagem': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['sucesso'])
        self.assertEqual(len(response.context['erros']), 4)
        self.assertEqual(Feedback.objects.count(), 0)

    def test_email_invalido_nao_salva(self):
        dados = {**self.dados_validos, 'email': 'isso-nao-e-email'}
        response = self.client.post(self.url, dados)

        self.assertIn('Informe um e-mail válido.', response.context['erros'])
        self.assertEqual(Feedback.objects.count(), 0)

    def test_nome_acima_do_limite_nao_salva(self):
        dados = {**self.dados_validos, 'nome': 'a' * 101}
        response = self.client.post(self.url, dados)

        self.assertIn(
            'O nome pode ter no máximo 100 caracteres.',
            response.context['erros'],
        )
        self.assertEqual(Feedback.objects.count(), 0)

    def test_dados_digitados_sao_mantidos_quando_ha_erro(self):
        dados = {**self.dados_validos, 'email': 'invalido'}
        response = self.client.post(self.url, dados)

        self.assertEqual(response.context['dados']['nome'], 'Maria Silva')