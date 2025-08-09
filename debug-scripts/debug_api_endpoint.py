#!/usr/bin/env python3
"""
Debug script to test CarsXE API endpoint directly with detailed logging
"""
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_endpoint():
    api_key = os.getenv("CARSXE_API_KEY")
    if not api_key:
        print("CARSXE_API_KEY not found in environment")
        return
    
    vin = "1HGBH41JXMN109186"
    
    # Test 1: Direct GET request with params
    print("=" * 60)
    print("TEST 1: GET with query params")
    url = "https://api.carsxe.com/specs"
    params = {"key": api_key, "vin": vin}
    
    try:
        with httpx.Client() as client:
            response = client.get(url, params=params, headers={"Accept": "application/json"})
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Content Type: {response.headers.get('content-type')}")
            print(f"Response (first 500 chars): {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Try with different User-Agent
    print("\n" + "=" * 60)
    print("TEST 2: GET with custom User-Agent")
    
    try:
        with httpx.Client() as client:
            response = client.get(
                url, 
                params=params, 
                headers={
                    "Accept": "application/json",
                    "User-Agent": "VinBot/1.0"
                }
            )
            print(f"Status: {response.status_code}")
            print(f"Content Type: {response.headers.get('content-type')}")
            print(f"Response (first 500 chars): {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Try POST method (in case API changed)
    print("\n" + "=" * 60)
    print("TEST 3: POST with JSON body")
    
    try:
        with httpx.Client() as client:
            response = client.post(
                url,
                json={"key": api_key, "vin": vin},
                headers={"Accept": "application/json"}
            )
            print(f"Status: {response.status_code}")
            print(f"Content Type: {response.headers.get('content-type')}")
            print(f"Response (first 500 chars): {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoint()