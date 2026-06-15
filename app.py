import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI



# -------------------------
# PAGE CONFIG
# -------------------------


st.set_page_config(
    page_title="TrustChain AI",
    page_icon="📦",
    layout="wide"
)
st.markdown("""
<style>

.stApp{
    background:#F5F7FB;
}

[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#071B4A,#0D2D73);
}

[data-testid="stSidebar"] *{
    color:white;
}

.metric-card{
    background:white;
    padding:20px;
    border-radius:18px;
    box-shadow:0 4px 20px rgba(0,0,0,0.08);
    text-align:center;
}

.dashboard-card{
    background:white;
    padding:20px;
    border-radius:18px;
    box-shadow:0 4px 20px rgba(0,0,0,0.08);
}

.small-badge{
    background:#E8F5E9;
    color:#2E7D32;
    padding:6px 12px;
    border-radius:20px;
    display:inline-block;
    font-size:12px;
}

</style>
""", unsafe_allow_html=True)


# -------------------------
# GEMINI SETUP
# -------------------------

client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"

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

    st.markdown("""
               
<h1>Welcome back, Viha 👋</h1>
<p style='color:gray'>
Here's what's happening with your procurement today.
</p>

<div style="
padding:25px;
border-radius:20px;
background:linear-gradient(135deg,#1e3c72,#2a5298);
color:white;
margin-bottom:20px;
">
<h1>📦 TrustChain AI</h1>
<p>Smart Procurement Intelligence for Small Businesses</p>
</div>
""", unsafe_allow_html=True)

    low_stock = products[
        products["CurrentStock"]
        < products["MinimumStock"]
    ]

    col1,col2,col3,col4 = st.columns(4)

    with col1:
          st.markdown(f"""
    <div class='metric-card'>
    <h4>🏢 Suppliers</h4>
    <h1>{len(suppliers)}</h1>
    </div>
    """, unsafe_allow_html=True)

    with col2:
               st.markdown(f"""
    <div class='metric-card'>
    <h4>⚠️ Low Stock</h4>
    <h1>{len(low_stock)}</h1>
    </div>
    """, unsafe_allow_html=True)

    with col3:
              st.markdown(f"""
    <div class='metric-card'>
    <h4>🛡 Reliability</h4>
    <h1>{round(suppliers['ReliabilityScore'].mean(),1)}%</h1>
    </div>
    """, unsafe_allow_html=True)

    with col4:
              st.markdown("""
    <div class='metric-card'>
    <h4>💰 Savings</h4>
    <h1>₹12,450</h1>
    </div>
    """, unsafe_allow_html=True)
    left,right = st.columns([2,1])

    with right:

            st.markdown("""
    <div class='dashboard-card'>
    <h3>✨ AI Insights</h3>

    • Reorder Milk within 2 days<br><br>

    • Bread supplier cost 8% higher<br><br>

    • Biscuit demand rising next week<br><br>

    • Reliability score improving
    </div>
    """, unsafe_allow_html=True)
    with left:

             st.markdown("""
    <div class='dashboard-card'>
    <h3>Inventory Risk Overview</h3>
    </div>
    """, unsafe_allow_html=True)

    for _, row in low_stock.iterrows():

        percent = min(
            100,
            row["CurrentStock"] /
            row["MinimumStock"] * 100
        )

        st.write(row["Product"])
        st.progress(percent/100)        
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

            response = client.chat.completions.create(
                 model="llama-3.3-70b-versatile",
                 messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
            )
            answer = response.choices[0].message.content
            st.success(answer)

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

    fig = px.pie(
    names=["Risk","Safe"],
    values=[risk,100-risk],
    hole=0.75
)

    st.plotly_chart(
    fig,
    use_container_width=True
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