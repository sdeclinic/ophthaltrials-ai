import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="OphthalTrials AI", layout="centered")

st.title("🧿 OphthalTrials AI")
st.write("Find ophthalmology clinical trials easily")

# -----------------------------
# USER INPUT
# -----------------------------
condition = st.text_input("Enter condition", "keratoconus")

# -----------------------------
# FETCH TRIALS FUNCTION (SAFE)
# -----------------------------
@st.cache_data
def fetch_trials(condition):
    url = f"https://clinicaltrials.gov/api/query/study_fields?expr={condition}&fields=NCTId,BriefTitle,Condition,LocationCountry,OverallStatus&min_rnk=1&max_rnk=20&fmt=json"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            st.warning("⚠️ Server error. Please try again.")
            return pd.DataFrame()

        try:
            data = response.json()
        except:
            st.warning("⚠️ Error reading data. Please retry.")
            return pd.DataFrame()

        studies = data.get("StudyFieldsResponse", {}).get("StudyFields", [])

        if not studies:
            return pd.DataFrame()

        trials = []
        for s in studies:
            trials.append({
                "Title": s.get("BriefTitle", [""])[0],
                "Condition": s.get("Condition", [""])[0],
                "Country": s.get("LocationCountry", [""])[0],
                "Status": s.get("OverallStatus", [""])[0],
                "NCTId": s.get("NCTId", [""])[0]
            })

        return pd.DataFrame(trials)

    except Exception:
        st.error("⚠️ Network issue. Please try again.")
        return pd.DataFrame()


# -----------------------------
# GET DATA
# -----------------------------
df = fetch_trials(condition)

# -----------------------------
# DISPLAY RESULTS
# -----------------------------
st.write(f"🔍 Found {len(df)} trials")

if df.empty:
    st.warning("No trials found. Try another condition like glaucoma or myopia.")

else:
    for _, row in df.iterrows():
        st.markdown(f"### {row['Title']}")
        st.write(f"**Condition:** {row['Condition']}")
        st.write(f"**Location:** {row['Country']}")
        st.write(f"**Status:** {row['Status']}")

        trial_link = f"https://clinicaltrials.gov/study/{row['NCTId']}"
        st.markdown(f"[🔗 View Trial Details]({trial_link})")

        st.write("---")
