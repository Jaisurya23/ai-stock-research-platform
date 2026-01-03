from flask import Flask, render_template, request, jsonify
from config import Config
import sqlite3
from datetime import datetime
import json
import os

# Enhanced Services
from services.yfinance_service import fetch_enhanced_financial_data
from services.news_scraper import fetch_advanced_news
from services.gemini_client import generate_research_report
from analysis.checklist_engine import perform_intelligent_evaluation

app = Flask(__name__)
app.config.from_object(Config)


# ---------------------------
# DATABASE CONNECTION
# ---------------------------
def get_db_connection():
    conn = sqlite3.connect(app.config["DATABASE_PATH"])
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------
# LOAD SYSTEM PROMPT
# ---------------------------
def load_system_prompt():
    try:
        with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """You are an AI-powered stock research assistant. Provide comprehensive analysis based on provided data.
Focus on: Business overview, Financial health, Growth prospects, Valuation, News impact, Risks, and Scenarios.
Always end with: "This analysis is for educational and research purposes only and does not constitute investment advice." """


# ---------------------------
# HOME PAGE
# ---------------------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------------------
# ENHANCED RESEARCH REQUEST
# ---------------------------
@app.route("/research", methods=["POST"])
def research():
    company = request.form.get("company")

    if not company:
        return "Company name is required", 400

    try:
        print(f"\n{'='*60}")
        print(f"🔍 Starting research for: {company}")
        print(f"{'='*60}\n")
        
        # 1. Fetch Enhanced Financial Data
        print(f"📊 Step 1/4: Fetching enhanced financial data...")
        enhanced_financial = fetch_enhanced_financial_data(company)
        
        if not enhanced_financial["success"]:
            error_msg = enhanced_financial.get('error', 'Unknown error')
            print(f"❌ Error fetching financial data: {error_msg}")
            return render_template(
                "error.html",
                error_message=f"Unable to fetch financial data for '{company}'. Please check the ticker symbol and try again.",
                suggestion="Try using the exact ticker symbol (e.g., 'HDFCBANK.NS' for NSE, 'AAPL' for US stocks)"
            ), 500
        
        resolved_ticker = enhanced_financial.get('resolved_ticker', company)
        print(f"   ✅ Data fetched successfully for {resolved_ticker}")
        print(f"   📈 Company: {enhanced_financial['data']['basic_info']['company_name']}")
        print(f"   💰 Market Cap: {enhanced_financial['data']['basic_info']['market_cap']}")

        # 2. Fetch and Analyze News
        print(f"\n📰 Step 2/4: Fetching and analyzing news...")
        news_analysis = fetch_advanced_news(
            company_name=enhanced_financial['data']['basic_info']['company_name'],
            ticker=resolved_ticker,
            max_items=15
        )
        
        if news_analysis["success"]:
            print(f"   ✅ Found {news_analysis['summary']['total_articles']} articles")
            print(f"   📊 Sentiment: {news_analysis['summary']['overall_sentiment']} {news_analysis['summary']['overall_emoji']}")
            print(f"   🔥 Critical news: {news_analysis['summary']['critical_news_count']}")
        else:
            print(f"   ⚠️ News fetch had issues, continuing with limited data")

        # 3. Perform Intelligent Checklist Evaluation
        print(f"\n✅ Step 3/4: Running intelligent checklist evaluation...")
        checklist_results = perform_intelligent_evaluation(enhanced_financial, news_analysis)
        print(f"   ✅ Overall Score: {checklist_results['total_score']}/100")
        print(f"   📋 Verdict: {checklist_results['verdict']['rating']}")

        # 4. Prepare data for AI
        financial_summary = format_financial_for_ai(enhanced_financial)
        news_summary = format_news_for_ai(news_analysis)
        checklist_summary = format_checklist_for_ai(checklist_results)

        # 5. Load AI system prompt
        system_prompt = load_system_prompt()

        # 6. Generate AI Analysis
        print(f"\n🤖 Step 4/4: Generating AI research report...")
        ai_report = generate_research_report(
            system_prompt=system_prompt,
            financial_data=financial_summary,
            news_data=news_summary,
            checklist_data=checklist_summary
        )
        print(f"   ✅ AI report generated successfully")

        # 7. Build comprehensive final report
        final_report = build_comprehensive_report(
            company=enhanced_financial['data']['basic_info']['company_name'],
            ticker=resolved_ticker,
            enhanced_financial=enhanced_financial,
            news_analysis=news_analysis,
            checklist_results=checklist_results,
            ai_report=ai_report
        )

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 8. Save to database
        print(f"\n💾 Saving report to database...")
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO research_history (company, report, created_at) VALUES (?, ?, ?)",
            (enhanced_financial['data']['basic_info']['company_name'], final_report, created_at)
        )
        conn.commit()
        conn.close()

        print(f"✅ Report generated and saved successfully!")
        print(f"{'='*60}\n")

        # 9. Render report
        return render_template(
            "report.html",
            company=enhanced_financial['data']['basic_info']['company_name'],
            ticker=resolved_ticker,
            report=final_report,
            created_at=created_at,
            financial_data=enhanced_financial,
            news_data=news_analysis,
            checklist_data=checklist_results
        )

    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template(
            "error.html",
            error_message="An unexpected error occurred while generating the report.",
            suggestion="Please try again or contact support if the issue persists.",
            technical_details=str(e)
        ), 500


