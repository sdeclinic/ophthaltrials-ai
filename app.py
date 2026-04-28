import streamlit as st
import requests
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def gpt_match(patient, trial_condition):
    prompt = f"""
You are an ophthalmology clinical trials expert.

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

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI error: {str(e)}"
