import streamlit as st
import requests
import pandas as pd

st.title("🧿 OphthalTrials AI")

condition = st.text_input("Enter condition", "keratoconus")

@st.cache_data
@st.cache_data
def fetch_trials(condition):
    url = f"https://clinicaltrials.gov/api/query/study_fields?expr={condition}+eye&fields=NCTId,BriefTitle,Condition,LocationCountry,Phase,OverallStatus&min_rnk=1&max_rnk=20&fmt=json"
    
    try:
        response = requests.get(url, timeout=10)

        # Check if response is OK
        if response.status_code != 200:
            st.error("⚠️ Error fetching data from server")
            return pd.DataFrame()

        # Try parsing JSON
        try:
            data = response.json()
        except:
            st.error("⚠️ Received invalid data. Please try again.")
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

    except Exception as e:
        st.error("⚠️ Something went wrong. Please retry.")
        return pd.DataFrame()    trials = []
    for s in studies:
        trials.append({
            "Title": s["BriefTitle"][0] if s["BriefTitle"] else "",
            "Condition": s["Condition"][0] if s["Condition"] else "",
            "Country": s["LocationCountry"][0] if s["LocationCountry"] else "",
            "Status": s["OverallStatus"][0] if s["OverallStatus"] else "",
            "NCTId": s["NCTId"][0]
        })

    return pd.DataFrame(trials)

df = fetch_trials(condition)

if df.empty:
    st.warning("No trials found or API error. Try again.")
else:
    for _, row in df.iterrows():
