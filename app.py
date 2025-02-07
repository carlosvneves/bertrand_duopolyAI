import streamlit as st
import numpy as np
from scipy.optimize import fsolve
import plotly.graph_objects as go
from sabm.utils import ModelType, BackendType
def simulate_duopoly(a, b1, b2, d12, d21, c1, c2, num_iterations, p1_init, p2_init):
    """
    Simula o modelo de duopólio de Bertrand e retorna figuras Plotly para a dinâmica competitiva e o diagrama de fase,
    juntamente com um resumo textual dos preços de equilíbrio.

    Parâmetros:
        a (float): Parâmetro de demanda base.
        b1 (float): Sensibilidade ao preço próprio da Empresa 1.
        b2 (float): Sensibilidade ao preço próprio da Empresa 2.
        d12 (float): Efeito cruzado de preço: da Empresa 2 sobre a Empresa 1.
        d21 (float): Efeito cruzado de preço: da Empresa 1 sobre a Empresa 2.
        c1 (float): Custo marginal da Empresa 1.
        c2 (float): Custo marginal da Empresa 2.
        num_iterations (int): Número de iterações para a simulação da dinâmica competitiva.
        p1_init (float): Preço inicial da Empresa 1.
        p2_init (float): Preço inicial da Empresa 2.

    Retorna:
        fig1 (plotly.graph_objects.Figure): Figura mostrando a dinâmica competitiva.
        fig2 (plotly.graph_objects.Figure): Figura mostrando o diagrama de fase.
        text_output (str): Resumo textual dos preços de equilíbrio ou mensagens de erro.        
    """

    # -----------------------------
    # Verificação de Estabilidade
    # -----------------------------
    if b1 <= d12 or b2 <= d21:
        error_msg = ("Condição de estabilidade violada: b1 deve ser maior que d12 e "
                     "b2 deve ser maior que d21.")
        return None, None, error_msg

    # -----------------------------
    # Simulação da Dinâmica Competitiva
    # -----------------------------
    p1_history = [p1_init]
    p2_history = [p2_init]
    p1, p2 = p1_init, p2_init

    def best_response_firm1(p2_val):
        return (a + d12 * p2_val + b1 * c1) / (2 * b1)

    def best_response_firm2(p1_val):
        return (a + d21 * p1_val + b2 * c2) / (2 * b2)

    for i in range(num_iterations):
        p1_new = best_response_firm1(p2)
        p2_new = best_response_firm2(p1)
        p1, p2 = p1_new, p2_new  # Atualização simultânea
        p1_history.append(p1)
        p2_history.append(p2)

    competitive_p1, competitive_p2 = p1_history[-1], p2_history[-1]

    # -----------------------------
    # Cálculo do Resultado Colusivo
    # -----------------------------
    def collusive_focs(prices):
        p1_val, p2_val = prices
        eq1 = a + b1 * c1 + d12 * p2_val - 2 * b1 * p1_val + d21 * (p2_val - c2)
        eq2 = a + b2 * c2 + d21 * p1_val + d12 * (p1_val - c1) - 2 * b2 * p2_val
        return [eq1, eq2]

    initial_guess = [competitive_p1, competitive_p2]
    collusive_solution, infodict, ier, mesg = fsolve(collusive_focs, initial_guess, full_output=True)
    if ier != 1:
        text_output = "fsolve não convergiu para uma solução. Mensagem: " + mesg
        collusive_p1, collusive_p2 = None, None
    else:
        collusive_p1, collusive_p2 = collusive_solution
        text_output = (
            f"Preços de Equilíbrio Competitivo:\n"
            f"  Empresa 1: {competitive_p1:.2f}\n"
            f"  Empresa 2: {competitive_p2:.2f}\n\n"
            f"Preços do Resultado Colusivo:\n"
            f"  Empresa 1: {collusive_p1:.2f}\n"
            f"  Empresa 2: {collusive_p2:.2f}"
        )

    # -----------------------------
    # Visualização com Plotly
    # -----------------------------
    iterations = np.arange(len(p1_history))

    ## Figura 1: Dinâmica Competitiva
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=iterations, y=p1_history, mode='lines+markers', name="Preço Competitivo - Empresa 1"))
    fig1.add_trace(go.Scatter(
        x=iterations, y=p2_history, mode='lines+markers', name="Preço Competitivo - Empresa 2"))

    # Linhas horizontais para os equilíbrios
    fig1.add_hline(
        y=competitive_p1, line=dict(color='red', dash='dash'),
        annotation_text="Equilíbrio Competitivo - Empresa 1", annotation_position="top left")
    fig1.add_hline(
        y=competitive_p2, line=dict(color='red', dash='dot'),
        annotation_text="Equilíbrio Competitivo - Empresa 2", annotation_position="bottom left")
    if collusive_p1 is not None and collusive_p2 is not None:
        fig1.add_hline(
            y=collusive_p1, line=dict(color='green', dash='dash'),
            annotation_text="Resultado Colusivo - Empresa 1", annotation_position="top right")
        fig1.add_hline(
            y=collusive_p2, line=dict(color='green', dash='dot'),
            annotation_text="Resultado Colusivo - Empresa 2", annotation_position="bottom right")

    fig1.update_layout(
        title="Dinâmica Competitiva de Resposta Ótima no Duopólio de Bertrand",
        xaxis_title="Iteração",
        yaxis_title="Preço",
        template="plotly_white"
    )

    ## Figura 2: Diagrama de Fase
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=p1_history, y=p2_history, mode='lines+markers', name="Trajetória"))
    fig2.add_trace(go.Scatter(
        x=[competitive_p1], y=[competitive_p2],
        mode='markers', marker=dict(color='red', size=12),
        name="Equilíbrio Competitivo"))
    if collusive_p1 is not None and collusive_p2 is not None:
        fig2.add_trace(go.Scatter(
            x=[collusive_p1], y=[collusive_p2],
            mode='markers', marker=dict(color='green', size=12),
            name="Resultado Colusivo"))

    fig2.update_layout(
        title="Diagrama de Fase: Preço da Empresa 1 vs. Preço da Empresa 2 (Dinâmica Competitiva)",
        xaxis_title="Preço da Empresa 1",
        yaxis_title="Preço da Empresa 2",
        template="plotly_white"
    )

    return fig1, fig2, text_output

