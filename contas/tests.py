#COMANDO PARA TESTE NO CMD:
#set RODAR_SELENIUM=1 && set VELOCIDADE=0.2 && python manage.py test contas.tests.SistemaCompletoE2ETest
#OBS: lembre-se de baixar o requirements.txt antes

import datetime
import os
import re
import time
import unittest
 
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
 
User = get_user_model()
 
PASTA_DEBUG = "debug_e2e"
TOTAL_PERGUNTAS = 16
PAUSA_BASE = 1.5  # segundos de uma "pausa 1"
VELOCIDADE = float(os.environ.get("VELOCIDADE", "1"))
 
EMAIL = "gestor.restaurante@impacta.com"
SENHA = "SenhaSegura123!"
NOVA_SENHA = "NovaSenha456!"
NOME = "Gestor ESG"
NOME_NOVO = "Gestor ESG Atualizado"
 
NOME_RESTAURANTE = "Restaurante Orgânico E2E"
SLUG_RESTAURANTE = "restaurante-organico-e2e"
 
 
@unittest.skipUnless(
    os.environ.get("RODAR_SELENIUM"),
    "defina RODAR_SELENIUM=1 para rodar os testes do Chrome",
)
class SistemaCompletoE2ETest(StaticLiveServerTestCase):
    # ==================================================================
    # SETUP / TEARDOWN
    # ==================================================================
    def setUp(self):
        opts = webdriver.ChromeOptions()
        if os.environ.get("HEADLESS"):
            opts.add_argument("--headless=new")
        # Os confirm() do site (excluir ingrediente / excluir gasto) sao
        # aceitos automaticamente.
        opts.set_capability("unhandledPromptBehavior", "accept")
 
        self.browser = webdriver.Chrome(options=opts)
        self.browser.implicitly_wait(0)  # so esperas explicitas
        self.browser.maximize_window()
        self.wait = WebDriverWait(self.browser, 10)
 
        self.falhas = []
        self.diag_pk = None
        self.senha_atual = SENHA
        os.makedirs(PASTA_DEBUG, exist_ok=True)
 
    def tearDown(self):
        try:
            self.passo_lento(1)
        finally:
            self.browser.quit()
 
    # ==================================================================
    # HELPERS GERAIS
    # ==================================================================
    def passo_lento(self, fator=1.0):
        """Pausa para acompanhar visualmente (controlada por VELOCIDADE)."""
        tempo = fator * PAUSA_BASE * VELOCIDADE
        if tempo > 0:
            time.sleep(tempo)
 
    def url(self, caminho):
        return self.live_server_url + caminho
 
    def ir(self, caminho, pausa=1.0):
        self.browser.get(self.url(caminho))
        self.passo_lento(pausa)
 
    def corpo(self):
        """Texto visivel da pagina."""
        return self.browser.find_element(By.TAG_NAME, "body").text
 
    def assert_texto(self, texto, msg=None):
        # Comparacao sem diferenciar maiusculas (o CSS pode usar text-transform)
        self.assertIn(
            texto.lower(),
            self.corpo().lower(),
            msg or f"Texto nao encontrado na tela: {texto!r}",
        )
 
    def assert_html(self, texto, msg=None):
        self.assertIn(
            texto, self.browser.page_source,
            msg or f"Texto nao encontrado no HTML: {texto!r}",
        )
 
    def esperar(self, css, timeout=10, visivel=True):
        cond = (
            EC.visibility_of_element_located
            if visivel
            else EC.presence_of_element_located
        )
        return WebDriverWait(self.browser, timeout).until(cond((By.CSS_SELECTOR, css)))
 
    def esperar_xpath(self, xpath, timeout=10):
        return WebDriverWait(self.browser, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
 
    def esperar_url(self, trecho, timeout=15):
        WebDriverWait(self.browser, timeout).until(EC.url_contains(trecho))
 
    def esperar_url_igual(self, caminho, timeout=15):
        """Espera a URL ser exatamente o caminho (ignora barra final)."""
        alvo = (self.live_server_url + caminho).rstrip("/")
        WebDriverWait(self.browser, timeout).until(
            lambda d: d.current_url.split("#")[0].split("?")[0].rstrip("/") == alvo
        )
 
    def esperar_url_sem(self, trecho, timeout=15):
        """Espera a URL deixar de conter um trecho (ex.: sair de /acesso/)."""
        WebDriverWait(self.browser, timeout).until(
            lambda d: trecho not in d.current_url
        )
 
    def esperar_texto(self, texto, timeout=10):
        WebDriverWait(self.browser, timeout).until(
            lambda d: texto in d.find_element(By.TAG_NAME, "body").text
        )
 
    def todos(self, css):
        return self.browser.find_elements(By.CSS_SELECTOR, css)
 
    def existe(self, css):
        return len(self.todos(css)) > 0
 
    def _realcar(self, el):
        """Contorno vermelho no elemento para acompanhar a automacao."""
        try:
            self.browser.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});"
                "arguments[0].style.outline='3px solid #e53935';",
                el,
            )
        except Exception:
            pass
 
    def clicar(self, el, pausa=0.5):
        self._realcar(el)
        self.passo_lento(pausa * 0.5)
        self.browser.execute_script("arguments[0].click();", el)
        self.passo_lento(pausa)
 
    def enviar(self, botao, pausa=1.0):
        """Clica em um botao de submit ignorando o 'required' do navegador,
        para tambem poder testar a validacao feita pelo servidor."""
        try:
            self.browser.execute_script(
                "if (arguments[0].form) arguments[0].form.noValidate = true;", botao
            )
        except Exception:
            pass
        self.clicar(botao, pausa)
 
    def digitar(self, el, valor):
        """Digita caractere por caractere (visivel). Fallback para JS."""
        self._realcar(el)
        try:
            el.clear()
            for ch in valor:
                el.send_keys(ch)
                if VELOCIDADE > 0:
                    time.sleep(0.03 * VELOCIDADE)
        except Exception:
            self.definir_valor(el, valor)
        self.passo_lento(0.3)
 
    def definir_valor(self, el, valor):
        """Define o value via JS (campos date ou nao interativos)."""
        self._realcar(el)
        self.browser.execute_script(
            """
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
            arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
            """,
            el,
            valor,
        )
        self.passo_lento(0.3)
 
    def selecionar(self, el, valor=None, texto=None):
        self._realcar(el)
        sel = Select(el)
        if valor is not None:
            sel.select_by_value(valor)
        else:
            sel.select_by_visible_text(texto)
        self.passo_lento(0.4)
 
    def clicar_e_esperar_troca(self, el, pausa=1.0):
        """Clica e espera a pagina ser recarregada (elemento ficar 'stale')."""
        self.clicar(el, pausa=0)
        WebDriverWait(self.browser, 15).until(EC.staleness_of(el))
        self.passo_lento(pausa)
 
    def screenshot(self, nome):
        try:
            slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", nome)[:60]
            self.browser.save_screenshot(os.path.join(PASTA_DEBUG, f"{slug}.png"))
        except Exception:
            pass
 
    def tentar(self, nome, funcao, exige_login=True):
        """
        Executa uma etapa. Se falhar, registra (com screenshot e URL) e segue
        para a proxima etapa. No fim o teste FALHA se houve alguma falha.
        """
        print(f"\n>>> {nome}")
        try:
            funcao()
            if exige_login:
                self.assertNotIn(
                    "/acesso/",
                    self.browser.current_url,
                    "Redirecionado para a tela de login: sessao perdida",
                )
            print(f"    [OK] {nome}")
        except Exception as e:
            primeira = (str(e).strip().splitlines() or [""])[0]
            print(
                f"    [FALHA] {nome}: {e.__class__.__name__} {primeira}\n"
                f"            URL: {self.browser.current_url}"
            )
            self.screenshot(f"falha_{nome}")
            self.falhas.append(nome)
 
    # ------------------------------------------------------------------
    # login / logout pela interface
    # ------------------------------------------------------------------
    def _login_pela_interface(self, email, senha):
        self.ir("/acesso/")
        form = self.esperar("form[data-form='login']")
        self.digitar(form.find_element(By.ID, "login-email"), email)
        self.digitar(form.find_element(By.ID, "login-senha"), senha)
        self.clicar_e_esperar_troca(form.find_element(By.CSS_SELECTOR, "button[type='submit']"))
 
    def _sair_pelo_menu_guardiao(self):
        self.ir("/guardiao/boas-vindas/")
        self.clicar(self.esperar("#botaoConta"))
        sair = self.esperar("#menuConta .g-sair")
        self.clicar(sair, pausa=1.5)
 
    # ==================================================================
    # 1. PAGINAS PUBLICAS + CONTATO
    # ==================================================================
    def etapa_paginas_publicas(self):
        paginas = [
            ("/", "ESG aplicado ao ramo alimentício"),
            ("/sobre/", "Sobre o projeto"),
            ("/desafios/", "Desafios do ramo alimentício"),
            ("/solucoes/", "Soluções do nosso projeto"),
            ("/contato/", "Entre em contato"),
            ("/acesso/", "Bem-vindo de volta!"),
        ]
        for caminho, texto in paginas:
            self.ir(caminho, pausa=0.8)
            self.assert_html(texto, f"Texto ausente em {caminho}")
            self.assertTrue(self.browser.title.strip(), f"Sem <title> em {caminho}")
 
    def etapa_menu_publico(self):
        self.ir("/")
        navegacao = [
            ("sobre", "Sobre o projeto"),
            ("desafios", "Desafios do ramo alimentício"),
            ("solucoes", "Soluções do nosso projeto"),
            ("contato", "Entre em contato"),
            ("acesso", "Bem-vindo de volta!"),
        ]
        for trecho, texto in navegacao:
            link = self.esperar(f"#main-nav a[href*='/{trecho}/']")
            self.clicar(link, pausa=1.0)
            self.esperar_url(f"/{trecho}/")
            self.assert_html(texto)
        # Logo volta para a home
        self.clicar(self.esperar("a.logo"))
        self.esperar_url_igual("/")
 
    def etapa_contato(self):
        from contato.models import Feedback
 
        self.ir("/contato/")
 
        # (a) Envio vazio: validacao do servidor
        self.enviar(self.esperar(".contato-form button[type='submit']"), pausa=1.5)
        self.assert_texto("O campo nome é obrigatório.")
        self.assert_texto("O campo e-mail é obrigatório.")
        self.assert_texto("O campo assunto é obrigatório.")
        self.assert_texto("O campo mensagem é obrigatório.")
 
        # (b) E-mail invalido
        self.digitar(self.esperar("#nome"), "Testador E2E Selenium")
        self.digitar(self.esperar("#email"), "email-invalido")
        self.digitar(self.esperar("#assunto"), "Teste de Contato E2E")
        self.digitar(self.esperar("#mensagem"), "Mensagem automatizada.")
        self.enviar(self.esperar(".contato-form button[type='submit']"), pausa=1.5)
        self.assert_texto("Informe um e-mail válido.")
 
        # (c) Envio valido
        self.digitar(self.esperar("#email"), "testador@impacta.com")
        self.enviar(self.esperar(".contato-form button[type='submit']"), pausa=1.5)
        self.assert_texto("Mensagem enviada com sucesso!")
        self.assertTrue(
            Feedback.objects.filter(email="testador@impacta.com").exists(),
            "Feedback nao foi gravado no banco",
        )
 
    # ==================================================================
    # 2. PROTECAO DE ROTAS + LOGIN INVALIDO
    # ==================================================================
    def etapa_protecao_anonima(self):
        protegidas = [
            "/guardiao/boas-vindas/",
            "/guardiao/fornecedores/",
            "/guardiao/passaporte/editar/",
            "/gastos/painel/",
            "/gastos/registrar/",
            "/minha-conta/",
        ]
        for caminho in protegidas:
            self.ir(caminho, pausa=0.5)
            self.assertIn(
                "/acesso/?next=",
                self.browser.current_url,
                f"{caminho} deveria exigir login",
            )
 
    def etapa_login_invalido(self):
        self.ir("/acesso/")
        form = self.esperar("form[data-form='login']")
        self.digitar(form.find_element(By.ID, "login-email"), "nao.existe@impacta.com")
        self.digitar(form.find_element(By.ID, "login-senha"), "SenhaErrada999!")
        self.enviar(form.find_element(By.CSS_SELECTOR, "button[type='submit']"), pausa=1.5)
        self.assert_texto("E-mail ou senha inválidos.")
        self.assertIn("/acesso/", self.browser.current_url)
 
    # ==================================================================
    # 3. CADASTRO
    # ==================================================================
    def etapa_cadastro(self):
        self.ir("/acesso/")
        # Alterna para a aba de cadastro
        self.clicar(self.esperar("a[data-trocar='cadastro']"), pausa=1.0)
        form = self.esperar("form[data-form='cadastro']")
 
        # (a) Senha fraca -> erro de validacao
        self.digitar(form.find_element(By.ID, "cad-nome"), NOME)
        self.digitar(form.find_element(By.ID, "cad-email"), EMAIL)
        self.digitar(form.find_element(By.ID, "cad-senha"), "123")
        self.enviar(form.find_element(By.CSS_SELECTOR, "button[type='submit']"), pausa=1.5)
        self.assertIn("/acesso/", self.browser.current_url)
        self.assertTrue(self.existe(".erros li"), "Senha fraca deveria gerar erros")
 
        # (b) Cadastro valido -> ja entra logado no Guardiao
        form = self.esperar("form[data-form='cadastro']")
        self.digitar(form.find_element(By.ID, "cad-nome"), NOME)
        self.digitar(form.find_element(By.ID, "cad-email"), EMAIL)
        self.digitar(form.find_element(By.ID, "cad-senha"), SENHA)
        self.clicar(form.find_element(By.CSS_SELECTOR, "button[type='submit']"), pausa=0.5)
        self.esperar_url("/guardiao/boas-vindas/")
        self.assertTrue(User.objects.filter(email=EMAIL).exists(), "Usuario nao criado")
        self.assert_texto("Começar diagnóstico")
 
        # (c) Cadastro duplicado deve ser recusado (em outra sessao: so valida o erro)
        self._sair_pelo_menu_guardiao()
        self.ir("/acesso/?modo=cadastro")
        form = self.esperar("form[data-form='cadastro']")
        self.digitar(form.find_element(By.ID, "cad-nome"), NOME)
        self.digitar(form.find_element(By.ID, "cad-email"), EMAIL)
        self.digitar(form.find_element(By.ID, "cad-senha"), SENHA)
        self.enviar(form.find_element(By.CSS_SELECTOR, "button[type='submit']"), pausa=1.5)
        self.assert_texto("O e-mail informado já está em uso.")
 
        # volta a logar com o usuario criado
        self._login_pela_interface(EMAIL, SENHA)
        self.esperar_url("/guardiao/boas-vindas/")
 
    # ==================================================================
    # 4. MINHA CONTA
    # ==================================================================
    def etapa_minha_conta(self):
        self.ir("/minha-conta/")
        self.assert_texto("Minha conta")
        self.assert_texto(EMAIL)
 
        # Abre o painel "Editar perfil"
        self.clicar(self.esperar("#botaoEditarPerfil"))
        self.assertEqual(
            self.esperar("#botaoEditarPerfil").get_attribute("aria-expanded"), "true"
        )
 
        # Nome em branco -> erro
        campo = self.esperar("#id_first_name")
        self.digitar(campo, "")
        btn = self.esperar_xpath("//button[contains(., 'Salvar perfil')]")
        self.enviar(btn, pausa=1.5)
        self.assert_html("Informe seu nome.")
 
        # Nome valido
        self.clicar(self.esperar("#botaoEditarPerfil"))
        self.digitar(self.esperar("#id_first_name"), NOME_NOVO)
        self.enviar(self.esperar_xpath("//button[contains(., 'Salvar perfil')]"), pausa=1.5)
        self.assert_texto("Seu nome foi atualizado.")
        self.assert_texto(NOME_NOVO)
        self.assertEqual(User.objects.get(email=EMAIL).first_name, NOME_NOVO)
 
        # Troca de senha com senha antiga errada -> nao atualiza
        self.clicar(self.esperar("#botaoEditarPerfil"))
        self.digitar(self.esperar("#id_old_password"), "SenhaAntigaErrada1!")
        self.digitar(self.esperar("#id_new_password1"), NOVA_SENHA)
        self.digitar(self.esperar("#id_new_password2"), NOVA_SENHA)
        self.enviar(self.esperar_xpath("//button[contains(., 'Alterar senha')]"), pausa=1.5)
        self.assertNotIn("Sua senha foi atualizada.", self.browser.page_source)
        self.assertTrue(User.objects.get(email=EMAIL).check_password(SENHA))
 
        # Troca de senha valida
        self.clicar(self.esperar("#botaoEditarPerfil"))
        self.digitar(self.esperar("#id_old_password"), SENHA)
        self.digitar(self.esperar("#id_new_password1"), NOVA_SENHA)
        self.digitar(self.esperar("#id_new_password2"), NOVA_SENHA)
        self.enviar(self.esperar_xpath("//button[contains(., 'Alterar senha')]"), pausa=1.5)
        self.assert_texto("Sua senha foi atualizada.")
        self.assertTrue(User.objects.get(email=EMAIL).check_password(NOVA_SENHA))
        self.senha_atual = NOVA_SENHA
        # continua logado depois de trocar a senha
        self.ir("/guardiao/boas-vindas/")
 
    # ==================================================================
    # 5. BOAS-VINDAS / ABAS
    # ==================================================================
    def etapa_boas_vindas(self):
        self.ir("/gastos/painel/")  # pagina diferente para recarregar de verdade
 
        self.ir("/guardiao/boas-vindas/")
        self.assertTrue(self.existe("#slide-diagnostico.ativo"))
        self.assert_texto("Descubra como seu restaurante está em")
 
        # "Como funciona?" abre e fecha
        botao = self.esperar_xpath("//button[contains(., 'Como funciona')]")
        self.clicar(botao, pausa=1.0)
        self.assertTrue(self.esperar("#comoFunciona").is_displayed())
        self.assert_texto("16 perguntas")
        self.clicar(botao, pausa=1.0)
        self.assertFalse(self.esperar("#comoFunciona", visivel=False).is_displayed())
 
        # Abas por hash (carregando a partir de outra pagina)
        self.ir("/gastos/painel/", pausa=0.5)
        self.ir("/guardiao/boas-vindas/#metas")
        self.assertTrue(self.existe("#slide-metas.ativo"), "Aba #metas nao abriu")
        self.assert_texto("Reduzir desperdício")
 
        self.ir("/gastos/painel/", pausa=0.5)
        self.ir("/guardiao/boas-vindas/#qrcode")
        self.assertTrue(self.existe("#slide-qrcode.ativo"), "Aba #qrcode nao abriu")
        self.assert_texto("Acessar Passaporte de Sabores")
 
        # Menu do Guardiao
        self.ir("/guardiao/boas-vindas/")
        for trecho, texto in [
            ("/gastos/painel/", "Painel da cozinha"),
            ("/guardiao/fornecedores/", "Fornecedores de insumos e pontos de doação"),
            ("/guardiao/boas-vindas/", "Descubra como seu restaurante está em"),
        ]:
            self.clicar(self.esperar(f".g-menu a[href='{trecho}']"), pausa=1.0)
            self.esperar_url(trecho)
            self.assert_texto(texto)
 
    # ==================================================================
    # 6. DIAGNOSTICO ESG
    # ==================================================================
    def _numero_pergunta(self):
        m = re.search(r"/pergunta/(\d+)/", self.browser.current_url)
        return int(m.group(1)) if m else None
 
    def responder_diagnostico(self, politica, extras=False):
        """
        Responde as 16 perguntas. `politica(numero)` devolve o indice (0-3) da
        opcao. Com extras=True tambem testa: envio sem resposta, bloqueio de
        pular perguntas e o botao Voltar.
        Devolve (qtd_respondidas, pk_do_diagnostico).
        """
        respondidas = 0
        testou_vazio = testou_pulo = testou_voltar = False
 
        for _ in range(TOTAL_PERGUNTAS * 3):
            url = self.browser.current_url
            m_res = re.search(r"/guardiao/diagnostico/(\d+)/$", url)
            if m_res:
                return respondidas, int(m_res.group(1))
 
            numero = self._numero_pergunta()
            if numero is None:
                raise AssertionError(f"Saiu do questionario inesperadamente: {url}")
 
            radios = WebDriverWait(self.browser, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "input[name='resposta']")
                )
            )
            self.assertEqual(len(radios), 4, f"Pergunta {numero}: esperava 4 opcoes")
            form = radios[0].find_element(By.XPATH, "./ancestor::form")
            botao = form.find_element(By.CSS_SELECTOR, "button[type='submit']")
 
            # --- Extra 1: enviar sem escolher nada (pergunta 1)
            if extras and numero == 1 and not testou_vazio:
                testou_vazio = True
                self.clicar_e_esperar_troca(botao)
                self.assert_texto("Escolha uma das opções para continuar.")
                continue
 
            # --- Extra 2: tentar pular para a pergunta 10 (pergunta 2)
            if extras and numero == 2 and not testou_pulo:
                testou_pulo = True
                self.ir(f"/guardiao/diagnostico/pergunta/{TOTAL_PERGUNTAS}/", pausa=1.0)
                self.assertEqual(
                    self._numero_pergunta(), 2,
                    "Deveria ser redirecionado para a primeira pergunta pendente",
                )
                continue
 
            # --- Extra 3: botao Voltar (pergunta 3)
            if extras and numero == 3 and not testou_voltar:
                testou_voltar = True
                voltar = self.esperar("a.g-voltar")
                self.clicar(voltar, pausa=1.0)
                self.esperar_url("/pergunta/2/")
                self.assertTrue(
                    self.existe("input[name='resposta']:checked"),
                    "A resposta da pergunta 2 deveria continuar marcada",
                )
                # reenvia (sem contar como nova resposta) e volta para a 3
                novo = self.esperar("form.quiz-conteudo button[type='submit']")
                self.clicar_e_esperar_troca(novo)
                self.esperar_url("/pergunta/3/")
                continue
 
            # --- Resposta normal
            escolha = politica(numero)
            self.clicar(radios[escolha], pausa=0.6)
            self.assertTrue(radios[escolha].is_selected())
            self.clicar_e_esperar_troca(botao, pausa=0.8)
            respondidas += 1
            print(f"      pergunta {numero}/{TOTAL_PERGUNTAS} respondida (opcao {escolha})")
 
        raise AssertionError("Questionario nao terminou no limite de rodadas")
 
    def etapa_diagnostico_1(self):
        self.ir("/guardiao/boas-vindas/")
        self.clicar_e_esperar_troca(
            self.esperar("form[action*='iniciar'] button[type='submit']")
        )
        self.esperar_url("/pergunta/1/")
 
        # Respostas baixas (0 ou 1) para gerar varias missoes no plano de acao
        respondidas, pk = self.responder_diagnostico(
            politica=lambda n: n % 2, extras=True
        )
        self.assertEqual(respondidas, TOTAL_PERGUNTAS, "Nem todas as perguntas foram respondidas")
        self.diag_pk = pk
 
        from guardiao.models import Diagnostico, MissaoPlano
 
        self.assertEqual(Diagnostico.objects.filter(usuario__email=EMAIL).count(), 1)
        self.assertGreaterEqual(MissaoPlano.objects.filter(diagnostico_id=pk).count(), 1)
        self.assert_texto("Seu diagnóstico está pronto!")
 
    def etapa_resultado_detalhado(self):
        pk = self.exigir_pk()
        self.ir(f"/guardiao/diagnostico/{pk}/")
        self.assert_texto("Seu diagnóstico está pronto!")
        self.assertTrue(self.existe("a[href*='/detalhes/']"))
 
        # atalho "Ver ultimo resultado" da tela inicial
        self.ir("/guardiao/diagnostico/ultimo/", pausa=0.5)
        self.assertIn(f"/guardiao/diagnostico/{pk}/", self.browser.current_url)
 
        # Resultado detalhado por pilar
        self.clicar(self.esperar_xpath("//a[contains(., 'Ver resultados detalhados')]"), pausa=1.5)
        self.esperar_url("/detalhes/")
        self.assert_texto("Resultado por pilar")
        pilares = self.todos("details.det-pilar")
        self.assertEqual(len(pilares), 3, "Esperava 3 pilares (Ambiental, Social, Governança)")
        for nome in ("Ambiental", "Social", "Governança"):
            self.assert_html(nome)
        for resumo in self.todos("details.det-pilar summary"):
            self.clicar(resumo, pausa=0.7)   # alterna
            self.clicar(resumo, pausa=0.7)   # alterna de volta
 
        # Voltar
        self.clicar(self.esperar("a.g-voltar"), pausa=1.0)
        self.assertTrue(re.search(rf"/guardiao/diagnostico/{pk}/$", self.browser.current_url))
 
    def exigir_pk(self):
        if not self.diag_pk:
            raise AssertionError(
                "Nao ha diagnostico concluido (a etapa do diagnostico falhou antes)"
            )
        return self.diag_pk
 
    # ==================================================================
    # 7. PLANO DE ACAO E MISSOES
    # ==================================================================
    def _botao_missao(self, indice, classe):
        acoes = self.todos(".missao-acoes")[indice]
        return acoes.find_element(By.CSS_SELECTOR, f"button.{classe}")
 
    def etapa_plano_acao(self):
        pk = self.exigir_pk()
        self.ir(f"/guardiao/diagnostico/{pk}/plano/")
        self.assert_texto("Plano de ação")
        total = len(self.todos(".missao-acoes"))
        self.assertGreaterEqual(total, 1, "O plano de acao deveria ter missoes")
        print(f"      {total} missao(oes) no plano")
 
        # Destacar a primeira missao
        antes = self._botao_missao(0, "destaque")
        self.assertEqual(antes.get_attribute("aria-pressed"), "false")
        self.clicar_e_esperar_troca(antes)
        self.assertEqual(self._botao_missao(0, "destaque").get_attribute("aria-pressed"), "true")
 
        # Concluir a primeira missao
        antes = self._botao_missao(0, "concluir")
        self.assertEqual(antes.get_attribute("aria-pressed"), "false")
        self.clicar_e_esperar_troca(antes)
        self.assertEqual(self._botao_missao(0, "concluir").get_attribute("aria-pressed"), "true")
 
        # Se houver mais de uma missao, conclui a ultima tambem
        if total > 1:
            ultimo = total - 1
            self.clicar_e_esperar_troca(self._botao_missao(ultimo, "concluir"))
            self.assertEqual(
                self._botao_missao(ultimo, "concluir").get_attribute("aria-pressed"), "true"
            )
 
        # Atalho "Voltar" ao resultado e navegacao pelo botao do resultado
        self.clicar(self.esperar("a.g-voltar"), pausa=1.0)
        self.clicar(self.esperar_xpath("//a[contains(., 'Ver plano de ação')]"), pausa=1.0)
        self.esperar_url("/plano/")
 
    def etapa_missoes(self):
        pk = self.exigir_pk()
        self.ir(f"/guardiao/diagnostico/{pk}/plano/")
        links = [
            a.get_attribute("href")
            for a in self.todos(".missao-acoes a.g-botao")
        ]
        self.assertTrue(links, "Nenhum link 'Ver missao' encontrado")
 
        for i, href in enumerate(links, start=1):
            self.browser.get(href)
            self.passo_lento(0.8)
            for secao in ("Como fazer", "Benefício", "Tempo e custo"):
                self.assert_texto(secao, f"Missao {i}: faltou a secao {secao!r}")
 
        # Na primeira missao: alterna concluida e destaque pela pagina de detalhe
        self.browser.get(links[0])
        self.passo_lento(0.5)
        url_missao = self.browser.current_url
 
        botoes = self.todos(".det-missao-acoes form button")
        self.assertEqual(len(botoes), 2)
        texto_antes = botoes[0].text
        self.clicar_e_esperar_troca(botoes[0])
        self.assertEqual(self.browser.current_url, url_missao, "Deveria continuar na missao")
        self.assertNotEqual(
            self.todos(".det-missao-acoes form button")[0].text, texto_antes,
            "O botao 'concluida' deveria mudar de estado",
        )
 
        texto_antes = self.todos(".det-missao-acoes form button")[1].text
        self.clicar_e_esperar_troca(self.todos(".det-missao-acoes form button")[1])
        self.assertNotEqual(
            self.todos(".det-missao-acoes form button")[1].text, texto_antes,
            "O botao 'destacar' deveria mudar de estado",
        )
 
        # Voltar ao plano
        self.clicar(self.esperar_xpath("//a[contains(., 'Voltar ao plano de ação')]"), pausa=1.0)
        self.esperar_url_igual(f"/guardiao/diagnostico/{pk}/plano/")
        self.assert_texto("Plano de ação")
 
        # Missao inexistente -> 404
        self.ir(f"/guardiao/diagnostico/{pk}/plano/missao-que-nao-existe/", pausa=0.5)
        self.assertTrue(
            "404" in self.browser.title or "Not Found" in self.corpo() or "não encontrada" in self.corpo().lower()
            or "404" in self.corpo(),
            "Missao inexistente deveria dar 404",
        )
 
    # ==================================================================
    # 8. GASTOS
    # ==================================================================
    
    def etapa_painel_cozinha(self):
        self.ir("/gastos/painel/")
        self.assert_texto("Painel da cozinha")
 
        # Periodos
        for rotulo, parametro in [("Semana", "semana"), ("Mês", "mes"), ("Hoje", "hoje")]:
            link = self.esperar_xpath(f"//nav[@aria-label='Período']//a[normalize-space()='{rotulo}']")
            self.clicar(link, pausa=1.0)
            self.esperar_url(f"periodo={parametro}")
            self.assertTrue(
                self.existe(".p-abas a.ativa"), "Nenhuma aba de periodo marcada como ativa"
            )
 
        # Abas do grafico
        self.assertTrue(self.existe("#grafico-canvas"), "Canvas do grafico ausente")
        for rotulo, chave in [("Energia", "energia"), ("Desperdício", "desperdicio"), ("Água", "agua")]:
            link = self.esperar_xpath(f"//div[@id='grafico']//a[normalize-space()='{rotulo}']")
            self.clicar(link, pausa=1.0)
            self.esperar_url(f"grafico={chave}")
 
        # Atalho "Registrar agora"
        self.clicar(self.esperar_xpath("//a[contains(., 'Registrar agora')]"), pausa=1.0)
        self.esperar_url("/gastos/registrar/")
        self.assert_texto("Registrar e equipe")
 
    def etapa_registrar_consumo(self):
        from gastos.models import Registro, Sugestao
 
        self.ir("/gastos/registrar/")
        hoje = datetime.date.today().isoformat()
 
        # Quantidade invalida (zero) -> erro
        self.selecionar(self.esperar("#id_tipo"), valor="agua")
        self.digitar(self.esperar("#id_quantidade"), "0")
        self.definir_valor(self.esperar("#id_data"), hoje)
        self.enviar(self.esperar_xpath("//button[contains(., 'Salvar registro')]"), pausa=1.5)
        self.assert_texto("A quantidade precisa ser maior que zero.")
 
        # Um registro valido de cada tipo
        for tipo, qtd in [("agua", "120"), ("energia", "35"), ("desperdicio", "4"), ("doacao", "6")]:
            self.selecionar(self.esperar("#id_tipo"), valor=tipo)
            self.digitar(self.esperar("#id_quantidade"), qtd)
            self.definir_valor(self.esperar("#id_data"), hoje)
            self.digitar(self.esperar("#id_observacao"), f"Registro E2E {tipo}")
            self.enviar(self.esperar_xpath("//button[contains(., 'Salvar registro')]"), pausa=1.2)
            self.assert_texto("Registro salvo com sucesso!")
            self.assertTrue(
                Registro.objects.filter(tipo=tipo, usuario__email=EMAIL).exists(),
                f"Registro de {tipo} nao foi salvo",
            )
 
        # Mural da equipe: sugestao e apoio
        self.digitar(self.esperar("#id_texto"), "Descongelar alimentos na geladeira E2E")
        self.enviar(self.esperar_xpath("//form[contains(@action,'sugestao/nova')]//button"), pausa=1.5)
        self.assert_texto("Sugestão enviada!")
        self.assert_texto("Descongelar alimentos na geladeira E2E")
        self.assertTrue(Sugestao.objects.filter(texto__contains="E2E").exists())
 
        botao_apoio = self.esperar_xpath("//button[contains(., 'Apoiar (0)')]")
        self.clicar_e_esperar_troca(botao_apoio, pausa=1.2)
        self.assert_texto("Apoiar (1)")
 
        # Microtreinamentos e link de volta
        self.assert_texto("Microtreinamentos")
        self.clicar(self.esperar_xpath("//a[contains(., 'Voltar ao painel da cozinha')]"), pausa=1.0)
        self.esperar_url("/gastos/painel/")
 
    # ==================================================================
    # 9. FORNECEDORES / MAPA ESG
    # ==================================================================
    def etapa_mapa(self):
        self.ir("/guardiao/fornecedores/")
        self.assert_texto("Fornecedores de insumos e pontos de doação")
        self.assertTrue(self.existe("#mapa"))
 
        # Busca vazia
        self.clicar(self.esperar("#botao-buscar"), pausa=1.0)
        self.wait.until(
            lambda d: "Digite uma cidade" in d.find_element(By.ID, "contador").text
        )
 
        # Filtros: abre o painel e liga/desliga checkboxes
        self.clicar(self.esperar("#botao-filtros"), pausa=1.0)
        self.assertEqual(self.esperar("#botao-filtros").get_attribute("aria-expanded"), "true")
        self.assertTrue(self.esperar("#painel-filtros", visivel=False).get_attribute("class").find("aberto") >= 0)
        for chk in ("chk-igreja", "chk-banco", "chk-social", "chk-comunitario", "chk-doacao", "chk-fornecedor", "chk-parceiro"):
            self.clicar(self.esperar(f"#{chk}", visivel=False), pausa=0.3)
        # restaura o estado inicial dos filtros
        for chk in ("chk-igreja", "chk-banco", "chk-social", "chk-comunitario", "chk-doacao", "chk-fornecedor", "chk-parceiro"):
            self.clicar(self.esperar(f"#{chk}", visivel=False), pausa=0.2)
        self.clicar(self.esperar("#botao-filtros"), pausa=0.8)
 
        # Busca real
        self.digitar(self.esperar("#campo-busca"), "Boa Viagem, Recife")
        self.digitar(self.esperar("#campo-insumo"), "ovos")
        self.selecionar(self.esperar("#campo-raio"), valor="5000")
        self.clicar(self.esperar("#botao-buscar"), pausa=0.5)
 
        ignorar = ("Buscando...", "Digite um local", "Digite uma cidade")
        try:
            WebDriverWait(self.browser, 90).until(
                lambda d: not any(
                    t in d.find_element(By.ID, "contador").text for t in ignorar
                )
                and d.find_element(By.ID, "contador").text.strip() != ""
            )
        except TimeoutException:
            raise AssertionError("A busca do mapa nunca terminou (contador ficou parado)")
 
        resultado = self.esperar("#contador").text
        print(f"      Mapa respondeu: {resultado!r}")
        if any(p in resultado.lower() for p in ("configure", "erro", "indispon", "não foi possível", "falha", "tempo")):
            print(
                "      AVISO: a consulta externa (Overpass/internet) falhou; a interface do "
                "mapa funcionou, mas nao foi possivel validar os resultados."
            )
        self.passo_lento(2)
 
        if not self.existe(".leaflet-container"):
            print("      AVISO: Leaflet (CDN) nao carregou - verifique a conexao com a internet.")
 
        # APIs JSON
        self.ir("/guardiao/fornecedores/api/empresas/", pausa=0.5)
        self.assert_html("empresas")
        self.ir("/guardiao/fornecedores/api/parceiros/", pausa=0.5)
        self.assert_html("parceiros")
 
    # ==================================================================
    # 10. PASSAPORTE DE SABORES
    # ==================================================================
    def _mensagem_passaporte(self):
        return self.esperar(".passaporte-mensagem").text
 
    def etapa_passaporte(self):
        from guardiao.models import Passaporte
 
        self.ir("/guardiao/passaporte/editar/")
        self.assert_texto("Salvar Passaporte")
 
        # (a) Sem passaporte ainda: nao ha secao de ingredientes
        self.assertFalse(self.existe("#ingrediente_nome"), "Ingrediente nao deveria aparecer antes do passaporte")
 
        # (b) Envio vazio -> erro do servidor
        self.digitar(self.esperar("#nome_restaurante"), "")
        self.digitar(self.esperar("#historia"), "")
        self.enviar(self.esperar_xpath("//button[contains(., 'Salvar Passaporte')]"), pausa=1.5)
        self.assertIn("Preencha o nome e a história do restaurante.", self._mensagem_passaporte())
 
        # (c) Cadastro valido
        self.digitar(self.esperar("#nome_restaurante"), NOME_RESTAURANTE)
        self.digitar(
            self.esperar("#historia"),
            "História focada no desenvolvimento sustentável e apoio local.",
        )
        self.digitar(self.esperar("#impacto_comunitario"), "Doamos o excedente toda sexta-feira.")
        self.digitar(self.esperar("#programa_fidelidade"), "A cada 10 refeicoes, uma sobremesa gratis.")
        self.selecionar(self.esperar("#ativo"), valor="ativo")
        self.enviar(self.esperar_xpath("//button[contains(., 'Salvar Passaporte')]"), pausa=1.5)
        self.assertIn("Passaporte salvo com sucesso!", self._mensagem_passaporte())
 
        passaporte = Passaporte.objects.get(proprietario__email=EMAIL)
        self.assertEqual(passaporte.nome_restaurante, NOME_RESTAURANTE)
        self.assertEqual(passaporte.slug, SLUG_RESTAURANTE)
        self.assertTrue(passaporte.ativo)
 
        # (d) Painel + QR Code carregado de verdade
        self.assert_texto("Painel do restaurante")
        self.assert_texto("Ativo")
        qr = self.esperar("img[alt='QR Code do Passaporte de Sabores']")
        self.wait.until(
            lambda d: d.execute_script(
                "return arguments[0].complete && arguments[0].naturalWidth > 0;", qr
            )
        )
 
        # (e) Endpoint do QR Code devolve uma imagem PNG
        self.ir("/guardiao/passaporte/qrcode/", pausa=1.0)
        tipo = self.browser.execute_script("return document.contentType;")
        self.assertEqual(tipo, "image/png", "O QR Code deveria ser um PNG")
 
        # (f) Pagina publica (link "Visualizar pagina publica")
        self.ir("/guardiao/passaporte/editar/")
        link = self.esperar_xpath("//a[contains(., 'Visualizar página pública')]")
        href = link.get_attribute("href")
        self.assertIn(SLUG_RESTAURANTE, href)
        self.browser.get(href)
        self.passo_lento(1.5)
        self.assert_texto(NOME_RESTAURANTE)
        self.assert_texto("História do restaurante")
 
    def etapa_passaporte_ingredientes(self):
        from guardiao.models import Passaporte
 
        self.ir("/guardiao/passaporte/editar/")
        self.assert_texto("Nenhum ingrediente cadastrado ainda.")
 
        # Validacao: falta origem e fornecedor
        self.digitar(self.esperar("#ingrediente_nome"), "Tomate Orgânico")
        self.enviar(self.esperar_xpath("//button[contains(., 'Adicionar ingrediente')]"), pausa=1.5)
        self.assertIn(
            "Preencha o nome, a origem e o fornecedor do ingrediente.",
            self._mensagem_passaporte(),
        )
 
        # Ingredientes validos
        ingredientes = [
            ("Tomate Orgânico", "Horta Local Recife", "Produtor João da Silva"),
            ("Alface Crespa", "Sítio Verde - Vitória de Santo Antão", "Cooperativa Raízes"),
        ]
        for nome, origem, fornecedor in ingredientes:
            self.digitar(self.esperar("#ingrediente_nome"), nome)
            self.digitar(self.esperar("#ingrediente_origem"), origem)
            self.digitar(self.esperar("#ingrediente_fornecedor"), fornecedor)
            self.digitar(self.esperar("#ingrediente_descricao"), f"Descricao de {nome}")
            self.enviar(self.esperar_xpath("//button[contains(., 'Adicionar ingrediente')]"), pausa=1.5)
            self.assertIn("Ingrediente cadastrado com sucesso!", self._mensagem_passaporte())
            self.assert_texto(nome)
 
        passaporte = Passaporte.objects.get(proprietario__email=EMAIL)
        self.assertEqual(passaporte.ingredientes.count(), 2)
 
        def cartao(nome):
            return self.esperar_xpath(
                "//div[contains(@class,'passaporte-ingrediente')]"
                f"[.//h3[normalize-space()='{nome}']]"
            )
 
        # Editar o "Tomate Organico"
        card = cartao("Tomate Orgânico")
        self.clicar(card.find_element(By.CSS_SELECTOR, "details summary"), pausa=1.0)
        detalhes = card.find_element(By.CSS_SELECTOR, "details")
        self.digitar(detalhes.find_element(By.CSS_SELECTOR, "input[name='nome']"), "Tomate Cereja Orgânico")
        self.enviar(detalhes.find_element(By.CSS_SELECTOR, "button[type='submit']"), pausa=1.5)
        self.assertIn("Ingrediente atualizado com sucesso!", self._mensagem_passaporte())
        self.assert_texto("Tomate Cereja Orgânico")
 
        # Excluir a "Alface Crespa" (o confirm() e aceito automaticamente)
        card = cartao("Alface Crespa")
        excluir = card.find_element(By.XPATH, ".//form[contains(@action,'excluir')]//button")
        self.clicar_e_esperar_troca(excluir, pausa=1.5)
        self.assertIn("Ingrediente excluído com sucesso!", self._mensagem_passaporte())
        self.assertEqual(passaporte.ingredientes.count(), 1)
        self.assertNotIn("alface crespa", self.corpo().lower())
 
        # A pagina publica mostra o ingrediente e o fornecedor restantes
        self.ir(f"/guardiao/passaporte/{SLUG_RESTAURANTE}/")
        self.assert_texto("Tomate Cereja Orgânico")
        self.assert_texto("Produtor João da Silva")
        self.assert_texto("Fornecedores parceiros")
 
    def etapa_passaporte_status(self):
        # Desativa -> some o QR Code e a pagina publica fica indisponivel
        self.ir("/guardiao/passaporte/editar/")
        self.selecionar(self.esperar("#ativo"), valor="inativo")
        self.enviar(self.esperar_xpath("//button[contains(., 'Salvar Passaporte')]"), pausa=1.5)
        self.assertIn("Passaporte salvo com sucesso!", self._mensagem_passaporte())
        self.assertFalse(self.existe("img[alt='QR Code do Passaporte de Sabores']"))
        self.assert_texto("Inativo")
 
        self.ir(f"/guardiao/passaporte/{SLUG_RESTAURANTE}/")
        self.assert_texto("Passaporte não disponível")
 
        # Reativa
        self.ir("/guardiao/passaporte/editar/")
        self.selecionar(self.esperar("#ativo"), valor="ativo")
        self.enviar(self.esperar_xpath("//button[contains(., 'Salvar Passaporte')]"), pausa=1.5)
        self.assertTrue(self.existe("img[alt='QR Code do Passaporte de Sabores']"))
        self.ir(f"/guardiao/passaporte/{SLUG_RESTAURANTE}/")
        self.assert_texto(NOME_RESTAURANTE)
 
        # Slug inexistente -> 404
        self.ir("/guardiao/passaporte/restaurante-que-nao-existe/", pausa=0.5)
        self.assertTrue(
            "404" in self.corpo() or "Not Found" in self.corpo() or "404" in self.browser.title
        )
 
    # ==================================================================
    # 11. LOGOUT / PAGINA PUBLICA ANONIMA / NOVO LOGIN
    # ==================================================================
    def etapa_logout(self):
        self._sair_pelo_menu_guardiao()
        # Volta para a home e o menu mostra "Acessar" (nao mais "Minha conta")
        self.esperar("a.nav-acessar")  # falha (timeout) se nao deslogou
        self.assertFalse(self.existe("a.nav-conta"))
        # Rota protegida volta a pedir login
        self.ir("/guardiao/boas-vindas/", pausa=0.5)
        self.assertIn("/acesso/?next=", self.browser.current_url)
 
    def etapa_passaporte_publico_anonimo(self):
        self.ir(f"/guardiao/passaporte/{SLUG_RESTAURANTE}/")
        self.assertNotIn("/acesso/", self.browser.current_url)
        self.assert_texto(NOME_RESTAURANTE)
        self.assert_texto("Tomate Cereja Orgânico")
 
    def etapa_relogin(self):
        # Senha antiga nao funciona mais
        self._login_pela_interface(EMAIL, SENHA)
        self.assert_texto("E-mail ou senha inválidos.")
        # Senha nova funciona e respeita o ?next=
        self.ir("/gastos/painel/", pausa=0.3)  # anonimo -> /acesso/?next=/gastos/painel/
        self.assertIn("next=/gastos/painel/", self.browser.current_url)
        form = self.esperar("form[data-form='login']")
        self.digitar(form.find_element(By.ID, "login-email"), EMAIL.upper())  # case-insensitive
        self.digitar(form.find_element(By.ID, "login-senha"), self.senha_atual)
        self.clicar(form.find_element(By.CSS_SELECTOR, "button[type='submit']"), pausa=0.5)
        self.esperar_url_sem("/acesso/")
        self.esperar_url_igual("/gastos/painel/")
        self.assert_texto("Painel da cozinha")
 
    # ==================================================================
    # 12. SEGUNDO DIAGNOSTICO + EVOLUCAO
    # ==================================================================
    def etapa_diagnostico_2(self):
        from guardiao.models import Diagnostico
 
        self.ir("/guardiao/boas-vindas/")
        self.assert_texto("Refazer diagnóstico")      # agora ja existe um resultado
        self.assert_texto("Ver último resultado")
        self.clicar_e_esperar_troca(
            self.esperar("form[action*='iniciar'] button[type='submit']")
        )
        self.esperar_url("/pergunta/1/")
 
        # Todas as respostas maximas (3) -> nota 100 e plano sem missoes
        respondidas, pk = self.responder_diagnostico(politica=lambda n: 3)
        self.assertEqual(respondidas, TOTAL_PERGUNTAS)
        self.assertNotEqual(pk, self.diag_pk)
        self.assertEqual(Diagnostico.objects.filter(usuario__email=EMAIL).count(), 2)
 
        self.assert_texto("Seu diagnóstico está pronto!")
        self.assert_texto("pontos")                   # "Desde dd/mm/aaaa: +N pontos"
        self.assert_texto("Desde")
 
        self.ir(f"/guardiao/diagnostico/{pk}/plano/")
        self.assert_texto("Parabéns!")
 
        # Diagnostico antigo continua acessivel
        self.ir(f"/guardiao/diagnostico/{self.diag_pk}/")
        self.assert_texto("Seu diagnóstico está pronto!")
 
        # O diagnostico de outro usuario nao pode ser acessado (404)
        self.ir("/guardiao/diagnostico/999999/", pausa=0.5)
        self.assertTrue("404" in self.corpo() or "Not Found" in self.corpo() or "404" in self.browser.title)
 
    def etapa_logout_minha_conta(self):
        self.ir("/minha-conta/")
        botao = self.esperar_xpath("//button[contains(., 'Sair da conta')]")
        self.clicar(botao, pausa=1.5)
        self.esperar("a.nav-acessar")
        self.ir("/minha-conta/", pausa=0.5)
        self.assertIn("/acesso/?next=", self.browser.current_url)
 
    # ==================================================================
    # TESTE PRINCIPAL
    # ==================================================================
    def test_fluxo_completo_sistema(self):
        print("\n========== [1/12] Paginas publicas e contato ==========")
        self.tentar("paginas_publicas", self.etapa_paginas_publicas, exige_login=False)
        self.tentar("menu_publico", self.etapa_menu_publico, exige_login=False)
        self.tentar("contato", self.etapa_contato, exige_login=False)
 
        print("\n========== [2/12] Protecao de rotas e login invalido ==========")
        self.tentar("protecao_anonima", self.etapa_protecao_anonima, exige_login=False)
        self.tentar("login_invalido", self.etapa_login_invalido, exige_login=False)
 
        print("\n========== [3/12] Cadastro ==========")
        self.tentar("cadastro", self.etapa_cadastro)
        if "cadastro" in self.falhas:
            self.fail(
                "O cadastro/login falhou - as demais etapas dependem de um usuario "
                "logado. Veja o screenshot em debug_e2e/."
            )
 
        print("\n========== [4/12] Minha conta ==========")
        self.tentar("minha_conta", self.etapa_minha_conta)
 
        print("\n========== [5/12] Guardiao: boas-vindas e menu ==========")
        self.tentar("boas_vindas", self.etapa_boas_vindas)
 
        print("\n========== [6/12] Diagnostico ESG completo ==========")
        self.tentar("diagnostico_1", self.etapa_diagnostico_1)
        self.tentar("resultado_detalhado", self.etapa_resultado_detalhado)
 
        print("\n========== [7/12] Plano de acao e missoes ==========")
        self.tentar("plano_acao", self.etapa_plano_acao)
        self.tentar("missoes", self.etapa_missoes)
 
        print("\n========== [8/12] Gastos / painel da cozinha ==========")
        self.tentar("painel_cozinha", self.etapa_painel_cozinha)
        self.tentar("registrar_consumo", self.etapa_registrar_consumo)
 
        print("\n========== [9/12] Fornecedores / Mapa ESG ==========")
        self.tentar("mapa", self.etapa_mapa)
 
        print("\n========== [10/12] Passaporte de Sabores e QR Code ==========")
        self.tentar("passaporte", self.etapa_passaporte)
        self.tentar("passaporte_ingredientes", self.etapa_passaporte_ingredientes)
        self.tentar("passaporte_status", self.etapa_passaporte_status)
 
        print("\n========== [11/12] Logout e novo login ==========")
        self.tentar("logout", self.etapa_logout, exige_login=False)
        self.tentar("passaporte_publico_anonimo", self.etapa_passaporte_publico_anonimo, exige_login=False)
        self.tentar("relogin", self.etapa_relogin)
 
        print("\n========== [12/12] Segundo diagnostico e evolucao ==========")
        self.tentar("diagnostico_2", self.etapa_diagnostico_2)
        self.tentar("logout_minha_conta", self.etapa_logout_minha_conta, exige_login=False)
 
        print("\n==================================================")
        if self.falhas:
            print(f" ETAPAS COM FALHA: {', '.join(self.falhas)}")
            print(f" Screenshots em: ./{PASTA_DEBUG}/")
        else:
            print(" TODOS OS FLUXOS FORAM TESTADOS COM SUCESSO! ")
        print("==================================================")
 
        self.assertEqual(
            self.falhas, [], f"Etapas com falha: {', '.join(self.falhas)}"
        )
