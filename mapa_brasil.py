import streamlit as st
import pandas as pd
import plotly.express as px
import json
import numpy as np

def criar_mapa_brasil_interativo(df):
    """
    Cria um mapa interativo do Brasil com dados de vendas por estado.
    
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
        
        # Dados dos estados brasileiros com coordenadas
        estados_brasil = {
            'AC': {'nome': 'Acre', 'lat': -9.0238, 'lon': -70.812, 'sigla': 'AC'},
            'AL': {'nome': 'Alagoas', 'lat': -9.5713, 'lon': -36.782, 'sigla': 'AL'},
            'AM': {'nome': 'Amazonas', 'lat': -3.4168, 'lon': -65.8561, 'sigla': 'AM'},
            'AP': {'nome': 'Amapá', 'lat': 1.4, 'lon': -51.77, 'sigla': 'AP'},
            'BA': {'nome': 'Bahia', 'lat': -12.96, 'lon': -41.7007, 'sigla': 'BA'},
            'CE': {'nome': 'Ceará', 'lat': -5.4984, 'lon': -39.3206, 'sigla': 'CE'},
            'DF': {'nome': 'Distrito Federal', 'lat': -15.83, 'lon': -47.86, 'sigla': 'DF'},
            'ES': {'nome': 'Espírito Santo', 'lat': -19.19, 'lon': -40.34, 'sigla': 'ES'},
            'GO': {'nome': 'Goiás', 'lat': -15.98, 'lon': -49.86, 'sigla': 'GO'},
            'MA': {'nome': 'Maranhão', 'lat': -5.4, 'lon': -45.44, 'sigla': 'MA'},
            'MG': {'nome': 'Minas Gerais', 'lat': -18.1, 'lon': -44.38, 'sigla': 'MG'},
            'MS': {'nome': 'Mato Grosso do Sul', 'lat': -20.51, 'lon': -54.54, 'sigla': 'MS'},
            'MT': {'nome': 'Mato Grosso', 'lat': -12.64, 'lon': -55.42, 'sigla': 'MT'},
            'PA': {'nome': 'Pará', 'lat': -3.79, 'lon': -52.48, 'sigla': 'PA'},
            'PB': {'nome': 'Paraíba', 'lat': -7.28, 'lon': -36.72, 'sigla': 'PB'},
            'PE': {'nome': 'Pernambuco', 'lat': -8.38, 'lon': -37.86, 'sigla': 'PE'},
            'PI': {'nome': 'Piauí', 'lat': -6.6, 'lon': -42.28, 'sigla': 'PI'},
            'PR': {'nome': 'Paraná', 'lat': -24.89, 'lon': -51.55, 'sigla': 'PR'},
            'RJ': {'nome': 'Rio de Janeiro', 'lat': -22.25, 'lon': -42.66, 'sigla': 'RJ'},
            'RN': {'nome': 'Rio Grande do Norte', 'lat': -5.81, 'lon': -36.59, 'sigla': 'RN'},
            'RO': {'nome': 'Rondônia', 'lat': -10.83, 'lon': -63.34, 'sigla': 'RO'},
            'RR': {'nome': 'Roraima', 'lat': 1.99, 'lon': -61.33, 'sigla': 'RR'},
            'RS': {'nome': 'Rio Grande do Sul', 'lat': -30.17, 'lon': -53.5, 'sigla': 'RS'},
            'SC': {'nome': 'Santa Catarina', 'lat': -27.45, 'lon': -50.95, 'sigla': 'SC'},
            'SE': {'nome': 'Sergipe', 'lat': -10.57, 'lon': -37.45, 'sigla': 'SE'},
            'SP': {'nome': 'São Paulo', 'lat': -22.19, 'lon': -48.79, 'sigla': 'SP'},
            'TO': {'nome': 'Tocantins', 'lat': -9.46, 'lon': -48.26, 'sigla': 'TO'}
        }
        
        # Criar DataFrame para o mapa
        mapa_data = []
        
        # Simular dados de vendas por estado (na implementação real, isso viria do DataFrame)
        # Aqui vamos usar dados aleatórios para demonstração
        for sigla, info in estados_brasil.items():
            # Filtrar vendas para este estado (simulado)
            # Na implementação real, isso seria baseado em uma coluna de estado no DataFrame
            vendas_estado = np.random.randint(5000, 100000)
            
            # Preparar detalhes para exibição ao clicar
            detalhes = {
                'marketplaces': {
                    'Mercado Livre': np.random.randint(1000, 50000),
                    'Shopee': np.random.randint(1000, 30000),
                    'Amazon': np.random.randint(1000, 20000)
                },
                'contas': {
                    'VIA FLIX': np.random.randint(1000, 40000),
                    'MONACO': np.random.randint(1000, 30000),
                    'OUTRAS': np.random.randint(1000, 10000)
                }
            }
            
            # Texto para exibir ao passar o mouse
            hover_text = f"{info['nome']}: R$ {vendas_estado:,.2f}"
            
            # Adicionar ao DataFrame
            mapa_data.append({
                'estado': info['nome'],
                'sigla': sigla,
                'lat': info['lat'],
                'lon': info['lon'],
                'vendas': vendas_estado,
                'hover_text': hover_text,
                'detalhes': json.dumps(detalhes)
            })
        
        # Criar DataFrame
        mapa_df = pd.DataFrame(mapa_data)
        
        # Criar mapa interativo com Plotly
        fig = px.scatter_geo(
            mapa_df,
            lat='lat',
            lon='lon',
            size='vendas',
            hover_name='hover_text',
            custom_data=['estado', 'sigla', 'vendas', 'detalhes'],
            projection='natural earth',
            size_max=30,
            color_discrete_sequence=['#4361EE'],
            title='Vendas por Estado'
        )
        
        # Configurar o mapa para mostrar apenas o Brasil
        fig.update_geos(
            visible=False,
            resolution=50,
            scope='south america',
            showcountries=True,
            countrycolor='Black',
            showsubunits=True,
            subunitcolor='Black',
            center={'lat': -15.0, 'lon': -55.0},
            lataxis={'range': [-33, 5]},
            lonaxis={'range': [-74, -34]}
        )
        
        # Configurar layout
        fig.update_layout(
            height=600,
            margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            geo=dict(
                bgcolor='rgba(0,0,0,0)',
                lakecolor='rgba(0,0,0,0)',
                landcolor='rgba(240,240,240,1)',
                subunitcolor='rgba(217,217,217,1)'
            ),
            hoverlabel=dict(
                bgcolor='white',
                font_size=12,
                font_family='Poppins'
            )
        )
        
        # Adicionar texto informativo
        fig.add_annotation(
            text="Passe o mouse sobre os estados para ver as vendas. Clique para ver detalhes.",
            xref="paper", yref="paper",
            x=0.5, y=1.05,
            showarrow=False,
            font=dict(size=12, color="#4361EE")
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Erro ao criar mapa interativo: {str(e)}")
        return None

def exibir_detalhes_estado(estado, detalhes_json):
    """
    Exibe detalhes de vendas por marketplace e conta para um estado específico.
    
    Args:
        estado: Nome do estado
        detalhes_json: String JSON com detalhes de vendas
    """
    try:
        # Converter JSON para dicionário
        detalhes = json.loads(detalhes_json)
        
        st.markdown(f"### Detalhes de Vendas: {estado}")
        
        # Criar duas colunas
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de vendas por marketplace
            st.markdown("#### Vendas por Marketplace")
            marketplaces_df = pd.DataFrame({
                'Marketplace': list(detalhes['marketplaces'].keys()),
                'Vendas': list(detalhes['marketplaces'].values())
            })
            
            fig_mp = px.pie(
                marketplaces_df, 
                values='Vendas', 
                names='Marketplace',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            
            fig_mp.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            
            st.plotly_chart(fig_mp, use_container_width=True)
        
        with col2:
            # Gráfico de vendas por conta
            st.markdown("#### Vendas por Conta")
            contas_df = pd.DataFrame({
                'Conta': list(detalhes['contas'].keys()),
                'Vendas': list(detalhes['contas'].values())
            })
            
            fig_contas = px.bar(
                contas_df, 
                x='Conta', 
                y='Vendas',
                color='Vendas',
                color_continuous_scale='Blues',
                text_auto=True
            )
            
            fig_contas.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="",
                yaxis_title="",
                coloraxis_showscale=False
            )
            
            fig_contas.update_traces(
                texttemplate='R$ %{y:,.0f}',
                textposition='outside'
            )
            
            st.plotly_chart(fig_contas, use_container_width=True)
        
        # Tabela com detalhes completos
        st.markdown("#### Tabela Detalhada")
        
        # Criar dados para a tabela
        tabela_data = []
        
        # Adicionar dados de marketplace
        for mp, valor in detalhes['marketplaces'].items():
            tabela_data.append({
                'Categoria': 'Marketplace',
                'Nome': mp,
                'Valor': f"R$ {valor:,.2f}"
            })
        
        # Adicionar dados de contas
        for conta, valor in detalhes['contas'].items():
            tabela_data.append({
                'Categoria': 'Conta',
                'Nome': conta,
                'Valor': f"R$ {valor:,.2f}"
            })
        
        # Criar DataFrame
        tabela_df = pd.DataFrame(tabela_data)
        
        # Exibir tabela
        st.dataframe(tabela_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao exibir detalhes do estado: {str(e)}")
