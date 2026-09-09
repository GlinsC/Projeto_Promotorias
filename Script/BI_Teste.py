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

# Normalizar a promotoria para garantir consistência
def normalizar_promotoria(texto):
	return re.sub(r"(?<=\d)[ª°]", "º", texto)

# Aplicar somente a normalização dos símbolos ordinais na promotoria
dados = dados.rename(columns={dados.columns[-1]: "RESOLUCAO"})
dados["PROMOTORIA"] = dados["PROMOTORIA"].map(normalizar_promotoria)

# Identificar a resolução com base em palavras-chave
def identidade_resolucao(resolucao):
	identidades = [
		("POLICIAL", "Policial", "#1769aa", "#e5f3ff", "Quinto dia util do mês subsequente à visita."),
		("MILITAR", "Militar", "#b42318", "#fff0ee", "Quinto dia util do mês subsequente à visita."),
		("PRISIONAIS", "Estabelecimentos prisionais", "#6b46c1", "#f2edff", "Quinto dia util do mês subsequente à visita."),
		("IDOSOS", "Pessoas idosas", "#19724a", "#e9f8f0", "Até o dia 15 do mês subsequente à inspeção."),
		("ACOLHIMENTO INSTITUCIONAL", "Acolhimento institucional", "#b45309", "#fff6e5", "1º Semestre: até 15/05; 2º Semestre: até 01/12."),
		("FAMÍLIA ACOLHEDORA", "Família acolhedora", "#c24178", "#fff0f6" , "1º Semestre: até 15/05; 2º Semestre: até 01/12."),
		("LIBERDADE ASSISTIDA", "Liberdade assistida e PSC", "#087f8c", "#e7f8fa", "Até o dia 15/7"),
		("INTERNAÇÃO", "Internação", "#334e68", "#edf3f8", "Bimistre, 1º 15/03; 2º 15/05; 3º 15/07; 4º 15/09; 5º 15/11; 6º 15/01."),
		("SEMILIBERDADE", "Semiliberdade", "#8a5a00", "#fff8df", "Bimistre, 1º 15/03; 2º 15/05; 3º 15/07; 4º 15/09; 5º 15/11; 6º 15/01.")
	]
	for termo, nome, cor, fundo, prazo in identidades:
		if termo in resolucao.upper():
			return nome, cor, fundo, prazo
	return "Todas as resoluções", "#123b5d", "#eef7fc", ""


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

nome_identidade, cor, fundo_identidade, prazo = identidade_resolucao(opcaoResolucao)
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
		f'<span>Resolução selecionada</span><strong>{nome_identidade}</strong></div>'
		f'<p><strong>Prazo:</strong> {prazo}</p>',
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

