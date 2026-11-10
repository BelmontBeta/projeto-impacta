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
from selenium.webdriver.support.ui import WebDriverWait

User = get_user_model()

PASTA_DEBUG = "debug_e2e"


@unittest.skipUnless(
    os.environ.get("RODAR_SELENIUM"),
    "defina RODAR_SELENIUM=1 para rodar os testes do Chrome",
)
class SistemaCompletoE2ETest(StaticLiveServerTestCase):
    # ------------------------------------------------------------------
    # SETUP / TEARDOWN
    # ------------------------------------------------------------------
    def setUp(self):
        opts = webdriver.ChromeOptions()
        if os.environ.get("HEADLESS"):
            opts.add_argument("--headless=new")

        self.browser = webdriver.Chrome(options=opts)
        self.browser.implicitly_wait(0)
        self.browser.maximize_window()
        self.wait = WebDriverWait(self.browser, 10)

        self.falhas = []
        self.email_teste = "gestor.restaurante@impacta.com"
        self.senha_teste = "SenhaSegura123!"
        os.makedirs(PASTA_DEBUG, exist_ok=True)

    def tearDown(self):
        try:
            time.sleep(1)
        finally:
            self.browser.quit()

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------
    def passo_lento(self, segundos=1):
        """Pausa para permitir acompanhamento visual da automacao."""
        time.sleep(segundos)

    def url(self, caminho):
        return self.live_server_url + caminho

    def esperar(self, css, timeout=10, visivel=True):
        """Espera um elemento por seletor CSS e o retorna."""
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

    def existe(self, css):
        return len(self.browser.find_elements(By.CSS_SELECTOR, css)) > 0

    def clicar(self, elemento):
        """Rola ate o elemento e clica via JS (evita 'not interactable')."""
        self.browser.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", elemento
        )
        self.browser.execute_script("arguments[0].click();", elemento)

    def preencher(self, elemento, valor):
        """Preenche um campo; se o Selenium nao conseguir digitar, usa JS."""
        self.browser.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", elemento
        )
        try:
            elemento.clear()
            elemento.send_keys(valor)
        except Exception:
            self.browser.execute_script(
                """
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                """,
                elemento,
                valor,
            )

    def screenshot(self, nome):
        try:
            slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", nome)[:60]
            self.browser.save_screenshot(os.path.join(PASTA_DEBUG, f"{slug}.png"))
        except Exception:
            pass

    def _garantir_autenticacao(self):
        """Verifica se a sessao caiu e reloga caso necessario antes de etapas privadas."""
        from django.conf import settings

        self.browser.get(self.url("/guardiao/boas-vindas/"))
        if "/acesso/" in self.browser.current_url:
            print("  [Sessao expirada] Restaurando autenticacao...")
            self.client.login(username=self.email_teste, password=self.senha_teste)
            nome_cookie = settings.SESSION_COOKIE_NAME
            cookie = self.client.cookies[nome_cookie]
            self.browser.add_cookie(
                {"name": nome_cookie, "value": cookie.value, "path": "/"}
            )
            self.browser.get(self.url("/guardiao/boas-vindas/"))

    def tentar(self, nome, funcao):
        """
        Executa uma etapa. Se a sessao cair, restaura automaticamente para
        etapas que exigem login.
        """
        etapas_sem_login = {"paginas_publicas", "contato", "logout"}
        try:
            if nome not in etapas_sem_login:
                self._garantir_autenticacao()

            funcao()

            if nome not in etapas_sem_login:
                self.assertNotIn(
                    "/acesso/",
                    self.browser.current_url,
                    "Redirecionado para a tela de login: sessao nao autenticada",
                )
        except Exception as e:
            primeira_linha = (str(e).strip().splitlines() or [""])[0]
            print(
                f"  [FALHA] {nome}: {e.__class__.__name__} {primeira_linha}\n"
                f"          URL: {self.browser.current_url}"
            )
            self.screenshot(f"falha_{nome}")
            self.falhas.append(nome)

    # ------------------------------------------------------------------
    # DIAGNOSTICO ESG
    # ------------------------------------------------------------------
    def responder_diagnostico(self, max_rodadas=40):
        """Responde todas as perguntas ate chegar na tela de resultado."""
        respondidas = 0

        for _ in range(max_rodadas):
            if "resultado" in self.browser.current_url.lower():
                print("  Tela de resultado final atingida!")
                return respondidas

            try:
                radios = WebDriverWait(self.browser, 5).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "input[type='radio']")
                    )
                )
            except TimeoutException:
                print(
                    f"  Sem radios. URL: {self.browser.current_url} | "
                    f"Titulo: {self.browser.title}"
                )
                self.screenshot(f"diagnostico_sem_radios_{respondidas}")

                # Tenta avancar telas intermediarias (feedback, transicao de pilar...)
                try:
                    prox = self.browser.find_element(
                        By.XPATH,
                        "//a[contains(.,'Continuar') or contains(.,'Pr\u00f3xima') or contains(.,'Avan\u00e7ar')]"
                        " | //button[contains(.,'Continuar') or contains(.,'Pr\u00f3xima') or contains(.,'Avan\u00e7ar')]",
                    )
                    self.clicar(prox)
                    self.passo_lento(1)
                    continue
                except Exception:
                    return respondidas

            radio = radios[0]

            try:
                escopo = radio.find_element(By.XPATH, "./ancestor::form")
            except Exception:
                escopo = self.browser

            self.clicar(radio)
            self.passo_lento(0.5)
            btn = escopo.find_element(
                By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"
            )
            self.clicar(btn)

            # Espera a pagina trocar antes da proxima rodada
            try:
                WebDriverWait(self.browser, 10).until(EC.staleness_of(radio))
            except TimeoutException:
                print(
                    "  A pagina nao mudou apos enviar a resposta "
                    f"(URL: {self.browser.current_url})."
                )
                self.screenshot(f"diagnostico_nao_avancou_{respondidas}")
                return respondidas

            respondidas += 1
            print(f"  -> Pergunta {respondidas} respondida!")
            self.passo_lento(0.5)

        return respondidas

    # ------------------------------------------------------------------
    # ETAPAS
    # ------------------------------------------------------------------
    def etapa_paginas_publicas(self):
        paginas = [
            ("/", "ESG aplicado ao ramo aliment\u00edcio"),
            ("/sobre/", "Sobre o projeto"),
            ("/desafios/", "Desafios do ramo aliment\u00edcio"),
            ("/solucoes/", "Solu\u00e7\u00f5es do nosso projeto"),
        ]
        for caminho, texto in paginas:
            self.browser.get(self.url(caminho))
            self.passo_lento(0.5)
            self.assertIn(texto, self.browser.page_source, f"Texto ausente em {caminho}")

    def etapa_contato(self):
        print("Testando formulario de Contato...")
        self.browser.get(self.url("/contato/"))

        nome = self.esperar("input[name='nome'], input[type='text']")
        self.preencher(nome, "Testador E2E Selenium")

        campos_opcionais = [
            ("input[name='email'], input[type='email']", "testador@impacta.com"),
            ("input[name='assunto'], input[name='subject']", "Teste de Contato E2E"),
            ("textarea", "Mensagem automatizada de teste do formulario de contato."),
        ]
        for css, valor in campos_opcionais:
            elementos = self.browser.find_elements(By.CSS_SELECTOR, css)
            if elementos:
                self.preencher(elementos[0], valor)

        btn = self.esperar("button[type='submit'], input[type='submit']")
        self.clicar(btn)
        self.passo_lento(2)
        print("  Formulario de contato enviado.")

    def _login_pela_interface(self, email, senha):
        """Plano B: faz login preenchendo o formulario real de /acesso/."""
        self.browser.get(self.url("/acesso/"))
        self.passo_lento(1)

        for form in self.browser.find_elements(By.TAG_NAME, "form"):
            senhas = form.find_elements(By.CSS_SELECTOR, "input[type='password']")
            if len(senhas) != 1:
                continue
            usuarios = form.find_elements(
                By.CSS_SELECTOR,
                "input[type='email'], input[name='email'], "
                "input[name='username'], input[type='text']",
            )
            if not usuarios:
                continue

            self.preencher(usuarios[0], email)
            self.preencher(senhas[0], senha)
            btn = form.find_element(
                By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"
            )
            self.clicar(btn)
            self.passo_lento(2)
            return

        self.fail("Nao encontrei o formulario de login em /acesso/")

    def etapa_login(self):
        from django.conf import settings

        User.objects.create_user(
            username=self.email_teste,
            email=self.email_teste,
            password=self.senha_teste,
            first_name="Gestor ESG",
        )

        self.assertTrue(
            self.client.login(username=self.email_teste, password=self.senha_teste),
            "Login via test client falhou",
        )
        self.browser.get(self.url("/"))
        self.browser.delete_all_cookies()
        nome_cookie = settings.SESSION_COOKIE_NAME
        cookie = self.client.cookies[nome_cookie]
        self.browser.add_cookie(
            {"name": nome_cookie, "value": cookie.value, "path": "/"}
        )

        self._garantir_autenticacao()
        print("  Sessao autenticada via cookie!")

    def etapa_perfil(self):
        print("Atualizando dados em Minha Conta...")
        self.browser.get(self.url("/minha-conta/"))

        campo = self.esperar(
            "input[name='first_name'], input[name='nome']", visivel=False
        )
        self.preencher(campo, "Gestor ESG Atualizado")

        btn = self.esperar("form button[type='submit']", visivel=False)
        self.clicar(btn)
        self.passo_lento(2)
        print("  Perfil atualizado!")

    def etapa_diagnostico(self):
        self.browser.get(self.url("/guardiao/boas-vindas/"))
        self.passo_lento(1)

        iniciar = self.browser.find_elements(
            By.CSS_SELECTOR,
            "form[action*='iniciar'] button, a[href*='iniciar'], button.btn-iniciar",
        )
        if iniciar:
            self.clicar(iniciar[0])
            self.passo_lento(1)

        print("Respondendo a TODAS as perguntas do Diagnostico ESG...")
        respondidas = self.responder_diagnostico()
        print(f"  Total de {respondidas} perguntas respondidas.")

        self.assertGreater(
            respondidas, 1, "Diagnostico parou na primeira pergunta"
        )
        self.assertIn(
            "resultado",
            self.browser.current_url.lower(),
            "Diagnostico nao chegou na tela de resultado",
        )

    def etapa_resultado_detalhado(self):
        print("Navegando para o Resultado Detalhado por Pilar...")
        link = self.esperar_xpath(
            "//a[contains(@href,'detalhad') or "
            "contains(translate(., 'DETALHAD', 'detalhad'), 'detalhad')]"
        )
        self.clicar(link)
        self.passo_lento(2)

        for summary in self.browser.find_elements(By.TAG_NAME, "summary"):
            self.clicar(summary)
            self.passo_lento(0.5)

    def etapa_plano_acao(self):
        link = self.esperar_xpath(
            "//a[contains(@href,'plano') or "
            "contains(translate(., 'PLANO', 'plano'), 'plano')]"
        )
        self.clicar(link)
        self.passo_lento(2)

        missoes = self.browser.find_elements(
            By.CSS_SELECTOR, ".missao-acoes a, a.btn-missao"
        )
        if not missoes:
            print("  Nenhuma missao listada no plano de acao.")
            return

        print("  Visualizando detalhes da primeira missao...")
        self.clicar(missoes[0])
        self.passo_lento(1)

        btn_concluir = self.esperar_xpath(
            "//button[contains(., 'Conclu\u00edd') or contains(., 'Marcar')]"
        )
        self.clicar(btn_concluir)
        self.passo_lento(2)
        print("  Status da missao alternado!")

    def etapa_gastos(self):
        self.browser.get(self.url("/gastos/painel/"))
        self.passo_lento(1)
        self.assertNotIn("/login", self.browser.current_url.lower())
        self.assertFalse(
            self.existe("body.error-page") or "Server Error" in self.browser.title,
            "Dashboard de gastos retornou erro",
        )
        print("  Dashboard de Gastos acessado!")

    def etapa_fornecedores(self):
        self.browser.get(self.url("/guardiao/fornecedores/"))

        campo = self.esperar("#campo-busca, input[name='busca'], input[type='search']")
        self.preencher(campo, "Recife")

        btn = self.esperar("#botao-buscar, button[type='submit']")
        self.clicar(btn)
        self.passo_lento(2)
        print("  Busca realizada no Mapa ESG.")

    def etapa_passaporte_info(self):
        self.browser.get(self.url("/guardiao/passaporte/editar/"))

        nome = self.esperar("#nome_restaurante, input[name='nome_restaurante']")
        self.preencher(nome, "Restaurante Organico E2E")

        historia = self.esperar("#historia, textarea[name='historia']")
        self.preencher(
            historia, "Historia focada no desenvolvimento sustentavel e apoio local."
        )

        btn = self.esperar_xpath(
            "//button[contains(., 'Salvar Passaporte') or contains(., 'Salvar')]"
        )
        self.clicar(btn)
        self.passo_lento(2)
        print("  Informacoes do Passaporte salvas!")

    def etapa_passaporte_ingrediente(self):
        print("Cadastrando ingrediente no Passaporte...")
        if "passaporte/editar" not in self.browser.current_url:
            self.browser.get(self.url("/guardiao/passaporte/editar/"))

        nome = self.esperar("#ingrediente_nome, input[name='nome']")
        origem = self.esperar("#ingrediente_origem, input[name='origem']")
        fornecedor = self.esperar("#ingrediente_fornecedor, input[name='fornecedor']")

        self.preencher(nome, "Tomate Organico")
        self.preencher(origem, "Horta Local Recife")
        self.preencher(fornecedor, "Produtor Joao da Silva")

        btn = self.esperar_xpath(
            "//button[contains(., 'Adicionar') or contains(., 'Cadastrar')]"
        )
        self.clicar(btn)
        self.passo_lento(2)
        print("  Ingrediente cadastrado!")

    def etapa_logout(self):
        print("Testando encerramento da sessao (Logout)...")
        self.browser.get(self.url("/guardiao/boas-vindas/"))

        menu = self.browser.find_elements(
            By.CSS_SELECTOR, "#botaoConta, .menu-usuario, a[href*='conta']"
        )
        if menu:
            self.clicar(menu[0])
            self.passo_lento(1)

        btn_sair = self.esperar(
            "form[action*='sair'] button, a[href*='sair'], "
            "form[action*='logout'] button, a[href*='logout']",
            visivel=False,
        )
        self.clicar(btn_sair)
        self.passo_lento(2)
        print("  Logout efetuado!")

    # ------------------------------------------------------------------
    # TESTE PRINCIPAL
    # ------------------------------------------------------------------
    def test_fluxo_completo_sistema(self):
        print("\n--- [1/7] Paginas Institucionais Publicas e Contato ---")
        self.tentar("paginas_publicas", self.etapa_paginas_publicas)
        self.tentar("contato", self.etapa_contato)

        print("\n--- [2/7] Autenticacao e Gestao de Perfil ---")
        self.etapa_login()
        self.tentar("perfil", self.etapa_perfil)

        print("\n--- [3/7] Diagnostico ESG completo ---")
        self.tentar("diagnostico", self.etapa_diagnostico)
        self.tentar("resultado_detalhado", self.etapa_resultado_detalhado)

        print("\n--- [4/7] Plano de Acao e Missoes ---")
        self.tentar("plano_acao", self.etapa_plano_acao)

        print("\n--- [5/7] Modulo de Gastos / Dashboard ---")
        self.tentar("gastos", self.etapa_gastos)

        print("\n--- [6/7] Fornecedores / Mapa ESG ---")
        self.tentar("fornecedores", self.etapa_fornecedores)

        print("\n--- [7/7] Passaporte de Sabores e QR Code ---")
        self.tentar("passaporte_info", self.etapa_passaporte_info)
        self.tentar("passaporte_ingrediente", self.etapa_passaporte_ingrediente)
        self.tentar("logout", self.etapa_logout)

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
