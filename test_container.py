import asyncio
import sys
sys.path.append('/app')

async def test():
    from app.services.juhecha_service import juhecha_service
    print(f"Enterprise token: {juhecha_service.enterprise_token[:10]}...")
    print(f"Has valid enterprise token: {juhecha_service._has_valid_enterprise_token()}")
    
    result = await juhecha_service.search_enterprise_info("装修公司", 3)
    print(f"Result length: {len(result)}")
    
    if result:
        print("Companies found:")
        for i, company in enumerate(result[:3]):
            print(f"  {i+1}. {company.get('name', 'N/A')}")
    else:
        print("No results returned")
    
    # Test with '阿里巴巴'
    result2 = await juhecha_service.search_enterprise_info("阿里巴巴", 3)
    print(f"\n'Alibaba' result length: {len(result2)}")
    if result2:
        for i, company in enumerate(result2[:3]):
            print(f"  {i+1}. {company.get('name', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(test())
