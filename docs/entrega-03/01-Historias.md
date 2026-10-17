# 01 - Histórias de Usuário (Entrega 03)

Este arquivo contém as histórias de usuário definidas para a Entrega 03, com critérios de aceitação no formato BDD (Given / When / Then).

## História 1 — Envio e armazenamento de Feedback
Como usuário visitante eu quero enviar um feedback pelo formulário de contato para que minha mensagem fique registrada no sistema.

Critérios / Cenários (BDD):
- Cenário: Envio de feedback válido
  Given que estou na página de contato
  When eu preencho todos os campos obrigatórios com dados válidos e clico em "Enviar"
  Then eu recebo uma mensagem de sucesso e o feedback é salvo no banco de dados

- Cenário: Falha por campos obrigatórios vazios
  Given que estou na página de contato
  When eu deixo campos obrigatórios em branco e tento enviar
  Then eu vejo mensagens de erro para os campos obrigatórios e o feedback não é salvo

---

## História 2 — Validação de campos do formulário (frontend e backend)
Como usuário eu quero que o formulário valide os dados obrigatórios e formatos (ex: email) para evitar envios incorretos.

Critérios / Cenários (BDD):
- Cenário: Email inválido
  Given que estou no formulário de contato
  When eu insiro um email com formato inválido e tento enviar
  Then o sistema mostra validação de formato de email e impede o envio

- Cenário: Tamanho máximo de mensagem
  Given que estou no formulário de contato
  When eu insiro uma mensagem maior que 2000 caracteres e tento enviar
  Then o sistema mostra erro de tamanho e impede o envio

---

## História 3 — Visualização de feedbacks no painel administrativo
Como administrador eu quero visualizar a lista de feedbacks no Django Admin para poder consultar e responder quando necessário.

Critérios / Cenários (BDD):
- Cenário: Lista de feedbacks acessível
  Given que estou autenticado como admin
  When eu acesso /admin/ e vou à seção de feedbacks
  Then eu vejo a lista com os campos (nome, email, data, mensagem)

- Cenário: Acesso não permitido para usuário anônimo
  Given que não estou autenticado
  When tento acessar /admin/feedbacks
  Then sou redirecionado para a tela de login

---

## História 4 — Exportar feedbacks como CSV
Como administrador eu quero exportar os feedbacks selecionados em CSV para analisar offline.

Critérios / Cenários (BDD):
- Cenário: Exportação CSV
  Given que estou no Django Admin na lista de feedbacks
  When eu seleciono alguns registros e escolho a ação "Exportar CSV"
  Then um arquivo CSV é gerado contendo os campos selecionados e o download é iniciado

- Cenário: Sem seleção
  Given que não selecionei nenhum feedback
  When tento executar a ação de exportar
  Then o sistema informa que devo selecionar ao menos um registro

---

## História 5 — Página de desafios com filtro por tema
Como visitante eu quero filtrar os desafios por tema (ex: resíduos, energia, fornecedores) para encontrar conteúdo relevante.

Critérios / Cenários (BDD):
- Cenário: Filtro por tema
  Given que estou na página de desafios
  When eu seleciono o filtro "Resíduos"
  Then vejo apenas os desafios marcados com o tema "Resíduos"

- Cenário: Filtro sem resultados
  Given que estou na página de desafios
  When eu escolho um filtro sem correspondência
  Then é exibida uma mensagem "Nenhum desafio encontrado"

---

## História 6 — Dashboard simples de métricas ESG (contadores)
Como membro da equipe eu quero ver um painel com métricas básicas (total de feedbacks, feedbacks no último mês, número de desafios) para ter visão rápida do projeto.

Critérios / Cenários (BDD):
- Cenário: Visualização de métricas
  Given que estou autenticado como membro com permissão de leitura
  When acesso a rota /dashboard/
  Then vejo os contadores atualizados com os valores corretos

- Cenário: Dados atualizados após novo feedback
  Given que existiam N feedbacks
  When um novo feedback é enviado com sucesso
  Then o contador "Total de feedbacks" aumenta para N+1

---

## História 7 — Mobile responsiveness e acessibilidade básica
Como usuário mobile eu quero que o site se adapte ao meu dispositivo e esteja com contraste adequado para que eu consiga ler e navegar.

Critérios / Cenários (BDD):
- Cenário: Layout responsivo
  Given que acesso o site por um dispositivo com largura <= 480px
  When abro a página inicial
  Then o layout adapta o menu e os cards para leitura vertical

- Cenário: Contraste mínimo
  Given que uso um leitor ou preciso de contraste
  When visualizo o site
  Then o contraste entre texto e fundo segue padrões mínimos WCAG AA

