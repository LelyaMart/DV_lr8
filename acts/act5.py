import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import CAT_COLORS, dark_layout, insight_card, render_nav_buttons, section_title, subtitle, kpi_html

_TARGET_CAT = "Electronics"
_SAT_LIFT = 0.10


def render(df: pd.DataFrame, sel_cat: list[str], acts: list[str]):
    st.markdown("# Акт 5 — Решение")
    subtitle("What-if сценарий: рост удовлетворённости в Electronics на 10%")

    if _TARGET_CAT not in df["category"].unique():
        st.warning("Electronics скрыта фильтром категорий. Включите Electronics в сайдбаре.")
        render_nav_buttons(acts)
        return

    scenario = _build_scenario(df)

    _kpi_row(scenario)

    section_title("1. Факт vs what-if по прибыли")
    st.plotly_chart(_profit_comparison_chart(scenario), use_container_width=True)

    section_title("2. Эффект по сегментам")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(_segment_impact_chart(scenario), use_container_width=True)
    with col2:
        st.plotly_chart(_monthly_uplift_chart(scenario), use_container_width=True)

    _conclusions(scenario)
    render_nav_buttons(acts)


def _build_scenario(df: pd.DataFrame) -> pd.DataFrame:
    elec = df[df["category"] == _TARGET_CAT].copy()

    elec["sat_current"] = elec["customer_satisfaction"]
    elec["sat_what_if"] = (elec["customer_satisfaction"] * (1 + _SAT_LIFT)).clip(upper=5)

    elec["sat_uplift_real"] = elec["sat_what_if"] / elec["sat_current"] - 1

    elec["revenue_what_if"] = elec["revenue"] * (1 + elec["sat_uplift_real"])
    elec["profit_what_if"] = elec["profit"] * (1 + elec["sat_uplift_real"])
    elec["profit_uplift"] = elec["profit_what_if"] - elec["profit"]
    elec["revenue_uplift"] = elec["revenue_what_if"] - elec["revenue"]

    return elec


def _delta_pct(new: float, old: float) -> float:
    return 0.0 if old == 0 else (new - old) / abs(old) * 100


def _kpi_row(scenario: pd.DataFrame):
    actual_profit = scenario["profit"].sum()
    what_if_profit = scenario["profit_what_if"].sum()
    profit_uplift = what_if_profit - actual_profit

    actual_revenue = scenario["revenue"].sum()
    what_if_revenue = scenario["revenue_what_if"].sum()
    revenue_uplift = what_if_revenue - actual_revenue

    sat_now = scenario["sat_current"].mean()
    sat_new = scenario["sat_what_if"].mean()

    margin_now = actual_profit / actual_revenue * 100 if actual_revenue else 0
    margin_new = what_if_profit / what_if_revenue * 100 if what_if_revenue else 0

    st.markdown(f"""
    <div class="kpi-grid">
      {kpi_html("CSAT Electronics", f"{sat_new:.2f} / 5", _delta_pct(sat_new, sat_now), CAT_COLORS.get(_TARGET_CAT, "#3B82F6"))}
      {kpi_html("Доп. выручка", f"${revenue_uplift / 1e6:.1f}M", _delta_pct(what_if_revenue, actual_revenue), "#10B981")}
      {kpi_html("Доп. прибыль", f"${profit_uplift / 1e6:.1f}M", _delta_pct(what_if_profit, actual_profit), "#4ADE80")}
      {kpi_html("Маржа what-if", f"{margin_new:.1f}%", margin_new - margin_now, "#F59E0B")}
    </div>
    """, unsafe_allow_html=True)


def _profit_comparison_chart(scenario: pd.DataFrame) -> go.Figure:
    yearly = (
        scenario.groupby("year")
        .agg(
            profit=("profit", "sum"),
            profit_what_if=("profit_what_if", "sum"),
        )
        .reset_index()
    )
    yearly["year"] = yearly["year"].astype(str)
    yearly["uplift_pct"] = (yearly["profit_what_if"] - yearly["profit"]) / yearly["profit"] * 100

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=yearly["year"],
        y=yearly["profit"],
        name="Факт",
        marker_color="rgba(148,163,184,0.45)",
        hovertemplate="<b>%{x}</b><br>Факт: $%{y:,.0f}<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        x=yearly["year"],
        y=yearly["profit_what_if"],
        name="What-if",
        marker_color=CAT_COLORS.get(_TARGET_CAT, "#3B82F6"),
        hovertemplate="<b>%{x}</b><br>What-if: $%{y:,.0f}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=yearly["year"],
        y=yearly["uplift_pct"],
        name="Прирост %",
        yaxis="y2",
        mode="lines+markers+text",
        line=dict(color="rgba(255,255,255,0.25)", width=1.5, dash="dot"),
        marker=dict(color="#4ADE80", size=8, line=dict(color="#0F172A", width=1)),
        text=[f"+{v:.1f}%" for v in yearly["uplift_pct"]],
        textposition="top center",
        textfont=dict(color="#4ADE80", size=11),
        hovertemplate="<b>%{x}</b><br>Прирост прибыли: %{y:+.1f}%<extra></extra>",
    ))

    dark_layout(fig)
    fig.update_layout(
        title=dict(
            text="Прибыль Electronics: фактическая и смоделированная",
            font=dict(size=14, color="#94A3B8"),
            x=0,
        ),
        barmode="group",
        bargap=0.28,
        yaxis=dict(title="Прибыль ($)", tickprefix="$", gridcolor="#1E293B"),
        yaxis2=dict(
            title=dict(
                text="Прирост, %",
                font=dict(color="#64748B"),
            ),
            overlaying="y",
            side="right",
            ticksuffix="%",
            showgrid=False,
            zeroline=True,
            zerolinecolor="#334155",
            tickfont=dict(color="#64748B", size=11),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            orientation="h",
            y=-0.18,
            x=0.5,
            xanchor="center",
            yanchor="top",
        ),
        margin=dict(l=0, r=0, t=70, b=70),
    )
    return fig


