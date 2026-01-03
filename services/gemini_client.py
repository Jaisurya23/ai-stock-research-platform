import os
import google.generativeai as genai


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")


def generate_research_report(system_prompt, financial_data, news_data, checklist_data):
    """
    Generate comprehensive AI research report using enhanced data
    """

    prompt = f"""
{system_prompt}

============================
FINANCIAL ANALYSIS DATA
============================
{financial_data}

============================
NEWS SENTIMENT & HEADLINES
============================
{news_data}

============================
CHECKLIST EVALUATION RESULTS
============================
{checklist_data}
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating AI report: {str(e)}\n\nPlease check your Gemini API configuration."