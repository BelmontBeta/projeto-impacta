from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
import os

   class HistoriaTest(StaticLiveServerTestCase):
       def setUp(self):
           opts = webdriver.ChromeOptions()
           if os.environ.get("CI"):
               opts.add_argument("--headless=new")
           self.browser = webdriver.Chrome(options=opts)

       def tearDown(self):
           self.browser.quit()

       def test_minha_historia(self):
           self.browser.get(self.live_server_url + "/sua-url/")
           self.browser.find_element(By.NAME, "campo").send_keys("valor")
           self.browser.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
           self.assertIn("valor", self.browser.page_source)
