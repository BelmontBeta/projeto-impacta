from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .esg.analise import (
    analisar,
    calcular_nota_geral,
    definir_nivel,
    gerar_plano_de_acao,
)
from .esg.config import ESCALAS
from .esg.missoes import missoes
from .esg.perguntas import perguntas
from .models import Diagnostico, MissaoPlano

User = get_user_model()

# O projeto usa o armazenamento de estáticos com manifesto (WhiteNoise), que
# só funciona depois do collectstatic. Nos testes usamos o armazenamento simples.
ESTATICOS_SIMPLES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


def respostas_com(pontos):
    return [
        {"id": p["id"], "pilar": p["pilar"], "pontos": pontos}
        for p in perguntas
    ]


class DadosTests(TestCase):
    def test_toda_pergunta_tem_missao(self):
        for item in perguntas:
            self.assertIn(item["id"], missoes, item["id"])

    def test_ids_de_perguntas_sao_unicos(self):
        ids = [p["id"] for p in perguntas]
        self.assertEqual(len(ids), len(set(ids)))

    def test_escalas_tem_quatro_opcoes(self):
        for tipo, opcoes in ESCALAS.items():
            self.assertEqual(len(opcoes), 4, tipo)
        for item in perguntas:
            self.assertIn(item["tipo"], ESCALAS)


class AnaliseTests(TestCase):
    def test_tudo_maximo_da_100(self):
        self.assertEqual(calcular_nota_geral(respostas_com(3)), 100)

    def test_tudo_minimo_da_zero(self):
        self.assertEqual(calcular_nota_geral(respostas_com(0)), 0)

    def test_pilares_sao_os_tres(self):
        self.assertEqual(
            set(analisar(respostas_com(2))),
            {"Ambiental", "Social", "Governança"},
        )

    def test_niveis_nos_limites(self):
        self.assertEqual(definir_nivel(0)["nome"], "Inicial")
        self.assertEqual(definir_nivel(25)["nome"], "Inicial")
        self.assertEqual(definir_nivel(26)["nome"], "Em Desenvolvimento")
        self.assertEqual(definir_nivel(69)["nome"], "Estruturado")
        self.assertEqual(definir_nivel(100)["nome"], "Avançado")

    def test_plano_vazio_quando_tudo_bem(self):
        self.assertEqual(gerar_plano_de_acao(respostas_com(3), missoes), [])

    def test_plano_limitado_a_quatro_semanas(self):
        plano = gerar_plano_de_acao(respostas_com(0), missoes)
        self.assertEqual(len(plano), 4)
        self.assertEqual([m["semana"] for m in plano], [1, 2, 3, 4])

    def test_plano_varia_os_pilares(self):
        pilares = {m["pilar"] for m in gerar_plano_de_acao(respostas_com(0), missoes)}
        self.assertEqual(len(pilares), 3)


