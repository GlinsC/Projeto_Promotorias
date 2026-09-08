import streamlit as st
import pandas as pd
import re
from pathlib import Path


st.set_page_config(page_title="Dados Controle Externo", layout="wide")

arquivo_csv = Path(__file__).resolve().parents[1] / "Documento" / "Dados279Policial.csv"
dados = pd.read_csv(arquivo_csv, sep=",", encoding="utf-8")

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


def normalizar_promotoria(texto):
	return re.sub(r"(?<=\d)[ª°]", "º", texto)


dados = dados.map(lambda valor: corrigir_texto(valor) if isinstance(valor, str) else valor)
dados = dados.rename(columns={dados.columns[-1]: "RESOLUCAO"})
dados["PROMOTORIA"] = dados["PROMOTORIA"].map(normalizar_promotoria)
dados = dados.rename(columns={dados.columns[-1]: "RESOLUCAO"})

imagem = Path(__file__).resolve().parent / "GED.webp"

st.markdown(
	"""
	<style>
	[data-testid="stSidebar"] {
	    background: linear-gradient(180deg, #123b5d 0%, #0b263d 100%);
	}
	[data-testid="stSidebar"] h1,
	[data-testid="stSidebar"] h2,
	[data-testid="stSidebar"] h3,
	[data-testid="stSidebar"] label {
	    color: #f5f8fb;
	}
	[data-testid="stSidebar"] .stSelectbox label {
	    color: #b9d7ec;
	    font-weight: 600;
	}
	[data-testid="stSidebar"] [data-baseweb="select"] > div,
	[data-testid="stSidebar"] [data-baseweb="select"] [role="button"] {
	    background-color: #f7fbff;
	    border: 1px solid #70a9cf;
	    color: #000000 !important;
	    -webkit-text-fill-color: #000000 !important;
	}
	[data-testid="stSidebar"] [data-baseweb="select"] [role="button"] * {
	    color: #000000 !important;
	    -webkit-text-fill-color: #000000 !important;
	    opacity: 1 !important;
	}
	[data-baseweb="popover"] [role="option"] {
	    color: #000000 !important;
	    background-color: #ffffff;
	}
	[data-baseweb="popover"] [role="option"]:hover {
	    background-color: #e7f2f9;
	}
	.welcome {
	    padding: 3rem 2rem;
	    text-align: center;
	    background: linear-gradient(135deg, #eef7fc 0%, #ffffff 100%);
	    border: 1px solid #d5e6f0;
	    border-radius: 12px;
	}
	.welcome h1 {
	    color: #123b5d;
	    margin-bottom: 0.5rem;
	}
	.welcome p {
	    color: #557080;
	    font-size: 1.05rem;
	}
	</style>
	""",
	unsafe_allow_html=True,
)

if imagem.exists():
	st.sidebar.image(str(imagem), width=200)
st.sidebar.title("Dados Controle Externo")

opcaoResolucao = st.sidebar.selectbox(
    "Escolha uma resolução:",
    ["Todas"] + sorted(dados["RESOLUCAO"].unique()),
)
opcaoPromotoria = st.sidebar.selectbox(
	"Escolha uma promotoria:",
	["Todas"] + sorted(dados["PROMOTORIA"].unique())
)

dados_filtrados = dados.copy()
if opcaoResolucao != "Todas":
	dados_filtrados = dados_filtrados[dados_filtrados["RESOLUCAO"] == opcaoResolucao]
if opcaoPromotoria != "Todas":
	dados_filtrados = dados_filtrados[dados_filtrados["PROMOTORIA"] == opcaoPromotoria]

cor = "#d62728" if "MILITAR" in opcaoResolucao else "#1f77b4"
filtro_ativo = opcaoResolucao != "Todas" or opcaoPromotoria != "Todas"

if not filtro_ativo:
	st.markdown(
		"""
		<div class="welcome">
		    <h1>Dados Controle Externo</h1>
		    <p>Selecione uma resolução ou promotoria no menu ao lado para visualizar os registros.</p>
		</div>
		""",
		unsafe_allow_html=True,
	)
	if imagem.exists():
		st.image(str(imagem), use_container_width=True)
elif dados_filtrados.empty:
	st.warning("Nenhum registro encontrado para os filtros escolhidos.")
else:
	st.markdown(f'<h3 style="color: {cor};">Dados filtrados</h3>', unsafe_allow_html=True)
	st.caption(f"{len(dados_filtrados)} registro(s) encontrado(s)")

	def alternar_linhas(linha):
		cor_linha = "#f1f7fb" if linha.name % 2 == 0 else "#ffffff"
		return [f"background-color: {cor_linha}" for _ in linha]

	dados_estilizados = dados_filtrados.style.apply(alternar_linhas, axis=1)
	st.dataframe(dados_estilizados, width="stretch", hide_index=True)

