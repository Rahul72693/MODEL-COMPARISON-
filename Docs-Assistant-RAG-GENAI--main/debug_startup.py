import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

load_dotenv()

from backend.database import init_db
from backend.llm_providers import GeminiProvider, GroqProvider
from backend.comparison import ComparisonEngine
from backend.evaluation import MetricsEvaluator

def test_startup():
    print("Testing startup...")
    try:
        # 1. Database
        init_db()
        print("✅ Database initialized")
        
        # 2. Providers
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
        
        if GEMINI_API_KEY:
            gemini_provider = GeminiProvider(GEMINI_API_KEY, "gemini-2.0-flash")
            print("✅ Gemini provider initialized")
        else:
            print("⚠️ GEMINI_API_KEY not set")
            
        if GROQ_API_KEY:
            groq_provider = GroqProvider(GROQ_API_KEY, "llama-3.3-70b-versatile")
            print("✅ Groq provider initialized")
        else:
            print("⚠️ GROQ_API_KEY not set")
            
        # 3. Comparison Engine
        if 'gemini_provider' in locals() and 'groq_provider' in locals():
            comparison_engine = ComparisonEngine(gemini_provider, groq_provider)
            print("✅ Comparison engine initialized")
            
        # 4. Metrics Evaluator
        metrics_evaluator = MetricsEvaluator()
        print("✅ Metrics evaluator initialized")
        
        print("🚀 Startup test successful!")
    except Exception as e:
        print(f"❌ Startup test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_startup()
