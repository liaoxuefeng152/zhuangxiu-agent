"""
装修决策Agent - P37 材料进场人工核对 API（PRD V2.6.1 FR-019~FR-023）
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime, date
import logging
import json

from app.core.database import get_db
from app.core.security import get_user_id
from app.models import Quote, Contract, MaterialCheck, MaterialCheckItem, Construction
from app.schemas import ApiResponse
from app.api.v1.constructions import (
    calculate_construction_schedule,
    _stages_to_json_serializable,
)

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


def _extract_materials_from_result_json(result_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    从报价单/合同分析结果中提取材料清单
    
    返回格式：[
        {
            "material_name": "材料名称",
            "spec_brand": "规格/品牌",
            "quantity": "数量",
            "category": "关键材料|辅助材料",
            "unit_price": 单价（可选）
        }
    ]
    """
    materials = []
    
    if not result_json or not isinstance(result_json, dict):
        return materials
    
    # 方式1：直接从materials或material_list字段提取
    material_list = result_json.get("materials") or result_json.get("material_list") or []
    if isinstance(material_list, list):
        for item in material_list:
            if isinstance(item, dict):
                materials.append({
                    "material_name": item.get("material_name") or item.get("name") or item.get("item") or "",
                    "spec_brand": item.get("spec_brand") or item.get("brand") or item.get("specification") or item.get("spec") or "",
                    "quantity": str(item.get("quantity") or item.get("qty") or item.get("amount") or ""),
                    "category": item.get("category") or item.get("type") or "关键材料",
                    "unit_price": item.get("unit_price") or item.get("price") or None
                })
            elif isinstance(item, str):
                materials.append({
                    "material_name": item,
                    "spec_brand": "",
                    "quantity": "",
                    "category": "关键材料",
                    "unit_price": None
                })
    
    # 方式2：从OCR结果中提取材料项（如果AI分析结果中没有）
    if not materials:
        ocr_text = result_json.get("ocr_text") or result_json.get("ocr_result") or ""
        if isinstance(ocr_text, str) and ocr_text.strip():
            # 尝试从OCR文本中提取材料信息（简单匹配）
            lines = ocr_text.split("\n")
            for line in lines:
                line = line.strip()
                if any(keyword in line for keyword in ["材料", "品牌", "规格", "型号", "数量"]):
                    # 简单提取：假设格式为 "材料名称 规格/品牌 数量"
                    parts = line.split()
                    if len(parts) >= 1:
                        materials.append({
                            "material_name": parts[0] if parts else line,
                            "spec_brand": parts[1] if len(parts) > 1 else "",
                            "quantity": parts[2] if len(parts) > 2 else "",
                            "category": "关键材料",
                            "unit_price": None
                        })
    
    # 方式3：从高风险项和警告项中提取材料名称（降级方案）
    if not materials:
        high_risk = result_json.get("high_risk_items") or []
        warning = result_json.get("warning_items") or []
        for item in high_risk + warning:
            if isinstance(item, dict):
                name = item.get("name") or item.get("item") or item.get("description") or ""
                if name:
                    materials.append({
                        "material_name": name,
                        "spec_brand": item.get("brand") or item.get("specification") or "",
                        "quantity": str(item.get("quantity") or ""),
                        "category": "关键材料" if item in high_risk else "辅助材料",
                        "unit_price": item.get("price") or None
                    })
    
    return materials


