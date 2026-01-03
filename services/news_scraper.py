import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import json

class AdvancedNewsAnalyzer:
    """
    Multi-source news fetching with financial data integration
    """
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Sentiment keywords
        self.positive_keywords = [
            'growth', 'profit', 'surge', 'beat', 'exceeds', 'strong', 'up', 'gain', 'rises',
            'breakthrough', 'success', 'record', 'high', 'expansion', 'innovation', 'launch',
            'partnership', 'acquisition', 'revenue', 'earnings beat', 'outperform', 'upgrade',
            'bullish', 'rally', 'soar', 'jump', 'boost', 'positive', 'optimistic', 'confidence',
            'momentum', 'rebound', 'recover', 'improve', 'advance', 'milestone', 'achievement'
        ]
        
        self.negative_keywords = [
            'loss', 'decline', 'falls', 'drops', 'miss', 'weak', 'concern', 'risk',
            'investigation', 'lawsuit', 'layoff', 'cut', 'downgrade', 'warning', 'crisis',
            'scandal', 'fraud', 'bankruptcy', 'debt', 'failure', 'delay', 'recall', 'fine',
            'penalty', 'bearish', 'plunge', 'crash', 'slump', 'struggle', 'trouble',
            'disappointing', 'underperform', 'negative', 'worry', 'threat', 'volatile'
        ]
        
        self.neutral_keywords = [
            'announces', 'reports', 'plans', 'expects', 'meeting', 'conference',
            'update', 'statement', 'filing', 'changes', 'appoints', 'names'
        ]
    
    def fetch_and_analyze_news(self, company_name: str, ticker: str, max_items=15):
        """
        Fetch news from multiple sources with enhanced analysis
        """
        all_articles = []
        
        # Source 1: Google News
        google_news = self._fetch_google_news(company_name, max_items)
        if google_news and "error" not in google_news[0]:
            all_articles.extend(google_news)
        
        # Source 2: Yahoo Finance News
        yahoo_news = self._fetch_yahoo_finance_news(ticker, max_items // 2)
        if yahoo_news:
            all_articles.extend(yahoo_news)
        
        # Source 3: Market Events & Filings
        market_events = self._fetch_market_events(company_name, ticker)
        if market_events:
            all_articles.extend(market_events)
        
        if all_articles:
            # Remove duplicates based on title similarity
            unique_articles = self._remove_duplicates(all_articles)
            
            # Analyze each article
            analyzed_news = [self._analyze_article(article) for article in unique_articles[:max_items]]
            
            # Generate comprehensive summary
            summary = self._generate_news_summary(analyzed_news, company_name)
            
            # Get key themes
            themes = self._extract_key_themes(analyzed_news)
            
            return {
                "success": True,
                "articles": analyzed_news,
                "summary": summary,
                "key_themes": themes,
                "total_sources": len(set(a.get('source', 'Unknown') for a in analyzed_news))
            }
        else:
            return {
                "success": False,
                "articles": [],
                "summary": None,
                "key_themes": [],
                "error": "Unable to fetch news from any source"
            }
    
    def _fetch_google_news(self, company_name: str, max_items=10):
        """Fetch news from Google News"""
        try:
            query = company_name.replace(" ", "+")
            url = f"https://www.google.com/search?q={query}+stock+news&tbm=nws&hl=en"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            articles = soup.select("div.SoaBEf")
            news_list = []
            
            for article in articles[:max_items]:
                try:
                    title_elem = article.select_one("div.mCBkyc")
                    source_elem = article.select_one("div.MgUUmf")
                    time_elem = article.select_one("span.r0bn4c")
                    link_elem = article.find_parent("a")
                    
                    if title_elem and source_elem:
                        news_list.append({
                            "title": title_elem.get_text(strip=True),
                            "source": source_elem.get_text(strip=True),
                            "time": time_elem.get_text(strip=True) if time_elem else "Recently",
                            "link": link_elem["href"] if link_elem and "href" in link_elem.attrs else "#",
                            "source_type": "Google News"
                        })
                except Exception as e:
                    continue
            
            return news_list if news_list else [{"error": "No news found"}]
            
        except Exception as e:
            print(f"Google News error: {e}")
            return [{"error": f"Failed to fetch Google news: {str(e)}"}]
    
    def _fetch_yahoo_finance_news(self, ticker: str, max_items=5):
        """Fetch news from Yahoo Finance"""
        try:
            import yfinance as yf
            
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                return []
            
            news_list = []
            for item in news[:max_items]:
                try:
                    # Convert timestamp to readable format
                    pub_time = datetime.fromtimestamp(item.get('providerPublishTime', 0))
                    time_ago = self._calculate_time_ago(pub_time)
                    
                    news_list.append({
                        "title": item.get('title', 'No title'),
                        "source": item.get('publisher', 'Yahoo Finance'),
                        "time": time_ago,
                        "link": item.get('link', '#'),
                        "source_type": "Yahoo Finance"
                    })
                except Exception as e:
                    continue
            
            return news_list
            
        except Exception as e:
            print(f"Yahoo Finance news error: {e}")
            return []
    
    def _fetch_market_events(self, company_name: str, ticker: str):
        """Fetch recent market events and filings"""
        events = []
        
        try:
            import yfinance as yf
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Earnings date
            earnings_date = info.get('earningsDate')
            if earnings_date:
                try:
                    if isinstance(earnings_date, list) and len(earnings_date) > 0:
                        next_earnings = datetime.fromtimestamp(earnings_date[0])
                        if next_earnings > datetime.now():
                            events.append({
                                "title": f"Upcoming Earnings Report - {next_earnings.strftime('%B %d, %Y')}",
                                "source": "Market Calendar",
                                "time": "Scheduled",
                                "link": "#",
                                "source_type": "Market Event",
                                "event_type": "Earnings"
                            })
                except:
                    pass
            
            # Ex-dividend date
            ex_div_date = info.get('exDividendDate')
            if ex_div_date:
                try:
                    ex_div = datetime.fromtimestamp(ex_div_date)
                    if ex_div > datetime.now() - timedelta(days=30):
                        events.append({
                            "title": f"Ex-Dividend Date - {ex_div.strftime('%B %d, %Y')}",
                            "source": "Market Calendar",
                            "time": self._calculate_time_ago(ex_div),
                            "link": "#",
                            "source_type": "Market Event",
                            "event_type": "Dividend"
                        })
                except:
                    pass
            
            # Recent price movement
            current_price = info.get('currentPrice', 0)
            prev_close = info.get('previousClose', 0)
            if current_price and prev_close and abs(current_price - prev_close) / prev_close > 0.03:
                change_pct = ((current_price - prev_close) / prev_close) * 100
                direction = "surged" if change_pct > 0 else "declined"
                events.append({
                    "title": f"{company_name} stock {direction} {abs(change_pct):.2f}% in recent trading",
                    "source": "Market Data",
                    "time": "Today",
                    "link": "#",
                    "source_type": "Market Event",
                    "event_type": "Price Movement"
                })
            
        except Exception as e:
            print(f"Market events error: {e}")
        
        return events
    
    def _calculate_time_ago(self, dt):
        """Calculate human-readable time ago"""
        now = datetime.now()
        diff = now - dt
        
        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                minutes = diff.seconds // 60
                return f"{minutes} minutes ago" if minutes > 1 else "Just now"
            return f"{hours} hours ago" if hours > 1 else "1 hour ago"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} weeks ago" if weeks > 1 else "1 week ago"
        else:
            months = diff.days // 30
            return f"{months} months ago" if months > 1 else "1 month ago"
    
    def _remove_duplicates(self, articles):
        """Remove duplicate articles based on title similarity"""
        unique = []
        seen_titles = set()
        
        for article in articles:
            title = article.get('title', '').lower()
            # Create a simplified version for comparison
            title_simple = re.sub(r'[^\w\s]', '', title)[:50]
            
            if title_simple not in seen_titles:
                seen_titles.add(title_simple)
                unique.append(article)
        
        return unique
    
    def _analyze_article(self, article):
        """Analyze individual article for sentiment and category"""
        title_lower = article["title"].lower()
        
        # Calculate sentiment scores
        positive_score = sum(1 for keyword in self.positive_keywords if keyword in title_lower)
        negative_score = sum(1 for keyword in self.negative_keywords if keyword in title_lower)
        
        # Determine overall sentiment
        if positive_score > negative_score:
            sentiment = "Positive"
            sentiment_emoji = "📈"
            sentiment_color = "success"
        elif negative_score > positive_score:
            sentiment = "Negative"
            sentiment_emoji = "📉"
            sentiment_color = "danger"
        else:
            sentiment = "Neutral"
            sentiment_emoji = "➖"
            sentiment_color = "secondary"
        
        # Categorize news
        category = self._categorize_news(title_lower)
        
        # Calculate recency score
        recency = self._calculate_recency(article["time"])
        
        # Calculate importance
        importance = self._calculate_importance(positive_score, negative_score, recency, category)
        
        return {
            **article,
            "sentiment": sentiment,
            "sentiment_emoji": sentiment_emoji,
            "sentiment_color": sentiment_color,
            "sentiment_score": {
                "positive": positive_score,
                "negative": negative_score
            },
            "category": category,
            "recency": recency,
            "importance": importance
        }
    
    def _categorize_news(self, title_lower):
        """Categorize news into different types"""
        categories = {
            "Earnings": ['earnings', 'revenue', 'profit', 'quarterly', 'annual report', 'results', 'q1', 'q2', 'q3', 'q4'],
            "Product": ['launch', 'product', 'release', 'unveils', 'introduces', 'new'],
            "Market": ['market', 'stock', 'shares', 'trading', 'price', 'rally', 'surge', 'drop'],
            "Leadership": ['ceo', 'cfo', 'executive', 'appoints', 'resigns', 'board', 'management'],
            "Legal": ['lawsuit', 'investigation', 'regulatory', 'sec', 'fine', 'settlement', 'court'],
            "M&A": ['acquisition', 'merger', 'acquires', 'buys', 'deal', 'takeover', 'buyout'],
            "Strategy": ['expansion', 'partnership', 'collaboration', 'strategic', 'plans', 'investment'],
            "Operations": ['layoff', 'hiring', 'restructuring', 'plant', 'facility', 'production'],
            "Analyst": ['upgrade', 'downgrade', 'rating', 'analyst', 'target', 'price target'],
            "Dividend": ['dividend', 'payout', 'distribution', 'shareholder']
        }
        
        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return "General"
    
    def _calculate_recency(self, time_str):
        """Calculate recency score based on time string"""
        time_lower = time_str.lower()
        
        if 'just now' in time_lower or 'minute' in time_lower:
            return 10
        elif 'hour' in time_lower:
            return 9
        elif 'today' in time_lower or 'yesterday' in time_lower:
            return 8
        elif 'day' in time_lower:
            match = re.search(r'(\d+)', time_lower)
            if match:
                days = int(match.group(1))
                if days <= 3:
                    return 7
                elif days <= 7:
                    return 6
                else:
                    return 4
            return 6
        elif 'week' in time_lower:
            return 4
        elif 'month' in time_lower:
            return 2
        else:
            return 1
    
    def _calculate_importance(self, positive_score, negative_score, recency, category):
        """Calculate overall importance score"""
        sentiment_weight = max(positive_score, negative_score) * 3
        
        # Category weights
        category_weights = {
            "Earnings": 5,
            "M&A": 4,
            "Legal": 4,
            "Analyst": 3,
            "Leadership": 3,
            "Product": 2,
            "Market": 2
        }
        
        category_weight = category_weights.get(category, 1)
        
        total = sentiment_weight + recency + category_weight
        
        if total >= 18:
            return "Critical"
        elif total >= 12:
            return "High"
        elif total >= 7:
            return "Medium"
        else:
            return "Low"
    
    def _generate_news_summary(self, analyzed_articles, company_name):
        """Generate comprehensive summary statistics"""
        if not analyzed_articles:
            return None
        
        total = len(analyzed_articles)
        positive = sum(1 for a in analyzed_articles if a["sentiment"] == "Positive")
        negative = sum(1 for a in analyzed_articles if a["sentiment"] == "Negative")
        neutral = sum(1 for a in analyzed_articles if a["sentiment"] == "Neutral")
        
        # Calculate overall sentiment
        sentiment_score = positive - negative
        if sentiment_score > 3:
            overall_sentiment = "Strongly Bullish"
            overall_emoji = "🚀"
        elif sentiment_score > 0:
            overall_sentiment = "Bullish"
            overall_emoji = "🐂"
        elif sentiment_score < -3:
            overall_sentiment = "Strongly Bearish"
            overall_emoji = "⚠️"
        elif sentiment_score < 0:
            overall_sentiment = "Bearish"
            overall_emoji = "🐻"
        else:
            overall_sentiment = "Neutral"
            overall_emoji = "➖"
        
        # Category distribution
        categories = {}
        for article in analyzed_articles:
            cat = article["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        # Get critical and high importance news
        critical_news = [a for a in analyzed_articles if a["importance"] in ["Critical", "High"]]
        
        # Recent news (last 24-48 hours)
        recent_news = [a for a in analyzed_articles if a["recency"] >= 8]
        
        return {
            "company_name": company_name,
            "total_articles": total,
            "sentiment_distribution": {
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
                "positive_percentage": round((positive / total) * 100, 1),
                "negative_percentage": round((negative / total) * 100, 1),
                "neutral_percentage": round((neutral / total) * 100, 1)
            },
            "overall_sentiment": overall_sentiment,
            "overall_emoji": overall_emoji,
            "sentiment_score": sentiment_score,
            "category_distribution": categories,
            "most_common_category": max(categories, key=categories.get) if categories else "N/A",
            "critical_news_count": len(critical_news),
            "critical_articles": critical_news[:5],
            "recent_news_count": len(recent_news),
            "recent_articles": recent_news[:5]
        }
    
    def _extract_key_themes(self, analyzed_articles):
        """Extract key themes from news articles"""
        themes = []
        
        # Theme patterns
        theme_patterns = {
            "Growth & Expansion": ['growth', 'expansion', 'new market', 'international'],
            "Financial Performance": ['earnings', 'revenue', 'profit', 'margin'],
            "Strategic Moves": ['acquisition', 'partnership', 'merger', 'collaboration'],
            "Operational Changes": ['restructuring', 'layoff', 'hiring', 'efficiency'],
            "Market Sentiment": ['upgrade', 'downgrade', 'bullish', 'bearish'],
            "Regulatory Issues": ['investigation', 'lawsuit', 'regulatory', 'compliance'],
            "Innovation": ['launch', 'product', 'innovation', 'technology']
        }
        
        theme_counts = {}
        for theme, keywords in theme_patterns.items():
            count = 0
            for article in analyzed_articles:
                title_lower = article["title"].lower()
                if any(keyword in title_lower for keyword in keywords):
                    count += 1
            if count > 0:
                theme_counts[theme] = count
        
        # Sort by frequency
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [{"theme": theme, "count": count} for theme, count in sorted_themes[:5]]


def fetch_advanced_news(company_name: str, ticker: str, max_items=15):
    """Main function for integration"""
    analyzer = AdvancedNewsAnalyzer()
    return analyzer.fetch_and_analyze_news(company_name, ticker, max_items)