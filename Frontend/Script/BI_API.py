import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


st.set_page_config(page_title="Dados Controle Externo", layout="wide")


API_URL = os.getenv("BI_API_URL", "http://127.0.0.1:8000/api/").rstrip("/")
PASTA_STYLE = Path(__file__).resolve().parents[1] / "Style"
IMAGEM_LOGO = PASTA_STYLE / "logo_mpal_22.png"
ARQUIVO_CSS = PASTA_STYLE / "Style.css"


def buscar_endpoint(endpoint):
	resposta = requests.get(f"{API_URL}/{endpoint}", timeout=10)
	resposta.raise_for_status()
	return resposta.json()


@st.cache_data(ttl=300)
def carregar_dados_api():
	promotorias = pd.DataFrame(buscar_endpoint("promotorias/")["promotorias"])
	resolucoes = pd.DataFrame(buscar_endpoint("resolucoes/")["resolucoes"])
	relacoes = pd.DataFrame(buscar_endpoint("relacoes/")["relacoes"])

	dados = relacoes.merge(
		promotorias[["id", "nome_promotoria", "entrancia"]],
		left_on="promotoria_id",
		right_on="id",
		how="left",
		suffixes=("", "_promotoria"),
	).merge(
		resolucoes[
			[
				"id",
				"nome_resolucao",
				"descricao_resolucao",
				"prazo_resolucao",
				"numero_resolucao",
				"ano_resolucao",
			]
		],
		left_on="resolucao_id",
		right_on="id",
		how="left",
		suffixes=("", "_resolucao"),
	)

	return dados.rename(
		columns={
			"nome_promotoria": "PROMOTORIA",
			"entrancia": "ENTRANCIA",
			"Unidade": "UNIDADE",
			"nome_resolucao": "RESOLUCAO",
		}
	)


def identidade_resolucao(resolucao):
	identidades = [
		("POLICIAL", "Policial", "#1769aa", "#e5f3ff"),
		("MILITAR", "Militar", "#b42318", "#fff0ee"),
		("PRISIONAIS", "Estabelecimentos prisionais", "#6b46c1", "#f2edff"),
		("IDOSOS", "Pessoas idosas", "#19724a", "#e9f8f0"),
		("ACOLHIMENTO", "Acolhimento institucional", "#b45309", "#fff6e5"),
		("FAMÍLIA ACOLHEDORA", "Família acolhedora", "#c24178", "#fff0f6"),
		("LIBERDADE ASSISTIDA", "Liberdade assistida e PSC", "#087f8c", "#e7f8fa"),
		("INTERNAÇÃO", "Internação", "#334e68", "#edf3f8"),
		("SEMILIBERDADE", "Semiliberdade", "#8a5a00", "#fff8df"),
		("INTERCEPTAÇÃO", "Interceptação telefônica", "#b45309", "#fff6e5"),
	]
	texto = str(resolucao).upper()
	for termo, nome, cor, fundo in identidades:
		if termo in texto:
			return nome, cor, fundo
	return "Todas as resoluções", "#123b5d", "#eef7fc"


try:
	dados = carregar_dados_api()
except requests.RequestException as erro:
	st.error(
		"Não foi possível acessar a API Django. "
		f"Verifique se o backend está rodando em {API_URL}."
	)
	st.caption(f"Detalhe técnico: {erro}")
	st.stop()
except (KeyError, ValueError) as erro:
	st.error("A API respondeu em um formato diferente do esperado.")
	st.caption(f"Detalhe técnico: {erro}")
	st.stop()


if ARQUIVO_CSS.exists():
	st.markdown(
		f"<style>{ARQUIVO_CSS.read_text(encoding='utf-8')}</style>",
		unsafe_allow_html=True,
	)

if IMAGEM_LOGO.exists():
	st.sidebar.image(str(IMAGEM_LOGO), width=200)
st.sidebar.title("Encontre sua resolução")

resolucoes_disponiveis = sorted(dados["RESOLUCAO"].dropna().unique())
promotorias_disponiveis = sorted(dados["PROMOTORIA"].dropna().unique())

opcao_resolucao = st.sidebar.selectbox(
	"Escolha uma resolução:",
	["Todas"] + resolucoes_disponiveis,
)
opcao_promotoria = st.sidebar.selectbox(
	"Escolha uma promotoria:",
	["Todas"] + promotorias_disponiveis,
)

dados_filtrados = dados.copy()
if opcao_resolucao != "Todas":
	dados_filtrados = dados_filtrados[dados_filtrados["RESOLUCAO"] == opcao_resolucao]
if opcao_promotoria != "Todas":
	dados_filtrados = dados_filtrados[
		dados_filtrados["PROMOTORIA"] == opcao_promotoria
	]

dados_filtrados = dados_filtrados.sort_values(
	by="ENTRANCIA",
	key=lambda coluna: pd.to_numeric(
		coluna.astype("string").str.extract(r"(\d+)", expand=False),
		errors="coerce",
	),
	ascending=False,
	na_position="last",
	kind="mergesort",
)

nome_identidade, cor, fundo_identidade = identidade_resolucao(opcao_resolucao)
filtro_ativo = opcao_resolucao != "Todas" or opcao_promotoria != "Todas"

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
	resolucao_selecionada = dados_filtrados.iloc[0]
	st.markdown(
		f'<div class="resolution-banner" style="--identity-color: {cor}; --identity-background: {fundo_identidade};">'
		f'<span>Resolução selecionada</span><strong>{nome_identidade}</strong></div>'
		f'<p><strong>Prazo:</strong> {resolucao_selecionada["prazo_resolucao"]}</p>'
		f'<p><strong>Membros:</strong> {resolucao_selecionada["descricao_resolucao"]}</p>',
		unsafe_allow_html=True,
	)

	st.markdown(f'<h3 style="color: {cor};">Dados filtrados</h3>', unsafe_allow_html=True)
	st.caption(f"{len(dados_filtrados)} registro(s) encontrado(s)")

	def alternar_linhas(linha):
		cor_linha = "#f1f7fb" if linha.name % 2 == 0 else "#ffffff"
		return [f"background-color: {cor_linha}; color: #172b3a" for _ in linha]

	if dados_filtrados["UNIDADE"].isna().all():
		colunas_exibicao = ["PROMOTORIA", "ENTRANCIA", "RESOLUCAO"]
		dados_para_exibir = dados_filtrados[colunas_exibicao]
	else:
		dados_para_exibir = dados_filtrados[
			["PROMOTORIA", "ENTRANCIA", "RESOLUCAO", "UNIDADE"]
		]

	dados_estilizados = dados_para_exibir.style.apply(alternar_linhas, axis=1)
	st.dataframe(
		dados_estilizados,
		width="stretch",
		hide_index=True,
		use_container_width=True,
	)