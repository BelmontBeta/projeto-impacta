# Histórias de Usuário — Sustentabilidade para Restaurantes

Este documento apresenta os quatro épicos do projeto, suas histórias de usuário e os cenários de validação em BDD.

## Épicos do projeto

1. [O Guardião Invisível — Reconhecimento e Estruturação](#épico-1-o-guardião-invisível)
2. [A Alquimia da Cozinha — Superação de Obstáculos e Educação](#épico-2-a-alquimia-da-cozinha)
3. [A Teia de Sabores — Impacto Comunitário e Redefinição do Futuro](#épico-3-a-teia-de-sabores)
4. [O Passaporte de Sabores — Transparência, Reconhecimento e Conexão com o Cliente](#épico-4-o-passaporte-de-sabores)

---

## Épico 1: O Guardião Invisível

**Tema:** Reconhecimento e Estruturação  
**Status:** Concluído

> Como dono de um pequeno restaurante, quero responder a um diagnóstico rápido e simplificado sobre a rotina da minha operação, para entender meu nível atual de sustentabilidade e receber um plano de ação prático sem depender de consultorias caras ou termos técnicos.

### História 1.1 — Iniciar o diagnóstico

**Como** dono de um pequeno restaurante,  
**quero** iniciar um diagnóstico de sustentabilidade,  
**para** avaliar as práticas atuais da minha operação.

#### Cenário BDD: Acessar o diagnóstico

    Funcionalidade: Iniciar diagnóstico de sustentabilidade

    Cenário: Proprietário inicia um novo diagnóstico
      Dado que o proprietário acessou a plataforma
      Quando seleciona a opção "Iniciar diagnóstico"
      Então o sistema apresenta as perguntas do diagnóstico
      E informa que as respostas devem refletir a rotina atual do restaurante

### História 1.2 — Responder às perguntas do diagnóstico

**Como** dono de um pequeno restaurante,  
**quero** responder a perguntas simples sobre a rotina do meu estabelecimento,  
**para** fornecer as informações necessárias para avaliar sua sustentabilidade.

#### Cenário BDD: Responder às perguntas obrigatórias

    Funcionalidade: Responder ao diagnóstico

    Cenário: Preencher todas as respostas obrigatórias
      Dado que o proprietário iniciou o diagnóstico
      Quando responde todas as perguntas obrigatórias
      Então o sistema permite avançar para a próxima pergunta
      E mantém as respostas preenchidas durante o diagnóstico

#### Cenário BDD: Tentar avançar sem responder uma pergunta obrigatória

    Cenário: Existem perguntas obrigatórias sem resposta
      Dado que o proprietário está preenchendo o diagnóstico
      E não selecionou uma opção de resposta
      Quando tenta avançar para a próxima pergunta
      Então o sistema não permite avançar
      E informa que é necessário escolher uma opção

### História 1.3 — Revisar e enviar o diagnóstico

**Como** dono de um pequeno restaurante,  
**quero** revisar minhas respostas antes de enviá-las,  
**para** corrigir possíveis erros e garantir que o resultado seja baseado em informações corretas.

#### Cenário BDD: Revisar e enviar respostas

    Funcionalidade: Revisar diagnóstico

    Cenário: Proprietário revisa e confirma as respostas
      Dado que o proprietário respondeu às perguntas do diagnóstico
      Quando acessa a etapa de revisão
      Então o sistema apresenta um resumo das respostas
      Quando confirma o envio do diagnóstico
      Então o sistema registra as respostas
      E inicia o cálculo do resultado

### História 1.4 — Visualizar o resultado do diagnóstico

**Como** dono de um pequeno restaurante,  
**quero** visualizar o resultado do diagnóstico em linguagem simples,  
**para** entender o nível atual de sustentabilidade da minha operação.

#### Cenário BDD: Exibir o resultado calculado

    Funcionalidade: Resultado do diagnóstico

    Cenário: Diagnóstico enviado com sucesso
      Dado que o proprietário concluiu o diagnóstico
      Quando o sistema conclui o cálculo
      Então apresenta uma pontuação de sustentabilidade de 0 a 100
      E exibe uma classificação correspondente ao resultado
      E apresenta um resumo dos resultados por pilar

### História 1.5 — Consultar pontos fortes e oportunidades de melhoria

**Como** dono de um pequeno restaurante,  
**quero** identificar os pontos fortes e as oportunidades de melhoria apresentados no resultado,  
**para** compreender quais áreas da operação precisam de atenção.

#### Cenário BDD: Consultar os detalhes da análise

    Funcionalidade: Análise das áreas de sustentabilidade

    Cenário: Consultar os detalhes do resultado
      Dado que o proprietário visualizou o resultado do diagnóstico
      Quando acessa os detalhes da análise
      Então o sistema apresenta as respostas organizadas por pilar
      E apresenta o nível de cada pilar
      E descreve os resultados sem utilizar termos técnicos

### História 1.6 — Receber um plano de ação prático

**Como** dono de um pequeno restaurante,  
**quero** receber ações práticas relacionadas ao resultado do diagnóstico,  
**para** saber quais medidas posso tomar para melhorar a sustentabilidade da operação.

#### Cenário BDD: Exibir ações recomendadas

    Funcionalidade: Plano de ação

    Cenário: Gerar plano de ação com base no diagnóstico
      Dado que o sistema calculou o resultado do diagnóstico
      Quando gera o plano de ação
      Então seleciona ações relacionadas às respostas que precisam de melhoria
      E cada ação contém uma descrição clara e prática
      E as ações são organizadas por semana e prioridade

---

## Épico 2: A Alquimia da Cozinha

**Tema:** Superação de Obstáculos e Educação

> Como gerente de cozinha, quero registrar os dados de consumo de água, energia e desperdício de alimentos, para acompanhar metas visuais de economia e treinar minha equipe com ações operacionais de baixo custo.

### História 2.1 — Registrar consumo e desperdício

**Como** gerente de cozinha,  
**quero** registrar o consumo de água, energia e o desperdício de alimentos,  
**para** acompanhar os indicadores da operação ao longo do tempo.

#### Cenário BDD: Salvar um registro válido

    Funcionalidade: Registro de indicadores da cozinha

    Cenário: Salvar um registro válido
      Dado que o gerente está no formulário de registro
      Quando informa o consumo de água em litros
      E informa o consumo de energia em kWh
      E informa o desperdício de alimentos em kg
      E seleciona a data do registro
      E confirma o salvamento
      Então o sistema armazena os valores associados à data selecionada
      E apresenta uma confirmação de sucesso

#### Cenário BDD: Tentar salvar um registro incompleto

    Cenário: Faltam dados obrigatórios no registro
      Dado que o gerente está no formulário de registro
      E deixou um ou mais campos obrigatórios sem preencher
      Quando tenta salvar o registro
      Então o sistema não salva os dados
      E informa quais campos precisam ser preenchidos

### História 2.2 — Acompanhar metas e consultar dicas

**Como** gerente de cozinha,  
**quero** visualizar os indicadores em comparação com metas e consultar dicas operacionais,  
**para** acompanhar a evolução e orientar a equipe sobre práticas de baixo custo.

#### Cenário BDD: Consultar indicadores com registros disponíveis

    Funcionalidade: Acompanhamento de metas

    Cenário: Consultar indicadores com registros disponíveis
      Dado que existem registros de consumo e desperdício
      E há metas configuradas para os indicadores
      Quando o gerente acessa o painel de acompanhamento
      Então o sistema apresenta os valores registrados e as metas correspondentes
      E indica visualmente quais indicadores atingiram suas metas
      E apresenta dicas relacionadas a água, energia ou desperdício

#### Cenário BDD: Consultar o painel sem registros

    Cenário: Ainda não há dados registrados
      Dado que não existem registros de consumo ou desperdício
      Quando o gerente acessa o painel de acompanhamento
      Então o sistema informa que ainda não há dados disponíveis
      E orienta o gerente a registrar os primeiros indicadores

---

## Épico 3: A Teia de Sabores

**Tema:** Impacto Comunitário e Redefinição do Futuro

> Como responsável pelas compras e estoque do restaurante, quero visualizar produtores locais e entidades parceiras, para priorizar compras do bairro e destinar excedentes alimentares e resíduos de forma segura e legal.

### História 3.1 — Encontrar produtores locais

**Como** responsável pelas compras,  
**quero** pesquisar produtores locais por tipo de produto e localização,  
**para** encontrar fornecedores próximos para o restaurante.

#### Cenário BDD: Filtrar produtores por produto e distância

    Funcionalidade: Busca de produtores locais

    Cenário: Filtrar produtores por produto e distância
      Dado que o responsável acessou a área de produtores
      E existem produtores cadastrados com localização e produtos disponíveis
      Quando seleciona uma categoria de produto
      E informa um raio de busca
      Então o sistema apresenta os produtores que correspondem aos filtros
      E mostra a distância e as informações de contato de cada produtor

#### Cenário BDD: Nenhum produtor corresponde à busca

    Cenário: Busca sem resultados
      Dado que o responsável acessou a área de produtores
      Quando aplica filtros que não correspondem a nenhum produtor cadastrado
      Então o sistema informa que nenhum produtor foi encontrado
      E permite alterar os filtros da busca

### História 3.2 — Encontrar entidades para destinação

**Como** responsável pelo estoque,  
**quero** localizar entidades que recebam doações de alimentos ou resíduos,  
**para** destinar excedentes de forma adequada.

#### Cenário BDD: Consultar entidades por tipo de destinação

    Funcionalidade: Busca de entidades parceiras

    Cenário: Consultar entidades por tipo de destinação
      Dado que o responsável acessou a área de entidades parceiras
      E existem entidades cadastradas com tipos de destinação aceitos
      Quando seleciona uma categoria, como doação de alimentos ou compostagem
      Então o sistema apresenta as entidades compatíveis
      E exibe informações de contato, localização e condições de recebimento

#### Cenário BDD: Nenhuma entidade compatível é encontrada

    Cenário: Busca de entidades sem resultados
      Dado que o responsável selecionou um tipo de destinação
      Quando não existem entidades cadastradas compatíveis com essa categoria
      Então o sistema informa que nenhuma entidade foi encontrada
      E permite consultar outras categorias de destinação

---

## Épico 4: O Passaporte de Sabores

**Tema:** Transparência, Reconhecimento e Conexão com o Cliente

> Como dono do restaurante, quero disponibilizar um QR Code dinâmico no cardápio ou nas mesas, para mostrar a origem dos ingredientes e as ações sustentáveis do estabelecimento diretamente ao cliente final.

### História 4.1 — Cadastrar o passaporte do restaurante

**Como** dono de um restaurante,  
**quero** cadastrar a história do estabelecimento e suas ações sustentáveis,  
**para** apresentar aos clientes informações sobre o restaurante e seu impacto.

#### Cenário BDD: Cadastrar um passaporte válido

    Funcionalidade: Cadastro do passaporte de sabores

    Cenário: Dono cadastra as informações do restaurante
      Dado que o dono está autenticado na plataforma
      Quando informa o nome do restaurante
      E informa a história do estabelecimento
      E informa suas ações de impacto comunitário e sustentabilidade
      E salva o cadastro
      Então o sistema cria um passaporte para o restaurante
      E disponibiliza uma página pública com as informações cadastradas

#### Cenário BDD: Tentar cadastrar sem as informações obrigatórias

    Cenário: Nome ou história não foram informados
      Dado que o dono está preenchendo o cadastro do passaporte
      E deixou o nome do restaurante ou a história sem preencher
      Quando tenta salvar o cadastro
      Então o sistema não cria o passaporte
      E informa quais campos obrigatórios precisam ser preenchidos

### História 4.2 — Cadastrar a origem dos ingredientes

**Como** dono de um restaurante,  
**quero** cadastrar os ingredientes utilizados e suas origens,  
**para** mostrar aos clientes de onde vêm os produtos servidos.

#### Cenário BDD: Adicionar um ingrediente ao passaporte

    Funcionalidade: Cadastro da origem dos ingredientes

    Cenário: Dono cadastra um ingrediente válido
      Dado que existe um passaporte cadastrado para o restaurante
      Quando informa o nome do ingrediente
      E informa sua origem e fornecedor
      E salva o cadastro
      Então o ingrediente fica associado ao passaporte do restaurante
      E suas informações ficam disponíveis na página pública do passaporte

#### Cenário BDD: Cliente consulta os ingredientes

    Cenário: Exibir a origem dos ingredientes cadastrados
      Dado que o passaporte público do restaurante está ativo
      E existem ingredientes cadastrados
      Quando o cliente acessa o passaporte
      Então o sistema apresenta os ingredientes cadastrados
      E exibe a origem e o fornecedor de cada ingrediente
      E apresenta a descrição, caso tenha sido informada

### História 4.3 — Acessar o passaporte por QR Code

**Como** cliente do restaurante,  
**quero** acessar o passaporte de sabores por meio de um QR Code,  
**para** consultar a origem dos ingredientes e as ações sustentáveis do estabelecimento.

#### Cenário BDD: Cliente acessa um passaporte ativo pelo QR Code

    Funcionalidade: Acesso ao passaporte por QR Code

    Cenário: QR Code direciona para o passaporte do restaurante
      Dado que o restaurante possui um passaporte ativo
      E o QR Code está associado ao endereço público desse passaporte
      Quando o cliente escaneia o QR Code
      Então o sistema abre a página pública do passaporte
      E apresenta a história do restaurante
      E apresenta as informações de impacto e os ingredientes cadastrados

#### Cenário BDD: Cliente acessa um passaporte desativado

    Cenário: Passaporte não está ativo
      Dado que o QR Code aponta para um passaporte desativado
      Quando o cliente escaneia o QR Code
      Então o sistema não apresenta as informações do passaporte
      E exibe uma mensagem informando que a página não está disponível

### História 4.4 — Atualizar as informações do passaporte

**Como** dono de um restaurante,  
**quero** atualizar as informações do passaporte e dos ingredientes,  
**para** manter o conteúdo apresentado aos clientes correto e atualizado.

#### Cenário BDD: Atualizar informações existentes

    Funcionalidade: Atualização do passaporte

    Cenário: Dono atualiza informações do restaurante
      Dado que o dono possui um passaporte cadastrado
      Quando altera uma informação do restaurante ou de um ingrediente
      E salva as alterações
      Então o sistema atualiza as informações do passaporte
      E apresenta os dados atualizados aos próximos clientes que acessarem a página

---

## Histórias selecionadas para implementação

Como o **Épico 1 está concluído**, estas três histórias dele foram selecionadas para implementação do **ENTREGÁVEL 3** de FDS:

1. **História 1.1 — Iniciar o diagnóstico**
2. **História 1.2 — Responder às perguntas do diagnóstico**
3. **História 1.4 — Visualizar o resultado do diagnóstico**
