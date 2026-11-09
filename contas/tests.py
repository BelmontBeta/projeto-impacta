from django.contrib.staticfiles.testing import StaticLiveServerTestCase
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

    def tearDown(self):
        time.sleep(3) 
        self.browser.quit()

    def passo_lento(self, segundos=3):
        """Força o robô a esperar para que você veja a ação no screencast."""
        time.sleep(segundos)

    def test_fluxo_da_historia(self):
        self.browser.get(self.live_server_url + "/")
        self.passo_lento(4) 

        self.browser.get(self.live_server_url + "/gastos/")
        self.passo_lento(4) 

        self.assertIn("<body", self.browser.page_source.lower())
