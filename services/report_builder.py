from analysis.checklist_engine import evaluate_checklist

def build_final_report(company, ai_text, financial_data, news_data):
    """
    Combines AI output with structured metadata
    and formats it into a clean research report.
    """

    # ---- Financial Highlights ----
    financial_section = f"""
============================
COMPANY SNAPSHOT
============================
Company        : {financial_data.get('company_name')}
Sector         : {financial_data.get('sector')}
Industry       : {financial_data.get('industry')}
Market Cap     : {financial_data.get('market_cap')}
Revenue        : {financial_data.get('revenue')}
Net Income     : {financial_data.get('net_income')}
Debt           : {financial_data.get('debt')}
ROE            : {financial_data.get('roe')}
ROCE           : {financial_data.get('roce')}
Current Price  : {financial_data.get('current_price')}
Currency       : {financial_data.get('currency')}
"""

    # ---- News Summary ----
    news_section = "\n============================\nRECENT NEWS HEADLINES\n============================\n"
    if news_data and "error" not in news_data[0]:
        for i, news in enumerate(news_data, 1):
            news_section += f"{i}. {news['title']} ({news['source']}, {news['time']})\n"
    else:
        news_section += "News data unavailable.\n"

    # ---- AI Analysis ----
    ai_section = f"""
============================
AI RESEARCH ANALYSIS
============================
{ai_text}
"""

    # ---- Checklist Evaluation ----
    checklist, score, verdict = evaluate_checklist(financial_data)

    checklist_section = "\n============================\nCHECKLIST EVALUATION\n============================\n"
    for key, value in checklist.items():
        status = "✔️" if value else "❌"
        checklist_section += f"{status} {key}\n"

    checklist_section += f"\nChecklist Score: {score}/10\n"
    checklist_section += f"Checklist Verdict: {verdict}\n"

    # ---- Final Report ----
    final_report = (
    f"{financial_section}\n"
    f"{news_section}\n"
    f"{checklist_section}\n"
    f"{ai_section}\n"
)


    return final_report
