# Projeto Impacta 🚀

Solução web de impacto e inovação voltada à gestão ESG para pequenas e médias empresas do setor alimentício.

---

## 📝 Descrição do Projeto

O Projeto Impacta é uma aplicação web desenvolvida na disciplina **Projetos 2**, da **CESAR School**, com o objetivo de apresentar soluções relacionadas à sustentabilidade, impacto social e inovação no ramo alimentício.

A aplicação foi desenvolvida utilizando o framework Django e possui páginas informativas sobre ESG, desafios do setor, equipe do projeto e um formulário de contato para envio de feedbacks.

O projeto também foi publicado em ambiente de produção utilizando o Render.

---

## 🎯 Objetivos Principais

- Desenvolver uma solução web com foco em impacto social e empresarial;
- Aplicar conceitos de sustentabilidade no setor alimentício;
- Apresentar informações sobre práticas ESG;
- Permitir o envio e armazenamento de feedbacks;
- Aplicar conceitos de desenvolvimento web com Python e Django;
- Utilizar controle de versão com Git e GitHub;
- Aplicar metodologias ágeis durante o desenvolvimento;
- Publicar a aplicação em ambiente de produção.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Utilização |
|---|---|
| Python | Linguagem principal do projeto |
| Django | Framework web utilizado no desenvolvimento |
| HTML | Estrutura das páginas |
| CSS | Estilização e responsividade |
| SQLite | Banco de dados utilizado no desenvolvimento local |
| PostgreSQL | Banco de dados utilizado em produção |
| Gunicorn | Servidor WSGI da aplicação |
| WhiteNoise | Gerenciamento de arquivos estáticos em produção |
| Git | Controle de versão |
| GitHub | Repositório e gerenciamento de Issues |
| Jira | Organização das atividades e Sprint |
| Render | Hospedagem da aplicação |

---

## 📌 Funcionalidades

- Página inicial com apresentação do projeto;
- Página sobre o Projeto Impacta;
- Página com desafios relacionados ao ESG;
- Página com informações da equipe;
- Formulário de contato;
- Validação manual dos dados enviados pelo formulário;
- Armazenamento dos feedbacks no banco de dados;
- Painel administrativo do Django;
- Layout responsivo;
- Paleta de cores em tons de azul;
- Aplicação publicada em ambiente de produção.

A aplicação foi desenvolvida sem o uso de Generic Views e sem Django Forms, conforme orientação da disciplina. O formulário utiliza HTML, `request.POST` e validações implementadas manualmente.

---

## 🌐 Acesso à Aplicação

A aplicação está disponível em produção:

