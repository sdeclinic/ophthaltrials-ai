import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="OphthalTrials AI", layout="wide")

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.title("🧿 OphthalTrials AI")

menu = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "🔍 Trial Finder", "🧠 Patient Matching", "ℹ️ About"]
)

# -----------------------------
# FETCH TRIALS FUNCTION
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

# -----------------------------
# HOME SCREEN
# -----------------------------
if menu == "🏠 Home":

    st.markdown("""
    <h1 style='text-align:center; color:#0E6BA8;'>🧿 OphthalTrials AI</h1>
    <h4 style='text-align:center;'>AI-assisted Clinical Trial Matching</h4>
    """, unsafe_allow_html=True)

    st.markdown("### 🚀 What this app does:")
    st.write("""
    - 🔍 Find ophthalmology clinical trials  
    - 🇮🇳 Filter India-based studies  
    - 🧠 Match patient profiles  
    - 📊 Assist clinical decision making  
    """)

# -----------------------------
# TRIAL FINDER
# -----------------------------
elif menu == "🔍 Trial Finder":

    st.header("🔍 Trial Finder")

    condition = st.text_input("Enter condition", "myopia")
    india_only = st.checkbox("🇮🇳 India Trials Only")

    df = fetch_trials(condition)

    if india_only and not df.empty:
        df = df[df["Countries"].str.contains("India", case=False, na=False)]

    st.write(f"📊 Found {len(df)} trials")

    if df.empty:
        st.warning("No trials found")
    else:
        for _, row in df.iterrows():
            st.markdown(f"""
            <div style="
                background:#F7FBFF;
                padding:15px;
                border-radius:10px;
                margin-bottom:10px;
            ">
            <b>{row['Title']}</b><br>
            {row['Condition']}<br>
            {row['Status']}<br>
            {row['Countries']}<br>
            <a href="https://clinicaltrials.gov/study/{row['NCTId']}" target="_blank">View Trial</a>
            </div>
            """, unsafe_allow_html=True)

# -----------------------------
# PATIENT MATCHING (DEMO)
# -----------------------------
elif menu == "🧠 Patient Matching":

    st.header("🧠 Patient Matching")

    age = st.slider("Age", 1, 100, 30)
    diagnosis = st.text_input("Diagnosis", "myopia")

    st.info("Demo AI: Matching based on diagnosis relevance")

    condition = diagnosis
    df = fetch_trials(condition)

    st.write(f"📊 Found {len(df)} trials")

    if df.empty:
        st.warning("No trials found")
    else:
        for _, row in df.iterrows():

            st.markdown(f"### {row['Title']}")

            st.write(f"Condition: {row['Condition']}")
            st.write(f"Status: {row['Status']}")

            # SIMPLE MATCH LOGIC
            if diagnosis.lower() in row["Condition"].lower():
                st.success("✅ Likely Match")
            else:
                st.warning("⚠️ Possible Match")

            link = f"https://clinicaltrials.gov/study/{row['NCTId']}"
            st.markdown(f"[View Trial]({link})")

            st.write("---")

# -----------------------------
# ABOUT PAGE
# -----------------------------
elif menu == "ℹ️ About":

    st.header("ℹ️ About")

    st.write("""
    **OphthalTrials AI** is a clinical decision support tool designed for ophthalmologists.

    Built to:
    - Improve trial discovery
    - Assist patient eligibility assessment
    - Enhance academic and clinical practice

    ⚠️ This tool is assistive and not a substitute for clinical judgment.
    """)

    st.markdown("---")
    st.write("Developed for ophthalmology practice")
