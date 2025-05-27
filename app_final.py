# Importações necessárias
import pandas as pd
import os
from datetime import datetime, timedelta
import numpy as np
import io
import traceback
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import json
# import tempfile # Removido, não mais necessário

# Importar funções dos outros módulos
from processar_planilha_otimizado import processar_planilha_otimizado, get_margin_color
from personalizar_tabela import personalizar_tabela_por_marketplace
from mapa_brasil import criar_mapa_brasil_interativo, exibir_detalhes_estado

# --- CONFIGURAÇÕES GLOBAIS ---
pd.set_option("styler.render.max_elements", 1500000)
HISTORICO_PATH = "historico.csv"
LOGO_PATH = "logo.png"  # Caminho relativo para o logo
USUARIOS_PATH = "usuarios.json"  # Arquivo para armazenar usuários

# Definir constantes para colunas da planilha (definidas explicitamente para evitar erros)
COL_SKU_CUSTOS = 'SKU PRODUTOS'
COL_DATA_CUSTOS = 'DIA DE VENDA'
COL_CONTA_CUSTOS_ORIGINAL = 'CONTAS'
COL_PLATAFORMA_CUSTOS = 'PLATAFORMA'
COL_MARGEM_ESTRATEGICA_PLANILHA_CUSTOS = 'MARGEM ESTRATÉGICA'
COL_MARGEM_REAL_PLANILHA_CUSTOS = 'MARGEM REAL'
COL_VALOR_PRODUTO_PLANILHA_CUSTOS = 'PREÇO UND'
COL_ID_PRODUTO_CUSTOS = 'ID DO PRODUTO'
COL_QUANTIDADE_CUSTOS_ABA_CUSTOS = 'QUANTIDADE'
COL_VALOR_PEDIDO_CUSTOS = 'VALOR DO PEDIDO'

# Definir cores personalizadas para o tema
primary_color = "#4361EE"
secondary_color = "#3CCFCF"
text_color_sidebar = "#FFFFFF" # Cor do texto na sidebar (branco)
background_sidebar = "#2E3B55" # Cor de fundo da sidebar (azul escuro)
text_color_main = "#212529" # Cor do texto principal (preto)
background_main = "#F8F9FA" # Cor de fundo principal (cinza claro)

