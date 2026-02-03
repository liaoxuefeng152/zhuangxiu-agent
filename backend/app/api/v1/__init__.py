"""
装修决策Agent - API路由汇总
"""
from fastapi import APIRouter
from app.api.v1 import users, companies, quotes, contracts, constructions, payments

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(companies.router, prefix="/companies", tags=["公司检测"])
api_router.include_router(quotes.router, prefix="/quotes", tags=["报价单分析"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["合同审核"])
api_router.include_router(constructions.router, prefix="/constructions", tags=["施工进度"])
api_router.include_router(payments.router, prefix="/payments", tags=["订单支付"])
