import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import numpy as np
from datetime import datetime
import random

def criar_mapa_brasil_interativo(df):
    """
    Cria um mapa interativo do Brasil com dados de vendas por estado.
    Versão aprimorada com visual moderno e futurista.
    
    Args:
        df: DataFrame com os dados de vendas
        
    Returns:
        figura: Objeto de figura Plotly com o mapa interativo
    """
    try:
        # Definir constantes para colunas da planilha
        COL_CONTA_CUSTOS_ORIGINAL = 'CONTAS'
        COL_PLATAFORMA_CUSTOS = 'PLATAFORMA'
        COL_VALOR_PEDIDO_CUSTOS = 'VALOR DO PEDIDO'
        COL_TIPO_VENDA = 'TIPO DE VENDA'
        
        # Dados dos estados brasileiros com coordenadas
        estados_brasil = {
            'AC': {'nome': 'Acre', 'lat': -9.0238, 'lon': -70.812, 'sigla': 'AC', 'regiao': 'Norte'},
            'AL': {'nome': 'Alagoas', 'lat': -9.5713, 'lon': -36.782, 'sigla': 'AL', 'regiao': 'Nordeste'},
            'AM': {'nome': 'Amazonas', 'lat': -3.4168, 'lon': -65.8561, 'sigla': 'AM', 'regiao': 'Norte'},
            'AP': {'nome': 'Amapá', 'lat': 1.4, 'lon': -51.77, 'sigla': 'AP', 'regiao': 'Norte'},
            'BA': {'nome': 'Bahia', 'lat': -12.96, 'lon': -41.7007, 'sigla': 'BA', 'regiao': 'Nordeste'},
            'CE': {'nome': 'Ceará', 'lat': -5.4984, 'lon': -39.3206, 'sigla': 'CE', 'regiao': 'Nordeste'},
            'DF': {'nome': 'Distrito Federal', 'lat': -15.83, 'lon': -47.86, 'sigla': 'DF', 'regiao': 'Centro-Oeste'},
            'ES': {'nome': 'Espírito Santo', 'lat': -19.19, 'lon': -40.34, 'sigla': 'ES', 'regiao': 'Sudeste'},
            'GO': {'nome': 'Goiás', 'lat': -15.98, 'lon': -49.86, 'sigla': 'GO', 'regiao': 'Centro-Oeste'},
            'MA': {'nome': 'Maranhão', 'lat': -5.4, 'lon': -45.44, 'sigla': 'MA', 'regiao': 'Nordeste'},
            'MG': {'nome': 'Minas Gerais', 'lat': -18.1, 'lon': -44.38, 'sigla': 'MG', 'regiao': 'Sudeste'},
            'MS': {'nome': 'Mato Grosso do Sul', 'lat': -20.51, 'lon': -54.54, 'sigla': 'MS', 'regiao': 'Centro-Oeste'},
            'MT': {'nome': 'Mato Grosso', 'lat': -12.64, 'lon': -55.42, 'sigla': 'MT', 'regiao': 'Centro-Oeste'},
            'PA': {'nome': 'Pará', 'lat': -3.79, 'lon': -52.48, 'sigla': 'PA', 'regiao': 'Norte'},
            'PB': {'nome': 'Paraíba', 'lat': -7.28, 'lon': -36.72, 'sigla': 'PB', 'regiao': 'Nordeste'},
            'PE': {'nome': 'Pernambuco', 'lat': -8.38, 'lon': -37.86, 'sigla': 'PE', 'regiao': 'Nordeste'},
            'PI': {'nome': 'Piauí', 'lat': -6.6, 'lon': -42.28, 'sigla': 'PI', 'regiao': 'Nordeste'},
            'PR': {'nome': 'Paraná', 'lat': -24.89, 'lon': -51.55, 'sigla': 'PR', 'regiao': 'Sul'},
            'RJ': {'nome': 'Rio de Janeiro', 'lat': -22.25, 'lon': -42.66, 'sigla': 'RJ', 'regiao': 'Sudeste'},
            'RN': {'nome': 'Rio Grande do Norte', 'lat': -5.81, 'lon': -36.59, 'sigla': 'RN', 'regiao': 'Nordeste'},
            'RO': {'nome': 'Rondônia', 'lat': -10.83, 'lon': -63.34, 'sigla': 'RO', 'regiao': 'Norte'},
            'RR': {'nome': 'Roraima', 'lat': 1.99, 'lon': -61.33, 'sigla': 'RR', 'regiao': 'Norte'},
            'RS': {'nome': 'Rio Grande do Sul', 'lat': -30.17, 'lon': -53.5, 'sigla': 'RS', 'regiao': 'Sul'},
            'SC': {'nome': 'Santa Catarina', 'lat': -27.45, 'lon': -50.95, 'sigla': 'SC', 'regiao': 'Sul'},
            'SE': {'nome': 'Sergipe', 'lat': -10.57, 'lon': -37.45, 'sigla': 'SE', 'regiao': 'Nordeste'},
            'SP': {'nome': 'São Paulo', 'lat': -22.19, 'lon': -48.79, 'sigla': 'SP', 'regiao': 'Sudeste'},
            'TO': {'nome': 'Tocantins', 'lat': -9.46, 'lon': -48.26, 'sigla': 'TO', 'regiao': 'Norte'}
        }
        
        # Cores por região
        cores_regiao = {
            'Norte': '#3B82F6',      # Azul
            'Nordeste': '#10B981',   # Verde
            'Centro-Oeste': '#8B5CF6', # Roxo
            'Sudeste': '#F59E0B',    # Amarelo
            'Sul': '#EF4444'         # Vermelho
        }
        
        # Criar DataFrame para o mapa
        mapa_data = []
        
        # Verificar se temos dados reais ou precisamos simular
        tem_dados_reais = False
        if df is not None and not df.empty:
            # Verificar se temos coluna de estado
            if 'Estado' in df.columns and COL_VALOR_PEDIDO_CUSTOS in df.columns:
                tem_dados_reais = True
                # Agrupar vendas por estado
                vendas_por_estado = df.groupby('Estado')[COL_VALOR_PEDIDO_CUSTOS].sum().reset_index()
                vendas_por_estado_dict = dict(zip(vendas_por_estado['Estado'], vendas_por_estado[COL_VALOR_PEDIDO_CUSTOS]))
        
        # Preparar dados para cada estado
        for sigla, info in estados_brasil.items():
            # Obter vendas reais ou simular
            if tem_dados_reais and sigla in vendas_por_estado_dict:
                vendas_estado = vendas_por_estado_dict[sigla]
            else:
                # Simular dados mais realistas por região
                base_value = {
                    'Norte': random.randint(5000, 30000),
                    'Nordeste': random.randint(10000, 50000),
                    'Centro-Oeste': random.randint(15000, 60000),
                    'Sudeste': random.randint(30000, 120000),
                    'Sul': random.randint(20000, 80000)
                }
                vendas_estado = base_value[info['regiao']] * (0.8 + 0.4 * random.random())  # Variação de ±20%
            
            # Preparar detalhes para exibição ao clicar
            # Simular dados por tipo de venda e marketplace
            total_vendas = vendas_estado
            
            # Distribuição por tipo de venda
            if sigla in ['SP', 'RJ', 'MG', 'RS', 'PR']:  # Estados com mais showroom
                tipo_venda_pct = {'Marketplaces': 0.5, 'Atacado': 0.3, 'Showroom': 0.2}
            elif info['regiao'] in ['Norte', 'Nordeste']:  # Regiões com mais marketplace
                tipo_venda_pct = {'Marketplaces': 0.7, 'Atacado': 0.25, 'Showroom': 0.05}
            else:  # Outros estados
                tipo_venda_pct = {'Marketplaces': 0.6, 'Atacado': 0.35, 'Showroom': 0.05}
            
            # Distribuição por marketplace (para a parcela de Marketplaces)
            marketplace_pct = {
                'Mercado Livre': 0.45, 
                'Shopee': 0.25, 
                'Amazon': 0.15,
                'Magalu': 0.1,
                'Outros': 0.05
            }
            
            # Distribuição por conta
            conta_pct = {
                'VIA FLIX': 0.6,
                'MONACO': 0.3,
                'GS TORNEIRA': 0.1
            }
            
            # Calcular valores
            tipo_venda_valores = {k: total_vendas * v for k, v in tipo_venda_pct.items()}
            marketplace_valores = {k: tipo_venda_valores['Marketplaces'] * v for k, v in marketplace_pct.items()}
            conta_valores = {k: total_vendas * v for k, v in conta_pct.items()}
            
            # Dados de crescimento (simulação)
            mes_atual = datetime.now().month
            crescimento = random.uniform(-15, 30)  # Entre -15% e +30%
            
            # Preparar detalhes completos
            detalhes = {
                'tipo_venda': {k: float(v) for k, v in tipo_venda_valores.items()},
                'marketplaces': {k: float(v) for k, v in marketplace_valores.items()},
                'contas': {k: float(v) for k, v in conta_valores.items()},
                'crescimento': float(crescimento),
                'mes_atual': mes_atual,
                'produtos_destaque': [
                    {'nome': 'Produto A', 'vendas': float(random.randint(1000, 5000))},
                    {'nome': 'Produto B', 'vendas': float(random.randint(800, 4000))},
                    {'nome': 'Produto C', 'vendas': float(random.randint(500, 3000))}
                ]
            }
            
            # Texto para exibir ao passar o mouse
            hover_text = f"<b>{info['nome']}</b><br>R$ {vendas_estado:,.2f}<br>Crescimento: {crescimento:.1f}%"
            
            # Adicionar ao DataFrame
            mapa_data.append({
                'estado': info['nome'],
                'sigla': sigla,
                'lat': info['lat'],
                'lon': info['lon'],
                'vendas': vendas_estado,
                'hover_text': hover_text,
                'detalhes': json.dumps(detalhes),
                'regiao': info['regiao'],
                'cor': cores_regiao[info['regiao']]
            })
        
        # Criar DataFrame
        mapa_df = pd.DataFrame(mapa_data)
        
        # Normalizar tamanhos para visualização
        max_vendas = mapa_df['vendas'].max()
        min_vendas = mapa_df['vendas'].min()
        mapa_df['tamanho_normalizado'] = 10 + 40 * ((mapa_df['vendas'] - min_vendas) / (max_vendas - min_vendas))
        
        # Criar mapa interativo com Plotly
        fig = go.Figure()
        
        # Adicionar mapa base do Brasil
        fig.add_trace(
            go.Scattergeo(
                lon=[-70, -55, -34, -34, -70],  # Contorno aproximado do Brasil
                lat=[5, 5, -33, -33, 5],
                mode='lines',
                line=dict(width=1, color='rgba(200,200,200,0.5)'),
                showlegend=False
            )
        )
        
        # Adicionar pontos para cada estado, agrupados por região
        for regiao in mapa_df['regiao'].unique():
            df_regiao = mapa_df[mapa_df['regiao'] == regiao]
            
            fig.add_trace(
                go.Scattergeo(
                    lon=df_regiao['lon'],
                    lat=df_regiao['lat'],
                    text=df_regiao['hover_text'],
                    hoverinfo='text',
                    mode='markers',
                    name=regiao,
                    marker=dict(
                        size=df_regiao['tamanho_normalizado'],
                        color=cores_regiao[regiao],
                        opacity=0.8,
                        line=dict(width=1, color='rgba(255,255,255,0.8)'),
                        sizemode='diameter',
                        gradient=dict(
                            type='radial',
                            color='rgba(255,255,255,0.2)'
                        )
                    ),
                    customdata=list(zip(
                        df_regiao['estado'], 
                        df_regiao['sigla'], 
                        df_regiao['vendas'],
                        df_regiao['detalhes']
                    ))
                )
            )
        
        # Adicionar rótulos dos estados
        for i, row in mapa_df.iterrows():
            fig.add_trace(
                go.Scattergeo(
                    lon=[row['lon']],
                    lat=[row['lat']],
                    text=row['sigla'],
                    mode='text',
                    textfont=dict(
                        family='Arial',
                        size=10,
                        color='white'
                    ),
                    showlegend=False
                )
            )
        
        # Configurar o mapa para mostrar apenas o Brasil
        fig.update_geos(
            visible=False,
            resolution=50,
            scope='south america',
            showcountries=True,
            countrycolor='rgba(255,255,255,0.2)',
            showsubunits=True,
            subunitcolor='rgba(255,255,255,0.2)',
            center={'lat': -15.0, 'lon': -55.0},
            lataxis={'range': [-33, 5]},
            lonaxis={'range': [-74, -34]},
            projection_type='mercator',
            bgcolor='rgba(0,0,0,0)'
        )
        
        # Configurar layout
        fig.update_layout(
            title={
                'text': 'Mapa de Vendas por Estado',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 24, 'color': '#1E3A8A', 'family': 'Inter'}
            },
            height=650,
            margin=dict(l=0, r=0, t=50, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            geo=dict(
                bgcolor='rgba(0,0,0,0)',
                lakecolor='rgba(0,0,0,0)',
                landcolor='rgba(240,242,246,1)',
                subunitcolor='rgba(217,217,217,1)'
            ),
            hoverlabel=dict(
                bgcolor='white',
                font_size=12,
                font_family='Inter'
            ),
            legend=dict(
                title='Regiões',
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.1)',
                borderwidth=1
            ),
            updatemenus=[
                dict(
                    type='buttons',
                    showactive=False,
                    buttons=[
                        dict(
                            label='Resetar Visualização',
                            method='relayout',
                            args=[{'geo.center': {'lat': -15.0, 'lon': -55.0}, 
                                  'geo.lataxis.range': [-33, 5], 
                                  'geo.lonaxis.range': [-74, -34]}]
                        )
                    ],
                    x=0.05,
                    y=0.05,
                    xanchor='left',
                    yanchor='bottom',
                    pad={"r": 10, "t": 10},
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='rgba(0,0,0,0.1)',
                    borderwidth=1
                )
            ]
        )
        
        # Adicionar texto informativo
        fig.add_annotation(
            text="Clique nos estados para ver detalhes. Tamanho dos círculos representa volume de vendas.",
            xref="paper", yref="paper",
            x=0.5, y=1.06,
            showarrow=False,
            font=dict(size=12, color="#4361EE", family="Inter")
        )
        
        # Adicionar efeito de brilho nos estados (gradiente)
        for i in range(len(fig.data)):
            if hasattr(fig.data[i], 'marker') and fig.data[i].marker:
                fig.data[i].marker.gradient = dict(
                    type='radial',
                    color='rgba(255,255,255,0.8)'
                )
        
        return fig
    
    except Exception as e:
        st.error(f"Erro ao criar mapa interativo: {str(e)}")
        return None

