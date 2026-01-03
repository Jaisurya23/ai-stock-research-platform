class IntelligentChecklistEngine:
    """
    Advanced checklist evaluation with weighted scoring and detailed reasoning
    """
    
    def __init__(self):
        self.criteria = {
            "business_quality": {
                "weight": 20,
                "checks": []
            },
            "financial_strength": {
                "weight": 25,
                "checks": []
            },
            "growth_potential": {
                "weight": 20,
                "checks": []
            },
            "valuation": {
                "weight": 15,
                "checks": []
            },
            "risk_assessment": {
                "weight": 20,
                "checks": []
            }
        }
    
    def evaluate(self, enhanced_data, news_summary):
        """
        Comprehensive evaluation with weighted scoring
        """
        results = {
            "business_quality": self._check_business_quality(enhanced_data),
            "financial_strength": self._check_financial_strength(enhanced_data),
            "growth_potential": self._check_growth(enhanced_data),
            "valuation": self._check_valuation(enhanced_data),
            "risk_assessment": self._check_risks(enhanced_data, news_summary)
        }
        
        # Calculate weighted scores
        total_score = 0
        category_scores = {}
        
        for category, data in results.items():
            weight = self.criteria[category]["weight"]
            category_score = data["score"]
            weighted_score = (category_score / 100) * weight
            total_score += weighted_score
            category_scores[category] = {
                "score": category_score,
                "weighted_score": round(weighted_score, 2),
                "weight": weight
            }
        
        # Generate verdict
        verdict = self._generate_verdict(total_score, results)
        
        return {
            "category_results": results,
            "category_scores": category_scores,
            "total_score": round(total_score, 2),
            "max_score": 100,
            "verdict": verdict,
            "detailed_summary": self._generate_summary(results)
        }
    
    def _check_business_quality(self, data):
        """
        Evaluate business quality (20 points)
        """
        basic = data["data"]["basic_info"]
        profitability = data["data"]["profitability_metrics"]
        
        checks = []
        score = 0
        
        # Check 1: Profitability (50%)
        roe = profitability["roe"]
        if roe > 20:
            checks.append(("Excellent ROE (>20%)", True, f"ROE: {roe}%"))
            score += 50
        elif roe > 15:
            checks.append(("Strong ROE (15-20%)", True, f"ROE: {roe}%"))
            score += 35
        elif roe > 10:
            checks.append(("Decent ROE (10-15%)", True, f"ROE: {roe}%"))
            score += 20
        else:
            checks.append(("ROE Below Standard (<10%)", False, f"ROE: {roe}%"))
        
        # Check 2: Operating Margin (30%)
        op_margin = profitability["operating_margin"]
        if op_margin > 20:
            checks.append(("High Operating Margin (>20%)", True, f"Margin: {op_margin}%"))
            score += 30
        elif op_margin > 15:
            checks.append(("Good Operating Margin (15-20%)", True, f"Margin: {op_margin}%"))
            score += 20
        elif op_margin > 10:
            checks.append(("Acceptable Operating Margin (10-15%)", True, f"Margin: {op_margin}%"))
            score += 10
        else:
            checks.append(("Low Operating Margin (<10%)", False, f"Margin: {op_margin}%"))
        
        # Check 3: Company Size & Market Cap (20%)
        market_cap = basic.get("market_cap", "N/A")
        if market_cap != "N/A" and "$" in market_cap:
            if "B" in market_cap:
                checks.append(("Large Cap Company", True, f"Market Cap: {market_cap}"))
                score += 20
            else:
                checks.append(("Small/Mid Cap Company", True, f"Market Cap: {market_cap}"))
                score += 10
        
        return {
            "score": min(score, 100),
            "checks": checks,
            "category": "Business Quality"
        }
    
    def _check_financial_strength(self, data):
        """
        Evaluate financial health (25 points)
        """
        health = data["data"]["financial_health"]
        
        checks = []
        score = 0
        
        # Check 1: Current Ratio (25%)
        current_ratio = health["current_ratio"]
        if current_ratio >= 2:
            checks.append(("Strong Liquidity (CR >= 2)", True, f"Current Ratio: {current_ratio}"))
            score += 25
        elif current_ratio >= 1.5:
            checks.append(("Good Liquidity (CR >= 1.5)", True, f"Current Ratio: {current_ratio}"))
            score += 15
        elif current_ratio >= 1:
            checks.append(("Adequate Liquidity (CR >= 1)", True, f"Current Ratio: {current_ratio}"))
            score += 8
        else:
            checks.append(("Poor Liquidity (CR < 1)", False, f"Current Ratio: {current_ratio}"))
        
        # Check 2: Debt Management (35%)
        debt_to_equity = health["debt_to_equity"]
        if debt_to_equity < 50:
            checks.append(("Low Debt (D/E < 50%)", True, f"D/E: {debt_to_equity}%"))
            score += 35
        elif debt_to_equity < 100:
            checks.append(("Moderate Debt (D/E < 100%)", True, f"D/E: {debt_to_equity}%"))
            score += 20
        elif debt_to_equity < 150:
            checks.append(("High Debt (D/E < 150%)", False, f"D/E: {debt_to_equity}%"))
            score += 5
        else:
            checks.append(("Very High Debt (D/E >= 150%)", False, f"D/E: {debt_to_equity}%"))
        
        # Check 3: Free Cash Flow (25%)
        fcf = health["free_cash_flow"]
        if fcf != "N/A" and "$" in fcf:
            if "-" not in fcf:
                checks.append(("Positive Free Cash Flow", True, f"FCF: {fcf}"))
                score += 25
            else:
                checks.append(("Negative Free Cash Flow", False, f"FCF: {fcf}"))
        
        # Check 4: Interest Coverage (15%)
        interest_cov = health["interest_coverage"]
        if interest_cov > 5:
            checks.append(("Strong Interest Coverage (>5x)", True, f"Coverage: {interest_cov}x"))
            score += 15
        elif interest_cov > 3:
            checks.append(("Adequate Interest Coverage (>3x)", True, f"Coverage: {interest_cov}x"))
            score += 8
        else:
            checks.append(("Weak Interest Coverage (<3x)", False, f"Coverage: {interest_cov}x"))
        
        return {
            "score": min(score, 100),
            "checks": checks,
            "category": "Financial Strength"
        }
    
    def _check_growth(self, data):
        """
        Evaluate growth potential (20 points)
        """
        growth = data["data"]["growth_metrics"]
        profitability = data["data"]["profitability_metrics"]
        
        checks = []
        score = 0
        
        # Check 1: Revenue Growth (40%)
        rev_cagr = growth["revenue_3y_cagr"]
        if rev_cagr > 20:
            checks.append(("Excellent Revenue Growth (>20%)", True, f"3Y CAGR: {rev_cagr}%"))
            score += 40
        elif rev_cagr > 15:
            checks.append(("Strong Revenue Growth (15-20%)", True, f"3Y CAGR: {rev_cagr}%"))
            score += 30
        elif rev_cagr > 10:
            checks.append(("Good Revenue Growth (10-15%)", True, f"3Y CAGR: {rev_cagr}%"))
            score += 20
        elif rev_cagr > 5:
            checks.append(("Moderate Revenue Growth (5-10%)", True, f"3Y CAGR: {rev_cagr}%"))
            score += 10
        else:
            checks.append(("Low Revenue Growth (<5%)", False, f"3Y CAGR: {rev_cagr}%"))
        
        # Check 2: Earnings Growth (40%)
        earn_cagr = growth["earnings_3y_cagr"]
        if earn_cagr > 20:
            checks.append(("Excellent Earnings Growth (>20%)", True, f"3Y CAGR: {earn_cagr}%"))
            score += 40
        elif earn_cagr > 15:
            checks.append(("Strong Earnings Growth (15-20%)", True, f"3Y CAGR: {earn_cagr}%"))
            score += 30
        elif earn_cagr > 10:
            checks.append(("Good Earnings Growth (10-15%)", True, f"3Y CAGR: {earn_cagr}%"))
            score += 20
        elif earn_cagr > 5:
            checks.append(("Moderate Earnings Growth (5-10%)", True, f"3Y CAGR: {earn_cagr}%"))
            score += 10
        else:
            checks.append(("Low Earnings Growth (<5%)", False, f"3Y CAGR: {earn_cagr}%"))
        
        # Check 3: Margin Expansion (20%)
        profit_margin = profitability["profit_margin"]
        if profit_margin > 15:
            checks.append(("High Profit Margin (>15%)", True, f"Margin: {profit_margin}%"))
            score += 20
        elif profit_margin > 10:
            checks.append(("Good Profit Margin (10-15%)", True, f"Margin: {profit_margin}%"))
            score += 12
        elif profit_margin > 5:
            checks.append(("Moderate Profit Margin (5-10%)", True, f"Margin: {profit_margin}%"))
            score += 6
        else:
            checks.append(("Low Profit Margin (<5%)", False, f"Margin: {profit_margin}%"))
        
        return {
            "score": min(score, 100),
            "checks": checks,
            "category": "Growth Potential"
        }
    
    def _check_valuation(self, data):
        """
        Evaluate valuation metrics (15 points)
        """
        valuation = data["data"]["valuation_metrics"]
        
        checks = []
        score = 0
        
        # Check 1: P/E Ratio (40%)
        pe = valuation["pe_ratio"]
        if 0 < pe < 15:
            checks.append(("Attractive P/E (<15)", True, f"P/E: {pe}"))
            score += 40
        elif 0 < pe < 25:
            checks.append(("Reasonable P/E (15-25)", True, f"P/E: {pe}"))
            score += 25
        elif 0 < pe < 35:
            checks.append(("High P/E (25-35)", False, f"P/E: {pe}"))
            score += 10
        else:
            checks.append(("Very High P/E (>35)", False, f"P/E: {pe}"))
        
        # Check 2: PEG Ratio (30%)
        peg = valuation["peg_ratio"]
        if 0 < peg < 1:
            checks.append(("Undervalued (PEG < 1)", True, f"PEG: {peg}"))
            score += 30
        elif 0 < peg < 2:
            checks.append(("Fair Value (PEG 1-2)", True, f"PEG: {peg}"))
            score += 15
        else:
            checks.append(("Overvalued (PEG > 2)", False, f"PEG: {peg}"))
        
        # Check 3: Price to Book (30%)
        pb = valuation["price_to_book"]
        if 0 < pb < 3:
            checks.append(("Reasonable P/B (<3)", True, f"P/B: {pb}"))
            score += 30
        elif 0 < pb < 5:
            checks.append(("High P/B (3-5)", True, f"P/B: {pb}"))
            score += 15
        else:
            checks.append(("Very High P/B (>5)", False, f"P/B: {pb}"))
        
        return {
            "score": min(score, 100),
            "checks": checks,
            "category": "Valuation"
        }
    
    def _check_risks(self, data, news_summary):
        """
        Assess risk factors (20 points)
        """
        health = data["data"]["financial_health"]
        price = data["data"]["price_analysis"]
        
        checks = []
        score = 100  # Start at 100, deduct for risks
        
        # Check 1: Volatility Risk (25%)
        beta = price["beta"]
        if beta < 1:
            checks.append(("Low Volatility (Beta < 1)", True, f"Beta: {beta}"))
        elif beta < 1.3:
            checks.append(("Moderate Volatility (Beta 1-1.3)", True, f"Beta: {beta}"))
            score -= 10
        else:
            checks.append(("High Volatility (Beta > 1.3)", False, f"Beta: {beta}"))
            score -= 25
        
        # Check 2: Debt Risk (30%)
        debt_to_market = health["debt_to_market_cap"]
        if debt_to_market < 30:
            checks.append(("Low Debt Risk (<30%)", True, f"Debt/MCap: {debt_to_market}%"))
        elif debt_to_market < 60:
            checks.append(("Moderate Debt Risk (30-60%)", True, f"Debt/MCap: {debt_to_market}%"))
            score -= 15
        else:
            checks.append(("High Debt Risk (>60%)", False, f"Debt/MCap: {debt_to_market}%"))
            score -= 30
        
        # Check 3: News Sentiment Risk (25%)
        if news_summary and news_summary.get("success"):
            sentiment = news_summary["summary"]["overall_sentiment"]
            negative_pct = news_summary["summary"]["sentiment_distribution"]["negative_percentage"]
            
            if sentiment == "Bearish":
                checks.append(("Negative News Sentiment", False, f"Bearish: {negative_pct}% negative"))
                score -= 25
            elif sentiment == "Neutral":
                checks.append(("Neutral News Sentiment", True, f"Mixed sentiment"))
                score -= 10
            else:
                checks.append(("Positive News Sentiment", True, f"Bullish: {negative_pct}% negative"))
        
        # Check 4: Price Position Risk (20%)
        price_pos = price["price_position_in_range"]
        if price_pos > 80:
            checks.append(("Near 52-week High", False, f"At {price_pos}% of range"))
            score -= 20
        elif price_pos < 30:
            checks.append(("Near 52-week Low", True, f"At {price_pos}% of range (opportunity)"))
        else:
            checks.append(("Mid-range Price", True, f"At {price_pos}% of range"))
        
        return {
            "score": max(min(score, 100), 0),
            "checks": checks,
            "category": "Risk Assessment"
        }
    
    def _generate_verdict(self, total_score, results):
        """
        Generate final investment verdict
        """
        if total_score >= 75:
            rating = "🟢 STRONG BUY CANDIDATE"
            recommendation = "Excellent fundamentals with strong growth and manageable risk"
        elif total_score >= 60:
            rating = "🟢 BUY CANDIDATE"
            recommendation = "Good fundamentals, suitable for long-term investment"
        elif total_score >= 45:
            rating = "🟡 HOLD / RESEARCH MORE"
            recommendation = "Mixed signals, requires deeper analysis"
        elif total_score >= 30:
            rating = "🟠 AVOID FOR NOW"
            recommendation = "Weak fundamentals or high risk profile"
        else:
            rating = "🔴 STRONG AVOID"
            recommendation = "Poor fundamentals with significant risks"
        
        return {
            "rating": rating,
            "score": total_score,
            "recommendation": recommendation,
            "risk_level": self._calculate_risk_level(results)
        }
    
    def _calculate_risk_level(self, results):
        """
        Calculate overall risk level
        """
        risk_score = results["risk_assessment"]["score"]
        financial_score = results["financial_strength"]["score"]
        
        avg_safety = (risk_score + financial_score) / 2
        
        if avg_safety >= 75:
            return "Low Risk"
        elif avg_safety >= 50:
            return "Moderate Risk"
        else:
            return "High Risk"
    
    def _generate_summary(self, results):
        """
        Generate text summary of key findings
        """
        strengths = []
        weaknesses = []
        
        for category, data in results.items():
            for check_name, passed, detail in data["checks"]:
                if passed:
                    strengths.append(f"{check_name}: {detail}")
                else:
                    weaknesses.append(f"{check_name}: {detail}")
        
        return {
            "strengths": strengths[:5],  # Top 5
            "weaknesses": weaknesses[:5]  # Top 5
        }


# Integration function
def perform_intelligent_evaluation(enhanced_data, news_summary):
    """
    Main function to perform intelligent checklist evaluation
    """
    engine = IntelligentChecklistEngine()
    return engine.evaluate(enhanced_data, news_summary)