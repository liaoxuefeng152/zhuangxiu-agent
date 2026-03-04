#!/usr/bin/env python3
"""
检查PDF文件内容
"""
import re
import zlib

def check_pdf_content(filename):
    print(f"检查PDF文件: {filename}")
    
    with open(filename, 'rb') as f:
        data = f.read()
    
    print(f"文件大小: {len(data)} 字节")
    
    # 查找stream内容
    streams = re.findall(b'stream\s*(.*?)\s*endstream', data, re.DOTALL)
    print(f"找到stream数量: {len(streams)}")
    
    for i, stream in enumerate(streams[:3]):  # 只检查前3个stream
        stream = stream.strip()
        print(f"\n--- Stream {i+1} ---")
        print(f"大小: {len(stream)} 字节")
        
        # 尝试解压
        try:
            decompressed = zlib.decompress(stream)
            print(f"解压后大小: {len(decompressed)} 字节")
            
            # 显示部分内容
            print("内容预览 (前200字节):")
            preview = decompressed[:200]
            print(repr(preview))
            
            # 尝试查找文本
            # PDF文本操作符: Tj (显示文本), TJ (显示文本数组), Td/TD (移动文本位置)
            text_ops = re.findall(b'\((.*?)\)\s*Tj', decompressed)
            text_ops_TJ = re.findall(b'\[(.*?)\]\s*TJ', decompressed)
            
            if text_ops:
                print(f"\n找到Tj文本操作: {len(text_ops)}个")
                for j, text in enumerate(text_ops[:5]):
                    try:
                        # 尝试解码
                        decoded = text.decode('utf-8', errors='ignore')
                        print(f"  Tj[{j}]: {decoded[:50]}")
                    except:
                        print(f"  Tj[{j}]: {text[:50]}")
            
            if text_ops_TJ:
                print(f"\n找到TJ文本操作: {len(text_ops_TJ)}个")
                for j, text in enumerate(text_ops_TJ[:5]):
                    try:
                        # TJ通常是数组，包含文本和间距
                        decoded = text.decode('utf-8', errors='ignore')
                        print(f"  TJ[{j}]: {decoded[:50]}")
                    except:
                        print(f"  TJ[{j}]: {text[:50]}")
            
            # 查找字体引用
            font_refs = re.findall(b'/F(\d+)\s+\d+\s+Tf', decompressed)
            if font_refs:
                print(f"\n字体引用: {font_refs}")
            
        except Exception as e:
            print(f"解压失败: {e}")
            # 可能是未压缩的stream
            print("原始内容预览 (前200字节):")
            print(repr(stream[:200]))
    
    # 检查字体信息
    print("\n--- 字体信息 ---")
    font_pattern = re.findall(b'/Font\s*<<(.*?)>>', data, re.DOTALL)
    if font_pattern:
        print(f"找到字体定义: {len(font_pattern)}个")
        for i, font_def in enumerate(font_pattern[:2]):
            print(f"字体定义 {i+1}:")
            # 提取字体名称
            font_names = re.findall(b'/F(\d+)\s+(.*?)\s+R', font_def, re.DOTALL)
            for font_ref, font_desc in font_names:
                print(f"  F{font_ref}: {font_desc[:100]}")
    
    # 检查ToUnicode映射（用于CID字体）
    to_unicode = re.findall(b'/ToUnicode\s+(\d+)\s+\d+\s+R', data)
    if to_unicode:
        print(f"\n找到ToUnicode映射: {to_unicode}")

if __name__ == "__main__":
    check_pdf_content("fixed_chinese_pdf.pdf")
