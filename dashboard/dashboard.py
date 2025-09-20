import os
import requests
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="PlanoPy", page_icon="📊", layout="wide")

# API interna (rede do Docker)
API = os.getenv("PLANOPY_API", "http://planopy_api:8000")
PUBLIC_HOST = os.getenv("PUBLIC_HOST", "srv1009379.hstgr.cloud")
PUBLIC_API_DOCS = f"https://{PUBLIC_HOST}/api/docs"

st.title("📊 PlanoPy Dashboard")
st.caption(f"API interna alvo: {API}")
st.markdown(f"🔗 **Swagger da API:** [{PUBLIC_API_DOCS}]({PUBLIC_API_DOCS})")

with st.sidebar:
    st.subheader("Filtros")
    scenario = st.selectbox("Cenário", ["base", "otimista", "pessimista"], index=0)
    days = st.slider("Dias (histórico)", 7, 180, 30, step=1)
    variation = st.slider("Variação (multiplicador)", 0.1, 3.0, 1.0, step=0.1)

# Saúde da API
ok = False
try:
    resp = requests.get(f"{API}/", timeout=5)
    resp.raise_for_status()
    st.success(f"API OK • {resp.json()}")
    ok = True
except Exception as e:
    st.error(f"Falha ao conectar na API em {API}: {e}")

st.divider()

# Buscar métricas
if ok:
    try:
        r = requests.get(
            f"{API}/metrics",
            params={"days": days, "scenario": scenario, "variation": variation},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        st.error(f"Erro ao obter /metrics: {e}")
        data = []

    if data:
        dates = [d["date"] for d in data]
        vals = [d["value"] for d in data]

        # Gráfico (tema azul)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=vals, mode="lines+markers", name=scenario))
        fig.update_layout(
            title=f"Série temporal — cenário: {scenario}",
            xaxis_title="Data",
            yaxis_title="Valor",
            legend_title="Cenário",
            margin=dict(l=40, r=20, t=50, b=40),
        )
        # deixa a linha azul
        fig.update_traces(line=dict(width=3, color="#2563eb"), marker=dict(size=5))

        st.plotly_chart(fig, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("Valor atual", f"{vals[-1]:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        col2.metric("Média", f"{(sum(vals)/len(vals)):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        col3.metric("Dias", len(vals))
    else:
        st.info("Sem dados retornados. Ajuste os filtros e tente novamente.")
else:
    st.warning("Conecte a API para carregar os dados.")

