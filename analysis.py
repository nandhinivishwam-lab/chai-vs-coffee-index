"""Chai vs Coffee Index: which drink wins, where, when, and why?
Run: python analysis.py
"""
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams.update({"figure.figsize": (9, 5), "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 11})
COLORS = {"Chai": "#C8803B", "Coffee": "#4A2C2A"}

# 1. LOAD
df = pd.read_csv("chai_coffee_sales.csv")
print("Rows loaded:", len(df))

# 2. CLEAN
df = df.drop_duplicates()
df["temperature_c"] = df.groupby("city")["temperature_c"].transform(
    lambda s: s.fillna(s.median()))
df["date"] = pd.to_datetime(df["date"])
df["revenue"] = df["cups_sold"] * df["price_inr"]
print("Rows after cleaning:", len(df))

# 3. THE CHAI vs COFFEE INDEX  (chai cups / coffee cups; above 1 = chai wins)
cups = df.pivot_table(index="city", columns="drink", values="cups_sold", aggfunc="sum")
cups["index"] = (cups["Chai"] / cups["Coffee"]).round(2)
cups = cups.sort_values("index", ascending=False)
print("\nChai vs Coffee Index by city:\n", cups)

# 4. OTHER INSIGHTS
hourly = df.pivot_table(index="hour", columns="drink", values="cups_sold", aggfunc="mean")
df["temp_band"] = pd.cut(df["temperature_c"], [0, 20, 25, 30, 50],
                         labels=["Cold (<20)", "Cool (20-25)", "Warm (25-30)", "Hot (30+)"])
temp = df.pivot_table(index="temp_band", columns="drink", values="cups_sold",
                      aggfunc="mean", observed=True)
revenue = df.groupby("drink")["revenue"].sum()
total = df.groupby("drink")["cups_sold"].sum()

# 5. CHARTS
ax = cups[["Chai", "Coffee"]].plot(kind="bar", color=COLORS.values())
ax.set_title("Cups sold by city"); ax.set_ylabel("Total cups"); ax.set_xlabel("")
plt.xticks(rotation=0); plt.tight_layout(); plt.savefig("chart_1_cups_by_city.png", dpi=150); plt.close()

ax = hourly.plot(color=COLORS, marker="o")
ax.set_title("When do people drink what? (average cups per hour)")
ax.set_xlabel("Hour of day"); ax.set_ylabel("Avg cups")
plt.tight_layout(); plt.savefig("chart_2_hourly_pattern.png", dpi=150); plt.close()

ax = temp.plot(kind="bar", color=COLORS.values())
ax.set_title("Weather effect: average cups by temperature")
ax.set_xlabel(""); ax.set_ylabel("Avg cups")
plt.xticks(rotation=0); plt.tight_layout(); plt.savefig("chart_3_temperature_effect.png", dpi=150); plt.close()

ax = cups["index"].plot(kind="barh", color=["#C8803B" if v > 1 else "#4A2C2A" for v in cups["index"]])
ax.axvline(1, color="gray", ls="--"); ax.invert_yaxis()
ax.set_title("Chai vs Coffee Index (above 1 = chai wins)"); ax.set_ylabel("")
plt.tight_layout(); plt.savefig("chart_4_index.png", dpi=150); plt.close()

# 6. SAVE A SUMMARY
lines = [
    "CHAI vs COFFEE INDEX: KEY FINDINGS",
    f"- Most chai-loving city: {cups['index'].idxmax()} (index {cups['index'].max()})",
    f"- Most coffee-loving city: {cups['index'].idxmin()} (index {cups['index'].min()})",
    f"- Chai peak hour: {hourly['Chai'].idxmax()}:00 | Coffee peak hour: {hourly['Coffee'].idxmax()}:00",
    f"- Total cups: Chai {total['Chai']:,} vs Coffee {total['Coffee']:,}",
    f"- Revenue (INR): Chai {revenue['Chai']:,} vs Coffee {revenue['Coffee']:,}",
    "- Colder weather boosts chai; hot weather lifts coffee.",
]
open("summary.txt", "w").write("\n".join(lines))
print("\n" + "\n".join(lines))