# ---------------------------
# FORMATTING FUNCTIONS
# ---------------------------
def format_financial_for_ai(enhanced_data):
    """Format enhanced financial data for AI consumption"""
    data = enhanced_data["data"]
    quality = enhanced_data["quality_score"]
    
    return f"""
COMPANY INFORMATION:
Name: {data['basic_info']['company_name']}
Ticker: {data['basic_info']['ticker']}
Sector: {data['basic_info']['sector']}
Industry: {data['basic_info']['industry']}
Market Cap: {data['basic_info']['market_cap']}
Employees: {data['basic_info']['employees']}
Country: {data['basic_info']['country']}

VALUATION METRICS:
P/E Ratio: {data['valuation_metrics']['pe_ratio']}
Forward P/E: {data['valuation_metrics']['forward_pe']}
PEG Ratio: {data['valuation_metrics']['peg_ratio']}
Price to Book: {data['valuation_metrics']['price_to_book']}
Price to Sales: {data['valuation_metrics']['price_to_sales']}
EV/EBITDA: {data['valuation_metrics']['ev_to_ebitda']}
Analyst Target Price: {data['peer_comparison']['target_price']}

GROWTH METRICS:
Revenue 3Y CAGR: {data['growth_metrics']['revenue_3y_cagr']}%
Earnings 3Y CAGR: {data['growth_metrics']['earnings_3y_cagr']}%
Revenue Trend: {data['growth_metrics']['revenue_trend']}
QoQ Revenue Growth: {data['growth_metrics']['revenue_growth_qoq']}%

PROFITABILITY:
ROE: {data['profitability_metrics']['roe']}%
ROA: {data['profitability_metrics']['roa']}%
ROIC: {data['profitability_metrics']['roic']}%
Profit Margin: {data['profitability_metrics']['profit_margin']}%
Operating Margin: {data['profitability_metrics']['operating_margin']}%
Gross Margin: {data['profitability_metrics']['gross_margin']}%

FINANCIAL HEALTH:
Current Ratio: {data['financial_health']['current_ratio']}
Quick Ratio: {data['financial_health']['quick_ratio']}
Debt to Equity: {data['financial_health']['debt_to_equity']}%
Total Debt: {data['financial_health']['total_debt']}
Net Debt: {data['financial_health']['net_debt']}
Free Cash Flow: {data['financial_health']['free_cash_flow']}
Interest Coverage: {data['financial_health']['interest_coverage']}x

DIVIDEND INFORMATION:
Dividend Yield: {data['dividend_info']['dividend_yield']}%
Payout Ratio: {data['dividend_info']['payout_ratio']}%

PRICE ANALYSIS:
Current Price: {data['price_analysis']['current_price']}
52-Week Range: {data['price_analysis']['52_week_low']} - {data['price_analysis']['52_week_high']}
Position in Range: {data['price_analysis']['price_position_in_range']}%
Beta: {data['price_analysis']['beta']}
50-Day Average: {data['price_analysis']['fifty_day_avg']}
200-Day Average: {data['price_analysis']['two_hundred_day_avg']}

ANALYST COVERAGE:
Recommendation: {data['peer_comparison']['recommendation']}
Number of Analysts: {data['peer_comparison']['analyst_count']}
Target Price: {data['peer_comparison']['target_price']}

QUALITY SCORE:
Overall Score: {quality['score']}/{quality['max_score']} ({quality['percentage']}%)
Rating: {quality['rating']}
"""


