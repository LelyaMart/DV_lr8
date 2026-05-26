import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import SEG_COLORS, dark_layout, insight_card, render_nav_buttons, section_title, subtitle

SEG_ORDER = ["Premium", "Standard", "Budget"]


def render(df: pd.DataFrame, sel_cat: list[str], acts: list[str]):
    st.markdown("# Акт 3 — Анализ сегментов")
    subtitle("Кто формирует выручку и прибыль — размер и динамика каждого сегмента")

    totals = _calc_totals(df)
    yoy    = _calc_yoy(df)

    section_title("Абсолютные показатели")
    st.plotly_chart(
        _combined_bar(totals),
        use_container_width=True,
    )

    section_title("Динамика 2023 → 2024")
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(
            _yoy_bar(yoy, "revenue", "revenue_23", "rev_growth", "Выручка: 2023 vs 2024"),
            use_container_width=True,
        )
    with col4:
        st.plotly_chart(
            _yoy_bar(yoy, "profit", "profit_23", "prof_growth", "Прибыль: 2023 vs 2024"),
            use_container_width=True,
        )

    _conclusions(totals, yoy)
    render_nav_buttons(acts)


def _calc_totals(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("segment")
        .agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
        .reindex(SEG_ORDER)
        .reset_index()
        .assign(margin=lambda d: d["profit"] / d["revenue"] * 100)
    )


def _calc_yoy(df: pd.DataFrame) -> pd.DataFrame:
    by_year = (
        df.groupby(["segment", "year"])
        .agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
        .reset_index()
    )
    y23 = by_year[by_year["year"] == 2023].set_index("segment")
    y24 = by_year[by_year["year"] == 2024].set_index("segment")
    out = y24.copy()
    out["revenue_23"]  = y23["revenue"]
    out["profit_23"]   = y23["profit"]
    out["rev_growth"]  = (out["revenue"] - out["revenue_23"]) / out["revenue_23"] * 100
    out["prof_growth"] = (out["profit"]  - out["profit_23"])  / out["profit_23"]  * 100
    return out.reindex(SEG_ORDER).reset_index()


def _simple_bar(totals: pd.DataFrame, metric: str, title: str, show_margin: bool) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=totals["segment"],
        y=totals[metric],
        marker_color=[SEG_COLORS[s] for s in totals["segment"]],
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
        showlegend=False,
    ))

    if show_margin:
        for _, row in totals.iterrows():
            fig.add_annotation(
                x=row["segment"], y=row[metric],
                text=f"маржа {row['margin']:.1f}%",
                showarrow=False, yshift=12,
                font=dict(color="#64748B", size=11),
            )

    dark_layout(fig, legend=False)
    fig.update_layout(
        bargap=0.4,
        yaxis_tickprefix="$",
        title=dict(text=title, font=dict(size=14, color="#94A3B8"), x=0),
    )
    return fig

def _combined_bar(totals: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=totals["segment"],
        y=totals["revenue"],
        name="Выручка",
        marker_color=[SEG_COLORS[s] for s in totals["segment"]],
        opacity=0.9,
        hovertemplate="<b>%{x}</b><br>Выручка: $%{y:,.0f}<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        x=totals["segment"],
        y=totals["profit"],
        name="Прибыль",
        marker_color=[SEG_COLORS[s] for s in totals["segment"]],
        opacity=0.35,
        hovertemplate="<b>%{x}</b><br>Прибыль: $%{y:,.0f}<extra></extra>",
    ))

    for _, row in totals.iterrows():
        fig.add_annotation(
            x=row["segment"],
            y=row["profit"],
            text=f"маржа {row['margin']:.1f}%",
            showarrow=False,
            yshift=12,
            font=dict(
                color="#CBD5E1",
                size=12,
            ),
            bgcolor="rgba(15,23,42,0.85)",
            bordercolor="#334155",
            borderwidth=1,
            borderpad=4,        
        )

    dark_layout(fig)

    fig.update_layout(
        title=dict(
            text="Выручка, прибыль и маржа по сегментам",
            font=dict(size=14, color="#94A3B8"),
            x=0,
        ),
        barmode="group",
        bargap=0.32,
        bargroupgap=0.08,

        yaxis=dict(
            title="Сумма ($)",
            tickprefix="$",
            gridcolor="#1E293B",
            linecolor="rgba(0,0,0,0)",
        ),

        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            orientation="h",
            y=1.06,
            x=0,
        ),
    )

    return fig


