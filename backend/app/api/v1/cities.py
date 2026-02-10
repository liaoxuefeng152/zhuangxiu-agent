"""
装修决策Agent - 城市选择API (P35)
"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from app.core.security import get_user_id
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models import User
from app.schemas import ApiResponse

router = APIRouter(prefix="/cities", tags=["城市选择"])
logger = logging.getLogger(__name__)

# 热门城市 + 省份-城市 静态数据（PRD 首批10城）
HOT_CITIES = [
    {"code": "010", "name": "北京"},
    {"code": "021", "name": "上海"},
    {"code": "020", "name": "广州"},
    {"code": "0755", "name": "深圳"},
    {"code": "0571", "name": "杭州"},
    {"code": "028", "name": "成都"},
    {"code": "027", "name": "武汉"},
    {"code": "025", "name": "南京"},
    {"code": "023", "name": "重庆"},
    {"code": "029", "name": "西安"},
]

PROVINCES_CITIES = {
    "北京": ["北京市"],
    "上海": ["上海市"],
    "天津": ["天津市"],
    "重庆": ["重庆市"],
    "广东": ["广州市", "深圳市", "东莞市", "佛山市", "珠海市"],
    "浙江": ["杭州市", "宁波市", "温州市", "嘉兴市"],
    "江苏": ["南京市", "苏州市", "无锡市", "常州市"],
    "四川": ["成都市", "绵阳市"],
    "湖北": ["武汉市", "宜昌市"],
    "陕西": ["西安市", "咸阳市"],
    "山东": ["济南市", "青岛市"],
    "河南": ["郑州市", "洛阳市"],
    "福建": ["厦门市", "福州市"],
}


class CitySelectRequest(BaseModel):
    city_code: Optional[str] = None
    city_name: str = Field(..., min_length=1, description="城市名称，如 深圳市")


@router.get("/hot")
async def hot_cities():
    """热门城市列表"""
    return ApiResponse(code=0, msg="success", data={"list": HOT_CITIES})


@router.get("/list")
async def list_cities(
    province: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="搜索关键词"),
):
    """省份-城市列表；可选省份筛选或关键词搜索"""
    if q:
        q_lower = q.strip().lower()
        result = []
        for prov, cities in PROVINCES_CITIES.items():
            for c in cities:
                if q_lower in c.lower() or q_lower in prov.lower():
                    result.append({"province": prov, "name": c})
        return ApiResponse(code=0, msg="success", data={"list": result[:20]})
    if province:
        cities = PROVINCES_CITIES.get(province, [])
        return ApiResponse(code=0, msg="success", data={"list": [{"name": c} for c in cities]})
    return ApiResponse(
        code=0,
        msg="success",
        data={"provinces": list(PROVINCES_CITIES.keys()), "cities_by_province": PROVINCES_CITIES},
    )


@router.post("/select")
async def select_city(
    request: CitySelectRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """保存用户当前城市"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return ApiResponse(code=404, msg="用户不存在", data=None)
        user.city_code = request.city_code
        user.city_name = request.city_name
        await db.commit()
        return ApiResponse(
            code=0,
            msg="success",
            data={"city_code": request.city_code, "city_name": request.city_name},
        )
    except Exception as e:
        logger.error(f"选择城市失败: {e}", exc_info=True)
        return ApiResponse(code=500, msg="保存失败", data=None)


@router.get("/current")
async def current_city(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取用户当前选中的城市"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return ApiResponse(code=404, msg="用户不存在", data=None)
        return ApiResponse(
            code=0,
            msg="success",
            data={"city_code": user.city_code or "", "city_name": user.city_name or ""},
        )
    except Exception as e:
        logger.error(f"获取当前城市失败: {e}", exc_info=True)
        return ApiResponse(code=500, msg="获取失败", data=None)
