import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import CAT_COLORS, dark_layout, insight_card, section_title, subtitle, render_nav_buttons
from data import agg_monthly_by_category, agg_bubble

_ANOMALY_START = "2023-09-01"
_ANOMALY_END   = "2023-12-30"
_ANOMALY_CAT   = "Electronics"


def render(df: pd.DataFrame, sel_cat: list[str], acts: list[str]):
    st.markdown("# Акт 2 — Поиск аномалии")
    subtitle("Динамика прибыли по категориям — где скрыта проблема?")

    prof_data   = agg_monthly_by_category(df, "profit")
    bubble_data = agg_bubble(df)

    section_title("Прибыль по категориям")
    st.plotly_chart(
        _profit_chart(prof_data, sel_cat),
        use_container_width=True,
    )

    section_title("Маржа vs удовлетворённость по категориям")
    st.plotly_chart(
        _bubble_chart(bubble_data, sel_cat),
        use_container_width=True,
    )

    _conclusions(prof_data, sel_cat)
    render_nav_buttons(acts)


def _profit_chart(data: pd.DataFrame, sel_cat: list[str]) -> go.Figure:
    fig = go.Figure()

    for cat in sel_cat:
        d = data[data["category"] == cat].sort_values("date")
        fig.add_trace(go.Scatter(
            x=d["date"], y=d["profit"],
            name=cat,
            mode="lines",
            line=dict(color=CAT_COLORS.get(cat, "#94A3B8"), width=2),
            hovertemplate=f"<b>{cat}</b><br>%{{x|%b %Y}}<br>Прибыль: $%{{y:,.0f}}<extra></extra>",
        ))

    _add_anomaly_band(fig)

    if _ANOMALY_CAT in sel_cat:
        _add_anomaly_arrow(fig, data)

    dark_layout(fig)
    fig.update_layout(
        hovermode="x unified",
        yaxis_title="Прибыль ($)",
        yaxis_tickprefix="$",
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#CBD5E1"),
                    orientation="h", y=1.06, x=0),
    )
    return fig


def _add_anomaly_band(fig: go.Figure):
    x0, x1 = pd.Timestamp(_ANOMALY_START), pd.Timestamp(_ANOMALY_END)

    fig.add_vrect(
        x0=x0, x1=x1,
        fillcolor="rgba(239,68,68,0.07)",
        line_width=0, layer="below",
    )
    for x in [x0, x1]:
        fig.add_vline(
            x=int(x.timestamp() * 1000),
            line_dash="dot", line_color="rgba(239,68,68,0.35)", line_width=1,
        )
    fig.add_annotation(
        x=pd.Timestamp("2023-09-15"), y=1, yref="paper",
        text="⚠ Аномальный период",
        showarrow=False,
        font=dict(color="rgba(239,68,68,0.7)", size=11),
        xanchor="center", yanchor="top",
    )


def _add_anomaly_arrow(fig: go.Figure, data: pd.DataFrame):
    elec = data[
        (data["category"] == _ANOMALY_CAT) &
        (data["date"] >= _ANOMALY_START) &
        (data["date"] <= _ANOMALY_END)
    ]
    if elec.empty:
        return
    row = elec.loc[elec["profit"].idxmin()]
    fig.add_annotation(
        x=row["date"], y=row["profit"],
        text=f"Минимум {_ANOMALY_CAT}<br>${row['profit']:,.0f}",
        showarrow=True, arrowhead=2,
        arrowcolor="#EF4444", arrowwidth=1.5,
        ax=60, ay=-50,
        font=dict(color="#F87171", size=11),
        bgcolor="rgba(15,23,42,0.8)",
        bordercolor="#EF4444", borderwidth=1, borderpad=6,
    )


