import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import (
    dark_layout,
    insight_card,
    render_nav_buttons,
    section_title,
    subtitle,
    kpi_html,
)

_TARGET_CAT = "Electronics"


def render(df: pd.DataFrame, sel_cat: list[str], acts: list[str]):
    st.markdown("# Акт 6 — Рекомендации")
    subtitle("Финальные выводы и предлагаемые действия")

    elec = df[df["category"] == _TARGET_CAT]

    _kpi_row(elec)

    section_title("1. Ключевые выводы")

    insight_card([
        (
            "Основная проблема",
            "Категория Electronics показывает самую низкую удавлетворенность клиентов "
            "при высокой выручке и остаётся главным источником бизнес-риска."
        ),

        (
            "Потеря Premium-клиентов",
            "Снижение удовлетворённости сильнее всего влияет на Premium-сегмент — "
            "именно он формирует основную часть прибыли категории."
        ),

        (
            "Финансовый потенциал",
            "What-if анализ показал, что рост customer satisfaction на 10% "
            "может дать более $2M дополнительной прибыли."
        ),
    ])

    section_title("2. Рекомендуемые действия")

    st.plotly_chart(
        _priority_chart(),
        use_container_width=True,
    )

    section_title("4. Ожидаемый эффект")

    st.markdown("""
    <div class="insight-card">
        <h4>Что делать в первую очередь</h4>

- Улучшить качество поддержки Premium-клиентов  
- Сократить время доставки и возвратов  
- Пересмотреть гарантийный сервис Electronics  
- Запустить мониторинг удовлетворенности клиентов  
- Ввести SLA для клиентской поддержки  

<br>

<h4>KPI для контроля</h4>

- CSAT Electronics > 3.9  
- Retention Premium ↑  
- Return rate ↓  
- Delivery complaints ↓  
- Profit uplift +8–10%  
    """, unsafe_allow_html=True)

    render_nav_buttons(acts)

def _kpi_row(elec: pd.DataFrame):

    csat = elec["customer_satisfaction"].mean()

    revenue = elec["revenue"].sum()

    profit = elec["profit"].sum()

    what_if_profit = profit * 1.098

    uplift = what_if_profit - profit

    st.markdown(f"""
    <div class="kpi-grid">
      {kpi_html("Проблемная категория", "Electronics", -12.0, "#EF4444")}
      {kpi_html("Текущий CSAT", f"{csat:.2f} / 5", -8.0, "#F59E0B")}
      {kpi_html("Текущая прибыль", f"${profit / 1e6:.1f}M", 0.0, "#3B82F6")}
      {kpi_html("Potential uplift", f"+${uplift / 1e6:.1f}M", 9.8, "#22C55E")}
    </div>
    """, unsafe_allow_html=True)


def _priority_chart():

    actions = [
        "Support quality",
        "Delivery speed",
        "Returns process",
        "Premium service",
        "Customer feedback",
    ]

    impact = [9.5, 8.4, 7.8, 9.8, 6.8]
    effort = [6.0, 7.5, 5.5, 7.0, 3.0]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=effort,
        y=impact,
        mode="markers+text",
        text=actions,
        textposition="top center",
        marker=dict(
            size=[36, 30, 28, 42, 22],
            color=impact,
            colorscale="Blues",
            line=dict(color="#0F172A", width=2),
            opacity=0.9,
        ),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Effort: %{x}<br>"
            "Impact: %{y}<extra></extra>"
        ),
    ))

    fig.add_hline(
        y=8,
        line_dash="dot",
        line_color="#334155",
    )

    fig.add_vline(
        x=5,
        line_dash="dot",
        line_color="#334155",
    )

    fig.add_annotation(
        x=7,
        y=9.8,
        text="High impact priority",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#22C55E",
        font=dict(color="#22C55E"),
        bgcolor="rgba(15,23,42,0.9)",
        ax=90,
        ay=0
    )

    dark_layout(fig)

    fig.update_layout(
        title=dict(
            text="Impact vs effort matrix",
            font=dict(size=14, color="#94A3B8"),
            x=0,
        ),
        xaxis=dict(
            title="Implementation effort",
            range=[0, 10],
            gridcolor="#1E293B",
        ),
        yaxis=dict(
            title="Business impact",
            range=[0, 12],
            gridcolor="#1E293B",
        ),
        height=520,
        showlegend=False,
    )

    return fig

