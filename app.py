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

     [data-testid="stSidebar"]{
background:#111827;
}

.block-container{
padding-top:1rem;
}

h1,h2,h3{
font-weight:700;
}

.stButton button{
width:100%;
border-radius:12px;
height:3em;
font-weight:bold;
}

</style>
""",unsafe_allow_html=True)
    



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

    col1,col2,col3=st.columns(3)

    with col1:
        st.markdown(f"""
                    <div style="
                    background:#1E293B;
                    padding:20px;
                    border-radius:15px;
                     text-align:center;">
    <h3>🏢 Suppliers</h3>
    <h1>{len(suppliers)}</h1>
    </div>
    """,unsafe_allow_html=True)
    

    with col2:
         st.markdown(f"""
    <div style="
    background:#7F1D1D;
    padding:20px;
    border-radius:15px;
    text-align:center;">
    <h3>⚠ Low Stock</h3>
    <h1>{len(low_stock)}</h1>
    </div>
    """,unsafe_allow_html=True)

    with col3:
         st.markdown(f"""
    <div style="
    background:#14532D;
    padding:20px;
    border-radius:15px;
    text-align:center;">
    <h3>⭐ Reliability</h3>
    <h1>{round(suppliers['ReliabilityScore'].mean(),1)}</h1>
    </div>
    """,unsafe_allow_html=True)

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