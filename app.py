import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="OphthalTrials AI", layout="centered")

st.title("🧿 OphthalTrials AI")
st.write("Find ophthalmology clinical trials easily")

# -----------------------------
# INPUTS
# -----------------------------
condition = st.text_input("Enter condition", "myopia")

india_only = st.checkbox("🇮🇳 Show only trials in India")

# -----------------------------
# FETCH TRIALS (NEW API v2)
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
            locations_module = protocol.get("contactsLocationsModule", {})

            locations = locations_module.get("locations", [])

            # Extract country names
            countries = []
            for loc in locations:
                country = loc.get("country", "")
                if country:
                    countries.append(country)

            trials.append({
                "Title": identification.get("briefTitle", ""),
                "Condition": ", ".join(conditions.get("conditions", [])),
                "Status": status.get("overallStatus", ""),
                "Countries": ", ".join(countries),
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
# INDIA FILTER
# -----------------------------
if india_only and not df.empty:
    df = df[df["Countries"].str.contains("India", case=False, na=False)]

# -----------------------------
# DISPLAY
# -----------------------------
st.write(f"🔍 Found {len(df)} trials")

if df.empty:
    st.warning("No trials found. Try other keywords like glaucoma or retina.")
else:
    for _, row in df.iterrows():
        st.markdown(f"### {row['Title']}")
        st.write(f"**Condition:** {row['Condition']}")
        st.write(f"**Status:** {row['Status']}")
        st.write(f"**Countries:** {row['Countries']}")

        link = f"https://clinicaltrials.gov/study/{row['NCTId']}"
        st.markdown(f"[🔗 View Trial Details]({link})")

        st.write("---")