def _sort_materials_by_category(materials: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    按「关键材料→辅助材料」排序
    """
    key_materials = []
    auxiliary_materials = []
    other_materials = []
    
    for mat in materials:
        category = mat.get("category", "").strip()
        if "关键" in category or "主要" in category or "核心" in category:
            key_materials.append(mat)
        elif "辅助" in category or "次要" in category:
            auxiliary_materials.append(mat)
        else:
            # 默认归类为关键材料
            mat["category"] = "关键材料"
            key_materials.append(mat)
    
    return key_materials + auxiliary_materials + other_materials


@router.get("/material-list")
async def get_material_list_from_quote(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取材料清单（FR-019）：从报价单/合同同步，关键材料→辅助材料
    
    优先级：
    1. 报价单（最新完成的）
    2. 合同（最新完成的）
    3. 返回空列表
    """
    try:
        # 优先从报价单获取
        quote_result = await db.execute(
            select(Quote)
            .where(Quote.user_id == user_id, Quote.status == "completed")
            .order_by(Quote.created_at.desc())
            .limit(1)
        )
        quote = quote_result.scalar_one_or_none()
        
        materials = []
        source = "none"
        source_id = None
        
        if quote and quote.result_json:
            materials = _extract_materials_from_result_json(quote.result_json)
            if materials:
                source = "quote"
                source_id = quote.id
        
        # 如果报价单没有材料，尝试从合同获取
        if not materials:
            contract_result = await db.execute(
                select(Contract)
                .where(Contract.user_id == user_id, Contract.status == "completed")
                .order_by(Contract.created_at.desc())
                .limit(1)
            )
            contract = contract_result.scalar_one_or_none()
            
            if contract and contract.result_json:
                materials = _extract_materials_from_result_json(contract.result_json)
                if materials:
                    source = "contract"
                    source_id = contract.id
        
        # 排序：关键材料→辅助材料
        materials = _sort_materials_by_category(materials)
        
        # 如果没有材料，返回提示
        if not materials:
            return ApiResponse(
                code=0,
                msg="success",
                data={
                    "list": [],
                    "source": source,
                    "hint": "未同步到材料清单，请先上传报价单或合同"
                }
            )
        
        # 格式化返回数据（确保字段完整）
        formatted_materials = []
        for mat in materials[:50]:  # 最多返回50项
            formatted_materials.append({
                "material_name": mat.get("material_name", "").strip() or "未命名材料",
                "spec_brand": mat.get("spec_brand", "").strip(),
                "quantity": mat.get("quantity", "").strip(),
                "category": mat.get("category", "关键材料"),
                "unit_price": mat.get("unit_price")
            })
        
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "list": formatted_materials,
                "source": source,
                "source_id": source_id,
                "total_count": len(materials)
            }
        )
    except Exception as e:
        logger.error(f"获取材料清单失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


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

        # 同步更新施工进度 S00 状态；若用户未设置过开工日期则先创建进度计划再写 S00
        const_result = await db.execute(select(Construction).where(Construction.user_id == user_id))
        construction = const_result.scalar_one_or_none()
        s00_status = "checked" if request.result == "pass" else "need_rectify"
        if construction:
            stages_raw = construction.stages or {}
            if isinstance(stages_raw, str):
                try:
                    stages_raw = json.loads(stages_raw)
                except Exception:
                    stages_raw = {}
            if not isinstance(stages_raw, dict):
                stages_raw = {}
            stages = dict(stages_raw)
            # 若缺少 S00 或 stages 为空，用开工日补全阶段再写 S00（避免覆盖 S01-S05）
            if "S00" not in stages or not stages:
                start_dt = construction.start_date or datetime.combine(date.today(), datetime.min.time())
                if not construction.start_date:
                    construction.start_date = start_dt
                schedule = calculate_construction_schedule(start_dt)
                stages = dict(schedule["stages"])
                if construction.estimated_end_date is None:
                    construction.estimated_end_date = schedule["estimated_end_date"]
            if not isinstance(stages.get("S00"), dict):
                stages["S00"] = {}
            stages["S00"] = {**stages["S00"], "status": s00_status}
            construction.stages = _stages_to_json_serializable(stages)
            flag_modified(construction, "stages")
            await db.commit()
        else:
            # 用户未设置开工日期：创建进度计划并以今日为开工日，S00 直接写入核对结果
            start_dt = datetime.combine(date.today(), datetime.min.time())
            schedule = calculate_construction_schedule(start_dt)
            stages = dict(schedule["stages"])
            if "S00" in stages:
                stages["S00"]["status"] = s00_status
            construction = Construction(
                user_id=user_id,
                start_date=start_dt,
                estimated_end_date=schedule["estimated_end_date"],
                stages=_stages_to_json_serializable(stages),
                progress_percentage=0,
            )
            db.add(construction)
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
