"""Regras do diagnóstico em um só lugar.

Para ajustar a pontuação, os níveis ou o tamanho do plano de ação,
basta mexer neste arquivo.
"""

# Cada resposta vale de 0 a 3 pontos.
PONTOS_MAXIMO = 3

# Respostas com 0 ou 1 ponto viram missão no plano de ação.
LIMITE_RESPOSTA_BAIXA = 1

# Quantidade máxima de missões (uma por semana).
MAX_MISSOES = 4

# Opções de resposta, na ordem dos pontos (0, 1, 2, 3).
ESCALAS = {
    "frequencia": ["Nunca faço isso", "Faço às vezes", "Faço com frequência", "Faço sempre"],
    "existencia": [
        "Não tenho",
        "Estou começando",
        "Tenho, mas não acompanho",
        "Tenho e acompanho",
    ],
}

# Identidade visual e descrição de cada pilar.
PILARES = {
    "Ambiental": {
        "letra": "E",
        "classe": "ambiental",
        "descricao": "Consumo de energia, água, resíduos e desperdício de alimentos.",
    },
    "Social": {
        "letra": "S",
        "classe": "social",
        "descricao": "Relação com equipe, fornecedores locais e comunidade ao redor.",
    },
    "Governança": {
        "letra": "G",
        "classe": "governanca",
        "descricao": "Processos, finanças e comunicação com clientes.",
    },
}

# Níveis de maturidade, do mais baixo ao mais alto.
# "limite" é o percentual máximo (inclusive) que ainda pertence ao nível.
NIVEIS = [
    {
        "limite": 25,
        "nome": "Inicial",
        "classe": "inicial",
        "explicacao": "Você está no começo. Pequenos passos já vão fazer diferença.",
        "frase_geral": "Todo começo conta — comece pelas ações mais simples.",
        "frase_pilar": "Comece por uma ação simples para sair do lugar.",
    },
    {
        "limite": 50,
        "nome": "Em Desenvolvimento",
        "classe": "desenvolvimento",
        "explicacao": "Você já tem boas práticas, mas muitas ainda sem registro ou rotina.",
        "frase_geral": "Boa base — foque nas oportunidades para avançar.",
        "frase_pilar": "Boa base — algumas ações podem acelerar o progresso.",
    },
    {
        "limite": 75,
        "nome": "Estruturado",
        "classe": "estruturado",
        "explicacao": "Suas práticas estão organizadas. Falta acompanhar os resultados.",
        "frase_geral": "Práticas organizadas — falta acompanhar os resultados.",
        "frase_pilar": "Práticas organizadas. Acompanhar os números é o próximo passo.",
    },
    {
        "limite": 100,
        "nome": "Avançado",
        "classe": "avancado",
        "explicacao": "Você mantém boas práticas e acompanha os resultados. Continue assim!",
        "frase_geral": "Excelente! Continue acompanhando e refaça o diagnóstico em 3 meses.",
        "frase_pilar": "Excelente desempenho. Continue acompanhando.",
    },
]
