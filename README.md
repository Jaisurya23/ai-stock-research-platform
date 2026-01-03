# 🤖 AI Stock Research Platform

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> An intelligent, AI-powered stock research and analysis platform that provides comprehensive financial insights, news sentiment analysis, and investment recommendations in seconds.

![Platform Preview](docs/images/hero-screenshot.png)

## ✨ Features

### 🔍 **Comprehensive Stock Analysis**
- **25+ Key Financial Metrics** - P/E, PEG, ROE, ROIC, debt ratios, and more
- **Multi-dimensional Evaluation** - Business quality, financial strength, growth potential, valuation, and risk assessment
- **Historical Trend Analysis** - 3-year CAGR calculations for revenue and earnings
- **Real-time Price Data** - Current prices, 52-week ranges, and technical indicators

### 📰 **Advanced News Intelligence**
- **Multi-source News Aggregation** - Google News, Yahoo Finance, and market events
- **AI-powered Sentiment Analysis** - Bullish, bearish, or neutral classification
- **News Categorization** - Earnings, M&A, legal, product launches, and more
- **Importance Scoring** - Critical, high, medium, and low priority news
- **Recency Tracking** - Time-weighted news relevance

### 🎯 **Intelligent Checklist Engine**
- **Weighted Scoring System** - 100-point comprehensive evaluation
- **5 Key Categories**:
  - Business Quality (20%)
  - Financial Strength (25%)
  - Growth Potential (20%)
  - Valuation (15%)
  - Risk Assessment (20%)
- **Smart Verdicts** - Strong Buy, Buy, Hold, Avoid recommendations
- **Risk Profiling** - Low, moderate, or high-risk classification

### 🤖 **AI-Powered Insights**
- **Gemini AI Integration** - Deep analysis using Google's Gemini 1.5 Flash
- **Contextual Recommendations** - Personalized investment suggestions
- **Scenario Analysis** - Bull, base, and bear case evaluations
- **Comprehensive Reports** - Professional-grade research documents

### 💾 **Data Management**
- **Research History** - Save and access all previous reports
- **SQLite Database** - Lightweight, fast, and reliable storage
- **Export Functionality** - Download reports as text files
- **Search & Filter** - Find specific companies quickly

### 🎨 **Modern User Interface**
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Bootstrap 5** - Clean, professional, and intuitive
- **Real-time Loading** - Progress indicators and status updates
- **Dark/Light Compatible** - Comfortable viewing experience

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-stock-research-platform.git
   cd ai-stock-research-platform
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your Gemini API key
   # GEMINI_API_KEY=your_api_key_here
   ```

5. **Initialize the database**
   ```bash
   python db_init.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Open your browser**
   Navigate to `http://localhost:5000`

## 📖 Usage

### Analyzing a Stock

1. **Enter a ticker symbol or company name**
   - US stocks: `AAPL`, `MSFT`, `GOOGL`
   - Indian stocks: `TCS.NS`, `RELIANCE.NS`, `HDFCBANK.NS`
   - Or use company names: `Apple`, `Microsoft`, `Reliance`

2. **Click "Generate Research Report"**
   - The platform fetches real-time financial data
   - Analyzes recent news and sentiment
   - Runs intelligent checklist evaluation
   - Generates AI-powered insights

3. **Review the comprehensive report**
   - **Summary Tab**: Quick overview with verdict and scores
   - **Full Report Tab**: Complete detailed analysis
   - **Key Metrics Tab**: Financial metrics by category

4. **Export or save**
   - Download as text file
   - Print the report
   - Access from history anytime

### Supported Markets

- 🇺🇸 **US Markets** - NYSE, NASDAQ
- 🇮🇳 **Indian Markets** - NSE, BSE
- 🌍 **Global Markets** - Major international exchanges

## 🏗️ Project Structure

