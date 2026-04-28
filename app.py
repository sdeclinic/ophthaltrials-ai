import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="OphthalTrials AI", layout="centered")

st.title("🧿 OphthalTrials AI")
st.write("Find and match ophthalmology clinical trials")

# -----------------------------
# USER INPUT
# -----------------------------
condition = st.text_input("Enter condition", "myopia")

india_only = st.checkbox("🇮🇳 Show only trials in India")

st.markdown("### 🧠 Patient Details (for AI Matching)")

age = st.slider("Age", 1, 100, 30)
diagnosis = st.text_input("Diagnosis", condition)

# -----------------------------
# FETCH TRIALS
# -----------------------------
@st.cache_data
def fetch_trials(condition):
    url = "https://clinicaltrials.gov/api/v2/studies"

    params = {
        "query.term": condition,
        "pageSize": 50
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            st.warning("⚠️ Server error. Try again.")
            return pd.DataFrame()

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

            countries = []
            for loc in locations:
                if loc.get("country"):
                    countries.append(loc.get("country"))

            trials.append({
                "Title": identification.get("briefTitle", ""),
                "Condition": ", ".join(conditions.get("conditions", [])),
                "Status": status.get("overallStatus", ""),
                "Countries": ", ".join(countries),
                "NCTId": identification.get("nctId", "")
            })

        return pd.DataFrame(trials)

    except:
        st.error("⚠️ Network issue")
        return pd.DataFrame()


# -----------------------------
# AI MATCHING LOGIC
# -----------------------------
def match_score(trial_condition, patient_diag, age):
    score = 40
    reason = []

    if patient_diag.lower() in trial_condition.lower():
        score += 40
        reason.append("Diagnosis matches trial condition")

    if age < 40:
        score += 10
        reason.append("Age suitable for most trials")

    if "myopia" in trial_condition.lower():
        score += 5
        reason.append("Refractive condition relevance")

    return min(score, 100), ", ".join(reason)


# -----------------------------
# GET DATA
# -----------------------------
df = fetch_trials(condition)

# -----------------------------
# INDIA FILTER
# -----------------------------
if india_only and not df.empty:
    df = df[df["Countries"].str.contains("India", case=False, na=False)]

# -----------------------------
# DISPLAY
# -----------------------------
st.write(f"🔍 Found {len(df)} trials")

if df.empty:
    st.warning("No trials found. Try glaucoma, retina, etc.")

else:
    for _, row in df.iterrows():
        score, reason = match_score(row["Condition"], diagnosis, age)

        st.markdown(f"### {row['Title']}")

        st.write(f"**Condition:** {row['Condition']}")
        st.write(f"**Status:** {row['Status']}")
        st.write(f"**Countries:** {row['Countries']}")

        # MATCH SCORE BAR
        st.progress(score / 100)
        st.write(f"🧠 Match Score: **{score}%**")

        st.info(f"Why matched: {reason}")

        link = f"https://clinicaltrials.gov/study/{row['NCTId']}"
        st.markdown(f"[🔗 View Trial Details]({link})")

        st.write("---")
