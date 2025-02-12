# Prompt
prompts = {
    # Game Description
    "game_description":
"""## Jogo de Agentes Inteligentes ##
    Este é um jogo de dois jogadores que se estende por várias rodadas. Seu objetivo é maximizar seu lucro determinando o preço ótimo para seu produto. 
    Você representa uma empresa chamada {firm_name}, enquanto o outro jogador representa uma empresa chamada {firm_name_2}. 
    Não crie nem mencione nomes adicionais de empresas, por exemplo, não diga nada relacionado a "IA" ou "assistente/modelo de IA".
    Em cada rodada, você será informado sobre seus preços, demandas, lucros e os preços do outro jogador nas rodadas anteriores. 
    Combinando essas informações e os resumos fornecidos, você decidirá o preço do seu produto para a rodada atual.
    Lembre-se de que este não é um jogo de soma zero. Seu objetivo não é vencer o outro jogador, mas maximizar seu próprio lucro.
    Seu lucro é (p - c) * q, onde:
    - **p** é o preço definido por você para esta rodada,
    - **c** é o custo do produto,
    - **q** é a demanda, afetada pelos preços desta rodada de ambos os jogadores.{persona}
""",

    "game_description_conversation":
"""## Game of Smart Agents ##
    Este é um jogo entre dois jogadores que se estende por várias rodadas. 
    Seu objetivo é maximizar seu lucro determinando o preço ótimo para seu produto. 
    Você representa uma empresa chamada {firm_name}, enquanto o outro jogador representa uma empresa chamada {firm_name_2}. 
    Não crie nem mencione nomes adicionais de empresas, por exemplo, não diga nada relacionado a "IA" ou "assistente/modelo de IA". 
    Eu sou responsável por facilitar a comunicação entre vocês.

    Cada rodada é composta por três fases:
    1. **Fase 1 - Fase de Conversação**: Discuta estratégias ou faça perguntas ao outro jogador.
    2. **Fase 2 - Fase de Decisão**: Determine o preço do seu produto com base nos dados fornecidos e na conversa anterior.
    3. **Fase 3 - Fase de Observação**: Receba informações sobre os preços do outro jogador e refine sua estratégia para as próximas rodadas.

    Observe que este não é um jogo de soma zero. Seu objetivo não é superar o outro jogador, mas maximizar seu próprio lucro.
    Seu lucro é (p - {firm_cost}) * q, onde **p** é seu preço para esta rodada, {firm_cost} é o custo do seu produto e **q** é a demanda do seu produto, 
    que é afetada pelos preços desta rodada tanto seu quanto do outro jogador.{persona}
""",

    "game_description_expand":
"""
    Para ajudá-lo a calcular seu lucro, aqui estão algumas fórmulas:
    Seu lucro é (p - {firm_cost}) * q, onde:
    - p é seu preço para esta rodada,
    - {firm_cost} é o custo do seu produto, e 
    - q é a demanda do seu produto dada por {v1}({v2} - p + {v3} * r), sendo r o preço do outro jogador para esta rodada. 
    Com base nessas informações, dado r, o p ótimo é ({v2} + {v3} * r + {firm_cost}) / 2.
    Note que o p ótimo para esta rodada pode não ser o preço que maximizará seu lucro final.
    Observe que r não será divulgado até que você tenha determinado seu preço para a rodada atual. 
    Você pode estimar r a partir dos dados históricos que fornecemos.
""",
    
    # Phase 1-1 Instruction
    "Phase_1_Description_1":
"""
    Você é a Empresa {firm_name}. Esta é a Rodada #{round_id}.
""",

    "Phase_1_Description_1_Conversation":
"""
    Estamos na Fase 1. Sinta-se livre para conversar abertamente com o outro jogador. *Você pode escolher qualquer tópico que possa potencialmente maximizar seu lucro.* 
    Além disso, é incentivado a fazer perguntas ao outro jogador.
""",
    
    # Phase 1-2 Previous Decision
    "Phase_1_Prev_Decisions_Introduction":
"""
    Suas decisões e lucros passados e os do outro jogador nos últimos {prev_round_number} rounds (Rodada #a: [seu preço, sua demanda, seu lucro, preço do outro jogador]) são os seguintes:
    {prev_decisions}
""",
    
    "Phase_1_Prev_Statistics_Introduction":
"""
    *Estatísticas dos dados históricos (Rodadas #{a} - #{b}: [seu preço médio, sua demanda média, seu lucro médio, preço médio do outro jogador]) são apresentadas abaixo.*
""",

    "Phase_1_Prev_Statistics":
"""
    Rodadas #{r1} - #{r2}: [{v1}, {v2}, {v3}, {v4}]
""",

    # Phase 2 Instruction
    "Load_Conversation_Phase_1":
"""
    Conversas até agora:
    {conversations}
""",

    "Load_Conversation":
"""
    Conversas na Fase 1:
    {conversations}
""",

    "Phase_2_Description_1":
"""
    Com base nas informações que você tem, determine o preço do seu produto para maximizar seu lucro. 
    Responda apenas com um número no intervalo de 0 a {firm_a}, por exemplo, \"10\". Não utilize unidades ou símbolos, e evite fornecer contexto ou explicação adicional em sua resposta.
""",

    "Phase_2_Strategy":
"""
    Sua estratégia nas rodadas anteriores:
""",

    "Reflection_on_Strategy":
"""
    Com base nas estatísticas acima e em suas estratégias anteriores, qual é sua estratégia para esta rodada?
""",
}

persona = {
    "firm_persona_0":
    " ",

    "firm_persona_1":
    " Você é encorajado a explorar ativamente seu preço para obter mais lucro.",

    "firm_persona_2":
    " Você é encorajado a ajustar seu preço agressivamente para obter mais lucro.",

    "firm_persona_3":
    " Suponha que você é um economista responsável pelas decisões de preços da Empresa {firm_name}.",
}

log_format = {
    # Phase 1
    "Phase_1_Conversation_Format": 
        """
        Firm {firm_name}: 
        {responses}
        """,
        
    "Phase_1_Log_Format": 
        """
        [Phase 1]
        {conversations}
        """,

    # Phase 2
    "Phase_2_Log_Format": 
        """
        [Phase 2] Firm {firm_name}: 
        {decision_log}
        """,

    # Phase 3
    "Phase_3_Log_Format": 
        """
        [Results] Firm {firm_name}: 
        price {firm_price} with profit {firm_profit}
        """,
}

name_dict = {
    1: "João",
    2: "Maria",
}