def format_news_for_ai(news_analysis):
    """Format news analysis for AI consumption"""
    if not news_analysis["success"]:
        return "NEWS: Unable to fetch comprehensive news data"
    
    summary = news_analysis["summary"]
    articles = news_analysis["articles"]
    themes = news_analysis.get("key_themes", [])
    
    news_text = f"""
NEWS SENTIMENT ANALYSIS:
Company: {summary['company_name']}
Overall Sentiment: {summary['overall_sentiment']} {summary['overall_emoji']}
Sentiment Score: {summary['sentiment_score']} (Net: Positive minus Negative)
Total Articles Analyzed: {summary['total_articles']}
Sources: {news_analysis.get('total_sources', 'Multiple')} different news sources

SENTIMENT DISTRIBUTION:
Positive: {summary['sentiment_distribution']['positive']} ({summary['sentiment_distribution']['positive_percentage']}%)
Negative: {summary['sentiment_distribution']['negative']} ({summary['sentiment_distribution']['negative_percentage']}%)
Neutral: {summary['sentiment_distribution']['neutral']} ({summary['sentiment_distribution']['neutral_percentage']}%)

KEY THEMES IDENTIFIED:
"""
    
    for theme in themes:
        news_text += f"- {theme['theme']}: {theme['count']} articles\n"
    
    news_text += f"\nMOST COMMON CATEGORY: {summary['most_common_category']}\n"
    
    news_text += f"\nCRITICAL/HIGH IMPORTANCE NEWS ({summary['critical_news_count']} articles):\n"
    for i, article in enumerate(summary.get('critical_articles', [])[:5], 1):
        news_text += f"{i}. [{article['importance']}] {article['sentiment_emoji']} {article['title']}\n"
        news_text += f"   Source: {article['source']} | Category: {article['category']} | {article['time']}\n\n"
    
    news_text += f"\nRECENT HEADLINES (Last 24-48 hours - {summary['recent_news_count']} articles):\n"
    for i, article in enumerate(articles[:10], 1):
        news_text += f"{i}. {article['sentiment_emoji']} [{article['category']}] {article['title']}\n"
        news_text += f"   {article['source']} • {article['time']}\n"
    
    return news_text


def format_checklist_for_ai(checklist_results):
    """Format checklist results for AI consumption"""
    verdict = checklist_results["verdict"]
    
    checklist_text = f"""
INVESTMENT CHECKLIST EVALUATION:
Total Score: {checklist_results['total_score']}/100
Overall Verdict: {verdict['rating']}
Risk Level: {verdict['risk_level']}
Recommendation: {verdict['recommendation']}

DETAILED CATEGORY SCORES:
"""
    
    for category, scores in checklist_results['category_scores'].items():
        checklist_text += f"\n{category.replace('_', ' ').upper()}:\n"
        checklist_text += f"  Score: {scores['score']}/100\n"
        checklist_text += f"  Weight: {scores['weight']}% of total\n"
        checklist_text += f"  Weighted Contribution: {scores['weighted_score']} points\n"
    
    checklist_text += f"\n\nKEY STRENGTHS:\n"
    for i, strength in enumerate(checklist_results['detailed_summary']['strengths'][:7], 1):
        checklist_text += f"{i}. ✓ {strength}\n"
    
    checklist_text += f"\n\nKEY CONCERNS:\n"
    for i, weakness in enumerate(checklist_results['detailed_summary']['weaknesses'][:7], 1):
        checklist_text += f"{i}. ✗ {weakness}\n"
    
    return checklist_text


