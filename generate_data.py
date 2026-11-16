"""Creates a SIMULATED dataset of chai and coffee sales across Indian cities.
Run: python generate_data.py
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

cities = {
    # city: (average temp C, chai love, coffee love)
    "Mumbai":    (28, 1.15, 0.85),
    "Delhi":     (22, 1.45, 0.65),
    "Bengaluru": (24, 0.75, 1.35),
    "Chennai":   (30, 0.70, 1.40),
    "Kolkata":   (26, 1.30, 0.80),
    "Hyderabad": (27, 1.05, 0.95),
}
# how busy each hour is for tea/coffee (peaks morning + evening)
hour_peak = {h: 0.3 for h in range(6, 23)}
for h, v in {6: 0.8, 7: 1.4, 8: 1.6, 9: 1.2, 10: 0.9, 11: 0.7, 12: 0.6, 13: 0.6,
             14: 0.7, 15: 1.0, 16: 1.5, 17: 1.7, 18: 1.4, 19: 0.9, 20: 0.6}.items():
    hour_peak[h] = v

rows = []
dates = pd.date_range("2026-01-01", periods=90)
for date in dates:
    for city, (base_t, chai_love, coffee_love) in cities.items():
        day_temp = base_t + rng.normal(0, 2.5) + 4 * np.sin(date.dayofyear / 14)
        for hour in range(6, 23):
            temp = day_temp + (3 if 12 <= hour <= 16 else -2 if hour < 8 else 0)
            cold_boost = 1 + max(0, (24 - temp)) * 0.05   # chai wins when cold
            heat_boost = 1 + max(0, (temp - 29)) * 0.04   # coffee (iced) wins when hot
            for drink, love, boost, price in (
                ("Chai", chai_love, cold_boost, 15),
                ("Coffee", coffee_love, heat_boost, 40),
            ):
                lam = 12 * hour_peak[hour] * love * boost
                if drink == "Coffee" and hour >= 9:
                    lam *= 1.15   # coffee is a bit stronger in office hours
                cups = rng.poisson(lam)
                rows.append([date.date(), city, hour, round(temp, 1), drink, cups,
                             price + rng.choice([-2, 0, 0, 2])])

df = pd.DataFrame(rows, columns=["date", "city", "hour", "temperature_c",
                                 "drink", "cups_sold", "price_inr"])

# add a little mess on purpose so the cleaning step has real work to do
bad = rng.choice(df.index, size=150, replace=False)
df.loc[bad, "temperature_c"] = np.nan
df = pd.concat([df, df.sample(60, random_state=1)], ignore_index=True)

df.to_csv("chai_coffee_sales.csv", index=False)
print(f"Saved {len(df)} rows to chai_coffee_sales.csv")
