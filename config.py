import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database Configuration
    DATABASE_PATH = os.getenv("DATABASE_PATH", "database/research.db")
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # API Configuration
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    # News Configuration
    MAX_NEWS_ARTICLES = int(os.getenv("MAX_NEWS_ARTICLES", "15"))
    NEWS_CACHE_DURATION = int(os.getenv("NEWS_CACHE_DURATION", "3600"))  # 1 hour
    
    # Report Configuration
    MAX_REPORT_HISTORY = int(os.getenv("MAX_REPORT_HISTORY", "100"))
    
    @staticmethod
    def validate():
        """Validate critical configuration"""
        issues = []
        
        if not Config.GEMINI_API_KEY:
            issues.append("⚠️  GEMINI_API_KEY not configured. AI analysis will not work.")
            issues.append("   Set it in .env file: GEMINI_API_KEY=your_key_here")
        
        if not os.path.exists("database"):
            issues.append("⚠️  Database directory not found. Creating...")
            os.makedirs("database", exist_ok=True)
        
        if not os.path.exists(Config.DATABASE_PATH):
            issues.append("⚠️  Database file not found. Run db_init.py to create it.")
        
        return issues
    
    @staticmethod
    def print_config():
        """Print current configuration (for debugging)"""
        print("\n" + "="*60)
        print("📋 APPLICATION CONFIGURATION")
        print("="*60)
        print(f"DEBUG MODE: {Config.DEBUG}")
        print(f"DATABASE: {Config.DATABASE_PATH}")
        print(f"GEMINI API: {'✅ Configured' if Config.GEMINI_API_KEY else '❌ Not configured'}")
        print(f"MAX NEWS ARTICLES: {Config.MAX_NEWS_ARTICLES}")
        print(f"API TIMEOUT: {Config.API_TIMEOUT}s")
        print("="*60 + "\n")
        
        # Validate and show issues
        issues = Config.validate()
        if issues:
            print("⚠️  Configuration Issues:")
            for issue in issues:
                print(issue)
            print()


# Create .env.example file content
ENV_EXAMPLE = """# Flask Configuration
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
"""

# Create .env.example if it doesn't exist
if __name__ == "__main__":
    if not os.path.exists(".env.example"):
        with open(".env.example", "w") as f:
            f.write(ENV_EXAMPLE)
        print("✅ Created .env.example file")
    
    # Print current config
    Config.print_config()
    
    # Check for .env file
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. Creating from example...")
        with open(".env", "w") as f:
            f.write(ENV_EXAMPLE)
        print("✅ Created .env file. Please update it with your API keys!")
    
    issues = Config.validate()
    if not issues:
        print("✅ All configuration checks passed!")
    else:
        print("\n⚠️  Please fix the issues above before running the application.")