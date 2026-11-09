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
        self.browser.quit()

    def test_minha_historia(self):
        self.browser.get(self.live_server_url + "/")
        
        time.sleep(4)
        
        self.assertIn("<body", self.browser.page_source.lower())
