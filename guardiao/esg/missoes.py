"""Missões do plano de ação.

Cada missão tem o mesmo id da pergunta que a origina.
Todas são de baixo custo e não exigem consultoria.

Campos:
- titulo / como_fazer / custo / beneficio: texto completo (tela da missão);
- resumo / tempo / custo_rotulo: versão curta exibida nos cartões do plano.
"""

missoes = {
    # ---------------- Ambiental ----------------
    "agua": {
        "titulo": "Acompanhar o consumo de água",
        "resumo": "Anote toda semana a leitura do hidrômetro ou o valor da conta de água.",
        "como_fazer": "Toda segunda-feira, anote a leitura do hidrômetro (ou o valor da conta) em um caderno ou planilha.",
        "tempo": "5 min/sem.",
        "custo": "Zero",
        "custo_rotulo": "R$ 0",
        "beneficio": "Descobrir vazamentos e desperdícios, reduzindo a conta.",
    },
    "desperdicio": {
        "titulo": "Pesar o desperdício de comida por 7 dias",
        "resumo": "Separe um recipiente e anote os alimentos descartados diariamente.",
        "como_fazer": "Deixe uma balança e um balde de descarte na cozinha. Anote ao fim do dia o peso e o motivo (sobra, validade, erro).",
        "tempo": "5 min/dia",
        "custo": "Zero a baixo (balança simples)",
        "custo_rotulo": "Até R$ 50",
        "beneficio": "Enxergar onde o dinheiro está indo para o lixo e ajustar compras e porções.",
    },
    "energia": {
        "titulo": "Fazer a ronda da energia",
        "resumo": "Ao fechar, confira luzes e equipamentos ligados sem necessidade.",
        "como_fazer": "Ao fechar, confira luzes, ar-condicionado e equipamentos ligados sem uso. Anote o valor da conta de luz todo mês.",
        "tempo": "5 min/dia",
        "custo": "Zero",
        "custo_rotulo": "R$ 0",
        "beneficio": "Cortar gasto fixo sem mexer na qualidade do serviço.",
    },
    "residuos": {
        "titulo": "Separar o lixo em dois recipientes",
        "resumo": "Lixeiras identificadas para reciclável e lixo comum.",
        "como_fazer": "Coloque uma lixeira para recicláveis (papel, plástico, vidro, metal) e outra para o resto. Combine com a equipe quem leva para a coleta.",
        "tempo": "1h para org.",
        "custo": "Baixo (uma lixeira extra)",
        "custo_rotulo": "Até R$ 50",
        "beneficio": "Menos lixo comum e uma rotina de limpeza mais organizada.",
    },
    "oleo": {
        "titulo": "Guardar o óleo usado para coleta",
        "resumo": "Guarde o óleo usado em garrafa PET e leve a um ponto de coleta.",
        "como_fazer": "Armazene o óleo frio em garrafa PET e procure um ponto de coleta ou cooperativa da sua cidade que recolha.",
        "tempo": "10 min/sem.",
        "custo": "Zero",
        "custo_rotulo": "R$ 0",
        "beneficio": "Evita entupimento e poluição, e pode render parceria de coleta.",
    },
    "embalagens": {
        "titulo": "Revisar as embalagens das entregas",
        "resumo": "Liste o que vai em cada pedido e retire o que for excesso.",
        "como_fazer": "Liste o que vai em cada pedido (talheres, sachês, sacolas). Pergunte ao cliente se quer talheres e retire o que for excesso.",
        "tempo": "30 min",
        "custo": "Zero (pode até economizar)",
        "custo_rotulo": "R$ 0",
        "beneficio": "Menos custo com descartáveis e mais valor para clientes preocupados com o meio ambiente.",
    },

    # ---------------- Social ----------------
    "fornecedores_locais": {
        "titulo": "Testar um fornecedor local",
        "resumo": "Liste feiras e produtores próximos que forneçam ingredientes frescos.",
        "como_fazer": "Escolha 1 ou 2 itens do cardápio (hortaliças, ovos, pães) e peça orçamento a produtores da região.",
        "tempo": "30 min",
        "custo": "Zero",
        "custo_rotulo": "R$ 0",
        "beneficio": "Ingredientes mais frescos, menos transporte e fortalecimento da comunidade.",
    },
    "regras_equipe": {
        "titulo": "Escrever regras básicas de trabalho",
        "resumo": "Escreva horários, funções e regras de convivência e afixe na cozinha.",
        "como_fazer": "Em uma folha, anote horários, funções, regras de higiene e de convivência. Converse com a equipe e deixe afixado na cozinha.",
        "tempo": "1h",
        "custo": "Zero",
        "custo_rotulo": "R$ 0",
        "beneficio": "Menos conflitos e uma equipe que sabe o que se espera dela.",
    },
    "entregadores": {
        "titulo": "Conferir pagamento e segurança da equipe",
        "resumo": "Defina datas fixas de pagamento e pergunte o que falta à equipe.",
        "como_fazer": "Defina datas fixas de pagamento e pergunte a entregadores e funcionários o que falta (equipamento de proteção, local de descanso).",
        "tempo": "30 min",
        "custo": "Baixo",
        "custo_rotulo": "Até R$ 50",
        "beneficio": "Equipe mais estável, menos rotatividade e menor risco de problemas trabalhistas.",
    },
    "reuniao_equipe": {
        "titulo": "Fazer uma conversa mensal de 15 minutos",
        "resumo": "Reserve 15 minutos por mês para ouvir a equipe.",
        "como_fazer": "Reserve 15 minutos no mesmo dia todo mês. Pergunte: o que está funcionando, o que atrapalha e uma ideia de melhoria.",
        "tempo": "15 min/mês",
        "custo": "Zero",
        "custo_rotulo": "R$ 0",
        "beneficio": "Ideias que reduzem erros e desperdício, e uma equipe mais engajada.",
    },
    "canal_clientes": {
        "titulo": "Abrir um canal simples de feedback",
        "resumo": "Coloque um QR code ou WhatsApp na embalagem para receber feedback.",
        "como_fazer": "Coloque um QR code ou um número de WhatsApp na embalagem para reclamações e elogios. Responda em até 2 dias.",
        "tempo": "30 min",
        "custo": "Zero",
        "custo_rotulo": "R$ 0",
        "beneficio": "Resolver problemas antes de virarem má avaliação e saber o que os clientes valorizam.",
    },

    # ---------------- Governança ----------------
    "financeiro": {
        "titulo": "Registrar receitas e despesas",
        "resumo": "Registre entradas e saídas semanalmente em uma planilha simples.",
        "como_fazer": "Use uma planilha ou caderno e anote tudo que entra e sai, no mesmo dia. Separe a conta pessoal da conta do restaurante.",
        "tempo": "15 min/sem.",
        "custo": "Zero",
        "custo_rotulo": "R$ 0",
        "beneficio": "Saber de verdade se o negócio dá lucro e onde cortar custos.",
    },
    "metas": {
        "titulo": "Definir uma meta simples e medível",
        "resumo": "Escolha uma meta para 3 meses e anote o ponto de partida.",
        "como_fazer": "Escolha uma meta para os próximos 3 meses, como reduzir o desperdício de comida em 10%, e anote o ponto de partida.",
        "tempo": "20 min",
        "custo": "Zero",
        "custo_rotulo": "R$ 0",
        "beneficio": "Dá direção ao esforço e permite comemorar resultados reais.",
    },
    "formalizacao": {
        "titulo": "Regularizar a documentação do negócio",
        "resumo": "Confira CNPJ/MEI, alvará e a emissão de nota fiscal.",
        "como_fazer": "Verifique CNPJ/MEI, alvará e licença sanitária. O Sebrae e a prefeitura orientam gratuitamente. Emita nota fiscal nas vendas.",
        "tempo": "2h",
        "custo": "Baixo (taxas oficiais)",
        "custo_rotulo": "Taxas oficiais",
        "beneficio": "Evita multas, abre acesso a crédito e passa confiança para clientes e parceiros.",
    },
    "estoque": {
        "titulo": "Criar um controle de estoque e validade",
        "resumo": "Etiquete os itens com a validade e conte o estoque toda semana.",
        "como_fazer": "Etiquete os itens com a data de abertura e validade, use a regra 'o que vence primeiro sai primeiro' e faça uma contagem semanal.",
        "tempo": "30 min/sem.",
        "custo": "Baixo (etiquetas e caneta)",
        "custo_rotulo": "Até R$ 50",
        "beneficio": "Menos comida jogada fora e compras mais certeiras.",
    },
    "acompanhamento": {
        "titulo": "Revisar os resultados todo mês",
        "resumo": "No início do mês, compare vendas, custos e sobras com o mês anterior.",
        "como_fazer": "No primeiro dia útil, olhe vendas, custos e sobras do mês anterior e compare com o mês retrasado. Anote uma decisão.",
        "tempo": "30 min/mês",
        "custo": "Zero",
        "custo_rotulo": "R$ 0",
        "beneficio": "Decisões com base em dados, e não só na intuição.",
    },
}
