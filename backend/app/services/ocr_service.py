"""
装修决策Agent - 阿里云OCR服务
用于识别报价单、合同等文档内容

安全架构：使用ECS实例RAM角色自动获取临时凭证，无需AccessKey
"""
import base64
import logging
import io
from typing import Dict, Optional, List, Tuple
from PIL import Image, ImageFile
from alibabacloud_ocr_api20210707.client import Client as OcrClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ocr_api20210707 import models as ocr_models
from app.core.config import settings

logger = logging.getLogger(__name__)

# 允许加载大图片
ImageFile.LOAD_TRUNCATED_IMAGES = True


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

    def _optimize_image_for_ocr(self, image_data: bytes, max_height: int = 4000) -> Tuple[bytes, str, List[bytes]]:
        """
        优化图片以适应阿里云OCR要求
        
        Args:
            image_data: 原始图片数据
            max_height: 最大高度限制，超过此高度将分割图片（阿里云OCR建议不超过4000px）
            
        Returns:
            Tuple[优化后的图片数据, 图片格式, 分割后的图片数据列表]
        """
        try:
            # 打开图片
            image = Image.open(io.BytesIO(image_data))
            original_format = image.format or "JPEG"
            original_mode = image.mode
            original_size = image.size
            
            logger.info(f"原始图片: 格式={original_format}, 模式={original_mode}, 尺寸={original_size}")
            
            # 检查图片尺寸是否过大
            width, height = image.size
            max_total_pixels = 4000 * 4000  # 阿里云OCR建议的最大像素数
            
            if width * height > max_total_pixels:
                # 计算缩放比例
                scale_factor = (max_total_pixels / (width * height)) ** 0.5
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                logger.info(f"图片尺寸过大 ({width}x{height}={width*height}像素)，缩放至 {new_width}x{new_height}")
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                width, height = new_width, new_height
            
            # 转换为RGB模式（阿里云OCR要求）
            if original_mode != "RGB":
                logger.info(f"转换图片模式: {original_mode} -> RGB")
                if original_mode == "RGBA":
                    # 对于RGBA图片，创建白色背景
                    background = Image.new("RGB", image.size, (255, 255, 255))
                    # 处理透明度通道
                    if image.mode == 'RGBA':
                        r, g, b, a = image.split()
                        background.paste(image, mask=a)
                    else:
                        background.paste(image)
                    image = background
                elif original_mode == "P":
                    # 调色板模式，先转换为RGBA再转换为RGB
                    if image.info.get("transparency") is not None:
                        image = image.convert("RGBA")
                        background = Image.new("RGB", image.size, (255, 255, 255))
                        r, g, b, a = image.split()
                        background.paste(image, mask=a)
                        image = background
                    else:
                        image = image.convert("RGB")
                elif original_mode == "L":
                    # 灰度图转换为RGB
                    image = image.convert("RGB")
                else:
                    image = image.convert("RGB")
            
            # 检查图片尺寸
            logger.info(f"转换后图片尺寸: {width}x{height}")
            
            # 如果图片太高，进行分割（阿里云OCR对高度有限制）
            segments = []
            if height > max_height:
                logger.info(f"图片高度 {height} > {max_height}，进行分割")
                segment_count = (height + max_height - 1) // max_height  # 向上取整
                
                for i in range(segment_count):
                    top = i * max_height
                    bottom = min((i + 1) * max_height, height)
                    segment = image.crop((0, top, width, bottom))
                    
                    # 转换为JPEG格式（阿里云OCR兼容性最好）
                    buffered = io.BytesIO()
                    # 使用基线JPEG，避免渐进式JPEG导致OCR识别问题
                    segment.save(buffered, format="JPEG", quality=90, optimize=True, progressive=False)
                    segment_data = buffered.getvalue()
                    
                    # 检查图片大小是否超过阿里云限制（10MB）
                    if len(segment_data) > 10 * 1024 * 1024:
                        logger.warning(f"分割段 {i+1} 大小 {len(segment_data)} bytes 超过10MB，进行压缩")
                        # 压缩图片
                        segment = segment.resize((width, segment.height // 2), Image.Resampling.LANCZOS)
                        buffered = io.BytesIO()
                        segment.save(buffered, format="JPEG", quality=80, optimize=True, progressive=False)
                        segment_data = buffered.getvalue()
                    
                    segments.append(segment_data)
                    logger.info(f"分割段 {i+1}/{segment_count}: 尺寸={segment.size}, 大小={len(segment_data)} bytes")
                
                # 主图片使用第一段
                main_image_data = segments[0] if segments else None
            else:
                # 转换为JPEG格式（基线，非渐进式）
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG", quality=90, optimize=True, progressive=False)
                main_image_data = buffered.getvalue()
                
                # 检查图片大小是否超过阿里云限制
                if len(main_image_data) > 10 * 1024 * 1024:
                    logger.warning(f"图片大小 {len(main_image_data)} bytes 超过10MB，进行压缩")
                    # 压缩图片
                    scale_factor = (8 * 1024 * 1024 / len(main_image_data)) ** 0.5
                    new_width = int(width * scale_factor)
                    new_height = int(height * scale_factor)
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG", quality=85, optimize=True, progressive=False)
                    main_image_data = buffered.getvalue()
                
                segments = [main_image_data]
            
            logger.info(f"优化完成: 主图片大小={len(main_image_data)} bytes, 总段数={len(segments)}")
            return main_image_data, "JPEG", segments
            
        except Exception as e:
            logger.error(f"图片优化失败: {e}", exc_info=True)
            # 如果优化失败，返回原始数据，但尝试转换为JPEG格式
            try:
                # 尝试直接转换为JPEG
                image = Image.open(io.BytesIO(image_data))
                if image.mode != "RGB":
                    image = image.convert("RGB")
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG", quality=85, optimize=True, progressive=False)
                jpeg_data = buffered.getvalue()
                logger.warning(f"图片优化失败，使用原始数据转换为JPEG: {len(jpeg_data)} bytes")
                return jpeg_data, "JPEG", [jpeg_data]
            except:
                logger.error(f"无法转换图片为JPEG，返回原始数据")
                return image_data, "JPEG", [image_data]

    def _prepare_ocr_input(self, file_url: str) -> Tuple[str, str, List[str]]:
        """
        准备OCR输入数据，包括优化图片和分割处理
        
        Args:
            file_url: 文件URL或Base64编码
            
        Returns:
            Tuple[主输入数据, 输入类型, 所有分割段的输入数据列表]
        """
        try:
            input_type = "Unknown"
            base64_data = None
            
            # 提取Base64数据
            if file_url.startswith("data:"):
                # data URL格式
                if "," in file_url:
                    base64_data = file_url.split(",")[1]
                    mime_type = file_url.split(",")[0].split(":")[1].split(";")[0]
                    logger.info(f"从data URL提取Base64数据，MIME类型: {mime_type}")
                else:
                    # 如果没有逗号，可能是纯Base64数据
                    base64_data = file_url[5:] if file_url.startswith("data:") else file_url
                input_type = "Base64 (data URL)"
            elif file_url.startswith("http"):
                # URL格式，直接返回
                logger.info(f"使用URL输入: {file_url[:50]}...")
                return file_url, "URL", [file_url]
            else:
                # 纯Base64
                base64_data = file_url
                input_type = "Base64 (raw)"
            
            if base64_data:
                # 清理Base64数据（移除换行符和空格）
                cleaned_base64 = base64_data.replace("\n", "").replace("\r", "").replace(" ", "")
                
                # 检查Base64长度是否为4的倍数（Base64要求）
                padding_needed = len(cleaned_base64) % 4
                if padding_needed:
                    cleaned_base64 += "=" * (4 - padding_needed)
                    logger.info(f"Base64数据补全: 原长度{len(base64_data)}，补全后{len(cleaned_base64)}")
                
                # 解码Base64
                try:
                    image_data = base64.b64decode(cleaned_base64, validate=True)
                    logger.info(f"Base64解码成功: {len(image_data)} bytes")
                    
                    # 检查图片数据是否有效
                    if len(image_data) == 0:
                        logger.error("Base64解码后图片数据为空")
                        return file_url, input_type, [file_url]
                    
                    # 优化图片
                    optimized_data, image_format, segments = self._optimize_image_for_ocr(image_data)
                    
                    # 转换为Base64格式
                    segments_base64 = []
                    for i, segment_data in enumerate(segments):
                        segment_base64 = base64.b64encode(segment_data).decode("utf-8")
                        # 确保Base64格式正确
                        segments_base64.append(f"data:image/{image_format.lower()};base64,{segment_base64}")
                    
                    main_input = segments_base64[0]
                    logger.info(f"准备完成: 输入类型={input_type}, 图片格式={image_format}, 段数={len(segments)}")
                    return main_input, input_type, segments_base64
                    
                except base64.binascii.Error as e:
                    logger.error(f"Base64格式错误: {e}")
                    # 尝试使用原始数据（不清理）
                    try:
                        image_data = base64.b64decode(base64_data)
                        logger.info(f"使用原始Base64数据解码成功: {len(image_data)} bytes")
                        
                        # 优化图片
                        optimized_data, image_format, segments = self._optimize_image_for_ocr(image_data)
                        
                        # 转换为Base64格式
                        segments_base64 = []
                        for i, segment_data in enumerate(segments):
                            segment_base64 = base64.b64encode(segment_data).decode("utf-8")
                            segments_base64.append(f"data:image/{image_format.lower()};base64,{segment_base64}")
                        
                        main_input = segments_base64[0]
                        logger.info(f"使用原始数据准备完成: 输入类型={input_type}, 图片格式={image_format}, 段数={len(segments)}")
                        return main_input, input_type, segments_base64
                    except Exception as e2:
                        logger.error(f"原始Base64数据也解码失败: {e2}")
                        return file_url, input_type, [file_url]
                except Exception as e:
                    logger.error(f"Base64解码或优化失败: {e}")
                    # 如果失败，返回原始输入
                    return file_url, input_type, [file_url]
            
            return file_url, input_type, [file_url]
            
        except Exception as e:
            logger.error(f"准备OCR输入失败: {e}", exc_info=True)
            return file_url, "Unknown", [file_url]

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
            
            # 准备OCR输入（包括图片优化和分割）
            main_input, input_type, all_segments = self._prepare_ocr_input(file_url)
            logger.info(f"OCR输入准备完成: 类型={input_type}, 总段数={len(all_segments)}")
            
            # 如果有多段，分别识别
            all_text = ""
            all_errors = []
            
            for i, segment_input in enumerate(all_segments):
                segment_num = i + 1
                total_segments = len(all_segments)
                
                try:
                    logger.info(f"识别第 {segment_num}/{total_segments} 段")
                    
                    # 构建请求 - 使用OCR统一识别API
                    request = ocr_models.RecognizeAllTextRequest()

                    # 判断是URL还是Base64
                    if segment_input.startswith("http"):
                        request.url = segment_input
                    else:
                        # Base64数据
                        if segment_input.startswith("data:"):
                            if "," in segment_input:
                                base64_part = segment_input.split(",")[1]
                                request.body = base64_part
                            else:
                                request.body = segment_input
                        else:
                            request.body = segment_input

                    # 强制使用General类型，避免Advanced类型的参数兼容性问题
                    request.type = "General"
                    
                    # 对于General类型，只设置必要的参数，避免API兼容性问题
                    # General类型不支持output_coordinate、output_qrcode、output_bar_code等参数
                    # 所以不设置这些参数，让API使用默认值
                    
                    response = self.client.recognize_all_text(request)
                    text_content = response.body.data.content
                    
                    all_text += text_content + "\n"
                    logger.info(f"第 {segment_num}/{total_segments} 段识别成功，文本长度: {len(text_content)}")
                    
                except Exception as segment_error:
                    error_msg = str(segment_error)
                    error_detail = ""
                    
                    if hasattr(segment_error, 'response'):
                        try:
                            if hasattr(segment_error.response, 'body'):
                                error_detail = str(segment_error.response.body)
                        except:
                            pass
                    
                    logger.error(f"第 {segment_num}/{total_segments} 段识别失败: {error_msg}")
                    all_errors.append(f"段{segment_num}: {error_msg}")
                    
                    # 如果是第一段失败且是格式错误，尝试使用原始数据重试
                    if i == 0 and ("unsupportedImageFormat" in error_msg or "415" in error_detail):
                        logger.warning("检测到图片格式错误，尝试使用原始Base64数据重试")
                        try:
                            # 直接使用原始Base64数据
                            if file_url.startswith("data:"):
                                if "," in file_url:
                                    raw_base64 = file_url.split(",")[1]
                                else:
                                    raw_base64 = file_url
                            else:
                                raw_base64 = file_url
                            
                            retry_request = ocr_models.RecognizeAllTextRequest()
                            retry_request.body = raw_base64
                            retry_request.type = "General"
                            
                            response = self.client.recognize_all_text(retry_request)
                            text_content = response.body.data.content
                            all_text = text_content + "\n"
                            logger.info(f"原始数据重试成功，文本长度: {len(text_content)}")
                            break  # 跳出循环，不再处理其他段
                        except Exception as retry_error:
                            logger.error(f"原始数据重试也失败: {retry_error}")
            
            if not all_text and all_errors:
                logger.error(f"所有段识别都失败: {', '.join(all_errors)}")
                return None
            
            result = {
                "text": all_text.strip(),
                "prism_words_info": [],
                "ocr_type": ocr_type,
                "segments_processed": len(all_segments),
                "errors_encountered": len(all_errors)
            }

            logger.info(f"OCR统一识别成功，OCR类型: {ocr_type}, 文本长度: {len(result['text'])}, 处理段数: {len(all_segments)}")
            return result

        except Exception as e:
            error_msg = str(e)
            error_detail = ""
            error_code = ""
            error_type = type(e).__name__
            
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
                f"详细信息: {error_detail}",
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
