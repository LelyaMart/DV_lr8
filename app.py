"""
app.py — точка входа. Конфиг страницы, сайдбар и роутинг между актами.

Запуск:
    streamlit run app.py
"""

import streamlit as st

from config import inject_css
from data import load_data, filter_data
from acts import act1, act2, act3, act4, act5, act6

st.set_page_config(layout="wide", page_title="Business Story")
inject_css()

df = load_data()

ACTS = [
    "Акт 1 — Обзор бизнеса",
    "Акт 2 — Аномалия",
    "Акт 3 — Сегменты",
    "Акт 4 — Причина",
    "Акт 5 — Решение",
    "Акт 6 — Рекомендации",
]


if "act_index" not in st.session_state:
    st.session_state.act_index = 0

with st.sidebar:
    st.markdown("### Business Story")
    st.divider()

    selected = st.radio(
        "Навигация", ACTS,
        index=st.session_state.act_index,
        label_visibility="collapsed",
    )
    st.session_state.act_index = ACTS.index(selected)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**Фильтры**")

    all_categories = sorted(df["category"].unique())
    all_regions = sorted(df["region"].unique())

    if "category_multiselect" not in st.session_state:
        st.session_state.category_multiselect = all_categories.copy()

    if "region_multiselect" not in st.session_state:
        st.session_state.region_multiselect = all_regions.copy()


    st.markdown("##### Категория")

    cat_col1, cat_col2 = st.columns(2)

    with cat_col1:
        if st.button("✓ Все категории", use_container_width=True, key="select_all_categories"):
            st.session_state.category_multiselect = all_categories.copy()
            st.rerun()

    with cat_col2:
        if st.button("✕ Очистить", use_container_width=True, key="clear_categories"):
            st.session_state.category_multiselect = []
            st.rerun()

    sel_cat = st.multiselect(
        "Категория",
        all_categories,
        key="category_multiselect",
        label_visibility="collapsed",
    )


    st.markdown("##### Регион")

    reg_col1, reg_col2 = st.columns(2)

    with reg_col1:
        if st.button("✓ Все регионы", use_container_width=True, key="select_all_regions"):
            st.session_state.region_multiselect = all_regions.copy()
            st.rerun()

    with reg_col2:
        if st.button("✕ Очистить", use_container_width=True, key="clear_regions"):
            st.session_state.region_multiselect = []
            st.rerun()

    sel_reg = st.multiselect(
        "Регион",
        all_regions,
        key="region_multiselect",
        label_visibility="collapsed",
    )
    st.session_state.sel_reg = sel_reg
df_filtered = filter_data(df, sel_cat, sel_reg)

idx = st.session_state.act_index

if idx == 0:
    act1.render(df_filtered, sel_cat, ACTS)
elif idx == 1:
    act2.render(df_filtered, sel_cat, ACTS)
elif idx == 2:
    act3.render(df_filtered, sel_cat, ACTS)
elif idx == 3:
    act4.render(df_filtered, sel_cat, ACTS)
elif idx == 4:
    act5.render(df_filtered, sel_cat, ACTS)
elif idx == 5:
    act6.render(df_filtered, sel_cat, ACTS)