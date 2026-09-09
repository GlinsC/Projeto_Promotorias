import streamlit as st
import pandas as pd
import re
from pathlib import Path

# Set page configuration
st.set_page_config(page_title="Dados Controle Externo", layout="wide")

# Load do csv data com pandas
arquivo_csv = Path(__file__).resolve().parents[1] / "Dados" / "DadosResolucoesPorPromotorias.csv"
dados = pd.read_csv(arquivo_csv, sep=",", encoding="utf-8")

# Arquivos CSS e imagens
pasta_style = Path(__file__).resolve().parents[1] / "Style"
imagemLogoSidebar = pasta_style / "logo_mpal_22.png"
arquivo_css = pasta_style / "Style.css"
css = arquivo_css.read_text(encoding="utf-8")

#Tratamento para corrigir caracteres especiais e normalizar o texto
def corrigir_texto(texto):
	texto = str(texto)
	texto = re.sub(r"(\d+)�(?=\s+PJ|\s+Entr)", r"\1ª", texto)
	texto = re.sub(r"(\d+)�", r"\1º", texto)

	reparos = {
		"N�": "Nº",
		"Entr�ncia": "Entrância",
		"Col�nia": "Colônia",
		"Macei�": "Maceió",
		"S�o": "São",
		"Jos�": "José",
		"P�o": "Pão",
		"�gua": "Água",
		"�ndios": "Índios",
		"Jacar�": "Jacaré",
		"Jacu�pe": "Jacuípe",
		"Jequi�": "Jequié",
		"Pia�abu�u": "Piaçabuçu",
		"Ch�": "Chá",
		"T�tico": "Tático",
		"Se��o": "Seção",
		"Prote��o": "Proteção",
		"Tr�nsito": "Trânsito",
		"Cibern�ticos": "Cibernéticos",
		"Corrup��o": "Corrupção",
		"Lavagem de Dinheiro": "Lavagem de Dinheiro",
		"Institui��es": "Instituições",
		"�": "é",
	}
	for incorreto, correto in reparos.items():
		texto = texto.replace(incorreto, correto)
	return texto


# Normalizar a promotoria para garantir consistência
def normalizar_promotoria(texto):
	return re.sub(r"(?<=\d)[ª°]", "º", texto)

# Aplicando as funções de tratamento e normalização nos dados
dados = dados.map(lambda valor: corrigir_texto(valor) if isinstance(valor, str) else valor)
dados = dados.rename(columns={dados.columns[-1]: "RESOLUCAO"})
dados["PROMOTORIA"] = dados["PROMOTORIA"].map(normalizar_promotoria)

# Identificar a resolução com base em palavras-chave
def identidade_resolucao(resolucao):
	identidades = [
		("POLICIAL", "Policial", "#1769aa", "#e5f3ff"),
		("MILITAR", "Militar", "#b42318", "#fff0ee"),
		("PRISIONAIS", "Estabelecimentos prisionais", "#6b46c1", "#f2edff"),
		("IDOSOS", "Pessoas idosas", "#19724a", "#e9f8f0"),
		("ACOLHIMENTO INSTITUCIONAL", "Acolhimento institucional", "#b45309", "#fff6e5"),
		("FAMÍLIA ACOLHEDORA", "Família acolhedora", "#c24178", "#fff0f6"),
		("LIBERDADE ASSISTIDA", "Liberdade assistida e PSC", "#087f8c", "#e7f8fa"),
		("INTERNAÇÃO", "Internação", "#334e68", "#edf3f8"),
		("SEMILIBERDADE", "Semiliberdade", "#8a5a00", "#fff8df"),
	]
	for termo, nome, cor, fundo in identidades:
		if termo in resolucao.upper():
			return nome, cor, fundo
	return "Todas as resoluções", "#123b5d", "#eef7fc"


# Importando o CSS e aplicando no Streamlit
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

#Sidebar com logo e filtros
if imagemLogoSidebar.exists():
	st.sidebar.image(str(imagemLogoSidebar), width=200)
st.sidebar.title("Econtre sua resolução")

opcaoResolucao = st.sidebar.selectbox(
    "Escolha uma resolução:",
    ["Todas"] + sorted(dados["RESOLUCAO"].unique()),
)
opcaoPromotoria = st.sidebar.selectbox(
	"Escolha uma promotoria:",
	["Todas"] + sorted(dados["PROMOTORIA"].unique())
)

# Filtro dos dados com base nas seleções do usuário
dados_filtrados = dados.copy()
if opcaoResolucao != "Todas":
	dados_filtrados = dados_filtrados[dados_filtrados["RESOLUCAO"] == opcaoResolucao]
if opcaoPromotoria != "Todas":
	dados_filtrados = dados_filtrados[dados_filtrados["PROMOTORIA"] == opcaoPromotoria]

nome_identidade, cor, fundo_identidade = identidade_resolucao(opcaoResolucao)
filtro_ativo = opcaoResolucao != "Todas" or opcaoPromotoria != "Todas"

# Exibição dos dados filtrados ou mensagem de boas-vindas
if not filtro_ativo:
	st.markdown(
		"""
		<div class="welcome">
		    <h1>Encontre sua resolução</h1>
		    <p>Selecione uma resolução ou promotoria no menu ao lado para visualizar os registros.</p>
		</div>
		<div class="mpal-signature">
		    <strong>MPAL</strong>
		    <span>Ministério Público do Estado de Alagoas</span>
		</div>
		""",
		unsafe_allow_html=True,
	)
elif dados_filtrados.empty:
	st.warning("Nenhum registro encontrado para os filtros escolhidos.")
else:
	st.markdown(
		f'<div class="resolution-banner" style="--identity-color: {cor}; --identity-background: {fundo_identidade};">'
		f'<span>Resolução selecionada</span><strong>{nome_identidade}</strong></div>',
		unsafe_allow_html=True,
	)
	st.markdown(f'<h3 style="color: {cor};">Dados filtrados</h3>', unsafe_allow_html=True)
	st.caption(f"{len(dados_filtrados)} registro(s) encontrado(s)")

	def alternar_linhas(linha):
		cor_linha = "#f1f7fb" if linha.name % 2 == 0 else "#ffffff"
		return [
			f"background-color: {cor_linha}; color: #172b3a"
			for _ in linha
		]

	dados_estilizados = dados_filtrados.style.apply(alternar_linhas, axis=1)
	st.dataframe(dados_estilizados, width="stretch", hide_index=True, use_container_width=True)

