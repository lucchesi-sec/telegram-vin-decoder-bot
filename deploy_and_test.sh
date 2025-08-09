#!/bin/bash

echo "Deploying VinBot with CarsXE client fixes..."
echo "============================================"

# Deploy to Fly.io
echo "1. Deploying to Fly.io..."
fly deploy

# Wait for deployment to complete
echo "2. Waiting for deployment to stabilize (30 seconds)..."
sleep 30

# Check deployment status
echo "3. Checking deployment status..."
fly status

# Copy and run debug script in production
echo "4. Testing API connection from production..."
fly ssh console -C "cat > /tmp/test_api.py << 'EOF'
import httpx
import os
import asyncio

async def test():
    api_key = os.getenv('CARSXE_API_KEY')
    if not api_key:
        print('ERROR: No API key found')
        return
    
    url = 'https://api.carsxe.com/specs'
    params = {'key': api_key, 'vin': '1HGBH41JXMN109186'}
    
    print(f'Testing {url}...')
    
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(url, params=params, headers={'Accept': 'application/json'})
            print(f'Status: {resp.status_code}')
            print(f'Content-Type: {resp.headers.get(\"content-type\")}')
            if resp.text.startswith('<'):
                print('ERROR: HTML response received!')
                print(f'Preview: {resp.text[:200]}')
            else:
                print('SUCCESS: JSON response received')
                data = resp.json()
                if data.get('success'):
                    print(f'VIN decoded: {data.get(\"attributes\", {}).get(\"make\")}')
        except Exception as e:
            print(f'Error: {e}')

asyncio.run(test())
EOF
python /tmp/test_api.py"

# Check logs
echo "5. Checking recent logs..."
fly logs --limit 50

echo ""
echo "Deployment complete! Check the output above for any errors."
echo "To test the bot, send a VIN to your Telegram bot."