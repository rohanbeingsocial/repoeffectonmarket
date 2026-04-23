import pandas as pd
import matplotlib.pyplot as plt

# =========================
# 1. LOAD & CLEAN DATA
# =========================

# Load Nifty changes
nifty = pd.read_excel("change.xlsx")
nifty.columns = nifty.columns.str.strip()
nifty['Date'] = pd.to_datetime(nifty['Date'])
nifty = nifty.sort_values('Date')

# Load Policy Rates
policy = pd.read_excel("rate.xlsx")
policy.columns = policy.columns.str.strip()
policy['Date'] = pd.to_datetime(policy['Date'])
policy = policy.sort_values('Date')

# Load CPI Data (header=2 skips the title rows)
cpi = pd.read_excel("cpi.xlsx", header=2)

# Keep only the essential columns and rename them to match
cpi = cpi[['Month', 'Combined']].copy()
cpi.rename(columns={'Month': 'Date', 'Combined': 'CPI'}, inplace=True)
cpi['Date'] = pd.to_datetime(cpi['Date'])
cpi = cpi.sort_values('Date')

# =========================
# 2. CPI CHANGE & EXPECTATIONS
# =========================

# Calculate difference from previous month
cpi['CPI_Change'] = cpi['CPI'].diff()

# Determine if the market "Expected" a hike or a cut
def get_expected(change):
    return "Hike" if change > 0 else "Cut"

cpi['Expected'] = cpi['CPI_Change'].apply(get_expected)

# =========================
# 3. MERGE DATASETS
# =========================

# Link policy dates to the most recently available CPI data at that time
df = pd.merge_asof(policy, cpi, on='Date', direction='backward')

# =========================
# 4. CALCULATE RETURNS 
# =========================

def get_return(target_date, start_offset, end_offset):
    subset = nifty[
        (nifty['Date'] >= target_date + pd.Timedelta(days=start_offset)) &
        (nifty['Date'] <= target_date + pd.Timedelta(days=end_offset))
    ]
    return subset['Change %'].sum() if not subset.empty else 0

# Apply the return windows
df['Pre_Return'] = df['Date'].apply(lambda x: get_return(x, -5, -1))
df['Day_Before_Return'] = df['Date'].apply(lambda x: get_return(x, -1, -1))
df['Same_Day_Return'] = df['Date'].apply(lambda x: get_return(x, 0, 0))
df['Post_Return'] = df['Date'].apply(lambda x: get_return(x, 1, 5))
df['Month_Advance_Return'] = df['Date'].apply(lambda x: get_return(x, 1, 20))

# =========================
# 5. CLASSIFICATION & SURPRISE
# =========================

df['Type'] = df['Change'].apply(lambda x: "Hike" if x > 0 else "Cut")
df['Surprise'] = df.apply(lambda x: "Yes" if x['Expected'] != x['Type'] else "No", axis=1)

# =========================
# 6. FINAL FORMATTING & EXPORT
# =========================

# Map variables to match your final desired layout
df['Average_pre'] = df['Pre_Return']
df['Average post'] = df['Post_Return']
df['Average day before'] = df['Day_Before_Return']
df['Average same day'] = df['Same_Day_Return']
df['Average Month'] = df['Month_Advance_Return']

# Rename standard date column
df.rename(columns={'Date': 'Policy Date'}, inplace=True)

# Order the columns exactly as they appear in your corrected table
final_columns = [
    'Policy Date', 'Repo', 'Change', 'Type', 'CPI', 'CPI_Change', 
    'Pre_Return', 'Post_Return', 'Day_Before_Return', 'Same_Day_Return', 
    'Month_Advance_Return', 'Expected', 'Surprise', 
    'Average_pre', 'Average post', 'Average day before', 'Average same day', 'Average Month'
]

event_table = df[final_columns].copy()

# Save to Excel
output_filename = "event_table_generated.xlsx"
event_table.to_excel(output_filename, index=False)
print(f"✅ Successfully created {output_filename}")


# =========================
# 7. COMPARATIVE ANALYSIS & PLOTS
# =========================

print("\n--- STATISTICAL ANALYSIS ---")

print("\n1. Average Returns Accross All Events:")
print(event_table[['Pre_Return', 'Same_Day_Return', 'Post_Return', 'Month_Advance_Return']].mean())

print("\n2. Same Day Return: Expected vs Surprise:")
print(event_table.groupby('Surprise')['Same_Day_Return'].mean())

print("\n3. Same Day Return: Rate Hike vs Rate Cut:")
print(event_table.groupby('Type')['Same_Day_Return'].mean())

# Plot 1: Expected vs Surprise
plt.figure(figsize=(8, 5))
event_table.groupby('Surprise')['Same_Day_Return'].mean().plot(kind='bar', color=['#4C72B0', '#C44E52'])
plt.title("Market Reaction: Expected vs Surprise Moves")
plt.ylabel("Average Same Day Return")
plt.xlabel("Was the move a surprise?")
plt.axhline(0, color='black', linewidth=0.8)
plt.savefig("plot_surprise_vs_expected.png", bbox_inches='tight')
plt.show()

# Plot 2: Hike vs Cut
plt.figure(figsize=(8, 5))
event_table.groupby('Type')['Same_Day_Return'].mean().plot(kind='bar', color=['#55A868', '#DD8452'])
plt.title("Market Reaction: Rate Hikes vs Rate Cuts")
plt.ylabel("Average Same Day Return")
plt.xlabel("Policy Action Type")
plt.axhline(0, color='black', linewidth=0.8)
plt.savefig("plot_hike_vs_cut.png", bbox_inches='tight')
plt.show()

# Plot 3: Lag Effect (Timeline of returns)
plt.figure(figsize=(8, 5))
timeline = event_table[['Pre_Return', 'Same_Day_Return', 'Post_Return', 'Month_Advance_Return']].mean()
timeline.plot(kind='line', marker='o', color='#8172B3', linewidth=2, markersize=8)
plt.title("Lag Effect: Timeline of Average Nifty Returns")
plt.ylabel("Average Return (%)")
plt.xlabel("Timeframe around Policy Announcement")
plt.xticks(ticks=range(len(timeline)), labels=['Pre-Event', 'Same Day', 'Post-Event', 'Month Advance'], rotation=15)
plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
plt.grid(alpha=0.3)
plt.savefig("plot_lag_effect.png", bbox_inches='tight')
plt.show()

print("\n✅ Comparative analysis complete. Charts have been displayed and saved to your folder.")