def build_comprehensive_report(company, ticker, enhanced_financial, news_analysis, checklist_results, ai_report):
    """Build the final comprehensive report"""
    
    data = enhanced_financial["data"]
    quality = enhanced_financial["quality_score"]
    verdict = checklist_results["verdict"]
    
    # Header
    report = f"""
{'='*80}
AI-POWERED COMPREHENSIVE STOCK RESEARCH REPORT
{'='*80}
Company: {data['basic_info']['company_name']}
Ticker: {ticker}
Sector: {data['basic_info']['sector']} | Industry: {data['basic_info']['industry']}
Report Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Currency: {data['basic_info']['currency']}
{'='*80}

{'='*80}
EXECUTIVE SUMMARY
{'='*80}
Overall Verdict: {verdict['rating']}
Investment Score: {checklist_results['total_score']}/100
Quality Rating: {quality['rating']} ({quality['percentage']}%)
Risk Level: {verdict['risk_level']}

Recommendation: {verdict['recommendation']}

Current Price: {data['price_analysis']['current_price']} {data['basic_info']['currency']}
Target Price: {data['peer_comparison']['target_price']} {data['basic_info']['currency']}
Analyst Recommendation: {data['peer_comparison']['recommendation']}
{'='*80}

{'='*80}
COMPANY SNAPSHOT
{'='*80}
Company Name      : {data['basic_info']['company_name']}
Ticker Symbol     : {ticker}
Sector            : {data['basic_info']['sector']}
Industry          : {data['basic_info']['industry']}
Country           : {data['basic_info']['country']}
Website           : {data['basic_info']['website']}
Employees         : {data['basic_info']['employees']}

Market Cap        : {data['basic_info']['market_cap']}
Current Price     : {data['price_analysis']['current_price']} {data['basic_info']['currency']}
52-Week Range     : {data['price_analysis']['52_week_low']} - {data['price_analysis']['52_week_high']}
Price Position    : {data['price_analysis']['price_position_in_range']}% of 52-week range
Beta (Volatility) : {data['price_analysis']['beta']}

Business Overview:
{data['basic_info']['business_summary']}
{'='*80}

{'='*80}
VALUATION ANALYSIS
{'='*80}
P/E Ratio         : {data['valuation_metrics']['pe_ratio']}
Forward P/E       : {data['valuation_metrics']['forward_pe']}
PEG Ratio         : {data['valuation_metrics']['peg_ratio']}
Price/Book        : {data['valuation_metrics']['price_to_book']}
Price/Sales       : {data['valuation_metrics']['price_to_sales']}
EV/Revenue        : {data['valuation_metrics']['ev_to_revenue']}
EV/EBITDA         : {data['valuation_metrics']['ev_to_ebitda']}
Enterprise Value  : {data['valuation_metrics']['enterprise_value']}

Analyst Coverage:
Recommendation    : {data['peer_comparison']['recommendation']}
Number of Analysts: {data['peer_comparison']['analyst_count']}
Target Price      : {data['peer_comparison']['target_price']} {data['basic_info']['currency']}
{'='*80}

{'='*80}
GROWTH METRICS
{'='*80}
Revenue 3Y CAGR   : {data['growth_metrics']['revenue_3y_cagr']}%
Earnings 3Y CAGR  : {data['growth_metrics']['earnings_3y_cagr']}%
Revenue Trend     : {data['growth_metrics']['revenue_trend']}
QoQ Revenue Growth: {data['growth_metrics']['revenue_growth_qoq']}%
QoQ Earnings Growth: {data['growth_metrics']['earnings_growth_qoq']}%
{'='*80}

{'='*80}
PROFITABILITY METRICS
{'='*80}
Return on Equity  : {data['profitability_metrics']['roe']}%
Return on Assets  : {data['profitability_metrics']['roa']}%
Return on Invested Capital: {data['profitability_metrics']['roic']}%
Profit Margin     : {data['profitability_metrics']['profit_margin']}%
Operating Margin  : {data['profitability_metrics']['operating_margin']}%
Gross Margin      : {data['profitability_metrics']['gross_margin']}%
{'='*80}

{'='*80}
FINANCIAL HEALTH & LIQUIDITY
{'='*80}
Current Ratio     : {data['financial_health']['current_ratio']}
Quick Ratio       : {data['financial_health']['quick_ratio']}
Debt/Equity       : {data['financial_health']['debt_to_equity']}%
Total Debt        : {data['financial_health']['total_debt']}
Total Cash        : {data['financial_health']['total_cash']}
Net Debt          : {data['financial_health']['net_debt']}
Debt/Market Cap   : {data['financial_health']['debt_to_market_cap']}%
Free Cash Flow    : {data['financial_health']['free_cash_flow']}
Interest Coverage : {data['financial_health']['interest_coverage']}x
{'='*80}

{'='*80}
DIVIDEND INFORMATION
{'='*80}
Dividend Yield    : {data['dividend_info']['dividend_yield']}%
Dividend Rate     : {data['dividend_info']['dividend_rate']}
Payout Ratio      : {data['dividend_info']['payout_ratio']}%
5-Year Avg Yield  : {data['dividend_info']['five_year_avg_yield']}%
{'='*80}

{'='*80}
PRICE & TECHNICAL ANALYSIS
{'='*80}
Current Price     : {data['price_analysis']['current_price']} {data['basic_info']['currency']}
52-Week Low       : {data['price_analysis']['52_week_low']}
52-Week High      : {data['price_analysis']['52_week_high']}
Price Position    : {data['price_analysis']['price_position_in_range']}% of range
50-Day Average    : {data['price_analysis']['fifty_day_avg']}
200-Day Average   : {data['price_analysis']['two_hundred_day_avg']}
Beta              : {data['price_analysis']['beta']}
Volume            : {data['price_analysis']['volume']}
Average Volume    : {data['price_analysis']['avg_volume']}
{'='*80}

{'='*80}
NEWS SENTIMENT & MARKET BUZZ
{'='*80}
"""
    
    # Add news section
    if news_analysis["success"]:
        summary = news_analysis["summary"]
        themes = news_analysis.get("key_themes", [])
        
        report += f"""
Overall Sentiment : {summary['overall_sentiment']} {summary['overall_emoji']}
Sentiment Score   : {summary['sentiment_score']} (Net positive minus negative)
Articles Analyzed : {summary['total_articles']} from {news_analysis.get('total_sources', 'multiple')} sources

SENTIMENT BREAKDOWN:
Positive          : {summary['sentiment_distribution']['positive']} articles ({summary['sentiment_distribution']['positive_percentage']}%)
Negative          : {summary['sentiment_distribution']['negative']} articles ({summary['sentiment_distribution']['negative_percentage']}%)
Neutral           : {summary['sentiment_distribution']['neutral']} articles ({summary['sentiment_distribution']['neutral_percentage']}%)

KEY THEMES IDENTIFIED:
"""
        for theme in themes:
            report += f"• {theme['theme']}: {theme['count']} articles\n"
        
        report += f"\nMost Common Category: {summary['most_common_category']}\n"
        
        report += f"\n\nCRITICAL/HIGH IMPORTANCE NEWS:\n"
        report += "-" * 80 + "\n"
        for i, article in enumerate(summary.get('critical_articles', [])[:5], 1):
            report += f"\n{i}. {article['sentiment_emoji']} [{article['importance']}] {article['title']}\n"
            report += f"   Category: {article['category']} | Source: {article['source']}\n"
            report += f"   Time: {article['time']}\n"
        
        report += f"\n\nRECENT HEADLINES:\n"
        report += "-" * 80 + "\n"
        for i, article in enumerate(news_analysis["articles"][:12], 1):
            report += f"\n{i}. {article['sentiment_emoji']} [{article['category']}] {article['title']}\n"
            report += f"   {article['source']} • {article['time']}\n"
    else:
        report += "News data temporarily unavailable.\n"
    
    report += f"\n{'='*80}\n\n"
    
    # Add checklist section
    report += f"""
{'='*80}
INVESTMENT CHECKLIST EVALUATION
{'='*80}
"""
    
    for category_name, category_data in checklist_results['category_results'].items():
        score_info = checklist_results['category_scores'][category_name]
        report += f"\n{category_data['category'].upper()}: {score_info['score']}/100 "
        report += f"(Weight: {score_info['weight']}%, Contribution: {score_info['weighted_score']} pts)\n"
        report += "-" * 80 + "\n"
        
        for check_name, passed, detail in category_data['checks']:
            status = "✅" if passed else "❌"
            report += f"{status} {check_name}\n   {detail}\n\n"
    
    report += f"{'='*80}\n"
    report += f"OVERALL INVESTMENT SCORE: {checklist_results['total_score']}/100\n"
    report += f"VERDICT: {verdict['rating']}\n"
    report += f"RISK LEVEL: {verdict['risk_level']}\n"
    report += f"RECOMMENDATION: {verdict['recommendation']}\n"
    report += f"{'='*80}\n\n"
    
    # Add institutional holdings if available
    if data.get('institutional_holdings', {}).get('has_data'):
        report += f"""
{'='*80}
TOP INSTITUTIONAL HOLDERS
{'='*80}
"""
        for i, holder in enumerate(data['institutional_holdings']['top_holders'][:5], 1):
            report += f"{i}. {holder.get('Holder', 'N/A')}\n"
            report += f"   Shares: {holder.get('Shares', 'N/A')} | "
            report += f"Value: {holder.get('Value', 'N/A')}\n\n"
        report += f"{'='*80}\n\n"
    
    # Add AI analysis
    report += f"""
{'='*80}
AI-POWERED COMPREHENSIVE ANALYSIS
{'='*80}
{ai_report}

{'='*80}
DISCLAIMER & IMPORTANT NOTES
{'='*80}
This research report is generated using artificial intelligence and publicly 
available financial data. The analysis is for educational and research purposes 
only and does NOT constitute investment advice, financial advice, trading advice, 
or any other sort of advice.

Key Points to Remember:
• Past performance does not guarantee future results
• All investments carry risk, including potential loss of principal
• Conduct your own due diligence before making investment decisions
• Consult with a qualified financial advisor for personalized advice
• Market conditions can change rapidly
• The data presented may contain errors or become outdated

Data Sources: Yahoo Finance, Google News, Public Financial Filings
Analysis Method: AI-powered with rule-based checklist validation
Report Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{'='*80}
"""
    
    return report


