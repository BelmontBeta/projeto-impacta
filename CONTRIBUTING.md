<!-- omit in toc -->
# Como contribuir com o projeto-impacta

Antes de tudo, obrigado por dedicar seu tempo para contribuir! ❤️

Todos os tipos de contribuição são bem-vindos e valorizados. Consulte o [sumário](#sumário) para conhecer as diferentes formas de ajudar e entender como o projeto recebe contribuições. Leia também as seções relevantes antes de enviar sua contribuição.

> Se você gosta do projeto, mas não tem tempo para contribuir, tudo bem! Há outras formas simples de apoiar e demonstrar seu apreço, e também ficaremos muito felizes com isso:
> - Dê uma estrela ao projeto.
> - Compartilhe o projeto nas redes sociais.
> - Mencione este projeto no README do seu projeto.
> - Apresente o projeto em encontros locais e conte a amigos e colegas.

<!-- omit in toc -->
## Sumário

- [Código de Conduta](#código-de-conduta)
- [Tenho uma dúvida](#tenho-uma-dúvida)
  - [Quero contribuir](#quero-contribuir)
  - [Relato de bugs](#relato-de-bugs)
  - [Sugestões de melhorias](#sugestões-de-melhorias)
  - [Sua primeira contribuição de código](#sua-primeira-contribuição-de-código)
  - [Como melhorar a documentação](#como-melhorar-a-documentação)
- [Guias de estilo](#guias-de-estilo)
  - [Mensagens de commit](#mensagens-de-commit)
- [Faça parte da equipe do projeto](#faça-parte-da-equipe-do-projeto)

## Código de Conduta

Este projeto e todas as pessoas que participam dele são regidos pelo
[Código de Conduta do projeto-impacta](https://github.com/BelmontBeta/projeto-impacta/blob/main/CODE_OF_CONDUCT.md).
Ao participar, espera-se que você siga esse código. Relate comportamentos inaceitáveis para <>.

## Tenho uma dúvida

> Se você quer fazer uma pergunta, presumimos que já consultou a [documentação disponível](https://github.com/BelmontBeta/projeto-impacta/blob/main/README.md).

Antes de perguntar, recomendamos buscar [issues existentes](https://github.com/BelmontBeta/projeto-impacta/issues) que possam ajudar. Se encontrar uma issue adequada e ainda precisar de esclarecimentos, comente nela em vez de abrir uma nova.

Se ainda precisar fazer uma pergunta ou pedir esclarecimentos, recomendamos:

- Abra uma [issue](https://github.com/BelmontBeta/projeto-impacta/issues/new).
- Forneça o máximo de contexto possível sobre o problema ou a dúvida.
- Informe as versões do projeto e da plataforma (Node.js, npm etc.), conforme for relevante.

A equipe cuidará da solicitação assim que possível.

<!--
Você pode criar um rótulo específico para dúvidas e incluí-lo nesta descrição, para que as pessoas o usem nas issues.

Dependendo do tamanho do projeto, você também pode direcionar as perguntas para outros canais, como Stack Overflow ou Gitter. Outras possibilidades de contato e informação incluem:
- IRC
- Slack
- Gitter
- Tag no Stack Overflow
- Blog
- FAQ
- Roadmap
- Lista de e-mails
- Fórum
-->

## Quero contribuir

> ### Aviso legal <!-- omit in toc -->
> Ao contribuir com este projeto, você concorda que é autor(a) de 100% do conteúdo enviado, que possui os direitos necessários sobre ele e que o conteúdo pode ser disponibilizado sob a mesma licença do projeto.

### Relato de bugs

<!-- omit in toc -->
#### Antes de enviar um relato de bug

Um bom relato de bug deve conter informações suficientes para que outras pessoas possam entender e investigar o problema sem precisar buscar detalhes adicionais. Por isso, pedimos que você pesquise com cuidado, reúna as informações relevantes e descreva o problema em detalhes no relato.

- Verifique se está usando a versão mais recente.
- Confirme que o problema é realmente um bug, e não um erro de configuração ou incompatibilidade de componentes/versões do ambiente. Consulte a [documentação](https://github.com/BelmontBeta/projeto-impacta/blob/main/README.md).
- Verifique se outras pessoas já relataram ou resolveram o mesmo problema na [lista de issues](https://github.com/BelmontBeta/projeto-impacta/issues).
- Pesquise também na internet, inclusive no Stack Overflow, para saber se pessoas fora da comunidade do GitHub já discutiram o problema.
- Reúna informações sobre o bug:
  - Rastreamento da pilha (stack trace/traceback).
  - Sistema operacional, plataforma e versão (Windows, Linux, macOS, x86, ARM).
  - Versões do interpretador, compilador, SDK, ambiente de execução ou gerenciador de pacotes, conforme relevante.
  - Entradas fornecidas e resultados obtidos, se aplicável.
  - Se é possível reproduzir o problema de forma confiável e se ele também ocorre em versões anteriores.

<!-- omit in toc -->
#### Como enviar um bom relato de bug?

> Nunca relate publicamente, na lista de issues ou em qualquer outro lugar, problemas de segurança, vulnerabilidades ou bugs que incluam informações sensíveis. Em vez disso, envie relatos sensíveis por e-mail para <>.
<!-- Você também pode adicionar uma chave PGP para permitir o envio de mensagens criptografadas. -->

Usamos as issues do GitHub para acompanhar bugs e erros. Se você encontrar um problema no projeto:

- Abra uma [issue](https://github.com/BelmontBeta/projeto-impacta/issues/new). Como ainda não é possível saber se o caso é realmente um bug, descreva o problema sem atribuir um rótulo; a equipe fará a triagem.
- Explique qual comportamento esperava e qual comportamento ocorreu de fato.
- Forneça o máximo de contexto possível e descreva as *etapas para reproduzir* o problema, de modo que outra pessoa consiga reproduzi-lo. Um bom relato de bug deve incluir um exemplo de código que possa ser copiado e executado, quando aplicável.
- Inclua as informações reunidas na seção anterior.

Depois que a issue for aberta:

- A equipe do projeto adicionará os rótulos adequados.
- Uma pessoa da equipe tentará reproduzir o problema com as etapas fornecidas. Se não houver etapas ou não for possível identificar como reproduzi-lo, a equipe solicitará mais informações e marcará a issue como `needs-info`.
- Se a equipe conseguir reproduzir o problema, a issue será marcada como `needs-fix` e poderá receber outros rótulos (como `critical`). Em seguida, ficará disponível para ser [implementada por alguém](#sua-primeira-contribuição-de-código).

<!-- Você pode criar um modelo de issue para bugs e erros como guia e para definir quais informações devem ser incluídas. Se fizer isso, mencione-o aqui. -->

### Sugestões de melhorias

Esta seção orienta como enviar sugestões de melhorias para o projeto-impacta, **incluindo funcionalidades totalmente novas e pequenas melhorias em recursos existentes**. Seguir estas orientações ajuda a equipe a entender sua sugestão e decidir como encaminhá-la.

<!-- omit in toc -->
#### Antes de enviar uma sugestão de melhoria

- Verifique se está usando a versão mais recente.
- Leia com atenção a [documentação](https://github.com/BelmontBeta/projeto-impacta/blob/main/README.md) e confira se a funcionalidade já está disponível, talvez por meio de alguma configuração.
- Faça uma [busca nas issues](https://github.com/BelmontBeta/projeto-impacta/issues) para verificar se a melhoria já foi sugerida. Se já tiver sido, comente na issue existente em vez de abrir outra.
- Avalie se a ideia está de acordo com o escopo e os objetivos do projeto. Cabe a você apresentar argumentos que convençam as pessoas responsáveis pelo desenvolvimento do valor da funcionalidade. Lembre-se de que queremos atender a maioria das pessoas usuárias, não apenas um grupo pequeno.

<!-- omit in toc -->
#### Como enviar uma boa sugestão de melhoria?

As sugestões de melhorias são acompanhadas por meio de [issues do GitHub](https://github.com/BelmontBeta/projeto-impacta/issues).

- Use um **título claro e descritivo** para identificar a sugestão.
- Descreva a melhoria proposta passo a passo e com o máximo de detalhes possível.
- **Descreva o comportamento atual e explique qual comportamento você esperava e por quê.** Você também pode mencionar alternativas que não funcionaram.
- Se possível, **inclua capturas de tela ou gravações** que demonstrem as etapas ou indiquem a parte relacionada à sugestão. Você pode usar o [LICEcap](https://www.cockos.com/licecap/).
- **Explique por que essa melhoria seria útil para a maioria das pessoas que usam o projeto-impacta.** Você também pode mencionar outros projetos que resolveram o problema de uma forma que sirva de inspiração.

<!-- Você pode criar um modelo de issue para sugestões de melhorias como guia. Se fizer isso, mencione-o aqui. -->

### Sua primeira contribuição de código
<!-- TODO
Inclua instruções de configuração do ambiente, IDE e orientações para começar.
-->

### Como melhorar a documentação
<!-- TODO
Adicione orientações para atualizar, melhorar e corrigir a documentação.
-->

## Guias de estilo

### Mensagens de commit
<!-- TODO
Defina aqui as convenções para mensagens de commit.
-->

## Faça parte da equipe do projeto
<!-- TODO -->

<!-- omit in toc -->
## Agradecimentos

Este guia é baseado no [contributing.md](https://contributing.md/generator)!
