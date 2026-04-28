import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="OphthalTrials AI", layout="centered")

st.title("🧿 OphthalTrials AI")
st.write("Find ophthalmology clinical trials easily")

condition = st.text_input("Enter condition", "myopia")

# -----------------------------
# FETCH TRIALS (NEW API v2)
# -----------------------------
@st.cache_data
def fetch_trials(condition):
    url = "https://clinicaltrials.gov/api/v2/studies"

    params = {
        "query.term": condition,
        "pageSize": 20
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            st.warning("⚠️ Server not responding. Try again.")
            return pd.DataFrame()

        data = response.json()

        studies = data.get("studies", [])

        trials = []
        for s in studies:
            protocol = s.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            status = protocol.get("statusModule", {})
            conditions = protocol.get("conditionsModule", {})
            locations = protocol.get("contactsLocationsModule", {})

            trials.append({
                "Title": identification.get("briefTitle", ""),
                "Condition": ", ".join(conditions.get("conditions", [])),
                "Status": status.get("overallStatus", ""),
                "Location": str(locations.get("locations", []))[:80],
                "NCTId": identification.get("nctId", "")
            })

        return pd.DataFrame(trials)

    except Exception:
        st.error("⚠️ Network issue. Please retry.")
        return pd.DataFrame()


# -----------------------------
# GET DATA
# -----------------------------
df = fetch_trials(condition)

# -----------------------------
# DISPLAY
# -----------------------------
st.write(f"🔍 Found {len(df)} trials")

if df.empty:
    st.warning("No trials found. Try: glaucoma, retina, macular degeneration.")
else:
    for _, row in df.iterrows():
        st.markdown(f"### {row['Title']}")
        st.write(f"**Condition:** {row['Condition']}")
        st.write(f"**Status:** {row['Status']}")
        st.write(f"**Location:** {row['Location']}")

        link = f"https://clinicaltrials.gov/study/{row['NCTId']}"
        st.markdown(f"[🔗 View Trial Details]({link})")

        st.write("---")