[https://projeto-impacta.onrender.com](https://projeto-impacta.onrender.com)

### Painel administrativo

O painel administrativo pode ser acessado em:

[https://projeto-impacta.onrender.com/admin/](https://projeto-impacta.onrender.com/admin/)

O acesso é restrito ao usuário administrador configurado no ambiente de produção.

Por motivos de segurança, a senha não é disponibilizada neste documento.

### Google Sites

O acompanhamento ao nosso projeto pode ser feita pelo:

[https://sites.google.com/cesar.school/impacta/home](https://sites.google.com/cesar.school/impacta/home)

---

## 📁 Estrutura Principal do Projeto

```text
projeto-impacta/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── core/
│   ├── management/
│   │   └── commands/
│   │       └── criar_admin.py
│   ├── templates/
│   └── ...
├── contato/
│   ├── migrations/
│   ├── templates/
│   │   └── contato/
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── ...
├── static/
│   └── css/
│       └── style.css
├── docs/
│   ├── github-issues.png
│   ├── sprint-02.png
│   ├── deploy-render.png
│   ├── commits-main.png
│   └── admin-feedback.png
├── docs/entrega-03/
│   ├── README.md
│   ├── 01-Historias.md
│   ├── 02-Selecao-e-POSTIT.md
│   └── 03-Observacoes.md
├── manage.py
├── requirements.txt
└── README.md
```

---

## ▶️ Como Rodar o Projeto Localmente

### Pré-requisitos

- Python 3.8 ou superior;
- Git;
- pip.

### 1. Clonar o repositório

```bash
git clone https://github.com/BelmontBeta/projeto-impacta.git
cd projeto-impacta
```

### 2. Criar o ambiente virtual

No Windows:

```bash
python -m venv venv
```

### 3. Ativar o ambiente virtual

No Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

No Prompt de Comando:

```cmd
venv\Scripts\activate
```

### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Executar as migrações

```bash
python manage.py migrate
```

### 6. Verificar o projeto

```bash
python manage.py check
```

### 7. Iniciar o servidor

```bash
python manage.py runserver
```

A aplicação ficará disponível em:

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🚀 Deploy

O deploy da aplicação foi realizado utilizando o Render.

### Build Command

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py criar_admin
```

### Start Command

```bash
gunicorn config.wsgi:application
```

### Variáveis de ambiente

As principais variáveis utilizadas em produção são:

```text
SECRET_KEY
DEBUG
ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS
DATABASE_URL
DJANGO_SUPERUSER_USERNAME
DJANGO_SUPERUSER_EMAIL
DJANGO_SUPERUSER_PASSWORD
```

As informações sensíveis não são armazenadas no código-fonte nem no repositório público.

---

## 🧪 Testes Realizados

Foram realizados testes locais e em ambiente de produção.

| Teste | Resultado |
|---|---|
| Verificação do projeto com `python manage.py check` | Aprovado |
| Execução das migrações | Aprovado |
| Coleta dos arquivos estáticos | Aprovado |
| Inicialização do servidor local | Aprovado |
| Abertura da página inicial | Aprovado |
| Navegação entre as páginas | Aprovado |
| Exibição da página da equipe | Aprovado |
| Aplicação da paleta azul | Aprovado |
| Abertura do formulário de contato | Aprovado |
| Validação de campos obrigatórios | Aprovado |
| Envio de feedback | Aprovado |
| Armazenamento do feedback no banco de dados | Aprovado |
| Acesso ao painel administrativo | Aprovado |
| Visualização dos feedbacks no painel administrativo | Aprovado |
| Funcionamento dos arquivos estáticos em produção | Aprovado |
| Acesso à aplicação publicada no Render | Aprovado |

---

## 📋 Entrega 02

### Descrição

Desenvolvimento, testes, documentação e publicação da aplicação web Projeto Impacta.

### Atividades realizadas

- Atualização das informações da equipe;
- Implementação das páginas da aplicação;
- Implementação do formulário de contato;
- Validação manual dos dados enviados;
- Armazenamento dos feedbacks no banco de dados;
- Configuração do painel administrativo;
- Correção da paleta de cores para tons de azul;
- Configuração dos arquivos estáticos;
- Configuração do banco de dados de produção;
- Publicação da aplicação no Render;
- Criação do acesso administrativo;
- Realização dos testes locais e em produção;
- Atualização do README;
- Organização das tarefas no Jira;
- Registro e acompanhamento de issues no GitHub.

### Data

18/09/2026

---

## 📋 Entrega 03

### Descrição

Material da Entrega 03: histórias de usuário escritas em Markdown, seleção das histórias implementadas, observações e próximos passos.

### Conteúdo adicionado

- docs/entrega-03/01-Historias.md — Histórias completas com BDD
- docs/entrega-03/02-Selecao-e-POSTIT.md — Histórias selecionadas (POST-IT)
- docs/entrega-03/03-Observacoes.md — Observações e próximos passos

### Ações pendentes

- Adicionar prints do backlog do JIRA e do quadro da Sprint 03 em docs/entrega-03/evidencias/
- Gravar screencast das histórias em produção e adicionar link em docs/entrega-03/README.md
- Criar issues no GitHub para as histórias planejadas (Export CSV, filtros, dashboard)

---

## 🐛 Issues e Bug Tracker

O acompanhamento de tarefas, problemas e correções foi realizado por meio do GitHub Issues.

Acesse o bug tracker:

[GitHub Issues do Projeto Impacta](https://github.com/BelmontBeta/projeto-impacta/issues)

### Evidência

![GitHub Issues](docs/github-issues.png)

---

## 📅 Gerenciamento de Atividades

### Jira

O projeto utiliza Jira para organização das atividades, sprints e acompanhamento do progresso do desenvolvimento.

Acesse o quadro do Jira:

[Quadro do Projeto Impacta no Jira](https://projetos-fds-cesar.atlassian.net/jira/software/projects/IMP26/summary?atlOrigin=eyJpIjoiZDQwNTFiODg5NDlmNDhhZWE2MTdjYjYyNjVhM2NlZjUiLCJwIjoiaiJ9)

---

(continuação do README original)