# --- CONFIGURAÇÃO DA PÁGINA STREAMLIT ---
st.set_page_config(page_title="ViaFlix Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown(f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
    }}

    /* Cores e estilos gerais */
    .main {{
        background-color: {background_main};
        color: {text_color_main};
    }}

    /* Animações */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes slideInLeft {{
        from {{ transform: translateX(-50px); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    @keyframes pulse {{
        0% {{ transform: scale(1); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        50% {{ transform: scale(1.03); box-shadow: 0 8px 16px rgba(0,0,0,0.2); }}
        100% {{ transform: scale(1); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
    }}

    /* Cabeçalhos */
    h1, h2, h3 {{
        color: {primary_color};
        font-weight: 600;
        margin-bottom: 1.5rem;
        animation: fadeIn 0.8s ease-out;
    }}

    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc {{
        background-color: {background_sidebar};
        color: {text_color_sidebar};
        animation: slideInLeft 0.5s ease-out;
        padding-top: 2rem;
    }}
    .css-1d391kg .stRadio > label, .css-1d391kg .stSelectbox > label, .css-1d391kg .stDateInput > label {{
        color: {text_color_sidebar} !important; /* Garante que o label seja branco */
        font-weight: 500;
    }}
    .css-1d391kg .stRadio > div > label p {{
        color: {text_color_sidebar} !important; /* Cor do texto das opções do radio */
    }}
    .css-1d391kg .stSelectbox > div > div, .css-1d391kg .stDateInput > div > div {{
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: {text_color_sidebar};
    }}
    .css-1d391kg .stSelectbox > div > div svg {{
        fill: {text_color_sidebar}; /* Cor do ícone do selectbox */
    }}
    .css-1d391kg .stDateInput > div > div svg {{
        fill: {text_color_sidebar}; /* Cor do ícone do date input */
    }}
    .css-1d391kg .stButton > button {{
        width: 100%;
        border-radius: 50px;
        background: linear-gradient(90deg, {primary_color}, #6C8EFF);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.7rem 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        margin-top: 1rem;
    }}
    .css-1d391kg .stButton > button:hover {{
        transform: translateY(-3px) scale(1.03);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.3);
    }}

    /* Cards de Métricas */
    .metric-card {{
        background: white;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
        transition: all 0.4s ease-in-out;
        animation: fadeIn 0.8s ease-out;
        border-left: 5px solid {primary_color};
    }}
    .metric-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
        animation: pulse 1.5s infinite ease-in-out alternate;
    }}
    .metric-value {{
        font-size: 2.2rem;
        font-weight: 700;
        color: {primary_color};
        margin: 0.5rem 0;
    }}
    .metric-label {{
        color: #6C757D;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* Tabelas */
    .stDataFrame {{
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        animation: fadeIn 0.8s ease-out;
    }}
    .stDataFrame div[data-testid="stDataFrameResizable"] {{
        border-radius: 15px;
        overflow: hidden;
    }}
    table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin: 1rem 0;
        font-size: 0.9rem;
    }}
    th {{
        background: linear-gradient(90deg, {primary_color}, #6C8EFF);
        color: white;
        font-weight: 600;
        text-align: left;
        padding: 0.8rem 1rem;
        border: none;
    }}
    th:first-child {{ border-top-left-radius: 10px; }}
    th:last-child {{ border-top-right-radius: 10px; }}
    td {{
        padding: 0.8rem 1rem;
        border-bottom: 1px solid #dee2e6;
        background-color: white;
        transition: background-color 0.3s ease;
    }}
    tr:last-child td:first-child {{ border-bottom-left-radius: 10px; }}
    tr:last-child td:last-child {{ border-bottom-right-radius: 10px; }}
    tr:hover td {{
        background-color: #f1f3f5;
    }}

    /* Gráficos Plotly */
    .stPlotlyChart {{
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        background-color: white;
        padding: 1rem;
        margin-bottom: 1.5rem;
        animation: fadeIn 0.8s ease-out;
    }}

    /* Tela de Boas Vindas */
    .welcome-screen {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 100%;
        max-width: 600px;
        text-align: center;
    }}
    .welcome-logo {{
        max-width: 350px;
        margin: 0 auto 2rem auto;
        animation: pulse 2s infinite ease-in-out;
    }}
    .welcome-text {{
        font-size: 1.5rem;
        color: {primary_color};
        font-weight: 500;
        text-align: center;
        margin-bottom: 2rem;
    }}

    /* Painel Admin */
    .admin-card {{
        background: white;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        animation: fadeIn 0.8s ease-out;
    }}
    .admin-section {{
        margin-bottom: 2rem;
    }}
    .admin-title {{
        color: {primary_color};
        font-weight: 600;
        margin-bottom: 1rem;
        border-bottom: 2px solid {primary_color};
        padding-bottom: 0.5rem;
    }}
    
    /* Alertas */
    .alert-card {{
        background: white;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        animation: fadeIn 0.8s ease-out;
        border-left: 5px solid #EF476F;
    }}
    .alert-card.warning {{
        border-left: 5px solid #FF9800;
    }}
    .alert-card.info {{
        border-left: 5px solid #4361EE;
    }}
    .alert-title {{
        font-weight: 600;
        margin-bottom: 1rem;
        color: #212529;
    }}
    .alert-content {{
        max-height: 200px;
        overflow-y: auto;
        padding: 0.5rem;
        background-color: #f8f9fa;
        border-radius: 8px;
    }}
    .alert-item {{
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #dee2e6;
    }}
    .alert-item:last-child {{
        border-bottom: none;
        margin-bottom: 0;
    }}

    /* Esconder elementos padrão do Streamlit */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

</style>""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DOS ESTADOS DA SESSÃO ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'app_state' not in st.session_state:
    st.session_state.app_state = "login"  # Inicia na tela de login
if 'show_sidebar' not in st.session_state:
    st.session_state.show_sidebar = False
if 'df_result' not in st.session_state:
    st.session_state.df_result = None
if 'data_inicio_analise_state' not in st.session_state:
    st.session_state.data_inicio_analise_state = datetime.now().date() - timedelta(days=30)
if 'data_fim_analise_state' not in st.session_state:
    st.session_state.data_fim_analise_state = datetime.now().date()
if 'periodo_selecionado' not in st.session_state:
    st.session_state.periodo_selecionado = "30 dias"
if 'conta_mae_selecionada_ui_state' not in st.session_state:
    st.session_state.conta_mae_selecionada_ui_state = "Todas"
if 'tipo_margem_selecionada_state' not in st.session_state:
    st.session_state.tipo_margem_selecionada_state = "Margem Estratégica (N)"
if 'marketplace_selecionado_state' not in st.session_state:
    st.session_state.marketplace_selecionado_state = "Todos"
if 'clicked_state_details' not in st.session_state:
    st.session_state.clicked_state_details = None
if 'ml_options_expanded' not in st.session_state:
    st.session_state.ml_options_expanded = False
if 'selected_state' not in st.session_state:
    st.session_state.selected_state = None
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = "user"  # Padrão: usuário comum
if 'alert_sort_by' not in st.session_state:
    st.session_state.alert_sort_by = "Margem"  # Padrão: ordenar por margem
if 'alert_sort_order' not in st.session_state:
    st.session_state.alert_sort_order = "Crescente"  # Padrão: ordem crescente

# --- FUNÇÕES AUXILIARES ---
# Função para formatar moeda no padrão brasileiro
def format_currency_brl(value):
    if pd.isna(value):
        return "R$ 0,00"
    try:
        # Formata com ponto como separador de milhar e vírgula como separador decimal
        formatted_value = f"{value:_.2f}".replace('.', '#').replace(',', '.').replace('#', ',').replace('_', '.')
        return f"R$ {formatted_value}"
    except (ValueError, TypeError):
        return "R$ -" # Retorna um placeholder se a conversão falhar

# Função para carregar usuários
def carregar_usuarios():
    if os.path.exists(USUARIOS_PATH):
        try:
            with open(USUARIOS_PATH, 'r') as f:
                return json.load(f)
        except:
            return {"admin": {"senha": "admin", "role": "admin"}}
    else:
        # Criar arquivo de usuários padrão se não existir
        usuarios_padrao = {"admin": {"senha": "admin", "role": "admin"}}
        with open(USUARIOS_PATH, 'w') as f:
            json.dump(usuarios_padrao, f)
        return usuarios_padrao

# Função para salvar usuários
def salvar_usuarios(usuarios):
    with open(USUARIOS_PATH, 'w') as f:
        json.dump(usuarios, f)

# Função para autenticação
def authenticate(username, password):
    usuarios = carregar_usuarios()
    if username in usuarios and usuarios[username]["senha"] == password:
        st.session_state.user_role = usuarios[username]["role"]
        return True
    return False

# Função para exibir a tela de login
def display_login_screen():
    # Usar colunas para centralizar o login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Container para o login
        with st.container():
            # Logo centralizado
            try:
                logo = Image.open(LOGO_PATH)
                st.image(logo, width=180, use_container_width=True)
            except Exception as e:
                st.error(f"Não foi possível carregar o logo: {e}")
            
            st.markdown("<h2 style='text-align: center; color: #4361EE;'>Login</h2>", unsafe_allow_html=True)
            
            # Campos de login
            username = st.text_input("Usuário", key="username_input", placeholder="Usuário")
            password = st.text_input("Senha", type="password", key="password_input", placeholder="Senha")
            
            # Botão de login centralizado
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("Entrar", key="login_button", use_container_width=True):
                    if authenticate(username, password):
                        st.session_state.authenticated = True
                        st.session_state.app_state = "upload"
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos")

# Função para exibir a tela de boas-vindas/upload
def display_welcome_screen():
    # Usar colunas para centralizar o conteúdo
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Container para centralizar
        with st.container():
            try:
                # Tentar carregar o logo da empresa
                logo = Image.open(LOGO_PATH)
                st.image(logo, width=350, use_container_width=True)
            except FileNotFoundError:
                st.error(f"Erro: Logo não encontrado em {LOGO_PATH}")
            except Exception as e:
                st.error(f"Erro ao carregar o logo: {e}")

            st.markdown("<p style='text-align: center; font-size: 1.5rem; color: #4361EE; font-weight: 500;'>Bem-vindo ao Dashboard de Performance ViaFlix!<br>Faça o upload da sua planilha para começar.</p>", unsafe_allow_html=True)

            uploaded_file = st.file_uploader("Escolha a planilha Excel", type=["xlsx"], label_visibility="collapsed")
    
    return uploaded_file

# Função para exibir métricas em cards
def display_metrics(df, tipo_margem):
    st.subheader("Visão Geral")
    col1, col2, col3, col4 = st.columns(4)

    # Calcular métricas
    total_vendas = df[COL_VALOR_PEDIDO_CUSTOS].sum() if COL_VALOR_PEDIDO_CUSTOS in df.columns else 0
    
    # Calcular margem média e formatar com vírgula e símbolo de porcentagem
    if 'Margem_Num' in df.columns:
        margem_media = df['Margem_Num'].mean() # Margem_Num já está em formato percentual (ex: 11.58)
        # Formatar com duas casas decimais e vírgula
        margem_media_formatada = f"{margem_media:.2f}".replace(".", ",") + "%"
    else:
        margem_media_formatada = "0,00%"
    
    total_skus = df[COL_SKU_CUSTOS].nunique() if COL_SKU_CUSTOS in df.columns else 0
    total_pedidos = len(df)

    with col1:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-label'>Faturamento Total</div>
            <div class='metric-value'>{format_currency_brl(total_vendas)}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-label'>Margem Média ({tipo_margem.split(' ')[1]})</div>
            <div class='metric-value'>{margem_media_formatada}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-label'>SKUs Únicos</div>
            <div class='metric-value'>{total_skus}</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-label'>Total Pedidos</div>
            <div class='metric-value'>{total_pedidos}</div>
        </div>""", unsafe_allow_html=True)

# Função para lidar com o clique no mapa
def handle_map_click(chart_data):
    if chart_data is not None and len(chart_data['points']) > 0:
        point = chart_data['points'][0]
        if 'customdata' in point and len(point['customdata']) >= 4:
            estado = point['customdata'][0]
            detalhes_json = point['customdata'][3]
            st.session_state.selected_state = {'estado': estado, 'detalhes_json': detalhes_json}
            return True
    return False

# Função para exibir alertas em uma aba dedicada
def display_alerts_tab(df):
    # Criar três colunas para os diferentes tipos de alertas
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("### Filtros de Alertas")
        
        # Filtro por tipo de alerta
        tipo_alerta = st.radio(
            "Tipo de Alerta",
            ["Todos", "Margens Críticas", "Estoque Parado", "Alta Performance"],
            index=0
        )
        
        # Filtro por marketplace
        marketplaces = ["Todos"] + list(df[COL_PLATAFORMA_CUSTOS].unique())
        marketplace_filtro = st.selectbox(
            "Marketplace",
            marketplaces,
            index=0
        )
        
        # Filtro por conta
        contas = ["Todos"] + list(df[COL_CONTA_CUSTOS_ORIGINAL].unique())
        conta_filtro = st.selectbox(
            "Conta",
            contas,
            index=0
        )
        
        # Opções de ordenação
        st.markdown("### Ordenação")
        
        # Campo para ordenar
        st.session_state.alert_sort_by = st.selectbox(
            "Ordenar por",
            ["Margem", "SKU", "Conta", "Marketplace", "Estoque"],
            index=0
        )
        
        # Ordem (crescente/decrescente)
        st.session_state.alert_sort_order = st.radio(
            "Ordem",
            ["Crescente", "Decrescente"],
            index=0,
            horizontal=True
        )
    
    with col2:
        # Filtrar dados com base nas seleções
        df_alertas = df.copy()
        
        # Aplicar filtro por tipo de alerta
        if tipo_alerta == "Margens Críticas":
            df_alertas = df_alertas[df_alertas["Margem_Critica"] == True]
        elif tipo_alerta == "Estoque Parado":
            df_alertas = df_alertas[df_alertas["Estoque_Parado"] == True]
        elif tipo_alerta == "Alta Performance":
            df_alertas = df_alertas[df_alertas["Margem_Num"] > 20]
        
        # Aplicar filtro por marketplace
        if marketplace_filtro != "Todos":
            df_alertas = df_alertas[df_alertas[COL_PLATAFORMA_CUSTOS] == marketplace_filtro]
        
        # Aplicar filtro por conta
        if conta_filtro != "Todos":
            df_alertas = df_alertas[df_alertas[COL_CONTA_CUSTOS_ORIGINAL] == conta_filtro]
        
        # Definir colunas ANTES de criar df_alertas_final
        colunas_alertas = [
            COL_SKU_CUSTOS, 
            COL_ID_PRODUTO_CUSTOS,
            COL_CONTA_CUSTOS_ORIGINAL, 
            COL_PLATAFORMA_CUSTOS, 
            "Margem_Original", 
            "Estoque Tiny",
            "Estoque Total Full" # Adicionada coluna de estoque total full
        ]
        
        # Garantir que as colunas existem antes de tentar selecionar
        colunas_existentes_alertas = [col for col in colunas_alertas if col in df_alertas.columns]
        
        # Criar df_alertas_final AQUI, APÓS TODOS os filtros
        if not colunas_existentes_alertas:
             st.warning("Nenhuma coluna relevante encontrada para os alertas.")
             df_alertas_final = pd.DataFrame() # Define como vazio se não houver colunas
        elif df_alertas.empty:
             df_alertas_final = pd.DataFrame(columns=colunas_existentes_alertas) # Define com colunas mas vazio
        else:
             df_alertas_final = df_alertas[colunas_existentes_alertas].drop_duplicates()
            
        # Renomear colunas para melhor visualização (só se df não for vazio)
        if not df_alertas_final.empty:
            df_alertas_final = df_alertas_final.rename(columns={
                COL_SKU_CUSTOS: "SKU",
                COL_ID_PRODUTO_CUSTOS: "ID do Produto",
                COL_CONTA_CUSTOS_ORIGINAL: "Conta",
                COL_PLATAFORMA_CUSTOS: "Marketplace",
                "Margem_Original": "Margem",
                "Estoque Total Full": "Estoque Full" # Renomeada para Estoque Full
            })
        
        # Aplicar ordenação (só se df não for vazio)
        if not df_alertas_final.empty:
            sort_column_map = {
                "Margem": "Margem",
                "SKU": "SKU",
                "Conta": "Conta",
                "Marketplace": "Marketplace",
                "Estoque": "Estoque Tiny",
                "Estoque Full": "Estoque Full" # Adicionar opção de ordenação
            }
            
            # Adicionar a nova opção de ordenação ao selectbox se ainda não estiver lá
            # A lógica do selectbox em si está na UI (col1), aqui apenas garantimos que a ordenação funcione
            sort_options = list(sort_column_map.keys())
            # A verificação abaixo não é mais necessária aqui pois df_alertas_final já está definido
            # if "Estoque Total Full ML" not in st.session_state.alert_sort_by and "Estoque Total Full ML" in df_alertas_final.columns:
            #     pass 
            
            # Verificar se a coluna selecionada para ordenar existe
            if st.session_state.alert_sort_by in sort_column_map and sort_column_map[st.session_state.alert_sort_by] in df_alertas_final.columns:
                sort_column = sort_column_map[st.session_state.alert_sort_by]
                ascending = st.session_state.alert_sort_order == "Crescente"
                
                if sort_column == "Margem":
                    # Para ordenar por margem, precisamos extrair o valor numérico
                    try:
                        df_alertas_final["Margem_Num_Sort"] = df_alertas_final["Margem"].apply(
                            lambda x: float(str(x).replace("%", "").replace(",", ".").strip())
                        )
                        df_alertas_final = df_alertas_final.sort_values("Margem_Num_Sort", ascending=ascending)
                        df_alertas_final = df_alertas_final.drop("Margem_Num_Sort", axis=1)
                    except Exception as e:
                        st.warning(f"Erro ao ordenar por margem: {e}") # Informar erro mas continuar
                        # Tentar ordenação padrão por string se a numérica falhar
                        df_alertas_final = df_alertas_final.sort_values(sort_column, ascending=ascending)
                else:
                    # Ordenar por outras colunas (incluindo as de estoque)
                    df_alertas_final = df_alertas_final.sort_values(sort_column, ascending=ascending)
            else:
                 st.warning(f"Coluna selecionada para ordenação ('{st.session_state.alert_sort_by}') não encontrada ou inválida. Usando ordenação padrão.")
                 # Pode adicionar uma ordenação padrão aqui, ex: por SKU
                 if 'SKU' in df_alertas_final.columns:
                     df_alertas_final = df_alertas_final.sort_values('SKU', ascending=True)
        
        # Exibir a tabela de alertas
        if df_alertas_final.empty:
            st.info(f"Nenhum alerta encontrado para os filtros selecionados.")
        else:
            st.markdown(f"### Tabela de Alertas ({len(df_alertas_final)} itens)")
            
            # Aplicar formatação de cor na margem
            def highlight_margin(s):
                # Aplicar cor baseada no valor numérico da margem
                colors = []
                for v in s:
                    try:
                        # Extrair valor numérico da string de margem
                        if isinstance(v, str) and '%' in v:
                            num_value = float(v.replace('%', '').replace(',', '.').strip())
                            color = get_margin_color(num_value)
                        else:
                            color = get_margin_color(0)  # Valor padrão
                        colors.append(f'color: {color}; font-weight: bold')
                    except:
                        colors.append('')
                return colors
            
            # Formatar colunas de estoque como números inteiros
            format_dict = {}
            for col in df_alertas_final.columns:
                if "Estoque" in col:
                    format_dict[col] = "{:.0f}"  # Sem casas decimais
            
            # Exibir a tabela com formatação
            st.dataframe(
                df_alertas_final.style.apply(highlight_margin, subset=['Margem'])
                .format(format_dict),
                use_container_width=True
            )

# Função para exibir o painel de administração
def display_admin_panel():
    st.title("🔧 Painel de Administração")
    
    # Carregar usuários existentes
    usuarios = carregar_usuarios()
    
    # Dividir em abas
    tab1, tab2, tab3 = st.tabs(["👥 Gerenciar Usuários", "⚙️ Configurações", "📊 Logs"])
    
    with tab1:
        st.subheader("Gerenciar Usuários")
        
        # Exibir usuários existentes
        st.markdown("### Usuários Cadastrados")
        
        # Criar DataFrame para exibir usuários
        usuarios_df = pd.DataFrame([
            {"Usuário": user, "Função": data["role"]}
            for user, data in usuarios.items()
        ])
        
        st.dataframe(usuarios_df, use_container_width=True)
        
        # Formulário para adicionar novo usuário
        st.markdown("### Adicionar Novo Usuário")
        with st.form("novo_usuario"):
            novo_usuario = st.text_input("Nome de Usuário")
            nova_senha = st.text_input("Senha", type="password")
            nova_funcao = st.selectbox("Função", ["user", "admin"])
            
            submitted = st.form_submit_button("Adicionar Usuário")
            if submitted:
                if novo_usuario and nova_senha:
                    if novo_usuario in usuarios:
                        st.error(f"Usuário '{novo_usuario}' já existe!")
                    else:
                        usuarios[novo_usuario] = {"senha": nova_senha, "role": nova_funcao}
                        salvar_usuarios(usuarios)
                        st.success(f"Usuário '{novo_usuario}' adicionado com sucesso!")
                        st.rerun()
                else:
                    st.error("Preencha todos os campos!")
        
        # Formulário para remover usuário
        st.markdown("### Remover Usuário")
        with st.form("remover_usuario"):
            usuario_remover = st.selectbox("Selecione o usuário", list(usuarios.keys()))
            
            submitted = st.form_submit_button("Remover Usuário")
            if submitted:
                if usuario_remover == "admin" and len(usuarios) == 1:
                    st.error("Não é possível remover o único usuário administrador!")
                else:
                    del usuarios[usuario_remover]
                    salvar_usuarios(usuarios)
                    st.success(f"Usuário '{usuario_remover}' removido com sucesso!")
                    st.rerun()
    
    with tab2:
        st.subheader("Configurações do Sistema")
        
        # Configurações de aparência
        st.markdown("### Aparência")
        tema = st.selectbox("Tema", ["Claro", "Escuro", "Personalizado"], index=0)
        
        if tema == "Personalizado":
            cor_primaria = st.color_picker("Cor Primária", primary_color)
            cor_secundaria = st.color_picker("Cor Secundária", secondary_color)
            
            if st.button("Aplicar Tema"):
                st.success("Tema personalizado aplicado com sucesso!")
                # Aqui seria implementada a lógica para salvar as configurações
        
        # Configurações de exportação
        st.markdown("### Exportação de Dados")
        formato_padrao = st.selectbox("Formato Padrão de Exportação", ["Excel (.xlsx)", "CSV (.csv)", "PDF (.pdf)"], index=0)
        
        if st.button("Salvar Configurações"):
            st.success("Configurações salvas com sucesso!")
            # Aqui seria implementada a lógica para salvar as configurações
    
    with tab3:
        st.subheader("Logs do Sistema")
        
        # Simulação de logs
        logs = [
            {"data": "22/05/2025 15:30:45", "usuario": "admin", "acao": "Login no sistema"},
            {"data": "22/05/2025 15:35:12", "usuario": "admin", "acao": "Upload de planilha"},
            {"data": "22/05/2025 15:40:23", "usuario": "admin", "acao": "Exportação de relatório"}
        ]
        
        logs_df = pd.DataFrame(logs)
        st.dataframe(logs_df, use_container_width=True)
        
        if st.button("Limpar Logs"):
            st.success("Logs limpos com sucesso!")
            # Aqui seria implementada a lógica para limpar os logs

# --- SIDEBAR --- (Aparece após o upload)
def setup_sidebar():
    with st.sidebar:
        try:
            st.image(LOGO_PATH, use_container_width=True)
        except Exception as e:
            st.warning(f"Não foi possível carregar o logo na sidebar: {e}")
            
        st.markdown("## Filtros e Opções")

        # Seleção de Período (simplificado - apenas 7, 15, 30 dias e Personalizado)
        periodo_options = {
            "7 dias": 7,
            "15 dias": 15,
            "30 dias": 30,
            "Personalizado": None
        }
        st.session_state.periodo_selecionado = st.radio(
            "Período de Análise",
            options=periodo_options.keys(),
            index=list(periodo_options.keys()).index(st.session_state.periodo_selecionado) if st.session_state.periodo_selecionado in periodo_options.keys() else 2,
            horizontal=True
        )

        if st.session_state.periodo_selecionado == "Personalizado":
            col1, col2 = st.columns(2)
            with col1:
                # Sem limitação de data
                st.session_state.data_inicio_analise_state = st.date_input("Data Início", st.session_state.data_inicio_analise_state)
            with col2:
                st.session_state.data_fim_analise_state = st.date_input("Data Fim", st.session_state.data_fim_analise_state)
        else:
            days = periodo_options[st.session_state.periodo_selecionado]
            st.session_state.data_fim_analise_state = datetime.now().date()
            st.session_state.data_inicio_analise_state = st.session_state.data_fim_analise_state - timedelta(days=days)
            st.info(f"Período: {st.session_state.data_inicio_analise_state.strftime('%d/%m/%Y')} a {st.session_state.data_fim_analise_state.strftime('%d/%m/%Y')}")

        # Seleção de Conta Mãe (exemplo, ajustar conforme necessário)
        contas_disponiveis = ["Todas"] + list(st.session_state.df_result[COL_CONTA_CUSTOS_ORIGINAL].unique()) if st.session_state.df_result is not None and COL_CONTA_CUSTOS_ORIGINAL in st.session_state.df_result.columns else ["Todas"]
        st.session_state.conta_mae_selecionada_ui_state = st.selectbox(
            "Filtrar por Conta",
            options=contas_disponiveis,
            index=contas_disponiveis.index(st.session_state.conta_mae_selecionada_ui_state) if st.session_state.conta_mae_selecionada_ui_state in contas_disponiveis else 0
        )

        # Seleção de Marketplace
        marketplaces_disponiveis = ["Todos"] + list(st.session_state.df_result[COL_PLATAFORMA_CUSTOS].unique()) if st.session_state.df_result is not None and COL_PLATAFORMA_CUSTOS in st.session_state.df_result.columns else ["Todas"]
        st.session_state.marketplace_selecionado_state = st.selectbox(
            "Filtrar por Marketplace",
            options=marketplaces_disponiveis,
            index=marketplaces_disponiveis.index(st.session_state.marketplace_selecionado_state) if st.session_state.marketplace_selecionado_state in marketplaces_disponiveis else 0
        )
        
        # Opções adicionais para Mercado Livre
        if st.session_state.marketplace_selecionado_state == "Mercado Livre":
            st.session_state.ml_options_expanded = True
            st.markdown("### Opções Mercado Livre")
            
            # Exemplo de opções adicionais para Mercado Livre
            ml_tipo_anuncio = st.selectbox(
                "Tipo de Anúncio",
                options=["Todos", "Clássico", "Premium"],
                index=0
            )
            
            ml_estoque = st.radio(
                "Filtrar por Estoque",
                options=["Todos", "Full", "Tiny"],
                index=0,
                horizontal=True
            )
        else:
            st.session_state.ml_options_expanded = False

        # Seleção de Tipo de Margem
        st.session_state.tipo_margem_selecionada_state = st.radio(
            "Tipo de Margem",
            options=["Margem Estratégica (N)", "Margem Real (N)"],
            index=["Margem Estratégica (N)", "Margem Real (N)"].index(st.session_state.tipo_margem_selecionada_state),
            horizontal=True
        )

        # Botões de ação
        if st.button("🔄 Recarregar Planilha"):
            st.session_state.app_state = "upload"
            st.session_state.df_result = None
            st.session_state.clicked_state_details = None
            st.session_state.selected_state = None
            st.rerun()
        
        # Botão para Painel Administrador (apenas para admin)
        if st.session_state.user_role == "admin":
            if st.button("🔧 Painel Administrador"):
                st.session_state.admin_mode = True
                st.rerun()
            
        if st.button("🚪 Sair"):
            st.session_state.authenticated = False
            st.session_state.app_state = "login"
            st.session_state.df_result = None
            st.session_state.selected_state = None
            st.session_state.admin_mode = False
            st.rerun()

# --- LÓGICA PRINCIPAL DA APLICAÇÃO ---
if not st.session_state.authenticated:
    display_login_screen()
elif st.session_state.admin_mode:
    # Exibir painel de administração
    display_admin_panel()
    
    # Botão para voltar ao dashboard
    if st.button("← Voltar ao Dashboard"):
        st.session_state.admin_mode = False
        st.rerun()
elif st.session_state.app_state == "upload":
    uploaded_file = display_welcome_screen()
    if uploaded_file is not None:
        with st.spinner("Processando planilha... Por favor, aguarde."):
            try:
                # Remover a criação de arquivo temporário, passar o objeto uploaded_file diretamente
                # temp_file_path = os.path.join("/tmp", uploaded_file.name) # Linha removida
                # with open(temp_file_path, "wb") as f: # Linha removida
                #     f.write(uploaded_file.getbuffer()) # Linha removida
                
                df_processado = processar_planilha_otimizado(
                    uploaded_file, # Passa o objeto UploadedFile diretamente
                    st.session_state.tipo_margem_selecionada_state, # Passa o tipo de margem inicial
                    st.session_state.data_inicio_analise_state, # Passa data inicial
                    st.session_state.data_fim_analise_state # Passa data final
                )
                
                # Remover arquivo temporário - não mais necessário
                # os.remove(temp_file_path) # Linha removida
                
                if df_processado is not None and not df_processado.empty:
                    st.session_state.df_result = df_processado
                    st.session_state.app_state = "dashboard"
                    st.rerun()
                elif df_processado is not None and df_processado.empty:
                    st.warning("A planilha foi processada, mas não foram encontrados dados para os filtros selecionados.")
                # Se df_processado for None, o erro já foi mostrado dentro da função

            except Exception as e:
                st.error(f"Ocorreu um erro inesperado ao processar a planilha: {str(e)}")
                st.error(traceback.format_exc())

elif st.session_state.app_state == "dashboard" and st.session_state.df_result is not None:
    setup_sidebar() # Configura a sidebar agora que temos dados

    st.title("📊 Dashboard de Performance ViaFlix")

    # Filtrar dados com base nas seleções da sidebar
    df_filtrado = st.session_state.df_result.copy()

    # Filtrar por data (já feito no processamento inicial, mas pode refiltrar se necessário)
    # Garantir que as datas estejam no formato correto para comparação
    data_inicio = pd.to_datetime(st.session_state.data_inicio_analise_state).date()
    data_fim = pd.to_datetime(st.session_state.data_fim_analise_state).date()
    
    # Certificar que a coluna de data no DataFrame é do tipo date
    if COL_DATA_CUSTOS in df_filtrado.columns:
        # Converter para datetime se ainda não for, depois extrair a data
        if not pd.api.types.is_datetime64_any_dtype(df_filtrado[COL_DATA_CUSTOS]):
             df_filtrado[COL_DATA_CUSTOS] = pd.to_datetime(df_filtrado[COL_DATA_CUSTOS], errors='coerce')
        
        # Remover linhas onde a data não pôde ser convertida (NaT)
        df_filtrado.dropna(subset=[COL_DATA_CUSTOS], inplace=True)
        
        # Extrair a parte da data para comparação segura
        df_filtrado[COL_DATA_CUSTOS] = df_filtrado[COL_DATA_CUSTOS].dt.date
        
        df_filtrado = df_filtrado[
            (df_filtrado[COL_DATA_CUSTOS] >= data_inicio) &
            (df_filtrado[COL_DATA_CUSTOS] <= data_fim)
        ]
    else:
        st.warning(f"Coluna '{COL_DATA_CUSTOS}' não encontrada para filtro de data.")

    # Filtrar por conta
    if st.session_state.conta_mae_selecionada_ui_state != "Todas":
        df_filtrado = df_filtrado[df_filtrado[COL_CONTA_CUSTOS_ORIGINAL] == st.session_state.conta_mae_selecionada_ui_state]

    # Filtrar por marketplace
    if st.session_state.marketplace_selecionado_state != "Todos":
        df_filtrado = df_filtrado[df_filtrado[COL_PLATAFORMA_CUSTOS] == st.session_state.marketplace_selecionado_state]

    # Verificar se o DataFrame filtrado não está vazio
    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
    else:
        # Exibir métricas
        display_metrics(df_filtrado, st.session_state.tipo_margem_selecionada_state)

        st.markdown("--- ")

        # Abas para diferentes visualizações
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Análise Geral", "🗺️ Mapa de Vendas", "📄 Tabela Detalhada", "⚠️ Alertas"])

        with tab1:
            st.subheader("Análise Geral")
            col1, col2 = st.columns(2)
            with col1:
                # Gráfico de Vendas por Dia (Exemplo Plotly)
                try:
                    vendas_por_dia = df_filtrado.groupby(COL_DATA_CUSTOS)[COL_VALOR_PEDIDO_CUSTOS].sum().reset_index()
                    fig_vendas_dia = px.line(vendas_por_dia, x=COL_DATA_CUSTOS, y=COL_VALOR_PEDIDO_CUSTOS, title="Faturamento Diário", markers=True)
                    fig_vendas_dia.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_vendas_dia, use_container_width=True)
                except Exception as e:
                    st.warning(f"Não foi possível gerar o gráfico de faturamento diário: {e}")

            with col2:
                # Gráfico de Vendas por Marketplace (Exemplo Plotly)
                try:
                    vendas_por_marketplace = df_filtrado.groupby(COL_PLATAFORMA_CUSTOS)[COL_VALOR_PEDIDO_CUSTOS].sum().reset_index()
                    fig_vendas_mp = px.pie(vendas_por_marketplace, values=COL_VALOR_PEDIDO_CUSTOS, names=COL_PLATAFORMA_CUSTOS, title="Faturamento por Marketplace", hole=0.4)
                    fig_vendas_mp.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_vendas_mp, use_container_width=True)
                except Exception as e:
                    st.warning(f"Não foi possível gerar o gráfico de faturamento por marketplace: {e}")

        with tab2:
            st.subheader("Mapa Interativo de Vendas por Estado")
            # Criar e exibir o mapa interativo
            mapa_fig = criar_mapa_brasil_interativo(df_filtrado) # Passar df_filtrado para usar dados reais se implementado
            if mapa_fig:
                # Usar st.plotly_chart com eventos para capturar cliques
                clicked_point = st.plotly_chart(mapa_fig, use_container_width=True, on_click=handle_map_click)
                
                # Exibir detalhes do estado selecionado
                if st.session_state.selected_state:
                    exibir_detalhes_estado(
                        st.session_state.selected_state['estado'], 
                        st.session_state.selected_state['detalhes_json']
                    )
                else:
                    st.info("Clique em um estado no mapa para ver detalhes de vendas por marketplace e conta.")
            else:
                st.warning("Não foi possível gerar o mapa interativo.")

        with tab3:
            st.subheader("Tabela Detalhada de Produtos")
            try:
                # Personalizar e exibir a tabela
                df_tabela_personalizada = personalizar_tabela_por_marketplace(
                    df_filtrado,
                    st.session_state.marketplace_selecionado_state,
                    st.session_state.tipo_margem_selecionada_state
                )

                # Aplicar formatação de cor na margem
                def highlight_margin(s):
                    # Aplicar cor baseada no valor numérico da margem
                    colors = []
                    for v in s:
                        try:
                            # Extrair valor numérico da string de margem
                            if isinstance(v, str) and '%' in v:
                                num_value = float(v.replace('%', '').replace(',', '.').strip())
                                color = get_margin_color(num_value)
                            else:
                                color = get_margin_color(0)  # Valor padrão
                            colors.append(f'color: {color}; font-weight: bold')
                        except:
                            colors.append('')
                    return colors

                # Adicionar barra de pesquisa
                search_term = st.text_input("Pesquisar Produto (SKU ou ID)", key="search_detailed_table", placeholder="Digite o SKU ou ID...")

                df_display = df_tabela_personalizada.copy() # Trabalhar com uma cópia

                # --- START: Add logic for 'Estoque Full' column ---
                # Ensure necessary columns exist before proceeding
                # Define COL_CONTA_CUSTOS_ORIGINAL if not globally defined (it seems to be)
                required_cols = [COL_CONTA_CUSTOS_ORIGINAL, 'Estoque Full VF', 'Estoque Full DK', 'Estoque Full GS']
                # Check if all required source columns are present
                source_cols_present = all(col in df_display.columns for col in required_cols)

                if source_cols_present:
                    try:
                        # Define the conditions
                        cond_vf = df_display[COL_CONTA_CUSTOS_ORIGINAL] == 'Via Flix'
                        cond_dk = df_display[COL_CONTA_CUSTOS_ORIGINAL] == 'Monaco'
                        cond_gs = df_display[COL_CONTA_CUSTOS_ORIGINAL] == 'GS Torneira'

                        # Define the choices based on conditions
                        choices = [
                            pd.to_numeric(df_display['Estoque Full VF'], errors='coerce').fillna(0), # Convert to numeric, handle errors
                            pd.to_numeric(df_display['Estoque Full DK'], errors='coerce').fillna(0), # Convert to numeric, handle errors
                            pd.to_numeric(df_display['Estoque Full GS'], errors='coerce').fillna(0)  # Convert to numeric, handle errors
                        ]

                        # Apply np.select to create the new column
                        df_display['Estoque Full'] = np.select(
                            [cond_vf, cond_dk, cond_gs],
                            choices,
                            default=0 # Default value for accounts not matching the rules
                        ).astype(int) # Convert result to integer

                        # Remove the original individual stock columns
                        cols_to_drop = ['Estoque Full VF', 'Estoque Full DK', 'Estoque Full GS']
                        df_display = df_display.drop(columns=cols_to_drop)
                    except Exception as e:
                         st.error(f"Erro ao criar coluna 'Estoque Full': {e}")
                         if 'Estoque Full' not in df_display.columns: # Avoid overwriting if partially created
                              df_display['Estoque Full'] = 0 # Default column on error

                elif 'Estoque Full' not in df_display.columns: # Only warn if 'Estoque Full' doesn't already exist and source cols missing
                     # Check which required columns are missing
                     missing_cols = [col for col in required_cols if col not in df_display.columns]
                     st.warning(f"Não foi possível criar a coluna 'Estoque Full' personalizada. Colunas necessárias ausentes: {missing_cols}. Verifique a função 'personalizar_tabela_por_marketplace' ou a planilha original.")
                     # Optionally create a default 'Estoque Full' column if needed elsewhere
                     # df_display['Estoque Full'] = 0
                # --- END: Add logic for 'Estoque Full' column ---
                if search_term:
                    search_term_lower = search_term.lower()
                    # Garantir que as colunas existam antes de filtrar
                    filter_cols = []
                    if 'SKU' in df_display.columns:
                        # Garantir que a coluna SKU seja string antes de aplicar .str
                        filter_cols.append(df_display['SKU'].astype(str).str.lower().str.contains(search_term_lower, na=False))
                    if 'ID do Produto' in df_display.columns:
                         # Garantir que a coluna ID do Produto seja string antes de aplicar .str
                         filter_cols.append(df_display['ID do Produto'].astype(str).str.lower().str.contains(search_term_lower, na=False))
                    
                    if filter_cols:
                         # Combinar filtros com lógica OR
                         from functools import reduce
                         import operator
                         combined_filter = reduce(operator.or_, filter_cols)
                         df_display = df_display[combined_filter]
                    # Não precisa de warning se colunas não existirem, o filtro simplesmente não será aplicado nessas colunas.

                # Formatar a coluna de valor de venda e estoques APÓS filtrar
                format_dict = {}
                # Usar o nome da coluna RENOMEADA ('Preço') para aplicar a formatação BRL
                if 'Preço' in df_display.columns: 
                    format_dict['Preço'] = format_currency_brl 
                
                # Formatar colunas de estoque como números inteiros
                for col in df_display.columns:
                    if "Estoque" in col:
                        format_dict[col] = "{:.0f}"  # Sem casas decimais

                # Exibir a tabela com formatação (agora usando df_display)
                st.dataframe(
                    df_display.style.apply(highlight_margin, subset=['Margem'])
                    .format(format_dict),
                    use_container_width=True
                )
                
            except AttributeError as e:
                 if "'Series' object has no attribute 'columns'" in str(e):
                     st.error("Erro ao personalizar a tabela: Parece que os dados filtrados resultaram em uma única linha (Series) em vez de múltiplas linhas (DataFrame). Verifique os filtros.")
                     st.dataframe(df_filtrado) # Mostra o dataframe filtrado original
                 else:
                     st.error(f"Erro ao exibir a tabela detalhada: {e}")
                     st.error(traceback.format_exc())
            except Exception as e:
                st.error(f"Erro ao exibir a tabela detalhada: {e}")
                st.error(traceback.format_exc())
        
        with tab4:
            st.subheader("Alertas e Observações")
            # Exibir alertas em uma aba dedicada
            display_alerts_tab(df_filtrado)

else:
    # Se o estado for inválido ou df_result for None, volta para upload
    st.session_state.app_state = "upload"
    st.rerun()


