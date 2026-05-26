import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import dark_layout, kpi_html, section_title, subtitle, insight_card, render_nav_buttons
from data import agg_monthly, agg_by_category_year, agg_by_segment_year


def render(df: pd.DataFrame, sel_cat: list[str], acts: list[str]):
    st.markdown("# Акт 1 — Общий обзор бизнеса")
    subtitle("Динамика ключевых показателей за 2023–2024 год")

    _kpi_row(df)
    _line_chart(df)
    _bar_charts(df, sel_cat)
    _conclusions(df)
    render_nav_buttons(acts)


def _delta_pct(new: float, old: float) -> float:
    return 0.0 if old == 0 else (new - old) / abs(old) * 100


def _kpi_row(df: pd.DataFrame):
    y23 = df[df["year"] == 2023]
    y24 = df[df["year"] == 2024]

    rev_23, rev_24   = y23["revenue"].sum(), y24["revenue"].sum()
    prof_23, prof_24 = y23["profit"].sum(),  y24["profit"].sum()
    margin           = prof_24 / rev_24 * 100 if rev_24 else 0
    sat_all          = df["customer_satisfaction"].mean()
    sat_23           = y23["customer_satisfaction"].mean()
    sat_24           = y24["customer_satisfaction"].mean()

    st.markdown(f"""
    <div class="kpi-grid">
      {kpi_html("Общая выручка",          f"${(rev_23 + rev_24) / 1e6:.1f}M", _delta_pct(rev_24, rev_23),  "#3B82F6")}
      {kpi_html("Общая прибыль",          f"${(prof_23 + prof_24) / 1e6:.1f}M", _delta_pct(prof_24, prof_23), "#10B981")}
      {kpi_html("Маржа (2024)",           f"{margin:.1f}%",                    accent="#F59E0B")}
      {kpi_html("Ср. удовлетворённость",  f"{sat_all:.2f} / 5",               _delta_pct(sat_24, sat_23),   "#8B5CF6")}
    </div>
    """, unsafe_allow_html=True)


def _line_chart(df: pd.DataFrame):
    section_title("Динамика выручки и прибыли")

    monthly = agg_monthly(df)
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=monthly["date"], y=monthly["revenue"],
        name="Выручка", mode="lines",
        line=dict(color="#3B82F6", width=2.5),
        fill="tozeroy", fillcolor="rgba(59,130,246,0.08)",
        hovertemplate="<b>%{x|%b %Y}</b><br>Выручка: $%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=monthly["date"], y=monthly["profit"],
        name="Прибыль", mode="lines",
        line=dict(color="#4ADE80", width=2.5),
        fill="tozeroy", fillcolor="rgba(74,222,128,0.06)",
        hovertemplate="<b>%{x|%b %Y}</b><br>Прибыль: $%{y:,.0f}<extra></extra>",
    ))

    boundary_ts = int(pd.Timestamp("2024-01-01").timestamp() * 1000)
    fig.add_vline(x=boundary_ts, line_dash="dot", line_color="#334155")
    fig.add_annotation(
        x="2024-01-01", y=1, yref="paper",
        text="2024", showarrow=False,
        font=dict(color="#64748B", size=11),
        xanchor="left", yanchor="top",
    )

    dark_layout(fig)
    fig.update_layout(hovermode="x unified", yaxis_tickprefix="$")
    st.plotly_chart(fig, use_container_width=True)


_CAT_BRIGHT = {
    "Electronics": "#3B82F6",
    "Clothing":    "#10B981",
    "Home":        "#F59E0B",
    "Books":       "#8B5CF6",
    "Sports":      "#EF4444",
}
_CAT_DIM = {k: v.replace("#", "rgba(") + ",0.4)".replace("rgba(", "rgba(")
            for k, v in _CAT_BRIGHT.items()}

_CAT_DIM = {
    "Electronics": "rgba(59,130,246,0.35)",
    "Clothing":    "rgba(16,185,129,0.35)",
    "Home":        "rgba(245,158,11,0.35)",
    "Books":       "rgba(139,92,246,0.35)",
    "Sports":      "rgba(239,68,68,0.35)",
}

_SEG_BRIGHT = {
    "Premium":  "#0EA5E9",
    "Standard": "#6366F1",
    "Budget":   "#D97706",
}
_SEG_DIM = {
    "Premium":  "rgba(14,165,233,0.35)",
    "Standard": "rgba(99,102,241,0.35)",
    "Budget":   "rgba(217,119,6,0.35)",
}


