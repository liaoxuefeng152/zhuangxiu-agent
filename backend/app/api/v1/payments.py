"""
装修决策Agent - 订单支付API
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional
from dateutil.relativedelta import relativedelta
import hashlib
import random
import string
import logging

from app.core.database import get_db
from app.core.security import get_user_id
from app.core.config import settings
from app.models import Order, User, Quote, Contract, RefundRequest, CompanyScan, AcceptanceAnalysis
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
    生成微信支付签名（兼容V2 MD5签名，用于旧版本兼容）
    
    注意：微信支付V3使用RSA-SHA256签名，请使用generate_wechat_v3_signature函数

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


def generate_wechat_v3_signature(
    method: str,
    url: str,
    timestamp: int,
    nonce: str,
    body: str = ""
) -> str:
    """
    生成微信支付V3签名
    
    使用安全的密钥文件读取，遵循微信支付V3规范
    
    Args:
        method: HTTP方法，如 'GET', 'POST'
        url: 请求URL（不包含协议和域名）
        timestamp: 时间戳（秒）
        nonce: 随机字符串
        body: 请求体（JSON字符串），GET请求可为空
        
    Returns:
        str: Base64编码的签名
    """
    try:
        from app.services.wechat_pay_security import get_wechat_pay_security
        
        security = get_wechat_pay_security()
        return security.generate_v3_signature(method, url, timestamp, nonce, body)
        
    except Exception as e:
        logger.error(f"生成微信支付V3签名失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="生成支付签名失败"
        )


def decrypt_wechat_v3_data(
    associated_data: str,
    nonce: str,
    ciphertext: str
) -> str:
    """
    解密微信支付V3敏感数据
    
    使用安全的密钥文件读取，遵循微信支付V3规范
    
    Args:
        associated_data: 关联数据
        nonce: 随机串
        ciphertext: Base64编码的密文
        
    Returns:
        str: 解密后的明文（JSON字符串）
    """
    try:
        from app.services.wechat_pay_security import get_wechat_pay_security
        
        security = get_wechat_pay_security()
        return security.decrypt_v3_data(associated_data, nonce, ciphertext)
        
    except Exception as e:
        logger.error(f"解密微信支付V3数据失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="解密支付数据失败"
        )


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
        elif request.order_type == OrderType.MEMBER_MONTH:
            amount = settings.MEMBER_MONTHLY_PRICE
        elif request.order_type == OrderType.MEMBER_SEASON:
            amount = settings.MEMBER_QUARTERLY_PRICE
        elif request.order_type == OrderType.MEMBER_YEAR:
            amount = settings.MEMBER_YEARLY_PRICE
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单类型不正确"
            )

        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        is_member = user and user.is_member

        # 会员订单：无需 resource，直接创建订单
        if request.order_type in (OrderType.MEMBER_MONTH, OrderType.MEMBER_SEASON, OrderType.MEMBER_YEAR):
            pkg_id = request.order_type.value.replace("member_", "")
            order = Order(
                user_id=user_id,
                order_no=generate_order_no(),
                order_type=request.order_type.value,
                resource_type=None,
                resource_id=None,
                amount=amount,
                status=OrderStatus.PENDING,
                payment_method="wechat",
                order_metadata={"package_id": pkg_id}
            )
            db.add(order)
            await db.commit()
            await db.refresh(order)
            logger.info(f"创建会员订单成功: {order.order_no}, 金额: {amount}")
            return CreateOrderResponse(
                order_id=order.id,
                order_no=order.order_no,
                order_type=order.order_type,
                amount=float(order.amount),
                status=order.status
            )

        # P2 监理订单：无需 resource，直接创建订单
        if request.order_type in (OrderType.SUPERVISION_SINGLE, OrderType.SUPERVISION_PACKAGE):
            order = Order(
                user_id=user_id,
                order_no=generate_order_no(),
                order_type=request.order_type.value,
                resource_type=None,
                resource_id=None,
                amount=amount,
                status=OrderStatus.PENDING,
                payment_method="wechat",
                order_metadata={"product": request.order_type.value}
            )
            db.add(order)
            await db.commit()
            await db.refresh(order)
            logger.info(f"创建监理订单成功: {order.order_no}, 金额: {amount}")
            return CreateOrderResponse(
                order_id=order.id,
                order_no=order.order_no,
                order_type=order.order_type,
                amount=float(order.amount),
                status=order.status
            )

        # 报告解锁订单：必须带 resource_type 和 resource_id
        if not request.resource_type or request.resource_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="报告解锁订单需提供 resource_type 和 resource_id"
            )

        if request.resource_type == "quote":
            result = await db.execute(
                select(Quote).where(Quote.id == request.resource_id, Quote.user_id == user_id)
            )
            resource = result.scalar_one_or_none()
            if not resource:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报价单不存在")
            if is_member and not resource.is_unlocked:
                resource.is_unlocked = True
                resource.unlock_type = "member"
                await db.commit()
                logger.info(f"会员无限解锁: 报价单 {request.resource_id}, 用户 {user_id}")
                return CreateOrderResponse(
                    order_id=0, order_no="MEMBER_FREE", order_type=request.order_type.value,
                    amount=0.0, status="completed"
                )
        elif request.resource_type == "contract":
            result = await db.execute(
                select(Contract).where(Contract.id == request.resource_id, Contract.user_id == user_id)
            )
            resource = result.scalar_one_or_none()
            if not resource:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="合同不存在")
            if is_member and not resource.is_unlocked:
                resource.is_unlocked = True
                resource.unlock_type = "member"
                await db.commit()
                logger.info(f"会员无限解锁: 合同 {request.resource_id}, 用户 {user_id}")
                return CreateOrderResponse(
                    order_id=0, order_no="MEMBER_FREE", order_type=request.order_type.value,
                    amount=0.0, status="completed"
                )
        elif request.resource_type == "company":
            result = await db.execute(
                select(CompanyScan).where(CompanyScan.id == request.resource_id, CompanyScan.user_id == user_id)
            )
            resource = result.scalar_one_or_none()
            if not resource:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公司检测记录不存在")
            if is_member and not getattr(resource, "is_unlocked", False):
                resource.is_unlocked = True
                resource.unlock_type = "member"
                await db.commit()
                logger.info(f"会员无限解锁: 公司检测 {request.resource_id}, 用户 {user_id}")
                return CreateOrderResponse(
                    order_id=0, order_no="MEMBER_FREE", order_type=request.order_type.value,
                    amount=0.0, status="completed"
                )
        elif request.resource_type == "acceptance":
            result = await db.execute(
                select(AcceptanceAnalysis).where(
                    AcceptanceAnalysis.id == request.resource_id,
                    AcceptanceAnalysis.user_id == user_id,
                    AcceptanceAnalysis.deleted_at.is_(None)
                )
            )
            resource = result.scalar_one_or_none()
            if not resource:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="验收报告不存在")
            if is_member and not getattr(resource, "is_unlocked", False):
                resource.is_unlocked = True
                resource.unlock_type = "member"
                await db.commit()
                logger.info(f"会员无限解锁: 验收报告 {request.resource_id}, 用户 {user_id}")
                return CreateOrderResponse(
                    order_id=0, order_no="MEMBER_FREE", order_type=request.order_type.value,
                    amount=0.0, status="completed"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="资源类型不正确，支持 quote/contract/company/acceptance"
            )

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
            amount=float(order.amount),
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


class ConfirmPaidRequest(BaseModel):
    """支付确认请求（开发/联调用：模拟支付成功；生产可由微信回调后调用相同逻辑）"""
    order_id: int


async def _grant_order_benefits(order: Order, db: AsyncSession) -> None:
    """订单支付成功后发放权益（报告解锁/会员/监理仅更新订单状态）。与 confirm_paid / payment_notify 共用。"""
    user_id = order.user_id
    ot = order.order_type or ""
    if ot in ("report_single", "report_package") and order.resource_type and order.resource_id is not None:
        if order.resource_type == "quote":
            r = await db.execute(select(Quote).where(Quote.id == order.resource_id, Quote.user_id == user_id))
            obj = r.scalar_one_or_none()
            if obj:
                obj.is_unlocked = True
                obj.unlock_type = "single" if ot == "report_single" else "package"
        elif order.resource_type == "contract":
            r = await db.execute(select(Contract).where(Contract.id == order.resource_id, Contract.user_id == user_id))
            obj = r.scalar_one_or_none()
            if obj:
                obj.is_unlocked = True
                obj.unlock_type = "single" if ot == "report_single" else "package"
        elif order.resource_type == "company":
            r = await db.execute(select(CompanyScan).where(CompanyScan.id == order.resource_id, CompanyScan.user_id == user_id))
            obj = r.scalar_one_or_none()
            if obj:
                obj.is_unlocked = True
                obj.unlock_type = "single"
        elif order.resource_type == "acceptance":
            r = await db.execute(
                select(AcceptanceAnalysis).where(
                    AcceptanceAnalysis.id == order.resource_id,
                    AcceptanceAnalysis.user_id == user_id,
                    AcceptanceAnalysis.deleted_at.is_(None)
                )
            )
            obj = r.scalar_one_or_none()
            if obj:
                obj.is_unlocked = True
                obj.unlock_type = "single"
    elif ot in ("member_month", "member_season", "member_year"):
        months = 1 if ot == "member_month" else (3 if ot == "member_season" else 12)
        r = await db.execute(select(User).where(User.id == user_id))
        u = r.scalar_one_or_none()
        if u:
            u.is_member = True
            base = u.member_expire if u.member_expire and u.member_expire > datetime.now() else datetime.now()
            u.member_expire = base + relativedelta(months=months)
    # supervision_single / supervision_package：仅订单状态已更新，无需解锁资源


@router.post("/confirm-paid")
async def confirm_paid(
    request: ConfirmPaidRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    确认支付成功：将订单置为已支付并发放权益。
    开发环境：前端用户点击「确认支付」后调用，模拟微信支付成功。
    生产环境：应在微信支付回调中执行相同逻辑（更新订单 + 解锁资源/开通会员）。
    """
    try:
        result = await db.execute(
            select(Order).where(Order.id == request.order_id, Order.user_id == user_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
        if order.status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单状态不正确，仅待支付订单可确认"
            )

        order.status = OrderStatus.PAID.value
        order.paid_at = datetime.now()
        order.transaction_id = order.transaction_id or f"mock_{order.order_no}"
        await _grant_order_benefits(order, db)
        await db.commit()
        logger.info(f"确认支付成功: order_id={order.id}, order_no={order.order_no}, type={order.order_type}")
        return ApiResponse(code=0, msg="success", data={"order_id": order.id, "status": "paid"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"确认支付失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="确认支付失败"
        )


@router.post("/notify")
async def payment_notify(request: Request, db: AsyncSession = Depends(get_db)):
    """
    微信支付回调通知。支持V2和V3版本。
    
    V2版本：XML格式，包含 out_trade_no、transaction_id
    V3版本：JSON格式，包含加密的resource数据，需要解密
    
    与 confirm_paid 共用权益发放逻辑，确保回调后订单状态与权益一致。
    """
    try:
        import json as _json
        from xml.etree import ElementTree as ET
        
        raw = await request.body()
        raw_str = raw.decode('utf-8') if raw else ""
        
        # 初始化变量
        order_no = ""
        transaction_id = ""
        
        # 尝试解析V3 JSON格式
        try:
            v3_data = _json.loads(raw_str) if raw_str else {}
            
            # 检查是否是V3格式（包含resource字段）
            if "resource" in v3_data:
                resource = v3_data["resource"]
                associated_data = resource.get("associated_data", "")
                nonce = resource.get("nonce", "")
                ciphertext = resource.get("ciphertext", "")
                
                if ciphertext:
                    try:
                        # 解密V3数据
                        decrypted_data = decrypt_wechat_v3_data(associated_data, nonce, ciphertext)
                        decrypted_json = _json.loads(decrypted_data)
                        
                        # 从解密数据中获取订单信息
                        order_no = decrypted_json.get("out_trade_no", "")
                        transaction_id = decrypted_json.get("transaction_id", "")
                        
                        logger.info(f"微信支付V3回调数据解密成功: order_no={order_no}")
                    except Exception as decrypt_error:
                        logger.error(f"微信支付V3数据解密失败: {decrypt_error}")
                        return {"code": "FAIL", "message": "数据解密失败"}
                else:
                    # 如果没有加密数据，尝试直接从JSON获取
                    order_no = v3_data.get("out_trade_no", "") or v3_data.get("order_no", "")
                    transaction_id = v3_data.get("transaction_id", "")
            else:
                # 普通JSON格式
                order_no = v3_data.get("out_trade_no", "") or v3_data.get("order_no", "")
                transaction_id = v3_data.get("transaction_id", "")
                
        except _json.JSONDecodeError:
            # 不是JSON，尝试解析V2 XML格式
            try:
                if raw_str:
                    root = ET.fromstring(raw_str)
                    order_no_elem = root.find("out_trade_no")
                    transaction_id_elem = root.find("transaction_id")
                    
                    order_no = order_no_elem.text if order_no_elem is not None else ""
                    transaction_id = transaction_id_elem.text if transaction_id_elem is not None else ""
                    
                    logger.info(f"微信支付V2 XML回调解析成功: order_no={order_no}")
            except ET.ParseError:
                logger.warning("支付回调数据格式无法识别，既不是JSON也不是XML")
        
        # 验证订单号
        if not order_no:
            logger.warning("支付回调缺少订单号")
            return {"code": "FAIL", "message": "缺少订单号"}
        
        # 查找订单
        result = await db.execute(select(Order).where(Order.order_no == order_no))
        order = result.scalar_one_or_none()
        
        if not order:
            logger.warning(f"支付回调订单不存在: {order_no}")
            return {"code": "FAIL", "message": "订单不存在"}
        
        if order.status != OrderStatus.PENDING:
            logger.info(f"支付回调订单已处理: {order_no}, status={order.status}")
            return {"code": "SUCCESS", "message": "OK"}
        
        # 更新订单状态
        order.status = OrderStatus.PAID.value
        order.paid_at = datetime.now()
        order.transaction_id = transaction_id or f"wx_{order_no}"
        
        # 发放权益
        await _grant_order_benefits(order, db)
        await db.commit()
        
        logger.info(f"支付回调处理成功: order_no={order_no}, order_id={order.id}, transaction_id={transaction_id}")
        
        # 返回微信支付要求的响应格式
        return {"code": "SUCCESS", "message": "OK"}
        
    except Exception as e:
        logger.error(f"支付回调处理失败: {e}", exc_info=True)
        return {"code": "FAIL", "message": "处理失败"}


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
