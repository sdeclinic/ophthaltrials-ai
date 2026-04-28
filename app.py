import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="OphthalTrials AI", layout="wide")

# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<h1 style='text-align: center; color: #0E6BA8;'>🧿 OphthalTrials AI</h1>
<h4 style='text-align: center;'>AI-assisted Clinical Trial Matching in Ophthalmology</h4>
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
# PATIENT DETAILS
# -----------------------------
st.markdown("### 🧠 Patient Profile")

col3, col4 = st.columns(2)

with col3:
    age = st.slider("Age", 1, 100, 30)

with col4:
    diagnosis = st.text_input("Diagnosis", condition)

# -----------------------------
# FETCH TRIALS
# -----------------------------
@st.cache_data
def fetch_trials(condition):
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {"query.term": condition, "pageSize": 20}

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
                "Title": identification.get("briefTitle", ""),
                "Condition": ", ".join(conditions.get("conditions", [])),
                "Status": status.get("overallStatus", ""),
                "Countries": ", ".join(countries),
                "NCTId": identification.get("nctId", "")
            })

        return pd.DataFrame(trials)

    except:
        return pd.DataFrame()

df = fetch_trials(condition)

# -----------------------------
# FILTER INDIA
# -----------------------------
if india_only and not df.empty:
    df = df[df["Countries"].str.contains("India", case=False, na=False)]

# -----------------------------
# RESULTS HEADER
# -----------------------------
st.markdown(f"## 📊 Found {len(df)} Trials")

# -----------------------------
# DISPLAY CARDS
# -----------------------------
if df.empty:
    st.warning("No trials found. Try glaucoma, retina, etc.")

else:
    for _, row in df.iterrows():

        st.markdown(f"""
        <div style="
            background-color:#F7FBFF;
            padding:20px;
            border-radius:12px;
            margin-bottom:15px;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        ">
        <h4 style='color:#0E6BA8;'>{row['Title']}</h4>

        <b>Condition:</b> {row['Condition']}<br>
        <b>Status:</b> {row['Status']}<br>
        <b>Countries:</b> {row['Countries']}<br><br>

        <a href="https://clinicaltrials.gov/study/{row['NCTId']}" target="_blank">
        🔗 View Trial Details
        </a>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
<hr>
<p style='text-align:center; color: grey;'>
Powered by ClinicalTrials.gov | Designed for Ophthalmology Practice
</p>
""", unsafe_allow_html=True)
