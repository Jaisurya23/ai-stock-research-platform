import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests

class EnhancedFinancialAnalyzer:
    """
    Enhanced financial analyzer with better ticker resolution and comprehensive data
    """
    
    def __init__(self, ticker: str):
        self.original_ticker = ticker
        self.ticker = self._resolve_ticker(ticker)
        self.stock = yf.Ticker(self.ticker)
        self.info = self.stock.info
        
    def _resolve_ticker(self, ticker: str):
        """
        Resolve ticker symbol for different exchanges
        Handles Indian stocks, US stocks, and company names
        """
        ticker = ticker.upper().strip()
        
        # Indian stock suffixes
        indian_exchanges = {
            'NSE': '.NS',
            'BSE': '.BO'
        }
        
        # Common Indian stocks mapping
        indian_stocks = {
            'HDFC BANK': 'HDFCBANK.NS',
            'HDFCBANK': 'HDFCBANK.NS',
            'HDFC': 'HDFCBANK.NS',
            'ICICI BANK': 'ICICIBANK.NS',
            'ICICIBANK': 'ICICIBANK.NS',
            'RELIANCE': 'RELIANCE.NS',
            'TCS': 'TCS.NS',
            'INFOSYS': 'INFY.NS',
            'INFY': 'INFY.NS',
            'WIPRO': 'WIPRO.NS',
            'SBI': 'SBIN.NS',
            'BHARTI': 'BHARTIARTL.NS',
            'AIRTEL': 'BHARTIARTL.NS',
            'ITC': 'ITC.NS',
            'BAJAJ': 'BAJFINANCE.NS',
            'MARUTI': 'MARUTI.NS',
            'ASIAN PAINTS': 'ASIANPAINT.NS',
            'TITAN': 'TITAN.NS',
            'NESTLE': 'NESTLEIND.NS',
            'HUL': 'HINDUNILVR.NS',
            'HINDUSTAN UNILEVER': 'HINDUNILVR.NS'
        }
        
        # Check if it's a known Indian company name
        if ticker in indian_stocks:
            return indian_stocks[ticker]
        
        # If already has exchange suffix, return as is
        if '.NS' in ticker or '.BO' in ticker:
            return ticker
        
        # Try NSE first for Indian stocks
        if ticker in ['HDFCBANK', 'ICICIBANK', 'RELIANCE', 'TCS', 'INFY', 'WIPRO', 'SBIN']:
            return f"{ticker}.NS"
        
        # For other cases, try to validate ticker
        try:
            test_stock = yf.Ticker(ticker)
            if test_stock.info.get('regularMarketPrice'):
                return ticker
        except:
            pass
        
        # Try with .NS suffix
        try:
            test_ticker = f"{ticker}.NS"
            test_stock = yf.Ticker(test_ticker)
            if test_stock.info.get('regularMarketPrice'):
                return test_ticker
        except:
            pass
        
        # Default return
        return ticker
    
    def get_comprehensive_data(self):
        """
        Fetch comprehensive financial data with historical analysis
        """
        try:
            return {
                "basic_info": self._get_basic_info(),
                "valuation_metrics": self._get_valuation_metrics(),
                "growth_metrics": self._get_growth_metrics(),
                "profitability_metrics": self._get_profitability_metrics(),
                "financial_health": self._get_financial_health(),
                "dividend_info": self._get_dividend_info(),
                "price_analysis": self._get_price_analysis(),
                "peer_comparison": self._get_peer_comparison(),
                "institutional_holdings": self._get_institutional_holdings()
            }
        except Exception as e:
            print(f"Error fetching comprehensive data: {e}")
            return self._get_fallback_data()
    
    def _get_basic_info(self):
        """Basic company information"""
        return {
            "company_name": self.info.get("longName") or self.info.get("shortName", "N/A"),
            "ticker": self.ticker,
            "sector": self.info.get("sector", "N/A"),
            "industry": self.info.get("industry", "N/A"),
            "country": self.info.get("country", "N/A"),
            "website": self.info.get("website", "N/A"),
            "business_summary": self.info.get("longBusinessSummary", "N/A")[:500],
            "employees": self._format_number_plain(self.info.get("fullTimeEmployees")),
            "market_cap": self._format_number(self.info.get("marketCap")),
            "currency": self.info.get("currency", "USD")
        }
    
    def _get_valuation_metrics(self):
        """Calculate valuation ratios and metrics"""
        pe_ratio = self.info.get("trailingPE") or self.info.get("forwardPE", 0)
        
        return {
            "pe_ratio": round(pe_ratio, 2) if pe_ratio else 0,
            "forward_pe": round(self.info.get("forwardPE", 0), 2) if self.info.get("forwardPE") else 0,
            "peg_ratio": round(self.info.get("pegRatio", 0), 2) if self.info.get("pegRatio") else 0,
            "price_to_book": round(self.info.get("priceToBook", 0), 2) if self.info.get("priceToBook") else 0,
            "price_to_sales": round(self.info.get("priceToSalesTrailing12Months", 0), 2) if self.info.get("priceToSalesTrailing12Months") else 0,
            "enterprise_value": self._format_number(self.info.get("enterpriseValue")),
            "ev_to_revenue": round(self.info.get("enterpriseToRevenue", 0), 2) if self.info.get("enterpriseToRevenue") else 0,
            "ev_to_ebitda": round(self.info.get("enterpriseToEbitda", 0), 2) if self.info.get("enterpriseToEbitda") else 0
        }
    
    def _get_growth_metrics(self):
        """Calculate growth rates from historical data"""
        try:
            # Try to get quarterly and annual financials
            quarterly = self.stock.quarterly_financials
            annual = self.stock.financials
            
            revenue_growth = 0
            earnings_growth = 0
            revenue_trend = "Unknown"
            
            # Calculate from quarterly data if available
            if quarterly is not None and not quarterly.empty:
                revenue_growth = self._calculate_growth_from_financials(quarterly, "Total Revenue")
                earnings_growth = self._calculate_growth_from_financials(quarterly, "Net Income")
                revenue_trend = self._get_trend(quarterly, "Total Revenue")
            elif annual is not None and not annual.empty:
                revenue_growth = self._calculate_growth_from_financials(annual, "Total Revenue")
                earnings_growth = self._calculate_growth_from_financials(annual, "Net Income")
                revenue_trend = self._get_trend(annual, "Total Revenue")
            
            return {
                "revenue_3y_cagr": revenue_growth,
                "earnings_3y_cagr": earnings_growth,
                "revenue_growth_qoq": round(self.info.get("revenueGrowth", 0) * 100, 2) if self.info.get("revenueGrowth") else 0,
                "earnings_growth_qoq": round(self.info.get("earningsGrowth", 0) * 100, 2) if self.info.get("earningsGrowth") else 0,
                "revenue_trend": revenue_trend
            }
        except Exception as e:
            print(f"Error in growth metrics: {e}")
            return self._empty_growth_metrics()
    
    def _get_profitability_metrics(self):
        """Calculate profitability ratios"""
        return {
            "gross_margin": round(self.info.get("grossMargins", 0) * 100, 2) if self.info.get("grossMargins") else 0,
            "operating_margin": round(self.info.get("operatingMargins", 0) * 100, 2) if self.info.get("operatingMargins") else 0,
            "profit_margin": round(self.info.get("profitMargins", 0) * 100, 2) if self.info.get("profitMargins") else 0,
            "roe": round(self.info.get("returnOnEquity", 0) * 100, 2) if self.info.get("returnOnEquity") else 0,
            "roa": round(self.info.get("returnOnAssets", 0) * 100, 2) if self.info.get("returnOnAssets") else 0,
            "roic": self._calculate_roic()
        }
    
    def _get_financial_health(self):
        """Assess financial health metrics"""
        total_debt = self.info.get("totalDebt", 0) or 0
        total_cash = self.info.get("totalCash", 0) or 0
        market_cap = self.info.get("marketCap", 1) or 1
        
        return {
            "current_ratio": round(self.info.get("currentRatio", 0), 2) if self.info.get("currentRatio") else 0,
            "quick_ratio": round(self.info.get("quickRatio", 0), 2) if self.info.get("quickRatio") else 0,
            "debt_to_equity": round(self.info.get("debtToEquity", 0), 2) if self.info.get("debtToEquity") else 0,
            "total_debt": self._format_number(total_debt),
            "total_cash": self._format_number(total_cash),
            "net_debt": self._format_number(total_debt - total_cash),
            "debt_to_market_cap": round((total_debt / market_cap * 100), 2) if market_cap > 0 else 0,
            "interest_coverage": round(self.info.get("interestCoverage", 0), 2) if self.info.get("interestCoverage") else 0,
            "free_cash_flow": self._format_number(self.info.get("freeCashflow"))
        }
    
    def _get_dividend_info(self):
        """Get dividend information"""
        div_yield = self.info.get("dividendYield", 0)
        return {
            "dividend_yield": round(div_yield * 100, 2) if div_yield else 0,
            "dividend_rate": round(self.info.get("dividendRate", 0), 2) if self.info.get("dividendRate") else 0,
            "payout_ratio": round(self.info.get("payoutRatio", 0) * 100, 2) if self.info.get("payoutRatio") else 0,
            "five_year_avg_yield": round(self.info.get("fiveYearAvgDividendYield", 0), 2) if self.info.get("fiveYearAvgDividendYield") else 0
        }
    
    def _get_price_analysis(self):
        """Analyze current price vs historical ranges"""
        current_price = self.info.get("currentPrice") or self.info.get("regularMarketPrice", 0)
        fifty_two_week_low = self.info.get("fiftyTwoWeekLow", 0) or 0
        fifty_two_week_high = self.info.get("fiftyTwoWeekHigh", 0) or 0
        
        price_range = fifty_two_week_high - fifty_two_week_low
        price_position = 0
        if price_range > 0 and current_price > 0:
            price_position = round(((current_price - fifty_two_week_low) / price_range) * 100, 2)
        
        return {
            "current_price": round(current_price, 2) if current_price else 0,
            "52_week_low": round(fifty_two_week_low, 2) if fifty_two_week_low else 0,
            "52_week_high": round(fifty_two_week_high, 2) if fifty_two_week_high else 0,
            "price_position_in_range": price_position,
            "fifty_day_avg": round(self.info.get("fiftyDayAverage", 0), 2) if self.info.get("fiftyDayAverage") else 0,
            "two_hundred_day_avg": round(self.info.get("twoHundredDayAverage", 0), 2) if self.info.get("twoHundredDayAverage") else 0,
            "beta": round(self.info.get("beta", 1), 2) if self.info.get("beta") else 1,
            "volume": self._format_number_plain(self.info.get("volume")),
            "avg_volume": self._format_number_plain(self.info.get("averageVolume"))
        }
    
    def _get_peer_comparison(self):
        """Get basic peer comparison data"""
        return {
            "sector": self.info.get("sector", "N/A"),
            "industry": self.info.get("industry", "N/A"),
            "recommendation": self.info.get("recommendationKey", "N/A"),
            "target_price": round(self.info.get("targetMeanPrice", 0), 2) if self.info.get("targetMeanPrice") else 0,
            "analyst_count": self.info.get("numberOfAnalystOpinions", 0) or 0
        }
    
    def _get_institutional_holdings(self):
        """Get institutional ownership data"""
        try:
            institutions = self.stock.institutional_holders
            if institutions is not None and not institutions.empty:
                return {
                    "has_data": True,
                    "top_holders": institutions.head(5).to_dict('records') if len(institutions) > 0 else []
                }
        except:
            pass
        
        return {
            "has_data": False,
            "top_holders": []
        }
    
    # Helper methods
    
    def _calculate_growth_from_financials(self, financials, metric):
        """Calculate growth rate from financial statements"""
        try:
            if metric not in financials.index:
                return 0
            
            values = financials.loc[metric].dropna()
            if len(values) < 2:
                return 0
            
            sorted_values = values.sort_index()
            
            # Calculate YoY growth
            if len(sorted_values) >= 2:
                recent = sorted_values.iloc[0]
                older = sorted_values.iloc[-1]
                
                if older != 0:
                    years = len(sorted_values) - 1
                    if years > 0:
                        cagr = (pow(recent / older, 1/years) - 1) * 100
                        return round(cagr, 2)
            
            return 0
        except:
            return 0
    
    def _get_trend(self, financials, metric):
        """Determine if metric is increasing, decreasing, or flat"""
        try:
            if metric not in financials.index:
                return "Unknown"
            
            values = financials.loc[metric].dropna().sort_index(ascending=False)
            if len(values) < 2:
                return "Insufficient data"
            
            recent_values = values.head(min(3, len(values)))
            
            if len(recent_values) >= 2:
                increasing = all(recent_values.iloc[i] >= recent_values.iloc[i+1] 
                               for i in range(len(recent_values)-1))
                decreasing = all(recent_values.iloc[i] <= recent_values.iloc[i+1] 
                               for i in range(len(recent_values)-1))
                
                if increasing:
                    return "Growing"
                elif decreasing:
                    return "Declining"
            
            return "Mixed"
        except:
            return "Unknown"
    
    def _calculate_roic(self):
        """Calculate Return on Invested Capital"""
        try:
            ebit = self.info.get("ebit", 0)
            total_debt = self.info.get("totalDebt", 0) or 0
            total_equity = self.info.get("totalStockholderEquity", 0) or 0
            
            if total_debt + total_equity == 0:
                return 0
            
            roic = (ebit / (total_debt + total_equity)) * 100
            return round(roic, 2)
        except:
            return 0
    
    def _format_number(self, num):
        """Format large numbers with B, M, K suffixes"""
        if num is None or num == 0:
            return "N/A"
        
        if abs(num) >= 1e9:
            return f"${num/1e9:.2f}B"
        elif abs(num) >= 1e6:
            return f"${num/1e6:.2f}M"
        elif abs(num) >= 1e3:
            return f"${num/1e3:.2f}K"
        else:
            return f"${num:.2f}"
    
    def _format_number_plain(self, num):
        """Format numbers without $ sign"""
        if num is None or num == 0:
            return "N/A"
        
        if abs(num) >= 1e9:
            return f"{num/1e9:.2f}B"
        elif abs(num) >= 1e6:
            return f"{num/1e6:.2f}M"
        elif abs(num) >= 1e3:
            return f"{num/1e3:.2f}K"
        else:
            return f"{num:,.0f}"
    
    def _empty_growth_metrics(self):
        """Return empty growth metrics structure"""
        return {
            "revenue_3y_cagr": 0,
            "earnings_3y_cagr": 0,
            "revenue_growth_qoq": 0,
            "earnings_growth_qoq": 0,
            "revenue_trend": "Unknown"
        }
    
    def _get_fallback_data(self):
        """Return basic structure when data fetch fails"""
        return {
            "basic_info": {
                "company_name": self.original_ticker,
                "ticker": self.ticker,
                "sector": "N/A",
                "industry": "N/A",
                "country": "N/A",
                "website": "N/A",
                "business_summary": "Unable to fetch data",
                "employees": "N/A",
                "market_cap": "N/A",
                "currency": "USD"
            },
            "valuation_metrics": {"pe_ratio": 0, "forward_pe": 0, "peg_ratio": 0, "price_to_book": 0, "price_to_sales": 0, "enterprise_value": "N/A", "ev_to_revenue": 0, "ev_to_ebitda": 0},
            "growth_metrics": self._empty_growth_metrics(),
            "profitability_metrics": {"gross_margin": 0, "operating_margin": 0, "profit_margin": 0, "roe": 0, "roa": 0, "roic": 0},
            "financial_health": {"current_ratio": 0, "quick_ratio": 0, "debt_to_equity": 0, "total_debt": "N/A", "total_cash": "N/A", "net_debt": "N/A", "debt_to_market_cap": 0, "interest_coverage": 0, "free_cash_flow": "N/A"},
            "dividend_info": {"dividend_yield": 0, "dividend_rate": 0, "payout_ratio": 0, "five_year_avg_yield": 0},
            "price_analysis": {"current_price": 0, "52_week_low": 0, "52_week_high": 0, "price_position_in_range": 0, "fifty_day_avg": 0, "two_hundred_day_avg": 0, "beta": 1, "volume": "N/A", "avg_volume": "N/A"},
            "peer_comparison": {"sector": "N/A", "industry": "N/A", "recommendation": "N/A", "target_price": 0, "analyst_count": 0},
            "institutional_holdings": {"has_data": False, "top_holders": []}
        }
    
    def get_quality_score(self, comprehensive_data):
        """Calculate overall quality score (0-100) based on multiple factors"""
        score = 0
        max_score = 100
        
        # Profitability (30 points)
        profit_metrics = comprehensive_data["profitability_metrics"]
        if profit_metrics["roe"] > 15:
            score += 10
        elif profit_metrics["roe"] > 10:
            score += 5
        
        if profit_metrics["operating_margin"] > 15:
            score += 10
        elif profit_metrics["operating_margin"] > 10:
            score += 5
        
        if profit_metrics["profit_margin"] > 10:
            score += 10
        elif profit_metrics["profit_margin"] > 5:
            score += 5
        
        # Growth (25 points)
        growth_metrics = comprehensive_data["growth_metrics"]
        if growth_metrics["revenue_3y_cagr"] > 15:
            score += 15
        elif growth_metrics["revenue_3y_cagr"] > 10:
            score += 10
        elif growth_metrics["revenue_3y_cagr"] > 5:
            score += 5
        
        if growth_metrics["earnings_3y_cagr"] > 15:
            score += 10
        elif growth_metrics["earnings_3y_cagr"] > 10:
            score += 5
        
        # Financial Health (25 points)
        health = comprehensive_data["financial_health"]
        if health["current_ratio"] >= 2:
            score += 10
        elif health["current_ratio"] >= 1.5:
            score += 5
        
        if health["debt_to_equity"] < 50:
            score += 10
        elif health["debt_to_equity"] < 100:
            score += 5
        
        if health["interest_coverage"] > 5:
            score += 5
        elif health["interest_coverage"] > 3:
            score += 3
        
        # Valuation (20 points)
        valuation = comprehensive_data["valuation_metrics"]
        if 0 < valuation["pe_ratio"] < 20:
            score += 10
        elif 0 < valuation["pe_ratio"] < 30:
            score += 5
        
        if 0 < valuation["peg_ratio"] < 1:
            score += 10
        elif 0 < valuation["peg_ratio"] < 2:
            score += 5
        
        return {
            "score": score,
            "max_score": max_score,
            "percentage": round((score / max_score) * 100, 2),
            "rating": self._get_rating(score, max_score)
        }
    
    def _get_rating(self, score, max_score):
        """Convert score to rating"""
        percentage = (score / max_score) * 100
        
        if percentage >= 80:
            return "Excellent"
        elif percentage >= 60:
            return "Good"
        elif percentage >= 40:
            return "Average"
        elif percentage >= 20:
            return "Below Average"
        else:
            return "Poor"


def fetch_enhanced_financial_data(ticker: str):
    """Main function to fetch enhanced financial data"""
    try:
        analyzer = EnhancedFinancialAnalyzer(ticker)
        comprehensive_data = analyzer.get_comprehensive_data()
        quality_score = analyzer.get_quality_score(comprehensive_data)
        
        return {
            "success": True,
            "data": comprehensive_data,
            "quality_score": quality_score,
            "resolved_ticker": analyzer.ticker
        }
    except Exception as e:
        print(f"Error in fetch_enhanced_financial_data: {e}")
        return {
            "success": False,
            "error": f"Failed to fetch enhanced data: {str(e)}"
        }