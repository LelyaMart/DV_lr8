import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import CAT_COLORS, SEG_COLORS, dark_layout, insight_card, render_nav_buttons, section_title, subtitle

_TARGET_CAT = "Electronics"
_TARGET_SEG = "Premium"
SEG_ORDER = ["Premium", "Standard", "Budget"]


def render(df: pd.DataFrame, sel_cat: list[str], acts: list[str]):
    st.markdown("# Акт 4 — Причина")
    subtitle("Падение удовлетворённости в Electronics и реакция Premium-сегмента")

    if _TARGET_CAT not in df["category"].unique():
        st.warning("Electronics скрыта фильтром категорий. Включите Electronics в сайдбаре.")
        render_nav_buttons(acts)
        return

    monthly_sat = _calc_monthly_satisfaction(df)
    premium_flow = _calc_premium_flow(df)
    segment_mix = _calc_segment_mix(df)

    _kpi_row(df)

    section_title("1. Удовлетворённость клиентов: Electronics против рынка")
    st.plotly_chart(_satisfaction_chart(monthly_sat), use_container_width=True)

    section_title("2. Отток Premium внутри Electronics")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(_premium_flow_chart(premium_flow), use_container_width=True)
    with col2:
        st.plotly_chart(_segment_mix_chart(segment_mix), use_container_width=True)

    section_title("3. Где просела удовлетворённость")
    st.plotly_chart(
        _satisfaction_heatmap(df),
        use_container_width=True,
    )

    _conclusions(df, premium_flow, segment_mix)
    render_nav_buttons(acts)


def _delta_pct(new: float, old: float) -> float:
    return 0.0 if old == 0 else (new - old) / abs(old) * 100


