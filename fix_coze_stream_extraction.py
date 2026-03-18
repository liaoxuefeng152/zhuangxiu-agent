#!/usr/bin/env python3
"""
修复扣子智能体流式响应提取问题
问题：扣子智能体返回tool_request和tool_response类型，导致无法提取内容
解决方案：增强_extract_content_from_stream方法，正确处理所有类型的数据块
"""

import json
import logging

logger = logging.getLogger(__name__)

def fix_extract_content_from_stream(data_chunk: dict) -> str:
    """
    修复版的流式响应内容提取方法
    
    扣子智能体返回的数据块类型：
    1. message_start: 消息开始
    2. message_end: 消息结束
    3. tool_request: 工具调用请求
    4. tool_response: 工具调用响应
    5. answer: 实际回答内容（可能包含JSON）
    6. ping: 心跳
    
    需要正确处理answer类型，并过滤掉其他类型
    """
    try:
        # 获取事件类型
        event_type = data_chunk.get("type", "")
        
        # 过滤掉不需要的事件类型
        if event_type in ["message_start", "message_end", "ping", "session", "session.created", 
                         "conversation.message.created", "heartbeat", "done"]:
            return ""
        
        # 处理tool_request和tool_response - 这些是工具调用，不是实际内容
        if event_type in ["tool_request", "tool_response"]:
            # 工具调用可能包含一些信息，但通常不是我们需要的JSON
            # 可以记录日志，但返回空字符串
            logger.debug(f"过滤掉工具调用类型: {event_type}")
            return ""
        
        # 处理answer类型 - 这是实际的内容
        if event_type == "answer":
            # answer类型可能包含content字段
            content = data_chunk.get("content")
            if isinstance(content, dict):
                # 检查是否有text字段
                text = content.get("text")
                if isinstance(text, str) and text.strip():
                    return text.strip()
                # 检查是否有answer字段
                answer = content.get("answer")
                if isinstance(answer, str) and answer.strip():
                    return answer.strip()
            elif isinstance(content, str) and content.strip():
                return content.strip()
            
            # 如果没有content字段，检查其他可能的字段
            text = data_chunk.get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()
            
            # 检查delta字段
            delta = data_chunk.get("delta")
            if isinstance(delta, str) and delta.strip():
                return delta.strip()
            if isinstance(delta, dict):
                delta_content = delta.get("content") or delta.get("text")
                if isinstance(delta_content, str) and delta_content.strip():
                    return delta_content.strip()
        
        # 如果没有明确的事件类型，尝试从常见字段中提取内容
        # 检查text字段
        text = data_chunk.get("text")
        if isinstance(text, str) and text.strip():
            return text.strip()
        
        # 检查content字段
        content = data_chunk.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
        elif isinstance(content, dict):
            # 从content字典中提取text或answer
            text = content.get("text") or content.get("answer")
            if isinstance(text, str) and text.strip():
                return text.strip()
        
        # 检查delta字段
        delta = data_chunk.get("delta")
        if isinstance(delta, str) and delta.strip():
            return delta.strip()
        if isinstance(delta, dict):
            delta_content = delta.get("content") or delta.get("text")
            if isinstance(delta_content, str) and delta_content.strip():
                return delta_content.strip()
        
        # 检查output字段
        output = data_chunk.get("output")
        if isinstance(output, str) and output.strip():
            return output.strip()
        
        # 检查message字段
        message = data_chunk.get("message")
        if isinstance(message, dict):
            msg_content = message.get("content") or message.get("text")
            if isinstance(msg_content, str) and msg_content.strip():
                return msg_content.strip()
        
        # 如果没有找到内容，记录调试信息
        logger.debug(f"未找到内容的数据块: {json.dumps(data_chunk, ensure_ascii=False)[:200]}...")
        return ""
        
    except Exception as e:
        logger.debug(f"提取流式响应内容失败: {e}")
        return ""

def test_fix():
    """测试修复方法"""
    # 模拟扣子智能体返回的数据块
    test_chunks = [
        # tool_request类型
        {
            "type": "tool_request",
            "session_id": "test_session",
            "msg_id": "msg1",
            "sequence_id": 2
        },
        # tool_response类型
        {
            "type": "tool_response",
            "session_id": "test_session",
            "msg_id": "msg2",
            "sequence_id": 3
        },
        # answer类型 - 包含JSON开头
        {
            "type": "answer",
            "session_id": "test_session",
            "msg_id": "msg3",
            "sequence_id": 4,
            "content": {
                "text": '{"total_price": 85000.00, "risk_score": 65, "high_risk_items": ['
            }
        },
        # answer类型 - 包含JSON中间部分
        {
            "type": "answer",
            "session_id": "test_session",
            "msg_id": "msg3",
            "sequence_id": 5,
            "content": {
                "text": '{"name": "水电改造", "reason": "价格偏高"}, {"name": "墙面处理", "reason": "工艺不明确"}]'
            }
        },
        # answer类型 - 包含JSON结尾
        {
            "type": "answer",
            "session_id": "test_session",
            "msg_id": "msg3",
            "sequence_id": 6,
            "content": {
                "text": ', "suggestions": ["建议对比市场价格", "建议明确施工工艺"], "summary": "报价单分析完成"}'
            }
        },
        # message_end类型
        {
            "type": "message_end",
            "session_id": "test_session",
            "msg_id": "msg3",
            "sequence_id": 7
        }
    ]
    
    print("测试修复方法:")
    print("=" * 80)
    
    extracted_parts = []
    for i, chunk in enumerate(test_chunks):
        result = fix_extract_content_from_stream(chunk)
        if result:
            print(f"数据块 {i} ({chunk.get('type', 'unknown')}): 提取到内容: {result[:100]}...")
            extracted_parts.append(result)
        else:
            print(f"数据块 {i} ({chunk.get('type', 'unknown')}): 无内容")
    
    print("\n" + "=" * 80)
    print("合并所有内容:")
    full_content = "".join(extracted_parts)
    print(full_content)
    
    # 尝试解析JSON
    try:
        parsed = json.loads(full_content)
        print("\n✅ 成功解析JSON:")
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON解析失败: {e}")
        print("可能原因: JSON被分割成多个数据块，需要合并后解析")

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.DEBUG)
    test_fix()
