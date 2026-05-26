import pandas as pd
import streamlit as st


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("business_data.csv", parse_dates=["date"])
    df["year"] = df["date"].dt.year
    return df


def filter_data(df: pd.DataFrame, categories: list[str], regions: list[str]) -> pd.DataFrame:
    return df[df["category"].isin(categories) & df["region"].isin(regions)]


def agg_monthly(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(pd.Grouper(key="date", freq="ME"))
        .agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
        .reset_index()
    )


def agg_by_category_year(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby(["category", "year"])["revenue"].sum().reset_index()
    out["year"] = out["year"].astype(str)
    return out


def agg_by_segment_year(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby(["segment", "year"])["revenue"].sum().reset_index()
    out["year"] = out["year"].astype(str)
    return out


def agg_monthly_by_category(df: pd.DataFrame, metric: str = "revenue") -> pd.DataFrame:
    return (
        df.groupby([pd.Grouper(key="date", freq="ME"), "category"])
        .agg(value=(metric, "sum"))
        .reset_index()
        .rename(columns={"value": metric})
    )


def agg_bubble(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("category")
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            satisfaction=("customer_satisfaction", "mean"),
        )
        .reset_index()
        .assign(margin=lambda d: d["profit"] / d["revenue"] * 100)
    )


def agg_monthly_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby([pd.Grouper(key="date", freq="ME"), "segment"])
        .agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
        .reset_index()
    )