def _yoy_bar(
    yoy: pd.DataFrame,
    col_24: str,
    col_23: str,
    growth_col: str,
    title: str,
) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=yoy["segment"], y=yoy[col_23],
        name="2023",
        marker_color=[SEG_COLORS[s] for s in yoy["segment"]],
        opacity=0.35,
        hovertemplate="<b>%{x}</b><br>2023: $%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=yoy["segment"], y=yoy[col_24],
        name="2024",
        marker_color=[SEG_COLORS[s] for s in yoy["segment"]],
        opacity=1.0,
        hovertemplate="<b>%{x}</b><br>2024: $%{y:,.0f}<extra></extra>",
    ))

    growth_vals = yoy[growth_col]

    fig.add_trace(go.Scatter(
        x=yoy["segment"],
        y=growth_vals,
        name="Прирост %",
        yaxis="y2",
        mode="lines+markers+text",
        line=dict(color="rgba(255,255,255,0.25)", width=1.5, dash="dot"),
        marker=dict(
            size=7,
            color=["#4ADE80" if v >= 0 else "#F87171" for v in growth_vals],
            line=dict(color="#0F172A", width=1),
        ),
        text=[f"{v:+.1f}%" for v in growth_vals],
        textposition="top center",
        textfont=dict(
            size=11,
            color=["#4ADE80" if v >= 0 else "#F87171" for v in growth_vals],
        ),
        hovertemplate="<b>%{x}</b><br>Прирост: %{y:+.1f}%<extra></extra>",
    ))

    dark_layout(fig)
    fig.update_layout(
        barmode="group",
        bargap=0.3, bargroupgap=0.06,
        yaxis_tickprefix="$",
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#CBD5E1"),
                    orientation="h", y=1.06, x=0),
        title=dict(text=title, font=dict(size=14, color="#94A3B8"), x=0),
        yaxis2=dict(
        title="Прирост, %",
        overlaying="y",
        side="right",
        ticksuffix="%",
        showgrid=False,
        zeroline=True,
        zerolinecolor="#334155",
        tickfont=dict(color="#64748B", size=11),
        ),
    )
    return fig


def _conclusions(totals: pd.DataFrame, yoy: pd.DataFrame):
    section_title("Выводы по акту 3")

    total_rev  = totals["revenue"].sum()
    total_prof = totals["profit"].sum()
    prem       = totals[totals["segment"] == "Premium"].iloc[0]
    budg       = totals[totals["segment"] == "Budget"].iloc[0]
    prem_yoy   = yoy[yoy["segment"] == "Premium"].iloc[0]

    insight_card([
        ("1. Premium — главный донор",
         f"Сегмент Premium даёт {prem['revenue']/total_rev*100:.1f}% выручки "
         f"и {prem['profit']/total_prof*100:.1f}% прибыли. "
         f"Маржа Premium: {prem['margin']:.1f}% против {budg['margin']:.1f}% у Budget."),

        ("2. Рост 2023 → 2024",
         f"Выручка Premium выросла на {prem_yoy['rev_growth']:+.1f}%, "
         f"прибыль — на {prem_yoy['prof_growth']:+.1f}%. "
         "Все три сегмента показали положительную динамику."),

        ("3. Следующий шаг",
         "Структура сегментов здорова — нет оттока и нет перекосов. "
         "Значит, причина провала из акта 2 — внутри конкретной категории. "
         "В акте 4 проверим удовлетворённость."),
    ])