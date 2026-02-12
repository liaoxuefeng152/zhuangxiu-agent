"""
装修决策Agent - 订单支付API
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional
import hashlib
import random
import string
import logging

from app.core.database import get_db
from app.core.security import get_user_id
from app.core.config import settings
from app.models import Order, User, Quote, Contract, RefundRequest
from app.schemas import (
    CreateOrderRequest, CreateOrderResponse, PaymentRequest,
    PaymentResponse, OrderResponse, ApiResponse, OrderType, OrderStatus
)

def _safe_order_status(s: str) -> str:
    valid = {"pending", "paid", "completed", "cancelled", "refunded"}
    return s if s and s in valid else "pending"

router = APIRouter(prefix="/payments", tags=["订单支付"])
logger = logging.getLogger(__name__)


def generate_order_no() -> str:
    """生成订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"DECO{timestamp}{random_str}"


def generate_wechat_pay_sign(params: dict) -> str:
    """
    生成微信支付签名

    Args:
        params: 支付参数字典

    Returns:
        签名字符串
    """
    # 参数排序
    sorted_params = sorted(params.items(), key=lambda x: x[0])

    # 拼接字符串
    sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params if v])
    sign_str += f"&key={settings.WECHAT_API_KEY}"

    # MD5加密
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
    return sign