def _bubble_chart(data: pd.DataFrame, sel_cat: list[str]) -> go.Figure:
    d = data[data["category"].isin(sel_cat)].copy()

    fig = go.Figure()

    for _, row in d.iterrows():
        color = CAT_COLORS.get(row["category"], "#94A3B8")
        is_target = row["category"] == _ANOMALY_CAT

        fig.add_trace(go.Scatter(
            x=[row["satisfaction"]],
            y=[row["margin"]],
            mode="markers+text",
            name=row["category"],
            marker=dict(
                size=row["revenue"] / d["revenue"].max() * 80 + 20,
                color=color,
                opacity=0.85,
                line=dict(
                    color="#EF4444" if is_target else "rgba(255,255,255,0.2)",
                    width=3 if is_target else 1,
                ),
            ),
            text=row["category"],
            textposition="top center",
            textfont=dict(color=color, size=12),
            hovertemplate=(
                f"<b>{row['category']}</b><br>"
                f"Удовлетворённость: {row['satisfaction']:.3f}<br>"
                f"Маржа: {row['margin']:.1f}%<br>"
                f"Выручка: ${row['revenue']:,.0f}"
                "<extra></extra>"
            ),
        ))

    elec = d[d["category"] == _ANOMALY_CAT]
    if not elec.empty:
        fig.add_annotation(
            x=elec["satisfaction"].values[0],
            y=elec["margin"].values[0],
            text="Самая низкая удовлетворённость<br>при высокой выручке",
            showarrow=True, arrowhead=2,
            arrowcolor="#EF4444", arrowwidth=1.5,
            ax=90, ay=-50,
            font=dict(color="#F87171", size=11),
            bgcolor="rgba(15,23,42,0.85)",
            bordercolor="#EF4444", borderwidth=1, borderpad=6,
        )

    avg_sat    = d["satisfaction"].mean()
    avg_margin = d["margin"].mean()
    fig.add_vline(x=avg_sat,    line_dash="dot", line_color="#334155", line_width=1)
    fig.add_hline(y=avg_margin, line_dash="dot", line_color="#334155", line_width=1)

    dark_layout(fig, legend=False)
    fig.update_layout(
        showlegend=False,
        xaxis=dict(
            title="Средняя удовлетворённость клиентов",
            gridcolor="#1E293B",
            linecolor="#334155",
        ),
        yaxis=dict(
            title="Маржа, %",
            ticksuffix="%",
            gridcolor="#1E293B",
            linecolor="rgba(0,0,0,0)",
        ),
        height=420,
    )
    return fig


def _conclusions(prof_data: pd.DataFrame, sel_cat: list[str]):
    section_title("Выводы по акту 2")

    elec = prof_data[prof_data["category"] == _ANOMALY_CAT].sort_values("date")
    anomaly = elec[elec["date"].between(_ANOMALY_START, _ANOMALY_END)]
    normal  = elec[~elec["date"].between(_ANOMALY_START, _ANOMALY_END)]

    drop_pct = 0.0
    if not anomaly.empty and not normal.empty:
        drop_pct = (anomaly["profit"].mean() - normal["profit"].mean()) / normal["profit"].mean() * 100

    others_dropped = []
    for cat in sel_cat:
        if cat == _ANOMALY_CAT:
            continue
        d = prof_data[prof_data["category"] == cat]
        a = d[d["date"].between(_ANOMALY_START, _ANOMALY_END)]["profit"].mean()
        n = d[~d["date"].between(_ANOMALY_START, _ANOMALY_END)]["profit"].mean()
        if n and (a - n) / n * 100 < -5:
            others_dropped.append(cat)

    others_txt = (
        f"Похожую динамику показали: {', '.join(others_dropped)}."
        if others_dropped else
        "Остальные категории в этот период вели себя стабильно."
    )

    insight_card([
        ("1. Провал Electronics",
         f"С августа по декабрь 2023 года прибыль Electronics упала в среднем на {drop_pct:.1f}% "
         "относительно остального периода — самое глубокое отклонение среди всех категорий."),

        ("2. Сезонность или проблема?",
         f"Провал повторяется и в 2024 году в те же месяцы — значит, это не разовый сбой. "
         f"{others_txt}"),

        ("3. Следующий шаг",
         "Нужно выяснить причину: падение удовлетворённости, рост себестоимости "
         "или отток конкретного сегмента."),
    ])