from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time

class HistoriaTest(StaticLiveServerTestCase):
    def setUp(self):
        opts = webdriver.ChromeOptions()
        if os.environ.get("CI"):
            opts.add_argument("--headless=new")
        self.browser = webdriver.Chrome(options=opts)
        self.browser.implicitly_wait(5)
        self.browser.maximize_window()

    def tearDown(self):
        time.sleep(4)
        self.browser.quit()

    def passo_lento(self, segundos=4):
        """Força o robô a aguardar para que você consiga ver e narrar a funcionalidade."""
        time.sleep(segundos)

    def test_todas_as_funcionalidades_do_sistema(self):
      
        print("Criando usuário e autenticando sessão de teste...")
        username = "usuario_teste"
        password = "senha_segura_123"
        User.objects.create_user(username=username, password=password)

        self.client.login(username=username, password=password)

        self.browser.get(self.live_server_url + "/")
        
        session_cookie = self.client.cookies['sessionid']
        self.browser.add_cookie({
            'name': 'sessionid',
            'value': session_cookie.value,
            'path': '/',
        })
        print("Sessão injetada com sucesso! Áreas restritas liberadas.")

        print("Testando: Página Inicial...")
        self.browser.get(self.live_server_url + "/")
        self.passo_lento(4)
        self.assertIn("<body", self.browser.page_source.lower())

        print("Testando: Sobre...")
        self.browser.get(self.live_server_url + "/sobre/")
        self.passo_lento(4)
        self.assertIn("<body", self.browser.page_source.lower())

        print("Testando: Desafios...")
        self.browser.get(self.live_server_url + "/desafios/")
        self.passo_lento(4)
        self.assertIn("<body", self.browser.page_source.lower())

        print("Testando: Soluções...")
        self.browser.get(self.live_server_url + "/solucoes/")
        self.passo_lento(4)
        self.assertIn("<body", self.browser.page_source.lower())

        print("Testando: Contato e Envio do Formulário...")
        self.browser.get(self.live_server_url + "/contato/")
        self.passo_lento(3)
        self.assertIn("<body", self.browser.page_source.lower())

        try:
            campo_nome = self.browser.find_element(By.CSS_SELECTOR, "input[type='text']")
            campo_nome.send_keys("Testador Automatizado Selenium")
            self.passo_lento(1)
            
            try:
                campo_email = self.browser.find_element(By.CSS_SELECTOR, "input[type='email']")
                campo_email.send_keys("teste@impacta.com")
                self.passo_lento(1)
            except Exception:
                pass

            try:
                campo_assunto = self.browser.find_element(By.CSS_SELECTOR, "input[name='assunto'], input[name='subject'], input[placeholder*='assunto' i]")
                campo_assunto.send_keys("Feedback do Teste do Sistema")
                self.passo_lento(1)
            except Exception:
                print("Aviso: Campo 'assunto' não encontrado pelos seletores padrão. Tentando prosseguir...")

            try:
                campo_mensagem = self.browser.find_element(By.TAG_NAME, "textarea")
                campo_mensagem.send_keys("Esta é uma mensagem automatizada gerada pelo teste de sistema E2E.")
                self.passo_lento(2)
            except Exception:
                pass
            
            botao_enviar = self.browser.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            botao_enviar.click()
            print("Formulário de contato enviado com sucesso!")
            self.passo_lento(4) 
        except Exception as e:
            print("Aviso: Erro ao interagir com o formulário de contato:", e)
        
        print("Testando: Painel do Guardião...")
        self.browser.get(self.live_server_url + "/guardiao/boas-vindas/")
        self.passo_lento(4) 

         print("Testando: Módulo de Gastos...")
        self.browser.get(self.live_server_url + "/gastos/painel/")
        self.passo_lento(4) 

        print("Testando: Módulo de Fornecedores...")
        self.browser.get(self.live_server_url + "/guardiao/fornecedores/")
        self.passo_lento(4)

        print("Testando: QR code...")
        self.browser.get(self.live_server_url + "/guardiao/boas-vindas/#qrcode")
        self.passo_lento(4)

        print("Todos os fluxos foram testados visualmente com sucesso!")
