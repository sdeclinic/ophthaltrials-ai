import streamlit as st
import requests
import pandas as pd

st.title("🧿 OphthalTrials AI")

condition = st.text_input("Enter condition", "keratoconus")

@st.cache_data
@st.cache_data
@st.cache_data
def fetch_trials(condition):
    url = f"https://clinicaltrials.gov/api/query/study_fields?expr={condition}+eye&fields=NCTId,BriefTitle,Condition,LocationCountry,Phase,OverallStatus&min_rnk=1&max_rnk=20&fmt=json"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            st.warning("⚠️ Server error")
            return pd.DataFrame()

        try:
            data = response.json()
        except:
            st.warning("⚠️ Data error. Try again.")
            return pd.DataFrame()

        studies = data.get("StudyFieldsResponse", {}).get("StudyFields", [])

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

    except:
        st.error("⚠️ Network error")
        return pd.DataFrame()
