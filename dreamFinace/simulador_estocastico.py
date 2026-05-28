import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# Configuração da página para um estilo mais limpo e minimalista (Notion style)
st.set_page_config(
    page_title="Simulador Estocástico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada
# Removidos background-color rígidos para respeitar o tema Light/Dark nativo do Streamlit.
st.markdown("""
    <style>
    /* Fontes limpas parecidas com o Notion/Apple */
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Dicionário de ações (Principais Brasileiras + Americanas)
ACOES_DISPONIVEIS = {
    "ABEV3 - Ambev": "ABEV3.SA",
    "ALPA4 - Alpargatas": "ALPA4.SA",
    "ARZZ3 - Arezzo": "ARZZ3.SA",
    "ASAI3 - Assaí": "ASAI3.SA",
    "AZUL4 - Azul": "AZUL4.SA",
    "B3SA3 - B3": "B3SA3.SA",
    "BBAS3 - Banco do Brasil": "BBAS3.SA",
    "BBDC4 - Bradesco": "BBDC4.SA",
    "BBSE3 - BB Seguridade": "BBSE3.SA",
    "BPAC11 - BTG Pactual": "BPAC11.SA",
    "BRFS3 - BRF": "BRFS3.SA",
    "BRKM5 - Braskem": "BRKM5.SA",
    "CCRO3 - CCR": "CCRO3.SA",
    "CMIG4 - Cemig": "CMIG4.SA",
    "COGN3 - Cogna": "COGN3.SA",
    "CPFE3 - CPFL Energia": "CPFE3.SA",
    "CPLE6 - Copel": "CPLE6.SA",
    "CRFB3 - Carrefour Brasil": "CRFB3.SA",
    "CSAN3 - Cosan": "CSAN3.SA",
    "CSNA3 - CSN": "CSNA3.SA",
    "CVCB3 - CVC": "CVCB3.SA",
    "CYRE3 - Cyrela": "CYRE3.SA",
    "EGIE3 - Engie Brasil": "EGIE3.SA",
    "ELET3 - Eletrobras": "ELET3.SA",
    "EMBR3 - Embraer": "EMBR3.SA",
    "ENEV3 - Eneva": "ENEV3.SA",
    "EQTL3 - Equatorial": "EQTL3.SA",
    "EZTC3 - EZTEC": "EZTC3.SA",
    "FLRY3 - Fleury": "FLRY3.SA",
    "GGBR4 - Gerdau": "GGBR4.SA",
    "GOAU4 - Metalúrgica Gerdau": "GOAU4.SA",
    "GOLL4 - Gol": "GOLL4.SA",
    "HAPV3 - Hapvida": "HAPV3.SA",
    "HYPE3 - Hypera": "HYPE3.SA",
    "IGTI11 - Iguatemi": "IGTI11.SA",
    "ITSA4 - Itaúsa": "ITSA4.SA",
    "ITUB4 - Itaú Unibanco": "ITUB4.SA",
    "JBSS3 - JBS": "JBSS3.SA",
    "KLBN11 - Klabin": "KLBN11.SA",
    "LREN3 - Lojas Renner": "LREN3.SA",
    "MGLU3 - Magazine Luiza": "MGLU3.SA",
    "MRFG3 - Marfrig": "MRFG3.SA",
    "MRVE3 - MRV": "MRVE3.SA",
    "MULT3 - Multiplan": "MULT3.SA",
    "NTCO3 - Natura": "NTCO3.SA",
    "PCAR3 - Grupo Pão de Açúcar": "PCAR3.SA",
    "PETR3 - Petrobras (ON)": "PETR3.SA",
    "PETR4 - Petrobras (PN)": "PETR4.SA",
    "PETZ3 - Petz": "PETZ3.SA",
    "PRIO3 - Prio": "PRIO3.SA",
    "RADL3 - RaiaDrogasil": "RADL3.SA",
    "RAIL3 - Rumo": "RAIL3.SA",
    "RDOR3 - Rede D'Or": "RDOR3.SA",
    "RENT3 - Localiza": "RENT3.SA",
    "SANB11 - Santander Brasil": "SANB11.SA",
    "SBSP3 - Sabesp": "SBSP3.SA",
    "SLCE3 - SLC Agrícola": "SLCE3.SA",
    "SMTO3 - São Martinho": "SMTO3.SA",
    "SOMA3 - Grupo Soma": "SOMA3.SA",
    "SUZB3 - Suzano": "SUZB3.SA",
    "TAEE11 - Taesa": "TAEE11.SA",
    "TIMS3 - TIM": "TIMS3.SA",
    "TOTS3 - Totvs": "TOTS3.SA",
    "UGPA3 - Ultrapar": "UGPA3.SA",
    "USIM5 - Usiminas": "USIM5.SA",
    "VALE3 - Vale": "VALE3.SA",
    "VIVT3 - Vivo": "VIVT3.SA",
    "WEGE3 - WEG": "WEGE3.SA",
    "YDUQ3 - Yduqs": "YDUQ3.SA",
    
    # Adicionando opção manual para buscar QUALQUER ticker
    "🔍 OUTRA... (Digitar Ticker manualmente)": "OUTRO",
    
    # Opções americanas de destaque
    "AAPL - Apple (EUA)": "AAPL",
    "MSFT - Microsoft (EUA)": "MSFT",
    "GOOGL - Alphabet (EUA)": "GOOGL",
    "AMZN - Amazon (EUA)": "AMZN",
    "TSLA - Tesla (EUA)": "TSLA"
}

@st.cache_data(ttl=3600)
def baixar_dados(ticker):
    """
    Busca os dados históricos da ação usando o yfinance (últimos 6 meses).
    O decorator st.cache_data ajuda a evitar excesso de requisições à API.
    """
    try:
        dados = yf.download(ticker, period="6mo", progress=False)
        if dados.empty:
            return None
        
        # Acessar a coluna 'Close'
        fechamento = dados['Close'].dropna()
        
        # Lidar com o fato de que em novas versões do yfinance, 
        # o retorno pode ser um DataFrame multi-index mesmo para 1 ticker.
        if isinstance(fechamento, pd.DataFrame):
            fechamento = fechamento.squeeze()
            
        return fechamento
    except Exception as e:
        st.sidebar.error(f"Erro ao conectar com a API: {e}")
        return None

def simular_gbm(S0, mu, sigma, t, num_simulacoes):
    """
    Motor Matemático do Movimento Browniano Geométrico.
    
    Parâmetros:
    - S0: Preço inicial.
    - mu: Drift (Média diária dos retornos).
    - sigma: Volatilidade (Desvio padrão diário).
    - t: Horizonte de tempo (dias).
    - num_simulacoes: Quantidade de caminhos/futuros alternativos.
    """
    dt = 1 # Passo de tempo de 1 dia
    
    # Inicia a matriz de preços com zeros
    precos = np.zeros((t, num_simulacoes))
    precos[0] = S0 # Dia zero é o preço atual
    
    for i in range(1, t):
        # O núcleo estocástico: Gerando Z via Distribuição Normal Padrão
        Z = np.random.normal(0, 1, num_simulacoes)
        
        # Aplicando a equação de forma vetorizada (para todas as simulações simultaneamente)
        termo_drift = (mu - (sigma ** 2) / 2) * dt
        termo_choque = sigma * np.sqrt(dt) * Z
        
        precos[i] = precos[i-1] * np.exp(termo_drift + termo_choque)
        
    return precos

# ==========================================
# INTERFACE VISUAL (FRONT-END)
# ==========================================

# Título e subtítulo
st.title("Demonstrando a Reality com Processos Estocásticos Normais")
st.markdown("Uma visualização interativa do modelo de **Movimento Browniano Geométrico (GBM)** aplicado ao mercado de ações.")

# Barra lateral - Logomarca e Título Profissional (Alinhado à esquerda, fonte premium)
st.sidebar.markdown(
    "<h1 style='text-align: left; color: #ffffff; font-family: \"Georgia\", serif; letter-spacing: -0.5px;'>🏦 Dream Finance</h1>", 
    unsafe_allow_html=True
)
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Configurações do Modelo")

# Descobrindo o índice da PETR4 para ser o padrão
try:
    index_padrao = list(ACOES_DISPONIVEIS.keys()).index("PETR4 - Petrobras (PN)")
except ValueError:
    index_padrao = 0

# Dropdown interativo de ações com ícone
acao_selecionada = st.sidebar.selectbox(
    "📊 Selecione uma Ação:",
    options=list(ACOES_DISPONIVEIS.keys()),
    index=index_padrao,
    help="Escolha um ativo do Brasil ou EUA. Selecione 'OUTRA...' para digitar o ticker manualmente."
)

if ACOES_DISPONIVEIS[acao_selecionada] == "OUTRO":
    ticker_input = st.sidebar.text_input("🔤 Digite o Ticker (Ex: NVDA, TRPL4.SA):", value="")
    ticker = ticker_input.strip().upper()
else:
    ticker = ACOES_DISPONIVEIS[acao_selecionada]

# Number inputs aprimorados com ícones e explicações (substituindo sliders)
horizonte_tempo = st.sidebar.number_input(
    "⏳ Horizonte de Tempo (Dias):",
    min_value=10,
    max_value=1000,
    value=90,
    step=1,
    help="Quantos dias no futuro você deseja simular. O histórico exibido será ajustado para este mesmo período."
)

num_simulacoes = st.sidebar.number_input(
    "🔀 Caminhos (Simulações):",
    min_value=10,
    max_value=1000,
    value=100,
    step=10,
    help="Quantidade de futuros alternativos a serem projetados estocasticamente."
)

st.sidebar.markdown("---")

# Buscando os dados em tempo real
dados_historicos = None
if ticker:
    with st.spinner(f"Processando dados de {ticker}..."):
        dados_historicos = baixar_dados(ticker)

if dados_historicos is not None and not dados_historicos.empty:
    
    # -----------------------------
    # CÁLCULOS FINANCEIROS ESTATÍSTICOS
    # -----------------------------
    
    # 1. Preço de fechamento mais recente
    preco_atual = float(dados_historicos.iloc[-1])
    
    # 2. Log-retornos diários
    log_retornos = np.log(dados_historicos / dados_historicos.shift(1)).dropna()
    
    # 3. Drift (Média dos log-retornos)
    mu = float(log_retornos.mean())
    
    # 4. Volatilidade (Desvio padrão dos log-retornos)
    sigma = float(log_retornos.std())
    
    # Exibir métricas na sidebar com estilo elegante e cores em HEX
    moeda = "R$" if ".SA" in ticker else "US$"
    
    # Cálculo do preço alvo (Esperança Matemática do GBM)
    # E[S_T] = S_0 * exp((mu + sigma^2 / 2) * T)
    preco_alvo_esperado = preco_atual * np.exp((mu + (sigma**2) / 2) * horizonte_tempo)
    
    st.sidebar.markdown("### 📈 Métricas do Ativo")
    
    # Layout vertical (uma embaixo da outra) para evitar cortes
    st.sidebar.metric(
        "💵 Preço Atual", 
        f"{moeda} {preco_atual:.2f}", 
        help="Último preço de fechamento registrado no mercado real."
    )
    
    # Diferença percentual projetada
    variacao_projetada = ((preco_alvo_esperado / preco_atual) - 1) * 100
    st.sidebar.metric(
        "🎯 Alvo Esperado (Média)", 
        f"{moeda} {preco_alvo_esperado:.2f}", 
        delta=f"{variacao_projetada:.2f}%", 
        help="Preço esperado no futuro baseado no cálculo matemático da esperança do modelo estocástico."
    )
    
    st.sidebar.metric(
        "📊 Volatilidade Diária", 
        f"{(sigma * 100):.2f}%", 
        help="O Desvio padrão diário dos log-retornos históricos. Representa o risco."
    )
    
    st.sidebar.metric(
        "🚀 Drift Diário (μ)", 
        f"{(mu * 100):.4f}%", 
        help="Média de crescimento diário dos log-retornos. Representa a tendência."
    )
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.button("↻ Gerar Novos Caminhos", help="Recalcula todas as trajetórias usando novos valores estocásticos.", use_container_width=True)

    # -----------------------------
    # SIMULAÇÃO E GRÁFICO (HISTÓRICO + FUTURO)
    # -----------------------------
    
    # Pegando os últimos 'horizonte_tempo' dias para demonstrar a variância do passado
    tamanho_historico = min(horizonte_tempo, len(dados_historicos))
    historico_recente = dados_historicos.iloc[-tamanho_historico:]
    eixo_tempo_historico = np.arange(-tamanho_historico + 1, 1) # Array de -N até 0 (hoje)
    
    # Executa a simulação matemática
    caminhos = simular_gbm(S0=preco_atual, mu=mu, sigma=sigma, t=horizonte_tempo, num_simulacoes=num_simulacoes)
    
    # Prepara o gráfico interativo com Plotly
    fig = go.Figure()
    eixo_tempo_futuro = np.arange(0, horizonte_tempo)
    
    # 1. Adicionando o Histórico Passado
    fig.add_trace(go.Scatter(
        x=eixo_tempo_historico,
        y=historico_recente,
        mode='lines',
        line=dict(color='#2196f3', width=3), # Azul profissional
        name='Histórico Real',
        showlegend=True
    ))
    
    # 2. Adicionando os caminhos estocásticos gerados
    for i in range(num_simulacoes):
        fig.add_trace(go.Scatter(
            x=eixo_tempo_futuro,
            y=caminhos[:, i],
            mode='lines',
            line=dict(color='#9ba3af', width=1), # Cinza suave
            opacity=0.15,
            showlegend=False,
            hoverinfo='skip'
        ))
        
    # 3. Adicionando a linha do Preço Alvo Esperado (Drift Line)
    # Conectando o preço de hoje (dia 0) com o preço esperado (dia horizonte_tempo - 1)
    fig.add_trace(go.Scatter(
        x=[0, horizonte_tempo-1],
        y=[preco_atual, preco_alvo_esperado],
        mode='lines',
        line=dict(color='#4caf50', width=3, dash='dash'), # Verde
        name='Esperança Matemática (Alvo)',
        showlegend=True
    ))
    
    # 4. Adicionando a linha pontilhada do eixo Y (Dia zero / Hoje)
    fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="#ff9800", annotation_text="Hoje")
    
    # Configuração de layout transparente para integrar com Light/Dark mode
    fig.update_layout(
        title=dict(
            text=f"Histórico e Projeções Futuras - {acao_selecionada}",
            font=dict(size=22)
        ),
        xaxis_title="Dias em relação a hoje ($t=0$)",
        yaxis_title="Preço da Ação",
        plot_bgcolor="rgba(0,0,0,0)", # Fundo transparente
        paper_bgcolor="rgba(0,0,0,0)", # Fundo transparente
        margin=dict(l=40, r=40, t=80, b=40),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(128,128,128,0.2)",
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(128,128,128,0.2)",
            zeroline=False,
            tickprefix=moeda + " "
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified"
    )
    
    # Renderiza o gráfico usando toda a largura
    st.plotly_chart(fig, use_container_width=True)
    
    # -----------------------------
    # NOTA DIDÁTICA
    # -----------------------------
    # Explicação conceitual conforme solicitado
    st.info(
        "💡 **Nota Didática:** No modelo de Movimento Browniano Geométrico, o componente estocástico (choque) "
        "é governado por uma distribuição Normal onde a **variância cresce de forma linear** em relação ao tempo $t$. "
        "Isso implica que, à medida que avançamos para o futuro, o desvio padrão (a incerteza real do modelo) "
        "cresce proporcionalmente a $\sqrt{t}$. Visualmente, notamos isso através deste 'leque' de caminhos que se expande, "
        "demonstrando de forma matemática a dispersão e incerteza inerentes ao mercado financeiro."
    )

else:
    st.warning("Não foi possível processar os dados históricos neste momento. Tente novamente ou escolha outro ativo.")