def _calc_monthly_satisfaction(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["group"] = d["category"].where(d["category"] == _TARGET_CAT, "Остальные категории")
    return (
        d.groupby([pd.Grouper(key="date", freq="ME"), "group"])
        .agg(satisfaction=("customer_satisfaction", "mean"))
        .reset_index()
    )


def _calc_premium_flow(df: pd.DataFrame) -> pd.DataFrame:
    d = df[(df["category"] == _TARGET_CAT) & (df["segment"] == _TARGET_SEG)]
    return (
        d.groupby(pd.Grouper(key="date", freq="ME"))
        .agg(
            revenue=("revenue", "sum"),
            satisfaction=("customer_satisfaction", "mean"),
        )
        .reset_index()
    )


def _calc_segment_mix(df: pd.DataFrame) -> pd.DataFrame:
    d = df[df["category"] == _TARGET_CAT]
    by_seg = (
        d.groupby(["year", "segment"])
        .agg(revenue=("revenue", "sum"), satisfaction=("customer_satisfaction", "mean"))
        .reset_index()
    )
    totals = by_seg.groupby("year")["revenue"].transform("sum")
    by_seg["share"] = by_seg["revenue"] / totals * 100
    by_seg["year"] = by_seg["year"].astype(str)
    return by_seg


def _kpi_row(df: pd.DataFrame):
    from config import kpi_html

    elec = df[df["category"] == _TARGET_CAT]
    elec_23 = elec[elec["year"] == 2023]
    elec_24 = elec[elec["year"] == 2024]

    prem = elec[elec["segment"] == _TARGET_SEG]
    prem_23 = prem[prem["year"] == 2023]
    prem_24 = prem[prem["year"] == 2024]

    sat_23 = elec_23["customer_satisfaction"].mean()
    sat_24 = elec_24["customer_satisfaction"].mean()
    prem_sat_23 = prem_23["customer_satisfaction"].mean()
    prem_sat_24 = prem_24["customer_satisfaction"].mean()

    prem_rev_23 = prem_23["revenue"].sum()
    prem_rev_24 = prem_24["revenue"].sum()

    total_23 = elec_23["revenue"].sum()
    total_24 = elec_24["revenue"].sum()
    share_23 = prem_rev_23 / total_23 * 100 if total_23 else 0
    share_24 = prem_rev_24 / total_24 * 100 if total_24 else 0

    st.markdown(f"""
    <div class="kpi-grid">
      {kpi_html("Electronics CSAT 2024", f"{sat_24:.2f} / 5", _delta_pct(sat_24, sat_23), CAT_COLORS.get(_TARGET_CAT, "#3B82F6"))}
      {kpi_html("Premium CSAT в Electronics", f"{prem_sat_24:.2f} / 5", _delta_pct(prem_sat_24, prem_sat_23), SEG_COLORS.get(_TARGET_SEG, "#0EA5E9"))}
      {kpi_html("Выручка Premium", f"${prem_rev_24 / 1e6:.1f}M", _delta_pct(prem_rev_24, prem_rev_23), "#F87171")}
      {kpi_html("Доля Premium в Electronics", f"{share_24:.1f}%", share_24 - share_23, "#8B5CF6")}
    </div>
    """, unsafe_allow_html=True)


def _satisfaction_chart(data: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    colors = {
        _TARGET_CAT: CAT_COLORS.get(_TARGET_CAT, "#3B82F6"),
        "Остальные категории": "rgba(148,163,184,0.65)",
    }

    for group in [_TARGET_CAT, "Остальные категории"]:
        d = data[data["group"] == group].sort_values("date")
        fig.add_trace(go.Scatter(
            x=d["date"],
            y=d["satisfaction"],
            name=group,
            mode="lines+markers" if group == _TARGET_CAT else "lines",
            line=dict(color=colors[group], width=3 if group == _TARGET_CAT else 2),
            marker=dict(size=6, color=colors[group]),
            hovertemplate=f"<b>{group}</b><br>%{{x|%b %Y}}<br>CSAT: %{{y:.2f}} / 5<extra></extra>",
        ))

    elec = data[data["group"] == _TARGET_CAT]
    if not elec.empty:
        low = elec.loc[elec["satisfaction"].idxmin()]
        fig.add_annotation(
            x=low["date"],
            y=low["satisfaction"],
            text=f"Минимум CSAT<br>{low['satisfaction']:.2f} / 5",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#EF4444",
            arrowwidth=1.5,
            ax=70,
            ay=-45,
            font=dict(color="#F87171", size=11),
            bgcolor="rgba(15,23,42,0.85)",
            bordercolor="#EF4444",
            borderwidth=1,
            borderpad=6,
        )

    fig.add_hrect(
        y0=0,
        y1=3.75,
        fillcolor="rgba(239,68,68,0.06)",
        line_width=0,
        layer="below",
    )

    dark_layout(fig)
    fig.update_layout(
        hovermode="x unified",
        yaxis=dict(title="Customer satisfaction", range=[3.0, 4.8], gridcolor="#1E293B"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#CBD5E1"), orientation="h", y=1.06, x=0),
    )
    return fig


def _premium_flow_chart(data: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=data["date"],
        y=data["revenue"],
        name="Выручка Premium",
        marker_color=SEG_COLORS.get(_TARGET_SEG, "#0EA5E9"),
        opacity=0.85,
        hovertemplate="<b>%{x|%b %Y}</b><br>Выручка: $%{y:,.0f}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=data["date"],
        y=data["satisfaction"],
        name="CSAT Premium",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="#F87171", width=2.5),
        marker=dict(size=6, color="#F87171", line=dict(color="#0F172A", width=1)),
        hovertemplate="<b>%{x|%b %Y}</b><br>CSAT: %{y:.2f} / 5<extra></extra>",
    ))

    dark_layout(fig)
    fig.update_layout(
        title=dict(text="Premium в Electronics: выручка падает вслед за CSAT", font=dict(size=14, color="#94A3B8"), x=0),
        yaxis=dict(title="Выручка ($)", tickprefix="$", gridcolor="#1E293B"),
        yaxis2=dict(title="CSAT", overlaying="y", side="right", range=[3.2, 4.8], showgrid=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#CBD5E1"), orientation="h", y=1.08, x=0),
        bargap=0.18,
    )
    return fig


def _segment_mix_chart(data: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    for seg in SEG_ORDER:
        d = data[data["segment"] == seg].sort_values("year")
        fig.add_trace(go.Bar(
            x=d["year"],
            y=d["share"],
            name=seg,
            marker_color=SEG_COLORS.get(seg, "#94A3B8"),
            hovertemplate=f"<b>{seg}</b><br>%{{x}}<br>Доля: %{{y:.1f}}%<extra></extra>",
        ))

    prem = data[data["segment"] == _TARGET_SEG].sort_values("year")

    dark_layout(fig)
    fig.update_layout(
        title=dict(text="Структура выручки Electronics по сегментам", font=dict(size=14, color="#94A3B8"), x=0),
        barmode="stack",
        yaxis=dict(title="Доля в выручке", ticksuffix="%", range=[0, 100], gridcolor="#1E293B"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#CBD5E1"), orientation="h", y=1.08, x=0),
    )
    return fig


def _conclusions(df: pd.DataFrame, premium_flow: pd.DataFrame, segment_mix: pd.DataFrame):
    section_title("Выводы по акту 4")

    elec = df[df["category"] == _TARGET_CAT]
    elec_23 = elec[elec["year"] == 2023]
    elec_24 = elec[elec["year"] == 2024]

    sat_drop = _delta_pct(
        elec_24["customer_satisfaction"].mean(),
        elec_23["customer_satisfaction"].mean(),
    )

    prem = elec[elec["segment"] == _TARGET_SEG]
    prem_23 = prem[prem["year"] == 2023]
    prem_24 = prem[prem["year"] == 2024]

    prem_rev_drop = _delta_pct(
        prem_24["revenue"].sum(),
        prem_23["revenue"].sum(),
    )

    shares = segment_mix[segment_mix["segment"] == _TARGET_SEG].set_index("year")["share"]
    share_delta = shares.get("2024", 0) - shares.get("2023", 0)

    corr = 0.0
    if len(premium_flow) > 1:
        corr = premium_flow[["satisfaction", "revenue"]].corr().iloc[0, 1]

    insight_card([
        ("1. Причина — CSAT Electronics",
         f"При сезонных спадах удовлетворенность Electronics минимально, но снижается. "
         "Значит, даже минимальные колебания уровня сервиса сказываются на возвращаемости, и как следствие прибыли."),

        ("2. Premium реагирует первым",
         f"Выручка Premium внутри Electronics изменилась на {prem_rev_drop:+.1f}%, "
         f"а его доля в категории — на {share_delta:+.1f} п.п."),

        ("3. Связь метрик",
         f"Месячная корреляция между CSAT и выручкой Premium в Electronics: {corr:.2f}. "
         "Когда удовлетворённость проседает, Premium-покупатели сокращают покупки быстрее остальных."),
    ])

def _satisfaction_heatmap(df: pd.DataFrame) -> go.Figure:
    d = df[df["category"] == _TARGET_CAT].copy()

    heat = (
        d.groupby(["segment", "year"])
        .agg(satisfaction=("customer_satisfaction", "mean"))
        .reset_index()
    )

    heat["year"] = heat["year"].astype(str)

    pivot = (
        heat.pivot(index="segment", columns="year", values="satisfaction")
        .reindex(SEG_ORDER)
    )

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[
            [0.0, "#7F1D1D"],
            [0.5, "#F59E0B"],
            [1.0, "#10B981"],
        ],
        zmin=3.0,
        zmax=4.8,
        colorbar=dict(
            title=dict(
                text="CSAT",
                font=dict(color="#94A3B8"),
            ),
            title="CSAT",
            tickfont=dict(color="#94A3B8"),
        ),
        text=[[f"{v:.2f}" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont=dict(color="#F8FAFC", size=14),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Год: %{x}<br>"
            "CSAT: %{z:.2f} / 5"
            "<extra></extra>"
        ),
    ))

    dark_layout(fig, legend=False)
    fig.update_layout(
        title=dict(
            text="Customer satisfaction в Electronics: сегменты × годы",
            font=dict(size=14, color="#94A3B8"),
            x=0,
        ),
        xaxis=dict(
            title="Год",
            gridcolor="#1E293B",
            linecolor="#334155",
        ),
        yaxis=dict(
            title="Сегмент",
            gridcolor="#1E293B",
            linecolor="#334155",
        ),
        height=360,
    )

    return fig