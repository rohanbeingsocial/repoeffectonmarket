import pandas as pd

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

df = df[final_columns]

# Save to Excel
output_filename = "event_table_generated.xlsx"
df.to_excel(output_filename, index=False)

print(f"✅ Successfully created {output_filename}")
