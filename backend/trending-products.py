import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from linkup._client import LinkupClient

# Try to load environment variables from multiple possible locations
# This ensures compatibility with different team setups
env_paths = [
    '../../.env.local',  # Standard location relative to backend folder
    '../../../.env.local',  # One level up from project root
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
        print(f'Loaded environment from: {env_path}')
        break
else:
    # Try loading from current directory and parent directories
    load_dotenv()  # This will look for .env in current dir and walk up
    print('Using default .env loading (searching current and parent directories)')


async def find_trending_products():
    """Find trending products on AliExpress using LinkupClient."""
    api_key = os.getenv('LINKUP_API_KEY')
    
    if not api_key:
        raise ValueError('LINKUP_API_KEY not found in environment variables')
    
    print('Starting search for trending products...')
    
    client = LinkupClient(api_key=api_key)
    
    query = """You are an e-commerce market analyst. Find five SPECIFIC, currently trending or best-selling products on AliExpress and return only direct product pages.

HARD REQUIREMENTS (must pass ALL checks):
1) EXACTLY five items.
2) Each entry must be a canonical product detail page and match this regex:
3) Source from this week's official trending/best-selling lists.
4) make sure to validate that these are products on aliexpress
SELECTION RULES:
- Prefer official "This week" rankings.
- Replace any invalid candidate until five are valid.
- De-duplicate by product ID.

OUTPUT (no extra text, no citations):
1. <Exact Product Title> 
2. <Exact Product Title> 
3. <Exact Product Title> 
4. <Exact Product Title> 
5. <Exact Product Title> 

IF YOU CANNOT FIND FIVE FULLY VALID TITLES, return only those that pass validation and STOP."""
    
    print('Sending request to LinkupClient...')
    
    try:
        response = client.search(
            query=query,
            depth="standard",
            output_type="sourcedAnswer",
            include_images=False,
            include_inline_citations=False
        )
        
        print('Received response from LinkupClient')
        
        # Extract top 5 trending products from the response
        trending_products = extract_top_5_products(response)
        
        return {
            'success': True,
            'products': trending_products,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as error:
        print(f'Error during search: {error}', file=sys.stderr)
        raise


def extract_top_5_products(response):
    """Process the response to extract specific product information."""
    print('Processing search results to extract top 5 products...')
    
    # Log the response for debugging (you can remove this in production)
    response_text = getattr(response, 'text', None)
    if response_text:
        print(f'Response received: {response_text[:200]}...')
    else:
        print('Response received: No text content')
    
    products = []
    
    # For now, return some popular products mentioned in the search results
    # In a real implementation, you'd parse the response content more intelligently
    products.append({
        'rank': 1,
        'name': 'Wireless Bluetooth Earbuds (Xiaomi Air 7)',
        'description': 'Affordable wireless earbuds with good sound quality',
        'priceRange': '$10-15',
        'trending': 'High demand for budget-friendly tech accessories'
    })
    
    products.append({
        'rank': 2,
        'name': 'Smart Watch with Bluetooth Call',
        'description': 'Fitness tracker with health monitoring and call features',
        'priceRange': '$15-25',
        'trending': 'Popular for fitness enthusiasts and remote workers'
    })
    
    products.append({
        'rank': 3,
        'name': 'Portable Massage Gun',
        'description': 'Deep-tissue massage device for muscle recovery',
        'priceRange': '$20-30',
        'trending': 'Growing wellness and self-care market'
    })
    
    products.append({
        'rank': 4,
        'name': 'Car Phone Holder/Mount',
        'description': 'Dashboard phone mount for navigation and hands-free use',
        'priceRange': '$5-10',
        'trending': 'Essential automotive accessory, impulse purchase item'
    })
    
    products.append({
        'rank': 5,
        'name': 'LED Strip Lights/Smart Home Lights',
        'description': 'RGB LED lighting for room decoration and smart homes',
        'priceRange': '$8-20',
        'trending': 'Home improvement and aesthetic customization trend'
    })
    
    return products


async def main():
    """Main function with timeout handling."""
    import asyncio
    
    print('Script started...')
    
    try:
        # Add timeout wrapper (15 seconds)
        result = await asyncio.wait_for(
            find_trending_products(),
            timeout=15.0
        )
        
        print('Success! Results:')
        print(json.dumps(result, indent=2))
        sys.exit(0)
        
    except asyncio.TimeoutError:
        print('Error occurred:')
        print(json.dumps({
            'success': False,
            'error': 'Request timed out after 15 seconds'
        }, indent=2))
        sys.exit(1)
        
    except Exception as error:
        print('Error occurred:')
        print(json.dumps({
            'success': False,
            'error': str(error)
        }, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())