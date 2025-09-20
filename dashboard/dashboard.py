import os
import requests
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="PlanoPy", page_icon="📊", layout="wide")

# URL interna (rede do Docker) — NÃO é localhost
API = os.getenv("PLANOPY_API", "http://planopy_api:8000")

# Apenas para mostrar o link público do Swagger na UI
PUBLIC_HOST = os.getenv("PUBLIC_HOST", "srv1009379.hstgr.cloud")
PUBLIC_API_DOCS = f"https://{PUBLIC_HOST}/api/docs"

st.title("📊 PlanoPy Dashboard")
st.caption(f"API interna alvo: {API}")
st.markdown(f"🔗 **Swagger da API:** https://{PUBLIC_HOST}/api/docs")

with st.sidebar:
    st.subheader("Filtros")
    scenarios = st.multiselect(
        "Cenários", ["base", "otimista", "pessimista"], default=["base"]
    )
    days = st.slider("Dias (histórico)", min_value=7, max_value=180, value=30)
    variation = st.slider("Variação (multiplicador)", 0.1, 3.0, 1.0, 0.1)
    st.caption("Dica: selecione 2–3 cenários para comparar.")

# Checagem rápida de saúde
ok = False
try:
    r = requests.get(f"{API}/", timeout=5)
    r.raise_for_status()
    st.success(f"API OK • {r.json()}")

except Exception as e:
    st.error(f"Falha ao conectar na API em {API}: {e}")

st.divider()
st.write("Painéis e gráficos entram aqui…")

def fetch_metrics(scn: str):
    resp = requests.get(
        f"{API}/metrics",
        params={"days": days, "scenario": scn, "variation": variation},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    xs = [item["date"] for item in data]
    ys = [item["value"] for item in data]
    return xs, ys

if ok:
    if not scenarios:
        st.info("Selecione ao menos um cenário na barra lateral.")
    else:
        fig = go.Figure()

        # paleta em tons de azul
        palette = {
            "base": "#2563eb",       # azul principal
            "otimista": "#3b82f6",   # azul claro
            "pessimista": "#1d4ed8", # azul escuro
        }

        for scn in scenarios:
            try:
                xs, ys = fetch_metrics(scn)
                fig.add_trace(go.Scatter(
                    x=xs, y=ys, mode="lines+markers", name=scn.capitalize(),
                    line=dict(width=3, color=palette.get(scn, "#2563eb")),
                    marker=dict(size=5)
                ))
            except Exception as e:
                st.error(f"Erro ao obter dados do cenário '{scn}': {e}")

        fig.update_layout(
            title=f"Série temporal ({days} dias) • variação x{variation}",
            xaxis_title="Data",
            yaxis_title="Valor",
            legend_title="Cenários",
            margin=dict(l=40, r=20, t=50, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

        # KPIs simples do último cenário da lista (se houver dados)
        if scenarios:
            try:
                xs, ys = fetch_metrics(scenarios[-1])
                st.subheader("Indicadores")
                c1, c2, c3 = st.columns(3)
                c1.metric("Valor atual", f"{ys[-1]:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                c2.metric("Média", f"{(sum(ys)/len(ys)):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                c3.metric("Dias", len(ys))
            except Exception:
                pass

        st.divider()
        st.caption("Trilha de aprovação (exemplo): Proposta → Revisão → Aprovado ✅")
else:
    st.warning("Conecte a API para carregar os dados.")

