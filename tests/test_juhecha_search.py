import asyncio
import sys
sys.path.append('backend')
from app.core.config import settings
from app.services.juhecha_service import juhecha_service

async def test_search():
    print(f"Enterprise token: {juhecha_service.enterprise_token[:10] if juhecha_service.enterprise_token else 'None'}")
    print(f"Has valid enterprise token: {juhecha_service._has_valid_enterprise_token()}")
    
    # Test search
    result = await juhecha_service.search_enterprise_info("装修公司", 5)
    print(f"Search result: {result}")
    print(f"Number of results: {len(result)}")
    
    if result:
        for i, company in enumerate(result[:3]):
            print(f"  {i+1}. {company.get('name', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(test_search())
