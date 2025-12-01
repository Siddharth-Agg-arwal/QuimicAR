"""
Simple test script for the Chemistry AR API
"""
import requests
import sys

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/")
        print(f"[OK] Health check: {response.json()}")
        return True
    except Exception as e:
        print(f"[FAIL] Health check failed: {e}")
        return False

def test_get_levels():
    """Test the levels endpoint"""
    try:
        response = requests.get("http://localhost:8000/levels")
        print(f"[OK] Levels info: {response.json()}")
        return True
    except Exception as e:
        print(f"[FAIL] Get levels failed: {e}")
        return False

def test_set_level():
    """Test setting a level"""
    try:
        response = requests.post("http://localhost:8000/set_level/1")
        print(f"[OK] Set level: {response.json()}")
        return True
    except Exception as e:
        print(f"[FAIL] Set level failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Chemistry AR API...")
    print("-" * 50)
    
    results = []
    results.append(test_health_check())
    results.append(test_get_levels())
    results.append(test_set_level())
    
    print("-" * 50)
    if all(results):
        print("[OK] All tests passed!")
        sys.exit(0)
    else:
        print("[FAIL] Some tests failed")
        sys.exit(1)
