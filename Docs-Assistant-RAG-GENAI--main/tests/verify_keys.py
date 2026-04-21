import os
from dotenv import load_dotenv
from google import genai
from groq import Groq

load_dotenv()

def test_gemini():
    print("Testing Gemini...")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Gemini API Key not found")
        return
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Hello, are you working?"
        )
        print(f"✅ Gemini Response: {response.text[:50]}...")
    except Exception as e:
        print(f"❌ Gemini Error: {e}")

def test_groq():
    print("\nTesting Groq...")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ Groq API Key not found")
        return
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Hello, are you working?"}]
        )
        print(f"✅ Groq Response: {response.choices[0].message.content[:50]}...")
    except Exception as e:
        print(f"❌ Groq Error: {e}")

if __name__ == "__main__":
    test_gemini()
    test_groq()
