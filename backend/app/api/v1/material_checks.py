"""
装修决策Agent - P37 材料进场人工核对 API（PRD V2.6.1 FR-019~FR-023）
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import List, Optional, Any
import logging

from app.core.database import get_db
from app.core.security import get_user_id
from app.models import Quote, MaterialCheck, MaterialCheckItem, Construction
from app.schemas import ApiResponse

router = APIRouter(prefix="/material-checks", tags=["材料进场人工核对 P37"])
logger = logging.getLogger(__name__)


class MaterialItemInput(BaseModel):
    material_name: str = Field(..., max_length=200)
    spec_brand: Optional[str] = None
    quantity: Optional[str] = None
    photo_urls: List[str] = Field(default_factory=list, max_length=9)
    doc_certificate_url: Optional[str] = None
    doc_quality_url: Optional[str] = None
    doc_ccc_url: Optional[str] = None


class MaterialCheckSubmitRequest(BaseModel):
    quote_id: Optional[int] = None
    items: List[MaterialItemInput] = Field(..., min_length=1)
    result: str = Field(..., description="pass | fail")
    problem_note: Optional[str] = Field(None, max_length=100)


@router.get("/material-list")
async def get_material_list_from_quote(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取材料清单（FR-019）：从报价单同步，关键材料→辅助材料"""
    try:
        result = await db.execute(
            select(Quote)
            .where(Quote.user_id == user_id, Quote.status == "completed")
            .order_by(Quote.created_at.desc())
            .limit(1)
        )
        quote = result.scalar_one_or_none()
        if not quote or not quote.result_json:
            return ApiResponse(
                code=0,
                msg="success",
                data={
                    "list": [],
                    "source": "none",
                    "hint": "未同步到材料清单，请先上传报价单"
                }
            )

        rj = quote.result_json or {}
        materials = rj.get("materials") or rj.get("material_list") or []
        if not materials and (rj.get("high_risk_items") or rj.get("warning_items")):
            high = rj.get("high_risk_items") or []
            warn = rj.get("warning_items") or []
            for it in high + warn:
                name = it.get("name") or it.get("item") or it.get("description") or str(it)
                if isinstance(name, dict):
                    name = name.get("name") or name.get("item") or str(name)
                materials.append({"material_name": name, "spec_brand": "", "quantity": ""})
        if not materials:
            materials = [{"material_name": "关键材料（请从报价单补充）", "spec_brand": "", "quantity": ""}]

        return ApiResponse(
            code=0,
            msg="success",
            data={
                "list": materials[:50],
                "source": "quote",
                "quote_id": quote.id
            }
        )
    except Exception as e:
        logger.error(f"获取材料清单失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取失败")


@router.get("/latest")
async def get_latest_material_check(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取最近一次材料核对记录（S00 状态展示）"""
    try:
        result = await db.execute(
            select(MaterialCheck)
            .where(MaterialCheck.user_id == user_id)
            .order_by(MaterialCheck.submitted_at.desc())
            .limit(1)
        )
        check = result.scalar_one_or_none()
        if not check:
            return ApiResponse(code=0, msg="success", data=None)

        items_result = await db.execute(
            select(MaterialCheckItem).where(MaterialCheckItem.material_check_id == check.id)
        )
        items = items_result.scalars().all()
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "id": check.id,
                "result": check.result,
                "problem_note": check.problem_note,
                "submitted_at": check.submitted_at.isoformat() if check.submitted_at else None,
                "items": [
                    {
                        "id": i.id,
                        "material_name": i.material_name,
                        "spec_brand": i.spec_brand,
                        "quantity": i.quantity,
                        "photo_urls": i.photo_urls or [],
                        "doc_certificate_url": i.doc_certificate_url,
                        "doc_quality_url": i.doc_quality_url,
                        "doc_ccc_url": i.doc_ccc_url,
                    }
                    for i in items
                ]
            }
        )
    except Exception as e:
        logger.error(f"获取材料核对记录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取失败")


@router.post("/submit")
async def submit_material_check(
    request: MaterialCheckSubmitRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """提交材料进场人工核对结果（FR-023）；通过需所有项至少1张照片"""
    try:
        if request.result not in ("pass", "fail"):
            raise HTTPException(status_code=400, detail="result 必须为 pass 或 fail")

        if request.result == "pass":
            for it in request.items:
                if not (it.photo_urls and len(it.photo_urls) >= 1):
                    raise HTTPException(
                        status_code=400,
                        detail="还有材料未上传照片，无法通过核对"
                    )
        else:
            if not request.problem_note or len(request.problem_note.strip()) < 10:
                raise HTTPException(status_code=400, detail="核对未通过时请填写原因（至少10字）")

        check = MaterialCheck(
            user_id=user_id,
            quote_id=request.quote_id,
            result=request.result,
            problem_note=request.problem_note.strip() if request.problem_note else None
        )
        db.add(check)
        await db.flush()

        for it in request.items:
            item = MaterialCheckItem(
                material_check_id=check.id,
                material_name=it.material_name,
                spec_brand=it.spec_brand,
                quantity=it.quantity,
                photo_urls=it.photo_urls or [],
                doc_certificate_url=it.doc_certificate_url,
                doc_quality_url=it.doc_quality_url,
                doc_ccc_url=it.doc_ccc_url,
            )
            db.add(item)

        await db.commit()
        await db.refresh(check)

        # 同步更新施工进度 S00 状态
        const_result = await db.execute(select(Construction).where(Construction.user_id == user_id))
        construction = const_result.scalar_one_or_none()
        if construction and construction.stages:
            stages = dict(construction.stages)
            if "S00" in stages:
                stages["S00"]["status"] = "checked" if request.result == "pass" else "need_rectify"
                construction.stages = stages
                await db.commit()

        return ApiResponse(
            code=0,
            msg="提交成功",
            data={
                "id": check.id,
                "result": check.result,
                "submitted_at": check.submitted_at.isoformat() if check.submitted_at else None
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"提交材料核对失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="网络异常，请稍后重试")