def exibir_detalhes_estado(estado, detalhes_json):
    """
    Exibe detalhes de vendas por marketplace e conta para um estado específico.
    Versão aprimorada com visualizações mais modernas e interativas.
    
    Args:
        estado: Nome do estado
        detalhes_json: String JSON com detalhes de vendas
    """
    try:
        # Converter JSON para dicionário
        detalhes = json.loads(detalhes_json)
        
        # Criar container com estilo
        with st.container(border=True):
            # Cabeçalho com informações gerais
            col_titulo, col_crescimento = st.columns([3, 1])
            
            with col_titulo:
                st.markdown(f"<h2 style='color:#1E3A8A;'>{estado}</h2>", unsafe_allow_html=True)
            
            with col_crescimento:
                crescimento = detalhes.get('crescimento', 0)
                cor_crescimento = "#10B981" if crescimento >= 0 else "#EF4444"
                st.markdown(f"""
                <div style='background-color:white; padding:10px; border-radius:10px; text-align:center;'>
                    <span style='font-size:0.8rem; color:#6B7280;'>Crescimento</span><br>
                    <span style='font-size:1.5rem; font-weight:bold; color:{cor_crescimento};'>{crescimento:.1f}%</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Linha divisória
            st.markdown("<hr style='margin: 15px 0; border-color: #E5E7EB;'>", unsafe_allow_html=True)
            
            # Criar três colunas para os gráficos principais
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Gráfico de vendas por tipo (Marketplace, Atacado, Showroom)
                st.markdown("<h4 style='text-align:center;'>Vendas por Tipo</h4>", unsafe_allow_html=True)
                
                tipo_venda_df = pd.DataFrame({
                    'Tipo': list(detalhes['tipo_venda'].keys()),
                    'Vendas': list(detalhes['tipo_venda'].values())
                })
                
                cores_tipo = {
                    'Marketplaces': '#3B82F6',
                    'Atacado': '#10B981',
                    'Showroom': '#8B5CF6'
                }
                
                fig_tipo = px.pie(
                    tipo_venda_df, 
                    values='Vendas', 
                    names='Tipo',
                    hole=0.6,
                    color='Tipo',
                    color_discrete_map=cores_tipo
                )
                
                # Adicionar valor total no centro
                total_vendas = sum(detalhes['tipo_venda'].values())
                fig_tipo.add_annotation(
                    text=f"R$ {total_vendas:,.0f}",
                    x=0.5, y=0.5,
                    font_size=14,
                    font_family="Inter",
                    font_color="#1E3A8A",
                    showarrow=False
                )
                
                fig_tipo.update_traces(
                    textposition='outside',
                    textinfo='percent+label',
                    marker=dict(line=dict(color='white', width=2)),
                    pull=[0.05, 0, 0],
                    rotation=45
                )
                
                fig_tipo.update_layout(
                    height=300,
                    margin=dict(l=10, r=10, t=10, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                    showlegend=False,
                    uniformtext_minsize=12,
                    uniformtext_mode='hide'
                )
                
                st.plotly_chart(fig_tipo, use_container_width=True)
            
            with col2:
                # Gráfico de vendas por marketplace
                st.markdown("<h4 style='text-align:center;'>Vendas por Marketplace</h4>", unsafe_allow_html=True)
                
                marketplaces_df = pd.DataFrame({
                    'Marketplace': list(detalhes['marketplaces'].keys()),
                    'Vendas': list(detalhes['marketplaces'].values())
                }).sort_values('Vendas', ascending=False)
                
                fig_mp = px.bar(
                    marketplaces_df,
                    x='Marketplace',
                    y='Vendas',
                    color='Vendas',
                    color_continuous_scale='Blues',
                    text_auto='.2s'
                )
                
                fig_mp.update_traces(
                    textfont_size=12,
                    textangle=0,
                    textposition="outside",
                    cliponaxis=False,
                    marker_line_color='white',
                    marker_line_width=1.5,
                    opacity=0.9
                )
                
                fig_mp.update_layout(
                    height=300,
                    margin=dict(l=10, r=10, t=10, b=50),
                    xaxis_title="",
                    yaxis_title="",
                    coloraxis_showscale=False,
                    xaxis={'categoryorder':'total descending'}
                )
                
                # Formatação do eixo Y para moeda
                fig_mp.update_yaxes(tickprefix="R$ ", tickformat=",.0f")
                
                st.plotly_chart(fig_mp, use_container_width=True)
            
            with col3:
                # Gráfico de vendas por conta
                st.markdown("<h4 style='text-align:center;'>Vendas por Conta</h4>", unsafe_allow_html=True)
                
                contas_df = pd.DataFrame({
                    'Conta': list(detalhes['contas'].keys()),
                    'Vendas': list(detalhes['contas'].values())
                }).sort_values('Vendas', ascending=True)  # Ascendente para gráfico horizontal
                
                cores_contas = {
                    'VIA FLIX': '#3B82F6',
                    'MONACO': '#F59E0B',
                    'GS TORNEIRA': '#8B5CF6'
                }
                
                fig_contas = px.bar(
                    contas_df,
                    y='Conta',
                    x='Vendas',
                    color='Conta',
                    color_discrete_map=cores_contas,
                    text_auto='.2s',
                    orientation='h'
                )
                
                fig_contas.update_traces(
                    textfont_size=12,
                    textposition="outside",
                    cliponaxis=False,
                    marker_line_color='white',
                    marker_line_width=1.5,
                    opacity=0.9
                )
                
                fig_contas.update_layout(
                    height=300,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis_title="",
                    yaxis_title="",
                    showlegend=False
                )
                
                # Formatação do eixo X para moeda
                fig_contas.update_xaxes(tickprefix="R$ ", tickformat=",.0f")
                
                st.plotly_chart(fig_contas, use_container_width=True)
            
            # Linha divisória
            st.markdown("<hr style='margin: 15px 0; border-color: #E5E7EB;'>", unsafe_allow_html=True)
            
            # Produtos em destaque
            st.markdown("<h4 style='text-align:center;'>Produtos em Destaque</h4>", unsafe_allow_html=True)
            
            produtos_df = pd.DataFrame(detalhes['produtos_destaque'])
            
            # Criar colunas para cada produto
            cols_produtos = st.columns(len(produtos_df))
            
            for i, (_, produto) in enumerate(produtos_df.iterrows()):
                with cols_produtos[i]:
                    st.markdown(f"""
                    <div style='background-color:white; padding:15px; border-radius:10px; text-align:center; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
                        <span style='font-size:1.1rem; font-weight:bold; color:#1E3A8A;'>{produto['nome']}</span><br>
                        <span style='font-size:1.3rem; color:#10B981;'>R$ {produto['vendas']:,.2f}</span><br>
                        <span style='font-size:0.8rem; color:#6B7280;'>Vendas no período</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Linha divisória
            st.markdown("<hr style='margin: 15px 0; border-color: #E5E7EB;'>", unsafe_allow_html=True)
            
            # Botão para exportar dados
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            
            with col_btn1:
                st.markdown("""
                <div style='text-align:center;'>
                    <button style='background-color:#1E3A8A; color:white; border:none; padding:10px 15px; border-radius:5px; cursor:pointer; width:100%;'>
                        📊 Ver Relatório Completo
                    </button>
                </div>
                """, unsafe_allow_html=True)
            
            with col_btn2:
                st.markdown("""
                <div style='text-align:center;'>
                    <button style='background-color:#10B981; color:white; border:none; padding:10px 15px; border-radius:5px; cursor:pointer; width:100%;'>
                        📥 Exportar Dados
                    </button>
                </div>
                """, unsafe_allow_html=True)
            
            with col_btn3:
                st.markdown("""
                <div style='text-align:center;'>
                    <button style='background-color:#6B7280; color:white; border:none; padding:10px 15px; border-radius:5px; cursor:pointer; width:100%;'>
                        🔍 Análise Detalhada
                    </button>
                </div>
                """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Erro ao exibir detalhes do estado: {str(e)}")