```
ai-stock-research-platform/
│
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── db_init.py                  # Database initialization
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
│
├── services/                  # Business logic services
│   ├── yfinance_service.py   # Enhanced financial data fetcher
│   ├── news_scraper.py       # Multi-source news aggregator
│   └── gemini_client.py      # AI report generator
│
├── analysis/                  # Analysis engines
│   └── checklist_engine.py   # Intelligent evaluation system
│
├── prompts/                   # AI prompts
│   └── system_prompt.txt     # Gemini system instructions
│
├── database/                  # SQLite database
│   └── research.db           # Research history storage
│
├── static/                    # Static assets
│   ├── css/
│   │   └── style.css         # Custom styles
│   └── js/
│       └── main.js           # Client-side scripts
│
└── templates/                 # HTML templates
    ├── base.html             # Base template
    ├── home.html             # Landing page
    ├── report.html           # Report viewer
    ├── history.html          # History page
    └── error.html            # Error page
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DATABASE_PATH=database/research.db

# API Keys
GEMINI_API_KEY=your-gemini-api-key-here

# API Configuration
API_TIMEOUT=30
MAX_RETRIES=3

# News Configuration
MAX_NEWS_ARTICLES=15
NEWS_CACHE_DURATION=3600

# Report Configuration
MAX_REPORT_HISTORY=100
```

### Customization

- **Modify checklist weights** in `analysis/checklist_engine.py`
- **Adjust AI prompts** in `prompts/system_prompt.txt`
- **Customize UI** in `static/css/style.css`
- **Change news sources** in `services/news_scraper.py`

## 📊 Key Metrics Analyzed

### Valuation Metrics
- P/E Ratio, Forward P/E, PEG Ratio
- Price/Book, Price/Sales
- EV/EBITDA, EV/Revenue
- Enterprise Value

### Growth Metrics
- Revenue 3Y CAGR
- Earnings 3Y CAGR
- QoQ Revenue & Earnings Growth
- Revenue Trend Analysis

### Profitability Metrics
- ROE, ROA, ROIC
- Profit Margin, Operating Margin
- Gross Margin
- Efficiency Ratios

### Financial Health
- Current Ratio, Quick Ratio
- Debt/Equity, Debt/Market Cap
- Free Cash Flow
- Interest Coverage

### Risk Indicators
- Beta (Volatility)
- Price Position in 52-Week Range
- News Sentiment
- Debt Levels

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

## 🐛 Known Issues & Limitations

- **Rate Limits**: Yahoo Finance and Google News may rate-limit requests
- **Data Accuracy**: Financial data depends on third-party sources
- **News Coverage**: Limited to English language news
- **Historical Data**: Some metrics require sufficient historical data
- **API Costs**: Gemini API has usage limits on free tier

## 🔮 Roadmap

- [ ] **PDF Export** - Generate downloadable PDF reports
- [ ] **Email Alerts** - Price and news alerts
- [ ] **Portfolio Tracking** - Track multiple stocks
- [ ] **Comparison Tool** - Compare multiple companies
- [ ] **Technical Analysis** - Charts and technical indicators
- [ ] **Fundamental Screener** - Filter stocks by criteria
- [ ] **Watchlist** - Save favorite stocks
- [ ] **Mobile App** - Native iOS/Android apps
- [ ] **API Access** - RESTful API for developers
- [ ] **Multi-language** - Support for multiple languages

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This platform is for **educational and research purposes only**. It does NOT constitute:

- Investment advice
- Financial advice
- Trading advice
- Professional recommendations

**Important Notes:**
- Always conduct your own due diligence
- Consult with qualified financial advisors
- Past performance does not guarantee future results
- All investments carry risk, including potential loss of principal
- Market conditions can change rapidly

## 🙏 Acknowledgments

- **yfinance** - Yahoo Finance data library
- **Google Gemini AI** - AI-powered analysis
- **Beautiful Soup** - Web scraping
- **Flask** - Web framework
- **Bootstrap** - UI components
- **Font Awesome** - Icons

## 📞 Support
- **Email**: jaisurya230904@gmail.com

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/ai-stock-research-platform&type=Date)](https://star-history.com/#yourusername/ai-stock-research-platform&Date)

---

**Made with ❤️ by [Jaisurya](https://github.com/yourusername)**

If you find this project helpful, please consider giving it a ⭐ on GitHub!