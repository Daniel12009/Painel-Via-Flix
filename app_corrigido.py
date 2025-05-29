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

# Importar funções dos outros módulos - usando os nomes de arquivo corretos
from processar_planilha_otimizado_melhorado import processar_planilha_otimizado, atualizar_margem_sem_reprocessamento
from personalizar_tabela_melhorado import personalizar_tabela_por_marketplace, atualizar_tabela_com_nova_margem
from mapa_brasil_aprimorado import criar_mapa_brasil_interativo, exibir_detalhes_estado

# --- CONFIGURAÇÕES GLOBAIS ---
pd.set_option("styler.render.max_elements", 1500000)
HISTORICO_PATH = "historico.csv"; LOGO_PATH = "logo.png"; USUARIOS_PATH = "usuarios.json"
COL_SKU_CUSTOS = 'SKU PRODUTOS'; COL_DATA_CUSTOS = 'DIA DE VENDA'; COL_CONTA_CUSTOS_ORIGINAL = 'CONTAS'
COL_PLATAFORMA_CUSTOS = 'PLATAFORMA'; COL_MARGEM_ESTRATEGICA_PLANILHA_CUSTOS = 'MARGEM ESTRATÉGICA'
COL_MARGEM_REAL_PLANILHA_CUSTOS = 'MARGEM REAL'; COL_VALOR_PRODUTO_PLANILHA_CUSTOS = 'PREÇO UND'
COL_ID_PRODUTO_CUSTOS = 'ID DO PRODUTO'; COL_QUANTIDADE_CUSTOS_ABA_CUSTOS = 'QUANTIDADE'
COL_VALOR_PEDIDO_CUSTOS = 'VALOR DO PEDIDO'
COL_TIPO_ANUNCIO_ML_CUSTOS = 'TIPO ANUNCIO ML'
COL_TIPO_VENDA = 'TIPO DE VENDA'  # Nova coluna para identificar Marketplace, Atacado ou Showroom

# Cores modernas para o novo design (Tema Claro)
primary_color = "#1E3A8A"  # Azul profissional
secondary_color = "#3CCFCF"  # Turquesa
accent_color = "#FF9500"  # Laranja
success_color = "#10B981"  # Verde
warning_color = "#F59E0B"  # Amarelo
danger_color = "#EF4444"  # Vermelho
text_color_sidebar = "#FFFFFF"  # Texto escuro para o sidebar claro
background_sidebar = "#174F87"  # Fundo claro (cinza muito claro) para sidebar
text_color_main = "#FFFFFF"  # Cinza escuro para texto
background_main = "#FFFFFF"  # Fundo branco para área principal

