#!/usr/bin/env python3
"""
移除DeepSeek API依赖的脚本
"""
import re

def remove_deepseek_dependencies(content):
    """移除DeepSeek API依赖"""
    
    # 1. 修改__init__方法中的DeepSeek客户端初始化
    content = re.sub(
        r'        # DeepSeek API作为备用服务\n        self\.deepseek_client = AsyncOpenAI\(\n            api_key=settings\.DEEPSEEK_API_KEY or "",\n            base_url=settings\.DEEPSEEK_API_BASE or "https://api\.deepseek\.com/v1"\n        \)\n        self\.use_deepseek = bool\(settings\.DEEPSEEK_API_KEY\)',
        '        # DeepSeek API已移除，不再使用\n        self.deepseek_client = None\n        self.use_deepseek = False',
        content
    )
    
    # 2. 修改__init__方法中的DeepSeek日志
    content = re.sub(
        r'            if self\.use_deepseek:\n                logger\.info\(f"DeepSeek API配置: 已启用"\)',
        '            if self.use_deepseek:\n                logger.info(f"DeepSeek API配置: 已移除，不再使用")',
        content
    )
    
    # 3. 修改analyze_quote方法，去掉降级使用DeepSeek的逻辑
    content = re.sub(
        r'            # 尝试扣子服务\n            result = None\n            if self\.use_site_api:\n                result = await self\._call_site_api\(image_url, prompt, user_id\)\n                if not result and self\.use_deepseek:\n                    logger\.info\("扣子站点API调用失败，降级使用DeepSeek API"\)\n                    result = await self\._call_deepseek_api\(image_url, prompt, user_id\)\n            elif self\.use_open_api:\n                result = await self\._call_open_api\(image_url, prompt, user_id\)\n                if not result and self\.use_deepseek:\n                    logger\.info\("扣子开放平台API调用失败，降级使用DeepSeek API"\)\n                    result = await self\._call_deepseek_api\(image_url, prompt, user_id\)\n            elif self\.use_deepseek:\n                result = await self\._call_deepseek_api\(image_url, prompt, user_id\)\n            else:\n                logger\.error\("AI分析服务配置不完整，无法调用"\)\n                return None',
        '            # 尝试扣子服务\n            result = None\n            if self.use_site_api:\n                result = await self._call_site_api(image_url, prompt, user_id)\n                if not result:\n                    logger.error("扣子站点API调用失败，没有备用服务")\n            elif self.use_open_api:\n                result = await self._call_open_api(image_url, prompt, user_id)\n                if not result:\n                    logger.error("扣子开放平台API调用失败，没有备用服务")\n            else:\n                logger.error("AI分析服务配置不完整，无法调用")\n                return None',
        content
    )
    
    # 4. 修改analyze_contract方法，去掉降级使用DeepSeek的逻辑
    content = re.sub(
        r'            # 尝试扣子服务 - 使用与报价单相同的调用方式\n            result = None\n            if self\.use_site_api:\n                logger\.info\("使用扣子站点API分析合同"\)\n                result = await self\._call_site_api\(image_url, prompt, user_id\)\n                if result:\n                    logger\.info\(f"✅ 扣子站点API合同分析成功"\)\n                else:\n                    logger\.warning\("❌ 扣子站点API合同分析失败，尝试降级"\)\n                    if self\.use_deepseek:\n                        logger\.info\("降级使用DeepSeek API"\)\n                        result = await self\._call_deepseek_api\(image_url, prompt, user_id\)\n            elif self\.use_open_api:\n                logger\.info\("使用扣子开放平台API分析合同"\)\n                result = await self\._call_open_api\(image_url, prompt, user_id\)\n                if result:\n                    logger\.info\(f"✅ 扣子开放平台API合同分析成功"\)\n                else:\n                    logger\.warning\("❌ 扣子开放平台API合同分析失败，尝试降级"\)\n                    if self\.use_deepseek:\n                        logger\.info\("降级使用DeepSeek API"\)\n                        result = await self\._call_deepseek_api\(image_url, prompt, user_id\)\n            elif self\.use_deepseek:\n                logger\.info\("使用DeepSeek API分析合同"\)\n                result = await self\._call_deepseek_api\(image_url, prompt, user_id\)\n            else:\n                logger\.error\("❌ AI分析服务配置不完整，无法调用"\)\n                return self\._get_fallback_contract_analysis\(image_url\)',
        '            # 尝试扣子服务 - 使用与报价单相同的调用方式\n            result = None\n            if self.use_site_api:\n                logger.info("使用扣子站点API分析合同")\n                result = await self._call_site_api(image_url, prompt, user_id)\n                if result:\n                    logger.info(f"✅ 扣子站点API合同分析成功")\n                else:\n                    logger.error("❌ 扣子站点API合同分析失败，没有备用服务")\n            elif self.use_open_api:\n                logger.info("使用扣子开放平台API分析合同")\n                result = await self._call_open_api(image_url, prompt, user_id)\n                if result:\n                    logger.info(f"✅ 扣子开放平台API合同分析成功")\n                else:\n                    logger.error("❌ 扣子开放平台API合同分析失败，没有备用服务")\n            else:\n                logger.error("❌ AI分析服务配置不完整，无法调用")\n                return self._get_fallback_contract_analysis(image_url)',
        content
    )
    
    # 5. 修改analyze_acceptance方法，去掉降级使用DeepSeek的逻辑
    content = re.sub(
        r'            # 尝试扣子服务\n            result = None\n            if self\.use_site_api:\n                result = await self\._call_site_api\(image_url, prompt, user_id\)\n                if not result and self\.use_deepseek:\n                    logger\.info\("扣子站点API调用失败，降级使用DeepSeek API"\)\n                    result = await self\._call_deepseek_api\(image_url, prompt, user_id\)\n            elif self\.use_open_api:\n                result = await self\._call_open_api\(image_url, prompt, user_id\)\n                if not result and self\.use_deepseek:\n                    logger\.info\("扣子开放平台API调用失败，降级使用DeepSeek API"\)\n                    result = await self\._call_deepseek_api\(image_url, prompt, user_id\)\n            elif self\.use_deepseek:\n                result = await self\._call_deepseek_api\(image_url, prompt, user_id\)\n            else:\n                logger\.error\("AI分析服务配置不完整，无法调用"\)\n                return None',
        '            # 尝试扣子服务\n            result = None\n            if self.use_site_api:\n                result = await self._call_site_api(image_url, prompt, user_id)\n                if not result:\n                    logger.error("扣子站点API调用失败，没有备用服务")\n            elif self.use_open_api:\n                result = await self._call_open_api(image_url, prompt, user_id)\n                if not result:\n                    logger.error("扣子开放平台API调用失败，没有备用服务")\n            else:\n                logger.error("AI分析服务配置不完整，无法调用")\n                return None',
        content
    )
    
    # 6. 修改analyze_acceptance_photos方法，去掉降级使用DeepSeek的逻辑
    content = re.sub(
        r'            # 尝试扣子服务\n            result = None\n            if self\.use_site_api:\n                result = await self\._call_site_api\(first_image_url, prompt, user_id\)\n                if not result and self\.use_deepseek:\n                    logger\.info\("扣子站点API调用失败，降级使用DeepSeek API"\)\n                    result = await self\._call_deepseek_api\(first_image_url, prompt, user_id\)\n            elif self\.use_open_api:\n                result = await self\._call_open_api\(first_image_url, prompt, user_id\)\n                if not result and self\.use_deepseek:\n                    logger\.info\("扣子开放平台API调用失败，降级使用DeepSeek API"\)\n                    result = await self\._call_deepseek_api\(first_image_url, prompt, user_id\)\n            elif self\.use_deepseek:\n                result = await self\._call_deepseek_api\(first_image_url, prompt, user_id\)\n            else:\n                logger\.error\("AI分析服务配置不完整，无法调用"\)\n                return None',
        '            # 尝试扣子服务\n            result = None\n            if self.use_site_api:\n                result = await self._call_site_api(first_image_url, prompt, user_id)\n                if not result:\n                    logger.error("扣子站点API调用失败，没有备用服务")\n            elif self.use_open_api:\n                result = await self._call_open_api(first_image_url, prompt, user_id)\n                if not result:\n                    logger.error("扣子开放平台API调用失败，没有备用服务")\n            else:\n                logger.error("AI分析服务配置不完整，无法调用")\n                return None',
        content
    )
    
    # 7. 修改_call_deepseek_api方法，使其总是返回None
    content = re.sub(
        r'    async def _call_deepseek_api\(self, image_url: str, prompt: str, user_id: Optional\[int\] = None\) -> Optional\[Dict\[str, Any\]\]:\n        """\n        调用DeepSeek API作为备用服务\n        \n        Args:\n            image_url: 图片URL\n            prompt: 提示词\n            user_id: 用户ID\n            \n        Returns:\n            分析结果\n        """\n        try:\n            # 检查是否有有效的DeepSeek API密钥\n            if not self\.use_deepseek:\n                logger\.warning\("DeepSeek API未配置或配置无效，跳过调用"\)\n                return None\n                \n            logger\.info\(f"调用DeepSeek API分析图片: {image_url\[:100\]}\.\.\., 用户ID: {user_id}"\)\n            \n            # 构建消息，包含图片URL\n            messages = \[\n                {"role": "system", "content": "你是一位专业的装修分析专家。请分析用户提供的装修相关图片，返回JSON格式的结构化分析结果。"},\n                {"role": "user", "content": f"{prompt}\\n\\n图片URL: {image_url}"}\n            \]\n            \n            # 调用DeepSeek API\n            response = await self\.deepseek_client\.chat\.completions\.create\(\n                model="deepseek-chat",\n                messages=messages,\n                temperature=0\.3,\n                max_tokens=2000\n            \)\n            \n            result_text = \(response\.choices\[0\]\.message\.content or ""\)\.strip\(\)\n            logger\.debug\(f"DeepSeek API响应: {result_text\[:500\]}\.\.\."\)\n            \n            # 尝试提取JSON\n            if "```json" in result_text:\n                result_text = result_text\.split\("```json"\)\[1\]\.split\("```"\)\[0\]\.strip\(\)\n            elif "```" in result_text:\n                result_text = result_text\.split\("```"\)\[1\]\.split\("```"\)\[0\]\.strip\(\)\n            \n            # 解析JSON\n            try:\n                result = json\.loads\(result_text\)\n                return result\n            except json\.JSONDecodeError:\n                # 如果无法解析为JSON，返回原始文本\n                logger\.warning\(f"DeepSeek API返回非JSON格式，返回原始文本: {result_text\[:200\]}\.\.\."\)\n                return {"raw_text": result_text}\n                \n        except Exception as e:\n            logger\.error\(f"DeepSeek API调用异常: {e}"\)\n            # 不抛出异常，返回None让扣子服务继续工作\n            return None',
        '    async def _call_deepseek_api(self, image_url: str, prompt: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:\n        """\n        调用DeepSeek API作为备用服务（已移除，不再使用）\n        \n        Args:\n            image_url: 图片URL\n            prompt: 提示词\n            user_id: 用户ID\n            \n        Returns:\n            总是返回None，因为DeepSeek API已移除\n        """\n        logger.warning("DeepSeek API已移除，不再使用")\n        return None',
        content
    )
    
    return content

def main():
    # 读取文件
    with open("backend/app/services/coze_service.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 移除DeepSeek依赖
    new_content = remove_deepseek_dependencies(content)
    
    # 写回文件
    with open("backend/app/services/coze_service.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("✅ 已成功移除DeepSeek API依赖")

if __name__ == "__main__":
    main()
