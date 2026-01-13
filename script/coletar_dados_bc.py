import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ==========================
# CONFIGURAÇÕES INICIAIS
# ==========================
st.set_page_config(page_title="Painel Financeiro Dinâmico", layout="wide")
st.title("📊 Painel Financeiro - BC/SGS")
st.markdown("Dados atualizados automaticamente via API do Banco Central")

# ==========================
# FUNÇÃO PARA BUSCAR DADOS
# ==========================
@st.cache_data
def get_bcb_series(code, start_date, end_date):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json&dataInicial={start_date}&dataFinal={end_date}"
    data = requests.get(url).json()
    df = pd.DataFrame(data)
    df["data"] = pd.to_datetime(df["data"], dayfirst=True)
    df["valor"] = pd.to_numeric(df["valor"])
    df = df.sort_values("data")
    return df

# ==========================
# FILTRO DE PERÍODO
# ==========================
periodos = {
    "12 meses": 12,
    "24 meses": 24,
    "36 meses": 36
}

periodo_selecionado = st.selectbox("Selecione o período de análise:", list(periodos.keys()))
meses = periodos[periodo_selecionado]

# Datas para consulta (sempre pega histórico maior para cálculos)
hoje = datetime.today()
data_inicio = (hoje - pd.DateOffset(months=36)).strftime("%d/%m/%Y")  # pega 36 meses no total
data_fim = hoje.strftime("%d/%m/%Y")

# ==========================
# COLETA DE DADOS
# ==========================
selic = get_bcb_series(11, data_inicio, data_fim)
usd   = get_bcb_series(1,  data_inicio, data_fim)
ipca  = get_bcb_series(433, data_inicio, data_fim)

# ==========================
# FILTRA OS DADOS PELO PERÍODO SELECIONADO
# ==========================
selic_period = selic[selic["data"] >= (hoje - pd.DateOffset(months=meses))]
usd_period   = usd[usd["data"] >= (hoje - pd.DateOffset(months=meses))]
ipca_period  = ipca[ipca["data"] >= (hoje - pd.DateOffset(months=meses))]

# ==========================
# CÁLCULO DOS KPIs
# ==========================
# SELIC
selic_atual = selic_period["valor"].iloc[-1]
selic_30d = selic_period["valor"].iloc[-30] if len(selic_period) > 30 else selic_period["valor"].iloc[0]
selic_var = ((selic_atual / selic_30d) - 1) * 100

# USD
usd_atual = usd_period["valor"].iloc[-1]
usd_7d = usd_period["valor"].iloc[-7] if len(usd_period) > 7 else usd_period["valor"].iloc[0]
usd_30d = usd_period["valor"].iloc[-30] if len(usd_period) > 30 else usd_period["valor"].iloc[0]
usd_ret_7 = ((usd_atual / usd_7d) - 1) * 100
usd_ret_30 = ((usd_atual / usd_30d) - 1) * 100
usd_period["retorno"] = usd_period["valor"].pct_change()
usd_vol = usd_period["retorno"].iloc[-30:].std() * (252 ** 0.5) * 100
usd_period["mm30"] = usd_period["valor"].rolling(30).mean()

# IPCA acumulado
ipca_acum_12m = ((1 + ipca_period["valor"].tail(12)/100).prod() - 1) * 100
ipca_meta = 3.5  # meta de inflação

# ==========================
# KPIs PRINCIPAIS
# ==========================
st.markdown("### ⚡ KPIs Principais")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("📈 SELIC Atual", f"{selic_atual:.2f}%", f"{selic_var:.2f}% vs 30 dias",
            delta_color="inverse" if selic_var > 0 else "normal")

col2.metric("💵 USD/BRL Atual", f"R$ {usd_atual:.2f}", f"{usd_ret_7:.2f}% (7 dias)",
            delta_color="inverse" if usd_ret_7 > 0 else "normal")

col3.metric("📊 Retorno USD/BRL 30d", f"{usd_ret_30:.2f}%", "Retorno 30 dias",
            delta_color="inverse" if usd_ret_30 > 0 else "normal")

col4.metric("⚡ Volatilidade USD/BRL 30d", f"{usd_vol:.2f}%", "Base diária anualizada",
            delta_color="normal")

col5.metric("📦 IPCA Acumulado 12m", f"{ipca_acum_12m:.2f}%", "Acumulado 12 meses",
            delta_color="inverse" if ipca_acum_12m > ipca_meta else "normal")

st.divider()

# ==========================
# INSIGHTS AUTOMÁTICOS
# ==========================
st.markdown("### 💡 Insights Automáticos")

# 1️⃣ SELIC tendência de alta
selic_alert = selic_var > 0.5
selic_alert_text = "Alta detectada nos últimos 30 dias" if selic_alert else "Sem alta relevante"
st.metric("📈 SELIC Tendência", selic_alert_text, delta=f"{selic_var:.2f}% (30d)",
          delta_color="inverse" if selic_alert else "normal")

# 2️⃣ USD/BRL acima da média móvel
usd_signal = usd_atual > usd_period["mm30"].iloc[-1]
usd_signal_text = "Acima da média móvel 30d" if usd_signal else "Dentro da faixa normal"
st.metric("💵 USD/BRL Força Relativa", usd_signal_text, delta=f"{usd_ret_7:.2f}% (7d)",
          delta_color="inverse" if usd_signal else "normal")

# 3️⃣ IPCA acumulado x meta
ipca_signal = ipca_acum_12m > ipca_meta
ipca_signal_text = "Acima da meta" if ipca_signal else "Dentro da meta"
st.metric("📦 IPCA x Meta", ipca_signal_text, delta=f"{ipca_acum_12m:.2f}% (12m)",
          delta_color="inverse" if ipca_signal else "normal")

st.divider()

# ==========================
# GRÁFICOS INTERATIVOS
# ==========================
st.markdown("### 📊 Evolução dos Indicadores")

tabs = st.tabs(["📈 SELIC", "💵 USD/BRL", "📦 IPCA"])

with tabs[0]:
    fig_selic = px.line(
        selic_period, x="data", y="valor",
        title=f"Evolução da Taxa SELIC - Últimos {meses} meses",
        markers=True
    )
    st.plotly_chart(fig_selic, use_container_width=True)

with tabs[1]:
    fig_usd = px.line(
        usd_period, x="data", y="valor",
        title=f"Evolução do USD/BRL - Últimos {meses} meses",
        markers=True, color_discrete_sequence=["orange"]
    )
    fig_usd.add_scatter(
        x=usd_period["data"], y=usd_period["mm30"],
        mode="lines", name="Média Móvel 30d",
        line=dict(dash='dash', color='blue')
    )
    st.plotly_chart(fig_usd, use_container_width=True)

with tabs[2]:
    fig_ipca = px.bar(
        ipca_period, x="data", y="valor",
        title=f"Variação Mensal do IPCA - Últimos {meses} meses",
        color="valor", color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_ipca, use_container_width=True)

st.divider()
st.markdown("✅ Painel automatizado e atualizado via API pública do Banco Central")
