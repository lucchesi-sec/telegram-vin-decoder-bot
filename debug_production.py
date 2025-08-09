#!/usr/bin/env python3
"""
Debug script to test CarsXE API from production environment
Run this on Fly.io: fly ssh console -C "python debug_production.py"
"""
import httpx
import os
import asyncio
import json

async def test_production():
    api_key = os.getenv("CARSXE_API_KEY")
    print(f"Environment: Production (Fly.io)")
    print(f"API Key present: {'Yes' if api_key else 'No'}")
    
    if not api_key:
        print("ERROR: CARSXE_API_KEY not found!")
        return
    
    vin = "1HGBH41JXMN109186"
    url = "https://api.carsxe.com/specs"
    
    print(f"\nTesting VIN: {vin}")
    print(f"Endpoint: {url}")
    
    # Test with async client (same as bot uses)
    async with httpx.AsyncClient(timeout=15) as client:
        print("\n" + "=" * 60)
        print("TEST 1: Async GET (same as bot)")
        
        params = {"key": api_key, "vin": vin}
        headers = {"Accept": "application/json"}
        
        try:
            response = await client.get(url, params=params, headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            # Check if HTML response
            if response.text.strip().startswith("<"):
                print("ERROR: Received HTML response!")
                print(f"Response preview: {response.text[:500]}")
                
                # Try to extract any useful info from HTML
                if "cloudflare" in response.text.lower():
                    print("\nPOSSIBLE ISSUE: Cloudflare blocking detected")
                elif "next" in response.text.lower() or "_next" in response.text:
                    print("\nPOSSIBLE ISSUE: Being redirected to a Next.js app")
            else:
                print("Success: JSON response received")
                try:
                    data = response.json()
                    print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'non-dict'}")
                    if isinstance(data, dict) and data.get("success"):
                        print(f"VIN decoded successfully: {data.get('attributes', {}).get('make', 'Unknown')}")
                except:
                    print(f"Response text: {response.text[:500]}")
                    
        except Exception as e:
            print(f"Error: {e}")
    
    # Test with sync client and different headers
    print("\n" + "=" * 60)
    print("TEST 2: Sync GET with full browser headers")
    
    with httpx.Client(timeout=15) as client:
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        
        try:
            response = client.get(url, params=params, headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            if response.text.strip().startswith("<"):
                print("ERROR: Still receiving HTML!")
                print(f"Headers received: {dict(response.headers)}")
            else:
                print("Success with browser headers")
                
        except Exception as e:
            print(f"Error: {e}")
    
    # Test DNS resolution
    print("\n" + "=" * 60)
    print("TEST 3: DNS and connectivity check")
    
    import socket
    try:
        ip = socket.gethostbyname("api.carsxe.com")
        print(f"api.carsxe.com resolves to: {ip}")
    except Exception as e:
        print(f"DNS resolution failed: {e}")
    
    # Test with curl command
    print("\n" + "=" * 60)
    print("TEST 4: Raw curl command")
    
    import subprocess
    try:
        cmd = f'curl -s "https://api.carsxe.com/specs?key={api_key}&vin={vin}" -H "Accept: application/json" | head -c 500'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Curl output: {result.stdout}")
        if result.stderr:
            print(f"Curl errors: {result.stderr}")
    except Exception as e:
        print(f"Curl failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_production())