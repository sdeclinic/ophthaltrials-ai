import streamlit as st
import requests
import pandas as pd
from openai import OpenAI

st.set_page_config(page_title="OphthalTrials AI", layout="centered")

st.title("🧿 OphthalTrials AI (GPT Powered)")
st.write("AI-assisted clinical trial matching")

# -----------------------------
# USER INPUT
# -----------------------------
condition = st.text_input("Enter condition", "myopia")
india_only = st.checkbox("🇮🇳 Show only trials in India")

st.markdown("### 🧠 Patient Details")

age = st.slider("Age", 1, 100, 30)
diagnosis = st.text_input("Diagnosis", condition)

# -----------------------------
# INIT GPT
# -----------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

# -----------------------------
# GPT MATCHING FUNCTION
# -----------------------------
def gpt_match(patient, trial_condition):

    prompt = f"""
    You are an ophthalmology clinical trials expert.

    Patient:
    Age: {patient['age']}
    Diagnosis: {patient['diagnosis']}

    Trial Condition:
    {trial_condition}

    Tasks:
    1. Give match score (0-100)
    2. Say Eligible / Maybe / Not Eligible
    3. Give short reason
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except:
        return "AI analysis unavailable"

# -----------------------------
# GET DATA
# -----------------------------
df = fetch_trials(condition)

if india_only and not df.empty:
    df = df[df["Countries"].str.contains("India", case=False, na=False)]

# -----------------------------
# DISPLAY
# -----------------------------
st.write(f"🔍 Found {len(df)} trials")

patient = {"age": age, "diagnosis": diagnosis}

if df.empty:
    st.warning("No trials found.")
else:
    for _, row in df.iterrows():

        st.markdown(f"### {row['Title']}")
        st.write(f"**Condition:** {row['Condition']}")
        st.write(f"**Status:** {row['Status']}")
        st.write(f"**Countries:** {row['Countries']}")

        with st.spinner("🧠 AI analyzing..."):
            result = gpt_match(patient, row["Condition"])

        st.info(result)

        link = f"https://clinicaltrials.gov/study/{row['NCTId']}"
        st.markdown(f"[🔗 View Trial]({link})")

        st.write("---")
