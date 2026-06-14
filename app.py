import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# -------------------------
# PAGE CONFIG
# -------------------------

st.set_page_config(
    page_title="TrustChain AI",
    page_icon="📦",
    layout="wide"
)

# -------------------------
# GEMINI SETUP
# -------------------------

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)

# -------------------------
# LOAD DATA
# -------------------------

suppliers = pd.read_csv("suppliers.csv")
products = pd.read_csv("products.csv")

# -------------------------
# RELIABILITY SCORE
# -------------------------

def calculate_score(row):

    score = (
        row["Fulfillment"] * 0.40
        + row["OnTime"] * 0.30
        + row["Rating"] * 20 * 0.20
        + row["PriceScore"] * 20 * 0.10
    )

    return round(score, 2)

suppliers["ReliabilityScore"] = suppliers.apply(
    calculate_score,
    axis=1
)

# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.title("📦 TrustChain AI")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Supplier Rankings",
        "Inventory Visibility",
        "Supplier Comparison",
        "AI Advisor",
        "Contract Center"
    ]
)

# ==================================================
# DASHBOARD
# ==================================================

if page == "Dashboard":

    st.title("📊 Supply Chain Dashboard")

    low_stock = products[
        products["CurrentStock"]
        < products["MinimumStock"]
    ]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Suppliers",
        len(suppliers)
    )

    c2.metric(
        "Low Stock Products",
        len(low_stock)
    )

    c3.metric(
        "Average Reliability",
        round(
            suppliers["ReliabilityScore"].mean(),
            1
        )
    )

    st.divider()

    st.subheader("⚠️ Low Stock Alerts")

    if len(low_stock):

        for _, row in low_stock.iterrows():

            st.error(
                f"{row['Product']} stock low ({row['CurrentStock']} left)"
            )

    st.subheader("🏆 Supplier Leaderboard")

    top = suppliers.sort_values(
        "ReliabilityScore",
        ascending=False
    )

    st.dataframe(
        top[
            [
                "Supplier",
                "Category",
                "ReliabilityScore"
            ]
        ]
    )

# ==================================================
# SUPPLIER RANKINGS
# ==================================================

elif page == "Supplier Rankings":

    st.title("🏆 Supplier Rankings")

    ranking = suppliers.sort_values(
        "ReliabilityScore",
        ascending=False
    )

    st.dataframe(ranking)

    fig = px.bar(
        ranking,
        x="Supplier",
        y="ReliabilityScore",
        title="Reliability Score Ranking"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==================================================
# INVENTORY
# ==================================================

elif page == "Inventory Visibility":

    st.title("📦 Supplier Inventory")

    st.dataframe(
        suppliers[
            [
                "Supplier",
                "Category",
                "Inventory"
            ]
        ]
    )

    fig = px.pie(
        suppliers,
        names="Supplier",
        values="Inventory",
        title="Inventory Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==================================================
# COMPARISON
# ==================================================

elif page == "Supplier Comparison":

    st.title("⚖️ Compare Suppliers")

    s1 = st.selectbox(
        "Supplier 1",
        suppliers["Supplier"]
    )

    s2 = st.selectbox(
        "Supplier 2",
        suppliers["Supplier"],
        index=1
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(s1)

        st.dataframe(
            suppliers[
                suppliers["Supplier"] == s1
            ]
        )

    with col2:

        st.subheader(s2)

        st.dataframe(
            suppliers[
                suppliers["Supplier"] == s2
            ]
        )

# ==================================================
# AI ADVISOR
# ==================================================

elif page == "AI Advisor":

    st.title("🤖 AI Procurement Advisor")

    supplier = st.selectbox(
        "Choose Supplier",
        suppliers["Supplier"]
    )

    question = st.text_area(
        "Ask AI",
        placeholder="Should I choose this supplier?"
    )

    if st.button("Generate Insight"):

        supplier_info = suppliers[
            suppliers["Supplier"] == supplier
        ]

        prompt = f"""
You are an expert supply chain consultant.

Supplier Data:

{supplier_info.to_string()}

Question:

{question}

Give:
1. Analysis
2. Risks
3. Recommendation
4. Business Impact
"""

        with st.spinner("Thinking..."):

            response = model.generate_content(
                prompt
            )

            st.success(response.text)

# ==================================================
# CONTRACT CENTER
# ==================================================

elif page == "Contract Center":

    st.title("📄 Contract Center")

    supplier = st.selectbox(
        "Select Supplier",
        suppliers["Supplier"]
    )

    score = suppliers.loc[
        suppliers["Supplier"] == supplier,
        "ReliabilityScore"
    ].values[0]

    risk = max(
        0,
        100 - int(score)
    )

    st.subheader("Risk Meter")

    st.progress(
        risk / 100
    )

    st.write(
        f"Risk Level: {risk}%"
    )

    if st.button(
        "Generate Contract"
    ):

        st.success(
            f"""
Contract Created Successfully

Supplier: {supplier}

Terms Included:

✓ Delivery SLA

✓ Inventory Visibility

✓ Penalty Clause

✓ Monthly Performance Review

✓ Renewal Terms
"""
        )