def _segment_impact_chart(scenario: pd.DataFrame) -> go.Figure:
    seg = (
        scenario.groupby("segment")
        .agg(
            profit=("profit", "sum"),
            profit_what_if=("profit_what_if", "sum"),
            profit_uplift=("profit_uplift", "sum"),
        )
        .reset_index()
    )

    order = ["Premium", "Standard", "Budget"]
    seg["segment"] = pd.Categorical(seg["segment"], categories=order, ordered=True)
    seg = seg.sort_values("segment")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=seg["segment"],
        y=seg["profit"],
        name="Факт",
        marker_color="rgba(148,163,184,0.4)",
        hovertemplate="<b>%{x}</b><br>Факт: $%{y:,.0f}<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        x=seg["segment"],
        y=seg["profit_uplift"],
        name="Доп. прибыль",
        marker_color="#4ADE80",
        hovertemplate="<b>%{x}</b><br>Доп. прибыль: $%{y:,.0f}<extra></extra>",
    ))

    for _, row in seg.iterrows():
        fig.add_annotation(
            x=row["segment"],
            y=row["profit"] + row["profit_uplift"],
            text=f"+${row['profit_uplift'] / 1e6:.1f}M",
            showarrow=False,
            yshift=10,
            font=dict(color="#4ADE80", size=11),
        )

    dark_layout(fig)
    fig.update_layout(
        title=dict(
            text="Где появляется дополнительная прибыль",
            font=dict(size=14, color="#94A3B8"),
            x=0,
        ),
        barmode="stack",
        yaxis=dict(title="Прибыль ($)", tickprefix="$", gridcolor="#1E293B"),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            orientation="h",
            y=-0.22,
            x=0.5,
            xanchor="center",
            yanchor="top",
        ),
        margin=dict(l=0, r=0, t=70, b=80),
    )
    return fig


def _monthly_uplift_chart(scenario: pd.DataFrame) -> go.Figure:
    monthly = (
        scenario.groupby(pd.Grouper(key="date", freq="ME"))
        .agg(
            profit=("profit", "sum"),
            profit_what_if=("profit_what_if", "sum"),
            profit_uplift=("profit_uplift", "sum"),
        )
        .reset_index()
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=monthly["date"],
        y=monthly["profit"],
        name="Факт",
        mode="lines",
        line=dict(color="rgba(148,163,184,0.65)", width=2),
        hovertemplate="<b>%{x|%b %Y}</b><br>Факт: $%{y:,.0f}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=monthly["date"],
        y=monthly["profit_what_if"],
        name="What-if",
        mode="lines",
        line=dict(color=CAT_COLORS.get(_TARGET_CAT, "#3B82F6"), width=2.5),
        fill="tonexty",
        fillcolor="rgba(59,130,246,0.10)",
        hovertemplate="<b>%{x|%b %Y}</b><br>What-if: $%{y:,.0f}<extra></extra>",
    ))

    max_row = monthly.loc[monthly["profit_uplift"].idxmax()]
    fig.add_annotation(
        x=max_row["date"],
        y=max_row["profit_what_if"],
        text=f"Макс. эффект<br>+${max_row['profit_uplift']:,.0f}",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#4ADE80",
        arrowwidth=1.5,
        ax=65,
        ay=-45,
        font=dict(color="#4ADE80", size=11),
        bgcolor="rgba(15,23,42,0.85)",
        bordercolor="#4ADE80",
        borderwidth=1,
        borderpad=6,
    )

    dark_layout(fig)
    fig.update_layout(
        title=dict(
            text="Месячная динамика эффекта",
            font=dict(size=14, color="#94A3B8"),
            x=0,
        ),
        hovermode="x unified",
        yaxis=dict(title="Прибыль ($)", tickprefix="$", gridcolor="#1E293B"),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            orientation="h",
            y=-0.22,
            x=0.5,
            xanchor="center",
            yanchor="top",
        ),
        margin=dict(l=0, r=0, t=70, b=80),
    )
    return fig


def _conclusions(scenario: pd.DataFrame):
    section_title("Выводы по акту 5")

    actual_profit = scenario["profit"].sum()
    what_if_profit = scenario["profit_what_if"].sum()
    uplift = what_if_profit - actual_profit
    uplift_pct = _delta_pct(what_if_profit, actual_profit)

    seg = (
        scenario.groupby("segment")
        .agg(profit_uplift=("profit_uplift", "sum"))
        .sort_values("profit_uplift", ascending=False)
    )
    top_seg = seg.index[0]
    top_seg_value = seg.iloc[0]["profit_uplift"]

    avg_sat_now = scenario["sat_current"].mean()
    avg_sat_new = scenario["sat_what_if"].mean()

    insight_card([
        ("1. Решение имеет финансовый эффект",
         f"Рост CSAT Electronics с {avg_sat_now:.2f} до {avg_sat_new:.2f} даёт "
         f"+${uplift / 1e6:.1f}M к прибыли, или {uplift_pct:+.1f}% к факту."),

        (f"2. Главный рычаг — {top_seg}",
         f"Наибольший вклад в дополнительную прибыль даёт сегмент {top_seg}: "
         f"+${top_seg_value / 1e6:.1f}M. Поэтому улучшение сервиса нужно начинать с Premium-клиентов."),

        ("3. Рекомендация",
         "Сфокусироваться на Electronics: качество поддержки, скорость доставки, возвраты и гарантийный сервис. "
         "Цель — вернуть удовлетворённость и остановить отток самого прибыльного сегмента."),
    ])