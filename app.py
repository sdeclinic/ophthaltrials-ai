import streamlit as st
import requests
import pandas as pd

st.title("🧿 OphthalTrials AI")

condition = st.text_input("Enter condition", "keratoconus")

@st.cache_data
def fetch_trials(condition):
    url = f"https://clinicaltrials.gov/api/query/study_fields?expr={condition}+eye&fields=NCTId,BriefTitle,Condition,LocationCountry,Phase,OverallStatus&min_rnk=1&max_rnk=20&fmt=json"
    response = requests.get(url)
    data = response.json()

    studies = data["StudyFieldsResponse"]["StudyFields"]

    trials = []
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

for _, row in df.iterrows():
    st.write("###", row["Title"])
    st.write("Condition:", row["Condition"])
    st.write("Location:", row["Country"])
    st.write("Status:", row["Status"])
    st.markdown(f"[View Trial](https://clinicaltrials.gov/study/{row['NCTId']})")
    st.write("---")
