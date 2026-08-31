# 🥗 Análise de Competidores e Benchmarking - Projeto Impacta
> Plataforma Web de Gestão ESG para PMEs do Setor Alimentício

## 1. Introdução
Este documento apresenta a análise de mercado para o **Projeto Impacta**, uma aplicação web desenvolvida em **Python/Django** projetada para apoiar Pequenas e Médias Empresas (PMEs) do setor alimentício (restaurantes, distribuidores e pequenas agroindústrias) no monitoramento, gestão e publicação de dados ESG (*Environmental, Social, and Governance*).

---

## 2. Análise Detalhada dos Competidores

### 2.1 Sustentase
- **Descrição do Funcionamento:** Sistema SaaS focado em diagnósticos de impacto socioambiental para empresas em crescimento via formulários de consumo energético e resíduos.
- **Capturas de Tela/Interface:**
  
  ![Interface Sustentase](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxz_PU7tIQpA5U4FGWiLwRc1VZulTBJcs-bN06bJmFCG2HeMOrKLc8fss&s=10)
- **Pontos Fortes:**
  - Interface simples voltada para PMEs.
  - Relatórios executivos prontos para download.
- **Pontos Fracos:**
  - Ausência de controle específico sobre descarte de alimentos orgânicos.
  - Não possui integração automatizada com banco de dados via APIs or ORM.

### 2.2 Resultante ESG
- **Descrição do Funcionamento:** Plataforma de consultoria e cálculo de pegada de carbono focada em diagnósticos corporativos avançados.
- **Capturas de Tela/Interface:**
  
  ![Interface Resultante](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSdMQFy6N7niGOSEDE8_3m2Etkr7Y-3RQANixFtRQMM9sDVHW7keSbU6WM&s=10)
- **Pontos Fortes:**
  - Alinhamento rigoroso aos padrões internacionais (GHG Protocol e GRI).
  - Alta credibilidade de relatórios corporativos.
- **Pontos Fracos:**
  - Custo inviável para PMEs alimentícias.
  - Pouca interatividade para a operação do dia a dia (ex: cozinhas e depósitos).

### 2.3 EcoVadis
- **Descrição do Funcionamento:** Plataforma global de classificação de sustentabilidade na cadeia de suprimentos corporativa.
- **Capturas de Tela/Interface:**
  
  ![Interface EcoVadis](https://destraconsultoria.com.br/wp-content/uploads/2023/02/ecovadis.png)
- **Pontos Fortes:**
  - Reconhecimento internacional e selo auditado.
  - Avaliação rigorosa da cadeia de suprimentos.
- **Pontos Fracos:**
  - Burocracia elevada e custos em moeda estrangeira.
  - Interface complexa e sem foco na regulamentação alimentar nacional (ANVISA/MAPA).

### 2.4 Moka ESG
- **Descrição do Funcionamento:** Ferramenta SaaS para acompanhamento diário de indicadores de governança e métricas de desempenho socioambiental.
- **Capturas de Tela/Interface:**
  
  ![Interface Moka ESG](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQmXa5YNTjrNAh7VDG7cxx0Ao1y-z0VqPCtEVleR2BvcntbrCi7mWAgOwk&s=10)
- **Pontos Fortes:**
  - Dashboards visuais bem estruturados.
  - Canal de denúncias e módulo de governança integrados.
- **Pontos Fracos:**
  - Sem rastreamento de desperdício de insumos orgânicos.
  - Não oferece relatórios voltados ao consumidor final do ramo alimentício.

### 2.5 Greenly
- **Descrição do Funcionamento:** Software de contabilidade de carbono que calcula emissões a partir de dados financeiros e de compras.
- **Capturas de Tela/Interface:**
  
  ![Interface Greenly](https://tse3.mm.bing.net/th/id/OIP.o8HYIM2BmcY2rOuwwcy-HAHaE7?r=0&pid=Api)
- **Pontos Fortes:**
  - Coleta e classificação automatizada de gastos.
  - Interface moderna e plano de ação gamificado.
- **Pontos Fracos:**
  - Foco exclusivo em emissões (pilhar Ambiental), ignorando o Social e a Governança.
  - Pouco suporte para dados operacionais de preparo e armazenamento de alimentos.

---

## 3. Benchmark Comparativo

| Critério / Funcionalidade | Sustentase | Resultante | EcoVadis | Moka ESG | Greenly | **Projeto Impacta** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Aplicação Web Adaptável (Design Responsivo)** | Sim | Parcial | Sim | Sim | Sim | **Sim** |
| **Pequenas e Médias Empresas Alimentícias (Foco)** | Parcial | Não | Não | Não | Não | **Sim** |
| **Persistência CRUD em DB Relacional (MySQL/PostgreSQL)** | Sim | Sim | Sim | Sim | Sim | **Sim** |
| **Cálculo e Registro de Desperdício de Alimentos** | Não | Não | Não | Não | Não | **Sim** |
| **Geração de QR Code/Selo Público para o Cliente Final** | Não | Não | Sim | Não | Não | **Sim** |
| **Deploy Habilitado em Nuvem (Azure/AWS/Render)** | Sim | Sim | Sim | Sim | Sim | **Sim** |

---

## 4. Requisitos Não Triviais para o Projeto Impacta

1. **RNF01 - Processamento Dinâmico ORM/Django para Conversão de Desperdício em Carbono:**
   - O sistema deve interceptar as inserções no banco de dados através de *Django Signals* e calcular instantaneamente as emissões equivalentes de $CH_4$ e $CO_2e$ com base no volume de insumos descartados, garantindo a atualização do banco PostgreSQL/MySQL com tempo de resposta `< 120ms`.

2. **RNF02 - Autenticação Granular e Controle de Acesso por Papel (RBAC com Django Groups):**
   - A aplicação web deve implementar permissões estritas para garantir que operadores de cozinha, gestores ESG e auditores externos acessem exclusivamente seus respectivos escopos de leitura e escrita no banco de dados, auditando cada alteração com *timestamps* imutáveis.

3. **RNF03 - Invalidation Caching e Cache de Consultas Relacionais para Dashboards:**
   - Para permitir a renderização de relatórios adaptáveis em dispositivos móveis sem sobrecarregar o banco de dados na nuvem, a aplicação deve utilizar Redis como camada de cache do ORM Django, garantindo que métricas agregadas sejam entregues em menos de **80ms**.

4. **RNF04 - Pipeline Integrado de Pipeline CI/CD para Deploy Contínuo em Nuvem (Azure App Service):**
   - O ambiente de produção em nuvem deve contar com deploy automatizado via GitHub Actions, executando testes de integração de leitura/escrita no banco de dados e aplicando migrações de esquema (*Django Migrations*) sem *downtime* visível ao usuário.

---
