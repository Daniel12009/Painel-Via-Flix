import streamlit as st
import pandas as pd
import numpy as np

def personalizar_tabela_por_marketplace(df, marketplace_selecionado, tipo_margem):
    """
    Personaliza a tabela de produtos com base no marketplace selecionado.
    
    Args:
        df: DataFrame com os dados
        marketplace_selecionado: Marketplace selecionado no filtro
        tipo_margem: Tipo de margem selecionada (Estratégica ou Real)
        
    Returns:
        DataFrame: DataFrame personalizado para exibição
    """
    # Definir constantes para colunas da planilha
    COL_SKU_CUSTOS = 'SKU PRODUTOS'
    COL_CONTA_CUSTOS_ORIGINAL = 'CONTAS'
    COL_PLATAFORMA_CUSTOS = 'PLATAFORMA'
    COL_ID_PRODUTO_CUSTOS = 'ID DO PRODUTO'
    COL_VALOR_PRODUTO_PLANILHA_CUSTOS = 'PREÇO UND'
    
    # Verificar se df é um DataFrame ou uma Series
    if isinstance(df, pd.Series):
        # Converter Series para DataFrame
        df = pd.DataFrame([df])
    
    # Filtrar por marketplace se necessário
    if marketplace_selecionado != "Todos":
        df = df[df[COL_PLATAFORMA_CUSTOS] == marketplace_selecionado]
    
    # Verificar se o DataFrame está vazio após filtro
    if df.empty:
        return pd.DataFrame(columns=[COL_SKU_CUSTOS, COL_CONTA_CUSTOS_ORIGINAL, COL_PLATAFORMA_CUSTOS, 'Margem', COL_VALOR_PRODUTO_PLANILHA_CUSTOS])
    
    # Selecionar colunas relevantes com base no marketplace
    colunas_base = [
        COL_SKU_CUSTOS,
        COL_ID_PRODUTO_CUSTOS,
        COL_CONTA_CUSTOS_ORIGINAL,
        COL_PLATAFORMA_CUSTOS,
        'Margem_Original',  # Usar a margem já formatada
        COL_VALOR_PRODUTO_PLANILHA_CUSTOS
    ]
    
    # Adicionar colunas de estoque
    colunas_estoque = [col for col in df.columns if "Estoque" in col]
    colunas_selecionadas = colunas_base + colunas_estoque
    
    # Adicionar colunas específicas para Mercado Livre
    if marketplace_selecionado == "Mercado Livre":
        if 'Tipo de Anúncio' in df.columns:
            colunas_selecionadas.append('Tipo de Anúncio')
    
    # Selecionar apenas as colunas que existem no DataFrame
    colunas_existentes = [col for col in colunas_selecionadas if col in df.columns]
    df_personalizado = df[colunas_existentes].copy()
    
    # Remover duplicatas
    df_personalizado = df_personalizado.drop_duplicates(subset=[COL_SKU_CUSTOS, COL_CONTA_CUSTOS_ORIGINAL, COL_PLATAFORMA_CUSTOS])
    
    # Renomear colunas para melhor visualização
    mapeamento_colunas = {
        COL_SKU_CUSTOS: 'SKU',
        COL_ID_PRODUTO_CUSTOS: 'ID do Produto',
        COL_CONTA_CUSTOS_ORIGINAL: 'Conta',
        COL_PLATAFORMA_CUSTOS: 'Marketplace',
        'Margem_Original': 'Margem',
        COL_VALOR_PRODUTO_PLANILHA_CUSTOS: 'Preço'
    }
    
    # Aplicar renomeação apenas para colunas que existem
    mapeamento_filtrado = {k: v for k, v in mapeamento_colunas.items() if k in df_personalizado.columns}
    df_personalizado = df_personalizado.rename(columns=mapeamento_filtrado)
    
    return df_personalizado
