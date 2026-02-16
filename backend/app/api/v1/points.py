"""
装修决策Agent - 积分系统API（V2.6.7新增）
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.security import get_user_id
from app.models import User, PointRecord
from app.schemas import ApiResponse

router = APIRouter(prefix="/points", tags=["积分系统"])
logger = logging.getLogger(__name__)

# 积分奖励配置
SHARE_REPORT_POINTS = 10  # 分享报告奖励积分
SHARE_PROGRESS_POINTS = 5  # 分享进度奖励积分
DAILY_CHECKIN_POINTS = 1  # 每日签到积分


class ShareRewardRequest(BaseModel):
    """分享奖励请求"""
    share_type: str  # report: 分享报告, progress: 分享进度
    resource_type: Optional[str] = None  # acceptance, quote, contract, company, construction
    resource_id: Optional[int] = None  # 资源ID


@router.post("/share-reward")
async def share_reward(
    request: ShareRewardRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    分享奖励积分（V2.6.7新增）
    分享报告/进度后调用此接口获得积分奖励
    每日同一类型分享仅奖励一次
    """
    try:
        # 获取用户
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        # 确定奖励积分
        if request.share_type == "report":
            reward_points = SHARE_REPORT_POINTS
            source_type = f"share_report_{request.resource_type or 'unknown'}"
            description = f"分享{request.resource_type or '报告'}获得积分"
        elif request.share_type == "progress":
            reward_points = SHARE_PROGRESS_POINTS
            source_type = "share_progress"
            description = "分享施工进度获得积分"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的分享类型")

        # 检查今日是否已获得该类型奖励（防止重复刷积分）
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_records = await db.execute(
            select(PointRecord).where(
                and_(
                    PointRecord.user_id == user_id,
                    PointRecord.source_type == source_type,
                    PointRecord.created_at >= today_start
                )
            )
        )
        existing_record = today_records.scalar_one_or_none()
        if existing_record:
            return ApiResponse(
                code=0,
                msg="今日已获得该类型分享奖励",
                data={
                    "points": getattr(user, "points", 0) or 0,
                    "reward_points": 0,
                    "already_rewarded": True
                }
            )

        # 添加积分记录
        point_record = PointRecord(
            user_id=user_id,
            points=reward_points,
            source_type=source_type,
            source_id=request.resource_id,
            description=description
        )
        db.add(point_record)

        # 更新用户积分
        current_points = getattr(user, "points", 0) or 0
        user.points = current_points + reward_points

        await db.commit()

        logger.info(f"用户 {user_id} 分享 {request.share_type} 获得 {reward_points} 积分")

        return ApiResponse(
            code=0,
            msg="分享成功，获得积分奖励",
            data={
                "points": user.points,
                "reward_points": reward_points,
                "already_rewarded": False
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分享奖励失败: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="奖励发放失败"
        )


@router.get("/records")
async def get_point_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取积分记录列表（V2.6.7新增）
    """
    try:
        offset = (page - 1) * page_size

        # 查询总数
        count_result = await db.execute(
            select(func.count(PointRecord.id)).where(PointRecord.user_id == user_id)
        )
        total = count_result.scalar_one()

        # 查询记录
        records_result = await db.execute(
            select(PointRecord)
            .where(PointRecord.user_id == user_id)
            .order_by(PointRecord.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        records = records_result.scalars().all()

        return ApiResponse(
            code=0,
            msg="success",
            data={
                "total": total,
                "page": page,
                "page_size": page_size,
                "records": [
                    {
                        "id": r.id,
                        "points": r.points,
                        "source_type": r.source_type,
                        "description": r.description,
                        "created_at": r.created_at.isoformat()
                    }
                    for r in records
                ]
            }
        )

    except Exception as e:
        logger.error(f"获取积分记录失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取失败"
        )


@router.get("/summary")
async def get_points_summary(
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取积分汇总信息（V2.6.7新增）
    """
    try:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        # 统计本月获得积分
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_points_result = await db.execute(
            select(func.sum(PointRecord.points)).where(
                and_(
                    PointRecord.user_id == user_id,
                    PointRecord.points > 0,
                    PointRecord.created_at >= month_start
                )
            )
        )
        month_points = month_points_result.scalar_one() or 0

        return ApiResponse(
            code=0,
            msg="success",
            data={
                "total_points": getattr(user, "points", 0) or 0,
                "month_points": int(month_points)
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取积分汇总失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取失败"
        )
