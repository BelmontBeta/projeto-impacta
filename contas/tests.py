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
            "/gastos/",
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
 
            
