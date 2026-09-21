import pandas as pd
import re
from pathlib import Path

# 1. Carrega os dois arquivos CSV
pasta_dados = Path(__file__).resolve().parent
df_resolucoes = pd.read_csv(
	pasta_dados / 'DadosResolucoesPorPromotorias - Copia (2).csv'
)
df_promotorias = pd.read_csv(
	pasta_dados / 'DadosResolucoesPorPromotorias - Copia.csv'
)

# 2. Padroniza a coluna usada para relacionar as tabelas
def normalizar_promotoria(coluna):
	return (
		coluna.astype('string')
		.str.strip()
		.map(lambda valor: re.sub(r'(?<=\d)°', 'ª', valor) if pd.notna(valor) else valor)
	)


df_resolucoes['PROMOTORIA'] = normalizar_promotoria(df_resolucoes['PROMOTORIA'])
df_promotorias['nome_promotoria'] = normalizar_promotoria(df_promotorias['nome_promotoria'])
df_promotorias = df_promotorias.rename(columns={'nome_promotoria': 'PROMOTORIA'})

# 3. Adiciona o ID da promotoria a cada resolução
df_resultado = pd.merge(
	df_resolucoes,
	df_promotorias[['PROMOTORIA', 'ID_promotoria']],
	on='PROMOTORIA',
	how='left',
)

# 4. Reordena as colunas para o formato de carregamento
df_resultado = df_resultado.rename(columns={'ID Resolução': 'id_resolucao'})
df_resultado = df_resultado[
	['ID_promotoria', 'id_resolucao', 'PROMOTORIA', 'UNIDADE']
].rename(columns={'ID_promotoria': 'id_promotoria'})

# 5. Exporta o resultado para um novo arquivo CSV
arquivo_saida = pasta_dados / 'resultado_final.csv'
df_resultado.to_csv(arquivo_saida, index=False, encoding='utf-8-sig')
print(f'Arquivo criado: {arquivo_saida}')
print(f'Registros: {len(df_resultado)}')
print(f'Promotorias sem ID: {df_resultado["id_promotoria"].isna().sum()}')