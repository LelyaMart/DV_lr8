import streamlit as st
import plotly.graph_objects as go

CAT_COLORS = {
    "Electronics": "#3B82F6",
    "Clothing":    "#10B981",
    "Home":        "#F59E0B",
    "Books":       "#8B5CF6",
    "Sports":      "#EF4444",
}

SEG_COLORS = {
    "Premium":  "#0EA5E9",
    "Standard": "#64748B",
    "Budget":   "#D97706",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #0F172A; color: #F1F5F9; }
section[data-testid="stSidebar"] { background: #1E293B; }
.block-container { padding-top: 2rem !important; }

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}
.kpi-card {
    background: #1E293B;
    border-radius: 14px;
    padding: 20px 22px;
    border-top: 3px solid var(--accent);
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 100px; height: 100px;
    background: var(--accent);
    opacity: 0.06;
    border-radius: 50%;
}
.kpi-label {
    font-size: 11px; font-weight: 600; color: #64748B;
    text-transform: uppercase; letter-spacing: .08em; margin-bottom: 8px;
}
.kpi-value { font-size: 30px; font-weight: 700; color: #F1F5F9; line-height: 1; }
.kpi-delta { font-size: 12px; font-weight: 500; margin-top: 6px; }
.delta-pos { color: #4ADE80; }
.delta-neg { color: #F87171; }

.section-title {
    font-size: 13px; font-weight: 600; color: #64748B;
    text-transform: uppercase; letter-spacing: .08em;
    margin: 28px 0 14px;
    display: flex; align-items: center; gap: 8px;
}
.section-title::after { content: ''; flex: 1; height: 1px; background: #1E293B; }

.nav-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #1E293B;
}
.nav-step {
    font-size: 12px; color: #475569; text-align: center;
}

.insight-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-top: 8px;
}
.insight-card {
    background: #1E293B;
    border-radius: 12px;
    padding: 18px 20px;
    border-left: 3px solid #38BDF8;
}
.insight-card-title {
    font-size: 13px; font-weight: 700; color: #F1F5F9;
    margin-bottom: 8px;
}
.insight-card-body {
    font-size: 13px; color: #94A3B8; line-height: 1.6;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #E2E8F0 !important;
}

.stMultiSelect div[data-baseweb="select"] > div {
    background-color: #0F172A !important;
    border: 1px solid #334155 !important;
    color: #F8FAFC !important;
}

.stMultiSelect span[data-baseweb="tag"] {
    background-color: #EF4444 !important;
    color: white !important;
}

div[role="listbox"] {
    background-color: #0F172A !important;
    color: #F8FAFC !important;
}

div[role="option"]:hover {
    background-color: #1E293B !important;
}

.stButton > button {
    background: #1E293B !important;
    color: #F8FAFC !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    border-color: #3B82F6 !important;
    color: #FFFFFF !important;
    background: #2563EB !important;
}

.stButton > button:disabled {
    background: #334155 !important;
    color: #CBD5E1 !important;
    opacity: 0.7 !important;
}

header[data-testid="stHeader"] {
    display: none;
}

div[data-testid="stToolbar"] {
    display: none;
}

div[data-testid="stDecoration"] {
    display: none;
}

.block-container {
    padding-top: 1.2rem !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 1rem !important;
    padding-left: 0.8rem !important;
    padding-right: 0.8rem !important;
}

.sidebar-title {
    margin-bottom: 0.8rem !important;
}

section[data-testid="stSidebar"] hr {
    margin-top: 0.6rem !important;
    margin-bottom: 0.8rem !important;
    border-color: #1E293B !important;
}

section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] h5 {
    margin-top: 0.7rem !important;
    margin-bottom: 0.35rem !important;
}

div[role="radiogroup"] {
    gap: 0.15rem !important;
}

.stButton > button {
    padding-top: 0.35rem !important;
    padding-bottom: 0.35rem !important;
    min-height: 38px !important;
}

.element-container:has(.stButton) {
    margin-bottom: 0.2rem !important;
}

.stMultiSelect {
    margin-top: -0.2rem !important;
    margin-bottom: 0.5rem !important;
}

.stMultiSelect div[data-baseweb="select"] > div {
    min-height: 42px !important;
    padding-top: 2px !important;
    padding-bottom: 2px !important;
}

.stMultiSelect span[data-baseweb="tag"] {
    margin: 2px !important;
    padding-top: 1px !important;
    padding-bottom: 1px !important;
}

.filter-block {
    margin-bottom: 0.8rem !important;
}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def dark_layout(fig: go.Figure, title: str = "", legend: bool = True) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#F1F5F9"), x=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94A3B8", size=12),
        legend=dict(
            bgcolor="rgba(0,0,0,0)", font=dict(color="#CBD5E1"),
            orientation="h", y=1.08, x=0,
        ) if legend else dict(visible=False),
        xaxis=dict(gridcolor="#1E293B", linecolor="#334155", showgrid=False),
        yaxis=dict(gridcolor="#1E293B", linecolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=44, b=0),
        hoverlabel=dict(
            bgcolor="#1E293B", bordercolor="#334155",
            font=dict(color="#F1F5F9", size=12),
        ),
    )
    return fig


def kpi_html(label: str, value: str, delta: float | None = None, accent: str = "#3B82F6") -> str:
    delta_html = ""
    if delta is not None:
        sign  = "+" if delta >= 0 else ""
        cls   = "delta-pos" if delta >= 0 else "delta-neg"
        arrow = "↑" if delta >= 0 else "↓"
        delta_html = f'<div class="kpi-delta {cls}">{arrow} {sign}{delta:.1f}% к 2023</div>'
    return f"""
    <div class="kpi-card" style="--accent:{accent}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {delta_html}
    </div>"""


def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def subtitle(text: str):
    st.markdown(f'<div class="subtitle">{text}</div>', unsafe_allow_html=True)


def insight_card(items: list[tuple[str, str]]):
    cards_html = "\n".join(
        f"""<div class="insight-card">
              <div class="insight-card-title">{title}</div>
              <div class="insight-card-body">{body}</div>
            </div>"""
        for title, body in items
    )
    st.markdown(
        f'<div class="insight-grid">{cards_html}</div>',
        unsafe_allow_html=True,
    )


def render_nav_buttons(acts: list[str]):
    current = st.session_state.act_index
    total   = len(acts)

    st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
    col_prev, col_mid, col_next = st.columns([1, 2, 1])

    with col_prev:
        if current > 0:
            if st.button("← Назад", use_container_width=True, key=f"nav_prev_{current}"):
                st.session_state.act_index = current - 1
                st.rerun()

    with col_mid:
        st.markdown(
            f'<div class="nav-step">Шаг {current + 1} из {total}</div>',
            unsafe_allow_html=True,
        )

    with col_next:
        if current < total - 1:
            if st.button("Далее →", use_container_width=True, key=f"nav_next_{current}"):
                st.session_state.act_index = current + 1
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)