st.set_page_config(page_title="ViaFlix Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# CSS aprimorado com novas cores e estilos modernos
st.markdown(f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    .main {{ background-color: {background_main}; color: {text_color_main}; }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    
    /* Ajuste completo do sidebar para azul escuro */
    .css-1d391kg, .css-1lcbmhc, [data-testid="stSidebar"] {{ 
        background-color: {background_sidebar} !important; 
        color: {text_color_sidebar} !important; 
        padding-top: 2rem; 
    }}
    
    /* Garantir que todos os textos no sidebar sejam brancos */
    [data-testid="stSidebar"] *, .css-1d391kg *, .css-1lcbmhc * {{ 
        color:  !important; 
    }}
    
    /* Ajustes específicos para elementos de formulário no sidebar */
    .css-1d391kg .stRadio > label, 
    .css-1d391kg .stSelectbox > label, 
    .css-1d391kg .stDateInput > label,
    [data-testid="stSidebar"] .stRadio > label, 
    [data-testid="stSidebar"] .stSelectbox > label, 
    [data-testid="stSidebar"] .stDateInput > label {{ 
        color: {text_color_sidebar} !important; 
        font-weight: 500; 
    }}
    
    .css-1d391kg .stRadio > div > label p, 
    [data-testid="stSidebar"] .stRadio > div > label p {{ 
        color: {text_color_sidebar} !important; 
    }}
    
    /* Estilos para textos e títulos no sidebar */
    .sidebar-text {{ 
        color: {text_color_sidebar} !important; 
        opacity: 0.9;
    }}
    
    .sidebar-title {{ 
        color: {text_color_sidebar} !important; 
        font-weight: bold; 
        font-size: 1.2rem; 
        margin-bottom: 1rem; 
        text-shadow: 0px 1px 2px rgba(0,0,0,0.3);
    }}
    
    /* Estilo aprimorado para itens do menu */
    .sidebar-menu-item {{ 
        padding: 12px 15px; 
        border-radius: 8px; 
        margin-bottom: 8px; 
        cursor: pointer; 
        transition: all 0.3s ease;
        color: {text_color_sidebar} !important;
        border-left: 3px solid transparent;
    }}
    
    .sidebar-menu-item:hover {{ 
        background-color: rgba(255,255,255,0.15); 
        border-left: 3px solid {secondary_color};
    }}
    
    .sidebar-menu-item.active {{ 
        background-color: rgba(255,255,255,0.2); 
        font-weight: 600;
        color: {text_color_sidebar} !important;
        border-left: 3px solid {secondary_color};
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }}
    .metric-card {{ 
        background: white; 
        border-radius: 12px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
        padding: 1.5rem; 
        text-align: center; 
        margin-bottom: 1.5rem; 
        border-left: 5px solid {primary_color}; 
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    .metric-card:hover {{ 
        transform: translateY(-5px); 
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }}
    .metric-card::after {{
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 30%;
        height: 5px;
        background: linear-gradient(90deg, transparent, {secondary_color});
    }}
    .metric-value {{ 
        font-size: 2.2rem; 
        font-weight: 700; 
        color: {primary_color}; 
        margin: 0.5rem 0; 
        background: linear-gradient(90deg, {primary_color}, {secondary_color});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 1px rgba(0,0,0,0.1);
    }}
    .metric-label {{ 
        color: #6C757D; 
        font-size: 0.9rem; 
        font-weight: 500; 
        text-transform: uppercase; 
        letter-spacing: 0.5px; 
    }}
    .stTabs [data-baseweb="tab-list"] {{ 
        gap: 2px; 
        background-color: #F1F5F9;
        border-radius: 10px;
        padding: 5px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        border-radius: 8px;
        padding: 0px 20px;
        background-color: transparent;
        transition: all 0.3s ease;
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: white !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        border-bottom: 2px solid {primary_color};
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: rgba(255,255,255,0.7);
    }}
    .custom-filter-container {{
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-top: 3px solid {secondary_color};
    }}
    .custom-chart-container {{
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-top: 3px solid {primary_color};
    }}
    .stButton>button {{
        background-color: #0000003d;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: {secondary_color};
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    .category-icon {{
        font-size: 1.5rem;
        margin-right: 10px;
        vertical-align: middle;
    }}
    .custom-tab {{
        border-radius: 8px;
        padding: 10px 15px;
        background-color: white;
        margin-right: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid #E5E7EB;
    }}
    .custom-tab.active {{
        background-color: {primary_color};
        color: white;
        border-color: {primary_color};
    }}
    .custom-tab:hover {{
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    .tooltip {{
        position: relative;
        display: inline-block;
    }}
    .tooltip .tooltiptext {{
        visibility: hidden;
        width: 200px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }}
    .tooltip:hover .tooltiptext {{
        visibility: visible;
        opacity: 1;
    }}
</style>""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DOS ESTADOS DA SESSÃO ---
default_states = {
    'authenticated': False, 'app_state': "login", 'df_result': None,
    # Definir datas padrão para um período que provavelmente terá dados ou um default seguro
    'data_inicio_analise_state': datetime.now().date() - timedelta(days=29), # Para 30 dias, o início é D-29
    'data_fim_analise_state': datetime.now().date(),
    'periodo_selecionado': "30 dias", # Padrão
    'conta_mae_selecionada_ui_state': "Todas",
    'tipo_margem_selecionada_state': "Margem Estratégica (L)", 
    'marketplace_selecionado_state': "Todos", 'ml_options_expanded': False,
    'selected_state': None, 'admin_mode': False, 'user_role': "user",
    'alert_sort_by': "Margem", 'alert_sort_order': "Crescente",
    'dummy_rerun_counter': 0, 'df_com_status_vendedores': None,
    'ml_tipo_anuncio_selecionado': "Todos",
    'categoria_selecionada': "Dashboard", # Nova variável para controlar a categoria selecionada (Dashboard, Marketplaces, Atacado, Showroom)
    'tipo_venda_selecionado': "Todos" # Nova variável para filtrar por tipo de venda
}
for key, value in default_states.items():
    if key not in st.session_state: st.session_state[key] = value

# --- FUNÇÕES AUXILIARES ---
def format_currency_brl(value):
    if pd.isna(value) or value == "-": return "R$ 0,00"
    try: float_value = float(value); formatted_value = f"{float_value:_.2f}".replace('.', '#').replace(',', '.').replace('#', ',').replace('_', '.'); return f"R$ {formatted_value}"
    except: return "R$ -"

def get_margin_color(margin_value_numeric):
    try:
        val = float(margin_value_numeric)
        if val < 10: return danger_color
        elif val < 16: return warning_color
        else: return success_color
    except: return primary_color

def carregar_usuarios():
    if os.path.exists(USUARIOS_PATH):
        try:
            with open(USUARIOS_PATH, 'r') as f: data = json.load(f)
            return data if isinstance(data, dict) else {"admin": {"senha": "admin", "role": "admin"}}
        except: return {"admin": {"senha": "admin", "role": "admin"}}
    else: return {"admin": {"senha": "admin", "role": "admin"}}

def salvar_usuarios(usuarios):
    try:
        with open(USUARIOS_PATH, 'w') as f: json.dump(usuarios, f, indent=4)
    except Exception as e: st.error(f"Erro ao salvar usuários: {e}")

def authenticate(username, password):
    usuarios = carregar_usuarios()
    user_data = usuarios.get(username)
    if isinstance(user_data, dict) and user_data.get("senha") == password:
        st.session_state.user_role = user_data.get("role", "user"); return True
    return False

def display_login_screen():
    col1, col2, col3 = st.columns([1,1,1]) 
    with col2:
        with st.container(border=True):
            try: logo = Image.open(LOGO_PATH); st.image(logo, width=150)
            except: st.markdown("## ViaFlix Login")
            st.markdown("<h3 style='text-align: center;'>Acessar Dashboard</h3>", unsafe_allow_html=True)
            username = st.text_input("Usuário", key="login_user_final_v10", placeholder="seu_usuario")
            password = st.text_input("Senha", type="password", key="login_pass_final_v10", placeholder="********")
            if st.button("Entrar", key="login_btn_final_v10", use_container_width=True, type="primary"):
                if authenticate(username, password):
                    st.session_state.authenticated = True; st.session_state.app_state = "upload"; st.rerun()
                else: st.error("Usuário ou senha inválidos.")

def display_welcome_screen():
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True) 
        try: logo = Image.open(LOGO_PATH); st.image(logo, width=300, use_container_width=False)
        except: pass
        st.markdown("<h2 style='text-align: center;'>Dashboard de Performance ViaFlix</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 1.1rem;'>Faça o upload da sua planilha de custos para começar a análise.</p>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(" ", type=["xlsx"], label_visibility="collapsed", key="welcome_uploader_final_v10")
        st.markdown("<p style='text-align: center; font-size: 0.9rem; color: grey;'>Arraste e solte o arquivo ou clique para procurar.</p>", unsafe_allow_html=True)
    return uploaded_file

def display_metrics(df, tipo_margem_selecionada_ui_metrics, categoria=None):
    """
    Exibe métricas gerais ou específicas por categoria (Marketplace, Atacado, Showroom)
    """
    st.subheader("Visão Geral" if categoria == "Todos" or categoria is None else f"Visão Geral - {categoria}")
    
    # Filtrar por categoria se necessário
    if categoria and categoria != "Todos" and COL_TIPO_VENDA in df.columns:
        df_filtered = df[df[COL_TIPO_VENDA] == categoria].copy()
    else:
        df_filtered = df.copy()
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    total_vendas_met = df_filtered[COL_VALOR_PEDIDO_CUSTOS].sum() if COL_VALOR_PEDIDO_CUSTOS in df_filtered.columns else 0.0
    
    margem_media_fmt_met = "0,00%"
    if 'Margem_Num' in df_filtered.columns and not df_filtered['Margem_Num'].empty:
        margem_media_calc_met = df_filtered['Margem_Num'].mean() 
        if not pd.isna(margem_media_calc_met): 
            margem_media_fmt_met = f"{margem_media_calc_met:.2f}".replace(".", ",") + "%"
    
    letra_margem_met = tipo_margem_selecionada_ui_metrics.split('(')[-1].split(')')[0] if '(' in tipo_margem_selecionada_ui_metrics else 'N/A'
    total_skus_met = df_filtered[COL_SKU_CUSTOS].nunique() if COL_SKU_CUSTOS in df_filtered.columns else 0
    total_pedidos_met = len(df_filtered) if not df_filtered.empty else 0
    
    # Ícones para cada métrica
    with col_m1: 
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Faturamento Total</div>
            <div class='metric-value'>{format_currency_brl(total_vendas_met)}</div>
            <div style='font-size: 0.8rem; color: #6C757D;'>💰 Valor total das vendas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m2: 
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Margem Média ({letra_margem_met})</div>
            <div class='metric-value'>{margem_media_fmt_met}</div>
            <div style='font-size: 0.8rem; color: #6C757D;'>📈 Rentabilidade média</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m3: 
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>SKUs Únicos</div>
            <div class='metric-value'>{total_skus_met}</div>
            <div style='font-size: 0.8rem; color: #6C757D;'>🏷️ Produtos diferentes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m4: 
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Total Pedidos</div>
            <div class='metric-value'>{total_pedidos_met}</div>
            <div style='font-size: 0.8rem; color: #6C757D;'>📦 Pedidos processados</div>
        </div>
        """, unsafe_allow_html=True)

def display_category_specific_metrics(df, categoria):
    """
    Exibe métricas específicas para cada categoria (Marketplace, Atacado, Showroom)
    """
    if categoria == "Marketplaces":
        # Métricas específicas para Marketplaces
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição por marketplace
            if COL_PLATAFORMA_CUSTOS in df.columns:
                marketplace_counts = df[COL_PLATAFORMA_CUSTOS].value_counts().reset_index()
                marketplace_counts.columns = ['Marketplace', 'Contagem']
                
                fig = px.pie(
                    marketplace_counts, 
                    values='Contagem', 
                    names='Marketplace',
                    title='Distribuição por Marketplace',
                    color_discrete_sequence=px.colors.sequential.Blues_r,
                    hole=0.4
                )
                
                fig.update_layout(
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                    margin=dict(t=50, b=50, l=10, r=10)
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Tipo de anúncio (para Mercado Livre)
            if 'Tipo de Anúncio' in df.columns:
                ml_df = df[df[COL_PLATAFORMA_CUSTOS] == 'Mercado Livre']
                if not ml_df.empty:
                    anuncio_counts = ml_df['Tipo de Anúncio'].value_counts().reset_index()
                    anuncio_counts.columns = ['Tipo de Anúncio', 'Contagem']
                    
                    fig = px.bar(
                        anuncio_counts,
                        x='Tipo de Anúncio',
                        y='Contagem',
                        title='Tipos de Anúncio no Mercado Livre',
                        color='Contagem',
                        color_continuous_scale='Blues'
                    )
                    
                    fig.update_layout(
                        xaxis_title="",
                        yaxis_title="Quantidade",
                        coloraxis_showscale=False,
                        margin=dict(t=50, b=50, l=10, r=10)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Sem dados do Mercado Livre para exibir.")
    
    elif categoria == "Atacado":
        # Métricas específicas para Atacado
        col1, col2 = st.columns(2)
        
        with col1:
            # Valor médio de pedido por região
            if 'Estado' in df.columns and COL_VALOR_PEDIDO_CUSTOS in df.columns:
                region_avg = df.groupby('Estado')[COL_VALOR_PEDIDO_CUSTOS].mean().reset_index()
                region_avg.columns = ['Estado', 'Valor Médio']
                region_avg = region_avg.sort_values('Valor Médio', ascending=False)
                
                fig = px.bar(
                    region_avg,
                    x='Estado',
                    y='Valor Médio',
                    title='Valor Médio de Pedido por Estado',
                    color='Valor Médio',
                    color_continuous_scale='Blues'
                )
                
                fig.update_layout(
                    xaxis_title="",
                    yaxis_title="Valor Médio (R$)",
                    coloraxis_showscale=False,
                    margin=dict(t=50, b=50, l=10, r=10)
                )
                
                fig.update_traces(
                    texttemplate='R$ %{y:,.2f}',
                    textposition='outside'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Simulação para demonstração
                estados = ['SP', 'MG', 'RJ', 'RS', 'PR', 'BA', 'SC', 'GO', 'PE', 'CE']
                valores = [np.random.randint(5000, 15000) for _ in range(10)]
                
                sim_df = pd.DataFrame({
                    'Estado': estados,
                    'Valor Médio': valores
                }).sort_values('Valor Médio', ascending=False)
                
                fig = px.bar(
                    sim_df,
                    x='Estado',
                    y='Valor Médio',
                    title='Valor Médio de Pedido por Estado (Simulação)',
                    color='Valor Médio',
                    color_continuous_scale='Blues'
                )
                
                fig.update_layout(
                    xaxis_title="",
                    yaxis_title="Valor Médio (R$)",
                    coloraxis_showscale=False,
                    margin=dict(t=50, b=50, l=10, r=10)
                )
                
                fig.update_traces(
                    texttemplate='R$ %{y:,.2f}',
                    textposition='outside'
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Frequência de compra por cliente
            # Simulação para demonstração
            freq_labels = ['1ª Compra', '2ª Compra', '3ª Compra', '4ª Compra', '5ª ou mais']
            freq_values = [40, 25, 15, 10, 10]
            
            fig = px.pie(
                values=freq_values,
                names=freq_labels,
                title='Frequência de Compra por Cliente',
                color_discrete_sequence=px.colors.sequential.Blues_r,
                hole=0.4
            )
            
            fig.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=50, b=50, l=10, r=10)
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    elif categoria == "Showroom":
        # Métricas específicas para Showroom
        col1, col2 = st.columns(2)
        
        with col1:
            # Vendas por vendedor
            # Simulação para demonstração
            vendedores = ['Carlos', 'Ana', 'Pedro', 'Mariana', 'João']
            vendas = [np.random.randint(50000, 150000) for _ in range(5)]
            
            sim_df = pd.DataFrame({
                'Vendedor': vendedores,
                'Vendas': vendas
            }).sort_values('Vendas', ascending=False)
            
            fig = px.bar(
                sim_df,
                x='Vendedor',
                y='Vendas',
                title='Vendas por Vendedor',
                color='Vendas',
                color_continuous_scale='Blues'
            )
            
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Valor Total (R$)",
                coloraxis_showscale=False,
                margin=dict(t=50, b=50, l=10, r=10)
            )
            
            fig.update_traces(
                texttemplate='R$ %{y:,.2f}',
                textposition='outside'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Métodos de pagamento
            # Simulação para demonstração
            metodos = ['Cartão de Crédito', 'Pix', 'Boleto', 'Dinheiro', 'Transferência']
            valores = [45, 30, 15, 5, 5]
            
            fig = px.pie(
                values=valores,
                names=metodos,
                title='Métodos de Pagamento',
                color_discrete_sequence=px.colors.sequential.Blues_r,
                hole=0.4
            )
            
            fig.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=50, b=50, l=10, r=10)
            )
            
            st.plotly_chart(fig, use_container_width=True)

def display_time_series_chart(df, categoria=None):
    """
    Exibe gráfico de série temporal de vendas, filtrado por categoria se especificado
    """
    # Filtrar por categoria se necessário
    if categoria and categoria != "Todos" and COL_TIPO_VENDA in df.columns:
        df_filtered = df[df[COL_TIPO_VENDA] == categoria].copy()
    else:
        df_filtered = df.copy()
    
    if COL_DATA_CUSTOS in df_filtered.columns and COL_VALOR_PEDIDO_CUSTOS in df_filtered.columns:
        # Agrupar por data
        df_filtered['Data'] = pd.to_datetime(df_filtered[COL_DATA_CUSTOS]).dt.date
        vendas_por_dia = df_filtered.groupby('Data')[COL_VALOR_PEDIDO_CUSTOS].sum().reset_index()
        
        # Criar gráfico
        fig = px.line(
            vendas_por_dia,
            x='Data',
            y=COL_VALOR_PEDIDO_CUSTOS,
            title='Evolução de Vendas ao Longo do Tempo',
            labels={COL_VALOR_PEDIDO_CUSTOS: 'Valor Total (R$)'},
            markers=True
        )
        
        # Adicionar área sob a linha
        fig.add_trace(
            go.Scatter(
                x=vendas_por_dia['Data'],
                y=vendas_por_dia[COL_VALOR_PEDIDO_CUSTOS],
                fill='tozeroy',
                fillcolor='rgba(67, 97, 238, 0.2)',
                line=dict(color=primary_color),
                mode='lines+markers',
                name='Vendas'
            )
        )
        
        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="Valor Total (R$)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=50, b=50, l=10, r=10)
        )
        
        # Formatação do eixo Y para moeda
        fig.update_yaxes(tickprefix="R$ ", tickformat=",.2f")
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Dados insuficientes para gerar o gráfico de evolução de vendas.")

def handle_map_click(chart_data):
    if chart_data and chart_data.get('points') and len(chart_data['points']) > 0:
        point = chart_data['points'][0]
        if 'customdata' in point and isinstance(point['customdata'], (list, tuple)) and len(point['customdata']) >= 4:
            st.session_state.selected_state = {'estado': point['customdata'][0], 'detalhes_json': point['customdata'][3]}; return True
    return False

def display_alerts_tab(df_alert_src_main, categoria=None):
    # Filtrar por categoria se necessário
    if categoria and categoria != "Todos" and COL_TIPO_VENDA in df_alert_src_main.columns:
        df_alert_src_main = df_alert_src_main[df_alert_src_main[COL_TIPO_VENDA] == categoria].copy()
    
    col1_alert_final, col2_alert_final = st.columns([1, 3])
    with col1_alert_final:
        with st.container(border=False, key="alert_filter_container"):
            st.markdown("### Filtros de Alertas")
            tipo_alerta_final = st.radio("Tipo de Alerta", ["Todos", "Margens Críticas", "Estoque Parado", "Concorrência de Vendedores", "Alta Performance"], index=0, key="alert_tipo_radio_final_v14")
            opts_mp_alert = ["Todos"] + (sorted(list(df_alert_src_main[COL_PLATAFORMA_CUSTOS].unique())) if COL_PLATAFORMA_CUSTOS in df_alert_src_main.columns else [])
            mp_filtro_alert_final = st.selectbox("Marketplace", opts_mp_alert, index=0, key="alert_mp_select_final_v14")
            opts_conta_alert = ["Todos"] + (sorted(list(df_alert_src_main[COL_CONTA_CUSTOS_ORIGINAL].unique())) if COL_CONTA_CUSTOS_ORIGINAL in df_alert_src_main.columns else [])
            conta_filtro_alert_final = st.selectbox("Conta", opts_conta_alert, index=0, key="alert_conta_select_final_v14")
            
            # Campo de busca para produtos nos alertas
            busca_produto_alerta = st.text_input("🔍 Buscar produto", placeholder="SKU, ID ou nome...", key="busca_produto_alerta")
            
            st.markdown("### Ordenação")
            opts_sort_alert = ["Margem", "SKU", "Conta", "Marketplace", "Estoque", "Vendedores Ativos"]
            idx_sort_by_alert_final = opts_sort_alert.index(st.session_state.alert_sort_by) if st.session_state.alert_sort_by in opts_sort_alert else 0
            st.session_state.alert_sort_by = st.selectbox("Ordenar por", opts_sort_alert, index=idx_sort_by_alert_final, key="alert_sort_by_select_final_v14")
            idx_sort_order_alert_final = ["Crescente", "Decrescente"].index(st.session_state.alert_sort_order) if st.session_state.alert_sort_order in ["Crescente", "Decrescente"] else 0
            st.session_state.alert_sort_order = st.radio("Ordem", ["Crescente", "Decrescente"], index=idx_sort_order_alert_final, horizontal=True, key="alert_sort_order_radio_final_v14")
    with col2_alert_final:
        df_alertas_build_final = df_alert_src_main.copy()
        if tipo_alerta_final == "Margens Críticas" and "Margem_Critica" in df_alertas_build_final.columns: df_alertas_build_final = df_alertas_build_final[df_alertas_build_final["Margem_Critica"] == True]
        elif tipo_alerta_final == "Estoque Parado" and "Estoque_Parado_Alerta" in df_alertas_build_final.columns: df_alertas_build_final = df_alertas_build_final[df_alertas_build_final["Estoque_Parado_Alerta"] == True]
        elif tipo_alerta_final == "Concorrência de Vendedores" and "Status_Vendedores_ML" in df_alertas_build_final.columns: df_alertas_build_final = df_alertas_build_final[df_alertas_build_final["Status_Vendedores_ML"] == "🔴"] 
        elif tipo_alerta_final == "Alta Performance" and "Margem_Num" in df_alertas_build_final.columns: df_alertas_build_final = df_alertas_build_final[df_alertas_build_final["Margem_Num"] > 20]
        if mp_filtro_alert_final != "Todos" and COL_PLATAFORMA_CUSTOS in df_alertas_build_final.columns: df_alertas_build_final = df_alertas_build_final[df_alertas_build_final[COL_PLATAFORMA_CUSTOS] == mp_filtro_alert_final]
        if conta_filtro_alert_final != "Todos" and COL_CONTA_CUSTOS_ORIGINAL in df_alertas_build_final.columns: df_alertas_build_final = df_alertas_build_final[df_alertas_build_final[COL_CONTA_CUSTOS_ORIGINAL] == conta_filtro_alert_final]
        
        cols_alert_final_show = [COL_SKU_CUSTOS, COL_ID_PRODUTO_CUSTOS, COL_CONTA_CUSTOS_ORIGINAL, COL_PLATAFORMA_CUSTOS, "Margem_Original", "Estoque Tiny", "Estoque Total Full", "Status_Vendedores_ML"]
        cols_exist_alert_final = [c for c in cols_alert_final_show if c in df_alertas_build_final.columns]
        df_show_alert_final = pd.DataFrame()
        if cols_exist_alert_final and not df_alertas_build_final.empty: df_show_alert_final = df_alertas_build_final[cols_exist_alert_final].drop_duplicates()
        
        with st.container(border=False, key="alert_table_container"):
            if df_show_alert_final.empty: 
                st.info("Nenhum alerta para os filtros selecionados.")
            else:
                # Renomear colunas para exibição - CORRIGIDO para evitar duplicatas
                rename_map = {
                    COL_SKU_CUSTOS: "SKU", 
                    COL_ID_PRODUTO_CUSTOS: "ID do Produto", 
                    COL_CONTA_CUSTOS_ORIGINAL: "Conta", 
                    COL_PLATAFORMA_CUSTOS: "Marketplace", 
                    "Margem_Original": "Margem", 
                    "Estoque Total Full": "Estoque Total Full ML", 
                    "Status_Vendedores_ML": "Vendedores Ativos"
                }
                
                # Aplicar renomeação apenas para colunas que existem
                rename_map_filtered = {k: v for k, v in rename_map.items() if k in df_show_alert_final.columns}
                df_show_alert_final = df_show_alert_final.rename(columns=rename_map_filtered)
                
                # Verificar se há colunas duplicadas após renomeação
                if df_show_alert_final.columns.duplicated().any():
                    # Remover colunas duplicadas
                    df_show_alert_final = df_show_alert_final.loc[:, ~df_show_alert_final.columns.duplicated()]
                
                # Aplicar filtro de busca se houver texto
                busca_aplicada = False
                if busca_produto_alerta:
                    busca_lower = busca_produto_alerta.lower()
                    mask = pd.Series(False, index=df_show_alert_final.index)
                    
                    # Buscar em todas as colunas de texto
                    for col in df_show_alert_final.columns:
                        # Converter para string e aplicar busca case-insensitive
                        if df_show_alert_final[col].dtype == object:  # Apenas colunas de texto
                            mask = mask | df_show_alert_final[col].astype(str).str.lower().str.contains(busca_lower, na=False)
                    
                    df_show_alert_final_filtrado = df_show_alert_final[mask]
                    
                    if df_show_alert_final_filtrado.empty:
                        st.warning(f"Nenhum produto encontrado com o termo '{busca_produto_alerta}'.")
                    else:
                        busca_aplicada = True
                        df_show_alert_final = df_show_alert_final_filtrado
                        st.success(f"Encontrado(s) {len(df_show_alert_final)} produto(s) com o termo '{busca_produto_alerta}'.")
                
                # Exibir título com contagem de itens
                st.markdown(f"### Tabela de Alertas ({len(df_show_alert_final)} itens)")
                
                # Ordenação
                sort_map_final_alert = {
                    "Margem": "Margem", 
                    "SKU": "SKU", 
                    "Conta": "Conta", 
                    "Marketplace": "Marketplace", 
                    "Estoque": "Estoque Tiny", 
                    "Vendedores Ativos": "Vendedores Ativos"
                } 
                
                sort_col_final_alert = st.session_state.alert_sort_by 
                if sort_col_final_alert in sort_map_final_alert and sort_map_final_alert[sort_col_final_alert] in df_show_alert_final.columns:
                    actual_sort_final_alert = sort_map_final_alert[sort_col_final_alert]
                    asc_final_alert = st.session_state.alert_sort_order == "Crescente" 
                    
                    if actual_sort_final_alert == "Margem":
                        try: 
                            df_show_alert_final["_MSort_"] = df_show_alert_final["Margem"].astype(str).str.rstrip('%').str.replace(',', '.', regex=False).astype(float)
                            df_show_alert_final = df_show_alert_final.sort_values("_MSort_", ascending=asc_final_alert, na_position='last').drop("_MSort_", axis=1)
                        except: 
                            df_show_alert_final = df_show_alert_final.sort_values(actual_sort_final_alert, ascending=asc_final_alert, na_position='last')
                    else: 
                        df_show_alert_final = df_show_alert_final.sort_values(actual_sort_final_alert, ascending=asc_final_alert, na_position='last')
                elif 'SKU' in df_show_alert_final.columns: 
                    df_show_alert_final = df_show_alert_final.sort_values('SKU', ascending=True, na_position='last')
                
                # Formatação
                fmt_dict_final_alert_show = {c: "{:.0f}" for c in df_show_alert_final.columns if "Estoque" in c} 
                style_final_alert_show = df_show_alert_final.style 
                
                if 'Margem' in df_show_alert_final.columns: 
                    style_final_alert_show = style_final_alert_show.apply(
                        lambda s: [f'color: {get_margin_color(float(str(v).replace("%","").replace(",",".")) if isinstance(v,str) and "%" in v else 0)}; font-weight: bold' for v in s], 
                        subset=['Margem']
                    )
                
                st.dataframe(style_final_alert_show.format(fmt_dict_final_alert_show, na_rep="-"), use_container_width=True)

def display_admin_panel():
    st.title("🔧 Painel de Administração")
    usuarios_admin_panel_fn_v9 = carregar_usuarios()
    tab_u_fn_v9, tab_c_fn_v9, tab_l_fn_v9 = st.tabs(["👥 Gerenciar Usuários", "⚙️ Configurações", "📊 Logs"])
    with tab_u_fn_v9:
        st.subheader("Gerenciar Usuários"); st.markdown("### Usuários Cadastrados")
        if usuarios_admin_panel_fn_v9:
            usuarios_df_fn_v9 = pd.DataFrame([
                {"Usuário": user, "Função": data.get("role", "user")}
                for user, data in usuarios_admin_panel_fn_v9.items()
            ])
            st.dataframe(usuarios_df_fn_v9, use_container_width=True)
        else: st.info("Nenhum usuário cadastrado.")
        
        with st.expander("Adicionar Novo Usuário", expanded=False):
            novo_usuario_fn_v9 = st.text_input("Nome de Usuário", key="novo_usuario_admin_v9")
            nova_senha_fn_v9 = st.text_input("Senha", type="password", key="nova_senha_admin_v9")
            nova_funcao_fn_v9 = st.selectbox("Função", ["user", "admin"], key="nova_funcao_admin_v9")
            if st.button("Adicionar Usuário", key="btn_add_user_admin_v9"):
                if novo_usuario_fn_v9 and nova_senha_fn_v9:
                    if novo_usuario_fn_v9 in usuarios_admin_panel_fn_v9:
                        st.error(f"Usuário '{novo_usuario_fn_v9}' já existe.")
                    else:
                        usuarios_admin_panel_fn_v9[novo_usuario_fn_v9] = {"senha": nova_senha_fn_v9, "role": nova_funcao_fn_v9}
                        salvar_usuarios(usuarios_admin_panel_fn_v9)
                        st.success(f"Usuário '{novo_usuario_fn_v9}' adicionado com sucesso!")
                        st.rerun()
                else: st.warning("Preencha todos os campos.")
        
        with st.expander("Remover Usuário", expanded=False):
            usuarios_para_remover_fn_v9 = list(usuarios_admin_panel_fn_v9.keys())
            if usuarios_para_remover_fn_v9:
                usuario_remover_fn_v9 = st.selectbox("Selecione o Usuário", usuarios_para_remover_fn_v9, key="usuario_remover_admin_v9")
                if st.button("Remover Usuário", key="btn_remove_user_admin_v9"):
                    if usuario_remover_fn_v9 == "admin":
                        st.error("Não é possível remover o usuário administrador padrão.")
                    else:
                        del usuarios_admin_panel_fn_v9[usuario_remover_fn_v9]
                        salvar_usuarios(usuarios_admin_panel_fn_v9)
                        st.success(f"Usuário '{usuario_remover_fn_v9}' removido com sucesso!")
                        st.rerun()
            else: st.info("Nenhum usuário disponível para remoção.")
    
    with tab_c_fn_v9:
        st.subheader("Configurações do Sistema")
        st.info("Esta seção permite configurar parâmetros do sistema.")
        
        # Exemplo de configurações
        with st.expander("Configurações de Exibição", expanded=True):
            st.checkbox("Mostrar alertas na página inicial", value=True, key="config_show_alerts_admin_v9")
            st.checkbox("Habilitar modo escuro", value=False, key="config_dark_mode_admin_v9")
            st.slider("Número máximo de itens por página", 10, 100, 50, key="config_items_per_page_admin_v9")
        
        with st.expander("Configurações de Notificação", expanded=False):
            st.checkbox("Enviar notificações por e-mail", value=False, key="config_email_notif_admin_v9")
            st.text_input("E-mail para notificações", key="config_email_address_admin_v9")
            st.multiselect("Tipos de notificação", ["Margens Críticas", "Estoque Baixo", "Novos Pedidos", "Concorrência"], default=["Margens Críticas"], key="config_notif_types_admin_v9")
        
        if st.button("Salvar Configurações", key="btn_save_config_admin_v9"):
            st.success("Configurações salvas com sucesso!")
    
    with tab_l_fn_v9:
        st.subheader("Logs do Sistema")
        st.info("Esta seção exibe logs e atividades do sistema.")
        
        # Exemplo de logs
        log_data_fn_v9 = [
            {"Data": "2023-05-28 14:30:22", "Usuário": "admin", "Ação": "Login no sistema", "Status": "Sucesso"},
            {"Data": "2023-05-28 14:35:10", "Usuário": "admin", "Ação": "Upload de planilha", "Status": "Sucesso"},
            {"Data": "2023-05-28 15:12:45", "Usuário": "user1", "Ação": "Exportação de relatório", "Status": "Sucesso"},
            {"Data": "2023-05-28 16:05:33", "Usuário": "user2", "Ação": "Alteração de configurações", "Status": "Falha"},
            {"Data": "2023-05-28 16:30:18", "Usuário": "admin", "Ação": "Adição de usuário", "Status": "Sucesso"}
        ]
        
        log_df_fn_v9 = pd.DataFrame(log_data_fn_v9)
        st.dataframe(log_df_fn_v9, use_container_width=True)
        
        col1_log_fn_v9, col2_log_fn_v9 = st.columns(2)
        with col1_log_fn_v9:
            st.download_button("Exportar Logs", log_df_fn_v9.to_csv(index=False), "logs_sistema.csv", "text/csv", key="btn_export_logs_admin_v9")
        with col2_log_fn_v9:
            st.button("Limpar Logs", key="btn_clear_logs_admin_v9")

def display_sidebar_filters(df):
    """
    Exibe filtros na barra lateral, adaptados à categoria selecionada
    """
    with st.sidebar:
        st.markdown("<div class='sidebar-title'>Filtros</div>", unsafe_allow_html=True)
        
        # Seleção de período
        st.markdown("<div class='sidebar-text'>### Período</div>", unsafe_allow_html=True)
        periodo_opcoes = ["7 dias", "15 dias", "30 dias", "90 dias", "Personalizado"]
        periodo_selecionado = st.radio("Selecione o período", periodo_opcoes, index=periodo_opcoes.index(st.session_state.periodo_selecionado) if st.session_state.periodo_selecionado in periodo_opcoes else 2, key="periodo_radio_v11")
        
        if periodo_selecionado != st.session_state.periodo_selecionado:
            st.session_state.periodo_selecionado = periodo_selecionado
            hoje = datetime.now().date()
            if periodo_selecionado == "7 dias": st.session_state.data_inicio_analise_state = hoje - timedelta(days=6)
            elif periodo_selecionado == "15 dias": st.session_state.data_inicio_analise_state = hoje - timedelta(days=14)
            elif periodo_selecionado == "30 dias": st.session_state.data_inicio_analise_state = hoje - timedelta(days=29)
            elif periodo_selecionado == "90 dias": st.session_state.data_inicio_analise_state = hoje - timedelta(days=89)
            st.session_state.data_fim_analise_state = hoje
            # Forçar reprocessamento quando o período mudar
            # st.session_state.dummy_rerun_counter += 1 # Não é mais necessário aqui
            st.rerun() # Garantir rerun explícito
        
        if periodo_selecionado == "Personalizado":
            col1_date, col2_date = st.columns(2)
            with col1_date: data_inicio = st.date_input("De", value=st.session_state.data_inicio_analise_state, key="data_inicio_v11")
            with col2_date: data_fim = st.date_input("Até", value=st.session_state.data_fim_analise_state, key="data_fim_v11")
            if data_inicio and data_fim:
                if data_inicio > data_fim: st.error("Data inicial deve ser anterior à data final.")
                else:
                    # Verificar se as datas mudaram antes de atualizar
                    if data_inicio != st.session_state.data_inicio_analise_state or data_fim != st.session_state.data_fim_analise_state:
                        st.session_state.data_inicio_analise_state = data_inicio
                        st.session_state.data_fim_analise_state = data_fim
                        # Forçar reprocessamento quando as datas personalizadas mudarem
                        # st.session_state.dummy_rerun_counter += 1 # Não é mais necessário aqui
                        st.rerun() # Garantir rerun explícito
        
        # Filtros específicos por categoria
        if st.session_state.categoria_selecionada == "Marketplaces":
            st.markdown("<div class='sidebar-text'>### Filtros de Marketplace</div>", unsafe_allow_html=True)
            
            # Filtro de marketplace
            marketplace_options = ["Todos"]
            if df is not None and COL_PLATAFORMA_CUSTOS in df.columns:
                marketplace_options.extend(sorted(df[COL_PLATAFORMA_CUSTOS].unique()))
            
            marketplace_selecionado = st.selectbox(
                "Marketplace", 
                marketplace_options,
                index=marketplace_options.index(st.session_state.marketplace_selecionado_state) if st.session_state.marketplace_selecionado_state in marketplace_options else 0,
                key="marketplace_select_v11"
            )
            
            if marketplace_selecionado != st.session_state.marketplace_selecionado_state:
                st.session_state.marketplace_selecionado_state = marketplace_selecionado
                st.session_state.dummy_rerun_counter += 1
            
            # Filtros específicos para Mercado Livre
            if marketplace_selecionado == "Mercado Livre":
                st.markdown("<div class='sidebar-text'>#### Filtros Mercado Livre</div>", unsafe_allow_html=True)
                
                ml_tipo_anuncio_options = ["Todos"]
                if df is not None and 'Tipo de Anúncio' in df.columns:
                    ml_df = df[df[COL_PLATAFORMA_CUSTOS] == "Mercado Livre"]
                    if not ml_df.empty:
                        ml_tipo_anuncio_options.extend(sorted(ml_df['Tipo de Anúncio'].unique()))
                
                ml_tipo_anuncio = st.selectbox(
                    "Tipo de Anúncio", 
                    ml_tipo_anuncio_options,
                    index=ml_tipo_anuncio_options.index(st.session_state.ml_tipo_anuncio_selecionado) if st.session_state.ml_tipo_anuncio_selecionado in ml_tipo_anuncio_options else 0,
                    key="ml_tipo_anuncio_select_v11"
                )
                
                if ml_tipo_anuncio != st.session_state.ml_tipo_anuncio_selecionado:
                    st.session_state.ml_tipo_anuncio_selecionado = ml_tipo_anuncio
                    st.session_state.dummy_rerun_counter += 1
        
        elif st.session_state.categoria_selecionada == "Atacado":
            st.markdown("<div class='sidebar-text'>### Filtros de Atacado</div>", unsafe_allow_html=True)
            
            # Filtro de região
            regioes = ["Todas", "Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
            regiao_selecionada = st.selectbox("Região", regioes, key="regiao_select_atacado_v11")
            
            # Filtro de valor mínimo
            valor_minimo = st.number_input("Valor Mínimo de Pedido", min_value=0, value=0, step=100, key="valor_minimo_atacado_v11")
            
            # Filtro de tipo de cliente
            tipo_cliente = st.radio("Tipo de Cliente", ["Todos", "PJ", "PF"], key="tipo_cliente_atacado_v11")
        
        elif st.session_state.categoria_selecionada == "Showroom":
            st.markdown("<div class='sidebar-text'>### Filtros de Showroom</div>", unsafe_allow_html=True)
            
            # Filtro de localização
            localizacoes = ["Todas", "São Paulo", "Rio de Janeiro", "Belo Horizonte", "Outras"]
            localizacao_selecionada = st.selectbox("Localização", localizacoes, key="localizacao_select_showroom_v11")
            
            # Filtro de vendedor
            vendedores = ["Todos", "Carlos", "Ana", "Pedro", "Mariana", "João"]
            vendedor_selecionado = st.selectbox("Vendedor", vendedores, key="vendedor_select_showroom_v11")
            
            # Filtro de método de pagamento
            metodos_pagamento = ["Todos", "Cartão de Crédito", "Pix", "Boleto", "Dinheiro", "Transferência"]
            metodo_pagamento_selecionado = st.selectbox("Método de Pagamento", metodos_pagamento, key="metodo_pagamento_showroom_v11")
        
        # Filtros comuns a todas as categorias
        st.markdown("<div class='sidebar-text'>### Filtros Gerais</div>", unsafe_allow_html=True)
        
        # Filtro de conta
        conta_options = ["Todas"]
        if df is not None and COL_CONTA_CUSTOS_ORIGINAL in df.columns:
            conta_options.extend(sorted(df[COL_CONTA_CUSTOS_ORIGINAL].unique()))
        
        conta_selecionada = st.selectbox(
            "Conta", 
            conta_options,
            index=conta_options.index(st.session_state.conta_mae_selecionada_ui_state) if st.session_state.conta_mae_selecionada_ui_state in conta_options else 0,
            key="conta_select_v11"
        )
        
        if conta_selecionada != st.session_state.conta_mae_selecionada_ui_state:
            st.session_state.conta_mae_selecionada_ui_state = conta_selecionada
            st.session_state.dummy_rerun_counter += 1
        
        # Filtro de tipo de margem
        tipo_margem_options = ["Margem Estratégica (L)", "Margem Real (M)"]
        tipo_margem_selecionada = st.radio(
            "Tipo de Margem", 
            tipo_margem_options,
            index=tipo_margem_options.index(st.session_state.tipo_margem_selecionada_state) if st.session_state.tipo_margem_selecionada_state in tipo_margem_options else 0,
            key="tipo_margem_radio_v11"
        )
        
        if tipo_margem_selecionada != st.session_state.tipo_margem_selecionada_state:
            st.session_state.tipo_margem_selecionada_state = tipo_margem_selecionada
            # Atualizar margem sem reprocessar todos os dados
            if st.session_state.df_result is not None:
                st.session_state.df_result = atualizar_margem_sem_reprocessamento(
                    st.session_state.df_result, 
                    tipo_margem_selecionada
                )
            st.session_state.dummy_rerun_counter += 1

def display_custom_menu():
    """
    Exibe menu de navegação personalizado sem dependências externas
    """
    with st.sidebar:
        st.markdown("<div class='sidebar-title'>ViaFlix Dashboard</div>", unsafe_allow_html=True)
        
        # Opções do menu
        menu_options = [
            {"id": "Dashboard", "icon": "📊", "label": "Dashboard"},
            {"id": "Marketplaces", "icon": "🛒", "label": "Marketplaces"},
            {"id": "Atacado", "icon": "🚚", "label": "Atacado"},
            {"id": "Showroom", "icon": "🏪", "label": "Showroom"},
            {"id": "Admin", "icon": "⚙️", "label": "Admin"}
        ]
        
        # Exibir opções do menu
        for option in menu_options:
            is_active = st.session_state.categoria_selecionada == option["id"]
            active_class = "active" if is_active else ""
            
            if st.sidebar.button(
                f"{option['icon']} {option['label']}", 
                key=f"menu_{option['id']}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.categoria_selecionada = option["id"]
                st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)

def main():
    # Verificar autenticação
    if not st.session_state.authenticated:
        display_login_screen()
        return
    
    # Verificar estado da aplicação
    if st.session_state.app_state == "upload":
        uploaded_file = display_welcome_screen()
        if uploaded_file:
            st.session_state.app_state = "dashboard"
            
            # Adicionar indicador de loading durante o processamento da planilha
            with st.spinner("Processando planilha... Por favor, aguarde."):
                st.session_state.df_result = processar_planilha_otimizado(
                    uploaded_file, 
                    st.session_state.tipo_margem_selecionada_state,
                    st.session_state.data_inicio_analise_state,
                    st.session_state.data_fim_analise_state,
                    COL_MARGEM_ESTRATEGICA_PLANILHA_CUSTOS,
                    COL_MARGEM_REAL_PLANILHA_CUSTOS,
                    COL_TIPO_ANUNCIO_ML_CUSTOS,
                    st.session_state.dummy_rerun_counter
                )
            st.rerun()
        return
    
    # Dashboard principal
    if st.session_state.app_state == "dashboard" and st.session_state.df_result is not None:
        # Barra lateral com menu de navegação personalizado
        display_custom_menu()
        
        # Mostrar filtros apenas se não estiver no painel de administração
        if st.session_state.categoria_selecionada != "Admin":
            display_sidebar_filters(st.session_state.df_result)
        
        # Conteúdo principal
        if st.session_state.categoria_selecionada == "Admin":
            # Verificar permissões de administrador
            if st.session_state.user_role == "admin":
                display_admin_panel()
            else:
                st.error("Você não tem permissão para acessar o painel de administração.")
        else:
            # Aplicar filtro de período ANTES de qualquer exibição
            df_completo = st.session_state.df_result.copy()
            if COL_DATA_CUSTOS in df_completo.columns:
                df_completo[COL_DATA_CUSTOS] = pd.to_datetime(df_completo[COL_DATA_CUSTOS], errors='coerce')
                df_completo.dropna(subset=[COL_DATA_CUSTOS], inplace=True)
                
                data_inicio_filtro = st.session_state.data_inicio_analise_state
                data_fim_filtro = st.session_state.data_fim_analise_state
                
                # Garantir que sejam objetos date
                if isinstance(data_inicio_filtro, datetime):
                    data_inicio_filtro = data_inicio_filtro.date()
                if isinstance(data_fim_filtro, datetime):
                    data_fim_filtro = data_fim_filtro.date()
                
                # Aplicar filtro de data
                df_filtered_by_date = df_completo[
                    (df_completo[COL_DATA_CUSTOS].dt.date >= data_inicio_filtro) & 
                    (df_completo[COL_DATA_CUSTOS].dt.date <= data_fim_filtro)
                ].copy()
            else:
                df_filtered_by_date = df_completo # Sem coluna de data, usar completo
            
            # Filtrar dados conforme a categoria selecionada (usando df_filtered_by_date)
            df_filtered = df_filtered_by_date.copy()
            
            # Aplicar filtros comuns
            if st.session_state.conta_mae_selecionada_ui_state != "Todas" and COL_CONTA_CUSTOS_ORIGINAL in df_filtered.columns:
                df_filtered = df_filtered[df_filtered[COL_CONTA_CUSTOS_ORIGINAL] == st.session_state.conta_mae_selecionada_ui_state]
            
            # Aplicar filtros específicos para Marketplaces
            if st.session_state.categoria_selecionada == "Marketplaces":
                # Filtrar apenas dados de Marketplaces
                if COL_TIPO_VENDA in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered[COL_TIPO_VENDA] == "Marketplaces"]
                
                # Aplicar filtro de marketplace
                if st.session_state.marketplace_selecionado_state != "Todos" and COL_PLATAFORMA_CUSTOS in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered[COL_PLATAFORMA_CUSTOS] == st.session_state.marketplace_selecionado_state]
                
                # Aplicar filtro de tipo de anúncio para Mercado Livre
                if st.session_state.marketplace_selecionado_state == "Mercado Livre" and st.session_state.ml_tipo_anuncio_selecionado != "Todos" and 'Tipo de Anúncio' in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered['Tipo de Anúncio'] == st.session_state.ml_tipo_anuncio_selecionado]
            
            # Aplicar filtros específicos para Atacado
            elif st.session_state.categoria_selecionada == "Atacado":
                # Filtrar apenas dados de Atacado
                if COL_TIPO_VENDA in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered[COL_TIPO_VENDA] == "Atacado"]
            
            # Aplicar filtros específicos para Showroom
            elif st.session_state.categoria_selecionada == "Showroom":
                # Filtrar apenas dados de Showroom
                if COL_TIPO_VENDA in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered[COL_TIPO_VENDA] == "Showroom"]
                   # Dashboard principal (consolidado)
            if st.session_state.categoria_selecionada == "Dashboard":
                st.title("Dashboard de Performance ViaFlix")
                
                # Métricas gerais (usando dados filtrados por data)
                display_metrics(df_filtered_by_date, st.session_state.tipo_margem_selecionada_state)
                
                # Gráfico de evolução temporal (usando dados filtrados por data)
                st.markdown("### Evolução de Vendas")
                display_time_series_chart(df_filtered_by_date)
                
                # Distribuição por tipo de venda (usando dados filtrados por data)
                if COL_TIPO_VENDA in df_filtered_by_date.columns:
                    st.markdown("### Distribuição por Tipo de Venda")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Gráfico de pizza por tipo de venda
                        tipo_venda_counts = df_filtered_by_date[COL_TIPO_VENDA].value_counts().reset_index()
                        tipo_venda_counts.columns = ['Tipo de Venda', 'Contagem']
                        fig = px.pie(
                            tipo_venda_counts, 
                            values='Contagem', 
                            names='Tipo de Venda',
                            title='Distribuição por Tipo de Venda',
                            color_discrete_sequence=px.colors.sequential.Blues_r,
                            hole=0.4
                        )                        
                        fig.update_layout(
                            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                            margin=dict(t=50, b=50, l=10, r=10)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Valor total por tipo de venda
                        if COL_VALOR_PEDIDO_CUSTOS in df_filtered_by_date.columns:
                            tipo_venda_valor = df_filtered_by_date.groupby(COL_TIPO_VENDA)[COL_VALOR_PEDIDO_CUSTOS].sum().reset_index()
                            tipo_venda_valor.columns = ["Tipo de Venda", "Valor Total"]                         
                            fig = px.bar(
                                tipo_venda_valor,
                                x='Tipo de Venda',
                                y='Valor Total',
                                title='Valor Total por Tipo de Venda',
                                color='Valor Total',
                                color_continuous_scale='Blues'
                            )                   
                            fig.update_layout(
                                xaxis_title="",
                                yaxis_title="Valor Total (R$)",
                                coloraxis_showscale=False,
                                margin=dict(t=50, b=50, l=10, r=10)
                            )
                            fig.update_traces(
                                texttemplate='R$ %{y:,.2f}',
                                textposition='outside'
                            )                            
                            # Formatação do eixo Y para moeda
                            fig.update_yaxes(tickprefix="R$ ", tickformat=",.2f")
                            
                            st.plotly_chart(fig, use_container_width=True)
                
               
                # Abas para diferentes visualizações
                tab1, tab2, tab3 = st.tabs(["📊 Análise de Produtos", "⚠️ Alertas", "📈 Tendências"])
                
                with tab1:
                    st.markdown("### Análise de Produtos")
                    
                    # Campo de busca para produtos
                    busca_produto = st.text_input("🔍 Buscar produto (SKU, ID ou nome)", placeholder="Digite para buscar...")
                    
                    # Tabela personalizada (usando dados filtrados por data)
                    df_tabela = personalizar_tabela_por_marketplace(df_filtered_by_date, "Todos", st.session_state.tipo_margem_selecionada_state)
                    
                    # Atualizar tabela com o tipo de margem selecionado
                    df_tabela = atualizar_tabela_com_nova_margem(df_tabela, st.session_state.tipo_margem_selecionada_state)
                    
                    if not df_tabela.empty:
                        # Verificar e remover colunas duplicadas
                        if df_tabela.columns.duplicated().any():
                            df_tabela = df_tabela.loc[:, ~df_tabela.columns.duplicated()]
                        
                        # Aplicar filtro de busca se houver texto
                        if busca_produto:
                            busca_lower = busca_produto.lower()
                            mask = pd.Series(False, index=df_tabela.index)
                            
                            # Buscar em todas as colunas de texto
                            for col in df_tabela.columns:
                                # Converter para string e aplicar busca case-insensitive
                                if df_tabela[col].dtype == object:  # Apenas colunas de texto
                                    mask = mask | df_tabela[col].astype(str).str.lower().str.contains(busca_lower, na=False)
                            
                            df_tabela_filtrada = df_tabela[mask]
                            
                            if df_tabela_filtrada.empty:
                                st.warning(f"Nenhum produto encontrado com o termo \'{busca_produto}\'.")
                                st.dataframe(df_tabela, use_container_width=True)
                            else:
                                st.success(f"Encontrado(s) {len(df_tabela_filtrada)} produto(s) com o termo \'{busca_produto}\'.")
                                st.dataframe(df_tabela_filtrada, use_container_width=True)
                        else:
                            st.dataframe(df_tabela, use_container_width=True)
                    else:
                        st.info("Sem dados para exibir na tabela de produtos.")
                
                with tab2:
                    # Alertas (usando dados filtrados por data)
                    display_alerts_tab(df_filtered_by_date)
                
                with tab3:
                    st.markdown("### Tendências de Vendas")
                    
                  
            
            # Dashboard específico para Marketplaces
            elif st.session_state.categoria_selecionada == "Marketplaces":
                st.title("Dashboard de Marketplaces")
                
                # Métricas específicas para Marketplaces
                display_metrics(df_filtered, st.session_state.tipo_margem_selecionada_state, "Marketplaces")
                
                # Gráficos específicos para Marketplaces
                display_category_specific_metrics(df_filtered, "Marketplaces")
                
                # Evolução temporal para Marketplaces
                st.markdown("### Evolução de Vendas em Marketplaces")
                display_time_series_chart(df_filtered, "Marketplaces")
                
                # Abas para diferentes visualizações
                tab1, tab2, tab3 = st.tabs(["📊 Produtos", "⚠️ Alertas", "🔍 Concorrência"])
                
                with tab1:
                    st.markdown("### Produtos em Marketplaces")
                    
                    # Tabela personalizada
                    df_tabela = personalizar_tabela_por_marketplace(df_filtered, st.session_state.marketplace_selecionado_state, st.session_state.tipo_margem_selecionada_state)
                    
                    # Atualizar tabela com o tipo de margem selecionado
                    df_tabela = atualizar_tabela_com_nova_margem(df_tabela, st.session_state.tipo_margem_selecionada_state)
                    
                    if not df_tabela.empty:
                        # Verificar e remover colunas duplicadas
                        if df_tabela.columns.duplicated().any():
                            df_tabela = df_tabela.loc[:, ~df_tabela.columns.duplicated()]
                        
                        st.dataframe(df_tabela, use_container_width=True)
                    else:
                        st.info("Sem dados para exibir na tabela de produtos.")
                
                with tab2:
                    display_alerts_tab(df_filtered, "Marketplaces")
                
                with tab3:
                    st.markdown("### Análise de Concorrência")
                    
                    # Simulação de dados de concorrência
                    st.info("Esta seção mostra a análise de concorrência nos marketplaces.")
                    
                    # Exemplo de gráfico de concorrência
                    concorrentes = ['Concorrente A', 'Concorrente B', 'Concorrente C', 'Concorrente D', 'ViaFlix']
                    precos = [89.90, 92.50, 99.90, 85.00, 94.90]
                    
                    fig = px.bar(
                        x=concorrentes,
                        y=precos,
                        title='Comparação de Preços com Concorrentes (Produto Exemplo)',
                        color=concorrentes,
                        color_discrete_sequence=[secondary_color, secondary_color, secondary_color, secondary_color, primary_color]
                    )
                    
                    fig.update_layout(
                        xaxis_title="",
                        yaxis_title="Preço Médio (R$)",
                        showlegend=False,
                        margin=dict(t=50, b=50, l=10, r=10)
                    )
                    
                    fig.update_traces(
                        texttemplate='R$ %{y:.2f}',
                        textposition='outside'
                    )
                    
                    # Formatação do eixo Y para moeda
                    fig.update_yaxes(tickprefix="R$ ", tickformat=",.2f")
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Dashboard específico para Atacado
            elif st.session_state.categoria_selecionada == "Atacado":
                st.title("Dashboard de Atacado")
                
                # Métricas específicas para Atacado
                display_metrics(df_filtered, st.session_state.tipo_margem_selecionada_state, "Atacado")
                
                # Gráficos específicos para Atacado
                display_category_specific_metrics(df_filtered, "Atacado")
                
                # Evolução temporal para Atacado
                st.markdown("### Evolução de Vendas no Atacado")
                display_time_series_chart(df_filtered, "Atacado")
                
                # Mapa do Brasil específico para Atacado
                st.markdown("### Mapa de Vendas por Estado - Atacado")
                mapa_fig = criar_mapa_brasil_interativo(df_filtered)
                if mapa_fig:
                    mapa_chart = st.plotly_chart(mapa_fig, use_container_width=True, key="mapa_brasil_atacado_chart")
                    if st.session_state.selected_state:
                        exibir_detalhes_estado(st.session_state.selected_state['estado'], st.session_state.selected_state['detalhes_json'])
                        if st.button("Fechar Detalhes", key="btn_fechar_detalhes_atacado"):
                            st.session_state.selected_state = None
                            st.rerun()
                
                # Abas para diferentes visualizações
                tab1, tab2 = st.tabs(["📊 Produtos", "⚠️ Alertas"])
                
                with tab1:
                    st.markdown("### Produtos no Atacado")
                    
                    # Tabela personalizada
                    df_tabela = personalizar_tabela_por_marketplace(df_filtered, "Todos", st.session_state.tipo_margem_selecionada_state)
                    
                    # Atualizar tabela com o tipo de margem selecionado
                    df_tabela = atualizar_tabela_com_nova_margem(df_tabela, st.session_state.tipo_margem_selecionada_state)
                    
                    if not df_tabela.empty:
                        # Verificar e remover colunas duplicadas
                        if df_tabela.columns.duplicated().any():
                            df_tabela = df_tabela.loc[:, ~df_tabela.columns.duplicated()]
                        
                        st.dataframe(df_tabela, use_container_width=True)
                    else:
                        st.info("Sem dados para exibir na tabela de produtos.")
                
                with tab2:
                    display_alerts_tab(df_filtered, "Atacado")
            
            # Dashboard específico para Showroom
            elif st.session_state.categoria_selecionada == "Showroom":
                st.title("Dashboard de Showroom")
                
                # Métricas específicas para Showroom
                display_metrics(df_filtered, st.session_state.tipo_margem_selecionada_state, "Showroom")
                
                # Gráficos específicos para Showroom
                display_category_specific_metrics(df_filtered, "Showroom")
                
                # Evolução temporal para Showroom
                st.markdown("### Evolução de Vendas no Showroom")
                display_time_series_chart(df_filtered, "Showroom")
                
                # Abas para diferentes visualizações
                tab1, tab2, tab3 = st.tabs(["📊 Produtos", "⚠️ Alertas", "👥 Vendedores"])
                
                with tab1:
                    st.markdown("### Produtos no Showroom")
                    
                    # Tabela personalizada
                    df_tabela = personalizar_tabela_por_marketplace(df_filtered, "Todos", st.session_state.tipo_margem_selecionada_state)
                    
                    # Atualizar tabela com o tipo de margem selecionado
                    df_tabela = atualizar_tabela_com_nova_margem(df_tabela, st.session_state.tipo_margem_selecionada_state)
                    
                    if not df_tabela.empty:
                        # Verificar e remover colunas duplicadas
                        if df_tabela.columns.duplicated().any():
                            df_tabela = df_tabela.loc[:, ~df_tabela.columns.duplicated()]
                        
                        st.dataframe(df_tabela, use_container_width=True)
                    else:
                        st.info("Sem dados para exibir na tabela de produtos.")
                
                with tab2:
                    display_alerts_tab(df_filtered, "Showroom")
                
                with tab3:
                    st.markdown("### Desempenho de Vendedores")
                    
                    # Simulação de dados de vendedores
                    vendedores = ['Carlos', 'Ana', 'Pedro', 'Mariana', 'João']
                    vendas = [np.random.randint(50000, 150000) for _ in range(5)]
                    metas = [100000, 120000, 90000, 110000, 80000]
                    
                    # Calcular percentual de atingimento da meta
                    atingimento = [(v / m) * 100 for v, m in zip(vendas, metas)]
                    
                    # Criar DataFrame
                    vendedores_df = pd.DataFrame({
                        'Vendedor': vendedores,
                        'Vendas': vendas,
                        'Meta': metas,
                        'Atingimento (%)': atingimento
                    })
                    
                    # Formatar valores
                    vendedores_df['Vendas'] = vendedores_df['Vendas'].apply(lambda x: f"R$ {x:,.2f}")
                    vendedores_df['Meta'] = vendedores_df['Meta'].apply(lambda x: f"R$ {x:,.2f}")
                    vendedores_df['Atingimento (%)'] = vendedores_df['Atingimento (%)'].apply(lambda x: f"{x:.1f}%")
                    
                    # Exibir tabela
                    st.dataframe(vendedores_df, use_container_width=True)
                    
                    # Gráfico de atingimento de metas
                    fig = go.Figure()
                    
                    for i, vendedor in enumerate(vendedores):
                        fig.add_trace(
                            go.Bar(
                                x=[vendedor],
                                y=[atingimento[i]],
                                name=vendedor,
                                text=f"{atingimento[i]:.1f}%",
                                textposition='outside',
                                marker_color=primary_color if atingimento[i] >= 100 else warning_color if atingimento[i] >= 80 else danger_color
                            )
                        )
                    
                    # Adicionar linha de 100%
                    fig.add_shape(
                        type="line",
                        x0=-0.5,
                        y0=100,
                        x1=len(vendedores) - 0.5,
                        y1=100,
                        line=dict(
                            color="red",
                            width=2,
                            dash="dash",
                        )
                    )
                    
                    fig.update_layout(
                        title='Atingimento de Metas por Vendedor',
                        xaxis_title="",
                        yaxis_title="Atingimento (%)",
                        showlegend=False,
                        margin=dict(t=50, b=50, l=10, r=10)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
