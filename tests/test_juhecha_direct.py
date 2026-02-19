import asyncio
import sys
import os
sys.path.append('backend')
os.environ['ENV'] = 'development'

async def test_juhecha():
    from app.services.juhecha_service import juhecha_service
    print(f"Enterprise token: {juhecha_service.enterprise_token[:10]}...")
    print(f"Has valid enterprise token: {juhecha_service._has_valid_enterprise_token()}")
    
    # Test search
    result = await juhecha_service.search_enterprise_info("装修公司", 5)
    print(f"Search result type: {type(result)}")
    print(f"Search result length: {len(result)}")
    
    if result:
        print("First 3 companies:")
        for i, company in enumerate(result[:3]):
            print(f"  {i+1}. {company.get('name', 'N/A')}")
    else:
        print("No results returned")
    
    # Test with a more specific company
    result2 = await juhecha_service.search_enterprise_info("阿里巴巴", 5)
    print(f"\n'Alibaba' search result length: {len(result2)}")
    if result2:
        print("First 3 companies for '阿里巴巴':")
        for i, company in enumerate(result2[:3]):
            print(f"  {i+1}. {company.get('name', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(test_juhecha())