# ---------------------------
# HISTORY PAGE
# ---------------------------
@app.route("/history")
def history():
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, company, created_at FROM research_history ORDER BY id DESC LIMIT 50"
    ).fetchall()
    conn.close()

    return render_template("history.html", history=rows)


# ---------------------------
# VIEW SAVED REPORT
# ---------------------------
@app.route("/report/<int:report_id>")
def view_report(report_id):
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM research_history WHERE id = ?",
        (report_id,)
    ).fetchone()
    conn.close()

    if row is None:
        return "Report not found", 404

    return render_template(
        "report.html",
        company=row["company"],
        report=row["report"],
        created_at=row["created_at"]
    )


# ---------------------------
# DELETE REPORT
# ---------------------------
@app.route("/delete/<int:report_id>", methods=["DELETE", "POST"])
def delete_report(report_id):
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM research_history WHERE id = ?", (report_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------
# CLEAR ALL HISTORY
# ---------------------------
@app.route("/clear_history", methods=["POST"])
def clear_history():
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM research_history")
        conn.commit()
        conn.close()
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------
# ERROR HANDLER
# ---------------------------
@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", 
                         error_message="Page not found",
                         suggestion="Return to home page"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html",
                         error_message="Internal server error",
                         suggestion="Please try again later"), 500


# ---------------------------
# APP ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    # Ensure database is initialized
    if not os.path.exists("database/research.db"):
        print("⚠️ Database not found. Please run db_init.py first.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)