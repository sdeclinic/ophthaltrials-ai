import streamlit as st
import requests
import pandas as pd
from openai import OpenAI

st.set_page_config(page_title="OphthalTrials AI", layout="centered")

st.title("🧿 OphthalTrials AI")
st.write("Clinical trial finder with optional AI matching")

# -----------------------------
# INPUT BOX (THIS IS YOUR INPUT)
# -----------------------------
condition = st.text_input("Enter condition", "myopia")

# AI Toggle
use_ai = st.checkbox("🧠 Enable AI Matching")

# Patient Inputs
st.markdown("### 🧠 Patient Details")
age = st.slider("Age", 1, 100, 30)
diagnosis = st.text_input("Diagnosis", condition)

patient = {"age": age, "diagnosis": diagnosis}

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

            trials.append({
                "Title": identification.get("briefTitle", ""),
                "Condition": ", ".join(conditions.get("conditions", [])),
                "Status": status.get("overallStatus", ""),
                "NCTId": identification.get("nctId", "")
            })

        return pd.DataFrame(trials)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        return pd.DataFrame()

# -----------------------------
# GPT FUNCTION (SAFE)
# -----------------------------
def gpt_match(patient, trial_condition):
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        prompt = f"""
You are an ophthalmology expert.

Patient:
Age: {patient['age']}
Diagnosis: {patient['diagnosis']}

Trial Condition:
{trial_condition}

Give:
1. Match score (0-100)
2. Eligible / Maybe / Not Eligible
3. Short reason
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ AI error: {str(e)}"

# -----------------------------
# GET DATA
# -----------------------------
df = fetch_trials(condition)

st.write(f"🔍 Found {len(df)} trials")

# -----------------------------
# DISPLAY RESULTS
# -----------------------------
if df.empty:
    st.warning("No trials found")
else:
    for _, row in df.iterrows():
        st.markdown(f"### {row['Title']}")
        st.write(f"Condition: {row['Condition']}")
        st.write(f"Status: {row['Status']}")

        if use_ai:
            with st.spinner("🧠 AI analyzing..."):
                result = gpt_match(patient, row["Condition"])
            st.info(result)

        link = f"https://clinicaltrials.gov/study/{row['NCTId']}"
        st.markdown(f"[View Trial]({link})")

        st.write("---")
