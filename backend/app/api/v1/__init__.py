"""
装修决策Agent - API路由汇总
"""
from fastapi import APIRouter
from app.api.v1 import users, companies, quotes, contracts, constructions, payments
from app.api.v1 import messages, feedback, construction_photos, acceptance, reports
from app.api.v1 import dev_seed, cities, consultation, data_manage, material_checks, material_library, oss, appeals, points, invitations, designer

api_router = APIRouter()

# 注册各模块路由
api_router.include_router(dev_seed.router)
api_router.include_router(users.router)
api_router.include_router(companies.router)
api_router.include_router(quotes.router)
api_router.include_router(contracts.router)
api_router.include_router(constructions.router)
api_router.include_router(payments.router)
api_router.include_router(messages.router)
api_router.include_router(feedback.router)
api_router.include_router(construction_photos.router)
api_router.include_router(acceptance.router)
api_router.include_router(reports.router)
api_router.include_router(cities.router)
api_router.include_router(consultation.router)
api_router.include_router(data_manage.router)
api_router.include_router(material_checks.router)
api_router.include_router(material_library.router)
api_router.include_router(oss.router)
api_router.include_router(appeals.router)
api_router.include_router(points.router)
api_router.include_router(invitations.router)  # V2.6.8新增：邀请系统
api_router.include_router(designer.router, prefix="/designer", tags=["AI设计师"])