@override_settings(STORAGES=ESTATICOS_SIMPLES)
class FluxoTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username="ana@exemplo.com",
            email="ana@exemplo.com",
            password="senha-forte-123",
            first_name="Ana",
        )
        self.client.force_login(self.usuario)

    def responder_tudo(self, pontos=2):
        self.client.post(reverse("guardiao:iniciar"))
        resposta = None
        for numero in range(1, len(perguntas) + 1):
            resposta = self.client.post(
                reverse("guardiao:pergunta", args=[numero]),
                {"resposta": pontos},
            )
        return resposta

    def test_telas_exigem_login(self):
        self.client.logout()
        for nome, args in [
            ("boas_vindas", []),
            ("pergunta", [1]),
            ("ultimo_resultado", []),
        ]:
            resposta = self.client.get(reverse(f"guardiao:{nome}", args=args))
            self.assertEqual(resposta.status_code, 302, nome)
            self.assertIn("/acesso/", resposta["Location"])

    def test_boas_vindas_mostra_botao_de_iniciar(self):
        resposta = self.client.get(reverse("guardiao:boas_vindas"))
        self.assertContains(resposta, "Começar diagnóstico")

    def test_pergunta_sem_iniciar_volta_para_o_inicio(self):
        resposta = self.client.get(reverse("guardiao:pergunta", args=[1]))
        self.assertRedirects(resposta, reverse("guardiao:boas_vindas"))

    def test_nao_pode_pular_perguntas(self):
        self.client.post(reverse("guardiao:iniciar"))
        resposta = self.client.get(reverse("guardiao:pergunta", args=[5]))
        self.assertRedirects(
            resposta,
            reverse("guardiao:pergunta", args=[1]),
            fetch_redirect_response=False,
        )

    def test_pergunta_inexistente_da_404(self):
        self.client.post(reverse("guardiao:iniciar"))
        self.assertEqual(
            self.client.get(reverse("guardiao:pergunta", args=[99])).status_code,
            404,
        )

    def test_resposta_invalida_mostra_erro(self):
        self.client.post(reverse("guardiao:iniciar"))
        for valor in ("", "9", "abc"):
            resposta = self.client.post(
                reverse("guardiao:pergunta", args=[1]), {"resposta": valor}
            )
            self.assertContains(resposta, "Escolha uma das opções")

    def test_fluxo_completo_salva_diagnostico_e_plano(self):
        resposta = self.responder_tudo(pontos=1)
        diagnostico = Diagnostico.objects.get()

        self.assertRedirects(
            resposta, reverse("guardiao:resultado", args=[diagnostico.pk])
        )
        self.assertEqual(diagnostico.usuario, self.usuario)
        self.assertEqual(len(diagnostico.respostas), len(perguntas))
        self.assertAlmostEqual(diagnostico.nota_geral, 33.3, places=1)
        self.assertEqual(MissaoPlano.objects.filter(diagnostico=diagnostico).count(), 4)

    def test_todas_as_telas_de_resultado_abrem(self):
        self.responder_tudo(pontos=1)
        diagnostico = Diagnostico.objects.get()

        resposta = self.client.get(reverse("guardiao:resultado", args=[diagnostico.pk]))
        self.assertContains(resposta, "Seu diagnóstico está pronto!")
        self.assertContains(resposta, "Em Desenvolvimento")

        resposta = self.client.get(
            reverse("guardiao:resultado_detalhado", args=[diagnostico.pk])
        )
        self.assertContains(resposta, "Resultado por pilar")
        self.assertContains(resposta, "Faço às vezes")

        resposta = self.client.get(reverse("guardiao:plano", args=[diagnostico.pk]))
        self.assertContains(resposta, "Plano de ação")
        self.assertContains(resposta, "Ver missão")

        missao = diagnostico.missoes.first()
        resposta = self.client.get(
            reverse("guardiao:missao", args=[diagnostico.pk, missao.missao_id])
        )
        self.assertContains(resposta, missoes[missao.missao_id]["titulo"])

    def test_plano_vazio_quando_tudo_perfeito(self):
        self.responder_tudo(pontos=3)
        diagnostico = Diagnostico.objects.get()
        resposta = self.client.get(reverse("guardiao:plano", args=[diagnostico.pk]))
        self.assertContains(resposta, "Parabéns!")

    def test_marcar_missao_como_concluida_e_destacada(self):
        self.responder_tudo(pontos=0)
        diagnostico = Diagnostico.objects.get()
        missao = diagnostico.missoes.first()
        url = reverse("guardiao:missao_alternar", args=[diagnostico.pk, missao.missao_id])

        self.client.post(url, {"campo": "concluida"})
        self.client.post(url, {"campo": "destacada"})
        missao.refresh_from_db()
        self.assertTrue(missao.concluida)
        self.assertTrue(missao.destacada)

        self.client.post(url, {"campo": "concluida"})
        missao.refresh_from_db()
        self.assertFalse(missao.concluida)

    def test_alternar_exige_post_e_campo_valido(self):
        self.responder_tudo(pontos=0)
        diagnostico = Diagnostico.objects.get()
        missao = diagnostico.missoes.first()
        url = reverse("guardiao:missao_alternar", args=[diagnostico.pk, missao.missao_id])

        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url, {"campo": "id"}).status_code, 404)

    def test_redirect_externo_e_ignorado(self):
        self.responder_tudo(pontos=0)
        diagnostico = Diagnostico.objects.get()
        missao = diagnostico.missoes.first()
        url = reverse("guardiao:missao_alternar", args=[diagnostico.pk, missao.missao_id])

        resposta = self.client.post(
            url, {"campo": "concluida", "voltar": "https://site-malicioso.com/"}
        )
        self.assertRedirects(
            resposta,
            reverse("guardiao:plano", args=[diagnostico.pk]),
        )

    def test_outro_usuario_nao_ve_o_diagnostico(self):
        self.responder_tudo(pontos=1)
        diagnostico = Diagnostico.objects.get()

        outro = User.objects.create_user(
            username="bia@exemplo.com", email="bia@exemplo.com", password="senha-forte-123"
        )
        self.client.force_login(outro)

        for nome in ("resultado", "resultado_detalhado", "plano"):
            resposta = self.client.get(reverse(f"guardiao:{nome}", args=[diagnostico.pk]))
            self.assertEqual(resposta.status_code, 404, nome)

        missao = diagnostico.missoes.first()
        url = reverse("guardiao:missao_alternar", args=[diagnostico.pk, missao.missao_id])
        self.assertEqual(self.client.post(url, {"campo": "concluida"}).status_code, 404)

    def test_segundo_diagnostico_mostra_evolucao(self):
        self.responder_tudo(pontos=1)
        self.responder_tudo(pontos=3)
        ultimo = Diagnostico.objects.first()
        resposta = self.client.get(reverse("guardiao:resultado", args=[ultimo.pk]))
        self.assertContains(resposta, "pontos")
        self.assertContains(resposta, "+67")

    def test_login_leva_para_o_guardiao(self):
        self.client.logout()
        resposta = self.client.post(
            "/acesso/",
            {"acao": "login", "email": "ana@exemplo.com", "senha": "senha-forte-123"},
        )
        self.assertRedirects(
            resposta, "/guardiao/boas-vindas/", fetch_redirect_response=False
        )
