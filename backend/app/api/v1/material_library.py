"""
装修决策Agent - 材料库API（V2.6.2优化）
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging

from app.core.database import get_db
from app.core.security import get_user_id
from app.models import Material, User
from app.schemas import ApiResponse

router = APIRouter(prefix="/material-library", tags=["材料库"])
logger = logging.getLogger(__name__)


class MaterialCreateRequest(BaseModel):
    """创建材料请求"""
    material_name: str = Field(..., max_length=200)
    category: str = Field(..., description="主材|辅材")
    spec_brand: Optional[str] = None
    unit: Optional[str] = None
    typical_price_range: Optional[Dict[str, Any]] = None
    city_code: Optional[str] = None
    description: Optional[str] = None


class MaterialResponse(BaseModel):
    """材料响应"""
    id: int
    material_name: str
    category: str
    spec_brand: Optional[str]
    unit: Optional[str]
    typical_price_range: Optional[Dict[str, Any]]
    city_code: Optional[str]
    description: Optional[str]


@router.get("/search")
async def search_materials(
    keyword: str = Query(..., description="材料名称关键词"),
    category: Optional[str] = Query(None, description="类别：主材|辅材"),
    city_code: Optional[str] = Query(None, description="城市代码（用于本地化价格）"),
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """搜索材料库（V2.6.2优化：智能补全材料信息）"""
    try:
        stmt = select(Material).where(
            Material.is_active == True,
            or_(
                Material.material_name.like(f"%{keyword}%"),
                Material.spec_brand.like(f"%{keyword}%") if keyword else False
            )
        )
        if category:
            stmt = stmt.where(Material.category == category)
        if city_code:
            stmt = stmt.where(
                or_(
                    Material.city_code == city_code,
                    Material.city_code.is_(None)  # 通用材料
                )
            )
        stmt = stmt.limit(20)
        
        result = await db.execute(stmt)
        materials = result.scalars().all()
        
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "list": [
                    {
                        "id": m.id,
                        "material_name": m.material_name,
                        "category": m.category,
                        "spec_brand": m.spec_brand,
                        "unit": m.unit,
                        "typical_price_range": m.typical_price_range,
                        "description": m.description
                    }
                    for m in materials
                ]
            }
        )
    except Exception as e:
        logger.error(f"搜索材料库失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="搜索失败")


@router.get("/common")
async def get_common_materials(
    category: Optional[str] = Query(None, description="类别：主材|辅材"),
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取常用材料列表（V2.6.2优化：常用材料模板）"""
    try:
        stmt = select(Material).where(Material.is_active == True)
        if category:
            stmt = stmt.where(Material.category == category)
        stmt = stmt.order_by(Material.created_at.desc()).limit(50)
        
        result = await db.execute(stmt)
        materials = result.scalars().all()
        
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "list": [
                    {
                        "id": m.id,
                        "material_name": m.material_name,
                        "category": m.category,
                        "spec_brand": m.spec_brand,
                        "unit": m.unit,
                        "typical_price_range": m.typical_price_range
                    }
                    for m in materials
                ]
            }
        )
    except Exception as e:
        logger.error(f"获取常用材料失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取失败")


@router.post("/match")
async def match_materials_from_quote(
    material_names: List[str] = Field(..., description="从报价单提取的材料名称列表"),
    city_code: Optional[str] = Query(None, description="城市代码"),
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """智能匹配材料（V2.6.2优化：根据报价单材料名称，自动匹配材料库）"""
    try:
        matched = []
        for name in material_names:
            # 模糊匹配材料名称
            stmt = select(Material).where(
                Material.is_active == True,
                Material.material_name.like(f"%{name}%")
            ).limit(1)
            result = await db.execute(stmt)
            material = result.scalar_one_or_none()
            if material:
                matched.append({
                    "original_name": name,
                    "matched": {
                        "id": material.id,
                        "material_name": material.material_name,
                        "category": material.category,
                        "spec_brand": material.spec_brand,
                        "unit": material.unit,
                        "typical_price_range": material.typical_price_range
                    }
                })
            else:
                matched.append({
                    "original_name": name,
                    "matched": None
                })
        
        return ApiResponse(
            code=0,
            msg="success",
            data={"matched": matched}
        )
    except Exception as e:
        logger.error(f"匹配材料失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="匹配失败")
