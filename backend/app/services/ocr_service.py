"""
装修决策Agent - 阿里云OCR服务
用于识别报价单、合同等文档内容

安全架构：使用ECS实例RAM角色自动获取临时凭证，无需AccessKey
"""
import base64
import logging
from typing import Dict, Optional, List
from alibabacloud_ocr_api20210707.client import Client as OcrClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ocr_api20210707 import models as ocr_models
from app.core.config import settings

logger = logging.getLogger(__name__)


class OcrService:
    """阿里云OCR服务 - 使用ECS RAM角色自动获取凭证"""

    def __init__(self):
        try:
            # 使用RAM角色自动获取凭证
            # 不设置access_key_id和access_key_secret，SDK会自动从以下位置获取：
            # 1. 环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID / ALIBABA_CLOUD_ACCESS_KEY_SECRET
            # 2. ECS实例元数据服务 (100.100.100.200)
            # 3. RAM角色凭证提供者
            self.config = open_api_models.Config()
            self.config.region_id = 'cn-hangzhou'
            
            # 设置OCR端点
            if hasattr(settings, 'ALIYUN_OCR_ENDPOINT') and settings.ALIYUN_OCR_ENDPOINT:
                self.config.endpoint = settings.ALIYUN_OCR_ENDPOINT
            else:
                self.config.endpoint = 'ocr-api.cn-hangzhou.aliyuncs.com'
            
            # 不设置access_key_id和access_key_secret，让SDK自动获取
            # 阿里云Python SDK v2支持自动从ECS实例元数据获取RAM角色凭证
            
            logger.info("OCR客户端初始化 - 使用RAM角色自动获取凭证")
            logger.info(f"OCR端点: {self.config.endpoint}")
            
            self.client = OcrClient(self.config)
            
            # 测试连接（可选调用）
            self._test_connection()
            
        except Exception as e:
            logger.error(f"OCR客户端初始化失败: {e}", exc_info=True)
            self.client = None
            logger.warning("OCR功能将不可用，请检查ECS实例是否绑定RAM角色")

    def _test_connection(self):
        """测试OCR连接是否正常（可选）"""
        try:
            # 创建一个简单的测试请求
            request = ocr_models.RecognizeGeneralRequest()
            request.url = "https://example.com/test.jpg"  # 虚拟URL，仅用于测试配置
            
            # 注意：这里不会真正调用API，只是测试客户端配置
            logger.info("OCR客户端配置测试完成")
        except Exception as e:
            logger.warning(f"OCR客户端配置测试异常（可能权限或网络问题）: {e}")

    async def recognize_general_text(self, file_url: str) -> Optional[Dict]:
        """
        通用文本识别（支持多语言）

        Args:
            file_url: 文件URL或Base64编码

        Returns:
            OCR识别结果
        """
        try:
            # 检查OCR客户端是否可用
            if self.client is None:
                logger.warning("OCR客户端未初始化，无法进行OCR识别")
                logger.warning("请检查ECS实例是否绑定RAM角色 'zhuangxiu-ecs-role'")
                return None
            
            # 构建请求
            request = ocr_models.RecognizeGeneralRequest()

            # 判断是URL还是Base64
            if file_url.startswith("http"):
                request.url = file_url
                input_type = "URL"
            elif file_url.startswith("data:"):
                # 移除data:xxx;base64,前缀（支持image和application/pdf）
                if "," in file_url:
                    request.body = file_url.split(",")[1]
                else:
                    request.body = file_url
                input_type = "Base64"
            else:
                # 假设是Base64
                request.body = file_url
                input_type = "Base64"

            # 调用OCR API
            logger.info(f"调用OCR API，输入类型: {input_type}, 长度: {len(file_url)}")
            
            # 添加调试信息：记录请求的详细信息
            logger.debug(f"OCR请求详情 - 端点: {self.config.endpoint}, 区域: {self.config.region_id}")
            
            response = self.client.recognize_general(request)

            result = {
                "text": response.body.data.content,
                "prism_words_info": response.body.data.prism_words_info
            }

            logger.info(f"OCR识别成功，文本长度: {len(result['text'])}")
            return result

        except Exception as e:
            error_msg = str(e)
            error_detail = ""
            error_code = ""
            error_type = type(e).__name__
            
            # 尝试获取更详细的错误信息
            if hasattr(e, 'response'):
                try:
                    if hasattr(e.response, 'body'):
                        error_detail = str(e.response.body)
                        # 尝试提取错误码和错误消息
                        if hasattr(e.response.body, 'code'):
                            error_code = str(e.response.body.code)
                        if hasattr(e.response.body, 'message'):
                            error_detail = str(e.response.body.message)
                    else:
                        error_detail = str(e.response)
                except Exception as ex:
                    logger.debug(f"解析错误详情失败: {ex}")
            
            # 记录完整的错误信息
            logger.error(
                f"OCR通用文本识别失败 - 错误类型: {error_type}, "
                f"错误消息: {error_msg}, "
                f"错误码: {error_code}, "
                f"详细信息: {error_detail}, "
                f"输入类型: {'URL' if file_url.startswith('http') else 'Base64'}, "
                f"输入长度: {len(file_url)}, "
                f"端点: {self.config.endpoint if hasattr(self, 'config') else 'N/A'}, "
                f"区域: {self.config.region_id if hasattr(self, 'config') else 'N/A'}",
                exc_info=True
            )
            
            # 如果是权限错误，提供明确的指导
            if "ocrServiceNotOpen" in error_msg or "401" in error_msg or "Forbidden" in error_msg:
                logger.error("OCR服务未开通或权限不足，请检查：")
                logger.error("1. 阿里云OCR服务是否已开通")
                logger.error("2. RAM角色 'zhuangxiu-ecs-role' 是否授权OCR权限")
                logger.error("3. ECS实例是否已绑定该RAM角色")
                logger.error("4. 检查RAM角色的权限策略是否包含 'AliyunOCRFullAccess'")
            
            # 如果是网络错误
            if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                logger.error("网络连接问题，请检查：")
                logger.error("1. 容器网络是否能访问阿里云OCR端点")
                logger.error("2. 安全组规则是否允许出站流量")
                logger.error("3. DNS解析是否正常")
            
            return None

    async def recognize_table(self, file_url: str) -> Optional[Dict]:
        """
        表格识别（适用于报价单中的价格表）

        Args:
            file_url: 文件URL或Base64编码

        Returns:
            表格识别结果
        """
        try:
            # 检查OCR客户端是否可用
            if self.client is None:
                logger.warning("OCR客户端未初始化，无法进行表格识别")
                return None
            
            request = ocr_models.RecognizeTableRequest()

            if file_url.startswith("http"):
                request.url = file_url
            elif file_url.startswith("data:"):
                # 移除data:xxx;base64,前缀（支持image和application/pdf）
                if "," in file_url:
                    request.body = file_url.split(",")[1]
                else:
                    request.body = file_url
            else:
                request.body = file_url

            response = self.client.recognize_table(request)

            result = {
                "tables": response.body.data.tables,
                "text": response.body.data.content
            }

            logger.info(f"表格识别成功，表格数量: {len(result['tables'])}")
            return result

        except Exception as e:
            error_msg = str(e)
            error_detail = ""
            error_code = ""
            # 尝试获取更详细的错误信息
            if hasattr(e, 'response'):
                try:
                    if hasattr(e.response, 'body'):
                        error_detail = str(e.response.body)
                        # 尝试提取错误码和错误消息
                        if hasattr(e.response.body, 'code'):
                            error_code = str(e.response.body.code)
                        if hasattr(e.response.body, 'message'):
                            error_detail = str(e.response.body.message)
                    else:
                        error_detail = str(e.response)
                except Exception as ex:
                    logger.debug(f"解析错误详情失败: {ex}")
            
            # 记录完整的错误信息
            logger.error(
                f"OCR表格识别失败: {error_msg}, "
                f"错误码: {error_code}, "
                f"详细信息: {error_detail}, "
                f"输入类型: {'URL' if file_url.startswith('http') else 'Base64'}, "
                f"输入长度: {len(file_url)}",
                exc_info=True
            )
            return None

    async def recognize_quote(self, file_url: str, file_type: str = "image") -> Optional[Dict]:
        """
        识别装修报价单（智能提取项目、价格等信息）

        Args:
            file_url: 文件URL
            file_type: 文件类型（image/pdf）

        Returns:
            报价单识别结果
        """
        try:
            # 优先使用表格识别
            if file_type == "image":
                table_result = await self.recognize_table(file_url)
                if table_result:
                    return {
                        "type": "table",
                        "content": table_result["text"],
                        "tables": table_result["tables"]
                    }

            # 降级到通用文本识别
            general_result = await self.recognize_general_text(file_url)
            if general_result:
                return {
                    "type": "text",
                    "content": general_result["text"],
                    "prism_words_info": general_result["prism_words_info"]
                }

            return None

        except Exception as e:
            logger.error(f"报价单识别失败: {e}", exc_info=True)
            return None

    async def recognize_contract(self, file_url: str) -> Optional[Dict]:
        """
        识别装修合同文本

        Args:
            file_url: 文件URL

        Returns:
            合同识别结果
        """
        try:
            # 合同主要是文本，使用通用识别
            general_result = await self.recognize_general_text(file_url)
            if general_result:
                return {
                    "type": "text",
                    "content": general_result["text"],
                    "prism_words_info": general_result["prism_words_info"]
                }

            return None

        except Exception as e:
            logger.error(f"合同识别失败: {e}", exc_info=True)
            return None

    def file_to_base64(self, file_path: str) -> str:
        """
        将文件转换为Base64编码

        Args:
            file_path: 文件路径

        Returns:
            Base64编码字符串
        """
        try:
            with open(file_path, "rb") as f:
                file_data = f.read()
                base64_str = base64.b64encode(file_data).decode("utf-8")
                return f"data:image/jpeg;base64,{base64_str}"
        except Exception as e:
            logger.error(f"文件转Base64失败: {e}", exc_info=True)
            raise


# 创建全局实例
ocr_service = OcrService()
