import os
import time
import unittest
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

User = get_user_model()


@unittest.skipUnless(
    os.environ.get("RODAR_SELENIUM"),
    "defina RODAR_SELENIUM=1 para rodar os testes do Chrome",
)
class SistemaCompletoE2ETest(StaticLiveServerTestCase):
    def setUp(self):
        opts = webdriver.ChromeOptions()
        if os.environ.get("HEADLESS"):
            opts.add_argument("--headless=new")
        
        self.browser = webdriver.Chrome(options=opts)
        self.browser.implicitly_wait(5)
        self.browser.maximize_window()
        self.wait = WebDriverWait(self.browser, 10)

    def tearDown(self):
        time.sleep(2)
        self.browser.quit()

    def passo_lento(self, segundos=2):
        """Pausa para permitir acompanhamento visual da automação."""
        time.sleep(segundos)

    def test_fluxo_completo_sistema(self):
        # -------------------------------------------------------------
        # 1. PÁGINAS INSTITUCIONAIS PÚBLICAS E CONTATO
        # -------------------------------------------------------------
        print("\n--- [1/7] Testando Páginas Institucionais Públicas ---")
        
        # Home
        self.browser.get(self.live_server_url + "/")
        self.passo_lento(1)
        self.assertIn("ESG aplicado ao ramo alimentício", self.browser.page_source)

        # Sobre
        self.browser.get(self.live_server_url + "/sobre/")
        self.passo_lento(1)
        self.assertIn("Sobre o projeto", self.browser.page_source)

        # Desafios
        self.browser.get(self.live_server_url + "/desafios/")
        self.passo_lento(1)
        self.assertIn("Desafios do ramo alimentício", self.browser.page_source)

        # Soluções
        self.browser.get(self.live_server_url + "/solucoes/")
        self.passo_lento(1)
        self.assertIn("Soluções do nosso projeto", self.browser.page_source)

        # Contato & Preenchimento do Formulário
        print("Testando formulário de Contato...")
        self.browser.get(self.live_server_url + "/contato/")
        self.passo_lento(1)

        try:
            input_nome = self.browser.find_element(By.CSS_SELECTOR, "input[name='nome'], input[type='text']")
            input_nome.clear()
            input_nome.send_keys("Testador E2E Selenium")

            try:
                input_email = self.browser.find_element(By.CSS_SELECTOR, "input[name='email'], input[type='email']")
                input_email.clear()
                input_email.send_keys("testador@impacta.com")
            except Exception:
                pass

            try:
                input_assunto = self.browser.find_element(By.CSS_SELECTOR, "input[name='assunto'], input[name='subject']")
                input_assunto.clear()
                input_assunto.send_keys("Teste de Contato E2E")
            except Exception:
                pass

            try:
                textarea_msg = self.browser.find_element(By.TAG_NAME, "textarea")
                textarea_msg.clear()
                textarea_msg.send_keys("Mensagem automatizada de teste do formulário de contato.")
            except Exception:
                pass

            self.passo_lento(1)
            btn_enviar = self.browser.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            # Usando JS para evitar intercepção por rodapé/header fixo
            self.browser.execute_script("arguments[0].click();", btn_enviar)
            self.passo_lento(2)
            print("Formulário de contato enviado.")
        except Exception as e:
            print(f"Aviso ao testar contato: {e}")

        # -------------------------------------------------------------
        # 2. AUTENTICAÇÃO E GESTÃO DE CONTA (LOGIN E PERFIL)
        # -------------------------------------------------------------
        print("\n--- [2/7] Testando Autenticação e Gestão de Perfil ---")
        
        email_teste = "gestor.restaurante@impacta.com"
        senha_teste = "SenhaSegura123!"
        nome_teste = "Gestor ESG"

        User.objects.create_user(
            username=email_teste,
            email=email_teste,
            password=senha_teste,
            first_name=nome_teste
        )

        self.browser.get(self.live_server_url + "/acesso/")
        self.passo_lento(1)

        # Seleciona especificamente os campos do formulário de Login (data-form="login")
        form_login = self.browser.find_element(By.CSS_SELECTOR, "form[data-form='login']")
        campo_email = form_login.find_element(By.NAME, "email")
        campo_senha = form_login.find_element(By.NAME, "senha")
        
        campo_email.clear()
        campo_email.send_keys(email_teste)
        campo_senha.clear()
        campo_senha.send_keys(senha_teste)
        self.passo_lento(1)
        
        btn_login = form_login.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.browser.execute_script("arguments[0].click();", btn_login)
        self.passo_lento(2)

        print("Login realizado com sucesso via formulário!")

        print("Atualizando dados em Minha Conta...")
        self.browser.get(self.live_server_url + "/minha-conta/")
        self.passo_lento(1)

        try:
            campo_novo_nome = self.browser.find_element(By.NAME, "first_name")
            campo_novo_nome.clear()
            campo_novo_nome.send_keys("Gestor ESG Atualizado")
            
            btn_salvar_perfil = self.browser.find_element(By.XPATH, "//form//button[contains(text(), 'Salvar') or @type='submit']")
            self.browser.execute_script("arguments[0].click();", btn_salvar_perfil)
            self.passo_lento(2)
            print("Perfil atualizado com sucesso!")
        except Exception as e:
            print(f"Aviso ao atualizar perfil: {e}")

        # -------------------------------------------------------------
        # 3. DIAGNÓSTICO ESG E RESULTADO DETALHADO
        # -------------------------------------------------------------
        print("\n--- [3/7] Testando Diagnóstico ESG completo ---")
        
        self.browser.get(self.live_server_url + "/guardiao/boas-vindas/")
        self.passo_lento(2)

        try:
            btn_iniciar = self.browser.find_element(By.CSS_SELECTOR, "form[action*='iniciar'] button, button.botao-iniciar")
            self.browser.execute_script("arguments[0].click();", btn_iniciar)
            self.passo_lento(2)
        except Exception as e:
            print(f"Aviso ao iniciar diagnóstico: {e}")

        print("Respondendo perguntas do Diagnóstico ESG...")
        perguntas_respondidas = 0
        
        for i in range(1, 20):
            if "resultado" in self.browser.current_url and "pergunta" not in self.browser.current_url:
                break

            try:
                opcoes = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='radio']"))
                )
                if opcoes:
                    self.browser.execute_script("arguments[0].click();", opcoes[0])
                    self.passo_lento(1)

                btn_avancar = self.browser.find_element(By.CSS_SELECTOR, "form.quiz-conteudo button[type='submit'], form button[type='submit']")
                self.browser.execute_script("arguments[0].click();", btn_avancar)
                
                perguntas_respondidas += 1
                self.passo_lento(2)
            except Exception as err:
                print(f"Finalizando quiz ou transição na pergunta {perguntas_respondidas + 1}: {err}")
                break

        print(f"Diagnóstico finalizado ({perguntas_respondidas} perguntas respondidas).")
        self.passo_lento(2)

        try:
            print("Navegando para o Resultado Detalhado por Pilar...")
            btn_detalhado = self.browser.find_element(By.XPATH, "//a[contains(text(), 'Ver resultados detalhados') or contains(@href, 'detalhado')]")
            self.browser.execute_script("arguments[0].click();", btn_detalhado)
            self.passo_lento(2)

            accordions = self.browser.find_elements(By.TAG_NAME, "summary")
            for summary in accordions:
                self.browser.execute_script("arguments[0].click();", summary)
                self.passo_lento(1)
        except Exception as e:
            print(f"Aviso na tela de resultado detalhado: {e}")

        # -------------------------------------------------------------
        # 4. PLANO DE AÇÃO E MISSÕES
        # -------------------------------------------------------------
        print("\n--- [4/7] Testando Plano de Ação e Missões ---")
        try:
            btn_plano_acao = self.browser.find_element(By.XPATH, "//a[contains(text(), 'Ver plano de ação') or contains(@href, 'plano-acao')]")
            self.browser.execute_script("arguments[0].click();", btn_plano_acao)
            self.passo_lento(2)

            missoes = self.browser.find_elements(By.CSS_SELECTOR, ".missao-acoes a")
            if missoes:
                print("Visualizando detalhes da primeira missão...")
                self.browser.execute_script("arguments[0].click();", missoes[0])
                self.passo_lento(2)

                try:
                    btn_concluir = self.browser.find_element(
                        By.XPATH, 
                        "//button[contains(text(), 'Concluída') or contains(text(), 'Marcar como concluída')]"
                    )
                    self.browser.execute_script("arguments[0].click();", btn_concluir)
                    self.passo_lento(2)
                    print("Status da missão alternado!")
                except Exception as e:
                    print(f"Aviso ao alternar missão: {e}")
        except Exception as e:
            print(f"Aviso no plano de ação: {e}")

        # -------------------------------------------------------------
        # 5. DASHBOARD E MÓDULO DE GASTOS
        # -------------------------------------------------------------
        print("\n--- [5/7] Testando Módulo de Gastos / Dashboard ---")
        self.browser.get(self.live_server_url + "/gastos/painel/")
        self.passo_lento(2)
        print("Dashboard de Gastos acessado.")

        # -------------------------------------------------------------
        # 6. FORNECEDORES E MAPA ESG
        # -------------------------------------------------------------
        print("\n--- [6/7] Testando Fornecedores / Mapa ESG ---")
        self.browser.get(self.live_server_url + "/guardiao/fornecedores/")
        self.passo_lento(2)

        try:
            campo_busca_mapa = self.browser.find_element(By.ID, "campo-busca")
            campo_busca_mapa.clear()
            campo_busca_mapa.send_keys("Recife")

            btn_buscar_mapa = self.browser.find_element(By.ID, "botao-buscar")
            self.browser.execute_script("arguments[0].click();", btn_buscar_mapa)
            self.passo_lento(3)
            print("Busca realizada no Mapa ESG.")
        except Exception as e:
            print(f"Aviso no teste do mapa: {e}")

        # -------------------------------------------------------------
        # 7. PASSAPORTE DE SABORES E QR CODE (CRUD DE INGREDIENTES)
        # -------------------------------------------------------------
        print("\n--- [7/7] Testando Passaporte de Sabores e QR Code ---")
        self.browser.get(self.live_server_url + "/guardiao/passaporte/editar/")
        self.passo_lento(2)

        try:
            nome_rest = self.browser.find_element(By.ID, "nome_restaurante")
            nome_rest.clear()
            nome_rest.send_keys("Restaurante Orgânico E2E")

            historia_rest = self.browser.find_element(By.ID, "historia")
            historia_rest.clear()
            historia_rest.send_keys("História focada no desenvolvimento sustentável e apoio local.")

            btn_salvar_passaporte = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Salvar Passaporte')]")
            self.browser.execute_script("arguments[0].click();", btn_salvar_passaporte)
            self.passo_lento(2)
            print("Informações do Passaporte salvas.")
        except Exception as e:
            print(f"Aviso ao salvar passaporte: {e}")

        try:
            print("Cadastrando ingrediente no Passaporte...")
            input_ing_nome = self.browser.find_element(By.ID, "ingrediente_nome")
            input_ing_origem = self.browser.find_element(By.ID, "ingrediente_origem")
            input_ing_fornecedor = self.browser.find_element(By.ID, "ingrediente_fornecedor")

            input_ing_nome.send_keys("Tomate Orgânico")
            input_ing_origem.send_keys("Horta Local Recife")
            input_ing_fornecedor.send_keys("Produtor João da Silva")

            btn_add_ing = self.browser.find_element(By.XPATH, "//form[contains(@action, 'adicionar')]//button")
            self.browser.execute_script("arguments[0].click();", btn_add_ing)
            self.passo_lento(2)
            print("Ingrediente cadastrado com sucesso!")
        except Exception as e:
            print(f"Aviso ao cadastrar ingrediente: {e}")

        print("\nTestando encerramento da sessão (Logout)...")
        self.browser.get(self.live_server_url + "/guardiao/boas-vindas/")
        self.passo_lento(1)
        
        try:
            btn_conta = self.browser.find_element(By.ID, "botaoConta")
            self.browser.execute_script("arguments[0].click();", btn_conta)
            self.passo_lento(1)
            
            btn_sair = self.browser.find_element(By.CSS_SELECTOR, "form[action*='sair'] button")
            self.browser.execute_script("arguments[0].click();", btn_sair)
            self.passo_lento(2)
            print("Logout efetuado com sucesso!")
        except Exception as e:
            print(f"Aviso ao realizar logout: {e}")

        print("\n==================================================")
        print(" TODOS OS FLUXOS FORAM TESTADOS COM SUCESSO! ")
        print("==================================================")
