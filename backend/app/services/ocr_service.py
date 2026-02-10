"""
装修决策Agent - 阿里云OCR服务
用于识别报价单、合同等文档内容
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
    """阿里云OCR服务"""

    def __init__(self):
        # 检查OCR配置是否存在
        if not settings.ALIYUN_ACCESS_KEY_ID or not settings.ALIYUN_ACCESS_KEY_SECRET:
            logger.warning("OCR配置不存在，OCR功能将不可用")
            self.client = None
            return
        
        try:
            self.config = open_api_models.Config(
                access_key_id=settings.ALIYUN_ACCESS_KEY_ID,
                access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET
            )
            self.config.endpoint = settings.ALIYUN_OCR_ENDPOINT
            self.client = OcrClient(self.config)
        except Exception as e:
            logger.error(f"OCR客户端初始化失败: {e}", exc_info=True)
            self.client = None

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
                return None
            
            # 构建请求
            request = ocr_models.RecognizeGeneralRequest()

            # 判断是URL还是Base64
            if file_url.startswith("http"):
                request.url = file_url
            elif file_url.startswith("data:"):
                # 移除data:xxx;base64,前缀（支持image和application/pdf）
                if "," in file_url:
                    request.body = file_url.split(",")[1]
                else:
                    request.body = file_url
            else:
                # 假设是Base64
                request.body = file_url

            # 调用OCR API
            logger.info(f"调用OCR API，输入类型: {'URL' if file_url.startswith('http') else 'Base64'}, 长度: {len(file_url)}")
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
                f"OCR通用文本识别失败: {error_msg}, "
                f"错误码: {error_code}, "
                f"详细信息: {error_detail}, "
                f"输入类型: {'URL' if file_url.startswith('http') else 'Base64'}, "
                f"输入长度: {len(file_url)}",
                exc_info=True
            )
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
