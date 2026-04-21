"""Test script for the comparison API."""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint."""
    print("\n" + "="*50)
    print("Testing /health endpoint...")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_extract():
    """Test document extraction."""
    print("\n" + "="*50)
    print("Testing /extract endpoint...")
    print("="*50)
    
    # Use existing test document
    doc_path = "Research on Non-alcoholic Fatty Liver Disease.pdf"
    
    try:
        with open(doc_path, "rb") as f:
            files = {"file": (doc_path, f, "application/pdf")}
            response = requests.post(f"{BASE_URL}/extract", files=files)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.json()
    except FileNotFoundError:
        print(f"⚠️ Test document not found: {doc_path}")
        print("Skipping extraction test")
        return None

def test_compare():
    """Test comparison endpoint."""
    print("\n" + "="*50)
    print("Testing /compare endpoint...")
    print("="*50)
    
    payload = {
        "session_id": "test-session-123",
        "message": "What is NAFLD?"
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/compare", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n--- GEMINI RESPONSE ---")
            print(f"Answer: {data['gemini']['answer'][:200]}...")
            print(f"Response Time: {data['gemini']['response_time']:.3f}s")
            print(f"Tokens: {data['gemini']['tokens']}")
            print(f"Cost: ${data['gemini']['cost']:.6f}")
            
            print("\n--- GROQ RESPONSE ---")
            print(f"Answer: {data['groq']['answer'][:200]}...")
            print(f"Response Time: {data['groq']['response_time']:.3f}s")
            print(f"Tokens: {data['groq']['tokens']}")
            print(f"Cost: ${data['groq']['cost']:.6f}")
            
            print("\n--- COMPARISON METRICS ---")
            print(f"Agreement Score: {data['comparison']['agreement_score']:.3f}")
            print(f"Gemini Faster: {data['comparison']['gemini_faster']}")
            print(f"Speed Ratio: {data['comparison']['speed_ratio']:.2f}x")
            print(f"Gemini Quality: {data['comparison']['gemini_quality_avg']:.3f}")
            print(f"Groq Quality: {data['comparison']['groq_quality_avg']:.3f}")
            
            return data
        else:
            print(f"Error: {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_metrics_summary():
    """Test metrics summary endpoint."""
    print("\n" + "="*50)
    print("Testing /metrics/summary endpoint...")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/metrics/summary?session_id=test-session-123")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_metrics_history():
    """Test metrics history endpoint."""
    print("\n" + "="*50)
    print("Testing /metrics/history endpoint...")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/metrics/history?limit=10")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['count']} evaluation runs")
        if data['count'] > 0:
            print(f"\nLatest run:")
            print(json.dumps(data['history'][0], indent=2))
    else:
        print(f"Error: {response.text}")
    
    return response.json() if response.status_code == 200 else None

def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("🧪 TESTING MODEL COMPARISON API")
    print("="*70)
    
    # Test 1: Health check
    health = test_health()
    
    if not health.get("gemini_ready"):
        print("\n⚠️ WARNING: Gemini not ready!")
    if not health.get("groq_ready"):
        print("\n⚠️ WARNING: Groq not ready! Please add GROQ_API_KEY to .env file")
    
    # Test 2: Extract document (optional)
    # test_extract()
    
    # Test 3: Compare models
    if health.get("comparison_ready"):
        test_compare()
        
        # Test 4: Get metrics summary
        test_metrics_summary()
        
        # Test 5: Get history
        test_metrics_history()
    else:
        print("\n⚠️ Skipping comparison tests - comparison engine not ready")
    
    print("\n" + "="*70)
    print("✅ TESTING COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    main()