@router.post("/create", response_model=CreateOrderResponse)
async def create_order(
    request: CreateOrderRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    创建订单

    Args:
        request: 创建订单请求
        user_id: 用户ID
        db: 数据库会话

    Returns:
        订单信息
    """
    try:
        # 计算价格
        if request.order_type == OrderType.REPORT_SINGLE:
            amount = settings.REPORT_SINGLE_PRICE
        elif request.order_type == OrderType.REPORT_PACKAGE:
            amount = settings.REPORT_THREE_PRICE
        elif request.order_type == OrderType.SUPERVISION_SINGLE:
            amount = settings.SUPERVISION_SINGLE_PRICE
        elif request.order_type == OrderType.SUPERVISION_PACKAGE:
            amount = settings.SUPERVISION_PACKAGE_PRICE
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单类型不正确"
            )

        # V2.6.2优化：检查用户是否为会员，会员无限解锁
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        is_member = user and user.is_member
        
        # 验证资源是否存在
        if request.resource_type == "quote":
            result = await db.execute(
                select(Quote).where(Quote.id == request.resource_id, Quote.user_id == user_id)
            )
            resource = result.scalar_one_or_none()
            if not resource:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="报价单不存在"
                )
            # 会员无限解锁
            if is_member and not resource.is_unlocked:
                resource.is_unlocked = True
                resource.unlock_type = "member"
                await db.commit()
                logger.info(f"会员无限解锁: 报价单 {request.resource_id}, 用户 {user_id}")
                return CreateOrderResponse(
                    order_id=0,
                    order_no="MEMBER_FREE",
                    order_type=request.order_type.value,
                    amount=0.0,
                    status="completed"
                )
        elif request.resource_type == "contract":
            result = await db.execute(
                select(Contract).where(Contract.id == request.resource_id, Contract.user_id == user_id)
            )
            resource = result.scalar_one_or_none()
            if not resource:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="合同不存在"
                )
            # 会员无限解锁
            if is_member and not resource.is_unlocked:
                resource.is_unlocked = True
                resource.unlock_type = "member"
                await db.commit()
                logger.info(f"会员无限解锁: 合同 {request.resource_id}, 用户 {user_id}")
                return CreateOrderResponse(
                    order_id=0,
                    order_no="MEMBER_FREE",
                    order_type=request.order_type.value,
                    amount=0.0,
                    status="completed"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="资源类型不正确"
            )

        # 创建订单
        order = Order(
            user_id=user_id,
            order_no=generate_order_no(),
            order_type=request.order_type.value,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            amount=amount,
            status=OrderStatus.PENDING,
            payment_method="wechat"
        )

        db.add(order)
        await db.commit()
        await db.refresh(order)

        logger.info(f"创建订单成功: {order.order_no}, 金额: {amount}")

        return CreateOrderResponse(
            order_id=order.id,
            order_no=order.order_no,
            order_type=order.order_type,
            amount=order.amount,
            status=order.status
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建订单失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建订单失败"
        )


@router.post("/pay", response_model=PaymentResponse)
async def pay_order(
    request: PaymentRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    发起支付（生成微信支付参数）

    Args:
        request: 支付请求
        user_id: 用户ID
        db: 数据库会话

    Returns:
        微信支付参数
    """
    try:
        # 查找订单
        result = await db.execute(
            select(Order).where(Order.id == request.order_id, Order.user_id == user_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )

        if order.status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单状态不正确"
            )

        # 生成微信支付参数（这里简化，实际应该调用微信支付API）
        # 以下为示例参数结构，实际需要集成微信支付SDK
        timestamp = str(int(datetime.now().timestamp()))
        nonce_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        body = f"装修决策Agent-{order.order_type}"

        pay_params = {
            "appId": settings.WECHAT_APP_ID,
            "timeStamp": timestamp,
            "nonceStr": nonce_str,
            "package": f"prepay_id={order.order_no}",
            "signType": "MD5",
            "paySign": generate_wechat_pay_sign({
                "appId": settings.WECHAT_APP_ID,
                "timeStamp": timestamp,
                "nonceStr": nonce_str,
                "package": f"prepay_id={order.order_no}",
                "signType": "MD5"
            })
        }

        logger.info(f"生成支付参数: {order.order_no}")

        return PaymentResponse(
            order_no=order.order_no,
            pay_sign=pay_params["paySign"],
            timestamp=pay_params["timeStamp"],
            nonce_str=pay_params["nonceStr"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成支付参数失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="生成支付参数失败"
        )


@router.post("/notify")
async def payment_notify(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    微信支付回调通知

    Args:
        background_tasks: 后台任务
        db: 数据库会话

    Returns:
        回调响应
    """
    try:
        # 实际应该验证微信签名
        # 这里简化处理

        # 查找订单并更新状态
        # 注意：实际应该从微信回调数据中获取订单号
        # order_no = callback_data.get('out_trade_no')

        # result = await db.execute(
        #     select(Order).where(Order.order_no == order_no)
        # )
        # order = result.scalar_one_or_none()
        #
        # if order and order.status == OrderStatus.PENDING:
        #     order.status = OrderStatus.PAID
        #     order.transaction_id = callback_data.get('transaction_id')
        #     order.paid_at = datetime.now()
        #     await db.commit()

        # 回复微信
        return {"return_code": "SUCCESS", "return_msg": "OK"}

    except Exception as e:
        logger.error(f"支付回调处理失败: {e}", exc_info=True)
        return {"return_code": "FAIL", "return_msg": "处理失败"}


@router.get("/orders")
async def list_orders(
    user_id: int = Depends(get_user_id),
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户订单列表

    Args:
        user_id: 用户ID
        page: 页码
        page_size: 每页数量
        db: 数据库会话

    Returns:
        订单列表
    """
    try:
        offset = (page - 1) * page_size

        result = await db.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .limit(page_size)
            .offset(offset)
        )
        orders = result.scalars().all()

        count_result = await db.execute(
            select(Order.id)
            .where(Order.user_id == user_id)
        )
        total = len(count_result.all())

        return ApiResponse(
            code=0,
            msg="success",
            data={
                "list": [
                    {
                        "id": order.id,
                        "order_no": order.order_no or "",
                        "order_type": order.order_type or "",
                        "amount": float(order.amount) if order.amount is not None else 0,
                        "status": order.status or "pending",
                        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
                        "created_at": order.created_at.isoformat() if order.created_at else None
                    }
                    for order in orders
                ],
                "total": total,
                "page": page,
                "page_size": page_size
            }
        )

    except Exception as e:
        logger.error(f"获取订单列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取订单列表失败"
        )


@router.get("/order/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取订单详情

    Args:
        order_id: 订单ID
        user_id: 用户ID
        db: 数据库会话

    Returns:
        订单详情
    """
    try:
        result = await db.execute(
            select(Order)
            .where(Order.id == order_id, Order.user_id == user_id)
        )
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )

        return OrderResponse(
            id=order.id,
            order_no=order.order_no or "",
            order_type=order.order_type or "",
            amount=float(order.amount) if order.amount is not None else 0,
            status=_safe_order_status(order.status or "pending"),
            paid_at=order.paid_at,
            created_at=order.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取订单详情失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取订单详情失败"
        )


class RefundApplyRequest(BaseModel):
    order_id: int
    reason: str
    note: Optional[str] = None


@router.post("/refund/apply")
async def apply_refund(
    request: RefundApplyRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """提交退款申请（P34）"""
    try:
        result = await db.execute(
            select(Order).where(Order.id == request.order_id, Order.user_id == user_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
        if order.status not in (OrderStatus.PAID.value, "paid", "completed"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持已支付订单申请退款")
        existing = await db.execute(
            select(RefundRequest).where(RefundRequest.order_id == request.order_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该订单已提交过退款申请")
        refund_amount = float(order.amount)
        rr = RefundRequest(
            order_id=order.id,
            user_id=user_id,
            reason=(request.reason or "")[:100],
            note=request.note,
            refund_amount=refund_amount,
            status="pending",
        )
        db.add(rr)
        await db.commit()
        await db.refresh(rr)
        return ApiResponse(
            code=0,
            msg="申请提交成功，1-3个工作日处理",
            data={"id": rr.id, "status": rr.status},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"退款申请失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="提交失败")


@router.get("/refund/status")
async def refund_status(
    order_id: int,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db),
):
    """查询订单退款状态"""
    try:
        result = await db.execute(
            select(RefundRequest).where(
                RefundRequest.order_id == order_id,
                RefundRequest.user_id == user_id,
            )
        )
        rr = result.scalar_one_or_none()
        if not rr:
            return ApiResponse(code=0, msg="success", data=None)
        return ApiResponse(
            code=0,
            msg="success",
            data={
                "id": rr.id,
                "order_id": rr.order_id,
                "status": rr.status,
                "refund_amount": rr.refund_amount,
                "created_at": rr.created_at.isoformat() if rr.created_at else None,
            },
        )
    except Exception as e:
        logger.error(f"查询退款状态失败: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="查询失败")
