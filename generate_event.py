import pandas as pd

# =========================
# 1. LOAD & CLEAN DATA
# =========================

# Load Nifty changes
# Replace with your actual file name (e.g., 'change.xlsx' or 'change.csv')
nifty = pd.read_csv("change.xlsx - Sheet1.csv")
nifty.columns = nifty.columns.str.strip()
nifty['Date'] = pd.to_datetime(nifty['Date'])
nifty = nifty.sort_values('Date')

# Load Policy Rates
# Replace with your actual file name (e.g., 'rate.xlsx' or 'rate.csv')
policy = pd.read_csv("rate.xlsx - Sheet1.csv")
policy.columns = policy.columns.str.strip()
policy['Date'] = pd.to_datetime(policy['Date'])
policy = policy.sort_values('Date')

# Load CPI Data
# header=2 skips the first two empty/title rows so we can grab the real column names
# Replace with your actual file name (e.g., 'cpi.xlsx' or 'cpi.csv')
cpi = pd.read_csv("cpi.xlsx - Sheet2.csv", header=2)

# Keep only the essential columns: 'Month' (Date) and 'Combined' (Overall CPI)
cpi = cpi[['Month', 'Combined']].copy()
cpi.rename(columns={'Month': 'Date', 'Combined': 'CPI'}, inplace=True)
cpi['Date'] = pd.to_datetime(cpi['Date'])
cpi = cpi.sort_values('Date')

# =========================
# 2. CPI CHANGE & EXPECTATIONS
# =========================

# Calculate difference from previous month
cpi['CPI_Change'] = cpi['CPI'].diff()

# Determine if the market "Expected" a hike or a cut based on inflation trend
def get_expected(change):
    return "Hike" if change > 0 else "Cut"

cpi['Expected'] = cpi['CPI_Change'].apply(get_expected)

# =========================
# 3. MERGE DATASETS
# =========================

# Merge policy dates with the most recently available CPI data at that time
df = pd.merge_asof(policy, cpi, on='Date', direction='backward')

# =========================
# 4. CALCULATE RETURNS 
# =========================

def get_return(target_date, start_offset, end_offset):
    """
    Sums the 'Change %' within a specific window of days around the target date.
    """
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

# Ensure actual 'Type' classification is standardized
df['Type'] = df['Change'].apply(lambda x: "Hike" if x > 0 else "Cut")

# Determine if the Central Bank's move surprised the market
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

# Rename standard date column to "Policy Date"
df.rename(columns={'Date': 'Policy Date'}, inplace=True)

# Select and order the columns exactly as they appear in your 'corrected_event_table.csv'
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
print(df.head())