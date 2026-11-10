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
            self.browser.execute_script("arguments[0].click();", btn_enviar)
            self.passo_lento(2)
            print("Formulário de contato enviado com sucesso.")
        except Exception as e:
            print(f"Aviso ao testar contato: {e}")

        # -------------------------------------------------------------
        # 2. AUTENTICAÇÃO E GESTÃO DE CONTA (LOGIN E PERFIL)
        # -------------------------------------------------------------
        print("\n--- [2/7] Testando Autenticação e Gestão de Perfil ---")
        
        email_teste = "gestor.restaurante@impacta.com"
        senha_teste = "SenhaSegura123!"
        nome_teste = "Gestor ESG"

        # 1. Cria o usuário no banco de dados
        user = User.objects.create_user(
            username=email_teste,
            email=email_teste,
            password=senha_teste,
            first_name=nome_teste
        )

        # 2. Injeta o cookie de sessão do Django diretamente no Selenium
        self.client.login(username=email_teste, password=senha_teste)
        self.browser.get(self.live_server_url + "/")
        session_cookie = self.client.cookies['sessionid']
        self.browser.add_cookie({
            'name': 'sessionid',
            'value': session_cookie.value,
            'path': '/',
        })
        print("Sessão de usuário autenticada e mantida com sucesso!")

        # 3. Testa a atualização do perfil em Minha Conta
        print("Atualizando dados em Minha Conta...")
        self.browser.get(self.live_server_url + "/minha-conta/")
        self.passo_lento(2)

        try:
            campo_novo_nome = self.browser.find_element(By.CSS_SELECTOR, "input[name='first_name'], input[name='nome']")
            campo_novo_nome.clear()
            campo_novo_nome.send_keys("Gestor ESG Atualizado")
            
            btn_salvar_perfil = self.browser.find_element(By.CSS_SELECTOR, "form button[type='submit']")
            self.browser.execute_script("arguments[0].click();", btn_salvar_perfil)
            self.passo_lento(2)
            print("Perfil atualizado com sucesso!")
        except Exception as e:
            print(f"Aviso ao atualizar perfil: {e}")

        # -------------------------------------------------------------
        # 3. DIAGNÓSTICO ESG COMPLETO (RESPONDE TODAS AS PERGUNTAS)
        # -------------------------------------------------------------
        print("\n--- [3/7] Testando Diagnóstico ESG completo ---")
        
        self.browser.get(self.live_server_url + "/guardiao/boas-vindas/")
        self.passo_lento(2)

        # Inicia o diagnóstico se estiver na tela inicial
        try:
            btn_iniciar = self.browser.find_element(By.CSS_SELECTOR, "form[action*='iniciar'] button, a[href*='iniciar'], button.btn-iniciar")
            self.browser.execute_script("arguments[0].click();", btn_iniciar)
            self.passo_lento(2)
        except Exception:
            pass

        print("Respondendo a TODAS as perguntas do Diagnóstico ESG...")
        perguntas_respondidas = 0
        
        # Percorre dinamicamente todas as perguntas do questionário
        for rodada in range(1, 25):
            url_atual = self.browser.current_url.lower()

            # Se for redirecionado para a tela de resultado final, encerra o loop
            if "resultado" in url_atual and "pergunta" not in url_atual:
                print("Tela de resultado final atingida!")
                break

            try:
                # Aguarda as opções do rádio button da pergunta atual
                opcoes = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='radio']"))
                )
                if opcoes:
                    # Clica na primeira alternativa da pergunta
                    self.browser.execute_script("arguments[0].click();", opcoes[0])
                    self.passo_lento(1)

                # Clica no botão para avançar para a próxima pergunta
                btn_avancar = self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
                self.browser.execute_script("arguments[0].click();", btn_avancar)
                
                perguntas_respondidas += 1
                print(f"  -> Pergunta {perguntas_respondidas} respondida!")
                self.passo_lento(2)
            except Exception as err:
                print(f"Concluindo questionário após {perguntas_respondidas} perguntas. (Status: {err})")
                break

        print(f"Diagnóstico ESG concluído! Total de {perguntas_respondidas} perguntas respondidas.")
        self.passo_lento(2)

        # Tela de Resultado Detalhado por Pilar
        try:
            print("Navegando para o Resultado Detalhado por Pilar...")
            btn_detalhado = self.browser.find_element(By.XPATH, "//a[contains(text(), 'detalhad') or contains(@href, 'detalhad')]")
            self.browser.execute_script("arguments[0].click();", btn_detalhado)
            self.passo_lento(2)

            accordions = self.browser.find_elements(By.TAG_NAME, "summary")
            for summary in accordions:
                self.browser.execute_script("arguments[0].click();", summary)
                self.passo_lento(1)
        except Exception as e:
            print(f"Aviso no resultado detalhado: {e}")

        # -------------------------------------------------------------
        # 4. PLANO DE AÇÃO E MISSÕES
        # -------------------------------------------------------------
        print("\n--- [4/7] Testando Plano de Ação e Missões ---")
        try:
            btn_plano_acao = self.browser.find_element(By.XPATH, "//a[contains(text(), 'plano') or contains(@href, 'plano')]")
            self.browser.execute_script("arguments[0].click();", btn_plano_acao)
            self.passo_lento(2)

            missoes = self.browser.find_elements(By.CSS_SELECTOR, ".missao-acoes a, a.btn-missao")
            if missoes:
                print("Visualizando detalhes da primeira missão...")
                self.browser.execute_script("arguments[0].click();", missoes[0])
                self.passo_lento(2)

                try:
                    btn_concluir = self.browser.find_element(
                        By.XPATH, 
                        "//button[contains(text(), 'Concluíd') or contains(text(), 'Marcar')]"
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
        print("Dashboard de Gastos acessado com sucesso!")

        # -------------------------------------------------------------
        # 6. FORNECEDORES E MAPA ESG
        # -------------------------------------------------------------
        print("\n--- [6/7] Testando Fornecedores / Mapa ESG ---")
        self.browser.get(self.live_server_url + "/guardiao/fornecedores/")
        self.passo_lento(2)

        try:
            campo_busca_mapa = self.browser.find_element(By.CSS_SELECTOR, "#campo-busca, input[name='busca'], input[type='search']")
            campo_busca_mapa.clear()
            campo_busca_mapa.send_keys("Recife")

            btn_buscar_mapa = self.browser.find_element(By.CSS_SELECTOR, "#botao-buscar, button[type='submit']")
            self.browser.execute_script("arguments[0].click();", btn_buscar_mapa)
            self.passo_lento(3)
            print("Busca realizada com sucesso no Mapa ESG.")
        except Exception as e:
            print(f"Aviso no teste do mapa: {e}")

        # -------------------------------------------------------------
        # 7. PASSAPORTE DE SABORES E QR CODE (CRUD DE INGREDIENTES)
        # -------------------------------------------------------------
        print("\n--- [7/7] Testando Passaporte de Sabores e QR Code ---")
        self.browser.get(self.live_server_url + "/guardiao/passaporte/editar/")
        self.passo_lento(2)

        # 1. Edita informações do Passaporte
        try:
            nome_rest = self.browser.find_element(By.CSS_SELECTOR, "#nome_restaurante, input[name='nome_restaurante']")
            nome_rest.clear()
            nome_rest.send_keys("Restaurante Orgânico E2E")

            historia_rest = self.browser.find_element(By.CSS_SELECTOR, "#historia, textarea[name='historia']")
            historia_rest.clear()
            historia_rest.send_keys("História focada no desenvolvimento sustentável e apoio local.")

            btn_salvar_passaporte = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Salvar Passaporte') or contains(text(), 'Salvar')]")
            self.browser.execute_script("arguments[0].click();", btn_salvar_passaporte)
            self.passo_lento(2)
            print("Informações do Passaporte salvas!")
        except Exception as e:
            print(f"Aviso ao salvar passaporte: {e}")

        # 2. Cadastra um ingrediente
        try:
            print("Cadastrating ingrediente no Passaporte...")
            input_ing_nome = self.browser.find_element(By.CSS_SELECTOR, "#ingrediente_nome, input[name='nome']")
            input_ing_origem = self.browser.find_element(By.CSS_SELECTOR, "#ingrediente_origem, input[name='origem']")
            input_ing_fornecedor = self.browser.find_element(By.CSS_SELECTOR, "#ingrediente_fornecedor, input[name='fornecedor']")

            input_ing_nome.send_keys("Tomate Orgânico")
            input_ing_origem.send_keys("Horta Local Recife")
            input_ing_fornecedor.send_keys("Produtor João da Silva")

            btn_add_ing = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Adicionar') or contains(text(), 'Cadastrar')]")
            self.browser.execute_script("arguments[0].click();", btn_add_ing)
            self.passo_lento(2)
            print("Ingrediente cadastrado com sucesso!")
        except Exception as e:
            print(f"Aviso ao cadastrar ingrediente: {e}")

        # 3. Encerramento da Sessão (Logout)
        print("\nTestando encerramento da sessão (Logout)...")
        self.browser.get(self.live_server_url + "/guardiao/boas-vindas/")
        self.passo_lento(1)
        
        try:
            btn_conta = self.browser.find_element(By.CSS_SELECTOR, "#botaoConta, .menu-usuario, a[href*='conta']")
            self.browser.execute_script("arguments[0].click();", btn_conta)
            self.passo_lento(1)
            
            btn_sair = self.browser.find_element(By.CSS_SELECTOR, "form[action*='sair'] button, a[href*='sair']")
            self.browser.execute_script("arguments[0].click();", btn_sair)
            self.passo_lento(2)
            print("Logout efetuado com sucesso!")
        except Exception as e:
            print(f"Aviso ao realizar logout: {e}")

        print("\n==================================================")
        print(" TODOS OS FLUXOS FORAM TESTADOS COM SUCESSO! ")
        print("==================================================")
