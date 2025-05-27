import pandas as pd
import streamlit as st
import traceback
from datetime import datetime, timedelta

def processar_planilha_otimizado(uploaded_file, tipo_margem, data_inicio_analise, data_fim_analise):
    """
    Versão otimizada da função processar_planilha para evitar erros de memória e corrigir cálculo.
    Garante que a soma do faturamento seja feita sobre os dados originais filtrados por data,
    e que os merges de estoque não inflem o resultado.
    
    Args:
        uploaded_file: Arquivo Excel carregado ou caminho do arquivo
        tipo_margem: Tipo de margem selecionada (Estratégica ou Real)
        data_inicio_analise: Data inicial do período de análise (objeto date)
        data_fim_analise: Data final do período de análise (objeto date)
        
    Returns:
        DataFrame: DataFrame consolidado com os dados processados
    """
    try:
        # Definir constantes para colunas da planilha
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
        
        # Ler a planilha Excel
        xls = pd.ExcelFile(uploaded_file)
        
        # Verificar se todas as abas necessárias existem
        abas_necessarias = ['CUSTOS', 'ESTOQUE'] # VENDAS não parece ser usada aqui
        for aba in abas_necessarias:
            if aba not in xls.sheet_names:
                st.error(f"A aba '{aba}' não foi encontrada na planilha.")
                return None
        
        # Definir colunas a serem lidas da aba CUSTOS
        colunas_custos_ler = [
            COL_SKU_CUSTOS, 
            COL_DATA_CUSTOS, 
            COL_CONTA_CUSTOS_ORIGINAL,
            COL_PLATAFORMA_CUSTOS,
            COL_MARGEM_ESTRATEGICA_PLANILHA_CUSTOS,
            COL_MARGEM_REAL_PLANILHA_CUSTOS,
            COL_VALOR_PRODUTO_PLANILHA_CUSTOS,
            COL_ID_PRODUTO_CUSTOS,
            COL_QUANTIDADE_CUSTOS_ABA_CUSTOS,
            COL_VALOR_PEDIDO_CUSTOS
        ]
        
        # Ler a aba CUSTOS com otimização de tipos de dados
        dtypes = {
            COL_SKU_CUSTOS: str,
            COL_CONTA_CUSTOS_ORIGINAL: str,
            COL_PLATAFORMA_CUSTOS: str,
            COL_ID_PRODUTO_CUSTOS: str,
            # Deixar valores numéricos serem inferidos ou converter depois
        }
        
        custos_df = pd.read_excel(
            xls, 
            sheet_name='CUSTOS',
            dtype=dtypes,
            usecols=colunas_custos_ler
        )
        
        # --- Pré-processamento CUSTOS ---
        # 1. Converter VALOR DO PEDIDO para numérico IMEDIATAMENTE, tratando erros
        custos_df[COL_VALOR_PEDIDO_CUSTOS] = pd.to_numeric(custos_df[COL_VALOR_PEDIDO_CUSTOS], errors='coerce')
        # Opcional: Remover linhas onde o valor do pedido não é válido, se necessário
        # custos_df.dropna(subset=[COL_VALOR_PEDIDO_CUSTOS], inplace=True)
        
        # 2. Converter coluna de data
        custos_df[COL_DATA_CUSTOS] = pd.to_datetime(custos_df[COL_DATA_CUSTOS], errors='coerce')
        custos_df.dropna(subset=[COL_DATA_CUSTOS], inplace=True) # Remover linhas com data inválida
        
        # 3. Filtrar por período de análise ANTES de qualquer merge
        # Garantir que as datas de análise sejam objetos date
        if isinstance(data_inicio_analise, datetime):
            data_inicio_analise = data_inicio_analise.date()
        if isinstance(data_fim_analise, datetime):
            data_fim_analise = data_fim_analise.date()
            
        custos_df_filtrado = custos_df[
            (custos_df[COL_DATA_CUSTOS].dt.date >= data_inicio_analise) & 
            (custos_df[COL_DATA_CUSTOS].dt.date <= data_fim_analise)
        ].copy() # Usar .copy() para evitar SettingWithCopyWarning
        
        if custos_df_filtrado.empty:
            st.warning(f"Não há dados na aba 'CUSTOS' para o período selecionado: {data_inicio_analise.strftime('%d/%m/%Y')} a {data_fim_analise.strftime('%d/%m/%Y')}")
            return pd.DataFrame() # Retornar DataFrame vazio

        # --- Processamento de Margem ---
        if tipo_margem == "Margem Estratégica (N)":
            col_margem = COL_MARGEM_ESTRATEGICA_PLANILHA_CUSTOS
        else: # "Margem Real (N)"
            col_margem = COL_MARGEM_REAL_PLANILHA_CUSTOS
        
        def converter_margem_para_numero(valor_margem):
            if pd.isna(valor_margem): return 0
            try:
                if isinstance(valor_margem, str) and '%' in valor_margem:
                    valor_str = valor_margem.replace('%', '').strip().replace(',', '.')
                    return float(valor_str)
                if isinstance(valor_margem, (int, float)): return float(valor_margem * 100)
                return float(str(valor_margem).replace(',', '.'))
            except: return 0

        custos_df_filtrado['Margem_Num'] = custos_df_filtrado[col_margem].apply(converter_margem_para_numero)

        def formatar_margem_original(valor):
            if pd.isna(valor): return "0,00%"
            if isinstance(valor, str) and '%' in valor: return valor
            try:
                if isinstance(valor, (int, float)): 
                    valor_percentual = valor * 100 if abs(valor) <= 1 else valor # Trata 0.15 e 15
                else:
                    valor_num = float(str(valor).replace(',', '.'))
                    valor_percentual = valor_num * 100 if abs(valor_num) <= 1 else valor_num
                return f"{valor_percentual:.2f}".replace(".", ",") + "%"
            except: return str(valor) # Retorna como string se falhar

        custos_df_filtrado['Margem_Original'] = custos_df_filtrado[col_margem].apply(formatar_margem_original)
        
        # --- Merges com Estoque ---
        try:
            estoque_df = pd.read_excel(xls, sheet_name='ESTOQUE', dtype={0: str}) # Ler SKU como string
            skus_unicos = custos_df_filtrado[COL_SKU_CUSTOS].unique()
            
            # Mapeamento de colunas de estoque (índice da coluna SKU, índice da coluna Estoque, nome da nova coluna)
            estoque_map = {
                'Estoque Full VF': (0, 1),
                'Estoque Full GS': (3, 4),
                'Estoque Full DK': (6, 7),
                'Estoque Tiny': (9, 10)
            }

            df_merged = custos_df_filtrado.copy() # Trabalhar com cópia para evitar modificar o original durante o loop

            for nome_coluna, (idx_sku, idx_estoque) in estoque_map.items():
                if nome_coluna not in df_merged.columns:
                    try:
                        # Selecionar e renomear colunas de estoque
                        estoque_temp = estoque_df.iloc[:, [idx_sku, idx_estoque]].copy()
                        estoque_temp.columns = ['SKU', nome_coluna]
                        
                        # Remover duplicatas no estoque ANTES do merge, mantendo a primeira ocorrência
                        # Isso evita que um SKU duplicado no estoque cause duplicação de linhas de CUSTOS
                        estoque_temp.drop_duplicates(subset=['SKU'], keep='first', inplace=True)
                        
                        # Filtrar estoque apenas para SKUs relevantes
                        estoque_temp = estoque_temp[estoque_temp['SKU'].isin(skus_unicos)]
                        
                        # Merge 'left' para manter todas as linhas de custos_df_filtrado
                        df_merged = pd.merge(
                            df_merged,
                            estoque_temp,
                            left_on=COL_SKU_CUSTOS,
                            right_on='SKU',
                            how='left' # Mantém todas as linhas de df_merged (custos)
                        )
                        
                        df_merged.drop('SKU', axis=1, inplace=True, errors='ignore')
                        df_merged[nome_coluna] = pd.to_numeric(df_merged[nome_coluna], errors='coerce').fillna(0)
                    except Exception as e:
                        st.warning(f"Não foi possível adicionar coluna '{nome_coluna}': {str(e)}")
                        if nome_coluna not in df_merged.columns:
                             df_merged[nome_coluna] = 0 # Garante que a coluna exista mesmo se o merge falhar
            
            custos_df_final = df_merged

        except Exception as e:
            st.error(f"Erro ao processar a aba 'ESTOQUE' ou realizar merges: {str(e)}")
            st.error(traceback.format_exc())
            # Continuar sem dados de estoque se houver erro, usando o df filtrado original
            custos_df_final = custos_df_filtrado.copy()
            for nome_coluna in estoque_map.keys():
                 if nome_coluna not in custos_df_final.columns:
                     custos_df_final[nome_coluna] = 0

        # --- REMOVIDO: Deduplicação Final Agressiva --- 
        # A deduplicação anterior estava removendo linhas legítimas.
        # A soma deve ser feita sobre o df_merged que contém todas as linhas originais
        # da aba CUSTOS para o período filtrado, apenas enriquecidas com dados de estoque.
        # A deduplicação feita ANTES do merge no lado do estoque já previne a inflação por SKUs duplicados no estoque.
        # st.write(f"(Debug) Linhas ANTES da deduplicação final: {len(custos_df_final)}")
        # custos_df_final.drop_duplicates(subset=colunas_custos_ler, keep='first', inplace=True)
        # st.write(f"(Debug) Linhas DEPOIS da deduplicação final: {len(custos_df_final)}")

        # --- START: Create 'Estoque Full' column based on rules ---
        # Ensure necessary columns exist before proceeding
        # Define COL_CONTA_CUSTOS_ORIGINAL if not globally defined (it seems to be)
        required_cols_for_new_stock = [COL_CONTA_CUSTOS_ORIGINAL, 'Estoque Full VF', 'Estoque Full DK', 'Estoque Full GS']
        source_cols_present_for_new_stock = all(col in custos_df_final.columns for col in required_cols_for_new_stock)

        if source_cols_present_for_new_stock:
            try:
                # Define the conditions
                cond_vf = custos_df_final[COL_CONTA_CUSTOS_ORIGINAL] == 'Via Flix'
                cond_dk = custos_df_final[COL_CONTA_CUSTOS_ORIGINAL] == 'Monaco'
                cond_gs = custos_df_final[COL_CONTA_CUSTOS_ORIGINAL] == 'GS Torneira'

                # Define the choices based on conditions (ensure numeric conversion)
                choices = [
                    pd.to_numeric(custos_df_final['Estoque Full VF'], errors='coerce').fillna(0),
                    pd.to_numeric(custos_df_final['Estoque Full DK'], errors='coerce').fillna(0),
                    pd.to_numeric(custos_df_final['Estoque Full GS'], errors='coerce').fillna(0)
                ]

                # Apply np.select to create the new column
                custos_df_final['Estoque Full'] = np.select(
                    [cond_vf, cond_dk, cond_gs],
                    choices,
                    default=0 # Default value for accounts not matching the rules
                ).astype(int) # Convert result to integer

                # Remove the original individual stock columns used for the new column
                cols_to_drop_individual = ['Estoque Full VF', 'Estoque Full DK', 'Estoque Full GS']
                custos_df_final = custos_df_final.drop(columns=cols_to_drop_individual, errors='ignore') # Use errors='ignore' in case they don't exist

            except Exception as e:
                 st.warning(f"Erro ao criar coluna 'Estoque Full' personalizada: {e}")
                 if 'Estoque Full' not in custos_df_final.columns:
                      custos_df_final['Estoque Full'] = 0 # Default column on error
        elif 'Estoque Full' not in custos_df_final.columns:
             # Check which required columns are missing
             missing_cols_for_new_stock = [col for col in required_cols_for_new_stock if col not in custos_df_final.columns]
             st.warning(f"Não foi possível criar a coluna 'Estoque Full' personalizada. Colunas necessárias ausentes: {missing_cols_for_new_stock}.")
             custos_df_final['Estoque Full'] = 0 # Create default column if logic fails
        # --- END: Create 'Estoque Full' column ---

        # --- Adicionar Colunas Placeholder (se necessário) ---
        # Adicionar coluna de Estoque Total Full para Mercado Livre
        colunas_estoque_full = [col for col in custos_df_final.columns if "Estoque Full" in col]
        if colunas_estoque_full:
            custos_df_final['Estoque Total Full'] = custos_df_final[colunas_estoque_full].sum(axis=1)
        else:
            custos_df_final['Estoque Total Full'] = 0
            
        # Adicionar outras colunas placeholder que podem ser usadas depois
        placeholder_cols = {
            'Devolução': 0,
            'Vendedores Ativos': 0,
            'Alertas': "",
            'Tipo de Anúncio': "Clássico", # Valor padrão
            'Margem_Critica': custos_df_final['Margem_Num'] < 10 if 'Margem_Num' in custos_df_final else False,
            'Estoque_Parado': custos_df_final['Estoque Tiny'] > 10 if 'Estoque Tiny' in custos_df_final else False
        }
        for col, default_val in placeholder_cols.items():
            if col not in custos_df_final.columns:
                custos_df_final[col] = default_val

        # Garantir que a coluna de valor do pedido é numérica antes de retornar
        custos_df_final[COL_VALOR_PEDIDO_CUSTOS] = pd.to_numeric(custos_df_final[COL_VALOR_PEDIDO_CUSTOS], errors='coerce').fillna(0)

        return custos_df_final
    
    except FileNotFoundError:
        st.error(f"Erro: Arquivo da planilha não encontrado.")
        return None
    except KeyError as e:
        st.error(f"Erro: Coluna obrigatória '{e}' não encontrada na planilha. Verifique as abas 'CUSTOS' e 'ESTOQUE'.")
        return None
    except Exception as e:
        st.error(f"Erro inesperado ao processar a planilha: {str(e)}")
        st.error(traceback.format_exc())
        return None

# Função para obter cor com base na margem (mantida igual)
def get_margin_color(margin):
    danger_color = "#EF476F"  # Vermelho
    orange_color = "#FF9800"  # Laranja
    primary_color = "#4361EE"  # Azul
    try:
        margin_value = float(margin)
        if margin_value < 10:
            return danger_color
        elif margin_value < 16:
            return orange_color
        else:
            return primary_color
    except:
        return primary_color

