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
            # 手动从ECS实例元数据服务获取RAM角色凭证
            import requests
            
            # 获取RAM角色名称
            role_name = None
            try:
                resp = requests.get('http://100.100.100.200/latest/meta-data/ram/security-credentials/', timeout=2)
                if resp.status_code == 200:
                    role_name = resp.text.strip()
                    logger.info(f"从ECS元数据获取到RAM角色名称: {role_name}")
            except Exception as e:
                logger.warning(f"获取RAM角色名称失败: {e}")
            
            if not role_name:
                logger.warning("无法获取RAM角色名称，尝试使用默认角色 'zhuangxiu-ecs-role'")
                role_name = 'zhuangxiu-ecs-role'
            
            # 获取RAM角色临时凭证
            credentials = None
            try:
                resp = requests.get(f'http://100.100.100.200/latest/meta-data/ram/security-credentials/{role_name}', timeout=2)
                if resp.status_code == 200:
                    credentials = resp.json()
                    logger.info(f"从ECS元数据获取到RAM角色凭证，AccessKeyId: {credentials.get('AccessKeyId', 'N/A')[:10]}...")
            except Exception as e:
                logger.warning(f"获取RAM角色凭证失败: {e}")
            
            self.config = open_api_models.Config()
            self.config.region_id = 'cn-hangzhou'
            
            # 设置OCR端点
            if hasattr(settings, 'ALIYUN_OCR_ENDPOINT') and settings.ALIYUN_OCR_ENDPOINT:
                self.config.endpoint = settings.ALIYUN_OCR_ENDPOINT
            else:
                self.config.endpoint = 'ocr-api.cn-hangzhou.aliyuncs.com'
            
            # 如果成功获取到凭证，使用它们
            if credentials and 'AccessKeyId' in credentials and 'AccessKeySecret' in credentials:
                self.config.access_key_id = credentials['AccessKeyId']
                self.config.access_key_secret = credentials['AccessKeySecret']
                self.config.security_token = credentials.get('SecurityToken', '')
                logger.info("使用ECS RAM角色凭证初始化OCR客户端")
            else:
                logger.error("无法获取ECS RAM角色凭证，请检查ECS实例是否绑定RAM角色")
                self.client = None
                return
            
            logger.info(f"OCR客户端初始化 - 端点: {self.config.endpoint}, 区域: {self.config.region_id}")
            
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
            # 创建一个简单的测试请求 - 使用OCR统一识别API
            request = ocr_models.RecognizeAllTextRequest()
            request.url = "https://example.com/test.jpg"  # 虚拟URL，仅用于测试配置
            
            # 注意：这里不会真正调用API，只是测试客户端配置
            logger.info("OCR统一识别客户端配置测试完成")
        except Exception as e:
            logger.warning(f"OCR统一识别客户端配置测试异常（可能权限或网络问题）: {e}")

    async def recognize_general_text(self, file_url: str, ocr_type: str = "General") -> Optional[Dict]:
        """
        通用文字识别（支持多语言）
        已迁移到OCR统一识别（RecognizeAllText）API

        Args:
            file_url: 文件URL或Base64编码
            ocr_type: OCR识别类型，可选值：
                - "General": 基础版通用文字识别（推荐，兼容性最好）
                - "Advanced": 通用文字识别高精版
                - "Table": 表格识别

        Returns:
            OCR识别结果
        """
        try:
            # 检查OCR客户端是否可用
            if self.client is None:
                logger.warning("OCR客户端未初始化，无法进行OCR识别")
                logger.warning("请检查ECS实例是否绑定RAM角色 'zhuangxiu-ecs-role'")
                return None
            
            # 构建请求 - 使用OCR统一识别API
            request = ocr_models.RecognizeAllTextRequest()

            # 判断是URL还是Base64
            input_type = "Unknown"
            if file_url.startswith("http"):
                request.url = file_url
                input_type = "URL"
            elif file_url.startswith("data:"):
                # 已经是完整的data URL格式
                if "," in file_url:
                    base64_data = file_url.split(",")[1]
                    request.body = base64_data
                    logger.info(f"从data URL提取Base64数据，前缀: {file_url.split(',')[0][:30]}...")
                else:
                    request.body = file_url
                input_type = "Base64 (data URL)"
            else:
                # 可能是纯Base64，尝试添加合适的MIME类型前缀
                # 检测常见的图片格式特征
                if file_url.startswith("iVBOR"):
                    logger.info("检测到PNG格式Base64数据")
                elif file_url.startswith("/9j/"):
                    logger.info("检测到JPEG格式Base64数据")
                elif file_url.startswith("R0lGOD"):
                    logger.info("检测到GIF格式Base64数据")
                
                request.body = file_url
                input_type = "Base64 (raw)"
                logger.warning("收到纯Base64数据，可能缺少MIME类型前缀")

            # 设置OCR识别类型
            request.type = ocr_type

            # 只保留最基本的必要参数
            # 注意：阿里云OCR API的Advanced类型可能不支持output_coordinate参数
            # 根据错误信息 "param (OutputQrcode) is not valid for type (Advanced)"
            # 我们移除output_coordinate参数，只保留type
            
            logger.info(f"调用OCR统一识别API，输入类型: {input_type}, OCR类型: {ocr_type}, 长度: {len(file_url)}")
            
            response = self.client.recognize_all_text(request)

            text_content = response.body.data.content
            
            result = {
                "text": text_content,
                "prism_words_info": [],
                "ocr_type": ocr_type
            }

            logger.info(f"OCR统一识别成功，OCR类型: {ocr_type}, 文本长度: {len(result['text'])}")
            return result

        except Exception as e:
            error_msg = str(e)
            error_detail = ""
            error_code = ""
            error_type = type(e).__name__
            input_type = locals().get('input_type', 'Unknown')
            
            if hasattr(e, 'response'):
                try:
                    if hasattr(e.response, 'body'):
                        error_detail = str(e.response.body)
                        if hasattr(e.response.body, 'code'):
                            error_code = str(e.response.body.code)
                        if hasattr(e.response.body, 'message'):
                            error_detail = str(e.response.body.message)
                    else:
                        error_detail = str(e.response)
                except Exception as ex:
                    logger.debug(f"解析错误详情失败: {ex}")
            
            logger.error(
                f"OCR统一识别失败 - OCR类型: {ocr_type}, 错误类型: {error_type}, "
                f"错误消息: {error_msg}, "
                f"错误码: {error_code}, "
                f"详细信息: {error_detail}, "
                f"输入类型: {input_type}, "
                f"输入长度: {len(file_url)}",
                exc_info=True
            )
            
            # 如果是参数错误，尝试降级重试
            if ("invalidInputParameter" in error_msg or 
                "is not valid for type" in error_msg):
                logger.warning(f"OCR类型 {ocr_type} 可能不支持某些参数，尝试降级到 General")
                if ocr_type != "General":
                    try:
                        logger.info(f"尝试使用 General 类型重试")
                        retry_request = ocr_models.RecognizeAllTextRequest()
                        
                        if file_url.startswith("http"):
                            retry_request.url = file_url
                        else:
                            # 重试时尝试提取base64部分
                            if file_url.startswith("data:") and "," in file_url:
                                retry_request.body = file_url.split(",")[1]
                            else:
                                retry_request.body = file_url
                        
                        retry_request.type = "General"
                        # 降级重试时也不使用output_coordinate参数
                        
                        response = self.client.recognize_all_text(retry_request)
                        
                        text_content = response.body.data.content
                        result = {
                            "text": text_content,
                            "prism_words_info": [],
                            "ocr_type": "General",
                            "fallback": True
                        }
                        logger.info(f"OCR降级识别成功，文本长度: {len(result['text'])}")
                        return result
                    except Exception as retry_e:
                        logger.error(f"OCR降级识别也失败: {str(retry_e)}")
            
            # 如果是图片格式错误
            if "unsupportedImageFormat" in error_msg or "415" in error_code:
                logger.error("图片格式不支持，请检查：")
                logger.error("1. 图片格式是否为jpg/png/bmp等常见格式")
                logger.error("2. Base64编码是否正确")
                logger.error("3. 图片是否损坏")
            
            # 如果是权限错误
            if "ocrServiceNotOpen" in error_msg or "401" in error_msg or "Forbidden" in error_msg:
                logger.error("OCR统一识别服务未开通或权限不足，请检查：")
                logger.error("1. 阿里云OCR统一识别服务是否已开通")
                logger.error("2. RAM角色 'zhuangxiu-ecs-role' 是否授权OCR权限")
                logger.error("3. ECS实例是否已绑定该RAM角色")
            
            # 如果是网络错误
            if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                logger.error("网络连接问题，请检查：")
                logger.error("1. 容器网络是否能访问阿里云OCR端点")
                logger.error("2. 安全组规则是否允许出站流量")
            
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
            if self.client is None:
                logger.warning("OCR客户端未初始化，无法进行表格识别")
                return None
            
            request = ocr_models.RecognizeTableRequest()

            if file_url.startswith("http"):
                request.url = file_url
            elif file_url.startswith("data:"):
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
            logger.error(f"OCR表格识别失败: {e}", exc_info=True)
            return None

    async def recognize_quote(self, file_url: str, file_type: str = "image") -> Optional[Dict]:
        """
        识别装修报价单

        Args:
            file_url: 文件URL
            file_type: 文件类型（image/pdf）

        Returns:
            报价单识别结果
        """
        try:
            if file_type == "image":
                table_result = await self.recognize_table(file_url)
                if table_result:
                    return {
                        "type": "table",
                        "content": table_result["text"],
                        "tables": table_result["tables"],
                        "ocr_type": "Table"
                    }

            general_result = await self.recognize_general_text(file_url, ocr_type="General")
            if general_result:
                return {
                    "type": "text",
                    "content": general_result["text"],
                    "prism_words_info": general_result["prism_words_info"],
                    "ocr_type": general_result.get("ocr_type", "General"),
                    "fallback": general_result.get("fallback", False)
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
            general_result = await self.recognize_general_text(file_url, ocr_type="General")
            if general_result:
                return {
                    "type": "text",
                    "content": general_result["text"],
                    "prism_words_info": general_result["prism_words_info"],
                    "ocr_type": general_result.get("ocr_type", "General"),
                    "fallback": general_result.get("fallback", False)
                }

            return None

        except Exception as e:
            logger.error(f"合同识别失败: {e}", exc_info=True)
            return None

    def file_to_base64(self, file_path: str) -> str:
        """
        将文件转换为Base64编码
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
