import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# 1. LOAD DATA
# =========================

# Load Nifty daily changes
nifty = pd.read_excel("change.xlsx")
nifty.columns = nifty.columns.str.strip()
nifty['Date'] = pd.to_datetime(nifty['Date'])

# Load Policy Rates
policy = pd.read_excel("rate.xlsx")
policy.columns = policy.columns.str.strip()
policy['Date'] = pd.to_datetime(policy['Date'])

# =========================
# 2. TAG POLICY DAYS
# =========================

# Create a list/set of exact dates when policies were announced
policy_dates = set(policy['Date'])

# Create a new column tagging if a trading day was a "Policy Day"
nifty['Day_Type'] = nifty['Date'].apply(
    lambda x: "Policy Announced" if x in policy_dates else "No Policy Announced"
)

# Convert raw changes to percentages for better readability on the chart
nifty['Return (%)'] = nifty['Change %'] * 100

# =========================
# 3. CALCULATE AVERAGES
# =========================

# Group the data to see the average return on both types of days
comparison_stats = nifty.groupby('Day_Type')['Return (%)'].mean().reset_index()

print("\n--- AVERAGE DAILY RETURNS ---")
print(comparison_stats.to_string(index=False))

# =========================
# 4. GENERATE THE CHART
# =========================

# Set up the plot style
plt.figure(figsize=(9, 6))
sns.set_style("whitegrid")

# Create a bar chart
bars = sns.barplot(
    data=comparison_stats, 
    x='Day_Type', 
    y='Return (%)', 
    palette=['#808080', '#D32F2F'], # Grey for normal days, Red for policy days
    edgecolor='black'
)

# Add titles and labels
plt.title("Nifty 50 Average Daily Returns: Policy vs. Non-Policy Days", fontsize=14, fontweight='bold', pad=15)
plt.ylabel("Average Daily Return (%)", fontsize=12)
plt.xlabel("", fontsize=12)

# Draw a line exactly at 0 to separate positive/negative returns clearly
plt.axhline(0, color='black', linewidth=1.2)

# Save and show the plot
plt.savefig("policy_vs_nonpolicy_returns.png", bbox_inches='tight', dpi=300)
plt.show()

print("\n✅ Chart successfully generated and saved as 'policy_vs_nonpolicy_returns.png'")