def model_opts_component(backend_option):
    # pull down menu to select the model
    if backend_option == BackendType.LocalOllama.name:
        opts = (
                ModelType.Deepseek_r1_1dot5b_Distill_Qwen.name,
                ModelType.Deepseek_r1_8b_Distill_Llama.name,
                ModelType.Mistral_7b.name)
    elif backend_option == BackendType.OnlineMistral.name:
        opts = (
                ModelType.Mistral_large.name, 
                ModelType.Mistral_small.name) 
    elif backend_option == BackendType.OnlineGroq.name:
        opts = (
                ModelType.Deepseek_r1_70b_Distill_Llama.name,
                ModelType.Llama_3dot3_70b_versatile.name)
    elif backend_option == BackendType.OnlineGoogle.name:
        opts = (ModelType.Gemini_2dot0_flash_lite.name)
    else:
        opts = (ModelType.MaritacaAI.name)
    
    model_option = st.selectbox(
        "Selecione o modelo :bulb:",
        opts,
        index=0
    )
    return model_option

def model_opts_backend():
    # pull down menu to select the model
    backend_option = st.selectbox(
        "Selecione o backend :rocket:",
        (BackendType.LocalOllama.name,
         BackendType.OnlineMaritacaAI.name,
         BackendType.OnlineGroq.name,
         BackendType.OnlineGoogle.name,
         BackendType.OnlineMistral.name
        ),  
        index=0
        
    )
    return backend_option

def main():
    st.set_page_config(page_icon="💬", 
                   page_title="SABM",
                   layout= "wide"
                   )
    st.title("Simulação de Duopólio de Bertrand com Plotly")
    st.write(
        """
        Esta aplicação interativa simula o modelo de duopólio de Bertrand.
        Ajuste os parâmetros na barra lateral para observar as dinâmicas competitivas e o diagrama de fase em tempo real.
        
        **Referências:**
        - [Documentação do Streamlit](https://docs.streamlit.io/)
        - [Biblioteca Plotly](https://plotly.com/python/)
        - [SciPy Optimize](https://docs.scipy.org/doc/scipy/reference/optimize.html)
        """
    )

    # -----------------------------
    # Barra Lateral para Entradas do Usuário
    # -----------------------------
    st.sidebar.header("Parâmetros do Modelo")

    a = st.sidebar.slider("Parâmetro a (Demanda Base)", 0.0, 30.0, 14.0, step=0.1)
    b1 = st.sidebar.slider("b1 (Sensibilidade ao Preço Próprio - Empresa 1)", 0.1, 5.0, 2.0, step=0.1)
    b2 = st.sidebar.slider("b2 (Sensibilidade ao Preço Próprio - Empresa 2)", 0.1, 5.0, 2.0, step=0.1)
    d12 = st.sidebar.slider("d12 (Efeito Cruzado: Empresa 2 sobre Empresa 1)", 0.0, 5.0, 1.0, step=0.1)
    d21 = st.sidebar.slider("d21 (Efeito Cruzado: Empresa 1 sobre Empresa 2)", 0.0, 5.0, 1.0, step=0.1)
    c1 = st.sidebar.slider("c1 (Custo Marginal - Empresa 1)", 0.0, 10.0, 2.0, step=0.1)
    c2 = st.sidebar.slider("c2 (Custo Marginal - Empresa 2)", 0.0, 10.0, 2.0, step=0.1)
    num_iterations = st.sidebar.slider("Número de Iterações", 10, 100, 50, step=1)
    p1_init = st.sidebar.slider("Preço Inicial p1 (Empresa 1)", 0.1, 10.0, 0.1, step=0.1)
    p2_init = st.sidebar.slider("Preço Inicial p2 (Empresa 2)", 0.1, 10.0, 0.1, step=0.1)

    tab_simple_model, tab_sabm_model = st.tabs(["Modelo Simples", "SABM"])
    
    with tab_simple_model:
        # Executa a simulação automaticamente sempre que os parâmetros são alterados
        fig1, fig2, text_output = simulate_duopoly(
            a, b1, b2, d12, d21, c1, c2, num_iterations, p1_init, p2_init
        )

        if fig1 is None or fig2 is None:
            st.error(text_output)
        else:
            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig2, use_container_width=True)
            st.text_area("Preços de Equilíbrio e Mensagens", text_output, height=200)
    
    with tab_sabm_model:
       backend_option = model_opts_backend()
       model_opts_component(backend_option)
       

if __name__ == "__main__":
    main()
