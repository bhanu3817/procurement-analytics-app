import streamlit as st
import snowflake.connector
import pandas as pd

st.set_page_config(layout="wide")

st.title("Procurement Analytics Cockpit")

# Snowflake connection
conn = snowflake.connector.connect(
    user='BHANU1420',
    password='9490376969Bhanu',
    account='PLYZUWU-SZ90944',
    warehouse='COMPUTE_WH',
    database='PROCUREMENT_DWH',
    schema='GOLD',
    role='ACCOUNTADMIN'
)

query = """
SELECT
    transaction_date,
    city,
    category,
    vendor_name,
    invoice_amount,
    discount_pct
FROM V_PROCUREMENT_ANALYTICS
"""

df = pd.read_sql(query, conn)

df["YEAR"] = pd.to_datetime(df["TRANSACTION_DATE"]).dt.year
df["MONTH"] = pd.to_datetime(df["TRANSACTION_DATE"]).dt.month

# ---------------- FILTERS ----------------
st.sidebar.header("Filters")

year = st.sidebar.selectbox("Select Year", sorted(df["YEAR"].unique()))
month = st.sidebar.selectbox("Select Month", sorted(df["MONTH"].unique()))
city = st.sidebar.multiselect("City", df["CITY"].unique(), default=df["CITY"].unique())
category = st.sidebar.multiselect("Category", df["CATEGORY"].unique(), default=df["CATEGORY"].unique())

filtered_df = df[
    (df["YEAR"] == year) &
    (df["MONTH"] == month) &
    (df["CITY"].isin(city)) &
    (df["CATEGORY"].isin(category))
]

# ---------------- KPIs ----------------
total_spend = filtered_df["INVOICE_AMOUNT"].sum()
transactions = len(filtered_df)
vendors = filtered_df["VENDOR_NAME"].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("Total Spend", f"{total_spend:,.0f}")
col2.metric("Transactions", transactions)
col3.metric("Vendors", vendors)

# ---------------- Spend Trend ----------------
trend = filtered_df.groupby("TRANSACTION_DATE")["INVOICE_AMOUNT"].sum()
st.subheader("Spend Trend")
st.line_chart(trend)

# ---------------- Category Spend ----------------
st.subheader("Spend by Category")
cat = filtered_df.groupby("CATEGORY")["INVOICE_AMOUNT"].sum().sort_values()
st.bar_chart(cat)

# ---------------- City Spend ----------------
st.subheader("Spend by City")
city_spend = filtered_df.groupby("CITY")["INVOICE_AMOUNT"].sum().sort_values()
st.bar_chart(city_spend)

# ---------------- Top Vendors ----------------
st.subheader("Top Vendors")
top_vendors = filtered_df.groupby("VENDOR_NAME")["INVOICE_AMOUNT"].sum().nlargest(10)
st.bar_chart(top_vendors)

# ---------------- Discount Efficiency ----------------
st.subheader("Vendor Discount Efficiency")
st.scatter_chart(filtered_df, x="DISCOUNT_PCT", y="INVOICE_AMOUNT")
