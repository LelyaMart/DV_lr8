import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_business_data(start_date='2023-01-01', end_date='2024-12-31', seed=42):
    """
    Generates synthetic business sales data with seasonality, trend and random noise.
    """
    np.random.seed(seed)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    categories = ['Electronics', 'Clothing', 'Home', 'Books', 'Sports']
    regions = ['North', 'South', 'East', 'West']
    segments = ['Premium', 'Standard', 'Budget']

    base_revenue = {
        'Electronics': 5000,
        'Clothing': 3000,
        'Home': 4000,
        'Books': 1500,
        'Sports': 2500,
    }
    trend_factor = 0.0003
    seasonality_amplitude = 0.25

    rows = []
    for date in dates:
        month = date.month
        season = 1 + seasonality_amplitude * np.sin(2 * np.pi * (month - 1) / 12)
        day_index = (date - dates[0]).days
        trend = 1 + trend_factor * day_index

        for cat in categories:
            for reg in regions:
                for seg in segments:
                    rev_base = base_revenue[cat] * season * trend
                    reg_factor = {'North': 1.2, 'South': 0.9, 'East': 1.0, 'West': 1.1}[reg]
                    seg_factor = {'Premium': 2.0, 'Standard': 1.0, 'Budget': 0.6}[seg]
                    noise = np.random.lognormal(0, 0.2)
                    revenue = rev_base * reg_factor * seg_factor * noise

                    cost = revenue * np.random.uniform(0.55, 0.65)
                    profit = revenue - cost

                    avg_price = {
                        'Electronics': 200,
                        'Clothing': 50,
                        'Home': 80,
                        'Books': 25,
                        'Sports': 60,
                    }[cat]
                    units_sold = int(revenue / avg_price * np.random.uniform(0.8, 1.2))

                    base_satisfaction = {'Premium': 4.5, 'Standard': 3.8, 'Budget': 3.2}[seg]
                    cat_satisfaction_delta = {
                        'Electronics': -0.3,
                        'Clothing': 0.1,
                        'Home': 0.0,
                        'Books': 0.2,
                        'Sports': 0.1,
                    }[cat]
                    sat = base_satisfaction + cat_satisfaction_delta + np.random.normal(0, 0.3)
                    sat = max(1, min(5, sat))
                    print(date)
                    rows.append([date, cat, reg, seg, revenue, cost, profit, units_sold, sat])

    df = pd.DataFrame(
        rows,
        columns=[
            'date', 'category', 'region', 'segment',
            'revenue', 'cost', 'profit', 'units_sold', 'customer_satisfaction',
        ],
    )
    return df


if __name__ == "__main__":
    df = generate_business_data()
    df.to_csv('business_data.csv', index=False)
    print("business_data.csv has been created successfully.")