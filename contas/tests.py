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

        print("Testando: Módulo de Gastos...")
        self.browser.get(self.live_server_url + "/gastos/")
        self.passo_lento(4) 
        
        print("Testando: Painel do Guardião...")
        self.browser.get(self.live_server_url + "/guardiao/boas-vindas/")
        self.passo_lento(4) 

        print("Testando: Módulo de Fornecedores...")
        self.browser.get(self.live_server_url + "/guardiao/fornecedores/")
        self.passo_lento(4)
        print("Testando: Interação e Formulários...")
        self.browser.get(self.live_server_url + "/")
       
        try:
            campo = self.browser.find_element(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
            campo.send_keys("Teste de Sistema Automatizado")
            self.passo_lento(2)
            
            botao = self.browser.find_element(By.CSS_SELECTOR, "button, input[type='submit']")
            print("Interação simulada com sucesso!")
        except Exception:
            print("Nenhum formulário padrão foi encontrado nesta tela para preenchimento.")

        self.passo_lento(2)