def _bar_charts(df: pd.DataFrame, sel_cat: list[str]):
    section_title("Выручка по категориям и сегментам (год к году)")

    col_cat, col_seg = st.columns(2)

    with col_cat:
        _bar_by_group(
            data=agg_by_category_year(df),
            group_col="category",
            order=sorted(sel_cat),
            bright=_CAT_BRIGHT,
            dim=_CAT_DIM,
        )

    with col_seg:
        _bar_by_group(
            data=agg_by_segment_year(df),
            group_col="segment",
            order=["Premium", "Standard", "Budget"],
            bright=_SEG_BRIGHT,
            dim=_SEG_DIM,
        )


def _bar_by_group(
    data: pd.DataFrame,
    group_col: str,
    order: list[str],
    bright: dict,
    dim: dict,
):
    d23 = data[data["year"] == "2023"].set_index(group_col)["revenue"]
    d24 = data[data["year"] == "2024"].set_index(group_col)["revenue"]
    growth = ((d24 - d23) / d23 * 100).reindex(order)

    fig = go.Figure()

    d = data[data["year"] == "2023"].set_index(group_col).reindex(order).reset_index()
    fig.add_trace(go.Bar(
        x=d[group_col], y=d["revenue"],
        name="2023",
        marker_color=[dim.get(g, "#334155") for g in d[group_col]],
        yaxis="y1",
        hovertemplate="<b>%{x}</b><br>2023: $%{y:,.0f}<extra></extra>",
    ))

    d = data[data["year"] == "2024"].set_index(group_col).reindex(order).reset_index()
    fig.add_trace(go.Bar(
        x=d[group_col], y=d["revenue"],
        name="2024",
        marker_color=[bright.get(g, "#3B82F6") for g in d[group_col]],
        yaxis="y1",
        hovertemplate="<b>%{x}</b><br>2024: $%{y:,.0f}<extra></extra>",
    ))

    g_min, g_max = growth.min(), growth.max()
    padding = max((g_max - g_min) * 0.8, 0.5)
    y2_min = g_min - padding
    y2_max = g_max + padding

    dot_colors = ["#4ADE80" if v >= 0 else "#F87171" for v in growth.values]

    fig.add_trace(go.Scatter(
        x=growth.index.tolist(),
        y=growth.values,
        name="Прирост %",
        mode="lines+markers+text",
        yaxis="y2",
        line=dict(color="rgba(255,255,255,0.2)", width=1.5, dash="dot"),
        marker=dict(color=dot_colors, size=7, line=dict(color="#0F172A", width=1)),
        text=[f"{v:+.1f}%" for v in growth.values],
        textposition="top center",
        textfont=dict(size=11, color=dot_colors),
        hovertemplate="<b>%{x}</b><br>Прирост: %{y:+.1f}%<extra></extra>",
    ))

    dark_layout(fig)
    fig.update_layout(
        barmode="group",
        bargap=0.25,
        bargroupgap=0.08,
        xaxis_title=None,
        yaxis=dict(
            title="Выручка ($)",
            gridcolor="#1E293B",
            linecolor="rgba(0,0,0,0)",
        ),
        yaxis2=dict(
            title=dict(
                text="Прирост, %",
                font=dict(color="#64748B"),
            ),
            overlaying="y",
            side="right",
            showgrid=False,
            ticksuffix="%",
            tickfont=dict(color="#64748B", size=11),
            zeroline=True,
            zerolinecolor="#334155",
            zerolinewidth=1,
            range=[y2_min, y2_max],
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            orientation="h",
            y=1.08, x=0,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


def _conclusions(df: pd.DataFrame):
    section_title("Выводы по акту 1")

    y23 = df[df["year"] == 2023]
    y24 = df[df["year"] == 2024]

    rev_growth  = _delta_pct(y24["revenue"].sum(), y23["revenue"].sum())
    prof_growth = _delta_pct(y24["profit"].sum(),  y23["profit"].sum())
    top_cat     = df.groupby("category")["revenue"].sum().idxmax()
    top_seg     = df.groupby("segment")["revenue"].sum().idxmax()
    avg_sat     = df["customer_satisfaction"].mean()

    insight_card([
        ("1. Устойчивый рост",
         f"Выручка выросла на {rev_growth:+.1f}%, прибыль — на {prof_growth:+.1f}%. "
         "Бизнес развивается стабильно, но при этом имеет выраженную сезонность."),

        (f"2. Лидер — {top_cat}",
         f"Категория {top_cat} генерирует наибольшую выручку. "
         f"Сегмент {top_seg} остаётся ключевым источником дохода по всем категориям."),

        (f"3. Удовлетворённость: {avg_sat:.2f}/5",
         "Средний балл держится ниже 4.5, что является потенциальной точкой развития. "
         "В следующих актах разберём подробнее."),
    ])