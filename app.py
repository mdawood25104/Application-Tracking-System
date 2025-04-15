import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import re

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Input prompt
input_prompt = """
Hey Act Like a skilled or very experienced ATS(Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst,
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide the best assistance 
for improving the resumes. Assign the percentage Matching based on the Job Description (JD) and 
the missing keywords with high accuracy.

Resume: {text}
Job Description: {jd}

I want the response in one single string having the structure:
{{"Job Description Match":"%","MissingKeywords:[]","Profile Summary":""}}
"""

# Streamlit App
st.title("Smart Applicant Tracking System")
st.text("Improve Your Resume with ATS")
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload resume in pdf format")

submit = st.button("Submit")

if submit:
       # Inside the `if submit:` block
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        formatted_input_prompt = input_prompt.format(text=text, jd=jd)
        response = get_gemini_response(formatted_input_prompt)

        try:
            # Try to clean up and extract JSON part
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                cleaned_json = match.group(0)
                response_data = json.loads(cleaned_json)
            else:
                raise ValueError("No JSON structure found in response.")

            st.markdown("### Evaluation Results")
            st.markdown(f"**💼 Job Description Match:** {response_data['Job Description Match']}")
            st.markdown(f"**📝 Missing Keywords:** {', '.join(response_data['MissingKeywords'])}")
            st.markdown(f"**🧐 Profile Summary:** {response_data['Profile Summary']}")

            if int(response_data["Job Description Match"].replace("%", "")) > 80:
                st.markdown("🎉 **Great match! You're on track!**")
            elif int(response_data["Job Description Match"].replace("%", "")) > 50:
                st.markdown("🙂 **Good match, but some improvements can be made.**")
            else:
                st.markdown("🤔 **You might want to revisit your resume to better align with the job description.**")
        except Exception as e:
            st.error(f"❌ Could not parse response properly: {e}")
            st.info("Try refining your prompt or checking if the model output is valid JSON.")
