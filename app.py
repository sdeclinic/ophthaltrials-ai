import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Sai Deep OphthalTrials AI", layout="wide")

# -----------------------------
# HEADER (BRANDED)
# -----------------------------
st.markdown("""
<h1 style='text-align:center; color:#0E6BA8;'>🧿 Sai Deep Eye Clinic</h1>
<h3 style='text-align:center;'>OphthalTrials AI</h3>
<p style='text-align:center; color:grey;'>AI-assisted Clinical Trial Matching in Ophthalmology</p>
<hr>
""", unsafe_allow_html=True)

# -----------------------------
# INPUT SECTION
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    condition = st.text_input("🔍 Enter Condition", "myopia")

with col2:
    india_only = st.checkbox("🇮🇳 India Trials Only")

# -----------------------------
# PATIENT PROFILE
# -----------------------------
st.markdown("### 🧠 Patient Profile")

col3, col4 = st.columns(2)

with col3:
    age = st.slider("Age", 1, 100, 30)

with col4:
    diagnosis = st.text_input("Diagnosis", condition)

use_ai = st.checkbox("🧠 Enable AI Matching (Demo Mode)")

# -----------------------------
# FETCH TRIALS
# -----------------------------
@st.cache_data
def fetch_trials(condition):
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {"query.term": condition, "pageSize": 30}

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        studies = data.get("studies", [])

        trials = []
        for s in studies:
            protocol = s.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            status = protocol.get("statusModule", {})
            conditions = protocol.get("conditionsModule", {})
            locations_module = protocol.get("contactsLocationsModule", {})

            locations = locations_module.get("locations", [])
            countries = [loc.get("country", "") for loc in locations]

            trials.append({
                "Title": identification.get("briefTitle", "No title"),
                "Condition": ", ".join(conditions.get("conditions", [])) or "Not specified",
                "Status": status.get("overallStatus", "Not specified"),
                "Countries": ", ".join(countries) if countries else "Not specified",
                "NCTId": identification.get("nctId", "")
            })

        return pd.DataFrame(trials)

    except:
        return pd.DataFrame()

# -----------------------------
# DEMO AI MATCHING
# -----------------------------
def demo_ai_match(patient_diag, trial_condition):
    if patient_diag.lower() in trial_condition.lower():
        return "🟢 Likely Eligible – Diagnosis matches trial condition"
    else:
        return "🟡 Possible Match – Needs further evaluation"

# -----------------------------
# GET DATA
# -----------------------------
df = fetch_trials(condition)

# -----------------------------
# FILTER INDIA
# -----------------------------
if india_only and not df.empty:
    df = df[df["Countries"].str.contains("India", case=False, na=False)]

# -----------------------------
# KPI CALCULATIONS
# -----------------------------
total_trials = len(df)

recruiting_trials = 0
india_trials = 0

if not df.empty:
    recruiting_trials = df[df["Status"].str.contains("Recruiting", case=False, na=False)].shape[0]
    india_trials = df[df["Countries"].str.contains("India", case=False, na=False)].shape[0]

# -----------------------------
# KPI CARDS UI
# -----------------------------
st.markdown("## 📊 Overview")

colA, colB, colC = st.columns(3)

def card(title, value, subtitle=""):
    st.markdown(f"""
    <div style="
        background: linear-gradient(145deg, #0B1F3A, #122A4A);
        padding:25px;
        border-radius:15px;
        text-align:center;
        color:white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    ">
        <h1 style='color:#00E5C0; margin-bottom:5px;'>{value}</h1>
        <p style='color:#A0AEC0; font-size:16px;'>{title}</p>
        <p style='color:#00E5C0; font-size:14px;'>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

with colA:
    card("TRIALS FOUND", total_trials)

with colB:
    card("RECRUITING NOW", recruiting_trials)

with colC:
    card("INDIA SITES", india_trials, "Use India filter ↑")

# -----------------------------
# RESULTS
# -----------------------------
st.markdown(f"## 🔍 Results")

if df.empty:
    st.warning("No trials found. Try glaucoma, retina, or macular degeneration.")

else:
    for _, row in df.iterrows():

        st.markdown(f"""
        <div style="
            background:#F7FBFF;
            padding:20px;
            border-radius:12px;
            margin-bottom:15px;
            border:1px solid #E0E0E0;
        ">
        <h4 style='color:#0E6BA8;'>{row['Title']}</h4>

        <b>Condition:</b> {row['Condition']}<br>
        <b>Status:</b> {row['Status']}<br>
        <b>Countries:</b> {row['Countries']}<br><br>
        """, unsafe_allow_html=True)

        # AI MATCH
        if use_ai:
            result = demo_ai_match(diagnosis, row["Condition"])
            st.info(result)

        # LINK
        link = f"https://clinicaltrials.gov/study/{row['NCTId']}"
        st.markdown(f"[🔗 View Trial Details]({link})")

        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
<hr>
<p style='text-align:center; color:#0E6BA8; font-weight:bold;'>
Sai Deep Eye Clinic
</p>

<p style='text-align:center;'>
Advanced eye care with technology & compassion
</p>

<p style='text-align:center; color:grey;'>
📞 Book your consultation today
</p>
""", unsafe_allow_html=True)
